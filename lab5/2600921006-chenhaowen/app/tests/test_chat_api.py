def test_chat_record_crud(client):
    """同一条记录应能创建、查到、修改，并在删除后消失。"""
    conversation_response = client.post(
        "/api/conversations", json={"title": "CRUD 测试"}
    )
    assert conversation_response.status_code == 201
    conversation_id = conversation_response.get_json()["id"]
    messages_url = f"/api/conversations/{conversation_id}/messages"

    # 创建：ID 使用实际返回值，同时核对问题与固定模型回复。
    response = client.post(messages_url, json={"message": "原始问题"})
    assert response.status_code == 201
    message_id = response.get_json()["id"]
    expected = {
        "id": message_id,
        "message": "原始问题",
        "reply": "固定测试回复",
    }
    assert response.get_json() == expected

    response = client.get(messages_url)
    assert response.status_code == 200
    assert response.get_json() == [expected]

    # 修改后重新查询，确认真正保存了新问题，并保留原有回复。
    record_url = f"{messages_url}/{message_id}"
    response = client.patch(record_url, json={"message": "修改后的问题"})
    assert response.status_code == 200
    expected_updated = {
        "id": message_id,
        "message": "修改后的问题",
        "reply": "固定测试回复",
    }
    assert response.get_json() == expected_updated

    response = client.get(messages_url)
    assert response.status_code == 200
    assert response.get_json() == [expected_updated]

    # 删除不能只看成功状态，还要确认记录已经消失。
    response = client.delete(record_url)
    assert response.status_code == 200
    assert response.get_json() == {"id": message_id, "deleted": True}

    response = client.get(messages_url)
    assert response.status_code == 200
    assert response.get_json() == []


def test_blank_message_is_rejected_without_creating_record(client):
    """空白消息应返回错误，且不能产生聊天记录。"""
    conversation_response = client.post(
        "/api/conversations", json={"title": "非法输入测试"}
    )
    assert conversation_response.status_code == 201
    conversation_id = conversation_response.get_json()["id"]
    messages_url = f"/api/conversations/{conversation_id}/messages"

    response = client.get(messages_url)
    assert response.status_code == 200
    assert response.get_json() == []

    response = client.post(messages_url, json={"message": "   "})
    assert response.status_code == 400
    assert response.get_json() == {"error": "message 必须是非空字符串"}

    response = client.get(messages_url)
    assert response.status_code == 200
    assert response.get_json() == []
