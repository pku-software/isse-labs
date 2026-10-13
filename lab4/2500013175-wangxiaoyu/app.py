import json
import math
import os
import threading
import time
from functools import wraps
from pathlib import Path

from flask import Flask, Response, jsonify, request, send_from_directory
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from metrics import REGISTRY, track_chat


app = Flask(__name__, static_folder="frontend", static_url_path="")
app.json.ensure_ascii = False
MODEL_MODE = os.getenv("MODEL_MODE", "mock").lower()
if MODEL_MODE not in ("mock", "real"):
    raise ValueError("MODEL_MODE must be mock or real")
store_lock = threading.RLock()

messages = []
next_message_id = 1
data_file = Path(__file__).parent / ".runtime" / "app" / "conversations.json"


def locked(view):
    """Serialize short CRUD operations, never hold this lock during a model call."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        with store_lock:
            return view(*args, **kwargs)
    return wrapped


class MockFailure(Exception):
    pass


def load_conversations():
    if not data_file.exists() or data_file.stat().st_size == 0:
        return []

    try:
        with data_file.open("r", encoding="utf-8") as file:
            loaded = json.load(file)
        if isinstance(loaded, list):
            return loaded
    except (OSError, json.JSONDecodeError):
        app.logger.exception("Failed to load conversation data")
    return []


def save_conversations():
    data_file.parent.mkdir(parents=True, exist_ok=True)
    temporary_file = data_file.with_suffix(".tmp")
    with temporary_file.open("w", encoding="utf-8") as file:
        json.dump(conversations, file, ensure_ascii=False, indent=2)
    temporary_file.replace(data_file)


conversations = load_conversations()
next_conversation_id = (
    max((conversation["id"] for conversation in conversations), default=0) + 1
)
next_conversation_message_id = (
    max(
        (
            message["id"]
            for conversation in conversations
            for message in conversation.get("messages", [])
        ),
        default=0,
    )
    + 1
)


def generate_reply(api_messages, mock_options=None):
    if MODEL_MODE == "mock":
        options = {} if mock_options is None else mock_options
        if not isinstance(options, dict):
            raise ValueError("mock 必须是 JSON 对象")
        delay = options.get("delay_seconds", 0.1)
        force_error = options.get("force_error", False)
        if (isinstance(delay, bool) or not isinstance(delay, (int, float))
                or not math.isfinite(delay) or not 0 <= delay <= 30):
            raise ValueError("mock.delay_seconds 必须是 0～30 秒的有限数字")
        if not isinstance(force_error, bool):
            raise ValueError("mock.force_error 必须是布尔值")
        time.sleep(delay)
        if force_error:
            raise MockFailure()
        return "这是本地 mock 测试回复，未调用外部模型。"

    # Real mode uses only the process environment; never loads a .env file.
    from openai import OpenAI

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("missing_api_key")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
        timeout=60.0,
    )
    completion = client.chat.completions.create(
        model="deepseek-flash",
        messages=api_messages,
        stream=False,
    )
    reply = completion.choices[0].message.content
    if not reply:
        raise ValueError("DeepSeek returned an empty reply")
    return reply


def find_conversation(conversation_id):
    return next(
        (item for item in conversations if item["id"] == conversation_id),
        None,
    )


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.get("/api/lab/status")
def lab_status():
    if MODEL_MODE != "mock":
        return jsonify({"error": "实验状态接口仅在 mock 模式可用"}), 404
    return jsonify({"mode": MODEL_MODE, "external_model_calls": False})


@app.get("/metrics")
def metrics():
    return Response(generate_latest(REGISTRY), content_type=CONTENT_TYPE_LATEST)


@app.post("/api/messages")
@track_chat
def create_message():
    global next_message_id

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "请提供 JSON 格式的请求数据"}), 400

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "message 不能为空"}), 400

    if MODEL_MODE == "real" and not os.getenv("DEEPSEEK_API_KEY"):
        return jsonify({"error": "服务器未配置 DeepSeek API Key"}), 500

    try:
        reply = generate_reply(
            [{"role": "user", "content": message.strip()}], data.get("mock")
        )
    except MockFailure:
        return jsonify({"error": "模拟模型失败", "code": "mock_failure"}), 503
    except ValueError as error:
        if MODEL_MODE == "mock":
            return jsonify({"error": str(error)}), 400
        app.logger.exception("Model response invalid")
        return jsonify({"error": "DeepSeek API 调用失败，请稍后重试"}), 502
    except Exception:
        app.logger.exception("DeepSeek API request failed")
        return jsonify({"error": "DeepSeek API 调用失败，请稍后重试"}), 502

    with store_lock:
        record = {
            "id": next_message_id,
            "message": message.strip(),
            "reply": reply,
        }
        messages.append(record)
        next_message_id += 1
        return jsonify(record), 201


@app.get("/api/messages")
@locked
def list_messages():
    return jsonify(messages)


@app.patch("/api/messages/<int:message_id>")
@locked
def update_message(message_id):
    record = next((item for item in messages if item["id"] == message_id), None)
    if record is None:
        return jsonify({"error": "聊天记录不存在"}), 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "请提供 JSON 格式的请求数据"}), 400

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "message 不能为空"}), 400

    record["message"] = message.strip()
    return jsonify(record)


@app.delete("/api/messages/<int:message_id>")
@locked
def delete_message(message_id):
    record = next((item for item in messages if item["id"] == message_id), None)
    if record is None:
        return jsonify({"error": "聊天记录不存在"}), 404

    messages.remove(record)
    return jsonify({"message": "聊天记录已删除"})


@app.post("/api/conversations")
@locked
def create_conversation():
    global next_conversation_id

    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify({"error": "请提供 JSON 格式的请求数据"}), 400

    title = data.get("title", "新对话")
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "title 不能为空"}), 400

    conversation = {
        "id": next_conversation_id,
        "title": title.strip(),
        "messages": [],
    }
    conversations.append(conversation)
    next_conversation_id += 1
    save_conversations()
    return jsonify(conversation), 201


@app.get("/api/conversations")
@locked
def list_conversations():
    summaries = [
        {
            "id": conversation["id"],
            "title": conversation["title"],
            "message_count": len(conversation["messages"]),
        }
        for conversation in conversations
    ]
    return jsonify(summaries)


@app.get("/api/conversations/<int:conversation_id>")
@locked
def get_conversation(conversation_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "会话不存在"}), 404
    return jsonify(conversation)


@app.patch("/api/conversations/<int:conversation_id>")
@locked
def update_conversation(conversation_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "会话不存在"}), 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "请提供 JSON 格式的请求数据"}), 400

    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "title 不能为空"}), 400

    conversation["title"] = title.strip()
    save_conversations()
    return jsonify(conversation)


@app.delete("/api/conversations/<int:conversation_id>")
@locked
def delete_conversation(conversation_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "会话不存在"}), 404

    conversations.remove(conversation)
    save_conversations()
    return jsonify({"message": "会话已删除"})


@app.post("/api/conversations/<int:conversation_id>/messages")
@track_chat
def create_conversation_message(conversation_id):
    global next_conversation_message_id

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "请提供 JSON 格式的请求数据"}), 400

    content = data.get("message")
    if not isinstance(content, str) or not content.strip():
        return jsonify({"error": "message 不能为空"}), 400

    user_content = content.strip()
    with store_lock:
        conversation = find_conversation(conversation_id)
        if conversation is None:
            return jsonify({"error": "会话不存在"}), 404
        api_messages = [
            {"role": item["role"], "content": item["content"]}
            for item in conversation["messages"]
        ]
    api_messages.append({"role": "user", "content": user_content})

    if MODEL_MODE == "real" and not os.getenv("DEEPSEEK_API_KEY"):
        return jsonify({"error": "服务器未配置 DeepSeek API Key"}), 500

    try:
        reply = generate_reply(api_messages, data.get("mock"))
    except MockFailure:
        return jsonify({"error": "模拟模型失败", "code": "mock_failure"}), 503
    except ValueError as error:
        if MODEL_MODE == "mock":
            return jsonify({"error": str(error)}), 400
        app.logger.exception("Model response invalid")
        return jsonify({"error": "DeepSeek API 调用失败，请稍后重试"}), 502
    except Exception:
        app.logger.exception("DeepSeek conversation request failed")
        return jsonify({"error": "DeepSeek API 调用失败，请稍后重试"}), 502

    with store_lock:
        # The conversation may have been deleted while waiting for the reply.
        conversation = find_conversation(conversation_id)
        if conversation is None:
            return jsonify({"error": "会话已删除"}), 404
        user_message = {
            "id": next_conversation_message_id,
            "role": "user",
            "content": user_content,
        }
        next_conversation_message_id += 1
        assistant_message = {
            "id": next_conversation_message_id,
            "role": "assistant",
            "content": reply,
        }
        next_conversation_message_id += 1
        conversation["messages"].extend([user_message, assistant_message])
        save_conversations()
        return jsonify({
            "user_message": user_message,
            "assistant_message": assistant_message,
        }), 201


@app.patch(
    "/api/conversations/<int:conversation_id>/messages/<int:message_id>"
)
@locked
def update_conversation_message(conversation_id, message_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "会话不存在"}), 404

    item = next(
        (message for message in conversation["messages"] if message["id"] == message_id),
        None,
    )
    if item is None:
        return jsonify({"error": "消息不存在"}), 404
    if item["role"] != "user":
        return jsonify({"error": "只能修改用户消息"}), 400

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "请提供 JSON 格式的请求数据"}), 400

    content = data.get("message")
    if not isinstance(content, str) or not content.strip():
        return jsonify({"error": "message 不能为空"}), 400

    item["content"] = content.strip()
    save_conversations()
    return jsonify(item)


@app.delete(
    "/api/conversations/<int:conversation_id>/messages/<int:message_id>"
)
@locked
def delete_conversation_message(conversation_id, message_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "会话不存在"}), 404

    message_index = next(
        (
            index
            for index, item in enumerate(conversation["messages"])
            if item["id"] == message_id
        ),
        None,
    )
    if message_index is None:
        return jsonify({"error": "消息不存在"}), 404

    item = conversation["messages"][message_index]
    if item["role"] != "user":
        return jsonify({"error": "只能删除完整问答"}), 400

    delete_count = 1
    if (
        message_index + 1 < len(conversation["messages"])
        and conversation["messages"][message_index + 1]["role"] == "assistant"
    ):
        delete_count = 2
    del conversation["messages"][message_index : message_index + delete_count]
    save_conversations()
    return jsonify({"message": "问答已删除"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("APP_PORT", "5001")),
            debug=False, threaded=True, use_reloader=False)
