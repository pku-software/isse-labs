import json
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

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CONVERSATIONS_FILE = os.path.join(DATA_DIR, "conversations.json")


def load_conversations():
    if not os.path.exists(CONVERSATIONS_FILE):
        return [], 1, 1
    try:
        with open(CONVERSATIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return [], 1, 1
    if not isinstance(data, list):
        return [], 1, 1

    next_conversation_id = 1
    next_message_id = 1
    for conv in data:
        if isinstance(conv, dict) and isinstance(conv.get("id"), int):
            next_conversation_id = max(next_conversation_id, conv["id"] + 1)
        for msg in conv.get("messages", []):
            if isinstance(msg, dict) and isinstance(msg.get("id"), int):
                next_message_id = max(next_message_id, msg["id"] + 1)
    return data, next_conversation_id, next_message_id


def save_conversations():
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CONVERSATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(conversations, f, ensure_ascii=False, indent=2)


conversations, next_conversation_id, next_message_id = load_conversations()


def find_conversation(conversation_id):
    for conv in conversations:
        if conv["id"] == conversation_id:
            return conv
    return None


def call_deepseek(messages):
    resp = requests.post(
        f"{DEEPSEEK_BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": DEEPSEEK_MODEL,
            "messages": messages,
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


@app.route("/api/conversations", methods=["POST"])
def create_conversation():
    global next_conversation_id

    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip() or "新会话"

    conv = {"id": next_conversation_id, "title": title, "messages": []}
    next_conversation_id += 1
    conversations.append(conv)
    save_conversations()
    return jsonify(conv), 201


@app.route("/api/conversations", methods=["GET"])
def list_conversations():
    return jsonify([{"id": c["id"], "title": c["title"]} for c in conversations])


@app.route("/api/conversations/<int:conversation_id>", methods=["GET"])
def get_conversation(conversation_id):
    conv = find_conversation(conversation_id)
    if conv is None:
        return jsonify({"error": "会话不存在"}), 404
    return jsonify(conv)


@app.route("/api/conversations/<int:conversation_id>", methods=["PATCH"])
def update_conversation(conversation_id):
    conv = find_conversation(conversation_id)
    if conv is None:
        return jsonify({"error": "会话不存在"}), 404

    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    if not title:
        return jsonify({"error": "title 不能为空"}), 400

    conv["title"] = title
    save_conversations()
    return jsonify(conv)


@app.route("/api/conversations/<int:conversation_id>", methods=["DELETE"])
def delete_conversation(conversation_id):
    for index, conv in enumerate(conversations):
        if conv["id"] == conversation_id:
            conversations.pop(index)
            save_conversations()
            return jsonify({"deleted": conversation_id})

    return jsonify({"error": "会话不存在"}), 404


@app.route("/api/conversations/<int:conversation_id>/messages", methods=["POST"])
def create_message(conversation_id):
    global next_message_id

    conv = find_conversation(conversation_id)
    if conv is None:
        return jsonify({"error": "会话不存在"}), 404

    if not DEEPSEEK_API_KEY:
        return jsonify({"error": "缺少 DEEPSEEK_API_KEY，请检查 .env 配置"}), 500

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "message" not in data:
        return jsonify({"error": "缺少 message 字段"}), 400

    message = str(data["message"]).strip()
    if not message:
        return jsonify({"error": "message 不能为空"}), 400

    user_msg = {"id": next_message_id, "role": "user", "content": message}
    next_message_id += 1
    conv["messages"].append(user_msg)

    try:
        history = [{"role": m["role"], "content": m["content"]} for m in conv["messages"]]
        reply = call_deepseek(history)
    except Exception as exc:
        conv["messages"].pop()
        save_conversations()
        return jsonify({"error": f"调用 DeepSeek 失败：{exc}"}), 502

    assistant_msg = {"id": next_message_id, "role": "assistant", "content": reply}
    next_message_id += 1
    conv["messages"].append(assistant_msg)
    save_conversations()

    return jsonify(assistant_msg), 201


@app.route("/api/conversations/<int:conversation_id>/messages/<int:message_id>", methods=["PATCH"])
def update_message(conversation_id, message_id):
    global next_message_id

    conv = find_conversation(conversation_id)
    if conv is None:
        return jsonify({"error": "会话不存在"}), 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "content" not in data:
        return jsonify({"error": "缺少 content 字段"}), 400

    content = str(data["content"]).strip()
    if not content:
        return jsonify({"error": "content 不能为空"}), 400

    target_index = None
    for index, msg in enumerate(conv["messages"]):
        if msg["id"] == message_id:
            target_index = index
            break

    if target_index is None:
        return jsonify({"error": "消息不存在"}), 404

    conv["messages"][target_index]["content"] = content

    if conv["messages"][target_index]["role"] != "user":
        save_conversations()
        return jsonify(conv["messages"][target_index])

    del conv["messages"][target_index + 1:]

    if not DEEPSEEK_API_KEY:
        save_conversations()
        return jsonify({"error": "缺少 DEEPSEEK_API_KEY，请检查 .env 配置"}), 500

    try:
        history = [{"role": m["role"], "content": m["content"]} for m in conv["messages"]]
        reply = call_deepseek(history)
    except Exception as exc:
        save_conversations()
        return jsonify({"error": f"调用 DeepSeek 失败：{exc}"}), 502

    assistant_msg = {"id": next_message_id, "role": "assistant", "content": reply}
    next_message_id += 1
    conv["messages"].append(assistant_msg)
    save_conversations()

    return jsonify(assistant_msg), 200


@app.route("/api/conversations/<int:conversation_id>/messages/<int:message_id>", methods=["DELETE"])
def delete_message(conversation_id, message_id):
    conv = find_conversation(conversation_id)
    if conv is None:
        return jsonify({"error": "会话不存在"}), 404

    for index, msg in enumerate(conv["messages"]):
        if msg["id"] == message_id:
            removed = conv["messages"].pop(index)
            if removed["role"] == "user" and index < len(conv["messages"]) and conv["messages"][index]["role"] == "assistant":
                conv["messages"].pop(index)
            save_conversations()
            return jsonify({"deleted": message_id})

    return jsonify({"error": "消息不存在"}), 404


if __name__ == "__main__":
    app.run(port=5001, debug=True)
