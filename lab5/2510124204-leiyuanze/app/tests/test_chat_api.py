# Lab5：聊天接口自动测试（模型调用使用 mock 的固定回复，不访问真实 DeepSeek）。
import importlib
import json

import pytest

import app as app_module

FIXED_REPLY = "固定回复（mock）"


class FakeModelResponse:
    # 模拟 urllib.request.urlopen 的返回值：支持 with 语句和 read()。
    def __init__(self, reply):
        self._body = json.dumps(
            {"choices": [{"message": {"content": reply}}]},
            ensure_ascii=False,
        ).encode("utf-8")

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


def fake_urlopen(request, timeout=None):
    return FakeModelResponse(FIXED_REPLY)


@pytest.fixture()
def client(tmp_path, monkeypatch):
    # 每次测试使用独立临时数据目录；LAB5_DATA_DIR 在加载数据前生效。
    monkeypatch.setenv("LAB5_DATA_DIR", str(tmp_path))
    # 使用占位 Key，避免依赖真实凭据。
    monkeypatch.setenv("DEEPSEEK_API_KEY", "lab5-test-key")
    importlib.reload(app_module)
    # mock 网络层：模型调用返回固定回复，测试不联网。
    monkeypatch.setattr(app_module.urllib.request, "urlopen", fake_urlopen)
    app_module.app.config.update(TESTING=True)
    return app_module.app.test_client()


def test_message_crud_flow_with_mocked_reply(client):
    # 多会话应用：先创建测试会话，记录挂在这个会话下。
    created = client.post("/api/conversations", json={"title": "CRUD 测试会话"})
    assert created.status_code == 201
    conversation_id = created.get_json()["id"]

    # 创建一条聊天记录；模型调用被 mock 成固定回复。
    sent = client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={"message": "你好，帮我记住这句话"},
    )
    assert sent.status_code == 201
    record = sent.get_json()
    message_id = record["id"]
    assert record["message"] == "你好，帮我记住这句话"
    assert record["reply"] == FIXED_REPLY

    # 查询：核对记录已经保存。
    fetched = client.get(f"/api/conversations/{conversation_id}").get_json()
    assert len(fetched["messages"]) == 1
    assert fetched["messages"][0]["id"] == message_id
    assert fetched["messages"][0]["message"] == "你好，帮我记住这句话"

    # 修改：更新消息内容并确认生效。
    updated = client.patch(
        f"/api/conversations/{conversation_id}/messages/{message_id}",
        json={"message": "修改后的内容"},
    )
    assert updated.status_code == 200
    assert updated.get_json()["message"] == "修改后的内容"
    stored = client.get(f"/api/conversations/{conversation_id}").get_json()
    assert stored["messages"][0]["message"] == "修改后的内容"

    # 删除：确认记录消失。
    deleted = client.delete(
        f"/api/conversations/{conversation_id}/messages/{message_id}"
    )
    assert deleted.status_code == 200
    assert deleted.get_json() == {"deleted": message_id}
    remaining = client.get(f"/api/conversations/{conversation_id}").get_json()
    assert remaining["messages"] == []


def test_empty_message_is_rejected_and_not_saved(client):
    created = client.post("/api/conversations", json={"title": "非法输入测试"})
    assert created.status_code == 201
    conversation_id = created.get_json()["id"]

    # 一类非法输入：空消息（只有空白字符）。
    response = client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={"message": "   "},
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "message 不能为空"}

    # 确认没有新增记录。
    conversation = client.get(f"/api/conversations/{conversation_id}").get_json()
    assert conversation["messages"] == []


def test_conversation_list_rename_and_delete(client):
    # 不带 title 创建：使用默认标题。
    first = client.post("/api/conversations", json={})
    assert first.status_code == 201
    first_body = first.get_json()
    assert first_body["title"] == f"新会话 {first_body['id']}"

    second = client.post("/api/conversations", json={"title": "第二个会话"})
    assert second.status_code == 201
    second_id = second.get_json()["id"]

    # 列表：能看到两个会话的摘要。
    summaries = client.get("/api/conversations").get_json()
    assert {item["id"] for item in summaries} == {first_body["id"], second_id}
    assert {"id", "title", "messageCount", "lastMessage", "createdAt", "updatedAt"} <= set(summaries[0])

    # 非法标题（超长）→ 400。
    too_long = client.post("/api/conversations", json={"title": "长" * 81})
    assert too_long.status_code == 400

    # 改名 → 确认更新。
    renamed = client.patch(
        f"/api/conversations/{second_id}",
        json={"title": "改名后的会话"},
    )
    assert renamed.status_code == 200
    assert renamed.get_json()["title"] == "改名后的会话"

    # 删除 → 确认消失。
    deleted = client.delete(f"/api/conversations/{second_id}")
    assert deleted.status_code == 200
    assert client.get(f"/api/conversations/{second_id}").status_code == 404
    remaining_ids = [item["id"] for item in client.get("/api/conversations").get_json()]
    assert remaining_ids == [first_body["id"]]
