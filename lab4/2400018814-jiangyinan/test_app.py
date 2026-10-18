import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import Mock, patch

os.environ["LAB4_MODEL_MODE"] = "mock"

import requests
from prometheus_client import REGISTRY
from werkzeug.serving import make_server

import app as application


def metric(name, labels=None):
    return REGISTRY.get_sample_value(name, labels or {})


class ChatMonitoringTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        storage = patch.object(application, "data_file", Path(self.directory.name) / "messages.json")
        storage.start()
        self.addCleanup(storage.stop)
        application.messages.clear()
        application.next_id = 1
        self.client = application.app.test_client()
        self.success = metric("chat_requests_total", {"outcome": "success"})
        self.errors = metric("chat_requests_total", {"outcome": "error"})
        self.count = metric("chat_request_duration_seconds_count")

    def assert_counts(self, success, errors):
        self.assertEqual(metric("chat_requests_total", {"outcome": "success"}), self.success + success)
        self.assertEqual(metric("chat_requests_total", {"outcome": "error"}), self.errors + errors)
        self.assertEqual(metric("chat_request_duration_seconds_count"), self.count + success + errors)
        self.assertEqual(metric("chat_inprogress_requests"), 0)

    def test_monitoring_and_static_reads_do_not_count_as_chat(self):
        for path in ("/", "/style.css", "/app.js", "/api/hello", "/api/messages"):
            with self.client.get(path) as response:
                self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get("/api/lab4/status").json,
                         {"mode": "mock", "external_model_calls": False})
        response = self.client.get("/metrics")
        self.assertIn("text/plain", response.content_type)
        self.assertIn(b"chat_request_duration_seconds_bucket", response.data)
        self.assert_counts(0, 0)

    def test_mock_crud_and_storage_without_external_call(self):
        with patch.object(application.requests, "post", side_effect=AssertionError("External call forbidden")):
            response = self.client.post("/api/messages", json={"message": "测试", "mock_delay": 0})
        self.assertEqual(response.status_code, 201)
        self.assertIn("模拟回复", response.json["reply"])
        record_id = response.json["id"]
        self.assertEqual(json.loads(application.data_file.read_text()), [response.json])
        self.assertEqual(self.client.get("/api/messages").json, [response.json])
        self.assertEqual(self.client.patch(f"/api/messages/{record_id}", json={"message": "修改"}).status_code, 200)
        self.assertEqual(self.client.delete(f"/api/messages/{record_id}").status_code, 200)
        self.assertEqual(self.client.get("/api/messages").json, [])
        self.assert_counts(1, 0)

    def test_simulated_failure_includes_delay_and_cleans_up(self):
        before = metric("chat_request_duration_seconds_sum")
        response = self.client.post("/api/messages", json={"message": "测试", "mock_delay": 0.1, "mock_error": True})
        self.assertEqual(response.status_code, 503)
        self.assertTrue(response.json["simulated"])
        self.assertGreaterEqual(metric("chat_request_duration_seconds_sum") - before, 0.1)
        self.assertEqual(application.messages, [])
        self.assert_counts(0, 1)

    def test_invalid_options_and_empty_messages(self):
        payloads = [{"message": "测试", "mock_delay": value}
                    for value in (None, "3", True, -1, 31, float("nan"), float("inf"))]
        payloads += [{"message": "测试", "mock_error": "true"}, {"message": " "}, []]
        for payload in payloads:
            self.assertEqual(self.client.post("/api/messages", json=payload).status_code, 400)
        self.assert_counts(0, len(payloads))

    def test_storage_exception_also_cleans_up(self):
        with patch.object(application, "save_messages", side_effect=OSError("test failure")):
            response = self.client.post("/api/messages", json={"message": "测试", "mock_delay": 0})
        self.assertEqual(response.status_code, 500)
        self.assert_counts(0, 1)

    def test_real_mode_does_not_report_mock_or_apply_mock_options(self):
        upstream = Mock(status_code=200)
        upstream.json.return_value = {"status": "completed", "output": [
            {"type": "message", "content": [{"type": "output_text", "text": "stubbed upstream response"}]}]}
        with patch.object(application, "MODEL_MODE", "real"), \
                patch.dict(os.environ, {"OPENAI_API_KEY": "unit-test-placeholder"}), \
                patch.object(application.requests, "post", return_value=upstream) as post, \
                patch.object(application.time, "sleep") as sleep:
            self.assertEqual(self.client.get("/api/lab4/status").status_code, 404)
            response = self.client.post("/api/messages", json={"message": "测试", "mock_delay": "ignored", "mock_error": True})
            self.assertEqual(response.status_code, 201)
            post.assert_called_once()
            sleep.assert_not_called()
        self.assert_counts(1, 0)

    def test_slow_concurrent_requests_leave_metrics_responsive(self):
        server = make_server("127.0.0.1", 0, application.app, threaded=True)
        serving = threading.Thread(target=server.serve_forever, daemon=True)
        serving.start()
        base = f"http://127.0.0.1:{server.server_port}"

        def send():
            with requests.Session() as session:
                session.trust_env = False
                return session.post(base + "/api/messages", json={"message": "并发测试", "mock_delay": 1}, timeout=5)

        try:
            with ThreadPoolExecutor(max_workers=3) as pool:
                jobs = [pool.submit(send) for _ in range(3)]
                deadline = time.monotonic() + 3
                while metric("chat_inprogress_requests") != 3 and time.monotonic() < deadline:
                    time.sleep(0.01)
                self.assertEqual(metric("chat_inprogress_requests"), 3)
                with requests.Session() as session:
                    session.trust_env = False
                    response = session.get(base + "/metrics", timeout=0.5)
                self.assertEqual(response.status_code, 200)
                self.assertIn("chat_inprogress_requests 3.0", response.text)
                responses = [job.result() for job in jobs]
                self.assertTrue(all(item.status_code == 201 for item in responses))
                self.assertEqual(len({item.json()["id"] for item in responses}), 3)
        finally:
            server.shutdown()
            server.server_close()
            serving.join(timeout=2)
        self.assertEqual(len(json.loads(application.data_file.read_text())), 3)
        self.assert_counts(3, 0)


if __name__ == "__main__":
    unittest.main()
