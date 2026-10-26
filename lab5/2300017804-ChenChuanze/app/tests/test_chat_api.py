import importlib
from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def application(tmp_path, monkeypatch):
    monkeypatch.setenv("LAB5_DATA_DIR", str(tmp_path))
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    with patch("dotenv.load_dotenv", return_value=False):
        module = importlib.import_module("app")
        module = importlib.reload(module)
    module.app.config["TESTING"] = True
    monkeypatch.setattr(module, "generate_reply", Mock(return_value=("固定测试回复", None)))
    assert module.data_file.parent == tmp_path
    return module


def test_conversation_chat_crud(application):
    client = application.app.test_client()
    created = client.post("/api/conversations", json={"title": "测试会话"})
    assert created.status_code == 201
    route = f"/api/conversations/{created.json['id']}"

    response = client.post(route + "/messages", json={"message": "你好"})
    assert response.status_code == 201
    turn_id = response.json["id"]
    assert response.json == {"id": turn_id, "message": "你好", "reply": "固定测试回复"}
    application.generate_reply.assert_called_once_with([{"role": "user", "content": "你好"}])
    assert client.get(route).json["messages"] == [
        {"turn_id": turn_id, "role": "user", "content": "你好"},
        {"turn_id": turn_id, "role": "assistant", "content": "固定测试回复"},
    ]
    assert client.get("/api/conversations").json[0]["message_count"] == 1
    renamed = client.patch(route, json={"title": "已重命名"})
    assert renamed.status_code == 200
    assert renamed.json["title"] == "已重命名"

    turn = f"{route}/messages/{turn_id}"
    updated = client.patch(turn, json={"message": "修改后"})
    assert updated.status_code == 200
    assert updated.json == {"id": turn_id, "message": "修改后"}
    assert client.get(route).json["messages"][0]["content"] == "修改后"
    assert application.load_state()[1][0]["messages"][0]["content"] == "修改后"

    assert client.delete(turn).status_code == 200
    assert client.get(route).json["messages"] == []
    assert application.load_state()[1][0]["messages"] == []
    assert client.delete(route).status_code == 200
    assert client.get(route).status_code == 404
    assert client.get("/api/conversations").json == []
    assert application.load_state() == ([], [])


def test_rejects_blank_message(application):
    client = application.app.test_client()
    created = client.post("/api/conversations", json={"title": "非法输入测试"})
    route = f"/api/conversations/{created.json['id']}"
    before = application.data_file.read_bytes()

    response = client.post(route + "/messages", json={"message": "   "})
    assert response.status_code == 400
    assert response.json == {"error": "消息不能为空"}
    assert client.get(route).json["messages"] == []
    assert application.data_file.read_bytes() == before
    application.generate_reply.assert_not_called()


def test_standalone_message_crud(application):
    client = application.app.test_client()
    created = client.post("/api/messages", json={"message": "独立问答"})
    assert created.status_code == 201
    record = created.json
    assert record["message"] == "独立问答"
    assert record["reply"] == "固定测试回复"
    assert client.get("/api/messages").json == [record]
    route = f"/api/messages/{record['id']}"

    updated = client.patch(route, json={"message": "修改后的独立问答"})
    assert updated.status_code == 200
    assert updated.json["message"] == "修改后的独立问答"
    assert client.get("/api/messages").json[0]["message"] == "修改后的独立问答"
    assert application.load_state()[0][0]["message"] == "修改后的独立问答"

    assert client.delete(route).status_code == 200
    assert client.get("/api/messages").json == []
    assert application.load_state() == ([], [])
