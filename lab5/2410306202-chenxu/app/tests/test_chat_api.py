"""Lab5 的两个重点测试：一条聊天记录的 CRUD 流程，以及一类非法输入。"""

import pytest


def test_turn_crud_flow(client, fixed_reply):
    """创建会话后，对同一条聊天记录做创建、查询、修改、删除，每一步都核对实际内容。"""

    # 这是多会话版本，先创建一个会话
    response = client.post("/api/conversations", json={"title": "测试会话"})
    assert response.status_code == 201
    conversation_id = response.get_json()["id"]

    # 创建：发一条消息，应该得到一轮问答（提问 + 模型回复）
    response = client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={"message": "你好，这是第一条测试消息"},
    )
    assert response.status_code == 201
    conversation = response.get_json()
    assert len(conversation["turns"]) == 1
    turn = conversation["turns"][0]
    turn_id = turn["id"]
    assert turn["message"] == "你好，这是第一条测试消息"
    assert turn["reply"] == fixed_reply

    # 查询：重新读这个会话，确认记录真的存在
    response = client.get(f"/api/conversations/{conversation_id}")
    assert response.status_code == 200
    turns = response.get_json()["turns"]
    assert [item["id"] for item in turns] == [turn_id]
    assert turns[0]["message"] == "你好，这是第一条测试消息"

    # 修改：改提问内容，确认更新生效，模型回复没被改掉
    response = client.patch(
        f"/api/conversations/{conversation_id}/turns/{turn_id}",
        json={"message": "改过的提问"},
    )
    assert response.status_code == 200
    turns = response.get_json()["turns"]
    assert turns[0]["message"] == "改过的提问"
    assert turns[0]["reply"] == fixed_reply

    # 删除：删掉这一轮，再查一次，确认记录真的消失了
    response = client.delete(f"/api/conversations/{conversation_id}/turns/{turn_id}")
    assert response.status_code == 200
    assert response.get_json()["turns"] == []

    response = client.get(f"/api/conversations/{conversation_id}")
    assert response.get_json()["turns"] == []


@pytest.mark.parametrize(
    "payload",
    [
        {"message": "   "},  # 只有空白
        {"message": ""},  # 空字符串
        {},  # 缺少 message 字段
    ],
)
def test_invalid_message_is_rejected(client, payload):
    """非法输入：内容为空或缺少 message 字段时应返回 400，并且不留下任何记录。"""

    response = client.post("/api/conversations", json={"title": "非法输入测试"})
    conversation_id = response.get_json()["id"]

    response = client.post(
        f"/api/conversations/{conversation_id}/messages",
        json=payload,
    )
    assert response.status_code == 400
    assert "message" in response.get_json()["error"]

    # 关键：请求被拒绝后，会话里不能多出任何记录
    response = client.get(f"/api/conversations/{conversation_id}")
    assert response.get_json()["turns"] == []
