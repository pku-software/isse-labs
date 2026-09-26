"""AI 聊天 Web 应用的后端。

Flask 同时承担两件事：
1. 提供前端页面和静态资源（`/`、`/style.css`、`/app.js`）；
2. 提供会话与聊天相关的 JSON API（`/api/...`）。

一个会话（conversation）包含多轮问答，每一轮是一问一答：
{"id": 1, "message": "用户的提问", "reply": "模型的回复"}。
调用 DeepSeek 时，后端会把当前会话已有的问答展开成带 role 的 messages 数组，
再加上这一次的新问题，让模型能接着上下文回答。

会话和消息保存在内存里，同时每次改动都会写回 data/conversations.json，
所以 Flask 重启后还能把数据读回来。

API Key 只保存在后端的 .env 文件里，通过环境变量读取，不会出现在前端代码中。
"""

import json
import os

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

# 把 .env 里的变量读进当前进程的环境变量。
# 文件不存在时它只是什么都不做，不会报错。
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
DATA_DIR = os.path.join(BASE_DIR, "data")
CONVERSATIONS_FILE = os.path.join(DATA_DIR, "conversations.json")

# DeepSeek 的接口地址与模型名，来自官方文档。
# 如果官方文档更新了接口地址或模型名，只需要改这两行。
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_TIMEOUT = 60

DEFAULT_CONVERSATION_TITLE = "新会话"

app = Flask(__name__)

# 让 JSON 响应中的中文直接以中文输出，而不是被转义成 \uXXXX
app.json.ensure_ascii = False


# ---------------------------------------------------------------------------
# 数据层：读取文件、查找、写回文件
# ---------------------------------------------------------------------------


def load_conversations():
    """从 JSON 文件读取全部会话；文件不存在、为空或内容损坏时从空数据开始。"""
    if not os.path.exists(CONVERSATIONS_FILE):
        return []

    try:
        with open(CONVERSATIONS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, ValueError):
        return []

    if not isinstance(data, list):
        return []

    loaded = []
    for item in data:
        if not isinstance(item, dict) or not isinstance(item.get("id"), int):
            continue

        turns = []
        for turn in item.get("turns", []):
            if not isinstance(turn, dict) or not isinstance(turn.get("id"), int):
                continue
            turns.append(
                {
                    "id": turn["id"],
                    "message": str(turn.get("message", "")),
                    "reply": str(turn.get("reply", "")),
                }
            )

        loaded.append(
            {
                "id": item["id"],
                "title": str(item.get("title") or DEFAULT_CONVERSATION_TITLE),
                "turns": turns,
            }
        )

    return loaded


def save_conversations():
    """把内存里的会话整体写回 JSON 文件。"""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CONVERSATIONS_FILE, "w", encoding="utf-8") as file:
        json.dump(conversations, file, ensure_ascii=False, indent=2)


# 全部会话，形如
# [{"id": 1, "title": "会话标题", "turns": [{"id": 1, "message": "...", "reply": "..."}]}]
conversations = load_conversations()

# 下一条会话 id：接在文件里已有最大 id 之后，保证不和已有会话重复
next_conversation_id = max((item["id"] for item in conversations), default=0) + 1


def find_conversation(conversation_id):
    """按 id 查找会话，找不到返回 None。"""
    for conversation in conversations:
        if conversation["id"] == conversation_id:
            return conversation
    return None


def find_turn(conversation, turn_id):
    """在某个会话里按 id 查找一轮问答，找不到返回 None。"""
    for turn in conversation["turns"]:
        if turn["id"] == turn_id:
            return turn
    return None


def next_turn_id(conversation):
    """返回某个会话里下一轮问答的 id。"""
    return max((turn["id"] for turn in conversation["turns"]), default=0) + 1


def create_conversation(title):
    """新建一个会话，写回文件并返回它。"""
    global next_conversation_id

    conversation = {
        "id": next_conversation_id,
        "title": title,
        "turns": [],
    }
    next_conversation_id += 1
    conversations.append(conversation)
    save_conversations()
    return conversation


def get_default_conversation():
    """兼容接口 /api/messages 使用的默认会话：一个会话都没有时自动建一个。"""
    if not conversations:
        create_conversation("默认会话")
    return conversations[0]


def read_message_text(payload):
    """从请求体里取出并校验 message 字段。

    返回 (问题文本, 错误说明)；校验失败时文本为 None。
    """
    if not isinstance(payload, dict) or "message" not in payload:
        return None, "请求体需要是 JSON，并且包含 message 字段"

    text = payload["message"]
    if not isinstance(text, str) or not text.strip():
        return None, "message 必须是非空字符串"

    return text.strip(), None


