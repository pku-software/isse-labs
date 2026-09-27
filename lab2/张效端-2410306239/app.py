import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from openai import OpenAI

# 读取个人目录下的 .env 文件，把其中的变量（如 DEEPSEEK_API_KEY）加载为环境变量
load_dotenv()

app = Flask(__name__, static_folder="frontend", static_url_path="")
# 保证 JSON 响应中的中文直接显示，不被转义为 \uXXXX
app.json.ensure_ascii = False

# 用 .env 中的 Key 创建 DeepSeek 客户端。
# Key 只存在于后端环境变量中，不会出现在代码里，也不会返回给浏览器。
api_key = os.getenv("DEEPSEEK_API_KEY")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com") if api_key else None

# 聊天记录全部保存在内存中（Flask 重启后数据会丢失）
# 每条记录格式：{"id": 1, "message": "用户输入", "reply": "后端回复"}
messages = []
next_id = 1


def find_message(message_id):
    """在内存列表中查找指定 id 的记录，找不到返回 None"""
    for msg in messages:
        if msg["id"] == message_id:
            return msg
    return None


def call_deepseek(text):
    """调用 DeepSeek 模型，返回模型回复文本；失败时抛出异常"""
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": text}],
    )
    return response.choices[0].message.content


@app.route("/")
def index():
    # 浏览器访问 http://localhost:5001/ 时返回前端页面
    return app.send_static_file("index.html")


@app.route("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.route("/api/messages", methods=["POST"])
def create_message():
    """创建一条聊天记录：调用 DeepSeek 获得真实回复"""
    global next_id
    data = request.get_json(silent=True)
    if not data or not data.get("message"):
        return jsonify({"error": "缺少 message 字段"}), 400
    if client is None:
        return jsonify({"error": "未配置 DEEPSEEK_API_KEY，请检查 .env 文件"}), 500
    try:
        reply = call_deepseek(data["message"])
    except Exception as e:
        # 模型调用失败时返回清晰的 JSON 错误，不让 Flask 直接崩溃
        return jsonify({"error": f"调用 DeepSeek API 失败：{e}"}), 502
    record = {"id": next_id, "message": data["message"], "reply": reply}
    messages.append(record)
    next_id += 1
    return jsonify(record), 201


@app.route("/api/messages", methods=["GET"])
def list_messages():
    """返回全部聊天记录"""
    return jsonify(messages)


@app.route("/api/messages/<int:message_id>", methods=["PATCH"])
def update_message(message_id):
    """修改指定聊天记录的 message 字段"""
    record = find_message(message_id)
    if record is None:
        return jsonify({"error": f"ID 为 {message_id} 的记录不存在"}), 404
    data = request.get_json(silent=True)
    if not data or not data.get("message"):
        return jsonify({"error": "缺少 message 字段"}), 400
    record["message"] = data["message"]
    return jsonify(record)


@app.route("/api/messages/<int:message_id>", methods=["DELETE"])
def delete_message(message_id):
    """删除指定聊天记录"""
    record = find_message(message_id)
    if record is None:
        return jsonify({"error": f"ID 为 {message_id} 的记录不存在"}), 404
    messages.remove(record)
    return jsonify({"deleted": record})


if __name__ == "__main__":
    app.run(port=5001, debug=True)
