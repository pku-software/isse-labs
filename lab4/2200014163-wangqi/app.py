import json
import os
import threading
import time

import requests
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)


load_dotenv()

app = Flask(__name__, static_folder="frontend", static_url_path="")
app.json.ensure_ascii = False

# 实验运行模式：mock（本地模拟，默认）或 real（真实模型）。
APP_MODE = os.getenv("APP_MODE", "mock").strip().lower()
if APP_MODE not in ("mock", "real"):
    APP_MODE = "mock"

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CONVERSATIONS_FILE = os.path.join(DATA_DIR, "conversations.json")

# 监控指标：只统计聊天请求处理，不含 /metrics、状态接口与静态资源。
CHAT_REQUESTS_TOTAL = Counter(
    "chat_requests_total",
    "聊天请求处理完成总数，按 outcome 区分成功与错误",
    ["outcome"],
)
CHAT_REQUESTS_TOTAL.labels(outcome="success")
CHAT_REQUESTS_TOTAL.labels(outcome="error")

CHAT_INPROGRESS_REQUESTS = Gauge(
    "chat_inprogress_requests",
    "当前正在处理的聊天请求数",
)

CHAT_REQUEST_DURATION_SECONDS = Histogram(
    "chat_request_duration_seconds",
    "聊天请求服务端处理耗时（秒）",
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

# 共享会话数据的线程安全锁。
_STORE_LOCK = threading.Lock()

# mock 模式允许的最大后端延迟，与教学脚本参数范围一致。
_MOCK_MAX_DELAY_SECONDS = 10.0


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


class MockModelError(Exception):
    """mock 模式下按实验要求模拟的失败。"""


def generate_reply(history, delay_seconds=0.0, force_error=False):
    """生成聊天回复：mock 模式用固定回复并支持实验延迟/失败，real 模式调用真实模型。"""
    if APP_MODE == "mock":
        if delay_seconds:
            time.sleep(delay_seconds)
        if force_error:
            raise MockModelError("模拟错误")
        return "（mock 回复）这是一条本地模拟回复，用于监控实验。"
    return call_deepseek(history)


def remove_message_by_id(conv, message_id):
    for index, msg in enumerate(conv["messages"]):
        if msg.get("id") == message_id:
            conv["messages"].pop(index)
            return True
    return False


def parse_experiment_options(data):
    """从聊天请求体解析实验选项；仅 mock 模式生效，real 模式一律忽略。"""
    if APP_MODE != "mock":
        return 0.0, False
    try:
        delay_seconds = float(data.get("delay_seconds", 0.0))
    except (TypeError, ValueError):
        delay_seconds = 0.0
    delay_seconds = max(0.0, min(delay_seconds, _MOCK_MAX_DELAY_SECONDS))
    force_error = bool(data.get("force_error", False))
    return delay_seconds, force_error


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.route("/api/experiment/status")
def experiment_status():
    return jsonify({
        "mode": APP_MODE,
        "external_model_calls": APP_MODE == "real",
    })


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.route("/api/conversations", methods=["POST"])
def create_conversation():
    global next_conversation_id

    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip() or "新会话"

    with _STORE_LOCK:
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

    with _STORE_LOCK:
        conv["title"] = title
        save_conversations()
    return jsonify(conv)


@app.route("/api/conversations/<int:conversation_id>", methods=["DELETE"])
def delete_conversation(conversation_id):
    with _STORE_LOCK:
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

    if APP_MODE == "real" and not DEEPSEEK_API_KEY:
        return jsonify({"error": "缺少 DEEPSEEK_API_KEY，请检查 .env 配置"}), 500

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "message" not in data:
        return jsonify({"error": "缺少 message 字段"}), 400

    message = str(data["message"]).strip()
    if not message:
        return jsonify({"error": "message 不能为空"}), 400

    delay_seconds, force_error = parse_experiment_options(data)

    CHAT_INPROGRESS_REQUESTS.inc()
    started_at = time.monotonic()
    user_msg = None
    try:
        with _STORE_LOCK:
            user_msg = {"id": next_message_id, "role": "user", "content": message}
            next_message_id += 1
            conv["messages"].append(user_msg)
            history = [{"role": m["role"], "content": m["content"]} for m in conv["messages"]]

        reply = generate_reply(history, delay_seconds=delay_seconds, force_error=force_error)

        with _STORE_LOCK:
            assistant_msg = {"id": next_message_id, "role": "assistant", "content": reply}
            next_message_id += 1
            conv["messages"].append(assistant_msg)
            save_conversations()

        CHAT_REQUESTS_TOTAL.labels(outcome="success").inc()
        return jsonify(assistant_msg), 201
    except MockModelError:
        with _STORE_LOCK:
            if user_msg is not None:
                remove_message_by_id(conv, user_msg["id"])
            save_conversations()
        CHAT_REQUESTS_TOTAL.labels(outcome="error").inc()
        return jsonify({"error": "模拟错误：本次请求按要求失败"}), 503
    except Exception as exc:
        with _STORE_LOCK:
            if user_msg is not None:
                remove_message_by_id(conv, user_msg["id"])
            save_conversations()
        CHAT_REQUESTS_TOTAL.labels(outcome="error").inc()
        return jsonify({"error": f"调用模型失败：{exc}"}), 502
    finally:
        CHAT_REQUEST_DURATION_SECONDS.observe(time.monotonic() - started_at)
        CHAT_INPROGRESS_REQUESTS.dec()


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

    if conv["messages"][target_index]["role"] != "user":
        with _STORE_LOCK:
            conv["messages"][target_index]["content"] = content
            save_conversations()
        return jsonify(conv["messages"][target_index])

    if APP_MODE == "real" and not DEEPSEEK_API_KEY:
        return jsonify({"error": "缺少 DEEPSEEK_API_KEY，请检查 .env 配置"}), 500

    CHAT_INPROGRESS_REQUESTS.inc()
    started_at = time.monotonic()
    try:
        with _STORE_LOCK:
            conv["messages"][target_index]["content"] = content
            del conv["messages"][target_index + 1:]
            history = [{"role": m["role"], "content": m["content"]} for m in conv["messages"]]

        reply = generate_reply(history)

        with _STORE_LOCK:
            assistant_msg = {"id": next_message_id, "role": "assistant", "content": reply}
            next_message_id += 1
            conv["messages"].append(assistant_msg)
            save_conversations()

        CHAT_REQUESTS_TOTAL.labels(outcome="success").inc()
        return jsonify(assistant_msg), 200
    except MockModelError:
        with _STORE_LOCK:
            save_conversations()
        CHAT_REQUESTS_TOTAL.labels(outcome="error").inc()
        return jsonify({"error": "模拟错误"}), 503
    except Exception as exc:
        with _STORE_LOCK:
            save_conversations()
        CHAT_REQUESTS_TOTAL.labels(outcome="error").inc()
        return jsonify({"error": f"调用模型失败：{exc}"}), 502
    finally:
        CHAT_REQUEST_DURATION_SECONDS.observe(time.monotonic() - started_at)
        CHAT_INPROGRESS_REQUESTS.dec()


@app.route("/api/conversations/<int:conversation_id>/messages/<int:message_id>", methods=["DELETE"])
def delete_message(conversation_id, message_id):
    with _STORE_LOCK:
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
    app.run(host="127.0.0.1", port=5001, debug=False, threaded=True)
