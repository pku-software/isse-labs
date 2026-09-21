"""Lab 2 AI 聊天 Web 应用 —— Flask 后端入口。

现在同一个 Flask 进程负责两件事：

- 把 ``frontend/`` 目录里的页面和静态资源交给浏览器；
- 提供聊天记录的 CRUD 接口。

聊天记录先放在内存列表里，Flask 一重启就清空；本阶段还没有接入 DeepSeek。
"""

from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="/static")
# 让 jsonify 直接输出中文，而不是 \uXXXX 转义
app.json.ensure_ascii = False

# 内存中的聊天记录，形如 {"id": 1, "message": "用户输入", "reply": "后端回复"}
messages: list[dict] = []
next_id = 1


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
    """新建一条聊天记录，本阶段的回复固定为“你好”。"""
    global next_id

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not str(data.get("message", "")).strip():
        return jsonify({"error": "请求体需要包含非空的 message 字段"}), 400

    record = {"id": next_id, "message": str(data["message"]).strip(), "reply": "你好"}
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
