from flask import Flask, jsonify, request, send_from_directory


app = Flask(__name__, static_folder="frontend", static_url_path="")
app.json.ensure_ascii = False

messages = []
next_message_id = 1


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.post("/api/messages")
def create_message():
    global next_message_id

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "请提供 JSON 格式的请求数据"}), 400

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "message 不能为空"}), 400

    record = {
        "id": next_message_id,
        "message": message.strip(),
        "reply": "你好",
    }
    messages.append(record)
    next_message_id += 1
    return jsonify(record), 201


@app.get("/api/messages")
def list_messages():
    return jsonify(messages)


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    record = next((item for item in messages if item["id"] == message_id), None)
    if record is None:
        return jsonify({"error": "聊天记录不存在"}), 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "请提供 JSON 格式的请求数据"}), 400

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "message 不能为空"}), 400

    record["message"] = message.strip()
    return jsonify(record)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    record = next((item for item in messages if item["id"] == message_id), None)
    if record is None:
        return jsonify({"error": "聊天记录不存在"}), 404

    messages.remove(record)
    return jsonify({"message": "聊天记录已删除"})


if __name__ == "__main__":
    app.run(port=5001, debug=True)
