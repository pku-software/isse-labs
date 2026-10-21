import pytest

import app as chat_app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """Give every test a fresh in-memory state and temporary data file."""
    monkeypatch.setattr(chat_app, "DATA_FILE", tmp_path / "messages.json")
    chat_app.messages = []
    chat_app.next_message_id = 1
    chat_app.app.config.update(TESTING=True)

    with chat_app.app.test_client() as test_client:
        yield test_client


def test_message_crud_flow(client, monkeypatch):
    monkeypatch.setattr(
        chat_app,
        "get_ai_reply",
        lambda message: ("固定的测试回复", None),
    )

    create_response = client.post("/api/messages", json={"message": "第一条问题"})
    assert create_response.status_code == 201
    created = create_response.get_json()
    assert created == {
        "id": 1,
        "message": "第一条问题",
        "reply": "固定的测试回复",
    }

    list_response = client.get("/api/messages")
    assert list_response.status_code == 200
    assert list_response.get_json() == [created]

    update_response = client.patch(
        f"/api/messages/{created['id']}",
        json={"message": "修改后的问题"},
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["message"] == "修改后的问题"

    updated_records = client.get("/api/messages").get_json()
    assert updated_records[0]["message"] == "修改后的问题"
    assert updated_records[0]["reply"] == "固定的测试回复"

    delete_response = client.delete(f"/api/messages/{created['id']}")
    assert delete_response.status_code == 200
    assert delete_response.get_json() == {"message": "deleted", "id": created["id"]}

    final_response = client.get("/api/messages")
    assert final_response.status_code == 200
    assert final_response.get_json() == []


def test_empty_message_is_rejected_without_creating_record(client):
    response = client.post("/api/messages", json={"message": "   "})

    assert response.status_code == 400
    assert response.get_json() == {"error": "message must be a non-empty string"}

    missing_json_response = client.post("/api/messages")
    assert missing_json_response.status_code == 400
    assert missing_json_response.get_json() == {
        "error": "message must be a non-empty string"
    }

    assert client.get("/api/messages").get_json() == []
