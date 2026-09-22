import os
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

# 載入當前目錄下的 .env 環境變數
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

app = Flask(__name__)
app.json.ensure_ascii = False

# 靜態檔案目錄
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

# 內存存儲聊天記錄
messages = []
next_id = 1

# DeepSeek API 配置
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# 提供前端靜態檔案
@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"message": "你好"})

# 1. 創建消息並調用 DeepSeek API
@app.route('/api/messages', methods=['POST'])
def create_message():
    global next_id
    data = request.get_json(silent=True)
    if not data or 'message' not in data or not str(data['message']).strip():
        return jsonify({"error": "缺少或無效的 message 欄位"}), 400

    user_text = str(data['message']).strip()

    # 安全讀取環境變數中的 API Key
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        return jsonify({"error": "未設定有效的 DEEPSEEK_API_KEY 環境變數，請檢查 .env 檔案"}), 500

    # 呼叫 DeepSeek 官方 API
    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": DEEPSEEK_MODEL,
                "messages": [
                    {"role": "user", "content": user_text}
                ],
                "stream": False
            },
            timeout=60
        )

        if response.status_code != 200:
            return jsonify({"error": f"DeepSeek API 錯誤（HTTP {response.status_code}）"}), 502

        res_json = response.json()
        ai_reply = res_json.get("choices", [{}])[0].get("message", {}).get("content", "無回覆內容")
    except requests.exceptions.Timeout:
        return jsonify({"error": "請求 DeepSeek API 超時，請稍後重試"}), 504
    except Exception as e:
        return jsonify({"error": f"請求 DeepSeek API 異常: {str(e)}"}), 502

    new_msg = {
        "id": next_id,
        "message": user_text,
        "reply": ai_reply
    }
    next_id += 1
    messages.append(new_msg)
    return jsonify(new_msg), 201

# 2. 獲取所有記錄
@app.route('/api/messages', methods=['GET'])
def get_messages():
    return jsonify(messages), 200

# 3. 修改記錄
@app.route('/api/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    data = request.get_json(silent=True)
    if not data or 'message' not in data or not str(data['message']).strip():
        return jsonify({"error": "缺少或無效的 message 欄位"}), 400

    target = next((m for m in messages if m['id'] == id), None)
    if not target:
        return jsonify({"error": f"找不到 ID 為 {id} 的消息"}), 404

    target['message'] = str(data['message']).strip()
    return jsonify(target), 200

# 4. 刪除記錄
@app.route('/api/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    global messages
    target = next((m for m in messages if m['id'] == id), None)
    if not target:
        return jsonify({"error": f"找不到 ID 為 {id} 的消息"}), 404

    messages = [m for m in messages if m['id'] != id]
    return jsonify({"message": f"成功刪除 ID 為 {id} 的消息"}), 200

if __name__ == '__main__':
    app.run(port=5001, debug=True)
