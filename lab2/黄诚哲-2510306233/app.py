from flask import Flask, jsonify

app = Flask(__name__)
app.json.ensure_ascii = False


@app.route("/api/hello")
def hello():
    return jsonify({"message": "你好"})


# TODO: 实现创建一条聊天记录
@app.route("/api/messages", methods=["POST"])
def create_message():
    return jsonify({"error": "Not Implemented"}), 501


# TODO: 实现读取全部聊天记录
@app.route("/api/messages", methods=["GET"])
def list_messages():
    return jsonify({"error": "Not Implemented"}), 501


# TODO: 实现修改一条聊天记录
@app.route("/api/messages/<int:message_id>", methods=["PATCH"])
def update_message(message_id):
    return jsonify({"error": "Not Implemented"}), 501


# TODO: 实现删除一条聊天记录
@app.route("/api/messages/<int:message_id>", methods=["DELETE"])
def delete_message(message_id):
    return jsonify({"error": "Not Implemented"}), 501


if __name__ == "__main__":
    app.run(port=5001, debug=True)
