import json
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from openai import OpenAI, OpenAIError


load_dotenv()


app = Flask(__name__, static_folder="frontend", static_url_path="")
app.json.ensure_ascii = False

DATA_FILE = Path(__file__).resolve().parent / "data" / "conversations.json"


def load_conversations():
    if not DATA_FILE.exists() or not DATA_FILE.read_text(encoding="utf-8").strip():
        return []

    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        app.logger.warning("Conversation data file contains invalid JSON; using empty data")
        return []

    if not isinstance(data, list):
        app.logger.warning("Conversation data must be a JSON array; using empty data")
        return []
    return data


def save_conversations():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary_file = DATA_FILE.with_suffix(".json.tmp")
    temporary_file.write_text(
        json.dumps(conversations, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temporary_file.replace(DATA_FILE)


def calculate_next_ids(items):
    conversation_ids = [item.get("id", 0) for item in items if isinstance(item, dict)]
    message_ids = [
        message.get("id", 0)
        for conversation in items
        if isinstance(conversation, dict)
        for message in conversation.get("messages", [])
        if isinstance(message, dict)
    ]
    return max(conversation_ids, default=0) + 1, max(message_ids, default=0) + 1


conversations = load_conversations()
next_conversation_id, next_message_id = calculate_next_ids(conversations)


def find_conversation(conversation_id: int):
    return next(
        (conversation for conversation in conversations if conversation["id"] == conversation_id),
        None,
    )


def find_message(conversation, message_id: int):
    return next(
        (message for message in conversation["messages"] if message["id"] == message_id),
        None,
    )


def conversation_summary(conversation):
    return {
        "id": conversation["id"],
        "title": conversation["title"],
        "message_count": len(conversation["messages"]),
    }


def get_json_object():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, (jsonify(error="请求体必须是 JSON 对象"), 400)
    return data, None


def get_deepseek_reply(history):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("服务器尚未配置 DeepSeek API Key")

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    completion = client.chat.completions.create(
        model="deepseek-flash",
        messages=[
            {"role": message["role"], "content": message["content"]}
            for message in history
        ],
        stream=False,
    )
    reply = completion.choices[0].message.content
    if not reply:
        raise ValueError("DeepSeek API 未返回有效回复")
    return reply


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/hello")
def hello():
    return jsonify(message="你好")


@app.post("/api/conversations")
def create_conversation():
    global next_conversation_id

    data, error = get_json_object()
    if error:
        return error

    title = data.get("title", "")
    if title is not None and not isinstance(title, str):
        return jsonify(error="title 必须是字符串"), 400

    title = title.strip() if title else f"新会话 {next_conversation_id}"
    conversation = {
        "id": next_conversation_id,
        "title": title,
        "messages": [],
    }
    conversations.append(conversation)
    next_conversation_id += 1
    save_conversations()
    return jsonify(conversation), 201


@app.get("/api/conversations")
def list_conversations():
    return jsonify([conversation_summary(item) for item in conversations])


@app.get("/api/conversations/<int:conversation_id>")
def get_conversation(conversation_id: int):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify(error="会话不存在"), 404
    return jsonify(conversation)


@app.patch("/api/conversations/<int:conversation_id>")
def update_conversation(conversation_id: int):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify(error="会话不存在"), 404

    data, error = get_json_object()
    if error:
        return error

    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        return jsonify(error="title 必须是非空字符串"), 400

    conversation["title"] = title.strip()
    save_conversations()
    return jsonify(conversation_summary(conversation))


@app.delete("/api/conversations/<int:conversation_id>")
def delete_conversation(conversation_id: int):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify(error="会话不存在"), 404

    conversations.remove(conversation)
    save_conversations()
    return "", 204


@app.post("/api/conversations/<int:conversation_id>/messages")
def create_conversation_message(conversation_id: int):
    global next_message_id

    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify(error="会话不存在"), 404

    data, error = get_json_object()
    if error:
        return error

    message_text = data.get("message")
    if not isinstance(message_text, str) or not message_text.strip():
        return jsonify(error="message 必须是非空字符串"), 400

    user_message = {
        "id": next_message_id,
        "turn_id": next_message_id,
        "role": "user",
        "content": message_text.strip(),
    }

    try:
        reply = get_deepseek_reply([*conversation["messages"], user_message])
    except RuntimeError as error:
        return jsonify(error=str(error)), 500
    except (OpenAIError, IndexError, AttributeError, ValueError) as error:
        app.logger.error("DeepSeek API request failed: %s", type(error).__name__)
        return jsonify(error="调用 DeepSeek API 失败，请稍后重试"), 502

    next_message_id += 1
    assistant_message = {
        "id": next_message_id,
        "turn_id": user_message["turn_id"],
        "role": "assistant",
        "content": reply,
    }
    next_message_id += 1

    conversation["messages"].extend([user_message, assistant_message])
    save_conversations()
    return jsonify(
        {"user_message": user_message, "assistant_message": assistant_message}
    ), 201


@app.patch("/api/conversations/<int:conversation_id>/messages/<int:message_id>")
def update_conversation_message(conversation_id: int, message_id: int):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify(error="会话不存在"), 404

    message = find_message(conversation, message_id)
    if message is None:
        return jsonify(error="消息不存在"), 404
    if message["role"] != "user":
        return jsonify(error="只支持修改用户消息"), 400

    data, error = get_json_object()
    if error:
        return error

    content = data.get("message")
    if not isinstance(content, str) or not content.strip():
        return jsonify(error="message 必须是非空字符串"), 400

    message["content"] = content.strip()
    save_conversations()
    return jsonify(message)


@app.delete("/api/conversations/<int:conversation_id>/messages/<int:message_id>")
def delete_conversation_message(conversation_id: int, message_id: int):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify(error="会话不存在"), 404

    message = find_message(conversation, message_id)
    if message is None:
        return jsonify(error="消息不存在"), 404

    turn_id = message["turn_id"]
    conversation["messages"] = [
        item for item in conversation["messages"] if item["turn_id"] != turn_id
    ]
    save_conversations()
    return "", 204


if __name__ == "__main__":
    app.run(port=5001, debug=True)
