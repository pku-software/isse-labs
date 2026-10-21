from types import SimpleNamespace

import pytest

import app as app_module


class FakeOpenAI:
    def __init__(self, *args, **kwargs):
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    @staticmethod
    def create(**kwargs):
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content="固定测试回复")
                )
            ]
        )


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setattr(app_module, "OpenAI", FakeOpenAI)
    monkeypatch.setattr(app_module, "MESSAGES_FILE", tmp_path / "messages.json")
    monkeypatch.setattr(app_module, "messages", [])
    monkeypatch.setattr(app_module, "next_message_id", 1)
    app_module.app.config.update(TESTING=True)

    with app_module.app.test_client() as test_client:
        yield test_client


def test_message_crud_flow(client):
    created = client.post("/api/messages", json={"message": "你好"})
    assert created.status_code == 201
    record = created.get_json()
    assert record == {"id": 1, "message": "你好", "reply": "固定测试回复"}

    listed = client.get("/api/messages")
    assert listed.status_code == 200
    assert listed.get_json() == [record]

    updated = client.patch("/api/messages/1", json={"message": "更新后的问题"})
    assert updated.status_code == 200
    assert updated.get_json() == {
        "id": 1,
        "message": "更新后的问题",
        "reply": "固定测试回复",
    }

    deleted = client.delete("/api/messages/1")
    assert deleted.status_code == 200
    assert client.get("/api/messages").get_json() == []


def test_empty_message_is_rejected_without_creating_record(client):
    response = client.post("/api/messages", json={"message": "   "})

    assert response.status_code == 400
    assert "非空字符串" in response.get_json()["error"]
    assert client.get("/api/messages").get_json() == []
