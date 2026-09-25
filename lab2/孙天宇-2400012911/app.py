"""提供聊天页面和基于进程内存的问答记录 API。"""

from itertools import count
from threading import Lock

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

app = Flask(__name__, static_folder="frontend", static_url_path="/static")
app.json.ensure_ascii = False

# 记录只属于当前进程，重启后会清空。
messages = []
message_ids = count(1)
messages_lock = Lock()


def read_message():
    """只接受包含非空字符串 message 的 JSON 对象。"""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None
    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return None
    return message.strip()


@app.errorhandler(HTTPException)
def http_error(error):
    response = error.get_response()
    response.data = app.json.dumps({"error": error.description})
    response.content_type = "application/json"
    return response


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api/hello")
def hello():
    return jsonify(message="你好")


@app.post("/api/messages")
def create_message():
    message = read_message()
    if message is None:
        return jsonify(error="请提交 JSON 对象，message 必须是非空字符串。"), 400
    with messages_lock:
        record = {"id": next(message_ids), "message": message, "reply": "你好"}
        messages.append(record)
        return jsonify(record), 201


@app.get("/api/messages")
def list_messages():
    with messages_lock:
        return jsonify(messages)


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    message = read_message()
    if message is None:
        return jsonify(error="请提交 JSON 对象，message 必须是非空字符串。"), 400
    with messages_lock:
        for record in messages:
            if record["id"] == message_id:
                record["message"] = message
                return jsonify(record)
    return jsonify(error="聊天记录不存在，请重新加载记录。"), 404


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    with messages_lock:
        for index, record in enumerate(messages):
            if record["id"] == message_id:
                messages.pop(index)
                return jsonify(id=message_id, message="问答已删除。")
    return jsonify(error="聊天记录不存在，请重新加载记录。"), 404


if __name__ == "__main__":
    app.run(port=5001, debug=True)
