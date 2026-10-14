"""本地聊天应用：默认 mock，保留会话和消息 CRUD；real 模式显式启用。"""

import json
import os
import math
import time
from copy import deepcopy
from functools import wraps
from threading import RLock
from pathlib import Path

import requests
from flask import Flask, jsonify, request, send_from_directory, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from metrics import CHAT_REQUESTS, CHAT_INPROGRESS, CHAT_DURATION

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
DATA_DIR = BASE_DIR / ".runtime" / "app"
CONVERSATIONS_FILE = DATA_DIR / "conversations.json"
DEFAULT_CONVERSATION_TITLE = "新会话"

# 不读取 .env；mock 分支不访问模型服务或读取 Key。
MODEL_MODE = os.getenv("MODEL_MODE", "mock").lower()
if MODEL_MODE not in {"mock", "real"}:
    raise ValueError("MODEL_MODE 必须为 mock 或 real")
store_lock = RLock()


def locked(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        with store_lock:
            return view(*args, **kwargs)
    return wrapped


def measured_chat(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        started = time.perf_counter()
        outcome = "error"
        CHAT_INPROGRESS.inc()
        try:
            response = app.make_response(view(*args, **kwargs))
            if 200 <= response.status_code < 300:
                outcome = "success"
            return response
        finally:
            CHAT_REQUESTS.labels(outcome=outcome).inc()
            CHAT_DURATION.observe(time.perf_counter() - started)
            CHAT_INPROGRESS.dec()
    return wrapped


# DeepSeek 的接口地址和模型名，参考官方文档：https://api-docs.deepseek.com/zh-cn/
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# 静态资源（style.css、app.js）由 Flask 从 frontend/ 目录提供，
# static_url_path="" 表示它们挂在网站根路径下，例如 /style.css
app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")

# 让 JSON 响应里的中文直接显示，而不是转义成 \uXXXX
app.json.ensure_ascii = False

# 会话在内存里保存一份，每次改动后同步写回 conversations.json。
# 每个会话形如 {"id", "title", "messages": [{"id", "message", "reply"}]}；
# 消息 id 在所有会话之间统一递增，这样按 id 修改或删除时不会有歧义。
conversations = []
next_conversation_id = 1
next_message_id = 1


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), content_type=CONTENT_TYPE_LATEST)


@app.get("/api/lab/status")
def lab_status():
    if MODEL_MODE != "mock":
        return jsonify({"error": "实验接口未启用"}), 404
    return jsonify({"mode": MODEL_MODE, "external_model_calls": False})


@app.get("/api/hello")
def hello():
    """最简单的接口，用于确认后端已经正常运行。"""
    return jsonify({"message": "你好"})


@app.get("/")
def index():
    """返回前端页面，这样浏览器访问 http://localhost:5001/ 就能打开它。"""
    return send_from_directory(FRONTEND_DIR, "index.html")


def find_conversation(conversation_id):
    """按 id 查找会话，找不到时返回 None。"""
    for conversation in conversations:
        if conversation["id"] == conversation_id:
            return conversation
    return None


def find_message(message_id):
    """在所有会话里按 id 找一条消息，返回 (会话, 消息)；找不到时两者都是 None。"""
    for conversation in conversations:
        for record in conversation["messages"]:
            if record["id"] == message_id:
                return conversation, record
    return None, None


def read_json_body():
    """读取请求体里的 JSON 对象，取不到时返回空字典。"""
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def read_message_text(body):
    """取出并校验 message 字段，不合法时返回 None。"""
    text = body.get("message")
    if not isinstance(text, str) or not text.strip():
        return None
    return text.strip()


def read_title(body):
    """取出并校验 title 字段，不合法时返回 None。"""
    title = body.get("title")
    if not isinstance(title, str) or not title.strip():
        return None
    return title.strip()


def create_conversation(title):
    """新建一个空会话并返回它。"""
    global next_conversation_id

    conversation = {"id": next_conversation_id, "title": title, "messages": []}
    conversations.append(conversation)
    next_conversation_id += 1
    return conversation


