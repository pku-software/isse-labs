import json
import os
from datetime import datetime, timezone
from pathlib import Path
import urllib.error
import urllib.request

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory


FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"
ENV_FILE = Path(__file__).resolve().parent / ".env"
DATA_DIR = Path(__file__).resolve().parent / "data"
CONVERSATIONS_FILE = DATA_DIR / "conversations.json"

load_dotenv(ENV_FILE)

app = Flask(__name__)
app.json.ensure_ascii = False


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_conversations():
    if not CONVERSATIONS_FILE.exists():
        return []

    try:
        payload = json.loads(CONVERSATIONS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        app.logger.error("Could not load conversations: %s", type(error).__name__)
        return []

    if not isinstance(payload, list):
        app.logger.error("conversations.json must contain a JSON array")
        return []

    records = []
    for conversation in payload:
        if not isinstance(conversation, dict):
            continue

        conversation_id = conversation.get("id")
        title = conversation.get("title")
        created_at = conversation.get("createdAt")
        updated_at = conversation.get("updatedAt")
        raw_messages = conversation.get("messages")

        if (
            not isinstance(conversation_id, int)
            or not isinstance(title, str)
            or not isinstance(created_at, str)
            or not isinstance(updated_at, str)
            or not isinstance(raw_messages, list)
        ):
            continue

        records.append(
            {
                "id": conversation_id,
                "title": title,
                "createdAt": created_at,
                "updatedAt": updated_at,
                "messages": [
                    message
                    for message in raw_messages
                    if isinstance(message, dict)
                    and isinstance(message.get("id"), int)
                    and isinstance(message.get("message"), str)
                    and isinstance(message.get("reply"), str)
                    and isinstance(message.get("createdAt"), str)
                ],
            }
        )

    return records


def save_conversations():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temporary_file = CONVERSATIONS_FILE.with_suffix(".json.tmp")
    temporary_file.write_text(
        json.dumps(conversations, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary_file.replace(CONVERSATIONS_FILE)


def find_conversation(conversation_id):
    return next(
        (
            conversation
            for conversation in conversations
            if conversation["id"] == conversation_id
        ),
        None,
    )


def find_message(conversation, message_id):
    return next(
        (
            message
            for message in conversation["messages"]
            if message["id"] == message_id
        ),
        None,
    )


def parse_message_payload():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, "请求体必须是 JSON 对象"

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return None, "message 不能为空"

    return message.strip(), None


def parse_title_payload():
    data = request.get_json(silent=True)
    if data is None:
        return None, None
    if not isinstance(data, dict):
        return None, "请求体必须是 JSON 对象"

    title = data.get("title")
    if title is None:
        return None, None
    if not isinstance(title, str) or not title.strip():
        return None, "title 不能为空"
    if len(title.strip()) > 80:
        return None, "title 不能超过 80 个字符"

    return title.strip(), None


def conversation_summary(conversation):
    last_message = conversation["messages"][-1]["message"] if conversation["messages"] else None
    return {
        "id": conversation["id"],
        "title": conversation["title"],
        "messageCount": len(conversation["messages"]),
        "lastMessage": last_message,
        "createdAt": conversation["createdAt"],
        "updatedAt": conversation["updatedAt"],
    }


def generate_reply(message, history):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return None, ("DEEPSEEK_API_KEY 未配置", 503)

    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-flash")

    model_messages = []
    for previous_message in history[-10:]:
        model_messages.append(
            {"role": "user", "content": previous_message["message"]}
        )
        model_messages.append(
            {"role": "assistant", "content": previous_message["reply"]}
        )
    model_messages.append({"role": "user", "content": message})

    payload = {
        "model": model,
        "messages": model_messages,
        "stream": False,
        "thinking": {"type": "disabled"},
    }
    api_request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(api_request, timeout=60) as response:
            response_data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        app.logger.error("DeepSeek HTTP error: %s", error.code)
        return None, ("DeepSeek 服务暂时不可用，请稍后重试", 502)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        app.logger.error("DeepSeek request failed: %s", type(error).__name__)
        return None, ("DeepSeek 服务暂时不可用，请稍后重试", 502)

    choices = response_data.get("choices")
    if not isinstance(choices, list) or not choices:
        return None, ("DeepSeek 没有返回可用回复", 502)

    reply = choices[0].get("message", {}).get("content")
    if not isinstance(reply, str) or not reply.strip():
        return None, ("DeepSeek 没有返回可用回复", 502)

    return reply.strip(), None


conversations = load_conversations()
next_conversation_id = max(
    (conversation["id"] for conversation in conversations),
    default=0,
) + 1
next_message_id = max(
    (
        message["id"]
        for conversation in conversations
        for message in conversation["messages"]
    ),
    default=0,
) + 1


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/style.css")
def stylesheet():
    return send_from_directory(FRONTEND_DIR, "style.css")


@app.get("/app.js")
def javascript():
    return send_from_directory(FRONTEND_DIR, "app.js")


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.get("/api/conversations")
def list_conversations():
    summaries = [conversation_summary(item) for item in conversations]
    summaries.sort(key=lambda item: item["updatedAt"], reverse=True)
    return jsonify(summaries)


@app.post("/api/conversations")
def create_conversation():
    global next_conversation_id

    title, error = parse_title_payload()
    if error:
        return jsonify({"error": error}), 400

    now = utc_now()
    conversation = {
        "id": next_conversation_id,
        "title": title or f"新会话 {next_conversation_id}",
        "createdAt": now,
        "updatedAt": now,
        "messages": [],
    }
    next_conversation_id += 1
    conversations.append(conversation)

    try:
        save_conversations()
    except OSError as error:
        conversations.remove(conversation)
        next_conversation_id -= 1
        app.logger.error(
            "Could not save created conversation: %s",
            type(error).__name__,
        )
        return jsonify({"error": "会话保存失败"}), 500

    return jsonify(conversation), 201


@app.get("/api/conversations/<int:conversation_id>")
def get_conversation(conversation_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "会话不存在"}), 404

    return jsonify(conversation)


@app.patch("/api/conversations/<int:conversation_id>")
def rename_conversation(conversation_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "会话不存在"}), 404

    title, error = parse_title_payload()
    if error:
        return jsonify({"error": error}), 400
    if title is None:
        return jsonify({"error": "title 不能为空"}), 400

    previous_title = conversation["title"]
    previous_updated_at = conversation["updatedAt"]
    conversation["title"] = title
    conversation["updatedAt"] = utc_now()

    try:
        save_conversations()
    except OSError as error:
        conversation["title"] = previous_title
        conversation["updatedAt"] = previous_updated_at
        app.logger.error(
            "Could not save renamed conversation: %s",
            type(error).__name__,
        )
        return jsonify({"error": "会话保存失败"}), 500

    return jsonify(conversation_summary(conversation))


@app.delete("/api/conversations/<int:conversation_id>")
def delete_conversation(conversation_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "会话不存在"}), 404

    conversation_index = conversations.index(conversation)
    conversations.remove(conversation)

    try:
        save_conversations()
    except OSError as error:
        conversations.insert(conversation_index, conversation)
        app.logger.error(
            "Could not save deleted conversation: %s",
            type(error).__name__,
        )
        return jsonify({"error": "会话保存失败"}), 500

    return jsonify({"deleted": conversation_id})


