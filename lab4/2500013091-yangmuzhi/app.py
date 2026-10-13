import json
import math
import os
import threading
import time
from functools import wraps
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from metrics import REGISTRY, track_chat


app = Flask(__name__, static_folder="frontend", static_url_path="")
app.config["MODEL_MODE"] = os.environ.get("LAB4_MODEL_MODE", "mock").lower()
if app.config["MODEL_MODE"] not in {"mock", "real"}:
    raise ValueError("LAB4_MODEL_MODE must be mock or real")
if hasattr(app, "json"):
    app.json.ensure_ascii = False
else:
    # Flask 2.x 使用配置项控制 JSON 中的中文转义。
    app.config["JSON_AS_ASCII"] = False

messages = []
next_message_id = 1
data_path = Path(__file__).parent / ".runtime" / "app" / "conversations.json"
store_lock = threading.RLock()


def with_store_lock(view):
    """Protect short CRUD operations, including JSON serialization and file writes."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        with store_lock:
            return view(*args, **kwargs)
    return wrapped


def load_conversations():
    if not data_path.exists() or data_path.stat().st_size == 0:
        return []

    try:
        with data_path.open("r", encoding="utf-8") as data_file:
            data = json.load(data_file)
    except (OSError, json.JSONDecodeError):
        app.logger.warning("无法读取 conversations.json，将使用空数据")
        return []

    stored_conversations = data.get("conversations") if isinstance(data, dict) else None
    if not isinstance(stored_conversations, list):
        app.logger.warning("conversations.json 数据结构无效，将使用空数据")
        return []

    return stored_conversations


def save_conversations():
    data_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = data_path.with_suffix(".tmp")
    with temporary_path.open("w", encoding="utf-8") as data_file:
        json.dump(
            {"conversations": conversations},
            data_file,
            ensure_ascii=False,
            indent=2,
        )
        data_file.write("\n")
    temporary_path.replace(data_path)


conversations = load_conversations()
stored_messages = [
    message
    for conversation in conversations
    for message in conversation.get("messages", [])
]
next_conversation_id = max(
    (item.get("id", 0) for item in conversations if isinstance(item, dict)),
    default=0,
) + 1
next_conversation_message_id = max(
    (item.get("id", 0) for item in stored_messages if isinstance(item, dict)),
    default=0,
) + 1
next_turn_id = max(
    (item.get("turn_id", 0) for item in stored_messages if isinstance(item, dict)),
    default=0,
) + 1


def find_message(message_id):
    return next((item for item in messages if item["id"] == message_id), None)


def find_conversation(conversation_id):
    return next(
        (item for item in conversations if item["id"] == conversation_id),
        None,
    )


def read_message_text():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, "请求体必须是 JSON 对象"

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return None, "message 必须是非空字符串"

    return message.strip(), None


def generate_reply(api_messages):
    if app.config["MODEL_MODE"] == "mock":
        options = request.get_json(silent=True).get("mock", {})
        if not isinstance(options, dict):
            return None, ("mock 必须是 JSON 对象", 400)
        delay = options.get("delay_seconds", 0.1)
        force_error = options.get("force_error", False)
        if (isinstance(delay, bool) or not isinstance(delay, (int, float))
                or not 0 <= delay <= 30 or not math.isfinite(delay)):
            return None, ("mock.delay_seconds 必须是 0 到 30 之间的有限数值", 400)
        if not isinstance(force_error, bool):
            return None, ("mock.force_error 必须是布尔值", 400)
        time.sleep(delay)
        if force_error:
            return None, ("本地 mock 模拟失败", 503)
        return "这是本地 mock 测试回复，未调用外部模型。", None

    # Only real mode imports the SDK and reads the process environment variable.
    # No .env file is loaded, and mock options never enter the real call.
    import httpx
    from openai import (
        APIConnectionError, APIStatusError, AuthenticationError, OpenAI, RateLimitError,
    )

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return None, ("服务器未配置 DeepSeek API Key", 500)

    try:
        with OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
            http_client=httpx.Client(trust_env=False),
        ) as client:
            response = client.chat.completions.create(
                model="deepseek-flash",
                messages=api_messages,
                stream=False,
            )
        reply = response.choices[0].message.content
    except AuthenticationError:
        app.logger.error("DeepSeek API 鉴权失败")
        return None, ("DeepSeek API 鉴权失败，请检查服务器端 Key 配置", 502)
    except RateLimitError:
        app.logger.error("DeepSeek API 请求受限")
        return None, ("DeepSeek API 请求过于频繁，请稍后重试", 502)
    except APIConnectionError:
        app.logger.error("无法连接 DeepSeek API")
        return None, ("无法连接 DeepSeek API，请检查网络后重试", 502)
    except APIStatusError as error:
        app.logger.error("DeepSeek API 返回 HTTP %s", error.status_code)
        if error.status_code == 402:
            return None, ("DeepSeek API 账户余额不足", 502)
        return None, (f"DeepSeek API 返回 HTTP {error.status_code}", 502)
    except (IndexError, AttributeError):
        app.logger.error("DeepSeek API 响应格式异常")
        return None, ("DeepSeek API 响应格式异常", 502)

    if not isinstance(reply, str) or not reply.strip():
        return None, ("DeepSeek API 未返回有效回复", 502)

    return reply.strip(), None


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.get("/api/lab/status")
def lab_status():
    if app.config["MODEL_MODE"] != "mock":
        return jsonify({"error": "实验状态接口仅在 mock 模式开放"}), 404
    return jsonify({"mode": app.config["MODEL_MODE"], "external_model_calls": False})


@app.get("/metrics")
def metrics():
    return app.response_class(generate_latest(REGISTRY), content_type=CONTENT_TYPE_LATEST)


@app.post("/api/messages")
@track_chat
def create_message():
    global next_message_id

    message, error = read_message_text()
    if error:
        return jsonify({"error": error}), 400

    reply, deepseek_error = generate_reply(
        [{"role": "user", "content": message}]
    )
    if deepseek_error:
        error_message, status_code = deepseek_error
        return jsonify({"error": error_message}), status_code

    with store_lock:
        record = {
            "id": next_message_id,
            "message": message,
            "reply": reply,
        }
        messages.append(record)
        next_message_id += 1
        return jsonify(record), 201


@app.get("/api/messages")
@with_store_lock
def list_messages():
    return jsonify(messages)


@app.patch("/api/messages/<int:message_id>")
@with_store_lock
def update_message(message_id):
    record = find_message(message_id)
    if record is None:
        return jsonify({"error": "聊天记录不存在"}), 404

    message, error = read_message_text()
    if error:
        return jsonify({"error": error}), 400

    record["message"] = message
    return jsonify(record)


@app.delete("/api/messages/<int:message_id>")
@with_store_lock
def delete_message(message_id):
    record = find_message(message_id)
    if record is None:
        return jsonify({"error": "聊天记录不存在"}), 404

    messages.remove(record)
    return jsonify({"message": "聊天记录已删除", "id": message_id})


@app.post("/api/conversations")
@with_store_lock
def create_conversation():
    global next_conversation_id

    data = request.get_json(silent=True)
    if data is None:
        data = {}
    if not isinstance(data, dict):
        return jsonify({"error": "请求体必须是 JSON 对象"}), 400

    title = data.get("title", "新会话")
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "title 必须是非空字符串"}), 400

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
@with_store_lock
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
@with_store_lock
def get_conversation(conversation_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "会话不存在"}), 404
    return jsonify(conversation)


@app.patch("/api/conversations/<int:conversation_id>")
@with_store_lock
def rename_conversation(conversation_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "会话不存在"}), 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "请求体必须是 JSON 对象"}), 400

    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "title 必须是非空字符串"}), 400

    conversation["title"] = title.strip()
    save_conversations()
    return jsonify(conversation)


@app.delete("/api/conversations/<int:conversation_id>")
@with_store_lock
def delete_conversation(conversation_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "会话不存在"}), 404

    conversations.remove(conversation)
    save_conversations()
    return jsonify({"message": "会话已删除", "id": conversation_id})


@app.post("/api/conversations/<int:conversation_id>/messages")
@track_chat
def create_conversation_message(conversation_id):
    global next_conversation_message_id, next_turn_id

    message, error = read_message_text()
    if error:
        return jsonify({"error": error}), 400

    with store_lock:
        conversation = find_conversation(conversation_id)
        if conversation is None:
            return jsonify({"error": "会话不存在"}), 404
        api_messages = [
            {"role": item["role"], "content": item["content"]}
            for item in conversation["messages"]
        ]
    api_messages.append({"role": "user", "content": message})

    # Release the storage lock while waiting for a reply so requests can overlap.
    reply, deepseek_error = generate_reply(api_messages)
    if deepseek_error:
        error_message, status_code = deepseek_error
        return jsonify({"error": error_message}), status_code

    with store_lock:
        if find_conversation(conversation_id) is not conversation:
            return jsonify({"error": "等待回复期间会话已被删除"}), 409
        user_message = {
            "id": next_conversation_message_id,
            "turn_id": next_turn_id,
            "role": "user",
            "content": message,
        }
        assistant_message = {
            "id": next_conversation_message_id + 1,
            "turn_id": next_turn_id,
            "role": "assistant",
            "content": reply,
        }
        conversation["messages"].extend([user_message, assistant_message])
        next_conversation_message_id += 2
        next_turn_id += 1
        save_conversations()
        return jsonify(conversation), 201


@app.patch("/api/conversations/<int:conversation_id>/turns/<int:turn_id>")
@with_store_lock
def update_conversation_turn(conversation_id, turn_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "会话不存在"}), 404

    user_message = next(
        (
            item
            for item in conversation["messages"]
            if item["turn_id"] == turn_id and item["role"] == "user"
        ),
        None,
    )
    if user_message is None:
        return jsonify({"error": "聊天轮次不存在"}), 404

    message, error = read_message_text()
    if error:
        return jsonify({"error": error}), 400

    user_message["content"] = message
    save_conversations()
    return jsonify(conversation)


@app.delete("/api/conversations/<int:conversation_id>/turns/<int:turn_id>")
@with_store_lock
def delete_conversation_turn(conversation_id, turn_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "会话不存在"}), 404

    remaining_messages = [
        item for item in conversation["messages"] if item["turn_id"] != turn_id
    ]
    if len(remaining_messages) == len(conversation["messages"]):
        return jsonify({"error": "聊天轮次不存在"}), 404

    conversation["messages"] = remaining_messages
    save_conversations()
    return jsonify(conversation)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("LAB4_PORT", "5001")),
            debug=False, use_reloader=False, threaded=True, load_dotenv=False)
