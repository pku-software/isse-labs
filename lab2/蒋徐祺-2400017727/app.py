import os

from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app = Flask(__name__)
app.json.ensure_ascii = False

# 聊天记录暂存在内存中，Flask 重启后会被清空。
messages = []


def next_message_id():
    return max((record["id"] for record in messages), default=0) + 1


def find_message(message_id):
    return next((record for record in messages if record["id"] == message_id), None)


def read_message_text():
    """从请求体中读出合法的 message 文本，不合法时返回 None。"""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None

    text = data.get("message")
    if not isinstance(text, str) or not text.strip():
        return None

    return text.strip()


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/<path:filename>")
def frontend_file(filename):
    """提供前端用到的静态文件，例如 style.css 和 app.js。"""
    return send_from_directory(FRONTEND_DIR, filename)


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.get("/api/messages")
def list_messages():
    return jsonify(messages)


@app.post("/api/messages")
def create_message():
    text = read_message_text()
    if text is None:
        return jsonify({"error": "请求体需要是 JSON，且 message 必须是非空字符串"}), 400

    record = {"id": next_message_id(), "message": text, "reply": "你好"}
    messages.append(record)
    return jsonify(record), 201


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    record = find_message(message_id)
    if record is None:
        return jsonify({"error": f"找不到 id 为 {message_id} 的聊天记录"}), 404

    text = read_message_text()
    if text is None:
        return jsonify({"error": "请求体需要是 JSON，且 message 必须是非空字符串"}), 400

    record["message"] = text
    return jsonify(record)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    record = find_message(message_id)
    if record is None:
        return jsonify({"error": f"找不到 id 为 {message_id} 的聊天记录"}), 404

    messages.remove(record)
    return jsonify(record)


if __name__ == "__main__":
    app.run(port=5001, debug=True)
