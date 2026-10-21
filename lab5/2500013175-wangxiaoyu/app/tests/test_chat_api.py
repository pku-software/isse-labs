import importlib
from unittest.mock import Mock

import pytest


@pytest.fixture
def chat_api(monkeypatch, tmp_path):
    # Configure storage before importing or reloading the app's saved data.
    monkeypatch.setenv("LAB5_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("DEEPSEEK_API_KEY", "lab5-test-placeholder")
    app_module = importlib.import_module("app")
    app_module = importlib.reload(app_module)
    app_module.app.config.update(TESTING=True)

    reply_mock = Mock(return_value="这是固定的测试回复")
    monkeypatch.setattr(app_module, "generate_reply", reply_mock)
    with app_module.app.test_client() as client:
        yield client, reply_mock


def test_conversation_message_crud(chat_api):
    client, reply_mock = chat_api

    response = client.post("/api/conversations", json={"title": "CRUD 测试"})
    assert response.status_code == 201
    conversation_id = response.get_json()["id"]
    conversation_url = f"/api/conversations/{conversation_id}"

    # Create a question and its mocked answer; IDs come from this response.
    response = client.post(
        f"{conversation_url}/messages", json={"message": "  你好  "}
    )
    assert response.status_code == 201
    record = response.get_json()
    user_message = record["user_message"]
    assistant_message = record["assistant_message"]
    assert user_message["content"] == "你好"
    assert assistant_message["content"] == "这是固定的测试回复"
    reply_mock.assert_called_once_with([{"role": "user", "content": "你好"}])

    # Read and verify the actual stored question and answer.
    response = client.get(conversation_url)
    assert response.status_code == 200
    assert response.get_json()["messages"] == [user_message, assistant_message]

    # Update the question and read it back.
    message_url = f"{conversation_url}/messages/{user_message['id']}"
    response = client.patch(message_url, json={"message": "修改后的问题"})
    assert response.status_code == 200
    assert response.get_json()["content"] == "修改后的问题"
    response = client.get(conversation_url)
    assert response.status_code == 200
    assert response.get_json()["messages"][0]["content"] == "修改后的问题"
    assert response.get_json()["messages"][1] == assistant_message

    # Deleting a question removes the complete question-answer pair.
    response = client.delete(message_url)
    assert response.status_code == 200
    assert response.get_json() == {"message": "问答已删除"}
    response = client.get(conversation_url)
    assert response.status_code == 200
    assert response.get_json()["messages"] == []


def test_empty_message_is_rejected(chat_api):
    client, reply_mock = chat_api
    response = client.post("/api/conversations", json={"title": "非法输入测试"})
    assert response.status_code == 201
    conversation_id = response.get_json()["id"]
    conversation_url = f"/api/conversations/{conversation_id}"

    response = client.post(
        f"{conversation_url}/messages", json={"message": "   "}
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "message 不能为空"}
    reply_mock.assert_not_called()

    response = client.get(conversation_url)
    assert response.status_code == 200
    assert response.get_json()["messages"] == []


def test_basic_message_crud(chat_api):
    """The retained standalone-message API is also part of the backend."""
    client, reply_mock = chat_api
    response = client.post("/api/messages", json={"message": "基础接口问题"})
    assert response.status_code == 201
    record = response.get_json()
    assert record["message"] == "基础接口问题"
    assert record["reply"] == "这是固定的测试回复"
    reply_mock.assert_called_once_with(
        [{"role": "user", "content": "基础接口问题"}]
    )

    response = client.get("/api/messages")
    assert response.status_code == 200
    assert response.get_json() == [record]

    message_url = f"/api/messages/{record['id']}"
    response = client.patch(message_url, json={"message": "更新后的基础问题"})
    assert response.status_code == 200
    updated_record = {**record, "message": "更新后的基础问题"}
    assert response.get_json() == updated_record
    response = client.get("/api/messages")
    assert response.status_code == 200
    assert response.get_json() == [updated_record]

    response = client.delete(message_url)
    assert response.status_code == 200
    assert response.get_json() == {"message": "聊天记录已删除"}
    response = client.get("/api/messages")
    assert response.status_code == 200
    assert response.get_json() == []


def test_conversation_management(chat_api):
    """A renamed or deleted conversation must be reflected in later reads."""
    client, reply_mock = chat_api
    response = client.post("/api/conversations", json={"title": "原会话标题"})
    assert response.status_code == 201
    conversation_id = response.get_json()["id"]
    conversation_url = f"/api/conversations/{conversation_id}"

    response = client.get("/api/conversations")
    assert response.status_code == 200
    assert response.get_json() == [
        {"id": conversation_id, "title": "原会话标题", "message_count": 0}
    ]

    response = client.patch(conversation_url, json={"title": "重命名后的会话"})
    assert response.status_code == 200
    assert response.get_json()["title"] == "重命名后的会话"
    response = client.get(conversation_url)
    assert response.status_code == 200
    assert response.get_json()["title"] == "重命名后的会话"
    response = client.get("/api/conversations")
    assert response.status_code == 200
    assert response.get_json() == [
        {"id": conversation_id, "title": "重命名后的会话", "message_count": 0}
    ]

    response = client.delete(conversation_url)
    assert response.status_code == 200
    assert response.get_json() == {"message": "会话已删除"}
    response = client.get(conversation_url)
    assert response.status_code == 404
    assert response.get_json() == {"error": "会话不存在"}
    response = client.get("/api/conversations")
    assert response.status_code == 200
    assert response.get_json() == []
    reply_mock.assert_not_called()
