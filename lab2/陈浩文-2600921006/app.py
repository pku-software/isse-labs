from itertools import count

from flask import Flask, jsonify, request

app = Flask(__name__, static_folder="frontend", static_url_path="/static")
app.json.ensure_ascii = False

# 数据只存在于当前 Flask 进程，重启后会清空。
messages = []
message_ids = count(1)


def read_message_text():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, "请求体必须是有效的 JSON 对象"

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return None, "message 必须是非空字符串"

    return message.strip(), None


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.post("/api/messages")
def create_message():
    text, error = read_message_text()
    if error:
        return jsonify({"error": error}), 400

    record = {"id": next(message_ids), "message": text, "reply": "你好"}
    messages.append(record)
    return jsonify(record), 201


@app.get("/api/messages")
def list_messages():
    return jsonify(messages)


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    record = next((item for item in messages if item["id"] == message_id), None)
    if record is None:
        return jsonify({"error": "聊天记录不存在"}), 404

    text, error = read_message_text()
    if error:
        return jsonify({"error": error}), 400

    record["message"] = text
    return jsonify(record)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    record = next((item for item in messages if item["id"] == message_id), None)
    if record is None:
        return jsonify({"error": "聊天记录不存在"}), 404

    messages.remove(record)
    return jsonify({"id": message_id, "deleted": True})


if __name__ == "__main__":
    app.run(port=5001, debug=True)
