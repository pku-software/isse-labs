from flask import Flask, jsonify

app = Flask(__name__)
app.json.ensure_ascii = False


@app.get("/api/hello")
def hello():
    return jsonify(message="你好")


@app.post("/api/messages")
def create_message():
    # TODO: 创建一条聊天记录。
    return jsonify(error="创建聊天记录尚未实现"), 501


@app.get("/api/messages")
def list_messages():
    # TODO: 返回全部聊天记录。
    return jsonify(error="查看聊天记录尚未实现"), 501


@app.patch("/api/messages/<int:id>")
def update_message(id):
    # TODO: 根据 ID 修改聊天记录。
    return jsonify(error="修改聊天记录尚未实现"), 501


@app.delete("/api/messages/<int:id>")
def delete_message(id):
    # TODO: 根据 ID 删除聊天记录。
    return jsonify(error="删除聊天记录尚未实现"), 501


if __name__ == "__main__":
    app.run(port=5001, debug=True)
