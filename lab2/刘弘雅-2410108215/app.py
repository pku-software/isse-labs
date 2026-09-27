from flask import Flask, jsonify

app = Flask(__name__)
app.json.ensure_ascii = False


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


# TODO: 实现创建一条聊天记录
@app.post("/api/messages")
def create_message():
    return jsonify({"error": "Not Implemented"}), 501


# TODO: 实现读取全部聊天记录
@app.get("/api/messages")
def list_messages():
    return jsonify({"error": "Not Implemented"}), 501


# TODO: 实现修改指定聊天记录
@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    return jsonify({"error": "Not Implemented"}), 501


# TODO: 实现删除指定聊天记录
@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    return jsonify({"error": "Not Implemented"}), 501


if __name__ == "__main__":
    app.run(port=5001, debug=True)
