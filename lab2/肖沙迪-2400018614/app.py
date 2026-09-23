"""AI 聊天 Web 应用的后端服务。

同一个 Flask 服务同时承担两件事：

- 提供前端页面和静态资源（frontend/ 目录）
- 提供聊天记录的 RESTful API

聊天记录目前只保存在 Python 内存里，Flask 重启后会清空。
这一阶段还不调用大模型，回复固定为「你好」。
"""

import os

from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

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


@app.post("/api/messages")
def create_message():
    """创建一条聊天记录。"""
    message, error = _read_message_field(request.get_json(silent=True))
    if error:
        return error

    record = {"id": _next_id(), "message": message, "reply": "你好"}
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
