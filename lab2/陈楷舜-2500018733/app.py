"""通过 DeepSeek 回复问题，并在内存中管理聊天记录。"""

import os
from itertools import count
from pathlib import Path
from threading import Lock

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from werkzeug.exceptions import (
    BadGateway,
    BadRequest,
    GatewayTimeout,
    HTTPException,
    NotFound,
    ServiceUnavailable,
    UnsupportedMediaType,
)


# 由后端进程读取本项目的配置，兼容 Windows 编辑器保存的 UTF-8 BOM。
# 不将密钥写入响应或日志；启动目录改变时仍能找到同一个 .env。
load_dotenv(Path(__file__).resolve().with_name(".env"), encoding="utf-8-sig")

# 将 frontend 中的文件映射到根路径，供 HTML 中的相对资源地址使用。
app = Flask(__name__, static_folder="frontend", static_url_path="")
app.json.ensure_ascii = False

messages = {}
message_ids = count(1)
messages_lock = Lock()
MAX_MESSAGE_LENGTH = 4000
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-flash"


def read_message():
    """校验 JSON 请求中的 message，并去掉首尾空白。"""
    if not request.is_json:
        raise UnsupportedMediaType("请使用 application/json 格式发送请求")
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise BadRequest("请求内容必须是有效的 JSON 对象")
    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        raise BadRequest("message 必须是非空字符串")
    message = message.strip()
    if len(message) > MAX_MESSAGE_LENGTH:
        raise BadRequest(f"消息不能超过 {MAX_MESSAGE_LENGTH} 个字符")
    return message


def get_ai_reply(message):
    """调用 DeepSeek，只返回回答文本，不向浏览器转发上游原始响应。"""
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key or api_key == "your_api_key_here":
        raise ServiceUnavailable("后端尚未配置 DeepSeek API Key，请配置 .env 并重启服务")
    if not api_key.isascii() or any(char.isspace() for char in api_key):
        raise ServiceUnavailable("DeepSeek API Key 格式不正确，请检查本地配置并重启服务")

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [{"role": "user", "content": message}],
        "thinking": {"type": "disabled"},
        "stream": False,
        "max_tokens": 2048,
    }
    try:
        with requests.post(
            DEEPSEEK_API_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload,
            timeout=(10, 60),
            allow_redirects=False,
        ) as response:
            if response.status_code in (401, 403):
                raise ServiceUnavailable("DeepSeek 身份验证失败，请检查后端 API Key 或账户权限")
            if response.status_code == 402:
                raise ServiceUnavailable("DeepSeek 账户余额不足，请在开放平台检查余额")
            if response.status_code == 429:
                raise ServiceUnavailable("DeepSeek 请求过于频繁，请稍后重试")
            if response.status_code != 200:
                raise BadGateway(f"DeepSeek 调用失败（HTTP {response.status_code}），请稍后重试")

            try:
                result = response.json()
                reply = result["choices"][0]["message"]["content"]
            except (ValueError, KeyError, IndexError, TypeError):
                raise BadGateway("DeepSeek 返回的数据格式异常，请稍后重试") from None
    except requests.Timeout:
        raise GatewayTimeout("等待 DeepSeek 回复超时，请稍后重试；本次未保存聊天记录") from None
    except requests.RequestException:
        # 不返回异常原文，避免其中携带请求头或其他敏感信息。
        raise BadGateway("无法连接 DeepSeek 服务，请检查网络后重试") from None

    if not isinstance(reply, str) or not reply.strip():
        raise BadGateway("DeepSeek 未返回有效的回答文本，请稍后重试")
    return reply.strip()


@app.errorhandler(HTTPException)
def handle_http_error(error):
    if request.path.startswith("/api/"):
        return jsonify({"error": error.description}), error.code
    return error


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.post("/api/messages")
def create_message():
    message = read_message()
    # 网络调用在锁外完成，不阻塞其他客户端查看或修改已有记录。
    reply = get_ai_reply(message)
    with messages_lock:
        record = {"id": next(message_ids), "message": message, "reply": reply}
        messages[record["id"]] = record
        return jsonify(record), 201


@app.get("/api/messages")
def list_messages():
    with messages_lock:
        return jsonify(list(messages.values()))


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    message = read_message()
    with messages_lock:
        record = messages.get(message_id)
        if record is None:
            raise NotFound("找不到这条聊天记录，请刷新列表后重试")
        record["message"] = message
        return jsonify(record)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    with messages_lock:
        if messages.pop(message_id, None) is None:
            raise NotFound("找不到这条聊天记录，请刷新列表后重试")
    return "", 204


if __name__ == "__main__":
    app.run(port=5001, debug=True)
