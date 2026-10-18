"""Mock-only tests with isolated storage; no .env or external model requests."""

from concurrent.futures import ThreadPoolExecutor
import importlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import threading
import time
import unittest
from unittest.mock import patch
from urllib.request import ProxyHandler, Request, build_opener

from werkzeug.serving import WSGIRequestHandler, make_server


project = Path(__file__).parent
runtime = project / ".runtime" / "app"
runtime.mkdir(parents=True, exist_ok=True)
import_storage = TemporaryDirectory(prefix="test-import-", dir=runtime)
with patch.dict("os.environ", {
    "CHAT_MODE": "mock", "APP_DATA_FILE": str(Path(import_storage.name) / "unused.json")
}):
    application = importlib.import_module("app")


def tearDownModule():
    import_storage.cleanup()


def metric(name, **labels):
    return application.REGISTRY.get_sample_value(name, labels)


class QuietHandler(WSGIRequestHandler):
    def log_request(self, *args, **kwargs):
        pass


class AppTests(unittest.TestCase):
    def setUp(self):
        storage = TemporaryDirectory(prefix="test-", dir=runtime)
        self.addCleanup(storage.cleanup)
        data_patch = patch.object(application, "data_file", Path(storage.name) / "state.json")
        data_patch.start()
        self.addCleanup(data_patch.stop)
        config_patch = patch.dict(application.app.config, {"CHAT_MODE": "mock", "TESTING": True})
        config_patch.start()
        self.addCleanup(config_patch.stop)
        with application.state_lock:
            application.messages.clear()
            application.conversations.clear()
            application.next_message_id = application.next_conversation_id = application.next_turn_id = 1
        self.client = application.app.test_client()

    def test_success_failure_and_nonchat_metrics(self):
        success = metric("chat_requests_total", outcome="success")
        error = metric("chat_requests_total", outcome="error")
        count = metric("chat_request_duration_seconds_count")
        duration = metric("chat_request_duration_seconds_sum")
        with patch.object(application.os, "getenv", side_effect=AssertionError("mock must not read a key")):
            response = self.client.post("/api/messages", json={"message": "测试", "mock_delay": 0})
            self.assertEqual(response.status_code, 201)
            self.assertIn("mock", response.json["reply"])
            failed = self.client.post("/api/messages", json={
                "message": "测试失败", "mock_delay": 0.02, "mock_error": True,
            })
            self.assertEqual(failed.status_code, 503)
            self.assertEqual(failed.json["code"], "mock_error")
        for route in ("/", "/frontend/app.js", "/frontend/style.css", "/api/hello", "/api/status", "/metrics"):
            with self.client.get(route) as response:
                self.assertEqual(response.status_code, 200, route)
        self.assertEqual(metric("chat_requests_total", outcome="success") - success, 1)
        self.assertEqual(metric("chat_requests_total", outcome="error") - error, 1)
        self.assertEqual(metric("chat_request_duration_seconds_count") - count, 2)
        self.assertGreaterEqual(metric("chat_request_duration_seconds_sum") - duration, 0.02)
        self.assertEqual(metric("chat_inprogress_requests"), 0)
        response = self.client.get("/metrics")
        self.assertTrue(response.content_type.startswith("text/plain"))
        self.assertIn(b'chat_request_duration_seconds_bucket{le="3.0"}', response.data)
        self.assertNotIn("测试".encode(), response.data)

    def test_invalid_options_are_errors(self):
        before = metric("chat_requests_total", outcome="error")
        cases = [
            {"message": " "}, {"message": 123},
            *({"message": "测试", "mock_delay": delay} for delay in (-1, 11, True, "1", float("nan"), float("inf"), 10**400)),
            {"message": "测试", "mock_error": "true"},
        ]
        for payload in cases:
            with self.subTest(payload=payload):
                self.assertEqual(self.client.post("/api/messages", json=payload).status_code, 400)
        self.assertEqual(metric("chat_requests_total", outcome="error") - before, len(cases))
        self.assertEqual(metric("chat_inprogress_requests"), 0)
        self.assertFalse(application.data_file.exists())

    def test_unexpected_exception_finalizes_metrics(self):
        before = metric("chat_requests_total", outcome="error")
        count = metric("chat_request_duration_seconds_count")
        with patch.object(application, "generate_reply", side_effect=RuntimeError("test failure")):
            with self.assertRaises(RuntimeError):
                self.client.post("/api/messages", json={"message": "异常测试"})
        self.assertEqual(metric("chat_requests_total", outcome="error") - before, 1)
        self.assertEqual(metric("chat_request_duration_seconds_count") - count, 1)
        self.assertEqual(metric("chat_inprogress_requests"), 0)

    def test_status_does_not_misreport_real_mode(self):
        self.assertEqual(self.client.get("/api/status").json, {"mode": "mock", "external_model_calls": False})
        with patch.dict(application.app.config, {"CHAT_MODE": "real"}):
            self.assertEqual(self.client.get("/api/status").status_code, 404)

    def test_original_crud_and_history(self):
        response = self.client.post("/api/conversations", json={"title": "测试会话"})
        self.assertEqual(response.status_code, 201)
        route = f"/api/conversations/{response.json['id']}"
        with patch.object(application, "generate_reply", wraps=application.generate_reply) as model:
            first = self.client.post(route + "/messages", json={"message": "你好", "mock_delay": 0})
            self.assertEqual(first.status_code, 201)
            self.assertEqual(self.client.post(route + "/messages", json={"message": "继续", "mock_delay": 0}).status_code, 201)
            self.assertEqual(len(model.call_args.args[0]), 3)
        self.assertEqual(self.client.patch(route, json={"title": "重命名"}).status_code, 200)
        turn = route + f"/messages/{first.json['id']}"
        self.assertEqual(self.client.patch(turn, json={"message": "修改后"}).status_code, 200)
        self.assertEqual(self.client.get(route).json["messages"][0]["content"], "修改后")
        self.assertEqual(self.client.delete(turn).status_code, 200)
        self.assertEqual(self.client.get("/api/conversations").json[0]["message_count"], 1)
        self.assertEqual(application.load_state()[1], application.conversations)
        self.assertEqual(self.client.delete(route).status_code, 200)
        self.assertEqual(self.client.get(route).status_code, 404)
        message = self.client.post("/api/messages", json={"message": "旧接口", "mock_delay": 0})
        route = f"/api/messages/{message.json['id']}"
        self.assertEqual(self.client.patch(route, json={"message": "修改"}).status_code, 200)
        self.assertEqual(self.client.get("/api/messages").json[0]["message"], "修改")
        self.assertEqual(self.client.delete(route).status_code, 200)
        self.assertEqual(self.client.get("/api/messages").json, [])

    def test_concurrent_http_chat_keeps_metrics_responsive(self):
        server = make_server("127.0.0.1", 0, application.app, threaded=True, request_handler=QuietHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(thread.join, 2)
        self.addCleanup(server.shutdown)
        base = f"http://127.0.0.1:{server.server_port}"
        conversation = self.client.post("/api/conversations", json={"title": "并发测试"}).json["id"]
        def send(number):
            path = "/api/messages" if number % 2 else f"/api/conversations/{conversation}/messages"
            payload = json.dumps({"message": "并发测试", "mock_delay": 0.7}).encode()
            req = Request(base + path, data=payload, headers={"Content-Type": "application/json"})
            with build_opener(ProxyHandler({})).open(req, timeout=4) as response:
                return response.status, json.load(response)
        with ThreadPoolExecutor(max_workers=6) as pool:
            futures = [pool.submit(send, number) for number in range(6)]
            deadline = time.monotonic() + 2
            while metric("chat_inprogress_requests") < 6 and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertEqual(metric("chat_inprogress_requests"), 6)
            with build_opener(ProxyHandler({})).open(base + "/metrics", timeout=0.5) as response:
                self.assertIn(b"chat_inprogress_requests 6.0", response.read())
            results = [future.result() for future in futures]
        self.assertTrue(all(code == 201 for code, _ in results))
        self.assertEqual(metric("chat_inprogress_requests"), 0)
        stored_messages, stored_conversations = application.load_state()
        self.assertEqual(len({item["id"] for item in stored_messages}), 3)
        self.assertEqual(len(stored_conversations[0]["messages"]), 6)
        self.assertEqual(len({item["turn_id"] for item in stored_conversations[0]["messages"]}), 3)

    def test_deleted_conversation_is_not_resurrected_after_reply(self):
        conversation = self.client.post("/api/conversations", json={"title": "删除测试"}).json["id"]
        route = f"/api/conversations/{conversation}"
        def delete_during_reply(*args):
            with application.app.test_client() as another_client:
                self.assertEqual(another_client.delete(route).status_code, 200)
            return "mock 回复", None
        with patch.object(application, "generate_reply", side_effect=delete_during_reply):
            response = self.client.post(route + "/messages", json={"message": "测试"})
        self.assertEqual(response.status_code, 409)
        self.assertEqual(application.load_state()[1], [])
        self.assertEqual(metric("chat_inprogress_requests"), 0)


if __name__ == "__main__":
    unittest.main()
