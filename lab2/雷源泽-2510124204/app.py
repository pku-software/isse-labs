from flask import Flask, jsonify


app = Flask(__name__)
app.json.ensure_ascii = False


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.post("/api/messages")
def create_message():
    # TODO: 接收消息，创建聊天记录并返回完整记录。
    return jsonify({"error": "Not implemented"}), 501


@app.get("/api/messages")
def list_messages():
    # TODO: 返回当前进程内存中的全部聊天记录。
    return jsonify({"error": "Not implemented"}), 501


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    # TODO: 根据 message_id 修改指定聊天记录的消息内容。
    return jsonify({"error": "Not implemented"}), 501


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    # TODO: 根据 message_id 删除指定聊天记录。
    return jsonify({"error": "Not implemented"}), 501


if __name__ == "__main__":
    app.run(port=5001, debug=True)
