"""
Lab 2 - AI Chat Web App
Flask 后端入口（任务 1：仅最小骨架）
"""

from flask import Flask, jsonify

app = Flask(__name__)
# 让 jsonify 默认不转义中文，任务 2 起继续沿用
app.json.ensure_ascii = False


@app.route("/api/hello", methods=["GET"])
def hello():
    """最小健康检查接口：返回固定中文问候。"""
    return jsonify({"message": "你好"})


# ---- CRUD 路由骨架（任务 1：暂时返回 501；任务 2 起实现真实逻辑） ----


@app.route("/api/messages", methods=["POST"])
def create_message():
    # TODO (任务 2): 接收用户消息，生成 id，存入内存列表并返回完整记录
    return jsonify({"error": "Not Implemented"}), 501


@app.route("/api/messages", methods=["GET"])
def list_messages():
    # TODO (任务 2): 返回内存中的全部聊天记录
    return jsonify({"error": "Not Implemented"}), 501


@app.route("/api/messages/<int:message_id>", methods=["PATCH"])
def update_message(message_id: int):
    # TODO (任务 2): 修改指定 id 的聊天记录（至少支持修改 message）
    return jsonify({"error": "Not Implemented"}), 501


@app.route("/api/messages/<int:message_id>", methods=["DELETE"])
def delete_message(message_id: int):
    # TODO (任务 2): 删除指定 id 的聊天记录
    return jsonify({"error": "Not Implemented"}), 501


if __name__ == "__main__":
    # 任务 1：Flask 不托管前端页面
    # 任务 2 起：会增加 / 与 /frontend/<file> 路由，使 http://localhost:5001/ 直接返回页面
    app.run(host="127.0.0.1", port=5001, debug=True)
