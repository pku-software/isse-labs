from flask import Flask, jsonify, request, send_from_directory


app = Flask(__name__, static_folder="frontend", static_url_path="/frontend")
app.json.ensure_ascii = False
messages = []
next_message_id = 1


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/hello")
def hello():
    return {"message": "你好"}


@app.post("/api/messages")
def create_message():
    global next_message_id

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get("message"), str):
        return {"error": "请提供 JSON 格式的 message 字符串"}, 400

    message = data["message"].strip()
    if not message:
        return {"error": "消息不能为空"}, 400

    record = {"id": next_message_id, "message": message, "reply": "你好"}
    next_message_id += 1
    messages.append(record)
    return record, 201


@app.get("/api/messages")
def list_messages():
    return jsonify(messages)


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    record = next((item for item in messages if item["id"] == message_id), None)
    if record is None:
        return {"error": "聊天记录不存在"}, 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get("message"), str):
        return {"error": "请提供 JSON 格式的 message 字符串"}, 400

    message = data["message"].strip()
    if not message:
        return {"error": "消息不能为空"}, 400

    record["message"] = message
    return record


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    record = next((item for item in messages if item["id"] == message_id), None)
    if record is None:
        return {"error": "聊天记录不存在"}, 404

    messages.remove(record)
    return {"message": "已删除"}


if __name__ == "__main__":
    app.run(port=5001, debug=True)
