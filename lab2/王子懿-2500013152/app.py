from flask import Flask, jsonify


app = Flask(__name__)
app.json.ensure_ascii = False


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.post("/api/messages")
def create_message():
    # TODO: 创建一条聊天记录。
    return jsonify({"error": "Not implemented"}), 501


@app.get("/api/messages")
def list_messages():
    # TODO: 返回全部聊天记录。
    return jsonify({"error": "Not implemented"}), 501


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    # TODO: 修改指定 ID 的聊天记录。
    return jsonify({"error": "Not implemented"}), 501


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    # TODO: 删除指定 ID 的聊天记录。
    return jsonify({"error": "Not implemented"}), 501


if __name__ == "__main__":
    app.run(port=5001, debug=True)
