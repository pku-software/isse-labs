import json


def test_message_crud(client, chat_app):
    module, model_mock = chat_app
    assert client.get("/api/messages").get_json() == {"messages": []}

    created = client.post("/api/messages", json={"message": "  测试消息  "})
    assert created.status_code == 201
    record = created.get_json()
    message_id = record["id"]
    assert isinstance(message_id, int)
    assert record["message"] == "测试消息"
    assert record["reply"] == "固定测试回复"
    model_mock.assert_called_once_with("测试消息")

    listed = client.get("/api/messages")
    assert listed.status_code == 200
    assert listed.get_json() == {"messages": [record]}

    updated = client.patch(
        f"/api/messages/{message_id}", json={"message": "修改后的消息"}
    )
    assert updated.status_code == 200
    expected = {**record, "message": "修改后的消息"}
    assert updated.get_json() == expected
    assert client.get("/api/messages").get_json() == {"messages": [expected]}
    assert json.loads(module.DATA_FILE.read_text(encoding="utf-8")) == [expected]

    deleted = client.delete(f"/api/messages/{message_id}")
    assert deleted.status_code == 200
    assert deleted.get_json() == {"message": "聊天记录已删除。", "id": message_id}
    assert client.get("/api/messages").get_json() == {"messages": []}
    assert json.loads(module.DATA_FILE.read_text(encoding="utf-8")) == []


def test_empty_message_is_rejected(client, chat_app):
    module, model_mock = chat_app
    response = client.post("/api/messages", json={"message": "   "})
    assert response.status_code == 400
    assert response.get_json() == {"error": "message 不能为空，且必须是文本。"}
    assert client.get("/api/messages").get_json() == {"messages": []}
    assert not module.DATA_FILE.exists()
    model_mock.assert_not_called()
