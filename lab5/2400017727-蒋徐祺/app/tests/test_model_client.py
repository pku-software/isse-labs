from unittest.mock import Mock

import app as chat_app


def test_model_request_and_reply(monkeypatch):
    # 只使用占位 Key，并在 HTTP 边界模拟固定模型响应。
    monkeypatch.setenv("DEEPSEEK_API_KEY", "lab5-test-placeholder")
    response = Mock(status_code=200)
    response.json.return_value = {
        "choices": [{"message": {"content": "这是固定的模型回复"}}]
    }
    post = Mock(return_value=response)
    monkeypatch.setattr(chat_app.requests, "post", post)

    assert chat_app.ask_deepseek("你好") == "这是固定的模型回复"
    post.assert_called_once_with(
        chat_app.DEEPSEEK_API_URL,
        headers={
            "Authorization": "Bearer lab5-test-placeholder",
            "Content-Type": "application/json",
        },
        json={
            "model": chat_app.DEEPSEEK_MODEL,
            "messages": [{"role": "user", "content": "你好"}],
            "stream": False,
        },
        timeout=chat_app.DEEPSEEK_TIMEOUT,
    )
