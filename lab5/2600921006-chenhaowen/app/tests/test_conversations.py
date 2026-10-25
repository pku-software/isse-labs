def test_renaming_conversation_preserves_messages(client):
    """重命名应更新会话详情和列表，并保留已有聊天记录。"""
    response = client.post("/api/conversations", json={"title": "原会话名称"})
    assert response.status_code == 201
    conversation_id = response.get_json()["id"]
    conversation_url = f"/api/conversations/{conversation_id}"

    response = client.post(
        f"{conversation_url}/messages", json={"message": "重命名前的问题"}
    )
    assert response.status_code == 201
    expected_message = {
        "id": response.get_json()["id"],
        "message": "重命名前的问题",
        "reply": "固定测试回复",
    }
    assert response.get_json() == expected_message

    response = client.patch(conversation_url, json={"title": "新会话名称"})
    assert response.status_code == 200
    expected_conversation = {
        "id": conversation_id,
        "title": "新会话名称",
        "messages": [expected_message],
    }
    assert response.get_json() == expected_conversation

    response = client.get(conversation_url)
    assert response.status_code == 200
    assert response.get_json() == expected_conversation

    response = client.get("/api/conversations")
    assert response.status_code == 200
    assert {
        "id": conversation_id,
        "title": "新会话名称",
        "message_count": 1,
    } in response.get_json()
