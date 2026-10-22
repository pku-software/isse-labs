import importlib
from types import SimpleNamespace
from unittest.mock import Mock

import pytest


@pytest.fixture
def chat_client(monkeypatch, tmp_path):
    monkeypatch.setenv("LAB5_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("DEEPSEEK_API_KEY", "lab5-test-placeholder")
    import app

    importlib.reload(app)
    app.app.config.update(TESTING=True)
    model = Mock()
    model.return_value.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="固定测试回复"))]
    )
    monkeypatch.setattr(app, "OpenAI", model)
    with app.app.test_client() as client:
        yield client, model
