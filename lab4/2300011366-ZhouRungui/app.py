import math
import os
import threading
import time
from itertools import count

import requests
from flask import Flask, Response, jsonify, request, send_from_directory
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from metrics import CHAT_IN_PROGRESS, CHAT_REQUEST_DURATION, CHAT_REQUESTS


CHAT_MODE = os.getenv("CHAT_MODE", "mock").strip().lower()
if CHAT_MODE not in {"mock", "real"}:
    raise RuntimeError("CHAT_MODE 必须是 mock 或 real")

MAX_MOCK_DELAY_SECONDS = 10.0
MOCK_REPLY = "这是 Lab 4 的模拟回复，没有调用外部模型。"

app = Flask(__name__, static_folder="frontend", static_url_path="")
app.json.ensure_ascii = False
messages = []
message_ids = count(1)
messages_lock = threading.Lock()


def real_model_reply(message):
    """调用原有 DeepSeek 接口，返回 (reply, error)；error 为 (文案, 状态码)。"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return None, ("服务器尚未配置 DeepSeek API Key", 503)

    try:
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
            json={
                "model": "deepseek-flash",
                "messages": [{"role": "user", "content": message}],
                "thinking": {"type": "disabled"},
                "stream": False,
            },
            timeout=60,
        )
        response.raise_for_status()
    except requests.HTTPError:
        return None, ("DeepSeek API 请求失败，请检查 Key 或稍后重试", 502)
    except requests.RequestException:
        return None, ("暂时无法连接 DeepSeek API，请稍后重试", 502)

    try:
        result = response.json()
    except ValueError:
        return None, ("DeepSeek API 返回了非 JSON 数据", 502)

    if not isinstance(result, dict):
        return None, ("DeepSeek API 返回的 JSON 格式不正确", 502)
    if "error" in result:
        return None, ("DeepSeek API 返回了错误信息，请检查账号和 Key 状态", 502)

    choices = result.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        return None, ("DeepSeek API 回复中缺少 choices", 502)

    choice = choices[0]
    model_message = choice.get("message")
    if not isinstance(model_message, dict):
        return None, ("DeepSeek API 回复中缺少 message", 502)

    reply = model_message.get("content")
    if not isinstance(reply, str) or not reply.strip():
        reason = choice.get("finish_reason")
        if reason in {"length", "content_filter", "insufficient_system_resource", "aborted"}:
            return None, (f"DeepSeek 未生成文本，结束原因：{reason}", 502)
        return None, ("DeepSeek API 回复文本为空", 502)

    return reply.strip(), None


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.get("/api/lab4/status")
def lab4_status():
    return jsonify(
        {
            "mode": CHAT_MODE,
            "external_model_calls": CHAT_MODE == "real",
        }
    )


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.post("/api/messages")
def create_message():
    started_at = time.perf_counter()
    outcome = "error"
    CHAT_IN_PROGRESS.inc()

    try:
        data = request.get_json(silent=True)
        message = data.get("message") if isinstance(data, dict) else None
        if not isinstance(message, str) or not message.strip():
            return jsonify({"error": "message 必须是非空字符串"}), 400
        message = message.strip()

        if CHAT_MODE == "mock":
            delay_seconds = data.get("delay_seconds", 0)
            force_error = data.get("force_error", False)
            if (
                isinstance(delay_seconds, bool)
                or not isinstance(delay_seconds, (int, float))
                or not math.isfinite(delay_seconds)
                or not 0 <= delay_seconds <= MAX_MOCK_DELAY_SECONDS
            ):
                return jsonify({"error": "delay_seconds 必须在 0 到 10 秒之间"}), 400
            if not isinstance(force_error, bool):
                return jsonify({"error": "force_error 必须是布尔值"}), 400

            if delay_seconds:
                time.sleep(delay_seconds)
            if force_error:
                return jsonify({"error": "模拟模型错误"}), 503
            reply = MOCK_REPLY
        else:
            # Real mode deliberately ignores Lab 4-only delay/error fields.
            reply, error = real_model_reply(message)
            if error is not None:
                error_message, status_code = error
                return jsonify({"error": error_message}), status_code

        with messages_lock:
            record = {"id": next(message_ids), "message": message, "reply": reply}
            messages.append(record)

        outcome = "success"
        return jsonify(record), 201
    finally:
        CHAT_REQUESTS.labels(outcome=outcome).inc()
        CHAT_REQUEST_DURATION.observe(time.perf_counter() - started_at)
        CHAT_IN_PROGRESS.dec()


@app.get("/api/messages")
def list_messages():
    with messages_lock:
        return jsonify(messages)


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    data = request.get_json(silent=True)
    message = data.get("message") if isinstance(data, dict) else None
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "message 必须是非空字符串"}), 400

    with messages_lock:
        record = next((item for item in messages if item["id"] == message_id), None)
        if record is None:
            return jsonify({"error": "聊天记录不存在"}), 404
        record["message"] = message.strip()
        result = record.copy()
    return jsonify(result)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    with messages_lock:
        record = next((item for item in messages if item["id"] == message_id), None)
        if record is None:
            return jsonify({"error": "聊天记录不存在"}), 404
        messages.remove(record)
    return "", 204


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False, threaded=True)
