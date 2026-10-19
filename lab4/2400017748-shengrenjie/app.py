import os
import json
from pathlib import Path
from functools import wraps
from threading import RLock
import math
import time

from flask import Flask, jsonify, request, send_from_directory
from openai import OpenAI
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from metrics import measure_chat


app = Flask(__name__)
app.json.ensure_ascii = False
MODE = os.getenv("CHAT_MODE", "mock")
if MODE not in ("mock", "real"):
    raise ValueError("CHAT_MODE must be mock or real")
storage_lock = RLock()
messages = []
next_id = 1
DATA_DIR = Path(__file__).parent / ".runtime" / "app"
DATA_FILE = DATA_DIR / "messages.json"
CONVERSATIONS_FILE = DATA_DIR / "conversations.json"


def load_messages():
    if not DATA_FILE.exists() or not DATA_FILE.read_text(encoding="utf-8").strip():
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def save_messages():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(
        json.dumps(messages, ensure_ascii=False, indent=2), encoding="utf-8"
    )


messages.extend(load_messages())
if messages:
    next_id = max(record["id"] for record in messages) + 1
conversations = []
next_conversation_id = 1


def save_conversations():
    CONVERSATIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONVERSATIONS_FILE.write_text(json.dumps(conversations, ensure_ascii=False, indent=2), encoding="utf-8")


if CONVERSATIONS_FILE.exists() and CONVERSATIONS_FILE.read_text(encoding="utf-8").strip():
    try:
        conversations.extend(json.loads(CONVERSATIONS_FILE.read_text(encoding="utf-8")))
    except json.JSONDecodeError:
        conversations.clear()
if conversations:
    next_conversation_id = max(item["id"] for item in conversations) + 1


def locked_storage(function):
    @wraps(function)
    def locked(*args, **kwargs):
        with storage_lock:
            return function(*args, **kwargs)
    return locked


def model_reply(prompt, data):
    if MODE == "mock":
        delay = data.get("mock_delay_seconds", 0.1)
        force_error = data.get("mock_force_error", False)
        if (isinstance(delay, bool) or not isinstance(delay, (int, float))
                or not math.isfinite(delay) or not 0 <= delay <= 10
                or not isinstance(force_error, bool)):
            return None, (jsonify(error="无效的 mock 参数"), 400)
        time.sleep(delay)
        if force_error:
            return None, (jsonify(error="模拟模型调用失败", simulated=True), 503)
        return "这是本地 mock 测试回复。", None

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return None, (jsonify(error="未配置 DEEPSEEK_API_KEY"), 500)
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        completion = client.chat.completions.create(model="deepseek-v4-pro", messages=prompt)
        return completion.choices[0].message.content or "", None
    except Exception:
        return None, (jsonify(error="DeepSeek API 调用失败"), 502)


@app.get("/metrics")
def metrics():
    return app.response_class(generate_latest(), content_type=CONTENT_TYPE_LATEST)


@app.get("/api/lab-status")
def lab_status():
    if MODE != "mock":
        return jsonify(error="实验状态接口仅在 mock 模式可用"), 404
    return jsonify(mode=MODE, external_model_calls=False)


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
@measure_chat
def create_message():
    global next_id
    data = request.get_json(silent=True) or {}
    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return jsonify(error="message 不能为空"), 400

    reply, error = model_reply([{"role": "user", "content": message.strip()}], data)
    if error is not None:
        return error

    with storage_lock:
        record = {"id": next_id, "message": message.strip(), "reply": reply}
        messages.append(record)
        next_id += 1
        save_messages()
        return jsonify(record), 201


@app.get("/api/messages")
@locked_storage
def list_messages():
    return jsonify(messages)


@app.patch("/api/messages/<int:message_id>")
@locked_storage
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
@locked_storage
def delete_message(message_id):
    for index, record in enumerate(messages):
        if record["id"] == message_id:
            messages.pop(index)
            save_messages()
            return jsonify(message="删除成功")
    return jsonify(error="聊天记录不存在"), 404


@app.post("/api/conversations")
@locked_storage
def create_conversation():
    global next_conversation_id
    data = request.get_json(silent=True) or {}
    conversation = {"id": next_conversation_id, "title": data.get("title", "新会话"), "messages": []}
    conversations.append(conversation)
    next_conversation_id += 1
    save_conversations()
    return jsonify(conversation), 201


@app.get("/api/conversations")
@locked_storage
def list_conversations():
    return jsonify(conversations)


@app.patch("/api/conversations/<int:conversation_id>")
@locked_storage
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
@locked_storage
def delete_conversation(conversation_id):
    for index, conversation in enumerate(conversations):
        if conversation["id"] == conversation_id:
            conversations.pop(index)
            save_conversations()
            return jsonify(message="删除成功")
    return jsonify(error="会话不存在"), 404


@app.post("/api/conversations/<int:conversation_id>/messages")
@measure_chat
def create_conversation_message(conversation_id):
    data = request.get_json(silent=True) or {}
    message = data.get("message")
    with storage_lock:
        conversation = next((item for item in conversations if item["id"] == conversation_id), None)
        if conversation is None:
            return jsonify(error="会话不存在"), 404
        if not isinstance(message, str) or not message.strip():
            return jsonify(error="message 不能为空"), 400
        prompt = list(conversation["messages"]) + [{"role": "user", "content": message.strip()}]
    reply, error = model_reply(prompt, data)
    if error is not None:
        return error
    with storage_lock:
        if conversation not in conversations:
            return jsonify(error="会话不存在"), 404
        conversation["messages"].extend([
            {"role": "user", "content": message.strip()},
            {"role": "assistant", "content": reply},
        ])
        save_conversations()
        return jsonify(message=message.strip(), reply=reply)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5001")), threaded=True, debug=False)
