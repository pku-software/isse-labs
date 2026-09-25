"""通过 Flask 调用 DeepSeek，并在进程内存中保存问答记录。"""

import os
from itertools import count
from pathlib import Path
from threading import Lock

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

app = Flask(__name__, static_folder="frontend", static_url_path="/static")
app.json.ensure_ascii = False

# 由后端加载同目录配置，不向前端提供配置文件或变量值。
load_dotenv(Path(__file__).with_name(".env"), interpolate=False)

DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-flash"

# 记录只属于当前进程，重启后会清空。
messages = []
message_ids = count(1)
messages_lock = Lock()


class DeepSeekError(Exception):
    """只携带可以展示给用户的错误说明与 HTTP 状态码。"""

    def __init__(self, message, status_code):
        super().__init__(message)
        self.status_code = status_code


def generate_reply(message):
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key or api_key == "your_api_key_here":
        raise DeepSeekError("后端未配置 API Key，请检查本地 .env 后重启 Flask。", 503)
    if not api_key.isascii() or any(char.isspace() for char in api_key):
        raise DeepSeekError("API Key 格式不正确，请在本地检查配置后重启 Flask。", 503)

    try:
        with requests.post(
            DEEPSEEK_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": DEEPSEEK_MODEL,
                "messages": [{"role": "user", "content": message}],
                "thinking": {"type": "disabled"},
                "stream": False,
            },
            timeout=(10, 90),
            allow_redirects=False,
        ) as response:
            if response.status_code != 200:
                # 不转发第三方响应正文或异常原文，避免暴露请求配置。
                errors = {
                    400: ("DeepSeek 请求格式有误，请检查后端调用参数。", 502),
                    401: ("DeepSeek 身份验证失败，请在本地检查 Key 后重启 Flask。", 502),
                    402: ("DeepSeek 账户余额不足，请在开放平台检查账户。", 502),
                    422: ("DeepSeek 请求参数有误，请检查模型与调用参数。", 502),
                    429: ("DeepSeek 请求频率超限，请稍后重试。", 503),
                    500: ("DeepSeek 服务暂时出错，请稍后重试。", 502),
                    503: ("DeepSeek 服务繁忙，请稍后重试。", 503),
                }
                detail, status_code = errors.get(
                    response.status_code,
                    ("DeepSeek 调用失败，请稍后重试或检查后端配置。", 502),
                )
                raise DeepSeekError(detail, status_code)
            try:
                data = response.json()
                reply = data["choices"][0]["message"]["content"]
            except (ValueError, KeyError, IndexError, TypeError):
                raise DeepSeekError("DeepSeek 返回的内容格式异常，请稍后重试。", 502) from None
            if not isinstance(reply, str) or not reply.strip():
                raise DeepSeekError("DeepSeek 未返回有效回复，请稍后重试。", 502)
            return reply.strip()
    except requests.Timeout:
        raise DeepSeekError("等待 DeepSeek 回复超时，请稍后重试。", 504) from None
    except requests.RequestException:
        raise DeepSeekError("无法连接 DeepSeek，请检查网络后重试。", 502) from None


def read_message():
    """只接受包含非空字符串 message 的 JSON 对象。"""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None
    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return None
    return message.strip()


@app.errorhandler(HTTPException)
def http_error(error):
    response = error.get_response()
    response.data = app.json.dumps({"error": error.description})
    response.content_type = "application/json"
    return response


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api/hello")
def hello():
    return jsonify(message="你好")


@app.post("/api/messages")
def create_message():
    message = read_message()
    if message is None:
        return jsonify(error="请提交 JSON 对象，message 必须是非空字符串。"), 400
    # 网络调用不持有数据锁，等待模型时仍可查看、修改和删除已有记录。
    try:
        reply = generate_reply(message)
    except DeepSeekError as error:
        return jsonify(error=str(error)), error.status_code
    with messages_lock:
        record = {"id": next(message_ids), "message": message, "reply": reply}
        messages.append(record)
        return jsonify(record), 201


@app.get("/api/messages")
def list_messages():
    with messages_lock:
        return jsonify(messages)


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    message = read_message()
    if message is None:
        return jsonify(error="请提交 JSON 对象，message 必须是非空字符串。"), 400
    with messages_lock:
        for record in messages:
            if record["id"] == message_id:
                record["message"] = message
                return jsonify(record)
    return jsonify(error="聊天记录不存在，请重新加载记录。"), 404


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    with messages_lock:
        for index, record in enumerate(messages):
            if record["id"] == message_id:
                messages.pop(index)
                return jsonify(id=message_id, message="问答已删除。")
    return jsonify(error="聊天记录不存在，请重新加载记录。"), 404


if __name__ == "__main__":
    app.run(port=5001, debug=True)
