"""Isolate chat state and external model calls for each test."""

import importlib
from itertools import count
from unittest.mock import Mock

import dotenv
import pytest


@pytest.fixture
def chat_module(monkeypatch):
    # Patch before importing app so tests never load a real .env file.
    monkeypatch.setattr(dotenv, "load_dotenv", lambda *args, **kwargs: False)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "lab5-placeholder")
    module = importlib.import_module("app")
    monkeypatch.setitem(module.app.config, "TESTING", True)
    monkeypatch.setattr(module, "messages", [])
    monkeypatch.setattr(module, "message_ids", count(1))
    monkeypatch.setattr(
        module.requests,
        "post",
        Mock(side_effect=AssertionError("Unexpected external model request")),
    )
    return module


@pytest.fixture
def client(chat_module):
    return chat_module.app.test_client()


@pytest.fixture
def model_request(chat_module, monkeypatch):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "choices": [{"message": {"content": "固定测试回复"}}]
    }
    request = Mock(return_value=response)
    monkeypatch.setattr(chat_module.requests, "post", request)
    return request
