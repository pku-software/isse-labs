import json
import os

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

load_dotenv()

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"
OLD_DATA_FILE = os.path.join("data", "messages.json")
DATA_FILE = os.path.join("data", "conversations.json")

app = Flask(__name__)
app.json.ensure_ascii = False

conversations = []
next_conversation_id = 1


def load_data():
    global conversations, next_conversation_id
    if not os.path.exists(DATA_FILE):
        if os.path.exists(OLD_DATA_FILE):
            try:
                with open(OLD_DATA_FILE, "r", encoding="utf-8") as f:
                    old = json.load(f)
                migrated = []
                for record in old:
                    if "message" in record and "reply" in record:
                        migrated.append(
                            {"role": "user", "content": record["message"]}
                        )
                        migrated.append(
                            {"role": "assistant", "content": record["reply"]}
                        )
                conversations = (
                    [{"id": 1, "title": "导入的会话", "messages": migrated}]
                    if migrated
                    else []
                )
            except (json.JSONDecodeError, OSError):
                conversations = []
        else:
            conversations = []
        next_conversation_id = max((c["id"] for c in conversations), default=0) + 1
        save_data()
        return
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            conversations = json.load(f)
        if not isinstance(conversations, list):
            conversations = []
    except (json.JSONDecodeError, OSError):
        conversations = []
    next_conversation_id = max((c["id"] for c in conversations), default=0) + 1


def save_data():
    directory = os.path.dirname(DATA_FILE)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(conversations, f, ensure_ascii=False, indent=2)


def find_conversation(conversation_id):
    return next((c for c in conversations if c["id"] == conversation_id), None)


def next_message_id(conversation):
    return max((m["id"] for m in conversation["messages"]), default=0) + 1


def call_deepseek(history, content):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return None, "缺少 DEEPSEEK_API_KEY"
    payload_messages = [{"role": m["role"], "content": m["content"]} for m in history]
    payload_messages.append({"role": "user", "content": content})
    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={"model": DEEPSEEK_MODEL, "messages": payload_messages},
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"], None
    except requests.RequestException as exc:
        return None, f"调用 DeepSeek 失败: {exc}"
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        return None, f"解析 DeepSeek 响应失败: {exc}"


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


@app.route("/api/conversations", methods=["POST"])
def create_conversation():
    global next_conversation_id
    data = request.get_json(silent=True) or {}
    title = data.get("title", "新会话")
    if not isinstance(title, str) or not title.strip():
        title = "新会话"
    conversation = {
        "id": next_conversation_id,
        "title": title.strip(),
        "messages": [],
    }
    next_conversation_id += 1
    conversations.append(conversation)
    save_data()
    return jsonify(conversation), 201


@app.route("/api/conversations", methods=["GET"])
def list_conversations():
    return jsonify(conversations)


@app.route("/api/conversations/<int:conversation_id>", methods=["GET"])
def get_conversation(conversation_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "会话不存在"}), 404
    return jsonify(conversation)


@app.route("/api/conversations/<int:conversation_id>", methods=["PATCH"])
def update_conversation(conversation_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "会话不存在"}), 404
    data = request.get_json(silent=True)
    if not data or "title" not in data:
        return jsonify({"error": "缺少 title 字段"}), 400
    title = data["title"]
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "title 不能为空"}), 400
    conversation["title"] = title.strip()
    save_data()
    return jsonify(conversation)


@app.route("/api/conversations/<int:conversation_id>", methods=["DELETE"])
def delete_conversation(conversation_id):
    global conversations
    if find_conversation(conversation_id) is None:
        return jsonify({"error": "会话不存在"}), 404
    conversations = [c for c in conversations if c["id"] != conversation_id]
    save_data()
    return jsonify({"message": "删除成功"})


@app.route("/api/conversations/<int:conversation_id>/messages", methods=["POST"])
def create_message(conversation_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "会话不存在"}), 404
    data = request.get_json(silent=True)
    if not data or "message" not in data:
        return jsonify({"error": "缺少 message 字段"}), 400
    content = data["message"]
    if not isinstance(content, str) or not content.strip():
        return jsonify({"error": "message 不能为空"}), 400
    content = content.strip()

    reply, error = call_deepseek(conversation["messages"], content)
    if error:
        return jsonify({"error": error}), 502

    user_message = {
        "id": next_message_id(conversation),
        "role": "user",
        "content": content,
    }
    assistant_message = {
        "id": user_message["id"] + 1,
        "role": "assistant",
        "content": reply,
    }
    conversation["messages"].append(user_message)
    conversation["messages"].append(assistant_message)
    if conversation["title"] == "新会话":
        conversation["title"] = content[:20]
    save_data()
    return jsonify(conversation), 201


@app.route(
    "/api/conversations/<int:conversation_id>/messages/<int:message_id>",
    methods=["PATCH"],
)
def update_message(conversation_id, message_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "会话不存在"}), 404
    message = next(
        (m for m in conversation["messages"] if m["id"] == message_id), None
    )
    if message is None:
        return jsonify({"error": "消息不存在"}), 404
    data = request.get_json(silent=True)
    if not data or "content" not in data:
        return jsonify({"error": "缺少 content 字段"}), 400
    content = data["content"]
    if not isinstance(content, str) or not content.strip():
        return jsonify({"error": "content 不能为空"}), 400
    message["content"] = content.strip()
    save_data()
    return jsonify(message)


@app.route(
    "/api/conversations/<int:conversation_id>/messages/<int:message_id>",
    methods=["DELETE"],
)
def delete_message(conversation_id, message_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "会话不存在"}), 404
    if not any(m["id"] == message_id for m in conversation["messages"]):
        return jsonify({"error": "消息不存在"}), 404
    conversation["messages"] = [
        m for m in conversation["messages"] if m["id"] != message_id
    ]
    save_data()
    return jsonify({"message": "删除成功"})


if __name__ == "__main__":
    load_data()
    app.run(port=5001, debug=True)
