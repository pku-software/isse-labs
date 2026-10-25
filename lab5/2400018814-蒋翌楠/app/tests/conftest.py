import importlib
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture
def api(tmp_path, monkeypatch):
    monkeypatch.setenv("LAB5_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("OPENAI_API_KEY", "test-placeholder")
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    module = importlib.import_module("app")
    module = importlib.reload(module)
    response = Mock(status_code=200)
    response.json.return_value = {
        "status": "completed",
        "output": [{"type": "message", "content": [
            {"type": "output_text", "text": "固定测试回复"}
        ]}],
    }
    post = Mock(return_value=response)
    monkeypatch.setattr(module.requests, "post", post)
    module.app.config.update(TESTING=True)
    return module.app.test_client(), module, post, tmp_path / "messages.json"
