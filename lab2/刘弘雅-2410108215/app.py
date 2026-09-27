from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)
app.json.ensure_ascii = False

FRONTEND_DIR = str(Path(__file__).resolve().parent / "frontend")

messages = []
next_id = 1


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

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not str(data.get("message", "")).strip():
        return jsonify({"error": "message 不能为空"}), 400

    record = {
        "id": next_id,
        "message": str(data["message"]).strip(),
        "reply": "你好",
    }
    messages.append(record)
    next_id += 1
    return jsonify(record), 201


@app.get("/api/messages")
def list_messages():
    return jsonify(messages)


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not str(data.get("message", "")).strip():
        return jsonify({"error": "message 不能为空"}), 400

    for record in messages:
        if record["id"] == message_id:
            record["message"] = str(data["message"]).strip()
            return jsonify(record)

    return jsonify({"error": "消息不存在"}), 404


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    for index, record in enumerate(messages):
        if record["id"] == message_id:
            del messages[index]
            return jsonify({"deleted": message_id})

    return jsonify({"error": "消息不存在"}), 404


if __name__ == "__main__":
    app.run(port=5001, debug=True)
