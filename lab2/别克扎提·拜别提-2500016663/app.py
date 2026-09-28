"""AI 聊天助手后端服务。

同一个 Flask 进程同时提供：
- 前端页面（frontend/ 目录下的静态文件）
- 聊天记录 CRUD API（回复由 DeepSeek 模型生成）

数据只保存在内存列表中，Flask 重启后清空（本阶段刻意不持久化）。
API Key 通过 .env 提供，只存在于后端进程的环境中。
"""

import os

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

# 从项目根目录的 .env 文件加载环境变量（文件不存在时静默跳过）
load_dotenv()

app = Flask(__name__)

# 让 JSON 响应中的中文直接显示，而不是被转义成 \uXXXX
app.json.ensure_ascii = False

# DeepSeek 官方 API 配置（文档：https://api-docs.deepseek.com/zh-cn/）
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# 内存中的聊天记录：每个元素形如 {"id": 1, "message": "用户输入", "reply": "模型回复"}
messages = []
# 自增 id 计数器，用于保证每条记录的 id 唯一
next_id = 1


# ---------- 前端页面路由 ----------


@app.route("/")
def serve_index():
    """访问 http://localhost:5001/ 时返回前端页面。"""
    return send_from_directory("frontend", "index.html")


@app.route("/<path:filename>")
def serve_frontend_file(filename):
    """提供 frontend/ 下的其他静态文件（style.css、app.js 等）。

    Flask 会优先匹配更具体的路由（例如 /api/messages/<id>），
    只有匹配不上的路径才会落到这里。
    """
    return send_from_directory("frontend", filename)


# ---------- DeepSeek 调用 ----------


def call_deepseek(message):
    """把用户消息发给 DeepSeek，返回模型回复文本；失败时抛出异常。"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        # 只判断变量是否存在，绝不输出它的值
        raise ValueError("服务器缺少 DEEPSEEK_API_KEY，请检查 .env 是否创建")

    response = requests.post(
        DEEPSEEK_API_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": DEEPSEEK_MODEL,
            "messages": [{"role": "user", "content": message}],
        },
        timeout=30,
    )
    # 4xx / 5xx 响应时抛出 requests.HTTPError
    response.raise_for_status()
    data = response.json()
    # 官方响应结构：choices[0].message.content 即模型回复文本
    return data["choices"][0]["message"]["content"]


# ---------- API ----------


@app.route("/api/hello")
def hello():
    """健康检查接口。"""
    return jsonify({"message": "你好"})


@app.route("/api/messages", methods=["POST"])
def create_message():
    """创建一条聊天记录：读取 message，reply 由 DeepSeek 模型生成。"""
    global next_id

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "请求体必须是 JSON 对象"}), 400

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "字段 message 不能为空"}), 400

    # 先拿到模型回复，调用成功后才保存记录
    try:
        reply = call_deepseek(message.strip())
    except ValueError as exc:
        # Key 缺失属于服务器配置错误
        return jsonify({"error": str(exc)}), 500
    except requests.RequestException as exc:
        # 网络错误、超时、DeepSeek 返回 4xx/5xx
        return jsonify({"error": f"调用 DeepSeek API 失败：{exc}"}), 502
    except (KeyError, IndexError):
        # 响应 JSON 结构不符合预期
        return jsonify({"error": "DeepSeek 返回了无法解析的响应"}), 502

    record = {
        "id": next_id,
        "message": message.strip(),
        "reply": reply,
    }
    next_id += 1
    messages.append(record)
    # 201 Created：表示资源创建成功
    return jsonify(record), 201


@app.route("/api/messages", methods=["GET"])
def list_messages():
    """返回全部聊天记录。"""
    return jsonify(messages)


@app.route("/api/messages/<int:message_id>", methods=["PATCH"])
def update_message(message_id):
    """修改指定 id 记录的 message 字段。"""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "请求体必须是 JSON 对象"}), 400

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "字段 message 不能为空"}), 400

    for record in messages:
        if record["id"] == message_id:
            record["message"] = message.strip()
            return jsonify(record)

    return jsonify({"error": f"id 为 {message_id} 的记录不存在"}), 404


@app.route("/api/messages/<int:message_id>", methods=["DELETE"])
def delete_message(message_id):
    """删除指定 id 的记录。"""
    for index, record in enumerate(messages):
        if record["id"] == message_id:
            messages.pop(index)
            # 204 No Content：表示删除成功，响应没有正文
            return "", 204

    return jsonify({"error": f"id 为 {message_id} 的记录不存在"}), 404


if __name__ == "__main__":
    app.run(port=5001, debug=True)
