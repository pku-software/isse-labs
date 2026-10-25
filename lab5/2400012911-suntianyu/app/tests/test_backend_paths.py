"""根据覆盖率报告补充持久化、记录不存在和模型响应解析测试。"""

from unittest.mock import MagicMock, Mock

import pytest


def test_saved_messages_can_be_loaded(app_module):
    records = [{"id": 7, "message": "需要保存的消息", "reply": "模拟回复"}]
    app_module.save_messages(records)
    assert app_module.load_messages() == records


@pytest.mark.parametrize("method", ["patch", "delete"])
def test_missing_record_returns_404(client, model_reply, method):
    if method == "patch":
        response = client.patch("/api/messages/999", json={"message": "修改消息"})
    else:
        response = client.delete("/api/messages/999")
    assert response.status_code == 404
    assert response.get_json() == {"error": "聊天记录不存在，请重新加载记录。"}
    assert client.get("/api/messages").get_json() == []
    model_reply.assert_not_called()


def test_model_response_is_parsed(client, app_module, monkeypatch):
    # 保留 generate_reply 的真实逻辑，只模拟 requests.post 的响应。
    response = MagicMock()
    response.__enter__.return_value = response
    response.status_code = 200
    response.json.return_value = {
        "choices": [{"message": {"content": "  模拟 HTTP 返回的回复  "}}]
    }
    post = Mock(return_value=response)
    monkeypatch.setattr(app_module.requests, "post", post)

    created = client.post("/api/messages", json={"message": "测试模型响应"})
    assert created.status_code == 201
    record = created.get_json()
    assert record["message"] == "测试模型响应"
    assert record["reply"] == "模拟 HTTP 返回的回复"
    assert client.get("/api/messages").get_json() == [record]
    post.assert_called_once_with(
        app_module.DEEPSEEK_URL,
        headers={"Authorization": "Bearer lab5-test-placeholder"},
        json={
            "model": app_module.DEEPSEEK_MODEL,
            "messages": [{"role": "user", "content": "测试模型响应"}],
            "thinking": {"type": "disabled"},
            "stream": False,
        },
        timeout=(10, 90),
        allow_redirects=False,
    )
