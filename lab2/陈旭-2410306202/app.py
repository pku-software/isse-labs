"""AI 聊天 Web 应用的后端骨架。

本阶段只提供最简单的连通性接口 `GET /api/hello`，并把 CRUD 路由留成骨架。
暂时不返回前端页面、不接入 DeepSeek、不保存任何数据。
"""

from flask import Flask, jsonify

app = Flask(__name__)

# 让 JSON 响应中的中文直接以中文输出，而不是被转义成 \uXXXX
app.json.ensure_ascii = False

# 预留给后续阶段的聊天记录列表，一条记录形如 {"id": 1, "message": "用户输入", "reply": "后端回复"}
messages = []


@app.get("/api/hello")
def hello():
    """最简单的连通性测试接口。"""
    return jsonify({"message": "你好"})


# ---------------------------------------------------------------------------
# 以下是 CRUD 路由骨架，本阶段统一返回 501 Not Implemented。
# 下一阶段会在这些函数里实现基于内存的增删改查。
# ---------------------------------------------------------------------------


@app.post("/api/messages")
def create_message():
    """创建一条聊天记录。"""
    # TODO: 读取请求体中的 message，生成唯一 id，把 {id, message, reply} 存入内存并返回
    return jsonify({"error": "尚未实现"}), 501


@app.get("/api/messages")
def list_messages():
    """返回全部聊天记录。"""
    # TODO: 返回内存中保存的全部聊天记录
    return jsonify({"error": "尚未实现"}), 501


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    """修改指定 id 的聊天记录。"""
    # TODO: 按 id 找到记录并修改它的 message 字段；id 不存在时返回 404
    return jsonify({"error": "尚未实现"}), 501


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    """删除指定 id 的聊天记录。"""
    # TODO: 按 id 删除记录；id 不存在时返回 404
    return jsonify({"error": "尚未实现"}), 501


if __name__ == "__main__":
    app.run(port=5001, debug=True)
