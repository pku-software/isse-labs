import os

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# 从个人目录下的 .env 读取配置；Key 只在后端进程内使用，不会发给浏览器。
load_dotenv(os.path.join(BASE_DIR, ".env"))

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_TIMEOUT = 60

app = Flask(__name__)
app.json.ensure_ascii = False

# 聊天记录暂存在内存中，Flask 重启后会被清空。
messages = []


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
    return jsonify(messages)


@app.post("/api/messages")
def create_message():
    text = read_message_text()
    if text is None:
        return jsonify({"error": "请求体需要是 JSON，且 message 必须是非空字符串"}), 400

    try:
        reply = ask_deepseek(text)
    except DeepSeekError as error:
        return jsonify({"error": str(error)}), 502

    record = {"id": next_message_id(), "message": text, "reply": reply}
    messages.append(record)
    return jsonify(record), 201


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
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
    record = find_message(message_id)
    if record is None:
        return jsonify({"error": f"找不到 id 为 {message_id} 的聊天记录"}), 404

    messages.remove(record)
    return jsonify(record)


if __name__ == "__main__":
    app.run(port=5001, debug=True)
