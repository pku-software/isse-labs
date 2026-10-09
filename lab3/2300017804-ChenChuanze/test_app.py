import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch


project = Path(__file__).parent
spec = importlib.util.spec_from_file_location("lab3_app", project / "app.py")
application = importlib.util.module_from_spec(spec)
original_exists = Path.exists
with patch("dotenv.load_dotenv"), patch.object(
    Path, "exists", autospec=True,
    side_effect=lambda path: False if path == project / "data" / "conversations.json" else original_exists(path),
):
    spec.loader.exec_module(application)


class AppTests(unittest.TestCase):
    def setUp(self):
        self.storage = TemporaryDirectory(dir=project)
        self.addCleanup(self.storage.cleanup)
        self.data_patch = patch.object(
            application, "data_file", Path(self.storage.name) / "conversations.json"
        )
        self.data_patch.start()
        self.addCleanup(self.data_patch.stop)
        application.messages.clear()
        application.conversations.clear()
        application.next_message_id = application.next_conversation_id = application.next_turn_id = 1
        self.client = application.app.test_client()

    def test_page_static_and_hello(self):
        for route in ("/", "/frontend/app.js", "/frontend/style.css", "/api/hello"):
            with self.client.get(route) as response:
                self.assertEqual(response.status_code, 200, route)
        self.assertFalse(application.app.debug)

    def test_validation_and_missing_key(self):
        self.assertEqual(self.client.post("/api/messages", json={"message": " "}).status_code, 400)
        with patch.object(application.os, "getenv", return_value=None):
            self.assertEqual(self.client.post("/api/messages", json={"message": "你好"}).status_code, 503)
        self.assertFalse(application.data_file.exists())

    def test_conversation_and_turn_crud(self):
        response = self.client.post("/api/conversations", json={"title": "测试"})
        self.assertEqual(response.status_code, 201)
        route = f"/api/conversations/{response.json['id']}"
        self.assertEqual(self.client.patch(route, json={"title": "重命名"}).status_code, 200)
        with patch.object(application, "generate_reply", return_value=("模拟回复", None)) as model:
            first = self.client.post(route + "/messages", json={"message": "你好"})
            self.assertEqual(first.status_code, 201)
            self.assertEqual(self.client.post(route + "/messages", json={"message": "继续"}).status_code, 201)
            self.assertEqual(len(model.call_args.args[0]), 3)
        turn = route + f"/messages/{first.json['id']}"
        self.assertEqual(self.client.patch(turn, json={"message": "已修改"}).status_code, 200)
        self.assertEqual(self.client.get(route).json["messages"][0]["content"], "已修改")
        self.assertEqual(self.client.delete(turn).status_code, 200)
        self.assertEqual(len(self.client.get(route).json["messages"]), 2)
        self.assertEqual(self.client.get("/api/conversations").json[0]["message_count"], 1)
        stored_messages, stored_conversations = application.load_state()
        self.assertEqual(stored_messages, [])
        self.assertEqual(stored_conversations, application.conversations)
        self.assertEqual(self.client.delete(route).status_code, 200)
        self.assertEqual(self.client.get(route).status_code, 404)

    def test_legacy_message_crud(self):
        with patch.object(application, "generate_reply", return_value=("模拟回复", None)):
            response = self.client.post("/api/messages", json={"message": "你好"})
        self.assertEqual(response.status_code, 201)
        route = f"/api/messages/{response.json['id']}"
        self.assertEqual(self.client.patch(route, json={"message": "已修改"}).status_code, 200)
        self.assertEqual(self.client.get("/api/messages").json[0]["message"], "已修改")
        self.assertEqual(self.client.delete(route).status_code, 200)
        self.assertEqual(self.client.get("/api/messages").json, [])


if __name__ == "__main__":
    unittest.main()
