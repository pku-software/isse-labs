import os
import tempfile
from unittest.mock import MagicMock

import pytest


# 必须在 import app 之前设置，才能让 app 在导入时读取临时数据目录。
_TEST_DATA_DIR = tempfile.mkdtemp(prefix="lab5-test-data-")
os.environ["LAB5_DATA_DIR"] = _TEST_DATA_DIR
os.environ.setdefault("DEEPSEEK_API_KEY", "lab5-test-placeholder")

import app as chat_app


@pytest.fixture(autouse=True)
def reset_state(monkeypatch):
    chat_app.messages = []
    chat_app.next_id = 1

    # mock 模型客户端，让 get_deepseek_reply 走完整解析逻辑并返回固定回复。
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {
        "choices": [{"message": {"content": "固定模型回复"}}]
    }
    monkeypatch.setattr(chat_app.requests, "post", lambda *args, **kwargs: fake_response)
    yield


@pytest.fixture
def client():
    return chat_app.app.test_client()
