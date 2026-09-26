"""AI 聊天助手后端服务（骨架阶段）。

本阶段只提供最简单的健康检查接口，CRUD 路由暂未实现。
"""

from flask import Flask, jsonify

app = Flask(__name__)

# 让 JSON 响应中的中文直接显示，而不是被转义成 \uXXXX
app.json.ensure_ascii = False


@app.route("/api/hello")
def hello():
    """健康检查接口，用于确认 Flask 正常运行。"""
    return jsonify({"message": "你好"})


# ---------- 聊天记录 CRUD 路由骨架（本阶段统一返回 501 Not Implemented） ----------


@app.route("/api/messages", methods=["POST"])
def create_message():
    """创建一条聊天记录（一次问答）。"""
    # TODO: 解析请求体中的 message 字段，生成唯一 id，
    #       生成 reply，把 {id, message, reply} 存入内存列表并返回
    return jsonify({"error": "Not Implemented"}), 501


@app.route("/api/messages", methods=["GET"])
def list_messages():
    """获取全部聊天记录。"""
    # TODO: 返回内存列表中的全部记录
    return jsonify({"error": "Not Implemented"}), 501


@app.route("/api/messages/<int:message_id>", methods=["PATCH"])
def update_message(message_id):
    """修改指定 id 的聊天记录。"""
    # TODO: 按 id 查找记录，更新 message 字段后返回更新后的记录
    return jsonify({"error": "Not Implemented"}), 501


@app.route("/api/messages/<int:message_id>", methods=["DELETE"])
def delete_message(message_id):
    """删除指定 id 的聊天记录。"""
    # TODO: 按 id 查找并删除记录，返回合适的成功响应
    return jsonify({"error": "Not Implemented"}), 501


if __name__ == "__main__":
    app.run(port=5001, debug=True)
