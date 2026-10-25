"""Lab5 任务 1：两个重点测试——聊天记录 CRUD 与非法输入。

模型调用用 mock 替换成固定回复：测试不需要真实 DeepSeek Key，
也不需要先启动 Flask（test client 在测试进程里直接向应用发请求）。
"""
import pytest

import app as app_module


@pytest.fixture
def client(tmp_path, monkeypatch):
    """每个测试使用独立的临时数据目录，从干净状态开始"""
    monkeypatch.setenv("LAB5_DATA_DIR", str(tmp_path))
    app_module.reset_state()
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as c:
        yield c


def _mock_deepseek(monkeypatch, reply="这是测试用的固定回复"):
    """把模型调用替换成固定回复，测试不访问真实 DeepSeek。

    调用函数换掉还不够：接口里还有「没配 Key 就 500」的检查，
    所以 client 也换成一个占位对象（函数已被替换，不会真用它）。
    """
    monkeypatch.setattr(
        app_module, "call_deepseek_with_history", lambda history, text: reply
    )
    monkeypatch.setattr(app_module, "client", object())


def test_conversation_crud(client, monkeypatch):
    """一条聊天记录的创建、查询、修改、删除全流程，模型返回固定回复"""
    _mock_deepseek(monkeypatch)

    # 创建会话，从响应里拿到会话 id
    resp = client.post("/api/conversations", json={"title": "测试会话"})
    assert resp.status_code == 201
    conv = resp.get_json()
    cid = conv["id"]
    assert conv["title"] == "测试会话"

    # 创建一条聊天记录：发消息，模型回复被 mock 成固定文本
    resp = client.post(f"/api/conversations/{cid}/messages", json={"message": "你好"})
    assert resp.status_code == 201
    conv = resp.get_json()
    assert conv["messages"][-1]["message"] == "你好"
    assert conv["messages"][-1]["reply"] == "这是测试用的固定回复"

    # 查询并核对内容：标题、消息数、消息内容和回复都在
    resp = client.get(f"/api/conversations/{cid}")
    assert resp.status_code == 200
    conv = resp.get_json()
    assert conv["title"] == "测试会话"
    assert len(conv["messages"]) == 1
    assert conv["messages"][0]["reply"] == "这是测试用的固定回复"

    # 修改：给会话改名，确认更新生效
    resp = client.patch(f"/api/conversations/{cid}", json={"title": "改名后的会话"})
    assert resp.status_code == 200
    assert resp.get_json()["title"] == "改名后的会话"

    # 删除：删完再查应该 404（记录真的消失了）
    resp = client.delete(f"/api/conversations/{cid}")
    assert resp.status_code == 200
    resp = client.get(f"/api/conversations/{cid}")
    assert resp.status_code == 404


def test_message_without_field_is_rejected(client):
    """非法输入：不带 message 字段（或为空）发消息 → 400 且没有新增记录"""
    resp = client.post("/api/conversations", json={"title": "非法输入测试"})
    assert resp.status_code == 201
    cid = resp.get_json()["id"]

    # 完全不带 message 字段
    resp = client.post(f"/api/conversations/{cid}/messages", json={})
    assert resp.status_code == 400
    assert "message" in resp.get_json()["error"]

    # message 是空字符串
    resp = client.post(f"/api/conversations/{cid}/messages", json={"message": ""})
    assert resp.status_code == 400

    # 确认这两次非法请求没有产生任何记录
    resp = client.get(f"/api/conversations/{cid}")
    assert resp.get_json()["messages"] == []
