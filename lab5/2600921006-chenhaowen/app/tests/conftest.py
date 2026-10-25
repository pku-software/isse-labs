import importlib
import sys
from unittest.mock import MagicMock

import pytest
from openai.types.chat import ChatCompletion


@pytest.fixture
def app_module(tmp_path, monkeypatch):
    # app 在导入时加载数据，因此必须先设置独立目录和测试配置。
    monkeypatch.setenv("LAB5_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("DEEPSEEK_API_KEY", "lab5-test-placeholder")
    monkeypatch.setattr("dotenv.load_dotenv", lambda *args, **kwargs: False)

    # 每次测试重新导入，重新创建内存中的会话、ID 计数器和锁。
    sys.modules.pop("app", None)
    module = importlib.import_module("app")
    module.app.config["TESTING"] = True

    completion = ChatCompletion(
        id="lab5-mock-completion",
        object="chat.completion",
        created=0,
        model="deepseek-flash",
        choices=[
            {
                "index": 0,
                "finish_reason": "stop",
                "message": {"role": "assistant", "content": "固定测试回复"},
            }
        ],
    )
    mock_openai = MagicMock(name="OpenAI")
    mock_client = mock_openai.return_value.__enter__.return_value
    mock_client.chat.completions.create.return_value = completion
    monkeypatch.setattr(module, "OpenAI", mock_openai)

    yield module
    sys.modules.pop("app", None)


@pytest.fixture
def client(app_module):
    return app_module.app.test_client()
