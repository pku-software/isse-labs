import json
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

# 会话持久化：启动时从 data/conversations.json 读入内存，每次变更后写回文件。
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DATA_FILE = os.path.join(DATA_DIR, "conversations.json")


def load_conversations():
    """启动时读取 data/conversations.json；文件不存在或内容异常时从空列表开始"""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return []


def save_conversations():
    """把内存中的会话列表写回 data/conversations.json"""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(conversations, f, ensure_ascii=False, indent=2)


# 每个会话的结构：
# {"id": 1, "title": "会话标题", "messages": [{"id": 1, "message": "用户输入", "reply": "AI 回复"}]}
conversations = load_conversations()
# 新会话 id 从已有最大 id + 1 开始，避免冲突
next_conversation_id = max((c["id"] for c in conversations), default=0) + 1
# 消息 id 在所有会话之间全局唯一递增
next_message_id = max(
    (m["id"] for c in conversations for m in c.get("messages", [])), default=0
) + 1


def find_conversation(conversation_id):
    """在会话列表中查找指定 id 的会话，找不到返回 None"""
    for conv in conversations:
        if conv["id"] == conversation_id:
            return conv
    return None


def call_deepseek_with_history(history_messages, new_text):
    """携带该会话的历史消息调用 DeepSeek，返回模型回复文本；失败时抛出异常"""
    api_messages = []
    for m in history_messages:
        api_messages.append({"role": "user", "content": m["message"]})
        api_messages.append({"role": "assistant", "content": m["reply"]})
    api_messages.append({"role": "user", "content": new_text})
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=api_messages,
    )
    return response.choices[0].message.content


@app.route("/")
def index():
    # 浏览器访问 http://localhost:5001/ 时返回前端页面
    return app.send_static_file("index.html")


@app.route("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.route("/api/conversations", methods=["POST"])
def create_conversation():
    """创建一个新会话"""
    global next_conversation_id
    data = request.get_json(silent=True) or {}
    title = data.get("title") or "新会话"
    conv = {"id": next_conversation_id, "title": title, "messages": []}
    conversations.append(conv)
    next_conversation_id += 1
    save_conversations()
    return jsonify(conv), 201


@app.route("/api/conversations", methods=["GET"])
def list_conversations():
    """返回全部会话"""
    return jsonify(conversations)


@app.route("/api/conversations/<int:conversation_id>", methods=["GET"])
def get_conversation(conversation_id):
    """返回指定会话（含消息历史）"""
    conv = find_conversation(conversation_id)
    if conv is None:
        return jsonify({"error": f"ID 为 {conversation_id} 的会话不存在"}), 404
    return jsonify(conv)


@app.route("/api/conversations/<int:conversation_id>", methods=["PATCH"])
def update_conversation(conversation_id):
    """重命名指定会话"""
    conv = find_conversation(conversation_id)
    if conv is None:
        return jsonify({"error": f"ID 为 {conversation_id} 的会话不存在"}), 404
    data = request.get_json(silent=True)
    if not data or not data.get("title"):
        return jsonify({"error": "缺少 title 字段"}), 400
    conv["title"] = data["title"]
    save_conversations()
    return jsonify(conv)


@app.route("/api/conversations/<int:conversation_id>", methods=["DELETE"])
def delete_conversation(conversation_id):
    """删除指定会话"""
    conv = find_conversation(conversation_id)
    if conv is None:
        return jsonify({"error": f"ID 为 {conversation_id} 的会话不存在"}), 404
    conversations.remove(conv)
    save_conversations()
    return jsonify({"deleted": conv})


@app.route("/api/conversations/<int:conversation_id>/messages", methods=["POST"])
def create_conversation_message(conversation_id):
    """在指定会话中发送一条消息：携带历史调用 DeepSeek，返回更新后的会话"""
    global next_message_id
    conv = find_conversation(conversation_id)
    if conv is None:
        return jsonify({"error": f"ID 为 {conversation_id} 的会话不存在"}), 404
    data = request.get_json(silent=True)
    if not data or not data.get("message"):
        return jsonify({"error": "缺少 message 字段"}), 400
    if client is None:
        return jsonify({"error": "未配置 DEEPSEEK_API_KEY，请检查 .env 文件"}), 500
    try:
        reply = call_deepseek_with_history(conv["messages"], data["message"])
    except Exception as e:
        # 模型调用失败时返回清晰的 JSON 错误，不让 Flask 直接崩溃
        return jsonify({"error": f"调用 DeepSeek API 失败：{e}"}), 502
    record = {"id": next_message_id, "message": data["message"], "reply": reply}
    conv["messages"].append(record)
    next_message_id += 1
    save_conversations()
    return jsonify(conv), 201


if __name__ == "__main__":
    app.run(port=5001, debug=True)
