import importlib
from unittest.mock import patch

import pytest

import app as app_module


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """每个测试使用独立的临时数据目录，并把模型调用 mock 为固定回复。"""
    monkeypatch.setenv("LAB5_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("DEEPSEEK_API_KEY", "lab5-test-key")
    importlib.reload(app_module)
    with patch.object(app_module, "call_deepseek", return_value="模拟回复"):
        yield app_module.app.test_client()


def test_message_crud_flow(client):
    """一条聊天记录的创建、查询、修改、删除全流程。"""
    resp = client.post("/api/conversations")
    assert resp.status_code == 201
    conv_id = resp.get_json()["id"]

    # 创建：发送消息，模型调用被 mock，返回固定回复
    resp = client.post(
        f"/api/conversations/{conv_id}/messages", json={"message": "你好"}
    )
    assert resp.status_code == 201
    assistant = resp.get_json()
    assert assistant["role"] == "assistant"
    assert assistant["content"] == "模拟回复"
    assistant_id = assistant["id"]

    # 查询：会话里同时有用户消息和助手回复
    messages = client.get(f"/api/conversations/{conv_id}").get_json()["messages"]
    user_msg = next(m for m in messages if m["role"] == "user")
    assert user_msg["content"] == "你好"
    assert any(
        m["id"] == assistant_id and m["content"] == "模拟回复" for m in messages
    )

    # 修改：更新用户消息内容，重新生成助手回复
    resp = client.patch(
        f"/api/conversations/{conv_id}/messages/{user_msg['id']}",
        json={"content": "修改后的内容"},
    )
    assert resp.status_code == 200
    messages = client.get(f"/api/conversations/{conv_id}").get_json()["messages"]
    user_msg = next(m for m in messages if m["role"] == "user")
    assert user_msg["content"] == "修改后的内容"
    assert any(
        m["role"] == "assistant" and m["content"] == "模拟回复" for m in messages
    )

    # 删除：删除用户消息，连同其助手回复一起消失
    resp = client.delete(
        f"/api/conversations/{conv_id}/messages/{user_msg['id']}"
    )
    assert resp.status_code == 200
    messages = client.get(f"/api/conversations/{conv_id}").get_json()["messages"]
    assert messages == []


def test_invalid_message_rejected(client):
    """一类非法输入：空消息与缺少 message 字段都应被拒绝，且不新增记录。"""
    resp = client.post("/api/conversations")
    assert resp.status_code == 201
    conv_id = resp.get_json()["id"]

    # 空消息
    resp = client.post(
        f"/api/conversations/{conv_id}/messages", json={"message": "   "}
    )
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "message 不能为空"

    # 缺少 message 字段
    resp = client.post(f"/api/conversations/{conv_id}/messages", json={})
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "缺少 message 字段"

    # 两次非法请求都没有新增聊天记录
    messages = client.get(f"/api/conversations/{conv_id}").get_json()["messages"]
    assert messages == []


def test_conversation_management(client):
    """补充覆盖：首页、连通性接口、会话列表、重命名与删除。"""
    assert client.get("/").status_code == 200
    assert client.get("/api/hello").get_json() == {"message": "你好"}

    resp = client.post("/api/conversations")
    assert resp.status_code == 201
    conv_id = resp.get_json()["id"]

    listed = client.get("/api/conversations").get_json()
    assert [c["id"] for c in listed] == [conv_id]

    resp = client.patch(f"/api/conversations/{conv_id}", json={"title": "改名"})
    assert resp.status_code == 200
    assert resp.get_json()["title"] == "改名"

    resp = client.delete(f"/api/conversations/{conv_id}")
    assert resp.status_code == 200
    assert client.get("/api/conversations").get_json() == []
