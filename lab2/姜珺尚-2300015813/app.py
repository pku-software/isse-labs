"""Minimal Flask API for the chat application."""

from flask import Flask, jsonify

app = Flask(__name__, static_folder=None)
app.json.ensure_ascii = False


@app.get("/api/hello")
def hello():
    return jsonify(message="你好")


@app.post("/api/messages")
def create_message():
    # TODO: Validate input and create a chat record.
    return jsonify(error="创建聊天记录功能尚未实现"), 501


@app.get("/api/messages")
def list_messages():
    # TODO: Return all chat records.
    return jsonify(error="查看聊天记录功能尚未实现"), 501


@app.patch("/api/messages/<int:id>")
def update_message(id):
    # TODO: Find the record by ID and update its message.
    return jsonify(error="修改聊天记录功能尚未实现"), 501


@app.delete("/api/messages/<int:id>")
def delete_message(id):
    # TODO: Find the record by ID and delete it.
    return jsonify(error="删除聊天记录功能尚未实现"), 501


if __name__ == "__main__":
    app.run(port=5001, debug=True)