def default_conversation(create_if_missing=True):
    """给 /api/messages 兼容接口用的默认会话，也就是当前第一个会话。"""
    if conversations:
        return conversations[0]
    if create_if_missing:
        return create_conversation(DEFAULT_CONVERSATION_TITLE)
    return None


def load_data():
    """把 .runtime/app/conversations.json 里的会话读回内存，供 Flask 启动时调用。"""
    global conversations, next_conversation_id, next_message_id

    if not CONVERSATIONS_FILE.exists():
        return

    try:
        with CONVERSATIONS_FILE.open(encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        # 文件读不了或内容不是合法 JSON 时，从空数据开始，不让服务起不来
        return

    if not isinstance(data, list):
        return

    loaded = []
    for item in data:
        if not isinstance(item, dict):
            continue
        conversation_id = item.get("id")
        title = item.get("title")
        raw_messages = item.get("messages")
        if not isinstance(conversation_id, int):
            continue
        if not isinstance(title, str) or not isinstance(raw_messages, list):
            continue

        records = [
            {"id": record["id"], "message": record["message"], "reply": record["reply"]}
            for record in raw_messages
            if isinstance(record, dict)
            and isinstance(record.get("id"), int)
            and isinstance(record.get("message"), str)
            and isinstance(record.get("reply"), str)
        ]
        loaded.append({"id": conversation_id, "title": title, "messages": records})

    conversations = loaded

    # 新 id 都从已有数据的最大 id 往后接，避免和文件里的数据冲突
    next_conversation_id = max((item["id"] for item in conversations), default=0) + 1
    next_message_id = (
        max(
            (record["id"] for item in conversations for record in item["messages"]),
            default=0,
        )
        + 1
    )


def save_data():
    """把当前内存里的会话写回 .runtime/app/conversations.json。"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with CONVERSATIONS_FILE.open("w", encoding="utf-8") as file:
        json.dump(conversations, file, ensure_ascii=False, indent=2)


# 启动时先把上次保存的会话读回内存
load_data()


def ask_deepseek(history, message):
    """把会话历史和本次提问一起发给 DeepSeek，返回模型生成的回复文本。

    history 是当前会话里已有的记录，用来给模型提供上下文。
    任何一步出错都抛出 RuntimeError，由调用方转成 JSON 错误响应，
    避免异常直接把 Flask 进程打挂。
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError(
            "后端未配置 DEEPSEEK_API_KEY，请检查运行时环境变量"
        )

    # 历史里的每一轮问答都还原成 user / assistant 两条消息，
    # 最后再附上本次提问，模型就能基于同一会话的上下文回答
    chat_messages = []
    for record in history:
        chat_messages.append({"role": "user", "content": record["message"]})
        chat_messages.append({"role": "assistant", "content": record["reply"]})
    chat_messages.append({"role": "user", "content": message})

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": chat_messages,
        "stream": False,
    }

    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=60,
        )
    except requests.RequestException as error:
        raise RuntimeError("连接 DeepSeek 失败，请稍后重试") from error

    if response.status_code != 200:
        raise RuntimeError(
            f"DeepSeek 返回错误（HTTP {response.status_code}），请检查服务配置或额度"
        )

    try:
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        if not isinstance(content, str) or not content.strip():
            raise ValueError("empty or invalid content")
        return content.strip()
    except (ValueError, KeyError, IndexError, TypeError) as error:
        raise RuntimeError("DeepSeek 返回的数据格式与预期不一致") from error


@app.get("/api/conversations")
@locked
def list_conversations():
    """返回全部会话（每个会话里包含自己的消息）。"""
    return jsonify(conversations)


@app.post("/api/conversations")
@locked
def create_conversation_route():
    """新建一个会话。"""
    title = read_title(read_json_body()) or DEFAULT_CONVERSATION_TITLE
    conversation = create_conversation(title)
    save_data()
    return jsonify(conversation), 201


@app.get("/api/conversations/<int:conversation_id>")
@locked
def get_conversation(conversation_id):
    """返回指定会话及其消息。"""
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": f"id 为 {conversation_id} 的会话不存在"}), 404
    return jsonify(conversation)


