"""AI 聊天 Web 应用的后端。

当前阶段只搭建后端骨架：

- 提供最简单的接口 ``GET /api/hello``，用来确认 Flask 能独立运行；
- 为聊天记录的增删改查预留路由，统一返回 501 Not Implemented；
- 暂不返回前端页面，暂不调用 DeepSeek，暂不保存数据。

一条聊天记录约定为：``{"id": 1, "message": "用户输入", "reply": "后端回复"}``
"""

from flask import Flask, jsonify

app = Flask(__name__)

# 让 JSON 响应里的中文直接显示，而不是转义成 \uXXXX
app.json.ensure_ascii = False


@app.get("/api/hello")
def hello():
    """最简单的接口，用于确认后端已经正常运行。"""
    return jsonify({"message": "你好"})


@app.post("/api/messages")
def create_message():
    """创建一条聊天记录。

    TODO: 读取请求体里的 message 字段，生成唯一 id，把记录写入内存列表。
    """
    return jsonify({"error": "创建聊天记录的功能尚未实现"}), 501


@app.get("/api/messages")
def list_messages():
    """读取全部聊天记录。

    TODO: 返回内存列表中的所有记录。
    """
    return jsonify({"error": "读取聊天记录列表的功能尚未实现"}), 501


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    """修改指定 id 的聊天记录。

    TODO: 至少支持修改 message 字段；id 不存在时返回 404 和 JSON 错误信息。
    """
    return jsonify({"error": "修改聊天记录的功能尚未实现"}), 501


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    """删除指定 id 的聊天记录。

    TODO: 删除对应记录；id 不存在时返回 404 和 JSON 错误信息。
    """
    return jsonify({"error": "删除聊天记录的功能尚未实现"}), 501


if __name__ == "__main__":
    # 使用 5001 端口，避免与其它本地服务冲突
    app.run(port=5001, debug=True)
