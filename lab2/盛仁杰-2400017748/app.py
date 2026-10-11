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
CONVERSATIONS_FILE = Path(__file__).parent / "data" / "conversations.json"
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
conversations = []
next_conversation_id = 1


def save_conversations():
    CONVERSATIONS_FILE.parent.mkdir(exist_ok=True)
    CONVERSATIONS_FILE.write_text(json.dumps(conversations, ensure_ascii=False, indent=2), encoding="utf-8")


if CONVERSATIONS_FILE.exists() and CONVERSATIONS_FILE.read_text(encoding="utf-8").strip():
    try:
        conversations.extend(json.loads(CONVERSATIONS_FILE.read_text(encoding="utf-8")))
    except json.JSONDecodeError:
        conversations.clear()
if conversations:
    next_conversation_id = max(item["id"] for item in conversations) + 1


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


@app.post("/api/conversations")
def create_conversation():
    global next_conversation_id
    data = request.get_json(silent=True) or {}
    conversation = {"id": next_conversation_id, "title": data.get("title", "新会话"), "messages": []}
    conversations.append(conversation)
    next_conversation_id += 1
    save_conversations()
    return jsonify(conversation), 201


@app.get("/api/conversations")
def list_conversations():
    return jsonify(conversations)


@app.patch("/api/conversations/<int:conversation_id>")
def update_conversation(conversation_id):
    data = request.get_json(silent=True) or {}
    for conversation in conversations:
        if conversation["id"] == conversation_id:
            if isinstance(data.get("title"), str) and data["title"].strip():
                conversation["title"] = data["title"].strip()
            save_conversations()
            return jsonify(conversation)
    return jsonify(error="会话不存在"), 404


@app.delete("/api/conversations/<int:conversation_id>")
def delete_conversation(conversation_id):
    for index, conversation in enumerate(conversations):
        if conversation["id"] == conversation_id:
            conversations.pop(index)
            save_conversations()
            return jsonify(message="删除成功")
    return jsonify(error="会话不存在"), 404


@app.post("/api/conversations/<int:conversation_id>/messages")
def create_conversation_message(conversation_id):
    data = request.get_json(silent=True) or {}
    message = data.get("message")
    conversation = next((item for item in conversations if item["id"] == conversation_id), None)
    if conversation is None:
        return jsonify(error="会话不存在"), 404
    if not isinstance(message, str) or not message.strip():
        return jsonify(error="message 不能为空"), 400
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return jsonify(error="未配置 DEEPSEEK_API_KEY"), 500
    prompt = conversation["messages"] + [{"role": "user", "content": message.strip()}]
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        completion = client.chat.completions.create(model="deepseek-v4-pro", messages=prompt)
        reply = completion.choices[0].message.content or ""
    except Exception:
        return jsonify(error="DeepSeek API 调用失败"), 502
    conversation["messages"].extend([
        {"role": "user", "content": message.strip()},
        {"role": "assistant", "content": reply},
    ])
    save_conversations()
    return jsonify(message=message.strip(), reply=reply)


if __name__ == "__main__":
    app.run(port=5001, debug=True)
