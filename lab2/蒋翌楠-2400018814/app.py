from flask import Flask, jsonify, request

app = Flask(__name__, static_folder="frontend", static_url_path="")
app.json.ensure_ascii = False
messages = []
next_id = 1


@app.get("/")
def index():
    return app.send_static_file("index.html")


def read_message():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None
    message = data.get("message")
    return message.strip() if isinstance(message, str) else None


@app.get("/api/hello")
def hello():
    return jsonify(message="你好")


@app.post("/api/messages")
def create_message():
    global next_id
    message = read_message()
    if not message:
        return jsonify(error="请提供非空的 message 字符串"), 400
    record = {"id": next_id, "message": message, "reply": "你好"}
    next_id += 1
    messages.append(record)
    return jsonify(record), 201


@app.get("/api/messages")
def list_messages():
    return jsonify(messages)


@app.patch("/api/messages/<int:id>")
def update_message(id):
    record = next((item for item in messages if item["id"] == id), None)
    if record is None:
        return jsonify(error="聊天记录不存在"), 404
    message = read_message()
    if not message:
        return jsonify(error="请提供非空的 message 字符串"), 400
    record["message"] = message
    return jsonify(record)


@app.delete("/api/messages/<int:id>")
def delete_message(id):
    record = next((item for item in messages if item["id"] == id), None)
    if record is None:
        return jsonify(error="聊天记录不存在"), 404
    messages.remove(record)
    return jsonify(message="已删除聊天记录")


if __name__ == "__main__":
    app.run(port=5001, debug=True)
