from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

with patch("dotenv.load_dotenv"):
    import app as chat_app


@pytest.fixture
def client_and_model(monkeypatch):
    monkeypatch.setitem(chat_app.app.config, "TESTING", True)
    monkeypatch.setattr(chat_app, "messages", [])
    monkeypatch.setattr(chat_app, "next_message_id", 1)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "lab5-test-placeholder")

    model = Mock()
    model.return_value.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="测试固定回复"))]
    )
    monkeypatch.setattr(chat_app, "OpenAI", model)

    with chat_app.app.test_client() as client:
        yield client, model.return_value.chat.completions.create


def test_message_crud(client_and_model):
    client, model_call = client_and_model
    response = client.post("/api/messages", json={"message": "你好"})
    assert response.status_code == 201
    record = response.get_json()
    message_id = record["id"]
    assert record == {"id": message_id, "message": "你好", "reply": "测试固定回复"}
    model_call.assert_called_once_with(
        model="deepseek-flash",
        messages=[{"role": "user", "content": "你好"}],
    )

    response = client.get("/api/messages")
    assert response.status_code == 200
    assert response.get_json() == [record]

    response = client.patch(f"/api/messages/{message_id}", json={"message": "修改后的消息"})
    assert response.status_code == 200
    updated = {"id": message_id, "message": "修改后的消息", "reply": "测试固定回复"}
    assert response.get_json() == updated
    assert client.get("/api/messages").get_json() == [updated]

    response = client.delete(f"/api/messages/{message_id}")
    assert response.status_code == 204
    assert client.get("/api/messages").get_json() == []


def test_reject_empty_message(client_and_model):
    client, model_call = client_and_model
    response = client.post("/api/messages", json={"message": "   "})
    assert response.status_code == 400
    assert response.get_json() == {"error": "message 必须是非空字符串"}
    assert client.get("/api/messages").get_json() == []
    model_call.assert_not_called()
