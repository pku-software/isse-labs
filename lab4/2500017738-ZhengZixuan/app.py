import copy
import json
import os
import threading
import time
from functools import wraps
from pathlib import Path

from flask import Flask, jsonify, make_response, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest


app = Flask(__name__, static_folder="frontend", static_url_path="")
app.json.ensure_ascii = False

CHAT_MODE = os.getenv("CHAT_MODE", "mock").strip().lower()
if CHAT_MODE not in {"mock", "real"}:
    raise ValueError("CHAT_MODE 必须是 mock 或 real")

DATA_FILE = Path(__file__).resolve().parent / "data" / "conversations.json"
CONVERSATION_LOCK = threading.RLock()

CHAT_REQUESTS = Counter(
    "chat_requests_total",
    "Completed chat requests grouped by outcome.",
    ("outcome",),
)
CHAT_IN_PROGRESS = Gauge(
    "chat_inprogress_requests",
    "Number of chat requests currently being processed.",
)
CHAT_DURATION = Histogram(
    "chat_request_duration_seconds",
    "Server-side chat request processing time in seconds.",
    buckets=(0.05, 0.1, 0.2, 0.5, 1, 2, 3, 5, 10),
)
for _outcome in ("success", "error"):
    CHAT_REQUESTS.labels(outcome=_outcome).inc(0)


class MockChatError(Exception):
    """Raised for the deterministic Lab 4 mock failure scenario."""


class ConversationNotFound(Exception):
    """Raised when a conversation disappears while a chat is being handled."""


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
    """Write one locked snapshot atomically so concurrent requests do not mix files."""
    with CONVERSATION_LOCK:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        temporary_file = DATA_FILE.with_name(f".{DATA_FILE.name}.tmp")
        temporary_file.write_text(
            json.dumps(conversations, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        temporary_file.replace(DATA_FILE)


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


def mock_options(data):
    """Read bounded experiment controls only in mock mode."""
    if CHAT_MODE != "mock":
        return 0.0, False, None

    delay = data.get("lab4_delay_seconds", 0.1)
    force_error = data.get("lab4_force_error", False)
    if isinstance(delay, bool) or not isinstance(delay, (int, float)):
        return None, None, (jsonify({"error": "lab4_delay_seconds 必须是数字"}), 400)
    if not 0 <= delay <= 5:
        return None, None, (jsonify({"error": "lab4_delay_seconds 必须在 0 到 5 秒之间"}), 400)
    if not isinstance(force_error, bool):
        return None, None, (jsonify({"error": "lab4_force_error 必须是布尔值"}), 400)
    return float(delay), force_error, None


def ask_deepseek(history, message_text):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("missing_api_key")

    # Import only when real mode is actually used. Mock mode needs no SDK or key.
    from openai import OpenAI

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


def get_chat_reply(history, message_text, delay_seconds, force_error):
    if CHAT_MODE == "mock":
        # The delay is intentionally inside server-side request processing.
        time.sleep(delay_seconds)
        if force_error:
            raise MockChatError("模拟失败：这是 Lab 4 访问脚本触发的预期错误")
        return f"模拟回复：已收到“{message_text[:120]}”"
    return ask_deepseek(history, message_text)


def append_exchange(conversation, message_text, delay_seconds, force_error):
    global next_message_id

    with CONVERSATION_LOCK:
        if conversation not in conversations:
            raise ConversationNotFound("会话不存在")
        history = copy.deepcopy(conversation["messages"])

    # Do not hold the shared-data lock during the mock wait or real model call.
    reply = get_chat_reply(history, message_text, delay_seconds, force_error)

    with CONVERSATION_LOCK:
        if conversation not in conversations:
            raise ConversationNotFound("会话已删除")
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
    if isinstance(error, MockChatError):
        return jsonify({"error": str(error)}), 503
    if isinstance(error, ConversationNotFound):
        return jsonify({"error": str(error)}), 404
    if isinstance(error, RuntimeError) and str(error) == "missing_api_key":
        return jsonify({"error": "服务器未配置 DeepSeek API Key"}), 500
    return jsonify({"error": "聊天服务调用失败，请稍后重试"}), 502


def measure_chat_request(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        with CHAT_IN_PROGRESS.track_inprogress(), CHAT_DURATION.time():
            try:
                response = make_response(view(*args, **kwargs))
            except Exception:
                CHAT_REQUESTS.labels(outcome="error").inc()
                raise
            outcome = "success" if response.status_code < 400 else "error"
            CHAT_REQUESTS.labels(outcome=outcome).inc()
            return response

    return wrapped


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.get("/__lab4/status")
def lab4_status():
    return jsonify(
        {
            "mode": CHAT_MODE,
            "external_model_calls": CHAT_MODE == "real",
        }
    )


@app.get("/metrics")
def metrics():
    return make_response(generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST})


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

    with CONVERSATION_LOCK:
        title = title.strip() or f"新对话 {next_conversation_id}"
        conversation = {
            "id": next_conversation_id,
            "title": title,
            "messages": [],
        }
        conversations.append(conversation)
        next_conversation_id += 1
        save_conversations()
        return jsonify(copy.deepcopy(conversation)), 201


@app.get("/api/conversations")
def list_conversations():
    with CONVERSATION_LOCK:
        return jsonify(copy.deepcopy(conversations))


@app.get("/api/conversations/<int:conversation_id>")
def get_conversation(conversation_id):
    with CONVERSATION_LOCK:
        conversation = find_conversation(conversation_id)
        if conversation is None:
            return jsonify({"error": "会话不存在"}), 404
        return jsonify(copy.deepcopy(conversation))


@app.patch("/api/conversations/<int:conversation_id>")
def update_conversation(conversation_id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "请提供 JSON 请求体"}), 400

    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "title 不能为空"}), 400

    with CONVERSATION_LOCK:
        conversation = find_conversation(conversation_id)
        if conversation is None:
            return jsonify({"error": "会话不存在"}), 404
        conversation["title"] = title.strip()
        save_conversations()
        return jsonify(copy.deepcopy(conversation))


