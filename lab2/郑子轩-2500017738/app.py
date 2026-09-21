import json
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from openai import OpenAI


load_dotenv()


app = Flask(__name__, static_folder="frontend", static_url_path="")
app.json.ensure_ascii = False

DATA_FILE = Path(__file__).resolve().parent / "data" / "conversations.json"


def load_conversations():
    if not DATA_FILE.exists():
        return []

    content = DATA_FILE.read_text(encoding="utf-8").strip()
    if not content:
        return []

    data = json.loads(content)
    if not isinstance(data, list):
        raise ValueError("conversations.json 的最外层必须是数组")
    return data


def save_conversations():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(
        json.dumps(conversations, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


conversations = load_conversations()
next_conversation_id = max(
    (item.get("id", 0) for item in conversations if isinstance(item, dict)),
    default=0,
) + 1
next_message_id = max(
    (
        message.get("id", 0)
        for conversation in conversations
        if isinstance(conversation, dict)
        for message in conversation.get("messages", [])
        if isinstance(message, dict)
    ),
    default=0,
) + 1


def find_conversation(conversation_id):
    return next(
        (item for item in conversations if item["id"] == conversation_id),
        None,
    )


def find_user_message(message_id):
    for conversation in conversations:
        for index, message in enumerate(conversation["messages"]):
            if message["id"] == message_id and message["role"] == "user":
                return conversation, index, message
    return None


def validate_message_text(data):
    if not isinstance(data, dict):
        return None, (jsonify({"error": "请提供 JSON 请求体"}), 400)

    message_text = data.get("message")
    if not isinstance(message_text, str) or not message_text.strip():
        return None, (jsonify({"error": "message 不能为空"}), 400)
    return message_text.strip(), None


def ask_deepseek(history, message_text):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("missing_api_key")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )
    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=[
            {"role": item["role"], "content": item["content"]}
            for item in history
            if item.get("role") in {"user", "assistant"}
            and isinstance(item.get("content"), str)
        ]
        + [{"role": "user", "content": message_text}],
        stream=False,
    )
    reply = response.choices[0].message.content
    if not reply:
        raise ValueError("DeepSeek returned an empty reply")
    return reply


def append_exchange(conversation, message_text):
    global next_message_id

    reply = ask_deepseek(conversation["messages"], message_text)
    user_message = {
        "id": next_message_id,
        "role": "user",
        "content": message_text,
    }
    assistant_message = {
        "id": next_message_id + 1,
        "role": "assistant",
        "content": reply,
    }
    next_message_id += 2
    conversation["messages"].extend([user_message, assistant_message])
    save_conversations()
    return user_message, assistant_message


def record_from_pair(conversation, user_index):
    user_message = conversation["messages"][user_index]
    reply = ""
    if user_index + 1 < len(conversation["messages"]):
        candidate = conversation["messages"][user_index + 1]
        if candidate["role"] == "assistant":
            reply = candidate["content"]
    return {
        "id": user_message["id"],
        "message": user_message["content"],
        "reply": reply,
    }


def deepseek_error_response(error):
    if isinstance(error, RuntimeError) and str(error) == "missing_api_key":
        return jsonify({"error": "服务器未配置 DeepSeek API Key"}), 500
    return jsonify({"error": "DeepSeek API 调用失败，请稍后重试"}), 502


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.post("/api/conversations")
def create_conversation():
    global next_conversation_id

    data = request.get_json(silent=True)
    if data is None:
        data = {}
    if not isinstance(data, dict):
        return jsonify({"error": "请提供 JSON 请求体"}), 400

    title = data.get("title", "")
    if not isinstance(title, str):
        return jsonify({"error": "title 必须是字符串"}), 400
    title = title.strip() or f"新对话 {next_conversation_id}"

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
    return jsonify(conversations)


@app.get("/api/conversations/<int:conversation_id>")
def get_conversation(conversation_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "会话不存在"}), 404
    return jsonify(conversation)


@app.patch("/api/conversations/<int:conversation_id>")
def update_conversation(conversation_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "会话不存在"}), 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "请提供 JSON 请求体"}), 400

    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "title 不能为空"}), 400

    conversation["title"] = title.strip()
    save_conversations()
    return jsonify(conversation)


@app.delete("/api/conversations/<int:conversation_id>")
def delete_conversation(conversation_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "会话不存在"}), 404

    conversations.remove(conversation)
    save_conversations()
    return jsonify({"message": "会话已删除"})


@app.post("/api/conversations/<int:conversation_id>/messages")
def create_conversation_message(conversation_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "会话不存在"}), 404

    message_text, error = validate_message_text(request.get_json(silent=True))
    if error:
        return error

    try:
        append_exchange(conversation, message_text)
    except Exception as exc:
        return deepseek_error_response(exc)
    return jsonify(conversation), 201


# These routes preserve the original single-list CRUD API. They operate on the
# same persisted conversation data used by the multi-conversation interface.
@app.post("/api/messages")
def create_message():
    global next_conversation_id

    message_text, error = validate_message_text(request.get_json(silent=True))
    if error:
        return error

    if conversations:
        conversation = conversations[0]
    else:
        conversation = {
            "id": next_conversation_id,
            "title": "默认会话",
            "messages": [],
        }
        conversations.append(conversation)
        next_conversation_id += 1

    try:
        user_message, assistant_message = append_exchange(conversation, message_text)
    except Exception as exc:
        return deepseek_error_response(exc)

    return jsonify(
        {
            "id": user_message["id"],
            "message": user_message["content"],
            "reply": assistant_message["content"],
        }
    ), 201


@app.get("/api/messages")
def list_messages():
    records = []
    for conversation in conversations:
        for index, message in enumerate(conversation["messages"]):
            if message["role"] == "user":
                records.append(record_from_pair(conversation, index))
    return jsonify(records)


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    result = find_user_message(message_id)
    if result is None:
        return jsonify({"error": "聊天记录不存在"}), 404

    message_text, error = validate_message_text(request.get_json(silent=True))
    if error:
        return error

    conversation, index, message = result
    message["content"] = message_text
    save_conversations()
    return jsonify(record_from_pair(conversation, index))


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    result = find_user_message(message_id)
    if result is None:
        return jsonify({"error": "聊天记录不存在"}), 404

    conversation, index, _ = result
    del conversation["messages"][index]
    if (
        index < len(conversation["messages"])
        and conversation["messages"][index]["role"] == "assistant"
    ):
        del conversation["messages"][index]
    save_conversations()
    return jsonify({"message": "删除成功"})


if __name__ == "__main__":
    app.run(port=5001, debug=True)
