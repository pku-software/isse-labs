import os
import math
import time
from threading import RLock

import requests
from flask import Flask, Response, jsonify, request, send_from_directory
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from metrics import REQUESTS, INPROGRESS, DURATION

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# 配置仅从进程环境读取，实验默认 mock，不读取 .env。
MODEL_MODE = os.environ.get("MODEL_MODE", "mock").lower()
if MODEL_MODE not in {"mock", "real"}:
    raise ValueError("MODEL_MODE 必须是 mock 或 real")

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_TIMEOUT = 60

app = Flask(__name__)
app.json.ensure_ascii = False

# 聊天记录暂存在内存中，Flask 重启后会被清空。
messages = []
messages_lock = RLock()


class DeepSeekError(Exception):
    """调用 DeepSeek 过程中出现的问题，用于返回清晰的错误信息。"""


def next_message_id():
    return max((record["id"] for record in messages), default=0) + 1


def find_message(message_id):
    return next((record for record in messages if record["id"] == message_id), None)


def read_message_text():
    """从请求体中读出合法的 message 文本，不合法时返回 None。"""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None

    text = data.get("message")
    if not isinstance(text, str) or not text.strip():
        return None

    return text.strip()


def ask_deepseek(text):
    """把用户消息发给 DeepSeek，返回模型回复的文本。"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise DeepSeekError(
            "服务器没有配置 DEEPSEEK_API_KEY，请检查运行环境变量或本地 .env 文件"
        )

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [{"role": "user", "content": text}],
        "stream": False,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            json=payload,
            timeout=DEEPSEEK_TIMEOUT,
        )
    except requests.RequestException as error:
        raise DeepSeekError(f"无法连接 DeepSeek：{error}") from error

    if response.status_code != 200:
        detail = ""
        try:
            detail = response.json().get("error", {}).get("message", "")
        except ValueError:
            detail = ""
        suffix = f"：{detail}" if detail else ""
        raise DeepSeekError(f"DeepSeek 返回错误（HTTP {response.status_code}）{suffix}")

    try:
        return response.json()["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError) as error:
        raise DeepSeekError("DeepSeek 返回的数据结构不符合预期") from error


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), content_type=CONTENT_TYPE_LATEST)


@app.get("/api/lab-status")
def lab_status():
    return jsonify(mode=MODEL_MODE, external_model_calls=MODEL_MODE == "real")


@app.before_request
def start_chat_metrics():
    if request.endpoint == "create_message":
        request.environ["chat_started"] = time.perf_counter()
        INPROGRESS.inc()


@app.after_request
def finish_chat_response(response):
    if "chat_started" in request.environ:
        request.environ["chat_outcome"] = "success" if 200 <= response.status_code < 300 else "error"
    return response


@app.teardown_request
def finish_chat_metrics(error):
    started = request.environ.pop("chat_started", None)
    if started is not None:
        try:
            outcome = "error" if error is not None else request.environ.get("chat_outcome", "error")
            REQUESTS.labels(outcome=outcome).inc()
            DURATION.observe(time.perf_counter() - started)
        finally:
            INPROGRESS.dec()


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/<path:filename>")
def frontend_file(filename):
    """提供前端用到的静态文件，例如 style.css 和 app.js。"""
    return send_from_directory(FRONTEND_DIR, filename)


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.get("/api/messages")
def list_messages():
    with messages_lock:
        return jsonify([dict(record) for record in messages])


@app.post("/api/messages")
def create_message():
    text = read_message_text()
    if text is None:
        return jsonify({"error": "请求体需要是 JSON，且 message 必须是非空字符串"}), 400

    if MODEL_MODE == "mock":
        data = request.get_json()
        options = data.get("mock", {})
        if not isinstance(options, dict):
            return jsonify(error="mock 必须是对象"), 400
        delay = options.get("delay_seconds", 0.1)
        force_error = options.get("force_error", False)
        if (isinstance(delay, bool) or not isinstance(delay, (int, float))
                or not math.isfinite(delay) or not 0 <= delay <= 10
                or not isinstance(force_error, bool)):
            return jsonify(error="延迟须为 0–10 秒，force_error 须为布尔值"), 400
        time.sleep(delay)
        if force_error:
            return jsonify(error="实验模拟失败", simulated=True), 503
        reply = "这是本地 mock 测试回复。"
    else:
        try:
            reply = ask_deepseek(text)
        except DeepSeekError as error:
            return jsonify({"error": str(error)}), 502

    with messages_lock:
        record = {"id": next_message_id(), "message": text, "reply": reply}
        messages.append(record)
        return jsonify(record), 201


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    with messages_lock:
        record = find_message(message_id)
        if record is None:
            return jsonify({"error": f"找不到 id 为 {message_id} 的聊天记录"}), 404

        text = read_message_text()
        if text is None:
            return jsonify({"error": "请求体需要是 JSON，且 message 必须是非空字符串"}), 400

        record["message"] = text
        return jsonify(record)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    with messages_lock:
        record = find_message(message_id)
        if record is None:
            return jsonify({"error": f"找不到 id 为 {message_id} 的聊天记录"}), 404

        messages.remove(record)
        return jsonify(record)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5001")),
            debug=False, threaded=True, use_reloader=False)
