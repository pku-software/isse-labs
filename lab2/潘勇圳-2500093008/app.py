"""AI 聊天 Web 应用的后端。

当前阶段 Flask 同时提供前端页面和后端 API：

- 访问 ``GET /`` 返回 ``frontend/index.html``，样式和脚本也由 Flask 提供；
- ``GET /api/hello`` 用来确认服务是否正常运行；
- 聊天记录通过 ``/api/messages`` 完成创建、读取、修改和删除；
- 聊天记录同时保存在内存和 data/messages.json 里，Flask 启动时会先读回这个文件，
  所以重启之后记录依然存在（不使用数据库）；
- 回复由 Flask 调用 DeepSeek API 生成，API Key 只保存在本机的 .env 里。

一条聊天记录约定为：``{"id": 1, "message": "用户输入", "reply": "后端回复"}``
"""

import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
DATA_DIR = BASE_DIR / "data"
MESSAGES_FILE = DATA_DIR / "messages.json"

# 读取项目根目录下的 .env，把里面的键值对放进环境变量，
# 这样代码里只出现变量名，真实 Key 一直留在 .env 文件中
load_dotenv(BASE_DIR / ".env")

# DeepSeek 的接口地址和模型名，参考官方文档：https://api-docs.deepseek.com/zh-cn/
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# 静态资源（style.css、app.js）由 Flask 从 frontend/ 目录提供，
# static_url_path="" 表示它们挂在网站根路径下，例如 /style.css
app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")

# 让 JSON 响应里的中文直接显示，而不是转义成 \uXXXX
app.json.ensure_ascii = False

# 聊天记录在内存里保存一份，每次改动后同步写回 messages.json
messages = []
next_message_id = 1


@app.get("/api/hello")
def hello():
    """最简单的接口，用于确认后端已经正常运行。"""
    return jsonify({"message": "你好"})


@app.get("/")
def index():
    """返回前端页面，这样浏览器访问 http://localhost:5001/ 就能打开它。"""
    return send_from_directory(FRONTEND_DIR, "index.html")


def find_message(message_id):
    """按 id 查找聊天记录，找不到时返回 None。"""
    for record in messages:
        if record["id"] == message_id:
            return record
    return None


def read_message_text():
    """从请求体里取出 message 字段，并做一次非空校验。"""
    data = request.get_json(silent=True) or {}
    text = data.get("message")
    if not isinstance(text, str) or not text.strip():
        return None
    return text.strip()


def load_messages():
    """把 data/messages.json 里保存的记录读回内存，供 Flask 启动时调用。"""
    global messages, next_message_id

    if not MESSAGES_FILE.exists():
        return

    try:
        with MESSAGES_FILE.open(encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        # 文件读不了或内容不是合法 JSON 时，从空记录开始，不让服务起不来
        return

    if not isinstance(data, list):
        return

    messages = [
        record
        for record in data
        if isinstance(record, dict)
        and isinstance(record.get("id"), int)
        and isinstance(record.get("message"), str)
        and isinstance(record.get("reply"), str)
    ]

    # 新 id 从已有记录的最大 id 往后接，避免和文件里的记录冲突
    next_message_id = max((record["id"] for record in messages), default=0) + 1


def save_messages():
    """把当前内存里的记录写回 data/messages.json。"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with MESSAGES_FILE.open("w", encoding="utf-8") as file:
        json.dump(messages, file, ensure_ascii=False, indent=2)


# 启动时先把上次保存的记录读回内存
load_messages()


def ask_deepseek(message):
    """把用户消息发给 DeepSeek，返回模型生成的回复文本。

    任何一步出错都抛出 RuntimeError，由调用方转成 JSON 错误响应，
    避免异常直接把 Flask 进程打挂。
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError(
            "后端没有读到 DEEPSEEK_API_KEY，请检查项目根目录下的 .env 文件是否存在且内容正确"
        )

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [{"role": "user", "content": message}],
        "stream": False,
    }

    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=60,
        )
    except requests.RequestException as error:
        raise RuntimeError(f"连接 DeepSeek 失败：{error}") from error

    if response.status_code != 200:
        raise RuntimeError(
            f"DeepSeek 返回错误（HTTP {response.status_code}）：{response.text[:200]}"
        )

    data = response.json()
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as error:
        raise RuntimeError("DeepSeek 返回的数据格式与预期不一致") from error


@app.post("/api/messages")
def create_message():
    """创建一条聊天记录，回复由 DeepSeek 生成。"""
    global next_message_id

    text = read_message_text()
    if text is None:
        return jsonify({"error": "请求体需要是 JSON，并且 message 字段不能为空"}), 400

    try:
        reply = ask_deepseek(text)
    except RuntimeError as error:
        # 调用失败时不写入记录，把失败原因返回给前端显示
        return jsonify({"error": str(error)}), 502

    record = {"id": next_message_id, "message": text, "reply": reply}
    messages.append(record)
    next_message_id += 1
    save_messages()
    return jsonify(record), 201


@app.get("/api/messages")
def list_messages():
    """返回全部聊天记录。"""
    return jsonify(messages)


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    """修改指定聊天记录的用户消息内容。"""
    record = find_message(message_id)
    if record is None:
        return jsonify({"error": f"id 为 {message_id} 的聊天记录不存在"}), 404

    text = read_message_text()
    if text is None:
        return jsonify({"error": "请求体需要是 JSON，并且 message 字段不能为空"}), 400

    record["message"] = text
    save_messages()
    return jsonify(record)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    """删除指定聊天记录。"""
    record = find_message(message_id)
    if record is None:
        return jsonify({"error": f"id 为 {message_id} 的聊天记录不存在"}), 404

    messages.remove(record)
    save_messages()
    return jsonify({"deleted_id": message_id})


if __name__ == "__main__":
    # 使用 5001 端口，避免与其它本地服务冲突
    app.run(port=5001, debug=True)
