from flask import Flask, jsonify


app = Flask(__name__)
app.json.ensure_ascii = False


@app.get("/api/hello")
def hello():
    return jsonify(message="你好")


@app.post("/api/messages")
def create_message():
    # TODO: create and store a chat message.
    return jsonify(error="Not Implemented", message="创建聊天记录的功能尚未实现"), 501


@app.get("/api/messages")
def list_messages():
    # TODO: return all stored chat messages.
    return jsonify(error="Not Implemented", message="读取聊天记录的功能尚未实现"), 501


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id: int):
    # TODO: update the chat message identified by message_id.
    return jsonify(error="Not Implemented", message="修改聊天记录的功能尚未实现", id=message_id), 501


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id: int):
    # TODO: delete the chat message identified by message_id.
    return jsonify(error="Not Implemented", message="删除聊天记录的功能尚未实现", id=message_id), 501


if __name__ == "__main__":
    app.run(port=5001, debug=True)