# ---------------------------------------------------------------------------
# DeepSeek 调用
# ---------------------------------------------------------------------------


def describe_deepseek_error(response):
    """从 DeepSeek 的错误响应里取出一句可读的说明，取不到就退回状态码。"""
    try:
        body = response.json()
    except ValueError:
        text = (response.text or "").strip()
        return text[:300] if text else f"HTTP {response.status_code}"

    if isinstance(body, dict):
        error = body.get("error")
        if isinstance(error, dict) and error.get("message"):
            return str(error["message"])[:300]
        if isinstance(error, str) and error:
            return error[:300]

    return f"HTTP {response.status_code}"


def build_model_messages(conversation, question):
    """把会话里已有的问答展开成 DeepSeek 需要的 messages 数组。

    每一轮问答会展开成两条：一条 role 为 user 的历史提问，
    一条 role 为 assistant 的历史回复，最后再补上这一次的新问题。
    """
    model_messages = []
    for turn in conversation["turns"]:
        model_messages.append({"role": "user", "content": turn["message"]})
        model_messages.append({"role": "assistant", "content": turn["reply"]})

    model_messages.append({"role": "user", "content": question})
    return model_messages


def ask_deepseek(model_messages):
    """把 messages 数组发给 DeepSeek，返回模型回复的文本。

    出错时抛出 RuntimeError，由调用方转成 JSON 错误响应。
    API Key 只通过请求头发给 DeepSeek，不会出现在前端代码或响应里。
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("服务端没有读到 DEEPSEEK_API_KEY，请先按 .env.example 配置 .env")

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": model_messages,
        "stream": False,
    }

    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=DEEPSEEK_TIMEOUT,
        )
    except requests.RequestException as error:
        raise RuntimeError(f"无法连接 DeepSeek：{error}") from error

    if response.status_code != 200:
        raise RuntimeError(
            f"DeepSeek 返回错误（HTTP {response.status_code}）：{describe_deepseek_error(response)}"
        )

    try:
        return response.json()["choices"][0]["message"]["content"].strip()
    except (ValueError, KeyError, IndexError, TypeError, AttributeError) as error:
        raise RuntimeError("DeepSeek 的返回内容无法解析") from error


def add_turn(conversation, question):
    """在会话里新增一轮问答：带上下文调用 DeepSeek，把结果追加进去并写回文件。

    返回新的一轮问答；调用失败时抛出 RuntimeError。
    """
    reply = ask_deepseek(build_model_messages(conversation, question))

    turn = {
        "id": next_turn_id(conversation),
        "message": question,
        "reply": reply,
    }
    conversation["turns"].append(turn)
    save_conversations()
    return turn


# ---------------------------------------------------------------------------
# 前端页面与静态资源
# ---------------------------------------------------------------------------


@app.get("/")
def serve_index():
    """返回前端页面，浏览器访问 http://localhost:5001/ 时看到的就是它。"""
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/style.css")
def serve_style():
    """返回页面样式。缺少这个路由的话，浏览器会在加载样式时拿到 404。"""
    return send_from_directory(FRONTEND_DIR, "style.css")


@app.get("/app.js")
def serve_script():
    """返回前端脚本，前端就是用这里的 fetch() 调用下面那些 API 的。"""
    return send_from_directory(FRONTEND_DIR, "app.js")


# ---------------------------------------------------------------------------
# API：连通性测试
# ---------------------------------------------------------------------------


@app.get("/api/hello")
def hello():
    """最简单的连通性测试接口。"""
    return jsonify({"message": "你好"})


# ---------------------------------------------------------------------------
# API：会话
# ---------------------------------------------------------------------------


@app.post("/api/conversations")
def api_create_conversation():
    """新建会话。请求体可以省略，也可以带 {"title": "..."}。"""
    payload = request.get_json(silent=True)

    title = DEFAULT_CONVERSATION_TITLE
    if isinstance(payload, dict) and isinstance(payload.get("title"), str) and payload["title"].strip():
        title = payload["title"].strip()

    return jsonify(create_conversation(title)), 201


@app.get("/api/conversations")
def api_list_conversations():
    """返回会话列表，每项包含 id、标题和已有的问答轮数。"""
    summary = [
        {
            "id": conversation["id"],
            "title": conversation["title"],
            "turn_count": len(conversation["turns"]),
        }
        for conversation in conversations
    ]
    return jsonify(summary)


@app.get("/api/conversations/<int:conversation_id>")
def api_get_conversation(conversation_id):
    """返回某个会话的完整内容。"""
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": f"id 为 {conversation_id} 的会话不存在"}), 404

    return jsonify(conversation)


