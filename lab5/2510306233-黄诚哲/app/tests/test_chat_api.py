import app


def test_message_crud(client, monkeypatch):
    monkeypatch.setattr(
        app, "call_deepseek", lambda history, content: ("固定回复", None)
    )

    resp = client.post("/api/conversations", json={"title": "测试会话"})
    assert resp.status_code == 201
    conversation_id = resp.get_json()["id"]

    resp = client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={"message": "你好"},
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert len(data["messages"]) == 2
    user_message = data["messages"][0]
    assistant_message = data["messages"][1]
    assert user_message["role"] == "user"
    assert user_message["content"] == "你好"
    assert assistant_message["role"] == "assistant"
    assert assistant_message["content"] == "固定回复"
    message_id = user_message["id"]

    resp = client.get(f"/api/conversations/{conversation_id}")
    assert resp.status_code == 200
    found = next(m for m in resp.get_json()["messages"] if m["id"] == message_id)
    assert found["content"] == "你好"

    resp = client.patch(
        f"/api/conversations/{conversation_id}/messages/{message_id}",
        json={"content": "修改后的内容"},
    )
    assert resp.status_code == 200
    assert resp.get_json()["content"] == "修改后的内容"

    resp = client.delete(
        f"/api/conversations/{conversation_id}/messages/{message_id}"
    )
    assert resp.status_code == 200

    resp = client.get(f"/api/conversations/{conversation_id}")
    assert all(m["id"] != message_id for m in resp.get_json()["messages"])


def test_empty_message_rejected(client, monkeypatch):
    monkeypatch.setattr(
        app, "call_deepseek", lambda history, content: ("固定回复", None)
    )

    resp = client.post("/api/conversations", json={"title": "非法输入"})
    conversation_id = resp.get_json()["id"]

    resp = client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={"message": "   "},
    )
    assert resp.status_code == 400
    assert "不能为空" in resp.get_json()["error"]

    resp = client.get(f"/api/conversations/{conversation_id}")
    assert resp.get_json()["messages"] == []

def test_basic_routes(client):
    assert client.get("/").status_code == 200
    assert client.get("/style.css").status_code == 200
    assert client.get("/app.js").status_code == 200

    resp = client.get("/api/hello")
    assert resp.status_code == 200
    assert resp.get_json() == {"message": "你好"}

    resp = client.get("/api/conversations")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_conversation_crud(client):
    resp = client.post("/api/conversations", json={"title": ""})
    assert resp.status_code == 201
    conversation = resp.get_json()
    assert conversation["title"] == "新会话"
    conversation_id = conversation["id"]

    resp = client.get("/api/conversations")
    assert any(c["id"] == conversation_id for c in resp.get_json())

    resp = client.patch(
        f"/api/conversations/{conversation_id}", json={"title": "改名后的会话"}
    )
    assert resp.status_code == 200
    assert resp.get_json()["title"] == "改名后的会话"

    resp = client.patch(
        f"/api/conversations/{conversation_id}", json={"title": "   "}
    )
    assert resp.status_code == 400

    resp = client.get("/api/conversations/9999")
    assert resp.status_code == 404

    resp = client.delete(f"/api/conversations/{conversation_id}")
    assert resp.status_code == 200

    resp = client.delete(f"/api/conversations/{conversation_id}")
    assert resp.status_code == 404

    resp = client.get("/api/conversations")
    assert all(c["id"] != conversation_id for c in resp.get_json())


def test_message_error_branches(client, monkeypatch):
    monkeypatch.setattr(
        app, "call_deepseek", lambda history, content: ("固定回复", None)
    )

    resp = client.post("/api/conversations", json={"title": "错误分支"})
    conversation_id = resp.get_json()["id"]

    resp = client.post(
        f"/api/conversations/{conversation_id}/messages", json={"message": "你好"}
    )
    message_id = resp.get_json()["messages"][0]["id"]

    resp = client.post("/api/conversations/9999/messages", json={"message": "hi"})
    assert resp.status_code == 404

    resp = client.patch(
        "/api/conversations/9999/messages/1", json={"content": "x"}
    )
    assert resp.status_code == 404

    resp = client.delete("/api/conversations/9999/messages/1")
    assert resp.status_code == 404

    resp = client.post(
        f"/api/conversations/{conversation_id}/messages", json={}
    )
    assert resp.status_code == 400

    resp = client.patch(
        f"/api/conversations/{conversation_id}/messages/9999",
        json={"content": "x"},
    )
    assert resp.status_code == 404

    resp = client.delete(
        f"/api/conversations/{conversation_id}/messages/9999"
    )
    assert resp.status_code == 404

    resp = client.patch(
        f"/api/conversations/{conversation_id}/messages/{message_id}", json={}
    )
    assert resp.status_code == 400

    resp = client.patch(
        f"/api/conversations/{conversation_id}/messages/{message_id}",
        json={"content": "   "},
    )
    assert resp.status_code == 400


def test_message_requires_api_key(client, monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    resp = client.post("/api/conversations", json={"title": "缺少 Key"})
    conversation_id = resp.get_json()["id"]

    resp = client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={"message": "触发缺 Key"},
    )
    assert resp.status_code == 502
    assert "DEEPSEEK_API_KEY" in resp.get_json()["error"]


def test_load_data_reloads_persisted(client):
    resp = client.post("/api/conversations", json={"title": "持久化"})
    conversation_id = resp.get_json()["id"]

    app.load_data()

    assert conversation_id in [c["id"] for c in app.conversations]


def test_load_data_migrates_old_format(monkeypatch, tmp_path):
    import json

    old = [{"message": "hi", "reply": "hello"}]
    old_path = tmp_path / "messages.json"
    old_path.write_text(json.dumps(old, ensure_ascii=False), encoding="utf-8")

    monkeypatch.setattr(app, "DATA_FILE", str(tmp_path / "conversations.json"))
    monkeypatch.setattr(app, "OLD_DATA_FILE", str(old_path))
    app.load_data()

    assert app.conversations[0]["title"] == "导入的会话"
    assert app.conversations[0]["messages"][0]["content"] == "hi"
    assert app.conversations[0]["messages"][1]["content"] == "hello"