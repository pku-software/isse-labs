"""AI 聊天 Web 应用的后端。

Flask 同时承担两件事：
1. 提供前端页面和静态资源（`/`、`/style.css`、`/app.js`）；
2. 提供聊天记录相关的 JSON API（`/api/...`）。

创建聊天记录时，后端会去调用 DeepSeek 的接口拿真实回复。
API Key 只保存在后端的 .env 文件里，通过环境变量读取，不会出现在前端代码中。

聊天记录目前只保存在内存列表里，Flask 一重启数据就没了。
"""

import os

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

# 把 .env 里的变量读进当前进程的环境变量。
# 文件不存在时它只是什么都不做，不会报错。
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# DeepSeek 的接口地址与模型名，来自官方文档。
# 如果官方文档更新了接口地址或模型名，只需要改这两行。
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_TIMEOUT = 60

app = Flask(__name__)

# 让 JSON 响应中的中文直接以中文输出，而不是被转义成 \uXXXX
app.json.ensure_ascii = False

# 聊天记录保存在内存里，一条记录形如
# {"id": 1, "message": "用户输入", "reply": "后端回复"}
messages = []

# 下一条记录的 id。只增不减，保证删除记录后 id 也不会重复使用。
next_message_id = 1


def find_message(message_id):
    """按 id 查找记录，找不到返回 None。"""
    for record in messages:
        if record["id"] == message_id:
            return record
    return None


def describe_deepseek_error(response):
    """从 DeepSeek 的错误响应里取出一句可读的说明，取不到就退回状态码。"""
    try:
        body = response.json()
    except ValueError:
        text = (response.text or "").strip()
        return text[:300] if text else f"HTTP {response.status_code}"

    if isinstance(body, dict):
        error = body.get("error")
        if isinstance(error, dict) and error.get("message"):
            return str(error["message"])[:300]
        if isinstance(error, str) and error:
            return error[:300]

    return f"HTTP {response.status_code}"


def ask_deepseek(question):
    """把用户的问题发给 DeepSeek，返回模型回复的文本。

    出错时抛出 RuntimeError，由调用方转成 JSON 错误响应。
    API Key 通过请求头传给 DeepSeek，不会出现在前端代码或响应里。
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("服务端没有读到 DEEPSEEK_API_KEY，请先按 .env.example 配置 .env")

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "user", "content": question},
        ],
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
            timeout=DEEPSEEK_TIMEOUT,
        )
    except requests.RequestException as error:
        raise RuntimeError(f"无法连接 DeepSeek：{error}") from error

    if response.status_code != 200:
        raise RuntimeError(
            f"DeepSeek 返回错误（HTTP {response.status_code}）：{describe_deepseek_error(response)}"
        )

    try:
        return response.json()["choices"][0]["message"]["content"].strip()
    except (ValueError, KeyError, IndexError, TypeError, AttributeError) as error:
        raise RuntimeError("DeepSeek 的返回内容无法解析") from error


# ---------------------------------------------------------------------------
# 前端页面与静态资源
# ---------------------------------------------------------------------------


@app.get("/")
def serve_index():
    """返回前端页面，浏览器访问 http://localhost:5001/ 时看到的就是它。"""
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/style.css")
def serve_style():
    """返回页面样式。缺少这个路由的话，浏览器会在加载样式时拿到 404。"""
    return send_from_directory(FRONTEND_DIR, "style.css")


@app.get("/app.js")
def serve_script():
    """返回前端脚本，前端就是用这里的 fetch() 调用下面那些 API 的。"""
    return send_from_directory(FRONTEND_DIR, "app.js")


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------


@app.get("/api/hello")
def hello():
    """最简单的连通性测试接口。"""
    return jsonify({"message": "你好"})


@app.post("/api/messages")
def create_message():
    """创建一条聊天记录，reply 来自 DeepSeek 的真实回复。"""
    global next_message_id

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "message" not in data:
        return jsonify({"error": "请求体需要是 JSON，并且包含 message 字段"}), 400

    text = data["message"]
    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "message 必须是非空字符串"}), 400

    try:
        reply = ask_deepseek(text.strip())
    except RuntimeError as error:
        # 调用失败时返回清晰的 JSON 错误，而不是让 Flask 直接崩掉
        return jsonify({"error": str(error)}), 502

    record = {
        "id": next_message_id,
        "message": text.strip(),
        "reply": reply,
    }
    next_message_id += 1
    messages.append(record)

    return jsonify(record), 201


@app.get("/api/messages")
def list_messages():
    """返回内存中保存的全部聊天记录。"""
    return jsonify(messages)


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    """修改指定记录的 message 字段。"""
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "message" not in data:
        return jsonify({"error": "请求体需要是 JSON，并且包含 message 字段"}), 400

    text = data["message"]
    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "message 必须是非空字符串"}), 400

    record = find_message(message_id)
    if record is None:
        return jsonify({"error": f"id 为 {message_id} 的聊天记录不存在"}), 404

    record["message"] = text.strip()
    return jsonify(record)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    """删除指定 id 的聊天记录。"""
    record = find_message(message_id)
    if record is None:
        return jsonify({"error": f"id 为 {message_id} 的聊天记录不存在"}), 404

    messages.remove(record)
    return jsonify({"deleted": message_id})


if __name__ == "__main__":
    app.run(port=5001, debug=True)
