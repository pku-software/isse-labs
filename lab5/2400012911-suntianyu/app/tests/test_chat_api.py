"""检查聊天记录 CRUD 与空消息输入。"""

import json


def test_chat_record_crud(client, app_module, model_reply):
    assert client.get("/api/messages").get_json() == []

    created = client.post("/api/messages", json={"message": "你好"})
    assert created.status_code == 201
    record = created.get_json()
    record_id = record["id"]
    assert isinstance(record_id, int) and record_id > 0
    assert record["message"] == "你好"
    assert record["reply"] == "这是模拟的模型回复"
    model_reply.assert_called_once_with("你好")

    listed = client.get("/api/messages")
    assert listed.status_code == 200
    assert listed.get_json() == [record]
    assert json.loads(app_module.DATA_FILE.read_text(encoding="utf-8")) == [record]

    updated = client.patch(
        f"/api/messages/{record_id}", json={"message": "修改后的消息"}
    )
    expected = {**record, "message": "修改后的消息"}
    assert updated.status_code == 200
    assert updated.get_json() == expected
    assert client.get("/api/messages").get_json() == [expected]
    assert json.loads(app_module.DATA_FILE.read_text(encoding="utf-8")) == [expected]
    model_reply.assert_called_once_with("你好")

    deleted = client.delete(f"/api/messages/{record_id}")
    assert deleted.status_code == 200
    assert deleted.get_json()["id"] == record_id
    assert client.get("/api/messages").get_json() == []
    assert json.loads(app_module.DATA_FILE.read_text(encoding="utf-8")) == []


def test_empty_message_is_rejected(client, app_module, model_reply):
    before = client.get("/api/messages").get_json()
    response = client.post("/api/messages", json={"message": "   "})
    assert response.status_code == 400
    assert response.get_json() == {
        "error": "请提交 JSON 对象，message 必须是非空字符串。"
    }
    assert client.get("/api/messages").get_json() == before
    assert not app_module.DATA_FILE.exists()
    model_reply.assert_not_called()
