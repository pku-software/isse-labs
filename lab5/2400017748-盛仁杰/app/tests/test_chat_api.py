def test_message_crud(chat_client):
    client, model = chat_client

    response = client.post("/api/messages", json={"message": "你好"})
    assert response.status_code == 201
    record = response.get_json()
    message_id = record["id"]
    assert record == {
        "id": message_id,
        "message": "你好",
        "reply": "固定测试回复",
    }
    model.return_value.chat.completions.create.assert_called_once_with(
        model="deepseek-v4-pro",
        messages=[{"role": "user", "content": "你好"}],
    )

    response = client.get("/api/messages")
    assert response.status_code == 200
    assert response.get_json() == [record]

    response = client.patch(
        f"/api/messages/{message_id}", json={"message": "修改后的消息"}
    )
    assert response.status_code == 200
    updated = {**record, "message": "修改后的消息"}
    assert response.get_json() == updated
    assert client.get("/api/messages").get_json() == [updated]

    response = client.delete(f"/api/messages/{message_id}")
    assert response.status_code == 200
    assert response.get_json() == {"message": "删除成功"}
    assert client.get("/api/messages").get_json() == []


def test_empty_message_is_rejected(chat_client):
    client, model = chat_client

    response = client.post("/api/messages", json={"message": "   "})

    assert response.status_code == 400
    assert response.get_json() == {"error": "message 不能为空"}
    assert client.get("/api/messages").get_json() == []
    model.assert_not_called()


def test_conversation_lifecycle(chat_client):
    client, model = chat_client

    response = client.post("/api/conversations", json={"title": "测试会话"})
    assert response.status_code == 201
    conversation = response.get_json()
    conversation_id = conversation["id"]
    assert conversation == {
        "id": conversation_id, "title": "测试会话", "messages": []
    }

    response = client.post(
        f"/api/conversations/{conversation_id}/messages", json={"message": "你好"}
    )
    assert response.status_code == 200
    assert response.get_json() == {"message": "你好", "reply": "固定测试回复"}
    model.return_value.chat.completions.create.assert_called_once_with(
        model="deepseek-v4-pro",
        messages=[{"role": "user", "content": "你好"}],
    )
    conversation["messages"] = [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "固定测试回复"},
    ]
    response = client.get("/api/conversations")
    assert response.status_code == 200
    assert response.get_json() == [conversation]

    response = client.patch(
        f"/api/conversations/{conversation_id}", json={"title": "已改名"}
    )
    assert response.status_code == 200
    conversation["title"] = "已改名"
    assert response.get_json() == conversation
    assert client.get("/api/conversations").get_json() == [conversation]

    response = client.delete(f"/api/conversations/{conversation_id}")
    assert response.status_code == 200
    assert response.get_json() == {"message": "删除成功"}
    assert client.get("/api/conversations").get_json() == []
