import app as app_module
from app import app


def fixed_reply(_user_message):
    return "固定回复", None


def setup_function():
    app_module.messages.clear()
    app_module.next_id = 1
    app_module._original_request_reply = app_module.request_reply
    app_module.request_reply = fixed_reply


def teardown_function():
    app_module.messages.clear()
    app_module.next_id = 1
    app_module.request_reply = app_module._original_request_reply


def test_message_crud():
    client = app.test_client()

    created = client.post("/api/messages", json={"message": "你好"})
    assert created.status_code == 201
    record = created.get_json()
    assert record["message"] == "你好"
    assert record["reply"] == "固定回复"
    message_id = record["id"]

    listed = client.get("/api/messages")
    assert listed.status_code == 200
    records = listed.get_json()
    assert len(records) == 1
    assert records[0]["id"] == message_id
    assert records[0]["message"] == "你好"
    assert records[0]["reply"] == "固定回复"

    updated = client.patch(
        f"/api/messages/{message_id}",
        json={"message": "修改后的消息"},
    )
    assert updated.status_code == 200
    assert updated.get_json()["message"] == "修改后的消息"
    assert updated.get_json()["id"] == message_id

    deleted = client.delete(f"/api/messages/{message_id}")
    assert deleted.status_code == 200
    assert deleted.get_json()["id"] == message_id

    remaining = client.get("/api/messages")
    assert remaining.status_code == 200
    assert remaining.get_json() == []


def test_reject_empty_message():
    client = app.test_client()

    rejected = client.post("/api/messages", json={"message": "   "})
    assert rejected.status_code == 400
    assert rejected.get_json()["error"] == "message 不能为空"

    remaining = client.get("/api/messages")
    assert remaining.status_code == 200
    assert remaining.get_json() == []