@app.post("/api/conversations/<int:conversation_id>/messages")
def create_message(conversation_id):
    global next_message_id

    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "会话不存在"}), 404

    message, error = parse_message_payload()
    if error:
        return jsonify({"error": error}), 400

    reply, api_error = generate_reply(message, conversation["messages"])
    if api_error:
        detail, status_code = api_error
        return jsonify({"error": detail}), status_code

    record = {
        "id": next_message_id,
        "message": message,
        "reply": reply,
        "createdAt": utc_now(),
    }
    previous_updated_at = conversation["updatedAt"]
    next_message_id += 1
    conversation["messages"].append(record)
    conversation["updatedAt"] = record["createdAt"]

    try:
        save_conversations()
    except OSError as error:
        conversation["messages"].remove(record)
        conversation["updatedAt"] = previous_updated_at
        next_message_id -= 1
        app.logger.error("Could not save created message: %s", type(error).__name__)
        return jsonify({"error": "聊天记录保存失败"}), 500

    return jsonify(record), 201


@app.patch("/api/conversations/<int:conversation_id>/messages/<int:message_id>")
def update_message(conversation_id, message_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "会话不存在"}), 404

    record = find_message(conversation, message_id)
    if record is None:
        return jsonify({"error": "聊天记录不存在"}), 404

    message, error = parse_message_payload()
    if error:
        return jsonify({"error": error}), 400

    previous_message = record["message"]
    previous_updated_at = conversation["updatedAt"]
    record["message"] = message
    conversation["updatedAt"] = utc_now()

    try:
        save_conversations()
    except OSError as error:
        record["message"] = previous_message
        conversation["updatedAt"] = previous_updated_at
        app.logger.error("Could not save updated message: %s", type(error).__name__)
        return jsonify({"error": "聊天记录保存失败"}), 500

    return jsonify(record)


@app.delete("/api/conversations/<int:conversation_id>/messages/<int:message_id>")
def delete_message(conversation_id, message_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "会话不存在"}), 404

    record = find_message(conversation, message_id)
    if record is None:
        return jsonify({"error": "聊天记录不存在"}), 404

    record_index = conversation["messages"].index(record)
    previous_updated_at = conversation["updatedAt"]
    conversation["messages"].remove(record)
    conversation["updatedAt"] = utc_now()

    try:
        save_conversations()
    except OSError as error:
        conversation["messages"].insert(record_index, record)
        conversation["updatedAt"] = previous_updated_at
        app.logger.error("Could not save deleted message: %s", type(error).__name__)
        return jsonify({"error": "聊天记录保存失败"}), 500

    return jsonify({"deleted": message_id})


if __name__ == "__main__":
    app.run(port=5001, debug=True)
