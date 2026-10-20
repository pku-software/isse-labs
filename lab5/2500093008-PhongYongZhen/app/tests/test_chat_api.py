"""Exercise the chat API without contacting an external model."""

import json

import app as chat_app
import pytest


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(chat_app, "DATA_DIR", tmp_path)
    monkeypatch.setattr(chat_app, "CONVERSATIONS_FILE", tmp_path / "conversations.json")
    monkeypatch.setattr(chat_app, "conversations", [])
    monkeypatch.setattr(chat_app, "next_conversation_id", 1)
    monkeypatch.setattr(chat_app, "next_message_id", 1)
    monkeypatch.setattr(chat_app, "ask_deepseek", lambda history, message: "固定测试回复")
    return chat_app.app.test_client()


def test_chat_record_crud(client, tmp_path):
    created_session = client.post("/api/conversations", json={"title": "测试会话"})
    assert created_session.status_code == 201
    session_id = created_session.get_json()["id"]

    created = client.post(
        f"/api/conversations/{session_id}/messages", json={"message": "第一条消息"}
    )
    assert created.status_code == 201
    record_id = created.get_json()["id"]
    assert created.get_json()["reply"] == "固定测试回复"

    session = client.get(f"/api/conversations/{session_id}").get_json()
    assert session["messages"] == [created.get_json()]

    updated = client.patch(f"/api/messages/{record_id}", json={"message": "修改后的消息"})
    assert updated.status_code == 200
    assert updated.get_json()["message"] == "修改后的消息"
    assert client.get(f"/api/conversations/{session_id}").get_json()["messages"][0]["message"] == "修改后的消息"

    deleted = client.delete(f"/api/messages/{record_id}")
    assert deleted.status_code == 200
    assert deleted.get_json() == {"deleted_id": record_id}
    assert client.get(f"/api/conversations/{session_id}").get_json()["messages"] == []
    assert (tmp_path / "conversations.json").is_file()


def test_blank_message_is_rejected_without_creating_record(client):
    session_id = client.post("/api/conversations", json={"title": "空输入测试"}).get_json()["id"]
    response = client.post(f"/api/conversations/{session_id}/messages", json={"message": "   "})
    assert response.status_code == 400
    assert "message 字段不能为空" in response.get_json()["error"]
    assert client.get(f"/api/conversations/{session_id}").get_json()["messages"] == []


def test_saved_conversation_is_restored_and_ids_continue(client, tmp_path):
    session_id = client.post("/api/conversations", json={"title": "原会话"}).get_json()["id"]
    message_id = client.post(
        f"/api/conversations/{session_id}/messages", json={"message": "保存内容"}
    ).get_json()["id"]
    chat_app.conversations = []
    chat_app.next_conversation_id = 1
    chat_app.next_message_id = 1
    chat_app.load_data()
    assert chat_app.conversations[0]["messages"][0]["message"] == "保存内容"
    assert chat_app.next_conversation_id == session_id + 1
    assert chat_app.next_message_id == message_id + 1
    assert json.loads((tmp_path / "conversations.json").read_text())[0]["id"] == session_id


def test_conversation_management_and_missing_ids(client):
    assert client.get("/api/conversations").get_json() == []
    assert client.get("/api/conversations/999").status_code == 404
    assert client.patch("/api/conversations/999", json={"title": "无效"}).status_code == 404
    assert client.delete("/api/conversations/999").status_code == 404
    assert client.delete("/api/messages/999").status_code == 404

    session_id = client.post("/api/conversations", json={}).get_json()["id"]
    assert client.patch(f"/api/conversations/{session_id}", json={"title": " "}).status_code == 400
    renamed = client.patch(f"/api/conversations/{session_id}", json={"title": " 新名字 "})
    assert renamed.get_json()["title"] == "新名字"
    assert client.delete(f"/api/conversations/{session_id}").get_json() == {"deleted_id": session_id}
    assert client.get("/api/conversations").get_json() == []


def test_model_failure_does_not_save_message(client, monkeypatch):
    session_id = client.post("/api/conversations", json={"title": "失败测试"}).get_json()["id"]

    def unavailable(_history, _message):
        raise RuntimeError("模型暂不可用")

    monkeypatch.setattr(chat_app, "ask_deepseek", unavailable)
    response = client.post(f"/api/conversations/{session_id}/messages", json={"message": "你好"})
    assert response.status_code == 502
    assert "模型暂不可用" in response.get_json()["error"]
    assert client.get(f"/api/conversations/{session_id}").get_json()["messages"] == []
