import os
import threading
import time

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request, send_from_directory
from openai import OpenAI
from prometheus_client import REGISTRY
from prometheus_client.exposition import choose_encoder

from metrics import (
    chat_inprogress_requests,
    chat_request_duration_seconds,
    chat_requests_total,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

CHAT_MODE = os.getenv("CHAT_MODE", "mock").strip().lower()
if CHAT_MODE not in ("mock", "real"):
    raise RuntimeError("CHAT_MODE 只能是 mock 或 real")

# 模拟延迟必须短于脚本允许的最长超时（30 秒）。
MAX_DELAY_SECONDS = 30
MOCK_REPLY = "这是模拟回复。"

app = Flask(__name__)
app.json.ensure_ascii = False

FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

messages = []
next_id = 1
state_lock = threading.Lock()


def external_model_calls_enabled():
    return CHAT_MODE == "real"


def find_message(message_id):
    for item in messages:
        if item["id"] == message_id:
            return item
    return None


def read_message_text():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "message" not in data:
        return None, (jsonify({"error": "缺少 message"}), 400)
    text = data["message"]
    if not isinstance(text, str) or not text.strip():
        return None, (jsonify({"error": "message 不能为空"}), 400)
    return text.strip(), None


def validate_mock_options(data):
    delay = data.get("delay_seconds", 0)
    force_error = data.get("force_error", False)
    if isinstance(delay, bool) or not isinstance(delay, (int, float)):
        return jsonify({"error": "delay_seconds 必须是数字"}), 400
    if not 0 <= delay < MAX_DELAY_SECONDS:
        return jsonify({"error": "delay_seconds 必须在 0 到 30 秒以内"}), 400
    if not isinstance(force_error, bool):
        return jsonify({"error": "force_error 必须是 true 或 false"}), 400
    return None


def request_reply(user_message):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return None, (jsonify({"error": "缺少 DEEPSEEK_API_KEY"}), 500)
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        response = client.chat.completions.create(
            model="deepseek-flash",
            messages=[{"role": "user", "content": user_message}],
        )
        reply = response.choices[0].message.content
    except Exception:
        return None, (jsonify({"error": "模型调用失败"}), 502)
    if not isinstance(reply, str) or not reply.strip():
        return None, (jsonify({"error": "模型没有返回文本"}), 502)
    return reply.strip(), None


def mock_reply(data):
    delay = data.get("delay_seconds", 0)
    if delay:
        time.sleep(delay)
    if data.get("force_error", False):
        return None, (jsonify({"error": "模拟失败"}), 503)
    return MOCK_REPLY, None


def save_message(text, reply):
    global next_id
    with state_lock:
        record = {"id": next_id, "message": text, "reply": reply}
        next_id += 1
        messages.append(record)
        return dict(record)


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/style.css")
def style_css():
    return send_from_directory(FRONTEND_DIR, "style.css")


@app.get("/app.js")
def app_js():
    return send_from_directory(FRONTEND_DIR, "app.js")


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.get("/api/status")
def experiment_status():
    return jsonify(
        {
            "mode": CHAT_MODE,
            "external_model_calls": external_model_calls_enabled(),
        }
    )


@app.get("/metrics")
def metrics():
    encoder, content_type = choose_encoder(request.headers.get("Accept"))
    return Response(encoder(REGISTRY), content_type=content_type)


@app.post("/api/messages")
def create_message():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "message" not in data:
        return jsonify({"error": "缺少 message"}), 400
    text = data["message"]
    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "message 不能为空"}), 400
    text = text.strip()
    if CHAT_MODE == "mock":
        invalid = validate_mock_options(data)
        if invalid is not None:
            return invalid

    chat_inprogress_requests.inc()
    started = time.perf_counter()
    outcome = "error"
    try:
        if CHAT_MODE == "mock":
            reply, failure = mock_reply(data)
        else:
            reply, failure = request_reply(text)
        if failure is not None:
            return failure
        record = save_message(text, reply)
        outcome = "success"
        return jsonify(record), 201
    finally:
        chat_request_duration_seconds.observe(time.perf_counter() - started)
        chat_inprogress_requests.dec()
        chat_requests_total.labels(outcome=outcome).inc()


@app.get("/api/messages")
def list_messages():
    with state_lock:
        snapshot = [dict(item) for item in messages]
    return jsonify(snapshot)


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    text, error = read_message_text()
    if error is not None:
        return error
    with state_lock:
        record = find_message(message_id)
        if record is None:
            return jsonify({"error": "记录不存在", "id": message_id}), 404
        record["message"] = text
        return dict(record)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    with state_lock:
        record = find_message(message_id)
        if record is None:
            return jsonify({"error": "记录不存在", "id": message_id}), 404
        messages.remove(record)
        return dict(record)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, threaded=True, debug=False)
