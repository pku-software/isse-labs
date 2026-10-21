"""补充覆盖会话管理与 JSON 持久化读取。"""


def test_conversation_lifecycle_and_persistence(client, ai_reply, app_module):
    response = client.post("/api/conversations", json={"title": "持久化测试"})
    assert response.status_code == 201
    conversation_id = response.get_json()["id"]
    url = f"/api/conversations/{conversation_id}"

    response = client.post(f"{url}/messages", json={"message": "需要保存的问题"})
    assert response.status_code == 201
    record = response.get_json()
    assert record["message"] == "需要保存的问题"
    assert record["reply"] == "这是测试用的固定回复"
    ai_reply.assert_called_once_with("需要保存的问题", [])

    # 从临时 JSON 文件重新读取，检查完整会话与消息确实保存。
    expected = {"id": conversation_id, "title": "持久化测试", "messages": [record]}
    assert app_module.load_conversations() == {conversation_id: expected}
    response = client.get(url)
    assert response.status_code == 200
    assert response.get_json() == expected

    response = client.patch(url, json={"title": "已重命名"})
    assert response.status_code == 200
    expected = {**expected, "title": "已重命名"}
    assert response.get_json() == expected
    assert app_module.load_conversations() == {conversation_id: expected}

    response = client.get("/api/conversations")
    assert response.status_code == 200
    assert response.get_json() == [
        {"id": conversation_id, "title": "已重命名", "message_count": 1}
    ]

    response = client.delete(url)
    assert response.status_code == 204
    response = client.get(url)
    assert response.status_code == 404
    assert response.get_json() == {"error": "找不到这个会话，请刷新列表后重试"}
    response = client.get("/api/conversations")
    assert response.status_code == 200
    assert response.get_json() == []
    assert app_module.load_conversations() == {}
