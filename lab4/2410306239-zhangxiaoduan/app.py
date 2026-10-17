import json
import os
import threading
import time

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from openai import OpenAI

import metrics

# 读取个人目录下的 .env 文件，把其中的变量（如 DEEPSEEK_API_KEY）加载为环境变量
load_dotenv()

# 实验模式：mock（默认，固定测试回复、不需要 Key）或 real（沿用 Lab 2/3 的 DeepSeek 调用）
APP_MODE = os.getenv("APP_MODE", "mock")
if APP_MODE not in ("mock", "real"):
    APP_MODE = "mock"

# mock 模式允许的最大后端延迟（秒），防止实验选项把服务长时间阻塞
MOCK_MAX_DELAY_SECONDS = 5.0


class ChatError(Exception):
    """聊天处理中需要以明确状态码返回给客户端的问题"""

    def __init__(self, message, status):
        super().__init__(message)
        self.message = message
        self.status = status

app = Flask(__name__, static_folder="frontend", static_url_path="")
# 保证 JSON 响应中的中文直接显示，不被转义为 \uXXXX
app.json.ensure_ascii = False

# 只有 real 模式才创建 DeepSeek 客户端；mock 模式不创建、不调用外部模型，也不需要 Key。
# Key 只存在于后端环境变量中，不会出现在代码里，也不会返回给浏览器。
client = None
if APP_MODE == "real":
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


# 会话存储在多个线程间共享，写入前用同一把锁保护，避免并发修改互相覆盖
conversations_lock = threading.Lock()


def generate_reply(history_messages, data):
    """按当前模式生成回复。

    mock：固定测试回复，可带实验延迟与强制失败选项，不调用真实模型；
    real：沿用 Lab 2/3 的行为，携带历史调用 DeepSeek。
    """
    if APP_MODE == "mock":
        delay = float(data.get("delay_seconds") or 0)
        time.sleep(min(max(delay, 0.0), MOCK_MAX_DELAY_SECONDS))
        if data.get("force_error"):
            raise ChatError("模拟失败：请求携带 force_error 选项", 503)
        return "（模拟回复）当前是 mock 模式，未调用真实模型。"
    if client is None:
        raise ChatError("未配置 DEEPSEEK_API_KEY，请检查 .env 文件", 500)
    return call_deepseek_with_history(history_messages, data["message"])


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


@app.route("/api/mode")
def mode_status():
    """实验专用状态接口：按实际配置报告运行模式，供访问脚本核验"""
    return jsonify({
        "mode": APP_MODE,
        "external_model_calls": APP_MODE == "real" and client is not None,
    })


@app.route("/metrics")
def metrics_endpoint():
    """以 Prometheus 文本格式返回当前全部指标"""
    return metrics.metrics_response()


@app.route("/api/conversations", methods=["POST"])
def create_conversation():
    """创建一个新会话"""
    global next_conversation_id
    data = request.get_json(silent=True) or {}
    title = data.get("title") or "新会话"
    with conversations_lock:
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
    with conversations_lock:
        conv["title"] = data["title"]
        save_conversations()
    return jsonify(conv)


@app.route("/api/conversations/<int:conversation_id>", methods=["DELETE"])
def delete_conversation(conversation_id):
    """删除指定会话"""
    conv = find_conversation(conversation_id)
    if conv is None:
        return jsonify({"error": f"ID 为 {conversation_id} 的会话不存在"}), 404
    with conversations_lock:
        conversations.remove(conv)
        save_conversations()
    return jsonify({"deleted": conv})


@app.route("/api/conversations/<int:conversation_id>/messages", methods=["POST"])
def create_conversation_message(conversation_id):
    """在指定会话中发送一条消息：mock 模式返回固定回复，real 模式调用 DeepSeek。

    无论成功、模拟失败还是意外异常，三个指标都会正确收尾。
    """
    global next_message_id
    metrics.chat_inprogress_requests.inc()
    started = time.monotonic()
    try:
        conv = find_conversation(conversation_id)
        if conv is None:
            raise ChatError(f"ID 为 {conversation_id} 的会话不存在", 404)
        data = request.get_json(silent=True)
        if not data or not data.get("message"):
            raise ChatError("缺少 message 字段", 400)
        reply = generate_reply(conv["messages"], data)
        with conversations_lock:
            record = {"id": next_message_id, "message": data["message"], "reply": reply}
            conv["messages"].append(record)
            next_message_id += 1
            save_conversations()
        metrics.chat_requests_total.labels(outcome="success").inc()
        return jsonify(conv), 201
    except ChatError as e:
        metrics.chat_requests_total.labels(outcome="error").inc()
        return jsonify({"error": e.message}), e.status
    except Exception as e:
        # 模型调用等意外失败时返回清晰的 JSON 错误，不让 Flask 直接崩溃
        metrics.chat_requests_total.labels(outcome="error").inc()
        return jsonify({"error": f"调用模型失败：{e}"}), 502
    finally:
        metrics.chat_inprogress_requests.dec()
        metrics.chat_request_duration_seconds.observe(time.monotonic() - started)


if __name__ == "__main__":
    # 单进程 + 多线程：慢聊天请求期间 /metrics 仍能响应。
    # 关闭 debug 重载器，避免两个进程各自维护一套指标。
    app.run(host="127.0.0.1", port=5001, threaded=True, debug=False)
