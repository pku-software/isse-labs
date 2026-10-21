"""两个重点：一条聊天记录的 CRUD，以及空消息的拒绝处理。"""


def create_conversation(client):
    response = client.post("/api/conversations", json={"title": "测试会话"})
    assert response.status_code == 201
    return response.get_json()["id"]


def test_chat_record_crud(client, ai_reply):
    conversation_id = create_conversation(client)
    messages_url = f"/api/conversations/{conversation_id}/messages"

    # 创建：模型回复固定，检查实际返回的消息和回复。
    response = client.post(messages_url, json={"message": "你好"})
    assert response.status_code == 201
    record = response.get_json()
    message_id = record["id"]
    assert record["message"] == "你好"
    assert record["reply"] == "这是测试用的固定回复"
    ai_reply.assert_called_once_with("你好", [])

    # 查询：刚创建的完整记录应出现在该会话中。
    response = client.get(messages_url)
    assert response.status_code == 200
    assert response.get_json() == [record]

    # 修改：按应用原有行为，只更新问题，保留原回答。
    record_url = f"{messages_url}/{message_id}"
    response = client.patch(record_url, json={"message": "修改后的问题"})
    assert response.status_code == 200
    expected = {**record, "message": "修改后的问题"}
    assert response.get_json() == expected
    response = client.get(messages_url)
    assert response.status_code == 200
    assert response.get_json() == [expected]
    assert ai_reply.call_count == 1

    # 删除：除了状态码，还要确认记录确实消失。
    response = client.delete(record_url)
    assert response.status_code == 204
    response = client.get(messages_url)
    assert response.status_code == 200
    assert response.get_json() == []


def test_empty_message_is_rejected(client, ai_reply):
    conversation_id = create_conversation(client)
    messages_url = f"/api/conversations/{conversation_id}/messages"

    response = client.post(messages_url, json={"message": ""})
    assert response.status_code == 400
    assert response.get_json() == {"error": "message 必须是非空字符串"}
    ai_reply.assert_not_called()

    # 输入被拒绝后，不应留下聊天记录。
    response = client.get(messages_url)
    assert response.status_code == 200
    assert response.get_json() == []
