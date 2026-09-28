from pathlib import Path
import json
import os

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__)
app.json.ensure_ascii = False

FRONTEND_DIR = str(BASE_DIR / "frontend")

DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "messages.json"

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"


def load_messages():
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        return []

    if not isinstance(data, list):
        return []

    return [record for record in data if isinstance(record, dict)]


def save_messages():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(messages, file, ensure_ascii=False, indent=2)


messages = load_messages()
next_id = max((int(record.get("id", 0)) for record in messages), default=0) + 1


def get_deepseek_reply(message):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DeepSeek API Key 未配置")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [{"role": "user", "content": message}],
        "stream": False,
    }

    response = requests.post(
        DEEPSEEK_API_URL,
        headers=headers,
        json=payload,
        timeout=30,
    )
    if response.status_code != 200:
        raise RuntimeError("DeepSeek 模型调用失败")

    try:
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError):
        raise RuntimeError("DeepSeek 返回格式异常")


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

    user_message = str(data["message"]).strip()

    try:
        reply = get_deepseek_reply(user_message)
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 502
    except Exception:
        return jsonify({"error": "DeepSeek 模型调用失败"}), 502

    record = {
        "id": next_id,
        "message": user_message,
        "reply": reply,
    }
    messages.append(record)
    next_id += 1
    save_messages()
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
            save_messages()
            return jsonify(record)

    return jsonify({"error": "消息不存在"}), 404


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    for index, record in enumerate(messages):
        if record["id"] == message_id:
            del messages[index]
            save_messages()
            return jsonify({"deleted": message_id})

    return jsonify({"error": "消息不存在"}), 404


if __name__ == "__main__":
    app.run(port=5001, debug=True)
