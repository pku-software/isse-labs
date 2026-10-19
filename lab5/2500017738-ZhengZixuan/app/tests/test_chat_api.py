import pytest

import app as chat_app

_real_ask_deepseek = chat_app.ask_deepseek


@pytest.fixture

def client(tmp_path, monkeypatch):
    """Provide isolated in-memory records and a temporary persistence file."""
    chat_app.conversations.clear()
    monkeypatch.setattr(chat_app, "next_conversation_id", 1)
    monkeypatch.setattr(chat_app, "next_message_id", 1)
    monkeypatch.setattr(chat_app, "DATA_FILE", tmp_path / "conversations.json")
    monkeypatch.setattr(
        chat_app,
        "ask_deepseek",
        lambda history, message_text: "这是固定的测试回复",
    )
    chat_app.app.config.update(TESTING=True)
    yield chat_app.app.test_client()
    chat_app.conversations.clear()


def test_message_crud(client):
    # This app groups messages into conversations, so create one first.
    conversation_response = client.post(
        "/api/conversations", json={"title": "测试会话"}
    )
    assert conversation_response.status_code == 201
    conversation_id = conversation_response.get_json()["id"]

    # Create one user message; the model call is replaced with fixed text.
    create_response = client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={"message": "你好"},
    )
    assert create_response.status_code == 201
    created = create_response.get_json()
    assert created["messages"] == [
        {"id": 1, "role": "user", "content": "你好"},
        {"id": 2, "role": "assistant", "content": "这是固定的测试回复"},
    ]
    message_id = created["messages"][0]["id"]

    # Read the record through the application's list endpoint.
    list_response = client.get("/api/messages")
    assert list_response.status_code == 200
    assert list_response.get_json() == [
        {"id": message_id, "message": "你好", "reply": "这是固定的测试回复"}
    ]

    # Update the user message and confirm the list reflects the change.
    update_response = client.patch(
        f"/api/messages/{message_id}", json={"message": "更新后的内容"}
    )
    assert update_response.status_code == 200
    assert update_response.get_json() == {
        "id": message_id,
        "message": "更新后的内容",
        "reply": "这是固定的测试回复",
    }

    # Delete it and verify it no longer appears in the list.
    delete_response = client.delete(f"/api/messages/{message_id}")
    assert delete_response.status_code == 200
    assert client.get("/api/messages").get_json() == []


def test_empty_message_is_rejected_without_creating_record(client):
    conversation_response = client.post(
        "/api/conversations", json={"title": "非法输入测试"}
    )
    conversation_id = conversation_response.get_json()["id"]

    response = client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={"message": "   "},
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "message 不能为空"}
    conversation = client.get(f"/api/conversations/{conversation_id}").get_json()
    assert conversation["messages"] == []
    assert client.get("/api/messages").get_json() == []


def test_home_and_hello_endpoints(client):
    home_response = client.get("/")
    assert home_response.status_code == 200
    assert b"<!doctype html>" in home_response.data

    hello_response = client.get("/api/hello")
    assert hello_response.status_code == 200
    assert hello_response.get_json() == {"message": "你好"}


def test_conversation_management_and_missing_ids(client):
    create_response = client.post("/api/conversations", json={})
    assert create_response.status_code == 201
    conversation_id = create_response.get_json()["id"]
    assert create_response.get_json()["title"] == "新对话 1"

    assert client.get("/api/conversations").get_json()[0]["id"] == conversation_id
    assert client.get(f"/api/conversations/{conversation_id}").status_code == 200

    update_response = client.patch(
        f"/api/conversations/{conversation_id}", json={"title": "重命名会话"}
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["title"] == "重命名会话"

    delete_response = client.delete(f"/api/conversations/{conversation_id}")
    assert delete_response.status_code == 200
    assert client.get("/api/conversations").get_json() == []

    assert client.get("/api/conversations/999").status_code == 404
    assert client.patch("/api/conversations/999", json={"title": "不存在"}).status_code == 404
    assert client.delete("/api/conversations/999").status_code == 404
    assert client.post(
        "/api/conversations/999/messages", json={"message": "你好"}
    ).status_code == 404


def test_openai_adapter_and_missing_api_key(client, monkeypatch):
    from types import SimpleNamespace

    captured = {}

    class FakeCompletions:
        @staticmethod
        def create(**kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content="模拟模型回复"))]
            )

    fake_client = SimpleNamespace(
        chat=SimpleNamespace(completions=FakeCompletions())
    )
    monkeypatch.setattr(chat_app, "OpenAI", lambda **kwargs: fake_client)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")

    reply = _real_ask_deepseek(
        [{"role": "user", "content": "旧消息", "ignored": True}], "新消息"
    )
    assert reply == "模拟模型回复"
    assert captured["messages"] == [
        {"role": "user", "content": "旧消息"},
        {"role": "user", "content": "新消息"},
    ]
    assert captured["stream"] is False

    monkeypatch.setattr(chat_app, "ask_deepseek", _real_ask_deepseek)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    conversation_response = client.post("/api/conversations", json={})
    conversation_id = conversation_response.get_json()["id"]
    missing_key_response = client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={"message": "不会发起网络请求"},
    )
    assert missing_key_response.status_code == 500
    assert missing_key_response.get_json() == {
        "error": "服务器未配置 DeepSeek API Key"
    }
    assert client.get("/api/messages").get_json() == []
