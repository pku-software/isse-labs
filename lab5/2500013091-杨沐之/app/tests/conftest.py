import importlib
import sys
from unittest.mock import Mock

import dotenv
import pytest


@pytest.fixture
def app_module(tmp_path, monkeypatch):
    # 必须在导入应用、加载会话 JSON 前配置独立目录。
    monkeypatch.setenv("LAB5_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("DEEPSEEK_API_KEY", "lab5-test-placeholder")
    # 测试不加载本机真实 .env。
    monkeypatch.setattr(dotenv, "load_dotenv", lambda *args, **kwargs: False)

    if "app" in sys.modules:
        module = importlib.reload(sys.modules["app"])
    else:
        module = importlib.import_module("app")
    module.app.config.update(TESTING=True)
    return module


@pytest.fixture
def reply_mock(app_module, monkeypatch):
    mock = Mock(return_value=("测试固定回复", None))
    monkeypatch.setattr(app_module, "generate_reply", mock)
    return mock


@pytest.fixture
def client(app_module, reply_mock):
    with app_module.app.test_client() as test_client:
        yield test_client
