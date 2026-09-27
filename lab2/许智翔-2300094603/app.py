from flask import Flask, jsonify, render_template, request

app = Flask(__name__, template_folder="frontend", static_folder="frontend", static_url_path="/static")
app.json.ensure_ascii = False

# 当前阶段只保存在 Flask 进程内存中，重启后记录会清空。
messages = []
next_message_id = 1


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.post("/api/messages")
def create_message():
    global next_message_id
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "请求内容必须是 JSON 对象。"}), 400

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "message 不能为空，且必须是文本。"}), 400

    record = {
        "id": next_message_id,
        "message": message.strip(),
        "reply": "你好",
    }
    next_message_id += 1
    messages.append(record)
    return jsonify(record), 201


@app.get("/api/messages")
def list_messages():
    return jsonify({"messages": messages})


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "请求内容必须是 JSON 对象。"}), 400

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "message 不能为空，且必须是文本。"}), 400

    record = next((item for item in messages if item["id"] == message_id), None)
    if record is None:
        return jsonify({"error": "聊天记录不存在。"}), 404

    record["message"] = message.strip()
    return jsonify(record)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    index = next((i for i, item in enumerate(messages) if item["id"] == message_id), None)
    if index is None:
        return jsonify({"error": "聊天记录不存在。"}), 404

    deleted = messages.pop(index)
    return jsonify({"message": "聊天记录已删除。", "id": deleted["id"]})


if __name__ == "__main__":
    app.run(port=5001, debug=True)
