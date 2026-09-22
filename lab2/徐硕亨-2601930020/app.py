import os
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)
app.json.ensure_ascii = False

# 靜態檔案所在目錄
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')

# 內存存儲聊天記錄
# 格式: [{"id": 1, "message": "...", "reply": "..."}]
messages = []
next_id = 1

# 提供前端頁面與靜態資源
@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"message": "你好"})

# 1. 創建消息 (Create)
@app.route('/api/messages', methods=['POST'])
def create_message():
    global next_id
    data = request.get_json(silent=True)
    if not data or 'message' not in data or not str(data['message']).strip():
        return jsonify({"error": "缺少或無效的 message 欄位"}), 400

    new_msg = {
        "id": next_id,
        "message": str(data['message']).strip(),
        "reply": "你好"  # 本階段暫時固定回覆「你好」
    }
    next_id += 1
    messages.append(new_msg)
    return jsonify(new_msg), 201

# 2. 獲取全部消息 (Read)
@app.route('/api/messages', methods=['GET'])
def get_messages():
    return jsonify(messages), 200

# 3. 修改消息內容 (Update)
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

# 4. 刪除消息 (Delete)
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
