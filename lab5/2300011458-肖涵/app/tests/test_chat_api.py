import importlib

import pytest


@pytest.fixture
def app_client(tmp_path, monkeypatch):
    monkeypatch.setenv("LAB5_DATA_DIR", str(tmp_path))
    module = importlib.import_module("app")
    module = importlib.reload(module)
    assert module.DATA_FILE == tmp_path / "conversations.json"
    module.app.config["TESTING"] = True
    return module.app.test_client(), module


def create_test_conversation(client):
    response = client.post("/api/conversations", json={"title": "测试会话"})
    assert response.status_code == 201
    return response.get_json()["id"]


def test_one_chat_record_create_read_update_delete(app_client, monkeypatch):
    client, module = app_client
    monkeypatch.setattr(module, "get_deepseek_reply", lambda history: "固定回复")
    conversation_id = create_test_conversation(client)

    created = client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={"message": "你好"},
    )
    assert created.status_code == 201
    assert created.get_json()["assistant_message"]["content"] == "固定回复"
    message_id = created.get_json()["user_message"]["id"]

    queried = client.get(f"/api/conversations/{conversation_id}")
    assert queried.status_code == 200
    assert [item["content"] for item in queried.get_json()["messages"]] == [
        "你好",
        "固定回复",
    ]

    updated = client.patch(
        f"/api/conversations/{conversation_id}/messages/{message_id}",
        json={"message": "改写的问题"},
    )
    assert updated.status_code == 200
    assert updated.get_json()["content"] == "改写的问题"
    queried_again = client.get(f"/api/conversations/{conversation_id}")
    assert [item["content"] for item in queried_again.get_json()["messages"]] == [
        "改写的问题",
        "固定回复",
    ]

    deleted = client.delete(
        f"/api/conversations/{conversation_id}/messages/{message_id}"
    )
    assert deleted.status_code == 204
    after_delete = client.get(f"/api/conversations/{conversation_id}")
    assert after_delete.get_json()["messages"] == []

    renamed = client.patch(
        f"/api/conversations/{conversation_id}",
        json={"title": "已完成会话"},
    )
    assert renamed.status_code == 200
    assert renamed.get_json()["title"] == "已完成会话"
    listed = client.get("/api/conversations")
    assert listed.get_json() == [
        {"id": conversation_id, "title": "已完成会话", "message_count": 0}
    ]

    removed = client.delete(f"/api/conversations/{conversation_id}")
    assert removed.status_code == 204
    assert client.get(f"/api/conversations/{conversation_id}").status_code == 404


def test_blank_message_is_rejected_without_creating_record(app_client, monkeypatch):
    client, module = app_client
    model_calls = []

    def fake_reply(history):
        model_calls.append(history)
        return "固定回复"

    monkeypatch.setattr(module, "get_deepseek_reply", fake_reply)
    conversation_id = create_test_conversation(client)

    response = client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={"message": ""},
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "message 必须是非空字符串"
    assert client.get(f"/api/conversations/{conversation_id}").get_json()["messages"] == []
    assert model_calls == []
