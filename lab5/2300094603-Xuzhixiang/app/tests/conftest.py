import importlib.util
from pathlib import Path
from unittest.mock import Mock

import pytest


@pytest.fixture
def app_module(tmp_path, monkeypatch):
    # Configure storage before app.py initializes its in-memory records.
    monkeypatch.setenv("LAB5_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("DEEPSEEK_API_KEY", "lab5-test-placeholder")
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    spec = importlib.util.spec_from_file_location("app", app_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.app.config.update(TESTING=True)
    return module


@pytest.fixture
def chat_app(app_module, monkeypatch):
    module = app_module
    model_mock = Mock(return_value=("固定测试回复", None))
    monkeypatch.setattr(module, "ask_deepseek", model_mock)
    return module, model_mock


@pytest.fixture
def client(chat_app):
    module, _ = chat_app
    with module.app.test_client() as test_client:
        yield test_client