@app.patch("/api/conversations/<int:conversation_id>")
@locked
def rename_conversation(conversation_id):
    """重命名指定会话。"""
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": f"id 为 {conversation_id} 的会话不存在"}), 404

    title = read_title(read_json_body())
    if title is None:
        return jsonify({"error": "请求体需要是 JSON，并且 title 字段不能为空"}), 400

    conversation["title"] = title
    save_data()
    return jsonify(conversation)


@app.delete("/api/conversations/<int:conversation_id>")
@locked
def delete_conversation(conversation_id):
    """删除指定会话，会话里的消息也随之删除。"""
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": f"id 为 {conversation_id} 的会话不存在"}), 404

    conversations.remove(conversation)
    save_data()
    return jsonify({"deleted_id": conversation_id})


def create_record(conversation, text):
    """经同一聊天流程生成回复；等待模型时不持有共享存储锁。"""
    global next_message_id
    with store_lock:
        history = deepcopy(conversation["messages"])
    if MODEL_MODE == "mock":
        body = read_json_body()
        delay = body.get("mock_delay_seconds", 0.1)
        force_error = body.get("mock_force_error", False)
        if (isinstance(delay, bool) or not isinstance(delay, (int, float))
                or not math.isfinite(delay) or not 0 <= delay <= 10
                or not isinstance(force_error, bool)):
            return jsonify({"error": "延迟须为 0–10 秒，失败选项须为布尔值"}), 400
        time.sleep(delay)
        if force_error:
            return jsonify({"error": "实验模拟失败", "simulated": True}), 503
        reply = "这是本地模拟回复，未调用外部模型。"
    else:
        try:
            reply = ask_deepseek(history, text)
        except RuntimeError as error:
            return jsonify({"error": str(error)}), 502
    with store_lock:
        if find_conversation(conversation["id"]) is not conversation:
            return jsonify({"error": "处理期间会话已被删除"}), 409
        record = {"id": next_message_id, "message": text, "reply": reply}
        conversation["messages"].append(record)
        next_message_id += 1
        save_data()
        return jsonify(record), 201


@app.post("/api/conversations/<int:conversation_id>/messages")
@measured_chat
def create_conversation_message(conversation_id):
    """在指定会话里发一条消息，回复由 DeepSeek 生成。"""
    with store_lock:
        conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": f"id 为 {conversation_id} 的会话不存在"}), 404

    text = read_message_text(read_json_body())
    if text is None:
        return jsonify({"error": "请求体需要是 JSON，并且 message 字段不能为空"}), 400

    return create_record(conversation, text)


@app.get("/api/messages")
@locked
def list_messages():
    """兼容入口：返回默认会话里的全部消息。"""
    conversation = default_conversation(create_if_missing=False)
    return jsonify(conversation["messages"] if conversation else [])


@app.post("/api/messages")
@measured_chat
def create_message():
    """兼容入口：在默认会话里创建一条记录。"""
    text = read_message_text(read_json_body())
    if text is None:
        return jsonify({"error": "请求体需要是 JSON，并且 message 字段不能为空"}), 400

    with store_lock:
        conversation = default_conversation()
    return create_record(conversation, text)


@app.patch("/api/messages/<int:message_id>")
@locked
def update_message(message_id):
    """修改指定聊天记录的用户消息内容。"""
    conversation, record = find_message(message_id)
    if record is None:
        return jsonify({"error": f"id 为 {message_id} 的聊天记录不存在"}), 404

    text = read_message_text(read_json_body())
    if text is None:
        return jsonify({"error": "请求体需要是 JSON，并且 message 字段不能为空"}), 400

    record["message"] = text
    save_data()
    return jsonify(record)


@app.delete("/api/messages/<int:message_id>")
@locked
def delete_message(message_id):
    """删除指定聊天记录。"""
    conversation, record = find_message(message_id)
    if record is None:
        return jsonify({"error": f"id 为 {message_id} 的聊天记录不存在"}), 404

    conversation["messages"].remove(record)
    save_data()
    return jsonify({"deleted_id": message_id})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5001")),
            debug=False, threaded=True, use_reloader=False)
