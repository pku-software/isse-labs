import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
import app as chat_app

@pytest.fixture
def client(monkeypatch):
    # 使用臨時目錄隔離持久化數據
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("LAB5_DATA_DIR", tmpdir)
        monkeypatch.setenv("DEEPSEEK_API_KEY", "test-mock-api-key")
        chat_app.init_storage()
        chat_app.app.config["TESTING"] = True
        with chat_app.app.test_client() as client:
            yield client

# 1. 連通性與靜態頁面檢查
def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["Content-Type"]
    assert "<html" in response.data.decode("utf-8").lower()

def test_hello_endpoint(client):
    response = client.get("/api/hello")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert response.get_json() == {"message": "你好"}

# 2. 會話 (Conversation) CRUD 完整流程
def test_conversation_crud_flow(client):
    # 創建 (Create)
    res_create = client.post("/api/conversations", json={"title": "自動化測試會話"})
    assert res_create.status_code == 201
    conv_data = res_create.get_json()
    cid = conv_data["id"]
    assert conv_data["title"] == "自動化測試會話"

    # 查詢列表 (List)
    res_list = client.get("/api/conversations")
    assert res_list.status_code == 200
    conv_ids = [c["id"] for c in res_list.get_json()]
    assert cid in conv_ids

    # 查詢詳情 (Read)
    res_detail = client.get(f"/api/conversations/{cid}")
    assert res_detail.status_code == 200
    assert res_detail.get_json()["title"] == "自動化測試會話"

    # 更新 (Update)
    res_update = client.patch(f"/api/conversations/{cid}", json={"title": "修改後標題"})
    assert res_update.status_code == 200
    assert res_update.get_json()["title"] == "修改後標題"

    # 刪除 (Delete)
    res_delete = client.delete(f"/api/conversations/{cid}")
    assert res_delete.status_code == 200

    # 刪除後查詢驗證已不存在
    res_after = client.get(f"/api/conversations/{cid}")
    assert res_after.status_code == 404

# 3. 聊天訊息 (Message) CRUD 完整流程（含 Mock LLM 調用）
def test_message_crud_flow(client):
    # 建立會話
    res_create = client.post("/api/conversations", json={"title": "對話測試"})
    cid = res_create.get_json()["id"]

    # 發送訊息 (Create) - 使用 Mock 避免真實網路請求與 Token 消耗
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {"message": {"content": "這是一條自動測試的 AI 回覆"}}
        ]
    }

    with patch("requests.post", return_value=mock_response):
        res_msg = client.post(f"/api/conversations/{cid}/messages", json={"message": "你好！"})
        assert res_msg.status_code == 201
        data = res_msg.get_json()
        assert data["user_message"]["content"] == "你好！"
        assert data["assistant_message"]["content"] == "這是一條自動測試的 AI 回覆"
        mid = data["user_message"]["id"]

    # 讀取會話確認訊息已寫入
    res_conv = client.get(f"/api/conversations/{cid}")
    messages = res_conv.get_json()["messages"]
    assert len(messages) == 2

    # 修改單條訊息 (Update)
    res_patch = client.patch(f"/api/conversations/{cid}/messages/{mid}", json={"content": "修改後的提問"})
    assert res_patch.status_code == 200
    assert res_patch.get_json()["content"] == "修改後的提問"

    # 刪除單條訊息 (Delete)
    res_del_msg = client.delete(f"/api/conversations/{cid}/messages/{mid}")
    assert res_del_msg.status_code == 200

    # 驗證刪除後訊息已減少
    res_conv_after = client.get(f"/api/conversations/{cid}")
    remaining_ids = [m["id"] for m in res_conv_after.get_json()["messages"]]
    assert mid not in remaining_ids

# 4. 非法輸入與異常邊界測試
def test_invalid_inputs(client):
    # 發送訊息時缺少 message 欄位 -> 400
    res1 = client.post("/api/conversations/1/messages", json={})
    assert res1.status_code == 400

    # 發送空白 message -> 400
    res2 = client.post("/api/conversations/1/messages", json={"message": "   "})
    assert res2.status_code == 400

    # 修改會話名稱時傳入空 title -> 400
    res3 = client.patch("/api/conversations/1", json={"title": " "})
    assert res3.status_code == 400

    # 修改不存在的會話 -> 404
    res4 = client.patch("/api/conversations/99999", json={"title": "不存在"})
    assert res4.status_code == 404

    # 刪除不存在的會話 -> 404
    res5 = client.delete("/api/conversations/99999")
    assert res5.status_code == 404

    # 修改訊息時傳入空 content -> 400
    res6 = client.patch("/api/conversations/1/messages/1", json={"content": ""})
    assert res6.status_code == 400

    # 未設定 API KEY -> 500
    with patch.dict(os.environ, {"DEEPSEEK_API_KEY": ""}):
        res7 = client.post("/api/conversations/1/messages", json={"message": "測試無 Key"})
        assert res7.status_code == 500

    # DeepSeek 報錯 -> 502
    err_mock = MagicMock()
    err_mock.status_code = 500
    with patch("requests.post", return_value=err_mock):
        res8 = client.post("/api/conversations/1/messages", json={"message": "測試失敗"})
        assert res8.status_code == 502
