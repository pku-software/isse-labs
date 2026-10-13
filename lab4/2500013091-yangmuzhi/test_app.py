"""Regression checks for mock isolation, metrics cleanup, CRUD and concurrency."""

from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import ProxyHandler, Request, build_opener

os.environ["LAB4_MODEL_MODE"] = "mock"

import app as application
from prometheus_client.parser import text_string_to_metric_families
from werkzeug.serving import make_server


def values(body):
    return {
        (sample.name, tuple(sorted(sample.labels.items()))): sample.value
        for family in text_string_to_metric_families(body.decode("utf-8"))
        for sample in family.samples
    }


def sample(snapshot, name, **labels):
    return snapshot[(name, tuple(sorted(labels.items())))]


class AppTests(unittest.TestCase):
    def setUp(self):
        self.client = application.app.test_client()
        runtime = Path(__file__).resolve().parent / ".runtime" / "app"
        runtime.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="test-", dir=runtime)
        self.addCleanup(self.temp.cleanup)
        for name, value in (
            ("data_path", Path(self.temp.name) / "conversations.json"),
            ("messages", []), ("conversations", []),
            ("next_message_id", 1), ("next_conversation_id", 1),
            ("next_conversation_message_id", 1), ("next_turn_id", 1),
        ):
            patcher = patch.object(application, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def snapshot(self):
        response = self.client.get("/metrics")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content_type.startswith("text/plain"))
        return values(response.data)

    def test_success_failure_and_nonchat_exclusion(self):
        before = self.snapshot()
        for path in ("/", "/style.css", "/app.js", "/api/hello", "/api/lab/status",
                     "/api/messages", "/api/conversations", "/metrics"):
            with self.client.get(path) as response:
                self.assertEqual(response.status_code, 200)
        self.assertEqual(before, self.snapshot())
        for forced, expected in ((False, 201), (True, 503)):
            response = self.client.post("/api/messages", json={
                "message": "监控测试", "mock": {"delay_seconds": 0, "force_error": forced},
            })
            self.assertEqual(response.status_code, expected)
            self.assertIn("error" if forced else "reply", response.json)
        after = self.snapshot()
        for outcome in ("success", "error"):
            self.assertEqual(sample(after, "chat_requests_total", outcome=outcome)
                             - sample(before, "chat_requests_total", outcome=outcome), 1)
        self.assertEqual(sample(after, "chat_request_duration_seconds_count")
                         - sample(before, "chat_request_duration_seconds_count"), 2)
        self.assertEqual(sample(after, "chat_inprogress_requests"), 0)
        self.assertNotIn("openai", sys.modules)

    def test_unexpected_exception_also_finishes_metrics(self):
        before = self.snapshot()
        with patch.object(application, "generate_reply", side_effect=RuntimeError("test failure")):
            with patch.dict(application.app.config, {"TESTING": True}):
                with self.assertRaises(RuntimeError):
                    self.client.post("/api/messages", json={"message": "测试异常"})
        after = self.snapshot()
        self.assertEqual(sample(after, "chat_inprogress_requests"), 0)
        self.assertEqual(sample(after, "chat_requests_total", outcome="error")
                         - sample(before, "chat_requests_total", outcome="error"), 1)
        self.assertEqual(sample(after, "chat_request_duration_seconds_count")
                         - sample(before, "chat_request_duration_seconds_count"), 1)

    def test_mode_and_mock_validation(self):
        self.assertEqual(self.client.get("/api/lab/status").json,
                         {"mode": "mock", "external_model_calls": False})
        # Inspect status behavior only; never issue a real-mode chat request.
        with patch.dict(application.app.config, {"MODEL_MODE": "real"}):
            self.assertEqual(self.client.get("/api/lab/status").status_code, 404)
        for options in ([], {"delay_seconds": -1}, {"delay_seconds": 31},
                        {"delay_seconds": True}, {"delay_seconds": float("nan")},
                        {"delay_seconds": 10 ** 400},
                        {"force_error": "false"}):
            self.assertEqual(self.client.post("/api/messages", json={
                "message": "参数测试", "mock": options,
            }).status_code, 400)
        self.assertEqual(sample(self.snapshot(), "chat_inprogress_requests"), 0)

    def test_existing_crud_and_conversation_metrics(self):
        before = self.snapshot()
        created = self.client.post("/api/conversations", json={"title": "测试会话"})
        self.assertEqual(created.status_code, 201)
        path = "/api/conversations/" + str(created.json["id"])
        response = self.client.post(path + "/messages", json={
            "message": "测试消息", "mock": {"delay_seconds": 0},
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.json["messages"]), 2)
        turn_path = path + "/turns/" + str(response.json["messages"][0]["turn_id"])
        self.assertEqual(self.client.patch(turn_path, json={"message": "修改测试"}).status_code, 200)
        self.assertEqual(self.client.delete(turn_path).json["messages"], [])
        self.assertEqual(self.client.patch(path, json={"title": "新名称"}).json["title"], "新名称")
        self.assertEqual(self.client.get(path).status_code, 200)
        self.assertEqual(self.client.delete(path).status_code, 200)
        self.assertEqual(self.client.get(path).status_code, 404)
        saved = json.loads(application.data_path.read_text(encoding="utf-8"))
        self.assertEqual(saved["conversations"], [])
        after = self.snapshot()
        self.assertEqual(sample(after, "chat_requests_total", outcome="success")
                         - sample(before, "chat_requests_total", outcome="success"), 1)

    def test_real_http_concurrency_and_metrics_during_slow_chat(self):
        conversation_id = self.client.post("/api/conversations", json={"title": "并发测试"}).json["id"]
        server = make_server("127.0.0.1", 0, application.app, threaded=True)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = "http://127.0.0.1:" + str(server.server_port)

        def get_metrics():
            with build_opener(ProxyHandler({})).open(base + "/metrics", timeout=1) as response:
                return values(response.read())

        def send(number):
            request = Request(base + f"/api/conversations/{conversation_id}/messages",
                              data=json.dumps({"message": "并发测试", "mock": {
                                  "delay_seconds": 1.5, "force_error": number == 0,
                              }}).encode("utf-8"), headers={"Content-Type": "application/json"})
            try:
                with build_opener(ProxyHandler({})).open(request, timeout=5) as response:
                    return response.status
            except HTTPError as error:
                with error:
                    return error.code

        try:
            with ThreadPoolExecutor(max_workers=4) as pool:
                pending = [pool.submit(send, number) for number in range(4)]
                deadline = time.monotonic() + 1.0
                peak = 0
                while time.monotonic() < deadline:
                    started = time.monotonic()
                    snapshot = get_metrics()
                    self.assertLess(time.monotonic() - started, 1.0)
                    peak = max(peak, sample(snapshot, "chat_inprogress_requests"))
                    if peak == 4:
                        break
                    time.sleep(0.02)
                self.assertEqual(peak, 4)
                self.assertEqual(sorted(future.result() for future in pending), [201, 201, 201, 503])
            self.assertEqual(sample(get_metrics(), "chat_inprogress_requests"), 0)
            saved = json.loads(application.data_path.read_text(encoding="utf-8"))
            records = saved["conversations"][0]["messages"]
            self.assertEqual(len(records), 6)
            self.assertEqual(len({record["id"] for record in records}), 6)
            self.assertEqual(len({record["turn_id"] for record in records}), 3)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
