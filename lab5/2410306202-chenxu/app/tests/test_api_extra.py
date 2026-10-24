"""补充测试：覆盖会话管理、兼容接口、模型调用的错误处理和持久化读取。

两个重点测试在 test_chat_api.py 里；这里只把覆盖率报告中标出的未执行行走一遍。
"""

import json

import pytest
import requests

import app as chat_app


class FakeResponse:
    """代替 requests 的响应对象，用来在测试里控制模型接口的返回。"""

    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload
        self.text = text

    def json(self):
        if self._payload is None:
            raise ValueError("不是 JSON")
        return self._payload


def test_pages_and_hello(client):
    """首页、静态资源和连通性接口都能正常返回。"""
    assert client.get("/").status_code == 200
    assert client.get("/style.css").status_code == 200
    assert client.get("/app.js").status_code == 200

    response = client.get("/api/hello")
    assert response.status_code == 200
    assert response.get_json() == {"message": "你好"}


def test_create_conversation_without_body_uses_default_title(client):
    """不带请求体时用默认标题建会话。"""
    response = client.post("/api/conversations")
    assert response.status_code == 201
    assert response.get_json()["title"] == chat_app.DEFAULT_CONVERSATION_TITLE


def test_conversation_list_rename_and_delete(client):
    """会话列表、重命名、删除，以及会话不存在时的 404。"""
    conversation_id = client.post("/api/conversations", json={"title": "会话一"}).get_json()["id"]
    client.post(f"/api/conversations/{conversation_id}/messages", json={"message": "你好"})

    assert client.get("/api/conversations").get_json() == [
        {"id": conversation_id, "title": "会话一", "turn_count": 1}
    ]

    response = client.patch(f"/api/conversations/{conversation_id}", json={"title": "改名后的会话"})
    assert response.status_code == 200
    assert response.get_json()["title"] == "改名后的会话"

    # 请求体不合法返回 400；会话不存在返回 404
    assert client.patch(f"/api/conversations/{conversation_id}", json={}).status_code == 400
    assert client.patch("/api/conversations/999", json={"title": "x"}).status_code == 404
    assert client.get("/api/conversations/999").status_code == 404

    response = client.delete(f"/api/conversations/{conversation_id}")
    assert response.status_code == 200
    assert response.get_json() == {"deleted": conversation_id}
    assert client.get("/api/conversations").get_json() == []
    assert client.delete(f"/api/conversations/{conversation_id}").status_code == 404


def test_turn_endpoints_report_missing_resources(client):
    """给不存在的会话发消息、改删不存在的问答，都返回 404。"""
    assert client.post("/api/conversations/999/messages", json={"message": "你好"}).status_code == 404

    # 会话本身不存在时，改删问答也应返回 404
    assert client.patch("/api/conversations/999/turns/1", json={"message": "改"}).status_code == 404
    assert client.delete("/api/conversations/999/turns/1").status_code == 404

    conversation_id = client.post("/api/conversations", json={"title": "会话"}).get_json()["id"]
    assert client.patch(f"/api/conversations/{conversation_id}/turns/999", json={"message": "改"}).status_code == 404
    assert client.delete(f"/api/conversations/{conversation_id}/turns/999").status_code == 404

    client.post(f"/api/conversations/{conversation_id}/messages", json={"message": "你好"})
    turn_id = client.get(f"/api/conversations/{conversation_id}").get_json()["turns"][0]["id"]
    response = client.patch(f"/api/conversations/{conversation_id}/turns/{turn_id}", json={"message": "  "})
    assert response.status_code == 400


def test_model_failure_returns_502(client, monkeypatch):
    """模型调用失败时接口返回 502，而不是让请求崩掉。"""
    conversation_id = client.post("/api/conversations", json={"title": "会话"}).get_json()["id"]

    def boom(model_messages):
        raise RuntimeError("模型不可用")

    monkeypatch.setattr(chat_app, "ask_deepseek", boom)
    response = client.post(f"/api/conversations/{conversation_id}/messages", json={"message": "你好"})
    assert response.status_code == 502
    assert "模型不可用" in response.get_json()["error"]

    # 兼容接口走同一条错误处理
    assert client.post("/api/messages", json={"message": "你好"}).status_code == 502


def test_legacy_messages_endpoints(client):
    """兼容接口 /api/messages 作用在自动创建的默认会话上。"""
    response = client.post("/api/messages", json={"message": "第一条"})
    assert response.status_code == 201
    turn = response.get_json()
    assert turn["message"] == "第一条"

    assert client.post("/api/messages", json={"message": "   "}).status_code == 400

    assert [item["id"] for item in client.get("/api/messages").get_json()] == [turn["id"]]

    response = client.patch(f"/api/messages/{turn['id']}", json={"message": "改过的提问"})
    assert response.status_code == 200
    assert response.get_json()["message"] == "改过的提问"

    assert client.patch("/api/messages/999", json={"message": "改"}).status_code == 404
    assert client.patch(f"/api/messages/{turn['id']}", json={"message": ""}).status_code == 400
    assert client.delete("/api/messages/999").status_code == 404

    response = client.delete(f"/api/messages/{turn['id']}")
    assert response.status_code == 200
    assert response.get_json() == {"deleted": turn["id"]}
    assert client.get("/api/messages").get_json() == []


