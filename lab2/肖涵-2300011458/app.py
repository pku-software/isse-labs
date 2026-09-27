from flask import Flask, jsonify, request, send_from_directory


app = Flask(__name__, static_folder="frontend", static_url_path="")
app.json.ensure_ascii = False

messages = []
next_message_id = 1


def find_message(message_id: int):
    return next((message for message in messages if message["id"] == message_id), None)


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/hello")
def hello():
    return jsonify(message="你好")


@app.post("/api/messages")
def create_message():
    global next_message_id

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="请求体必须是 JSON 对象"), 400

    message_text = data.get("message")
    if not isinstance(message_text, str) or not message_text.strip():
        return jsonify(error="message 必须是非空字符串"), 400

    record = {
        "id": next_message_id,
        "message": message_text.strip(),
        "reply": "你好",
    }
    messages.append(record)
    next_message_id += 1

    return jsonify(record), 201


@app.get("/api/messages")
def list_messages():
    return jsonify(messages)


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id: int):
    record = find_message(message_id)
    if record is None:
        return jsonify(error="聊天记录不存在"), 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="请求体必须是 JSON 对象"), 400

    message_text = data.get("message")
    if not isinstance(message_text, str) or not message_text.strip():
        return jsonify(error="message 必须是非空字符串"), 400

    record["message"] = message_text.strip()
    return jsonify(record)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id: int):
    record = find_message(message_id)
    if record is None:
        return jsonify(error="聊天记录不存在"), 404

    messages.remove(record)
    return "", 204


if __name__ == "__main__":
    app.run(port=5001, debug=True)
