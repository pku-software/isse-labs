from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)
app.json.ensure_ascii = False

# 内存中的聊天记录列表
messages = []
next_id = 1


@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")


@app.route("/style.css")
def style():
    return send_from_directory("frontend", "style.css")


@app.route("/app.js")
def script():
    return send_from_directory("frontend", "app.js")


@app.route("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.route("/api/messages", methods=["POST"])
def create_message():
    global next_id
    data = request.get_json(silent=True)
    if not data or "message" not in data:
        return jsonify({"error": "缺少 message 字段"}), 400
    message = data["message"]
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "message 不能为空"}), 400

    record = {
        "id": next_id,
        "message": message.strip(),
        "reply": "你好",
    }
    next_id += 1
    messages.append(record)
    return jsonify(record), 201


@app.route("/api/messages", methods=["GET"])
def list_messages():
    return jsonify(messages)


@app.route("/api/messages/<int:message_id>", methods=["PATCH"])
def update_message(message_id):
    record = next((m for m in messages if m["id"] == message_id), None)
    if record is None:
        return jsonify({"error": "记录不存在"}), 404

    data = request.get_json(silent=True)
    if not data or "message" not in data:
        return jsonify({"error": "缺少 message 字段"}), 400
    message = data["message"]
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "message 不能为空"}), 400

    record["message"] = message.strip()
    return jsonify(record)


@app.route("/api/messages/<int:message_id>", methods=["DELETE"])
def delete_message(message_id):
    global messages
    record = next((m for m in messages if m["id"] == message_id), None)
    if record is None:
        return jsonify({"error": "记录不存在"}), 404
    messages = [m for m in messages if m["id"] != message_id]
    return jsonify({"message": "删除成功"})


if __name__ == "__main__":
    app.run(port=5001, debug=True)
