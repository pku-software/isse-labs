def test_message_crud(client_and_model):
    client, model = client_and_model
    assert client.get("/api/messages").get_json() == []

    # 创建：检查状态码、实际内容以及模型收到的输入。
    response = client.post("/api/messages", json={"message": "你好"})
    assert response.status_code == 201
    record = response.get_json()
    message_id = record["id"]
    assert isinstance(message_id, int)
    assert record == {
        "id": message_id,
        "message": "你好",
        "reply": "这是固定的测试回复",
    }
    model.assert_called_once_with("你好")

    # 查询：响应中确实存在刚创建的记录。
    response = client.get("/api/messages")
    assert response.status_code == 200
    assert response.get_json() == [record]

    # 修改：再次查询，确认修改已保存；当前接口只修改用户消息。
    response = client.patch(
        f"/api/messages/{message_id}", json={"message": "修改后的消息"}
    )
    assert response.status_code == 200
    updated = {**record, "message": "修改后的消息"}
    assert response.get_json() == updated
    assert client.get("/api/messages").get_json() == [updated]

    # 删除：返回成功之后，记录也应当真正消失。
    response = client.delete(f"/api/messages/{message_id}")
    assert response.status_code == 200
    assert response.get_json() == updated
    assert client.get("/api/messages").get_json() == []
    model.assert_called_once_with("你好")


def test_empty_message_is_rejected(client_and_model):
    client, model = client_and_model
    response = client.post("/api/messages", json={"message": "   "})

    assert response.status_code == 400
    assert "非空字符串" in response.get_json()["error"]
    assert client.get("/api/messages").get_json() == []
    model.assert_not_called()