@app.patch("/api/conversations/<int:conversation_id>")
def api_rename_conversation(conversation_id):
    """重命名会话。"""
    payload = request.get_json(silent=True)
    if (
        not isinstance(payload, dict)
        or not isinstance(payload.get("title"), str)
        or not payload["title"].strip()
    ):
        return jsonify({"error": "请求体需要是 JSON，并且包含非空的 title 字段"}), 400

    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": f"id 为 {conversation_id} 的会话不存在"}), 404

    conversation["title"] = payload["title"].strip()
    save_conversations()
    return jsonify(conversation)


@app.delete("/api/conversations/<int:conversation_id>")
def api_delete_conversation(conversation_id):
    """删除会话，连同它的全部问答。"""
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": f"id 为 {conversation_id} 的会话不存在"}), 404

    conversations.remove(conversation)
    save_conversations()
    return jsonify({"deleted": conversation_id})


# ---------------------------------------------------------------------------
# API：会话里的问答
# ---------------------------------------------------------------------------


@app.post("/api/conversations/<int:conversation_id>/messages")
def api_create_turn(conversation_id):
    """在当前会话里提问：带上该会话的历史调用 DeepSeek，返回更新后的会话。"""
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": f"id 为 {conversation_id} 的会话不存在"}), 404

    question, error = read_message_text(request.get_json(silent=True))
    if error:
        return jsonify({"error": error}), 400

    try:
        add_turn(conversation, question)
    except RuntimeError as runtime_error:
        # 调用失败时返回清晰的 JSON 错误，而不是让 Flask 直接崩掉
        return jsonify({"error": str(runtime_error)}), 502

    return jsonify(conversation), 201


@app.patch("/api/conversations/<int:conversation_id>/turns/<int:turn_id>")
def api_update_turn(conversation_id, turn_id):
    """修改某一轮问答里的提问内容。"""
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": f"id 为 {conversation_id} 的会话不存在"}), 404

    turn = find_turn(conversation, turn_id)
    if turn is None:
        return jsonify({"error": f"该会话里没有 id 为 {turn_id} 的问答"}), 404

    question, error = read_message_text(request.get_json(silent=True))
    if error:
        return jsonify({"error": error}), 400

    turn["message"] = question
    save_conversations()
    return jsonify(conversation)


@app.delete("/api/conversations/<int:conversation_id>/turns/<int:turn_id>")
def api_delete_turn(conversation_id, turn_id):
    """删除某一轮问答。"""
    conversation = find_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": f"id 为 {conversation_id} 的会话不存在"}), 404

    turn = find_turn(conversation, turn_id)
    if turn is None:
        return jsonify({"error": f"该会话里没有 id 为 {turn_id} 的问答"}), 404

    conversation["turns"].remove(turn)
    save_conversations()
    return jsonify(conversation)


# ---------------------------------------------------------------------------
# API：兼容接口
# ---------------------------------------------------------------------------
# 下面四个接口是必做阶段那套“一次问答 = 一条记录”的接口，现在统一作用在默认会话上，
# 保持原有的路径和返回结构不变。前端已经改用上面的会话接口。


@app.post("/api/messages")
def api_create_message():
    """在默认会话里新增一轮问答，返回这一轮记录。"""
    question, error = read_message_text(request.get_json(silent=True))
    if error:
        return jsonify({"error": error}), 400

    conversation = get_default_conversation()
    try:
        turn = add_turn(conversation, question)
    except RuntimeError as runtime_error:
        return jsonify({"error": str(runtime_error)}), 502

    return jsonify(turn), 201


@app.get("/api/messages")
def api_list_messages():
    """返回默认会话里的全部问答记录。"""
    return jsonify(get_default_conversation()["turns"])


@app.patch("/api/messages/<int:message_id>")
def api_update_message(message_id):
    """修改默认会话里某一轮问答的提问内容。"""
    conversation = get_default_conversation()
    turn = find_turn(conversation, message_id)
    if turn is None:
        return jsonify({"error": f"id 为 {message_id} 的聊天记录不存在"}), 404

    question, error = read_message_text(request.get_json(silent=True))
    if error:
        return jsonify({"error": error}), 400

    turn["message"] = question
    save_conversations()
    return jsonify(turn)


@app.delete("/api/messages/<int:message_id>")
def api_delete_message(message_id):
    """删除默认会话里某一轮问答。"""
    conversation = get_default_conversation()
    turn = find_turn(conversation, message_id)
    if turn is None:
        return jsonify({"error": f"id 为 {message_id} 的聊天记录不存在"}), 404

    conversation["turns"].remove(turn)
    save_conversations()
    return jsonify({"deleted": message_id})


if __name__ == "__main__":
    app.run(port=5001, debug=True)
