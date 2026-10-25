def test_chat_record_crud(client, mock_model):
    created = client.post(
        "/api/messages",
        json={"message": "请测试 CRUD"},
    )

    assert created.status_code == 201
    assert created.get_json() == {
        "id": 1,
        "message": "请测试 CRUD",
        "reply": "固定回复",
    }
    assert mock_model == [("test-key", "请测试 CRUD")]

    listed = client.get("/api/messages")

    assert listed.status_code == 200
    assert listed.get_json() == [
        {"id": 1, "message": "请测试 CRUD", "reply": "固定回复"}
    ]

    updated = client.patch(
        "/api/messages/1",
        json={"message": "修改后的消息"},
    )

    assert updated.status_code == 200
    assert updated.get_json() == {
        "id": 1,
        "message": "修改后的消息",
        "reply": "固定回复",
    }
    assert client.get("/api/messages").get_json() == [updated.get_json()]

    deleted = client.delete("/api/messages/1")

    assert deleted.status_code == 200
    assert deleted.get_json() == {"id": 1, "deleted": True}
    assert client.get("/api/messages").get_json() == []


def test_create_rejects_record_without_message(client, mock_model):
    response = client.post("/api/messages", json={})

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "请求体需要包含非空的 message 字段"
    }
    assert client.get("/api/messages").get_json() == []
    assert mock_model == []
