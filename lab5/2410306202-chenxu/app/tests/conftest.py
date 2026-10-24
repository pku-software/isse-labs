"""测试夹具：把应用切到临时数据目录，并用固定回复替换模型调用。"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# 必须在导入应用之前设置：应用会在导入时按 LAB5_DATA_DIR 定位数据文件，
# 指向临时目录后，测试不会读写项目里的真实聊天记录。
os.environ["LAB5_DATA_DIR"] = tempfile.mkdtemp(prefix="lab5-tests-")
os.environ.setdefault("DEEPSEEK_API_KEY", "lab5-test-placeholder")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import app as chat_app  # noqa: E402

FIXED_REPLY = "这是测试用的固定回复"


@pytest.fixture()
def fixed_reply():
    """mock 出来的模型回复，断言时用它比对。"""
    return FIXED_REPLY


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """每个用例一份独立的临时数据文件，并清空内存里的会话。"""
    monkeypatch.setattr(chat_app, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(chat_app, "CONVERSATIONS_FILE", str(tmp_path / "conversations.json"))
    monkeypatch.setattr(chat_app, "conversations", [])
    monkeypatch.setattr(chat_app, "next_conversation_id", 1)
    # 用固定回复替换真实的 DeepSeek 调用：测试不联网、不花钱、结果稳定。
    monkeypatch.setattr(chat_app, "ask_deepseek", lambda model_messages: FIXED_REPLY)
    return chat_app.app.test_client()
