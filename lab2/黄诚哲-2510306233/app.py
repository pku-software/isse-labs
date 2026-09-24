import os
import json

import requests
from flask import Flask, jsonify, request, send_from_directory
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"
DATA_FILE = os.path.join("data", "messages.json")

app = Flask(__name__)
app.json.ensure_ascii = False

# 内存中的聊天记录列表
messages = []
next_id = 1


def load_messages():
    global messages, next_id
    if not os.path.exists(DATA_FILE):
        messages = []
        next_id = 1
        return
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            messages = json.load(f)
        if not isinstance(messages, list):
            messages = []
    except (json.JSONDecodeError, OSError):
        messages = []
    next_id = max((m["id"] for m in messages), default=0) + 1


def save_messages():
    directory = os.path.dirname(DATA_FILE)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)


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

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return jsonify({"error": "缺少 DEEPSEEK_API_KEY"}), 500

    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": DEEPSEEK_MODEL,
                "messages": [{"role": "user", "content": message.strip()}],
            },
            timeout=60,
        )
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"]
    except requests.RequestException as exc:
        return jsonify({"error": f"调用 DeepSeek 失败: {exc}"}), 502
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        return jsonify({"error": f"解析 DeepSeek 响应失败: {exc}"}), 502

    record = {
        "id": next_id,
        "message": message.strip(),
        "reply": reply,
    }
    next_id += 1
    messages.append(record)
    save_messages()
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
    save_messages()
    return jsonify(record)


@app.route("/api/messages/<int:message_id>", methods=["DELETE"])
def delete_message(message_id):
    global messages
    record = next((m for m in messages if m["id"] == message_id), None)
    if record is None:
        return jsonify({"error": "记录不存在"}), 404
    messages = [m for m in messages if m["id"] != message_id]
    save_messages()
    return jsonify({"message": "删除成功"})


if __name__ == "__main__":
    load_messages()
    app.run(port=5001, debug=True)
