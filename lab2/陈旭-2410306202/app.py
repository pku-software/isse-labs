"""AI 聊天 Web 应用的后端。

Flask 同时承担两件事：
1. 提供前端页面和静态资源（`/`、`/style.css`、`/app.js`）；
2. 提供聊天记录相关的 JSON API（`/api/...`）。

聊天记录目前只保存在内存列表里，Flask 一重启数据就没了。
本阶段还没有接入 DeepSeek，AI 的回复固定为“你好”。
"""

import os

from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

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
    """创建一条聊天记录，AI 回复暂时固定为“你好”。"""
    global next_message_id

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "message" not in data:
        return jsonify({"error": "请求体需要是 JSON，并且包含 message 字段"}), 400

    text = data["message"]
    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "message 必须是非空字符串"}), 400

    record = {
        "id": next_message_id,
        "message": text.strip(),
        "reply": "你好",
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
