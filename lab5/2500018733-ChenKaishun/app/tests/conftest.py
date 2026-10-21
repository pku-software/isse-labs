"""每个测试独立加载应用，隔离持久化文件、内存状态和模型调用。"""

import importlib.util
import sys
from pathlib import Path
from unittest.mock import Mock

import dotenv
import pytest


def pytest_configure(config):
    # 全新检出没有 .pytest_cache；pytest 创建 basetemp 时不创建父目录。
    if config.option.basetemp:
        Path(config.option.basetemp).resolve().parent.mkdir(parents=True, exist_ok=True)


@pytest.fixture
def app_module(tmp_path, monkeypatch):
    # 必须在加载 app.py 前设置，应用会在模块初始化时读取数据。
    monkeypatch.setenv("LAB5_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("DEEPSEEK_API_KEY", "lab5-test-placeholder")
    # 测试不读取开发者的本地 .env。
    monkeypatch.setattr(dotenv, "load_dotenv", lambda *args, **kwargs: False)

    app_path = Path(__file__).resolve().parents[1] / "app.py"
    spec = importlib.util.spec_from_file_location("app", app_path)
    module = importlib.util.module_from_spec(spec)
    # 与 --cov=app 一致；monkeypatch 在测试结束后恢复模块注册。
    monkeypatch.setitem(sys.modules, "app", module)
    spec.loader.exec_module(module)
    assert module.DATA_FILE.parent == tmp_path, "应用必须使用测试的临时数据目录"
    module.app.config.update(TESTING=True)
    return module


@pytest.fixture
def client(app_module):
    with app_module.app.test_client() as test_client:
        yield test_client


@pytest.fixture
def ai_reply(app_module, monkeypatch):
    reply = Mock(return_value="这是测试用的固定回复")
    monkeypatch.setattr(app_module, "get_ai_reply", reply)
    return reply
