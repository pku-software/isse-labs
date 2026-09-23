"""AI 聊天 Web 应用的后端服务。

当前阶段（骨架阶段）后端只提供：

- GET /api/hello          最简单的一个接口，用来确认 Flask 能正常响应
- /api/messages 的 CRUD   只有路由骨架，统一返回 501 Not Implemented

这一阶段后端不返回前端页面，不调用大模型，也不保存任何数据。
"""

from flask import Flask, jsonify

app = Flask(__name__)

# 让 JSON 响应中的中文直接显示，而不是转义成 \uXXXX
app.json.ensure_ascii = False


@app.get("/api/hello")
def hello():
    """最简单的连通性接口。"""
    return jsonify({"message": "你好"})


# ---------------------------------------------------------------------------
# 聊天记录的 CRUD 路由骨架
#
# 一条聊天记录的数据结构约定为：
#     {"id": 1, "message": "用户输入", "reply": "后端回复"}
# ---------------------------------------------------------------------------


@app.post("/api/messages")
def create_message():
    """创建一条聊天记录。"""
    # TODO: 从请求体读取 message，分配一个唯一 id，生成 reply，返回完整记录
    return jsonify({"error": "创建聊天记录的功能尚未实现"}), 501


@app.get("/api/messages")
def list_messages():
    """读取全部聊天记录。"""
    # TODO: 返回内存中保存的全部聊天记录
    return jsonify({"error": "读取聊天记录的功能尚未实现"}), 501


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    """修改指定 id 的聊天记录。"""
    # TODO: 至少支持修改记录中的 message 字段；id 不存在时返回 404
    return jsonify({"error": "修改聊天记录的功能尚未实现"}), 501


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    """删除指定 id 的聊天记录。"""
    # TODO: 删除指定 id 的记录；id 不存在时返回 404
    return jsonify({"error": "删除聊天记录的功能尚未实现"}), 501


if __name__ == "__main__":
    app.run(port=5001, debug=True)
