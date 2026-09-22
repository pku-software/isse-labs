from flask import Flask, jsonify, request


app = Flask(__name__, static_folder="frontend", static_url_path="")
app.json.ensure_ascii = False

messages = []
next_message_id = 1


def find_message(message_id):
    return next((item for item in messages if item["id"] == message_id), None)


def read_message_from_request():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, "请提供 JSON 格式的请求体"

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
    global next_message_id

    message, error = read_message_from_request()
    if error:
        return jsonify({"error": error}), 400

    record = {"id": next_message_id, "message": message, "reply": "你好"}
    messages.append(record)
    next_message_id += 1
    return jsonify(record), 201


@app.get("/api/messages")
def list_messages():
    return jsonify(messages)


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    record = find_message(message_id)
    if record is None:
        return jsonify({"error": "聊天记录不存在"}), 404

    message, error = read_message_from_request()
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
    return jsonify({"message": "聊天记录已删除"})


if __name__ == "__main__":
    app.run(port=5001, debug=True)
