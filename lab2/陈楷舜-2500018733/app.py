"""提供聊天页面和仅在内存中保存记录的 CRUD API。"""

from itertools import count
from threading import Lock

from flask import Flask, jsonify, request
from werkzeug.exceptions import BadRequest, HTTPException, NotFound, UnsupportedMediaType


# 将 frontend 中的文件映射到根路径，供 HTML 中的相对资源地址使用。
app = Flask(__name__, static_folder="frontend", static_url_path="")
app.json.ensure_ascii = False

messages = {}
message_ids = count(1)
messages_lock = Lock()
MAX_MESSAGE_LENGTH = 4000


def read_message():
    """校验 JSON 请求中的 message，并去掉首尾空白。"""
    if not request.is_json:
        raise UnsupportedMediaType("请使用 application/json 格式发送请求")
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise BadRequest("请求内容必须是有效的 JSON 对象")
    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        raise BadRequest("message 必须是非空字符串")
    message = message.strip()
    if len(message) > MAX_MESSAGE_LENGTH:
        raise BadRequest(f"消息不能超过 {MAX_MESSAGE_LENGTH} 个字符")
    return message


@app.errorhandler(HTTPException)
def handle_http_error(error):
    if request.path.startswith("/api/"):
        return jsonify({"error": error.description}), error.code
    return error


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.post("/api/messages")
def create_message():
    message = read_message()
    with messages_lock:
        record = {"id": next(message_ids), "message": message, "reply": "你好"}
        messages[record["id"]] = record
        return jsonify(record), 201


@app.get("/api/messages")
def list_messages():
    with messages_lock:
        return jsonify(list(messages.values()))


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    message = read_message()
    with messages_lock:
        record = messages.get(message_id)
        if record is None:
            raise NotFound("找不到这条聊天记录，请刷新列表后重试")
        record["message"] = message
        return jsonify(record)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    with messages_lock:
        if messages.pop(message_id, None) is None:
            raise NotFound("找不到这条聊天记录，请刷新列表后重试")
    return "", 204


if __name__ == "__main__":
    app.run(port=5001, debug=True)