def test_build_model_messages_keeps_history():
    """发给模型的消息数组里，历史问答按顺序展开，最后才是新问题。"""
    conversation = {
        "id": 1,
        "title": "会话",
        "turns": [{"id": 1, "message": "旧问题", "reply": "旧回复"}],
    }
    assert chat_app.build_model_messages(conversation, "新问题") == [
        {"role": "user", "content": "旧问题"},
        {"role": "assistant", "content": "旧回复"},
        {"role": "user", "content": "新问题"},
    ]


def test_load_conversations_reads_and_filters_file(monkeypatch, tmp_path):
    """读取数据文件时跳过格式不对的内容，并补齐缺失字段。"""
    path = tmp_path / "conversations.json"
    path.write_text(
        json.dumps(
            [
                {
                    "id": 1,
                    "turns": [
                        {"id": 1, "message": "你好", "reply": "回复"},
                        {"id": 2},
                        {"no_id": True},
                        "junk",
                    ],
                },
                {"id": "不是整数"},
                "junk",
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(chat_app, "CONVERSATIONS_FILE", str(path))

    assert chat_app.load_conversations() == [
        {
            "id": 1,
            "title": chat_app.DEFAULT_CONVERSATION_TITLE,
            "turns": [
                {"id": 1, "message": "你好", "reply": "回复"},
                {"id": 2, "message": "", "reply": ""},
            ],
        }
    ]


@pytest.mark.parametrize("content", ["{不是合法 JSON", "{}", '"一段文本"'])
def test_load_conversations_falls_back_to_empty(monkeypatch, tmp_path, content):
    """文件损坏或结构不对时，从空数据开始而不是崩溃。"""
    path = tmp_path / "conversations.json"
    path.write_text(content, encoding="utf-8")
    monkeypatch.setattr(chat_app, "CONVERSATIONS_FILE", str(path))
    assert chat_app.load_conversations() == []


def test_ask_deepseek_sends_request_and_returns_reply(monkeypatch):
    """正常路径：带上 API Key 请求接口，并去掉回复两端的空白。"""
    calls = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        calls.update(url=url, headers=headers, payload=json, timeout=timeout)
        return FakeResponse(200, {"choices": [{"message": {"content": "  模型回复  "}}]})

    monkeypatch.setattr(requests, "post", fake_post)
    reply = chat_app.ask_deepseek([{"role": "user", "content": "你好"}])

    assert reply == "模型回复"
    assert calls["url"] == chat_app.DEEPSEEK_API_URL
    assert calls["headers"]["Authorization"].startswith("Bearer ")
    assert calls["payload"]["messages"] == [{"role": "user", "content": "你好"}]


def test_ask_deepseek_requires_api_key(monkeypatch):
    """没有配置 Key 时给出明确错误，而不是发出请求。"""
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    with pytest.raises(RuntimeError) as error:
        chat_app.ask_deepseek([])
    assert "DEEPSEEK_API_KEY" in str(error.value)


@pytest.mark.parametrize(
    "response, expected",
    [
        (FakeResponse(500, {"error": {"message": "额度不足"}}), "额度不足"),
        (FakeResponse(500, {"error": "服务异常"}), "服务异常"),
        (FakeResponse(503, None, "上游不可用"), "上游不可用"),
        (FakeResponse(503, None, ""), "HTTP 503"),
        (FakeResponse(500, {"unexpected": 1}), "HTTP 500"),
    ],
)
def test_ask_deepseek_reports_http_errors(monkeypatch, response, expected):
    """模型接口返回非 200 时，错误信息里要带上可读的原因。"""
    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: response)
    with pytest.raises(RuntimeError) as error:
        chat_app.ask_deepseek([])
    assert expected in str(error.value)


def test_ask_deepseek_handles_connection_and_format_errors(monkeypatch):
    """连接失败和返回内容无法解析时，都转成 RuntimeError。"""

    def refuse(*args, **kwargs):
        raise requests.RequestException("连接超时")

    monkeypatch.setattr(requests, "post", refuse)
    with pytest.raises(RuntimeError) as error:
        chat_app.ask_deepseek([])
    assert "无法连接 DeepSeek" in str(error.value)

    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: FakeResponse(200, {"choices": []}))
    with pytest.raises(RuntimeError) as error:
        chat_app.ask_deepseek([])
    assert "无法解析" in str(error.value)

    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: FakeResponse(200, None))
    with pytest.raises(RuntimeError) as error:
        chat_app.ask_deepseek([])
    assert "无法解析" in str(error.value)
