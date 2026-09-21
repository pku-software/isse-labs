"""Lab 2 AI 聊天 Web 应用 —— Flask 后端入口。

同一个 Flask 进程负责两件事：

- 把 ``frontend/`` 目录里的页面和静态资源交给浏览器；
- 提供聊天记录接口，新建记录时调用 DeepSeek 生成回复。

聊天记录仍然只放在内存里，Flask 一重启就清空。
DeepSeek 的 API Key 从同目录的 ``.env`` 读取，不会出现在源码里。
"""

import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

# 把 .env 里的键值读进环境变量，后面用 os.getenv 取用
load_dotenv(BASE_DIR / ".env")

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-flash"

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
        raise RuntimeError(f"无法连接 DeepSeek：{error}") from error

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
    """新建一条聊天记录：把用户消息交给 DeepSeek，存下这一问一答。"""
    global next_id

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not str(data.get("message", "")).strip():
        return jsonify({"error": "请求体需要包含非空的 message 字段"}), 400

    # Key 只在后端读取，不出现在响应、日志或页面里
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return jsonify({"error": "服务端没有读到 DEEPSEEK_API_KEY，请检查 .env 文件"}), 500

    message = str(data["message"]).strip()
    try:
        reply = ask_deepseek(api_key, message)
    except RuntimeError as error:
        return jsonify({"error": str(error)}), 502

    record = {"id": next_id, "message": message, "reply": reply}
    next_id += 1
    messages.append(record)
    return jsonify(record), 201


@app.route("/api/messages", methods=["GET"])
def list_messages():
    """返回内存中的全部聊天记录。"""
    return jsonify(messages), 200


@app.route("/api/messages/<int:message_id>", methods=["PATCH"])
def update_message(message_id: int):
    """修改指定记录的 message 内容。"""
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not str(data.get("message", "")).strip():
        return jsonify({"error": "请求体需要包含非空的 message 字段"}), 400

    record = find_message(message_id)
    if record is None:
        return jsonify({"error": f"id={message_id} 的聊天记录不存在"}), 404

    record["message"] = str(data["message"]).strip()
    return jsonify(record), 200


@app.route("/api/messages/<int:message_id>", methods=["DELETE"])
def delete_message(message_id: int):
    """删除指定记录。"""
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
    app.run(host="127.0.0.1", port=5001, debug=True)