@app.delete("/api/conversations/<int:conversation_id>")
def delete_conversation(conversation_id):
    with CONVERSATION_LOCK:
        conversation = find_conversation(conversation_id)
        if conversation is None:
            return jsonify({"error": "会话不存在"}), 404
        conversations.remove(conversation)
        save_conversations()
    return jsonify({"message": "会话已删除"})


@app.post("/api/conversations/<int:conversation_id>/messages")
@measure_chat_request
def create_conversation_message(conversation_id):
    with CONVERSATION_LOCK:
        conversation = find_conversation(conversation_id)
        if conversation is None:
            return jsonify({"error": "会话不存在"}), 404

    data = request.get_json(silent=True)
    message_text, error = validate_message_text(data)
    if error:
        return error
    delay_seconds, force_error, options_error = mock_options(data)
    if options_error:
        return options_error

    try:
        append_exchange(conversation, message_text, delay_seconds, force_error)
    except Exception as exc:
        return deepseek_error_response(exc)
    with CONVERSATION_LOCK:
        return jsonify(copy.deepcopy(conversation)), 201


@app.post("/api/messages")
@measure_chat_request
def create_message():
    global next_conversation_id

    data = request.get_json(silent=True)
    message_text, error = validate_message_text(data)
    if error:
        return error
    delay_seconds, force_error, options_error = mock_options(data)
    if options_error:
        return options_error

    with CONVERSATION_LOCK:
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
            save_conversations()

    try:
        user_message, assistant_message = append_exchange(
            conversation,
            message_text,
            delay_seconds,
            force_error,
        )
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
    with CONVERSATION_LOCK:
        records = []
        for conversation in conversations:
            for index, message in enumerate(conversation["messages"]):
                if message["role"] == "user":
                    records.append(record_from_pair(conversation, index))
        return jsonify(records)


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    data = request.get_json(silent=True)
    message_text, error = validate_message_text(data)
    if error:
        return error

    with CONVERSATION_LOCK:
        result = find_user_message(message_id)
        if result is None:
            return jsonify({"error": "聊天记录不存在"}), 404

        conversation, index, message = result
        message["content"] = message_text
        save_conversations()
        return jsonify(record_from_pair(conversation, index))


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    with CONVERSATION_LOCK:
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
    app.run(
        host="127.0.0.1",
        port=int(os.getenv("PORT", "5001")),
        debug=False,
        threaded=True,
    )
