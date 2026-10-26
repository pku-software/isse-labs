import app as chat_app


def test_message_crud(client):
    # 创建记录
    resp = client.post("/api/messages", json={"message": "你好，测试"})
    assert resp.status_code == 201
    record = resp.get_json()
    assert record["message"] == "你好，测试"
    assert record["reply"] == "固定模型回复"
    message_id = record["id"]

    # 查询并核对内容
    resp = client.get("/api/messages")
    assert resp.status_code == 200
    records = resp.get_json()
    assert any(r["id"] == message_id and r["message"] == "你好，测试" for r in records)

    # 修改后确认更新
    resp = client.patch(f"/api/messages/{message_id}", json={"message": "更新后的内容"})
    assert resp.status_code == 200
    assert resp.get_json()["message"] == "更新后的内容"

    # 删除后确认消失
    resp = client.delete(f"/api/messages/{message_id}")
    assert resp.status_code == 200
    assert resp.get_json()["deleted"] == message_id

    resp = client.get("/api/messages")
    assert all(r["id"] != message_id for r in resp.get_json())


def test_create_message_rejects_invalid_input(client):
    before = len(chat_app.messages)

    # 空白消息
    resp = client.post("/api/messages", json={"message": "   "})
    assert resp.status_code == 400
    assert "message" in resp.get_json()["error"]

    # 缺少 message 字段
    resp = client.post("/api/messages", json={})
    assert resp.status_code == 400

    # 确认没有新增记录
    assert len(chat_app.messages) == before


def test_static_and_hello_routes(client):
    assert client.get("/api/hello").get_json() == {"message": "你好"}
    assert client.get("/").status_code == 200
    assert client.get("/style.css").status_code == 200
    assert client.get("/app.js").status_code == 200
