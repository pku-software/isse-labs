import json

import pytest


def test_storage_isolation(api):
    client, module, post, path = api
    assert module.data_file == path
    assert client.get("/api/messages").json == []


def test_crud(api):
    client, module, post, path = api
    response = client.post("/api/messages", json={"message": "  你好  "})
    assert response.status_code == 201
    record = response.json
    assert record == {"id": record["id"], "message": "你好", "reply": "固定测试回复"}
    assert isinstance(record["id"], int)
    assert client.get("/api/messages").json == [record]
    assert json.loads(path.read_text()) == [record]
    post.assert_called_once()
    url = f"/api/messages/{record['id']}"
    response = client.patch(url, json={"message": "修改后"})
    assert response.status_code == 200
    updated = {**record, "message": "修改后"}
    assert response.json == updated
    assert client.get("/api/messages").json == [updated]
    assert json.loads(path.read_text()) == [updated]
    response = client.delete(url)
    assert response.status_code == 200
    assert response.json == {"message": "已删除聊天记录"}
    assert client.get("/api/messages").json == []
    assert json.loads(path.read_text()) == []


@pytest.mark.parametrize("body", [{"message": " \t\n"}, {}, {"message": 1}, [], None])
def test_invalid_message(api, body):
    client, module, post, path = api
    response = client.post("/api/messages", json=body)
    assert response.status_code == 400
    assert response.json == {"error": "请提供非空的 message 字符串"}
    assert client.get("/api/messages").json == []
    assert not path.exists()
    post.assert_not_called()


def test_pages_and_missing_records(api):
    client, module, post, path = api
    assert client.get("/").status_code == 200
    assert client.get("/api/hello").json == {"message": "你好"}
    for method in (client.patch, client.delete):
        response = method("/api/messages/999")
        assert response.status_code == 404
        assert response.json == {"error": "聊天记录不存在"}


def test_invalid_update_preserves_record(api):
    client, module, post, path = api
    record = client.post("/api/messages", json={"message": "原文"}).json
    response = client.patch(f"/api/messages/{record['id']}", json={"message": " "})
    assert response.status_code == 400
    assert client.get("/api/messages").json == [record]
    assert json.loads(path.read_text()) == [record]
