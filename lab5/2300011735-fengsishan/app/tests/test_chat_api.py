def test_chat_record_crud(client, mock_model):
    """一条记录从创建、查询、修改到删除，逐步核对实际数据。"""
    assert client.get("/api/messages").get_json() == []

    created = client.post("/api/messages", json={"message": "  你好，Lab5  "})
    assert created.status_code == 201
    record = created.get_json()
    message_id = record["id"]
    assert isinstance(message_id, int)
    assert record["message"] == "你好，Lab5"
    assert record["reply"] == "这是测试中的固定回复"

    listed = client.get("/api/messages")
    assert listed.status_code == 200
    assert listed.get_json() == [record]

    updated = client.patch(
        f"/api/messages/{message_id}",
        json={"message": "  修改后的消息  "},
    )
    assert updated.status_code == 200
    expected_record = {**record, "message": "修改后的消息"}
    assert updated.get_json() == expected_record
    assert client.get("/api/messages").get_json() == [expected_record]

    deleted = client.delete(f"/api/messages/{message_id}")
    assert deleted.status_code == 200
    assert deleted.get_json() == {"id": message_id, "message": "删除成功"}
    assert client.get("/api/messages").get_json() == []
    mock_model.assert_called_once()


def test_empty_message_rejected(client, mock_model):
    """空白消息应被拒绝，且不会新增记录或调用模型。"""
    assert client.get("/api/messages").get_json() == []

    response = client.post("/api/messages", json={"message": "  \t\n  "})

    assert response.status_code == 400
    assert response.get_json() == {"error": "message 必须是非空字符串"}
    assert client.get("/api/messages").get_json() == []
    mock_model.assert_not_called()
