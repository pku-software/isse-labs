import os

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request


load_dotenv()

app = Flask(__name__, static_folder="frontend", static_url_path="")
app.json.ensure_ascii = False

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# 聊天记录保存在内存中，Flask 重启后会清空。
messages = []
next_id = 1


def call_deepseek(message):
    resp = requests.post(
        f"{DEEPSEEK_BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": DEEPSEEK_MODEL,
            "messages": [{"role": "user", "content": message}],
            "stream": False,
        },
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.route("/api/messages", methods=["POST"])
def create_message():
    global next_id

    if not DEEPSEEK_API_KEY:
        return jsonify({"error": "缺少 DEEPSEEK_API_KEY，请检查 .env 配置"}), 500

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "message" not in data:
        return jsonify({"error": "缺少 message 字段"}), 400

    message = str(data["message"]).strip()
    if not message:
        return jsonify({"error": "message 不能为空"}), 400

    try:
        reply = call_deepseek(message)
    except Exception as exc:
        return jsonify({"error": f"调用 DeepSeek 失败：{exc}"}), 502

    record = {"id": next_id, "message": message, "reply": reply}
    next_id += 1
    messages.append(record)
    return jsonify(record), 201


@app.route("/api/messages", methods=["GET"])
def list_messages():
    return jsonify(messages)


@app.route("/api/messages/<int:message_id>", methods=["PATCH"])
def update_message(message_id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "message" not in data:
        return jsonify({"error": "缺少 message 字段"}), 400

    message = str(data["message"]).strip()
    if not message:
        return jsonify({"error": "message 不能为空"}), 400

    for record in messages:
        if record["id"] == message_id:
            record["message"] = message
            return jsonify(record)

    return jsonify({"error": "记录不存在"}), 404


@app.route("/api/messages/<int:message_id>", methods=["DELETE"])
def delete_message(message_id):
    for index, record in enumerate(messages):
        if record["id"] == message_id:
            messages.pop(index)
            return jsonify({"deleted": message_id})

    return jsonify({"error": "记录不存在"}), 404


if __name__ == "__main__":
    app.run(port=5001, debug=True)
