import os
import math
import time
from threading import Lock

from flask import Flask, Response, jsonify, request, send_from_directory
from openai import APIConnectionError, APIStatusError, AuthenticationError, OpenAI, RateLimitError
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from metrics import chat_requests, chat_inprogress, chat_duration


app = Flask(__name__, static_folder="frontend")
app.json.ensure_ascii = False
app.config["CHAT_MODE"] = os.getenv("CHAT_MODE", "mock")
if app.config["CHAT_MODE"] not in ("mock", "real"):
    raise ValueError("CHAT_MODE 必须为 mock 或 real")
messages = []
next_message_id = 1
messages_lock = Lock()


def message_from_request():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, (jsonify(error="请求体必须是 JSON 对象"), 400)

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return None, (jsonify(error="message 必须是非空字符串"), 400)

    return message.strip(), None


def find_message(message_id):
    return next((item for item in messages if item["id"] == message_id), None)


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/<path:filename>")
def frontend_file(filename):
    return send_from_directory(app.static_folder, filename)


@app.get("/api/hello")
def hello():
    return jsonify(message="你好")


@app.post("/api/messages")
def create_message():
    started = time.perf_counter()
    outcome = "error"
    chat_inprogress.inc()
    try:
        response = app.make_response(process_message())
        if response.status_code == 201:
            outcome = "success"
        return response
    finally:
        chat_duration.observe(time.perf_counter() - started)
        chat_requests.labels(outcome=outcome).inc()
        chat_inprogress.dec()


def process_message():
    global next_message_id

    message, error = message_from_request()
    if error:
        return error

    if app.config["CHAT_MODE"] == "mock":
        data = request.get_json()
        delay = data.get("mock_delay", 0.1)
        force_error = data.get("mock_error", False)
        if (
            isinstance(delay, bool)
            or not isinstance(delay, (int, float))
            or not math.isfinite(delay)
            or not 0 <= delay <= 10
            or not isinstance(force_error, bool)
        ):
            return jsonify(error="mock_delay 必须为 0～10 秒的数值，mock_error 必须为布尔值"), 400
        time.sleep(delay)
        if force_error:
            return jsonify(error="实验模拟错误"), 503
        reply = "你好"
    else:
        reply, error = real_reply(message)
        if error:
            return error

    with messages_lock:
        record = {"id": next_message_id, "message": message, "reply": reply}
        messages.append(record)
        next_message_id += 1
        return jsonify(record), 201


def real_reply(message):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return None, (jsonify(error="未配置 DEEPSEEK_API_KEY"), 503)

    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        completion = client.chat.completions.create(
            model="deepseek-flash",
            messages=[{"role": "user", "content": message}],
        )
        reply = completion.choices[0].message.content
        if not reply:
            return None, (jsonify(error="DeepSeek 未返回可用回复"), 502)
    except AuthenticationError:
        return None, (jsonify(error="DeepSeek API Key 无效或没有调用权限"), 502)
    except RateLimitError:
        return None, (jsonify(error="DeepSeek API 请求受限，请检查账户余额或稍后重试"), 429)
    except APIConnectionError:
        return None, (jsonify(error="无法连接 DeepSeek API，请检查网络连接"), 502)
    except APIStatusError as error:
        return None, (jsonify(error=f"DeepSeek API 返回错误状态：{error.status_code}"), 502)
    except Exception:
        return None, (jsonify(error="调用 DeepSeek API 时发生未知错误"), 502)

    return reply, None


@app.get("/api/lab-status")
def lab_status():
    if app.config["CHAT_MODE"] != "mock":
        return jsonify(error="实验状态接口仅在 mock 模式开放"), 404
    return jsonify(mode=app.config["CHAT_MODE"], external_model_calls=False)


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), content_type=CONTENT_TYPE_LATEST)


@app.get("/api/messages")
def list_messages():
    with messages_lock:
        return jsonify(messages)


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    with messages_lock:
        record = find_message(message_id)
        if record is None:
            return jsonify(error="未找到该聊天记录"), 404
        message, error = message_from_request()
        if error:
            return error
        record["message"] = message
        return jsonify(record)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    with messages_lock:
        record = find_message(message_id)
        if record is None:
            return jsonify(error="未找到该聊天记录"), 404
        messages.remove(record)
    return "", 204


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5001")), threaded=True, debug=False)
