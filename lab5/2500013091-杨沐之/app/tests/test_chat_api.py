def test_conversation_message_crud(client, reply_mock):
    # 多会话应用先创建会话，ID 从真实响应取得。
    response = client.post("/api/conversations", json={"title": "CRUD 测试"})
    assert response.status_code == 201
    conversation_id = response.get_json()["id"]
    conversation_url = f"/api/conversations/{conversation_id}"

    response = client.post(
        f"{conversation_url}/messages", json={"message": "你好"}
    )
    assert response.status_code == 201
    records = response.get_json()["messages"]
    assert len(records) == 2
    user_record, assistant_record = records
    turn_id = user_record["turn_id"]
    assert user_record["role"] == "user"
    assert user_record["content"] == "你好"
    assert assistant_record["role"] == "assistant"
    assert assistant_record["content"] == "测试固定回复"
    assert assistant_record["turn_id"] == turn_id
    assert user_record["id"] != assistant_record["id"]
    reply_mock.assert_called_once_with([{"role": "user", "content": "你好"}])

    response = client.get(conversation_url)
    assert response.status_code == 200
    assert response.get_json()["messages"] == records

    turn_url = f"{conversation_url}/turns/{turn_id}"
    response = client.patch(turn_url, json={"message": "修改后的消息"})
    assert response.status_code == 200
    response = client.get(conversation_url)
    assert response.status_code == 200
    updated_records = response.get_json()["messages"]
    assert len(updated_records) == 2
    assert updated_records[0]["id"] == user_record["id"]
    assert updated_records[0]["content"] == "修改后的消息"
    # 当前应用修改用户消息时，保留原来的模型回复。
    assert updated_records[1] == assistant_record

    response = client.delete(turn_url)
    assert response.status_code == 200
    response = client.get(conversation_url)
    assert response.status_code == 200
    assert response.get_json()["messages"] == []
    assert reply_mock.call_count == 1


def test_empty_message_is_rejected(client, reply_mock):
    response = client.post("/api/conversations", json={"title": "非法输入测试"})
    assert response.status_code == 201
    conversation_id = response.get_json()["id"]
    conversation_url = f"/api/conversations/{conversation_id}"

    response = client.post(
        f"{conversation_url}/messages", json={"message": "   "}
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "message 必须是非空字符串"}

    # 拒绝请求后再次查询，确认没有新增聊天记录，也未调用模型。
    response = client.get(conversation_url)
    assert response.status_code == 200
    assert response.get_json()["messages"] == []
    reply_mock.assert_not_called()
