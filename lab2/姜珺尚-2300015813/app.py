"""Chat page and JSON API with in-memory records."""

from itertools import count
from threading import Lock

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

app = Flask(__name__, static_folder="frontend", static_url_path="/static")
app.json.ensure_ascii = False

messages = []
message_ids = count(1)
messages_lock = Lock()


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api/hello")
def hello():
    return jsonify(message="你好")


def read_message():
    if not request.is_json:
        return None, (jsonify(error="请使用 application/json 发送请求"), 415)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, (jsonify(error="请求体必须是有效的 JSON 对象"), 400)
    text = data.get("message")
    if not isinstance(text, str) or not text.strip():
        return None, (jsonify(error="message 必须是非空字符串"), 400)
    return text.strip(), None


@app.post("/api/messages")
def create_message():
    text, error = read_message()
    if error is not None:
        return error
    with messages_lock:
        record = {"id": next(message_ids), "message": text, "reply": "你好"}
        messages.append(record)
        return jsonify(record), 201


@app.get("/api/messages")
def list_messages():
    with messages_lock:
        return jsonify(messages)


@app.patch("/api/messages/<int:id>")
def update_message(id):
    text, error = read_message()
    if error is not None:
        return error
    with messages_lock:
        for record in messages:
            if record["id"] == id:
                record["message"] = text
                return jsonify(record)
    return jsonify(error="聊天记录不存在，请刷新记录列表"), 404


@app.delete("/api/messages/<int:id>")
def delete_message(id):
    with messages_lock:
        for position, record in enumerate(messages):
            if record["id"] == id:
                del messages[position]
                return jsonify(id=id, deleted=True)
    return jsonify(error="聊天记录不存在，请刷新记录列表"), 404


@app.errorhandler(HTTPException)
def http_error(error):
    return jsonify(error=error.description), error.code


if __name__ == "__main__":
    app.run(port=5001, debug=True)
