from flask import Flask, jsonify


app = Flask(__name__)
app.json.ensure_ascii = False


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.post("/api/messages")
def create_message():
    # TODO: 接收消息并创建一条问答记录。
    return jsonify({"error": "尚未实现创建聊天记录"}), 501


@app.get("/api/messages")
def list_messages():
    # TODO: 返回所有聊天记录。
    return jsonify({"error": "尚未实现读取聊天记录"}), 501


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    # TODO: 根据 ID 修改聊天记录。
    return jsonify({"error": "尚未实现修改聊天记录"}), 501


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    # TODO: 根据 ID 删除聊天记录。
    return jsonify({"error": "尚未实现删除聊天记录"}), 501


if __name__ == "__main__":
    app.run(port=5001, debug=True)
