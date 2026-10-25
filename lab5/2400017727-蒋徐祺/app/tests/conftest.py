from unittest.mock import Mock, patch

import pytest

# 导入应用时不加载本机 .env；测试不需要真实配置。
with patch("dotenv.load_dotenv", return_value=False):
    import app as chat_app


@pytest.fixture()
def client_and_model(monkeypatch):
    # 每个测试获得新的列表，避免测试之间共享聊天记录。
    monkeypatch.setattr(chat_app, "messages", [])
    monkeypatch.setitem(chat_app.app.config, "TESTING", True)
    model = Mock(return_value="这是固定的测试回复")
    monkeypatch.setattr(chat_app, "ask_deepseek", model)
    with chat_app.app.test_client() as client:
        yield client, model
