from flask import Flask, jsonify, request

app = Flask(__name__, static_folder="frontend", static_url_path="")
# 保证 JSON 响应中的中文直接显示，不被转义为 \uXXXX
app.json.ensure_ascii = False

# 聊天记录全部保存在内存中（Flask 重启后数据会丢失）
# 每条记录格式：{"id": 1, "message": "用户输入", "reply": "后端回复"}
messages = []
next_id = 1


def find_message(message_id):
    """在内存列表中查找指定 id 的记录，找不到返回 None"""
    for msg in messages:
        if msg["id"] == message_id:
            return msg
    return None


@app.route("/")
def index():
    # 浏览器访问 http://localhost:5001/ 时返回前端页面
    return app.send_static_file("index.html")


@app.route("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.route("/api/messages", methods=["POST"])
def create_message():
    """创建一条聊天记录，reply 暂时固定为“你好”"""
    global next_id
    data = request.get_json(silent=True)
    if not data or not data.get("message"):
        return jsonify({"error": "缺少 message 字段"}), 400
    record = {"id": next_id, "message": data["message"], "reply": "你好"}
    messages.append(record)
    next_id += 1
    return jsonify(record), 201


@app.route("/api/messages", methods=["GET"])
def list_messages():
    """返回全部聊天记录"""
    return jsonify(messages)


@app.route("/api/messages/<int:message_id>", methods=["PATCH"])
def update_message(message_id):
    """修改指定聊天记录的 message 字段"""
    record = find_message(message_id)
    if record is None:
        return jsonify({"error": f"ID 为 {message_id} 的记录不存在"}), 404
    data = request.get_json(silent=True)
    if not data or not data.get("message"):
        return jsonify({"error": "缺少 message 字段"}), 400
    record["message"] = data["message"]
    return jsonify(record)


@app.route("/api/messages/<int:message_id>", methods=["DELETE"])
def delete_message(message_id):
    """删除指定聊天记录"""
    record = find_message(message_id)
    if record is None:
        return jsonify({"error": f"ID 为 {message_id} 的记录不存在"}), 404
    messages.remove(record)
    return jsonify({"deleted": record})


if __name__ == "__main__":
    app.run(port=5001, debug=True)
