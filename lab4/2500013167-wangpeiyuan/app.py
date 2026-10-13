"""Lab 4 聊天应用：默认本地 mock，记录聊天请求指标。

同一个 Flask 进程负责两件事：

- 把 ``frontend/`` 目录里的页面和静态资源交给浏览器；
- 提供聊天记录接口，mock 返回测试回复，real 可调用 DeepSeek。

聊天记录仍然只放在内存里，Flask 一重启就清空。
DeepSeek 的 API Key 在运行时从环境变量读取，不会出现在源码里。
"""

import os
import math
import threading
import time
from pathlib import Path

import requests
from flask import Flask, Response, jsonify, request, send_from_directory
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from metrics import CHAT_REQUESTS, CHAT_INPROGRESS, CHAT_DURATION

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

# ECI 在容器运行时注入环境变量；镜像不包含 .env 或真实 Key。

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-flash"
MODEL_MODE = os.getenv("MODEL_MODE", "mock").lower()
if MODEL_MODE not in ("mock", "real"):
    raise ValueError("MODEL_MODE must be mock or real")
messages_lock = threading.RLock()

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="/static")
# 让 jsonify 直接输出中文，而不是 \uXXXX 转义
app.json.ensure_ascii = False

# 内存中的聊天记录，形如 {"id": 1, "message": "用户输入", "reply": "AI 回复"}
messages: list[dict] = []
next_id = 1


def ask_deepseek(api_key: str, message: str) -> str:
    """把用户消息发给 DeepSeek，返回模型回复的文本。

    HTTP 层出错时抛出 RuntimeError，由路由转成 JSON 错误返回给前端。
    """
    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            json={
                "model": DEEPSEEK_MODEL,
                "messages": [{"role": "user", "content": message}],
                "stream": False,
            },
            timeout=60,
        )
    except requests.RequestException as error:
        raise RuntimeError("无法连接 DeepSeek，请稍后重试") from error

    if response.status_code != 200:
        raise RuntimeError(f"DeepSeek 返回了 HTTP {response.status_code}")

    try:
        reply = response.json()["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError) as error:
        raise RuntimeError("DeepSeek 的响应无法解析") from error

    return reply


@app.route("/", methods=["GET"])
def index():
    """把前端首页交给浏览器。"""
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/api/hello", methods=["GET"])
def hello():
    """最简单的连通性检查接口。"""
    return jsonify({"message": "你好"})


@app.route("/api/messages", methods=["POST"])
def create_message():
    started = time.perf_counter()
    CHAT_INPROGRESS.inc()
    outcome = "error"
    try:
        response, status = process_message()
        if 200 <= status < 300:
            outcome = "success"
        return response, status
    finally:
        CHAT_REQUESTS.labels(outcome=outcome).inc()
        CHAT_DURATION.observe(time.perf_counter() - started)
        CHAT_INPROGRESS.dec()


def process_message():
    """新建一条聊天记录：把用户消息交给 DeepSeek，存下这一问一答。"""
    global next_id

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not str(data.get("message", "")).strip():
        return jsonify({"error": "请求体需要包含非空的 message 字段"}), 400

    message = str(data["message"]).strip()
    if MODEL_MODE == "mock":
        delay = data.get("mock_delay_seconds", 0.1)
        force_error = data.get("mock_force_error", False)
        if (isinstance(delay, bool) or not isinstance(delay, (int, float))
                or not math.isfinite(delay) or not 0 <= delay <= 30
                or not isinstance(force_error, bool)):
            return jsonify({"error": "模拟延迟须为 0～30 秒，失败选项须为布尔值"}), 400
        time.sleep(delay)
        if force_error:
            return jsonify({"error": "实验模拟失败", "simulated": True}), 503
        reply = "这是本地 mock 测试回复，未调用外部模型。"
    else:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            return jsonify({"error": "服务端未配置 DEEPSEEK_API_KEY"}), 500
        try:
            reply = ask_deepseek(api_key, message)
        except RuntimeError as error:
            return jsonify({"error": str(error)}), 502

    with messages_lock:
        record = {"id": next_id, "message": message, "reply": reply}
        next_id += 1
        messages.append(record)
    return jsonify(record), 201


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), content_type=CONTENT_TYPE_LATEST)


@app.get("/api/lab-status")
def lab_status():
    if MODEL_MODE != "mock":
        return jsonify({"error": "实验状态接口仅在 mock 模式可用"}), 404
    return jsonify({"mode": MODEL_MODE, "external_model_calls": False})


@app.route("/api/messages", methods=["GET"])
def list_messages():
    """返回内存中的全部聊天记录。"""
    with messages_lock:
        return jsonify(messages), 200


@app.route("/api/messages/<int:message_id>", methods=["PATCH"])
def update_message(message_id: int):
    """修改指定记录的 message 内容。"""
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not str(data.get("message", "")).strip():
        return jsonify({"error": "请求体需要包含非空的 message 字段"}), 400

    with messages_lock:
        record = find_message(message_id)
        if record is None:
            return jsonify({"error": f"id={message_id} 的聊天记录不存在"}), 404
        record["message"] = str(data["message"]).strip()
        return jsonify(record), 200


@app.route("/api/messages/<int:message_id>", methods=["DELETE"])
def delete_message(message_id: int):
    """删除指定记录。"""
    with messages_lock:
        record = find_message(message_id)
        if record is None:
            return jsonify({"error": f"id={message_id} 的聊天记录不存在"}), 404
        messages.remove(record)
        return jsonify({"id": message_id, "deleted": True}), 200


def find_message(message_id: int):
    """按 id 在内存列表里查找记录，找不到返回 None。"""
    for record in messages:
        if record["id"] == message_id:
            return record
    return None


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("APP_PORT", "5001")),
            debug=False, threaded=True, use_reloader=False)
