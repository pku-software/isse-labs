import json
import os
from functools import wraps
from pathlib import Path
from threading import RLock
from time import sleep

from flask import Flask, Response, jsonify, request, send_from_directory
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from metrics import REGISTRY, track_chat


app = Flask(__name__, static_folder="frontend", static_url_path="/frontend")
app.json.ensure_ascii = False
app.config["CHAT_MODE"] = os.getenv("CHAT_MODE", "mock").lower()
if app.config["CHAT_MODE"] not in ("mock", "real"):
    raise ValueError("CHAT_MODE 必须为 mock 或 real")
runtime_dir = Path(__file__).parent / ".runtime" / "app"
data_file = Path(os.getenv(
    "APP_DATA_FILE", str(runtime_dir / f"{app.config['CHAT_MODE']}-conversations.json")
))
state_lock = RLock()
MAX_MOCK_DELAY = 10.0


def with_state_lock(view):
    """Serialize short CRUD operations, including response serialization."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        with state_lock:
            return app.make_response(view(*args, **kwargs))
    return wrapped


def load_state():
    if not data_file.exists():
        return [], []
    contents = data_file.read_text(encoding="utf-8")
    if not contents.strip():
        return [], []

    state = json.loads(contents)
    if not isinstance(state, dict):
        raise ValueError("聊天数据文件的最外层必须是 JSON 对象")
    stored_messages = state.get("messages", [])
    stored_conversations = state.get("conversations", [])
    if not isinstance(stored_messages, list) or not isinstance(stored_conversations, list):
        raise ValueError("聊天数据文件中的 messages 和 conversations 必须是数组")
    return stored_messages, stored_conversations


def save_state():
    data_file.parent.mkdir(parents=True, exist_ok=True)
    state = {"messages": messages, "conversations": conversations}
    temporary_file = data_file.with_suffix(".tmp")
    temporary_file.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary_file.replace(data_file)


messages, conversations = load_state()
next_message_id = max((item["id"] for item in messages), default=0) + 1
next_conversation_id = max((item["id"] for item in conversations), default=0) + 1
next_turn_id = max(
    (message["turn_id"] for conversation in conversations for message in conversation["messages"]),
    default=0,
) + 1


def generate_reply(chat_messages, options=None):
    if app.config["CHAT_MODE"] == "mock":
        options = options or {}
        delay = options.get("mock_delay", 0.1)
        force_error = options.get("mock_error", False)
        if type(delay) not in (int, float) or not 0 <= delay <= MAX_MOCK_DELAY:
            return None, ({"error": "mock_delay 必须是 0～10 秒之间的有限数字"}, 400)
        if not isinstance(force_error, bool):
            return None, ({"error": "mock_error 必须是布尔值"}, 400)
        sleep(delay)
        if force_error:
            return None, ({"error": "模拟模型请求失败", "code": "mock_error"}, 503)
        return "这是本地 mock 回复：应用已收到测试消息。", None

    # Real mode is retained for the original app; this lab never enables it.
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return None, ({"error": "服务器尚未配置 DeepSeek API Key"}, 503)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com", timeout=45.0)
        completion = client.chat.completions.create(
            model="deepseek-flash",
            messages=chat_messages,
            stream=False,
            extra_body={"thinking": {"type": "disabled"}},
        )
        reply = completion.choices[0].message.content
        if not reply:
            return None, ({"error": "DeepSeek 未返回回复内容"}, 502)
        return reply, None
    except Exception:
        return None, ({"error": "DeepSeek 请求失败，请稍后重试或检查服务配置"}, 502)


def find_conversation(conversation_id):
    return next((item for item in conversations if item["id"] == conversation_id), None)


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/hello")
def hello():
    return {"message": "你好"}


@app.get("/api/status")
def status():
    if app.config["CHAT_MODE"] != "mock":
        return {"error": "实验状态接口仅在 mock 模式下可用"}, 404
    return {"mode": app.config["CHAT_MODE"], "external_model_calls": False}


@app.get("/metrics")
def expose_metrics():
    return Response(generate_latest(REGISTRY), content_type=CONTENT_TYPE_LATEST)


@app.post("/api/messages")
@track_chat
def create_message():
    global next_message_id

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get("message"), str):
        return {"error": "请提供 JSON 格式的 message 字符串"}, 400

    message = data["message"].strip()
    if not message:
        return {"error": "消息不能为空"}, 400

    reply, error = generate_reply([{"role": "user", "content": message}], data)
    if error:
        return error

    with state_lock:
        record = {"id": next_message_id, "message": message, "reply": reply}
        next_message_id += 1
        messages.append(record)
        save_state()
        return jsonify(record), 201


@app.get("/api/messages")
@with_state_lock
def list_messages():
    return jsonify(messages)


@app.patch("/api/messages/<int:message_id>")
@with_state_lock
def update_message(message_id):
    record = next((item for item in messages if item["id"] == message_id), None)
    if record is None:
        return {"error": "聊天记录不存在"}, 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get("message"), str):
        return {"error": "请提供 JSON 格式的 message 字符串"}, 400

    message = data["message"].strip()
    if not message:
        return {"error": "消息不能为空"}, 400

    record["message"] = message
    save_state()
    return record


@app.delete("/api/messages/<int:message_id>")
@with_state_lock
def delete_message(message_id):
    record = next((item for item in messages if item["id"] == message_id), None)
    if record is None:
        return {"error": "聊天记录不存在"}, 404

    messages.remove(record)
    save_state()
    return {"message": "已删除"}


@app.post("/api/conversations")
@with_state_lock
def create_conversation():
    global next_conversation_id

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return {"error": "请提供 JSON 格式的会话标题"}, 400
    title = data.get("title", "新会话")
    if not isinstance(title, str) or not title.strip():
        return {"error": "会话标题不能为空"}, 400

    conversation = {"id": next_conversation_id, "title": title.strip(), "messages": []}
    next_conversation_id += 1
    conversations.append(conversation)
    save_state()
    return conversation, 201


@app.get("/api/conversations")
@with_state_lock
def list_conversations():
    return jsonify([
        {"id": item["id"], "title": item["title"], "message_count": len(item["messages"]) // 2}
        for item in conversations
    ])


@app.get("/api/conversations/<int:conversation_id>")
@with_state_lock
def get_conversation(conversation_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return {"error": "会话不存在"}, 404
    return conversation


@app.patch("/api/conversations/<int:conversation_id>")
@with_state_lock
def rename_conversation(conversation_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return {"error": "会话不存在"}, 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get("title"), str):
        return {"error": "请提供 JSON 格式的 title 字符串"}, 400
    title = data["title"].strip()
    if not title:
        return {"error": "会话标题不能为空"}, 400

    conversation["title"] = title
    save_state()
    return conversation


@app.delete("/api/conversations/<int:conversation_id>")
@with_state_lock
def delete_conversation(conversation_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return {"error": "会话不存在"}, 404
    conversations.remove(conversation)
    save_state()
    return {"message": "会话已删除"}


@app.post("/api/conversations/<int:conversation_id>/messages")
@track_chat
def create_conversation_message(conversation_id):
    global next_turn_id

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get("message"), str):
        return {"error": "请提供 JSON 格式的 message 字符串"}, 400
    message = data["message"].strip()
    if not message:
        return {"error": "消息不能为空"}, 400

    with state_lock:
        conversation = find_conversation(conversation_id)
        if conversation is None:
            return {"error": "会话不存在"}, 404
        history = [
            {"role": item["role"], "content": item["content"]}
            for item in conversation["messages"]
        ]
    # Neither the model call nor the mock delay holds the shared storage lock.
    reply, error = generate_reply(history + [{"role": "user", "content": message}], data)
    if error:
        return error

    with state_lock:
        if find_conversation(conversation_id) is not conversation:
            return {"error": "回复生成期间会话已被删除"}, 409
        turn_id = next_turn_id
        next_turn_id += 1
        conversation["messages"].extend([
            {"turn_id": turn_id, "role": "user", "content": message},
            {"turn_id": turn_id, "role": "assistant", "content": reply},
        ])
        save_state()
        return {"id": turn_id, "message": message, "reply": reply}, 201


@app.patch("/api/conversations/<int:conversation_id>/messages/<int:turn_id>")
@with_state_lock
def update_conversation_message(conversation_id, turn_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return {"error": "会话不存在"}, 404
    user_message = next((item for item in conversation["messages"] if item["turn_id"] == turn_id and item["role"] == "user"), None)
    if user_message is None:
        return {"error": "聊天记录不存在"}, 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get("message"), str):
        return {"error": "请提供 JSON 格式的 message 字符串"}, 400
    message = data["message"].strip()
    if not message:
        return {"error": "消息不能为空"}, 400

    user_message["content"] = message
    save_state()
    return {"id": turn_id, "message": message}


@app.delete("/api/conversations/<int:conversation_id>/messages/<int:turn_id>")
@with_state_lock
def delete_conversation_message(conversation_id, turn_id):
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return {"error": "会话不存在"}, 404
    if not any(item["turn_id"] == turn_id for item in conversation["messages"]):
        return {"error": "聊天记录不存在"}, 404

    conversation["messages"] = [
        item for item in conversation["messages"] if item["turn_id"] != turn_id
    ]
    save_state()
    return {"message": "已删除"}


if __name__ == "__main__":
    app.run(
        host="127.0.0.1", port=int(os.getenv("PORT", "5001")),
        debug=False, threaded=True, use_reloader=False,
    )
