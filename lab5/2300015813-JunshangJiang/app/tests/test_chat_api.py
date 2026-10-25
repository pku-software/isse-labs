from itertools import count

import pytest

import app as chat_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Use isolated JSON files and reset in-memory state for each test."""
    monkeypatch.setattr(chat_app, "DATA_FILE", tmp_path / "conversations.json")
    monkeypatch.setattr(chat_app, "LEGACY_FILE", tmp_path / "messages.json")
    monkeypatch.setattr(chat_app, "conversations", [])
    monkeypatch.setattr(chat_app, "conversation_ids", count(1))
    monkeypatch.setattr(chat_app, "message_ids", count(1))
    monkeypatch.setattr(
        chat_app,
        "deepseek_reply",
        lambda context: ("固定测试回复", None),
    )
    chat_app.app.config.update(TESTING=True)
    return chat_app.app.test_client()


def test_message_create_query_update_delete(client):
    created_conversation = client.post(
        "/api/conversations", json={"title": "测试会话"}
    )
    assert created_conversation.status_code == 201
    conversation_id = created_conversation.json["id"]

    created_message = client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={"message": "你好"},
    )
    assert created_message.status_code == 201
    message_id = created_message.json["id"]
    assert created_message.json["reply"] == "固定测试回复"

    queried = client.get(f"/api/conversations/{conversation_id}/messages")
    assert queried.status_code == 200
    assert queried.json == [
        {"id": message_id, "message": "你好", "reply": "固定测试回复"}
    ]

    updated = client.patch(
        f"/api/conversations/{conversation_id}/messages/{message_id}",
        json={"message": "你好，已修改"},
    )
    assert updated.status_code == 200
    assert updated.json == {
        "id": message_id,
        "message": "你好，已修改",
        "reply": "固定测试回复",
    }

    deleted = client.delete(
        f"/api/conversations/{conversation_id}/messages/{message_id}"
    )
    assert deleted.status_code == 200
    assert deleted.json == {"id": message_id, "deleted": True}
    assert client.get(
        f"/api/conversations/{conversation_id}/messages"
    ).json == []


def test_empty_message_is_rejected_without_creating_record(client):
    created_conversation = client.post(
        "/api/conversations", json={"title": "非法输入测试"}
    )
    conversation_id = created_conversation.json["id"]

    response = client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={"message": "   "},
    )

    assert response.status_code == 400
    assert response.json == {"error": "message 必须是非空字符串"}
    assert client.get(
        f"/api/conversations/{conversation_id}/messages"
    ).json == []


def test_conversation_routes_and_invalid_titles(client):
    assert client.get("/").status_code == 200
    assert client.get("/api/hello").json == {"message": "你好"}
    assert client.get("/api/conversations").json == []

    wrong_content_type = client.post("/api/conversations", data="{}")
    assert wrong_content_type.status_code == 415

    non_object = client.post("/api/conversations", json=["标题"])
    assert non_object.status_code == 400

    empty_title = client.post("/api/conversations", json={"title": "  "})
    assert empty_title.status_code == 400

    long_title = client.post("/api/conversations", json={"title": "名" * 101})
    assert long_title.status_code == 400

    created = client.post("/api/conversations", json={"title": "最初名称"})
    conversation_id = created.json["id"]
    assert client.get(f"/api/conversations/{conversation_id}").json["title"] == "最初名称"

    renamed = client.patch(
        f"/api/conversations/{conversation_id}", json={"title": "更新名称"}
    )
    assert renamed.status_code == 200
    assert renamed.json["title"] == "更新名称"
    assert client.get("/api/conversations").json == [
        {"id": conversation_id, "title": "更新名称", "message_count": 0}
    ]

    deleted = client.delete(f"/api/conversations/{conversation_id}")
    assert deleted.json == {"id": conversation_id, "deleted": True}
    assert client.get("/api/conversations").json == []


def test_missing_conversations_and_messages_return_not_found(client):
    assert client.get("/api/conversations/999").status_code == 404
    assert client.patch("/api/conversations/999", json={"title": "不存在"}).status_code == 404
    assert client.delete("/api/conversations/999").status_code == 404
    assert client.get("/api/conversations/999/messages").status_code == 404
    assert client.post(
        "/api/conversations/999/messages", json={"message": "你好"}
    ).status_code == 404
    assert client.patch(
        "/api/conversations/999/messages/1", json={"message": "修改"}
    ).status_code == 404
    assert client.delete("/api/conversations/999/messages/1").status_code == 404

    created = client.post("/api/conversations", json={"title": "空会话"})
    conversation_id = created.json["id"]
    assert client.patch(
        f"/api/conversations/{conversation_id}/messages/999",
        json={"message": "不存在"},
    ).status_code == 404
    assert client.delete(
        f"/api/conversations/{conversation_id}/messages/999"
    ).status_code == 404
    assert client.get("/missing-route").status_code == 404
