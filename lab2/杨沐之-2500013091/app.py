from flask import Flask, jsonify


app = Flask(__name__)
if hasattr(app, "json"):
    app.json.ensure_ascii = False
else:
    # Flask 2.x 使用配置项控制 JSON 中的中文转义。
    app.config["JSON_AS_ASCII"] = False


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.post("/api/messages")
def create_message():
    # TODO: 创建一条聊天记录。
    return jsonify({"error": "Not Implemented"}), 501


@app.get("/api/messages")
def list_messages():
    # TODO: 返回全部聊天记录。
    return jsonify({"error": "Not Implemented"}), 501


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    # TODO: 根据 message_id 修改聊天记录。
    return jsonify({"error": "Not Implemented"}), 501


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    # TODO: 根据 message_id 删除聊天记录。
    return jsonify({"error": "Not Implemented"}), 501


if __name__ == "__main__":
    app.run(port=5001, debug=True)
