"""Chat page and JSON API with in-memory records."""

import os
from pathlib import Path
from itertools import count
from threading import Lock

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

load_dotenv(Path(__file__).resolve().parent / ".env")

app = Flask(__name__, static_folder="frontend", static_url_path="/static")
app.json.ensure_ascii = False

messages = []
message_ids = count(1)
messages_lock = Lock()


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api/hello")
def hello():
    return jsonify(message="你好")


def read_message():
    if not request.is_json:
        return None, (jsonify(error="请使用 application/json 发送请求"), 415)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, (jsonify(error="请求体必须是有效的 JSON 对象"), 400)
    text = data.get("message")
    if not isinstance(text, str) or not text.strip():
        return None, (jsonify(error="message 必须是非空字符串"), 400)
    return text.strip(), None


def deepseek_reply(text):
    api_key = (os.getenv("DEEPSEEK_API_KEY") or "").strip()
    if not api_key or api_key == "your_api_key_here":
        return None, (jsonify(error="后端尚未配置有效的 DEEPSEEK_API_KEY，请检查本地 .env 并重启 Flask"), 503)

    # Never return upstream response bodies or exception details: they may
    # contain credentials. Only the backend sends the authorization header.
    try:
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "deepseek-flash",
                "messages": [{"role": "user", "content": text}],
                "thinking": {"type": "disabled"},
                "stream": False,
                "max_tokens": 2048,
            },
            timeout=(10, 90),
            allow_redirects=False,
        )
    except requests.Timeout:
        return None, (jsonify(error="DeepSeek 请求超时，请稍后重试"), 504)
    except (requests.RequestException, UnicodeError, ValueError):
        return None, (jsonify(error="无法连接 DeepSeek，请检查后端网络和 Key 配置"), 502)

    with response:
        if response.status_code != 200:
            errors = {
                400: "DeepSeek 拒绝了请求，请检查模型调用参数",
                401: "DeepSeek 鉴权失败，请检查本地 API Key 后重启 Flask",
                402: "DeepSeek 账户余额不足，请检查账户余额",
                403: "DeepSeek 拒绝访问，请检查账户权限",
                429: "DeepSeek 请求过于频繁，请稍后重试",
            }
            error = errors.get(response.status_code, "DeepSeek 服务调用失败，请稍后重试")
            return None, (jsonify(error=error), 502)
        try:
            reply = response.json()["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError):
            return None, (jsonify(error="DeepSeek 返回的数据格式异常，请稍后重试"), 502)
        if not isinstance(reply, str) or not reply.strip():
            return None, (jsonify(error="DeepSeek 未返回有效文本，请稍后重试"), 502)
        return reply.strip().replace(api_key, "[已隐藏敏感信息]"), None

@app.post("/api/messages")
def create_message():
    text, error = read_message()
    if error is not None:
        return error
    reply, error = deepseek_reply(text)
    if error is not None:
        return error
    with messages_lock:
        record = {"id": next(message_ids), "message": text, "reply": reply}
        messages.append(record)
        return jsonify(record), 201


@app.get("/api/messages")
def list_messages():
    with messages_lock:
        return jsonify(messages)


@app.patch("/api/messages/<int:id>")
def update_message(id):
    text, error = read_message()
    if error is not None:
        return error
    with messages_lock:
        for record in messages:
            if record["id"] == id:
                record["message"] = text
                return jsonify(record)
    return jsonify(error="聊天记录不存在，请刷新记录列表"), 404


@app.delete("/api/messages/<int:id>")
def delete_message(id):
    with messages_lock:
        for position, record in enumerate(messages):
            if record["id"] == id:
                del messages[position]
                return jsonify(id=id, deleted=True)
    return jsonify(error="聊天记录不存在，请刷新记录列表"), 404


@app.errorhandler(HTTPException)
def http_error(error):
    return jsonify(error=error.description), error.code


if __name__ == "__main__":
    app.run(port=5001, debug=True)
