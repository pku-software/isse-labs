"""聊天应用后端的行为测试。

运行方式（在仓库根目录）：

    python -m pytest -q

测试直接使用 Flask 的 test client 发请求，不需要先启动服务，也不会
访问真实的 DeepSeek 接口。
"""

import pytest

import app as chat


@pytest.fixture
def client():
    """每次测试前把内存数据清空，并提供 Flask test client。

    messages 和 next_id 是 app 模块级的全局变量，测试之间会互相影响，
    所以每条用例都从"没有任何记录"的状态开始。
    """
    chat.messages.clear()
    chat.next_id = 1
    chat.app.config["TESTING"] = True
    with chat.app.test_client() as client:
        yield client


@pytest.fixture
def mock_reply(monkeypatch):
    """把模型调用替换成固定回复。

    create_message() 内部使用的是模块里的 call_deepseek，所以替换
    app 模块上的这个属性，就能让接口逻辑照常执行、但不发出真实请求。
    """
    monkeypatch.setattr(chat, "call_deepseek", lambda message: "这是一条固定回复")


def test_message_crud_flow(client, mock_reply):
    """一条聊天记录从创建到删除的完整流程。"""
    # 创建：请求体只带 message，reply 由（被替换的）模型调用产生
    created = client.post("/api/messages", json={"message": "你好"})
    assert created.status_code == 201
    record = created.get_json()
    assert record["message"] == "你好"
    assert record["reply"] == "这是一条固定回复"
    message_id = record["id"]

    # 查询：列表里应该正好有刚才那一条
    listed = client.get("/api/messages")
    assert listed.status_code == 200
    assert listed.get_json() == [record]

    # 修改：改 message 字段，并确认改动真的存下来了
    updated = client.patch(
        f"/api/messages/{message_id}", json={"message": "改过的内容"}
    )
    assert updated.status_code == 200
    assert updated.get_json()["message"] == "改过的内容"
    assert client.get("/api/messages").get_json()[0]["message"] == "改过的内容"

    # 删除：返回 204 无正文，再查询应该已经没有记录了
    deleted = client.delete(f"/api/messages/{message_id}")
    assert deleted.status_code == 204
    assert client.get("/api/messages").get_json() == []


def test_create_rejects_blank_message(client, mock_reply):
    """只有空白的 message 属于非法输入，应被拒绝且不产生新记录。"""
    response = client.post("/api/messages", json={"message": "   "})

    assert response.status_code == 400
    assert "不能为空" in response.get_json()["error"]
    # 非法输入不能留下脏数据
    assert client.get("/api/messages").get_json() == []


# ---------------------------------------------------------------------------
# 下面几条是为了覆盖上面两个重点测试走不到的分支：
# 首页与静态文件、健康检查、请求体格式错误、模型配置缺失、记录不存在。
# ---------------------------------------------------------------------------


def test_hello_endpoint(client):
    """健康检查接口应固定返回问候语。"""
    response = client.get("/api/hello")

    assert response.status_code == 200
    assert response.get_json() == {"message": "你好"}


def test_home_page_and_static_file_are_served(client):
    """首页和 frontend/ 下的静态文件都由 Flask 直接提供。"""
    home = client.get("/")
    assert home.status_code == 200
    assert "AI 聊天助手" in home.get_data(as_text=True)

    stylesheet = client.get("/style.css")
    assert stylesheet.status_code == 200


def test_create_rejects_non_json_body(client):
    """请求体不是 JSON 对象时返回 400。"""
    response = client.post(
        "/api/messages", data="这不是 JSON", content_type="text/plain"
    )

    assert response.status_code == 400
    assert "JSON" in response.get_json()["error"]


def test_create_without_api_key_returns_500(client, monkeypatch):
    """缺少模型 Key 属于服务端配置错误，应返回 500 而不是 400。

    这条用例故意不 mock，让 call_deepseek 真正执行到"检查 Key"那一步；
    因为 Key 被删掉了，它会在发网络请求之前就抛出 ValueError。
    """
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    response = client.post("/api/messages", json={"message": "你好"})

    assert response.status_code == 500
    assert "DEEPSEEK_API_KEY" in response.get_json()["error"]
    # 调用失败时不能留下半条记录
    assert client.get("/api/messages").get_json() == []


def test_update_rejects_invalid_payload(client):
    """修改接口同样要挡住非 JSON 请求体和空白 message。"""
    non_json = client.patch(
        "/api/messages/1", data="这不是 JSON", content_type="text/plain"
    )
    assert non_json.status_code == 400

    blank = client.patch("/api/messages/1", json={"message": "   "})
    assert blank.status_code == 400
    assert "不能为空" in blank.get_json()["error"]


def test_update_missing_record_returns_404(client):
    """修改不存在的记录返回 404。"""
    response = client.patch("/api/messages/999", json={"message": "改一下"})

    assert response.status_code == 404
    assert "不存在" in response.get_json()["error"]


def test_delete_missing_record_returns_404(client):
    """删除不存在的记录返回 404。"""
    response = client.delete("/api/messages/999")

    assert response.status_code == 404
    assert "不存在" in response.get_json()["error"]
