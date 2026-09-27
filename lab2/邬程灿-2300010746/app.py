import os

from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)
app.json.ensure_ascii = False

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")

messages = []
next_id = 1


def find_message(message_id):
    for item in messages:
        if item["id"] == message_id:
            return item
    return None


def read_message_text():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "message" not in data:
        return None, (jsonify({"error": "缺少 message"}), 400)
    text = data["message"]
    if not isinstance(text, str) or not text.strip():
        return None, (jsonify({"error": "message 不能为空"}), 400)
    return text.strip(), None


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/style.css")
def style_css():
    return send_from_directory(FRONTEND_DIR, "style.css")


@app.get("/app.js")
def app_js():
    return send_from_directory(FRONTEND_DIR, "app.js")


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.post("/api/messages")
def create_message():
    global next_id
    text, error = read_message_text()
    if error is not None:
        return error
    record = {"id": next_id, "message": text, "reply": "你好"}
    next_id += 1
    messages.append(record)
    return jsonify(record), 201


@app.get("/api/messages")
def list_messages():
    return jsonify(messages)


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    record = find_message(message_id)
    if record is None:
        return jsonify({"error": "记录不存在", "id": message_id}), 404
    text, error = read_message_text()
    if error is not None:
        return error
    record["message"] = text
    return jsonify(record)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    record = find_message(message_id)
    if record is None:
        return jsonify({"error": "记录不存在", "id": message_id}), 404
    messages.remove(record)
    return jsonify(record)


if __name__ == "__main__":
    app.run(port=5001, debug=True)
