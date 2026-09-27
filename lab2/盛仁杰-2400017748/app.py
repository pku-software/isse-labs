import os
import json
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from openai import OpenAI


app = Flask(__name__)
app.json.ensure_ascii = False
messages = []
next_id = 1
DATA_FILE = Path(__file__).parent / "data" / "messages.json"
load_dotenv()


def load_messages():
    if not DATA_FILE.exists() or not DATA_FILE.read_text(encoding="utf-8").strip():
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def save_messages():
    DATA_FILE.parent.mkdir(exist_ok=True)
    DATA_FILE.write_text(
        json.dumps(messages, ensure_ascii=False, indent=2), encoding="utf-8"
    )


messages.extend(load_messages())
if messages:
    next_id = max(record["id"] for record in messages) + 1


@app.get("/")
def index():
    return send_from_directory("frontend", "index.html")


@app.get("/style.css")
def stylesheet():
    return send_from_directory("frontend", "style.css")


@app.get("/app.js")
def javascript():
    return send_from_directory("frontend", "app.js")


@app.get("/api/hello")
def hello():
    return jsonify(message="你好")


@app.post("/api/messages")
def create_message():
    global next_id
    data = request.get_json(silent=True) or {}
    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return jsonify(error="message 不能为空"), 400

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return jsonify(error="未配置 DEEPSEEK_API_KEY"), 500

    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        completion = client.chat.completions.create(
            model="deepseek-v4-pro",
            messages=[{"role": "user", "content": message.strip()}],
        )
        reply = completion.choices[0].message.content or ""
    except Exception:
        return jsonify(error="DeepSeek API 调用失败"), 502

    record = {"id": next_id, "message": message.strip(), "reply": reply}
    messages.append(record)
    next_id += 1
    save_messages()
    return jsonify(record), 201


@app.get("/api/messages")
def list_messages():
    return jsonify(messages)


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    data = request.get_json(silent=True) or {}
    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return jsonify(error="message 不能为空"), 400

    for record in messages:
        if record["id"] == message_id:
            record["message"] = message.strip()
            save_messages()
            return jsonify(record)
    return jsonify(error="聊天记录不存在"), 404


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    for index, record in enumerate(messages):
        if record["id"] == message_id:
            messages.pop(index)
            save_messages()
            return jsonify(message="删除成功")
    return jsonify(error="聊天记录不存在"), 404


if __name__ == "__main__":
    app.run(port=5001, debug=True)
