"""Regression checks for mock isolation, metric cleanup and shared storage."""

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from prometheus_client import REGISTRY

import app


def value(name, labels=None):
    return REGISTRY.get_sample_value(name, labels or {}) or 0


class ChatTests(unittest.TestCase):
    def setUp(self):
        app.DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.storage = tempfile.TemporaryDirectory(dir=app.DATA_FILE.parent)
        self.patches = [
            patch.object(app, "DATA_FILE", Path(self.storage.name) / "messages.json"),
            patch.object(app, "messages", []),
            patch.object(app, "next_message_id", 1),
            patch.object(app, "MODEL_MODE", "mock"),
        ]
        for item in self.patches:
            item.start()
        self.client = app.app.test_client()

    def tearDown(self):
        for item in reversed(self.patches):
            item.stop()
        self.storage.cleanup()

    def test_mock_does_not_import_sdk_and_crud_still_works(self):
        with patch.dict("sys.modules", {"openai": None}):
            response = self.client.post("/api/messages", json={
                "message": "非敏感测试消息", "mock_delay": 0,
            })
        self.assertEqual(response.status_code, 201)
        record = response.get_json()
        self.assertTrue(record["reply"])
        url = f'/api/messages/{record["id"]}'
        self.assertEqual(self.client.get("/api/messages").get_json(), [record])
        self.assertEqual(self.client.patch(url, json={"message": "修改测试"}).status_code, 200)
        self.assertEqual(self.client.delete(url).status_code, 200)
        self.assertEqual(json.loads(app.DATA_FILE.read_text()), [])

    def test_failure_counts_and_finishes(self):
        before_error = value("chat_requests_total", {"outcome": "error"})
        before_count = value("chat_request_duration_seconds_count")
        response = self.client.post("/api/messages", json={
            "message": "模拟失败测试", "mock_delay": 0.01, "mock_error": True,
        })
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.get_json(), {"error": "Simulated model failure"})
        self.assertEqual(value("chat_requests_total", {"outcome": "error"}), before_error + 1)
        self.assertEqual(value("chat_request_duration_seconds_count"), before_count + 1)
        self.assertEqual(value("chat_inprogress_requests"), 0)
        self.assertEqual(app.messages, [])

    def test_unexpected_exception_also_finishes_metrics(self):
        before = value("chat_requests_total", {"outcome": "error"})
        before_count = value("chat_request_duration_seconds_count")
        with patch.object(app, "get_ai_reply", side_effect=RuntimeError("test only")):
            with self.assertLogs(app.app.logger, level="ERROR"):
                response = self.client.post("/api/messages", json={"message": "异常测试"})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(value("chat_requests_total", {"outcome": "error"}), before + 1)
        self.assertEqual(value("chat_request_duration_seconds_count"), before_count + 1)
        self.assertEqual(value("chat_inprogress_requests"), 0)

    def test_storage_failure_rolls_back(self):
        with patch.object(app, "save_messages", side_effect=OSError("test only")):
            response = self.client.post("/api/messages", json={
                "message": "保存失败测试", "mock_delay": 0,
            })
        self.assertEqual(response.status_code, 500)
        self.assertEqual(app.messages, [])
        self.assertEqual(app.next_message_id, 1)
        self.assertEqual(value("chat_inprogress_requests"), 0)

    def test_non_chat_reads_do_not_change_chat_metrics(self):
        before = value("chat_request_duration_seconds_count")
        for url in ("/", "/app.js", "/api/hello", "/api/messages", "/api/lab/status", "/metrics"):
            with self.client.get(url) as response:
                self.assertEqual(response.status_code, 200)
        response = self.client.get("/metrics")
        self.assertTrue(response.content_type.startswith("text/plain"))
        self.assertEqual(value("chat_request_duration_seconds_count"), before)
        self.assertEqual(self.client.get("/api/lab/status").get_json(), {
            "mode": "mock", "external_model_calls": False,
        })
        with patch.object(app, "MODEL_MODE", "real"):
            self.assertEqual(self.client.get("/api/lab/status").status_code, 404)

    def test_invalid_mock_options_are_rejected(self):
        for fields in ({"mock_delay": -1}, {"mock_delay": 31},
                       {"mock_delay": float("nan")}, {"mock_delay": True},
                       {"mock_delay": "3"}, {"mock_error": "true"}):
            response = self.client.post("/api/messages", json={"message": "参数测试", **fields})
            self.assertEqual(response.status_code, 400)
        self.assertEqual(value("chat_inprogress_requests"), 0)

    def test_concurrent_creates_have_unique_ids_and_valid_storage(self):
        def send(_):
            with app.app.test_client() as client:
                response = client.post("/api/messages", json={
                    "message": "并发保存测试", "mock_delay": 0.01,
                })
                self.assertEqual(response.status_code, 201)
                return response.get_json()["id"]

        with ThreadPoolExecutor(max_workers=4) as pool:
            ids = list(pool.map(send, range(4)))
        self.assertEqual(sorted(ids), [1, 2, 3, 4])
        self.assertEqual(len(json.loads(app.DATA_FILE.read_text())), 4)
        self.assertEqual(value("chat_inprogress_requests"), 0)


if __name__ == "__main__":
    unittest.main()
