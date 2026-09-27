from flask import Flask, jsonify

app = Flask(__name__)
# 保证 JSON 响应中的中文直接显示，不被转义为 \uXXXX
app.json.ensure_ascii = False


@app.route("/api/hello")
def hello():
    return jsonify({"message": "你好"})


# TODO: POST /api/messages —— 创建一条聊天记录 {id, message, reply}，下一阶段实现
@app.route("/api/messages", methods=["POST"])
def create_message():
    return jsonify({"error": "Not implemented"}), 501


# TODO: GET /api/messages —— 返回全部聊天记录，下一阶段实现
@app.route("/api/messages", methods=["GET"])
def list_messages():
    return jsonify({"error": "Not implemented"}), 501


# TODO: PATCH /api/messages/<id> —— 修改指定聊天记录，下一阶段实现
@app.route("/api/messages/<int:message_id>", methods=["PATCH"])
def update_message(message_id):
    return jsonify({"error": "Not implemented"}), 501


# TODO: DELETE /api/messages/<id> —— 删除指定聊天记录，下一阶段实现
@app.route("/api/messages/<int:message_id>", methods=["DELETE"])
def delete_message(message_id):
    return jsonify({"error": "Not implemented"}), 501


if __name__ == "__main__":
    app.run(port=5001, debug=True)
