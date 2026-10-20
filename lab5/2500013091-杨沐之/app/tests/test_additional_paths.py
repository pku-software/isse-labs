def test_basic_message_crud(client, reply_mock):
    # 保留的基础消息接口同样属于本人的后端代码。
    response = client.post("/api/messages", json={"message": "   "})
    assert response.status_code == 400
    assert response.get_json() == {"error": "message 必须是非空字符串"}
    assert client.get("/api/messages").get_json() == []
    reply_mock.assert_not_called()

    response = client.post("/api/messages", json={"message": "基础消息"})
    assert response.status_code == 201
    record = response.get_json()
    message_id = record["id"]
    assert record["message"] == "基础消息"
    assert record["reply"] == "测试固定回复"
    message_url = f"/api/messages/{message_id}"

    response = client.get("/api/messages")
    assert response.status_code == 200
    assert response.get_json() == [record]

    # 非法修改不能破坏已有记录。
    response = client.patch(message_url, json={"message": "   "})
    assert response.status_code == 400
    assert response.get_json() == {"error": "message 必须是非空字符串"}
    assert client.get("/api/messages").get_json() == [record]

    response = client.patch(message_url, json={"message": "基础消息已修改"})
    assert response.status_code == 200
    updated_record = dict(record, message="基础消息已修改")
    assert response.get_json() == updated_record
    assert client.get("/api/messages").get_json() == [updated_record]

    response = client.delete(message_url)
    assert response.status_code == 200
    assert response.get_json() == {"message": "聊天记录已删除", "id": message_id}
    assert client.get("/api/messages").get_json() == []

    # 已删除的记录不能再修改或删除。
    response = client.patch(message_url, json={"message": "不存在的记录"})
    assert response.status_code == 404
    assert response.get_json() == {"error": "聊天记录不存在"}
    response = client.delete(message_url)
    assert response.status_code == 404
    assert response.get_json() == {"error": "聊天记录不存在"}
    reply_mock.assert_called_once_with([{"role": "user", "content": "基础消息"}])


def test_conversation_management_and_persistence(client, app_module, reply_mock):
    response = client.post("/api/conversations", json={"title": "原始标题"})
    assert response.status_code == 201
    conversation_id = response.get_json()["id"]
    conversation_url = f"/api/conversations/{conversation_id}"

    response = client.get("/api/conversations")
    assert response.status_code == 200
    assert response.get_json() == [
        {"id": conversation_id, "title": "原始标题", "message_count": 0}
    ]

    response = client.patch(conversation_url, json={"title": "重命名后"})
    assert response.status_code == 200
    renamed = {"id": conversation_id, "title": "重命名后", "messages": []}
    assert response.get_json() == renamed
    response = client.get(conversation_url)
    assert response.status_code == 200
    assert response.get_json() == renamed

    # 从临时 JSON 文件重新读取，验证更名已经保存。
    assert app_module.data_path.is_file()
    assert app_module.load_conversations() == [renamed]

    response = client.delete(conversation_url)
    assert response.status_code == 200
    assert response.get_json() == {"message": "会话已删除", "id": conversation_id}
    response = client.get(conversation_url)
    assert response.status_code == 404
    assert response.get_json() == {"error": "会话不存在"}
    response = client.get("/api/conversations")
    assert response.status_code == 200
    assert response.get_json() == []
    assert app_module.load_conversations() == []
    reply_mock.assert_not_called()
