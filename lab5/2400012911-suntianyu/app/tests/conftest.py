"""为每条测试加载使用临时数据目录的独立应用。"""

import importlib.util
import sys
from pathlib import Path
from unittest.mock import Mock

import dotenv
import pytest
import requests


@pytest.fixture
def app_module(tmp_path, monkeypatch):
    monkeypatch.setenv("LAB5_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("DEEPSEEK_API_KEY", "lab5-test-placeholder")
    # 测试不加载本地真实配置，也不允许意外发送网络请求。
    monkeypatch.setattr(dotenv, "load_dotenv", lambda *args, **kwargs: False)

    def block_network(*args, **kwargs):
        raise AssertionError("测试应模拟模型调用，不能访问网络")

    monkeypatch.setattr(requests.sessions.Session, "request", block_network)
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    spec = importlib.util.spec_from_file_location("app", app_path)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "app", module)
    spec.loader.exec_module(module)
    module.app.config["TESTING"] = True
    return module


@pytest.fixture
def client(app_module):
    with app_module.app.test_client() as test_client:
        yield test_client


@pytest.fixture
def model_reply(app_module, monkeypatch):
    reply = Mock(return_value="这是模拟的模型回复")
    monkeypatch.setattr(app_module, "generate_reply", reply)
    return reply
