"""AI 聊天应用的 Flask 接口骨架。"""

from flask import Flask, jsonify

app = Flask(__name__, static_folder=None)
app.json.ensure_ascii = False


@app.get("/api/hello")
def hello():
    return jsonify(message="你好")


@app.post("/api/messages")
def create_message():
    # TODO: 校验输入并创建一条问答记录。
    return jsonify(error="创建聊天记录尚未实现"), 501


@app.get("/api/messages")
def list_messages():
    # TODO: 返回全部聊天记录。
    return jsonify(error="查看聊天记录尚未实现"), 501


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    # TODO: 根据 message_id 查找记录并修改用户消息。
    return jsonify(error="修改聊天记录尚未实现"), 501


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    # TODO: 根据 message_id 查找并删除记录。
    return jsonify(error="删除聊天记录尚未实现"), 501


if __name__ == "__main__":
    app.run(port=5001, debug=True)
