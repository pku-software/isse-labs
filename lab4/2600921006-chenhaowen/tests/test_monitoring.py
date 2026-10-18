"""HTTP contract checks using isolated storage and no external model access."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import ProxyHandler, Request, build_opener

from prometheus_client.parser import text_string_to_metric_families
from werkzeug.serving import WSGIRequestHandler, make_server


PROJECT = Path(__file__).resolve().parents[1]


class QuietHandler(WSGIRequestHandler):
    def log_request(self, *args, **kwargs):
        pass


class MonitoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        runtime = PROJECT / ".runtime" / "app" / "tests"
        runtime.mkdir(parents=True, exist_ok=True)
        cls.cleanup = ExitStack()
        cls.addClassCleanup(cls.cleanup.close)
        sandbox = Path(cls.cleanup.enter_context(tempfile.TemporaryDirectory(dir=runtime)))
        for name in ("app.py", "metrics.py"):
            if (PROJECT / name).exists():
                shutil.copy2(PROJECT / name, sandbox / name)
        shutil.copytree(PROJECT / "frontend", sandbox / "frontend")
        cls.cleanup.enter_context(patch.dict(os.environ, {"DEEPSEEK_API_KEY": ""}))
        os.environ.pop("CHAT_MODE", None)
        cls.cleanup.enter_context(patch("openai.OpenAI", side_effect=AssertionError("External model access is forbidden")))
        cls.dotenv = cls.cleanup.enter_context(patch("dotenv.load_dotenv", return_value=False))
        sys.path.insert(0, str(sandbox))
        cls.cleanup.callback(sys.path.remove, str(sandbox))
        spec = importlib.util.spec_from_file_location("monitoring_test_app", sandbox / "app.py")
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)
        cls.server = make_server("127.0.0.1", 0, cls.module.app, threaded=True, request_handler=QuietHandler)
        cls.cleanup.callback(cls.server.server_close)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.cleanup.callback(cls.thread.join, 3)
        cls.cleanup.callback(cls.server.shutdown)
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    def http(self, path, payload=None, method=None, timeout=3):
        data = json.dumps(payload).encode() if payload is not None else None
        req = Request(self.base_url + path, data=data, method=method,
                      headers={"Content-Type": "application/json"})
        opener = build_opener(ProxyHandler({}))
        try:
            response = opener.open(req, timeout=timeout)
        except HTTPError as error:
            response = error
        with response:
            return response.status, response.read(), response.headers

    def samples(self, timeout=3):
        status, body, headers = self.http("/metrics", timeout=timeout)
        self.assertEqual(status, 200)
        self.assertTrue(headers.get_content_type().startswith("text/"))
        return {
            (sample.name, tuple(sorted(sample.labels.items()))): sample.value
            for family in text_string_to_metric_families(body.decode())
            for sample in family.samples
        }

    def value(self, samples, name, **labels):
        return samples[(name, tuple(sorted(labels.items())))]

    def new_conversation(self):
        status, body, _ = self.http("/api/conversations", {"title": "监控契约测试"})
        self.assertEqual(status, 201)
        return json.loads(body)["id"]

    def test_default_mock_reports_external_calls_disabled(self):
        status, body, _ = self.http("/api/lab-status")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {"mode": "mock", "external_model_calls": False})

    def test_import_does_not_load_dotenv(self):
        self.assertFalse(self.dotenv.called, "Application startup must not read .env")

    def test_success_and_failure_count_only_chat_requests(self):
        before = self.samples()
        for path in ("/", "/static/app.js", "/api/hello", "/api/lab-status", "/metrics"):
            self.assertEqual(self.http(path)[0], 200)
        conversation_id = self.new_conversation()
        path = f"/api/conversations/{conversation_id}/messages"
        status, body, _ = self.http(path, {"message": "固定测试消息", "mock_delay_seconds": 0})
        self.assertEqual(status, 201)
        record = json.loads(body)
        self.assertIsInstance(record["id"], int)
        self.assertTrue(record["reply"].strip())
        status, body, _ = self.http(path, {"message": "模拟失败", "mock_delay_seconds": 0, "mock_force_error": True})
        self.assertEqual(status, 503)
        self.assertEqual(json.loads(body)["code"], "mock_failure")
        self.assertEqual(self.http(f"{path}/{record['id']}", {"message": "修改测试消息"}, "PATCH")[0], 200)
        self.assertEqual(self.http(f"{path}/{record['id']}", method="DELETE")[0], 200)
        self.assertEqual(self.http(f"/api/conversations/{conversation_id}", method="DELETE")[0], 200)
        after = self.samples()
        for outcome in ("success", "error"):
            self.assertEqual(self.value(after, "chat_requests_total", outcome=outcome)
                             - self.value(before, "chat_requests_total", outcome=outcome), 1)
        self.assertEqual(self.value(after, "chat_request_duration_seconds_count")
                         - self.value(before, "chat_request_duration_seconds_count"), 2)
        self.assertEqual(self.value(after, "chat_inprogress_requests"), 0)
        self.assertTrue(all(set(labels).issubset({("outcome", "success"), ("outcome", "error")})
                            for name, labels in after if name == "chat_requests_total"))

    def test_parallel_slow_replies_preserve_records_and_allow_metrics(self):
        self.samples()
        conversation_id = self.new_conversation()
        path = f"/api/conversations/{conversation_id}/messages"
        with ThreadPoolExecutor(max_workers=2) as pool:
            pending = [pool.submit(self.http, path, {"message": "并发测试", "mock_delay_seconds": 0.8})
                       for _ in range(2)]
            deadline = time.monotonic() + 2
            observed = 0
            while time.monotonic() < deadline:
                observed = self.value(self.samples(timeout=0.4), "chat_inprogress_requests")
                if observed == 2:
                    break
                time.sleep(0.02)
            self.assertEqual(observed, 2, "Metrics must be readable while both chats are waiting")
            self.assertEqual([future.result()[0] for future in pending], [201, 201])
        status, body, _ = self.http(path)
        self.assertEqual(status, 200)
        self.assertEqual(len({record["id"] for record in json.loads(body)}), 2)
        self.assertEqual(self.value(self.samples(), "chat_inprogress_requests"), 0)

    def test_invalid_mock_options_are_rejected(self):
        invalid = [{"mock_delay_seconds": value} for value in (-1, 31, float("nan"), float("inf"), True, "1")]
        invalid.append({"mock_force_error": "true"})
        for options in invalid:
            with self.subTest(options=options):
                status, _, _ = self.http("/api/messages", {"message": "输入校验", **options})
                self.assertEqual(status, 400)

    def test_storage_failure_is_counted_and_inflight_recovers(self):
        before = self.samples()
        with patch.object(self.module, "write_conversations", side_effect=self.module.StorageError):
            status, _, _ = self.http("/api/messages", {"message": "存储失败测试", "mock_delay_seconds": 0})
        self.assertEqual(status, 500)
        after = self.samples()
        self.assertEqual(self.value(after, "chat_requests_total", outcome="error")
                         - self.value(before, "chat_requests_total", outcome="error"), 1)
        self.assertEqual(self.value(after, "chat_request_duration_seconds_count")
                         - self.value(before, "chat_request_duration_seconds_count"), 1)
        self.assertEqual(self.value(after, "chat_inprogress_requests"), 0)

    def test_real_configuration_cannot_report_mock(self):
        with patch.object(self.module, "CHAT_MODE", "real", create=True):
            self.assertEqual(self.http("/api/lab-status")[0], 404)


if __name__ == "__main__":
    unittest.main()
