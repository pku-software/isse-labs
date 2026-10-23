"""Check the record lifecycle and rejection of an empty message."""


def test_chat_record_crud(client, model_request):
    assert client.get("/api/messages").get_json() == []

    created = client.post("/api/messages", json={"message": "  测试消息  "})
    assert created.status_code == 201
    record = created.get_json()
    record_id = record["id"]
    assert isinstance(record_id, int)
    assert record["message"] == "测试消息"
    assert record["reply"] == "固定测试回复"
    assert client.get("/api/messages").get_json() == [record]

    updated = client.patch(
        f"/api/messages/{record_id}", json={"message": "  修改后的消息  "}
    )
    assert updated.status_code == 200
    changed = updated.get_json()
    assert changed == {
        "id": record_id, "message": "修改后的消息", "reply": "固定测试回复"
    }
    assert client.get("/api/messages").get_json() == [changed]

    deleted = client.delete(f"/api/messages/{record_id}")
    assert deleted.status_code == 204
    assert client.get("/api/messages").get_json() == []
    model_request.assert_called_once()
    sent_message = model_request.call_args.kwargs["json"]["messages"][0]["content"]
    assert sent_message == "测试消息"


def test_empty_message_is_rejected_without_creating_record(client, chat_module):
    rejected = client.post("/api/messages", json={"message": "   "})
    assert rejected.status_code == 400
    assert rejected.get_json() == {"error": "message 必须是非空字符串"}
    assert client.get("/api/messages").get_json() == []
    chat_module.requests.post.assert_not_called()
