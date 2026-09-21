"""Lab 2 AI 聊天 Web 应用 —— Flask 后端入口。

当前阶段只提供最小可运行的后端：

- ``GET /api/hello``：验证服务是否正常启动；
- 四条聊天记录接口先占位，统一返回 501。

本阶段不托管前端页面、不调用 DeepSeek、不做任何数据持久化。
"""

from flask import Flask, jsonify

app = Flask(__name__)
# 让 jsonify 直接输出中文，而不是 \\uXXXX 转义
app.json.ensure_ascii = False


@app.route("/api/hello", methods=["GET"])
def hello():
    """最简单的连通性检查接口。"""
    return jsonify({"message": "你好"})


@app.route("/api/messages", methods=["POST"])
def create_message():
    # TODO: 读取请求体中的 message，生成唯一 id，存入内存列表并返回完整记录
    return jsonify({"error": "Not Implemented"}), 501


@app.route("/api/messages", methods=["GET"])
def list_messages():
    # TODO: 返回内存中的全部聊天记录
    return jsonify({"error": "Not Implemented"}), 501


@app.route("/api/messages/<int:message_id>", methods=["PATCH"])
def update_message(message_id: int):
    # TODO: 修改指定 id 的聊天记录（至少支持修改 message）
    return jsonify({"error": "Not Implemented"}), 501


@app.route("/api/messages/<int:message_id>", methods=["DELETE"])
def delete_message(message_id: int):
    # TODO: 删除指定 id 的聊天记录
    return jsonify({"error": "Not Implemented"}), 501


if __name__ == "__main__":
    # 本阶段 Flask 只提供 API，不托管前端页面
    app.run(host="127.0.0.1", port=5001, debug=True)
