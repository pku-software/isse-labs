import sys
from pathlib import Path

import pytest

# Make the application module importable when pytest is launched from the
# repository root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app as app_module


@pytest.fixture()
def client(monkeypatch):
    """Provide a clean Flask client and deterministic in-memory state."""
    app_module.messages.clear()
    app_module.next_id = 1
    app_module.app.config["TESTING"] = True
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")

    with app_module.app.test_client() as test_client:
        yield test_client


@pytest.fixture()
def mock_model(monkeypatch):
    """Replace the real model call and record each invocation."""
    calls: list[tuple[str, str]] = []

    def fake_ask_deepseek(api_key: str, message: str) -> str:
        calls.append((api_key, message))
        return "固定回复"

    monkeypatch.setattr(app_module, "ask_deepseek", fake_ask_deepseek)
    return calls
