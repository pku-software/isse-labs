from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import app as chat_app


@pytest.fixture
def mock_model(monkeypatch):
    """替换应用使用的 SDK 客户端，固定回复且不发送网络请求。"""
    completion = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content="这是测试中的固定回复")
            )
        ]
    )
    sdk_client = Mock()
    sdk_client.chat.completions.create.return_value = completion
    monkeypatch.setattr(chat_app, "OpenAI", Mock(return_value=sdk_client))
    return sdk_client.chat.completions.create


@pytest.fixture
def client(monkeypatch, mock_model):
    """为每个测试准备独立的聊天状态和测试占位配置。"""
    monkeypatch.setenv("DEEPSEEK_API_KEY", "lab5-test-placeholder")
    monkeypatch.setattr(chat_app, "messages", [])
    monkeypatch.setattr(chat_app, "next_message_id", 1)
    monkeypatch.setitem(chat_app.app.config, "TESTING", True)

    with chat_app.app.test_client() as test_client:
        yield test_client
