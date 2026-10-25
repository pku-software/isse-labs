import pytest

import app as chat_app
from app import app as flask_app


@pytest.fixture
def client(monkeypatch):
    """Provide isolated API state and a deterministic model reply."""
    chat_app.messages.clear()
    monkeypatch.setattr(
        chat_app,
        "_request_model_reply",
        lambda message: f"固定测试回复：{message}",
    )

    with flask_app.test_client() as test_client:
        yield test_client

    chat_app.messages.clear()


def test_message_crud(client):
    created_response = client.post("/api/messages", json={"message": "测试消息"})
    assert created_response.status_code == 201

    created = created_response.get_json()
    assert created["message"] == "测试消息"
    assert created["reply"] == "固定测试回复：测试消息"

    listed_response = client.get("/api/messages")
    assert listed_response.status_code == 200
    assert listed_response.get_json() == [created]

    updated_response = client.patch(
        f"/api/messages/{created['id']}",
        json={"message": "修改后的测试消息"},
    )
    assert updated_response.status_code == 200
    assert updated_response.get_json()["message"] == "修改后的测试消息"

    listed_after_update = client.get("/api/messages").get_json()
    assert listed_after_update[0]["message"] == "修改后的测试消息"

    deleted_response = client.delete(f"/api/messages/{created['id']}")
    assert deleted_response.status_code == 200
    assert deleted_response.get_json() == {"id": created["id"], "deleted": True}
    assert client.get("/api/messages").get_json() == []


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"message": ""},
        {"message": "   "},
    ],
)
def test_invalid_message_is_rejected(client, payload):
    response = client.post("/api/messages", json=payload)

    assert response.status_code == 400
    assert "error" in response.get_json()
    assert client.get("/api/messages").get_json() == []


def test_non_object_json_is_rejected(client):
    response = client.post("/api/messages", json=["not", "an", "object"])

    assert response.status_code == 400
    assert client.get("/api/messages").get_json() == []


def test_invalid_update_is_rejected(client):
    response = client.patch("/api/messages/1", json={})

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_index_and_hello_are_available(client):
    index_response = client.get("/")
    hello_response = client.get("/api/hello")

    assert index_response.status_code == 200
    assert index_response.mimetype == "text/html"
    assert hello_response.status_code == 200
    assert hello_response.get_json() == {"message": "你好"}


def test_missing_message_ids_return_404(client):
    update_response = client.patch("/api/messages/999", json={"message": "不存在"})
    delete_response = client.delete("/api/messages/999")

    assert update_response.status_code == 404
    assert delete_response.status_code == 404


def test_model_failure_returns_502(client, monkeypatch):
    def fail_model_request(message):
        raise RuntimeError("模拟模型服务失败")

    monkeypatch.setattr(chat_app, "_request_model_reply", fail_model_request)
    response = client.post("/api/messages", json={"message": "触发失败"})

    assert response.status_code == 502
    assert response.get_json() == {"error": "模拟模型服务失败"}
    assert client.get("/api/messages").get_json() == []
