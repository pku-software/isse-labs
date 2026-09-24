"""AI 聊天 Web 应用的后端服务。

同一个 Flask 服务同时承担两件事：

- 提供前端页面和静态资源（frontend/ 目录）
- 提供聊天记录的 RESTful API

聊天记录目前只保存在 Python 内存里，Flask 重启后会清空。
创建记录时由后端调用 DeepSeek API 生成真实回复，API Key 只从 .env 读取。
"""

import os

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# 从个人目录下的 .env 读取配置；文件不存在时不会报错，只是读不到变量
load_dotenv(os.path.join(BASE_DIR, ".env"))

# DeepSeek 官方 Chat Completions 接口（OpenAI 兼容格式）
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-flash"

# static_url_path 设为空字符串，frontend/ 目录中的文件就直接挂在根路径下，
# 例如 /style.css 和 /app.js，前端页面里的相对引用因此可以直接命中。
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")

# 让 JSON 响应中的中文直接显示，而不是转义成 \uXXXX
app.json.ensure_ascii = False

# 聊天记录存放在内存中，Flask 重启后数据会丢失
messages = []


@app.get("/")
def index():
    """返回前端页面。"""
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/api/hello")
def hello():
    """最简单的连通性接口。"""
    return jsonify({"message": "你好"})


# ---------------------------------------------------------------------------
# 聊天记录的 CRUD 接口
#
# 一条聊天记录的数据结构约定为：
#     {"id": 1, "message": "用户输入", "reply": "后端回复"}
# ---------------------------------------------------------------------------


def _read_message_field(data):
    """从请求体里取出并校验 message 字段。

    返回 (message, error_response)，两者中只有一个不是 None。
    """
    if not isinstance(data, dict):
        return None, (jsonify({"error": "请求体必须是一个 JSON 对象"}), 400)

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return None, (jsonify({"error": "message 字段缺失，或内容为空"}), 400)

    return message.strip(), None


def _next_id():
    """生成一个不与现有记录冲突的 id。"""
    return max((record["id"] for record in messages), default=0) + 1


def _request_model_reply(message):
    """调用 DeepSeek API，返回模型生成的回复文本。

    Key 从环境变量读取，不会出现在代码或日志里；
    任何失败都抛出 RuntimeError，由调用方转成清晰的 JSON 错误。
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("后端没有读取到 DEEPSEEK_API_KEY，请检查个人目录下的 .env 文件")

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [{"role": "user", "content": message}],
        "stream": False,
    }

    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            json=payload,
            timeout=60,
        )
    except requests.RequestException as error:
        raise RuntimeError(f"无法连接到 DeepSeek：{error}") from error

    if response.status_code != 200:
        detail = ""
        try:
            body = response.json()
            if isinstance(body, dict) and isinstance(body.get("error"), dict):
                detail = body["error"].get("message", "")
        except ValueError:
            detail = ""
        suffix = f"：{detail}" if detail else ""
        raise RuntimeError(f"DeepSeek 返回了错误状态 {response.status_code}{suffix}")

    try:
        reply = response.json()["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError) as error:
        raise RuntimeError("无法从 DeepSeek 的响应中解析出回复内容") from error

    if not isinstance(reply, str) or not reply.strip():
        raise RuntimeError("DeepSeek 返回了空回复")

    return reply


@app.post("/api/messages")
def create_message():
    """创建一条聊天记录，并调用 DeepSeek 生成回复。"""
    message, error = _read_message_field(request.get_json(silent=True))
    if error:
        return error

    try:
        reply = _request_model_reply(message)
    except RuntimeError as error:
        return jsonify({"error": str(error)}), 502

    record = {"id": _next_id(), "message": message, "reply": reply}
    messages.append(record)
    return jsonify(record), 201


@app.get("/api/messages")
def list_messages():
    """读取全部聊天记录。"""
    return jsonify(messages)


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    """修改指定 id 的聊天记录。"""
    message, error = _read_message_field(request.get_json(silent=True))
    if error:
        return error

    for record in messages:
        if record["id"] == message_id:
            record["message"] = message
            return jsonify(record)

    return jsonify({"error": f"id 为 {message_id} 的聊天记录不存在"}), 404


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    """删除指定 id 的聊天记录。"""
    for index, record in enumerate(messages):
        if record["id"] == message_id:
            messages.pop(index)
            return jsonify({"id": message_id, "deleted": True})

    return jsonify({"error": f"id 为 {message_id} 的聊天记录不存在"}), 404


if __name__ == "__main__":
    app.run(port=5001, debug=True)
