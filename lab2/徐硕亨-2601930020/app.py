import os
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

app = Flask(__name__)
app.json.ensure_ascii = False

FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

# 內存存儲多會話
# 格式:
# [
#   {
#     "id": 1,
#     "title": "新會話 1",
#     "messages": [
#       {"id": 1, "role": "user", "content": "..."},
#       {"id": 2, "role": "assistant", "content": "..."}
#     ]
#   }
# ]
conversations = [
    {
        "id": 1,
        "title": "預設會話",
        "messages": []
    }
]
next_conv_id = 2
next_msg_id = 1

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# 提供前端頁面
@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"message": "你好"})

# ----------------- 會話 (Conversation) API -----------------

# 1. 建立會話
@app.route('/api/conversations', methods=['POST'])
def create_conversation():
    global next_conv_id
    data = request.get_json(silent=True) or {}
    title = str(data.get('title', '')).strip() or f"會話 {next_conv_id}"

    new_conv = {
        "id": next_conv_id,
        "title": title,
        "messages": []
    }
    next_conv_id += 1
    conversations.append(new_conv)
    return jsonify(new_conv), 201

# 2. 獲取所有會話列表
@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    # 回傳會話摘要資訊（含訊息數量）
    summary = [
        {
            "id": c["id"],
            "title": c["title"],
            "message_count": len(c["messages"])
        }
        for c in conversations
    ]
    return jsonify(summary), 200

# 3. 獲取特定會話詳情（含完整訊息紀錄）
@app.route('/api/conversations/<int:id>', methods=['GET'])
def get_conversation(id):
    conv = next((c for c in conversations if c["id"] == id), None)
    if not conv:
        return jsonify({"error": f"找不到 ID 為 {id} 的會話"}), 404
    return jsonify(conv), 200

# 4. 修改會話名稱 (Rename)
@app.route('/api/conversations/<int:id>', methods=['PATCH'])
def update_conversation(id):
    data = request.get_json(silent=True)
    if not data or 'title' not in data or not str(data['title']).strip():
        return jsonify({"error": "缺少有效的 title 欄位"}), 400

    conv = next((c for c in conversations if c["id"] == id), None)
    if not conv:
        return jsonify({"error": f"找不到 ID 為 {id} 的會話"}), 404

    conv['title'] = str(data['title']).strip()
    return jsonify(conv), 200

# 5. 刪除會話
@app.route('/api/conversations/<int:id>', methods=['DELETE'])
def delete_conversation(id):
    global conversations
    conv = next((c for c in conversations if c["id"] == id), None)
    if not conv:
        return jsonify({"error": f"找不到 ID 為 {id} 的會話"}), 404

    conversations = [c for c in conversations if c["id"] != id]
    # 若刪空則自動補一個預設會話
    if not conversations:
        conversations.append({"id": 1, "title": "預設會話", "messages": []})

    return jsonify({"message": f"成功刪除 ID 為 {id} 的會話"}), 200

# 6. 在特定會話中發送訊息（攜帶歷史上下文調用 DeepSeek）
@app.route('/api/conversations/<int:id>/messages', methods=['POST'])
def send_conversation_message(id):
    global next_msg_id
    conv = next((c for c in conversations if c["id"] == id), None)
    if not conv:
        return jsonify({"error": f"找不到 ID 為 {id} 的會話"}), 404

    data = request.get_json(silent=True)
    if not data or 'message' not in data or not str(data['message']).strip():
        return jsonify({"error": "缺少或無效的 message 欄位"}), 400

    user_text = str(data['message']).strip()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        return jsonify({"error": "未設定有效的 DEEPSEEK_API_KEY 環境變數"}), 500

    # 構造上下文：將目前會話中的歷史對話組成 messages 陣列
    history_payload = [
        {"role": m["role"], "content": m["content"]}
        for m in conv["messages"]
    ]
    # 加上當前使用者的新問題
    history_payload.append({"role": "user", "content": user_text})

    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": DEEPSEEK_MODEL,
                "messages": history_payload,
                "stream": False
            },
            timeout=60
        )

        if response.status_code != 200:
            return jsonify({"error": f"DeepSeek API 錯誤（HTTP {response.status_code}）"}), 502

        res_json = response.json()
        ai_reply = res_json.get("choices", [{}])[0].get("message", {}).get("content", "無回覆內容")
    except requests.exceptions.Timeout:
        return jsonify({"error": "請求 DeepSeek API 超時"}), 504
    except Exception as e:
        return jsonify({"error": f"請求 DeepSeek API 異常: {str(e)}"}), 502

    # 存入對話歷史中
    user_msg_obj = {
        "id": next_msg_id,
        "role": "user",
        "content": user_text
    }
    assistant_msg_obj = {
        "id": next_msg_id + 1,
        "role": "assistant",
        "content": ai_reply
    }
    next_msg_id += 2

    conv["messages"].append(user_msg_obj)
    conv["messages"].append(assistant_msg_obj)

    # 若會話標題仍是預設名稱，可用第一句話前10字自動命名
    if conv["title"].startswith("會話 ") or conv["title"] == "預設會話":
        if len(conv["messages"]) == 2:
            conv["title"] = user_text[:12] + ("..." if len(user_text) > 12 else "")

    return jsonify({
        "user_message": user_msg_obj,
        "assistant_message": assistant_msg_obj,
        "conversation": conv
    }), 201

# 7. 修改會話中的單條訊息
@app.route('/api/conversations/<int:cid>/messages/<int:mid>', methods=['PATCH'])
def update_conv_message(cid, mid):
    conv = next((c for c in conversations if c["id"] == cid), None)
    if not conv:
        return jsonify({"error": f"找不到會話 {cid}"}), 404

    data = request.get_json(silent=True)
    if not data or 'content' not in data or not str(data['content']).strip():
        return jsonify({"error": "缺少有效的 content 欄位"}), 400

    target = next((m for m in conv["messages"] if m["id"] == mid), None)
    if not target:
        return jsonify({"error": f"找不到訊息 {mid}"}), 404

    target["content"] = str(data["content"]).strip()
    return jsonify(target), 200

# 8. 刪除會話中的單條訊息
@app.route('/api/conversations/<int:cid>/messages/<int:mid>', methods=['DELETE'])
def delete_conv_message(cid, mid):
    conv = next((c for c in conversations if c["id"] == cid), None)
    if not conv:
        return jsonify({"error": f"找不到會話 {cid}"}), 404

    conv["messages"] = [m for m in conv["messages"] if m["id"] != mid]
    return jsonify({"message": f"成功刪除訊息 {mid}"}), 200

if __name__ == '__main__':
    app.run(port=5001, debug=True)
