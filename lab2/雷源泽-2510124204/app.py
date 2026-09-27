from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory


FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"

app = Flask(__name__)
app.json.ensure_ascii = False

messages = []
next_message_id = 1


def find_message(message_id):
    return next(
        (message for message in messages if message["id"] == message_id),
        None,
    )


def parse_message_payload():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, "请求体必须是 JSON 对象"

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return None, "message 不能为空"

    return message.strip(), None


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/style.css")
def stylesheet():
    return send_from_directory(FRONTEND_DIR, "style.css")


@app.get("/app.js")
def javascript():
    return send_from_directory(FRONTEND_DIR, "app.js")


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.post("/api/messages")
def create_message():
    global next_message_id

    message, error = parse_message_payload()
    if error:
        return jsonify({"error": error}), 400

    record = {
        "id": next_message_id,
        "message": message,
        "reply": "你好",
    }
    next_message_id += 1
    messages.append(record)

    return jsonify(record), 201


@app.get("/api/messages")
def list_messages():
    return jsonify(messages)


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    record = find_message(message_id)
    if record is None:
        return jsonify({"error": "聊天记录不存在"}), 404

    message, error = parse_message_payload()
    if error:
        return jsonify({"error": error}), 400

    record["message"] = message
    return jsonify(record)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    record = find_message(message_id)
    if record is None:
        return jsonify({"error": "聊天记录不存在"}), 404

    messages.remove(record)
    return jsonify({"deleted": message_id})


if __name__ == "__main__":
    app.run(port=5001, debug=True)
