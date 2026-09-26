"""AI 聊天助手后端服务。

同一个 Flask 进程同时提供：
- 前端页面（frontend/ 目录下的静态文件）
- 聊天记录 CRUD API

数据只保存在内存列表中，Flask 重启后清空（本阶段刻意不持久化）。
"""

from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)

# 让 JSON 响应中的中文直接显示，而不是被转义成 \uXXXX
app.json.ensure_ascii = False

# 内存中的聊天记录：每个元素形如 {"id": 1, "message": "用户输入", "reply": "后端回复"}
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


# ---------- API ----------


@app.route("/api/hello")
def hello():
    """健康检查接口。"""
    return jsonify({"message": "你好"})


@app.route("/api/messages", methods=["POST"])
def create_message():
    """创建一条聊天记录：读取 message，reply 暂时固定为“你好”。"""
    global next_id

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "请求体必须是 JSON 对象"}), 400

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "字段 message 不能为空"}), 400

    record = {
        "id": next_id,
        "message": message.strip(),
        "reply": "你好",
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
