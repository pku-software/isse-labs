"""AI 聊天 Web 应用的后端。

当前阶段 Flask 同时提供前端页面和后端 API：

- 访问 ``GET /`` 返回 ``frontend/index.html``，样式和脚本也由 Flask 提供；
- ``GET /api/hello`` 用来确认服务是否正常运行；
- 聊天记录通过 ``/api/messages`` 完成创建、读取、修改和删除；
- 数据只保存在内存里，不写文件、不连数据库，重启 Flask 后即丢失；
- 暂不调用 DeepSeek，回复固定为「你好」。

一条聊天记录约定为：``{"id": 1, "message": "用户输入", "reply": "后端回复"}``
"""

from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

# 静态资源（style.css、app.js）由 Flask 从 frontend/ 目录提供，
# static_url_path="" 表示它们挂在网站根路径下，例如 /style.css
app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")

# 让 JSON 响应里的中文直接显示，而不是转义成 \uXXXX
app.json.ensure_ascii = False

# 聊天记录暂时只保存在这个进程的内存里，Flask 一重启就没了
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


@app.post("/api/messages")
def create_message():
    """创建一条聊天记录，回复暂时固定为「你好」。"""
    global next_message_id

    text = read_message_text()
    if text is None:
        return jsonify({"error": "请求体需要是 JSON，并且 message 字段不能为空"}), 400

    record = {"id": next_message_id, "message": text, "reply": "你好"}
    messages.append(record)
    next_message_id += 1
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
    return jsonify(record)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    """删除指定聊天记录。"""
    record = find_message(message_id)
    if record is None:
        return jsonify({"error": f"id 为 {message_id} 的聊天记录不存在"}), 404

    messages.remove(record)
    return jsonify({"deleted_id": message_id})


if __name__ == "__main__":
    # 使用 5001 端口，避免与其它本地服务冲突
    app.run(port=5001, debug=True)
