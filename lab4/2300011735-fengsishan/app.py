import math
import os
from threading import Lock
from time import sleep

from flask import Flask, Response, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from metrics import REGISTRY, track_chat

app = Flask(__name__, static_folder="frontend", static_url_path="")
app.json.ensure_ascii = False
app.config["CHAT_MODE"] = os.environ.get("CHAT_MODE", "mock").strip().lower()
if app.config["CHAT_MODE"] not in {"mock", "real"}:
    raise ValueError("CHAT_MODE must be mock or real")

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-flash"
MOCK_REPLY = "这是本地 mock 测试回复，未调用外部模型。"
MOCK_MAX_DELAY_SECONDS = 20

messages = []
next_message_id = 1
messages_lock = Lock()


def find_message(message_id):
    """Caller must hold messages_lock while accessing the returned record."""
    return next(
        (message for message in messages if message["id"] == message_id),
        None,
    )


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.get("/api/lab/status")
def lab_status():
    if app.config["CHAT_MODE"] != "mock":
        return jsonify({"error": "实验状态接口仅在 mock 模式开放"}), 404
    return jsonify({"mode": app.config["CHAT_MODE"], "external_model_calls": False})


@app.get("/metrics")
def metrics():
    return Response(generate_latest(REGISTRY), content_type=CONTENT_TYPE_LATEST)


@app.post("/api/messages")
@track_chat
def create_message():
    global next_message_id

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "请求体必须是 JSON 对象"}), 400

    message_text = data.get("message")
    if not isinstance(message_text, str) or not message_text.strip():
        return jsonify({"error": "message 必须是非空字符串"}), 400

    if app.config["CHAT_MODE"] == "mock":
        options = data.get("mock", {})
        if not isinstance(options, dict):
            return jsonify({"error": "mock 必须是 JSON 对象"}), 400
        delay = options.get("delay_seconds", 0.1)
        force_error = options.get("force_error", False)
        if (isinstance(delay, bool) or not isinstance(delay, (int, float))
                or not math.isfinite(delay) or not 0 <= delay <= MOCK_MAX_DELAY_SECONDS):
            return jsonify({"error": "mock.delay_seconds 必须在 0～20 秒之间"}), 400
        if not isinstance(force_error, bool):
            return jsonify({"error": "mock.force_error 必须是布尔值"}), 400
        sleep(delay)
        if force_error:
            return jsonify({"error": "本地模拟聊天失败", "code": "simulated_error"}), 503
        reply = MOCK_REPLY
    else:
        # Real mode is explicit. Mock mode never imports or creates the model client.
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            return jsonify({"error": "服务器未配置 DEEPSEEK_API_KEY"}), 503
        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)
            completion = client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[{"role": "user", "content": message_text.strip()}],
                stream=False,
                reasoning_effort="high",
                extra_body={"thinking": {"type": "enabled"}},
            )
            reply = completion.choices[0].message.content
            if not isinstance(reply, str) or not reply.strip():
                raise ValueError("DeepSeek returned an empty reply")
        except Exception as error:
            app.logger.error("DeepSeek API call failed: %s", type(error).__name__)
            return jsonify({"error": "DeepSeek API 调用失败，请稍后重试"}), 502

    with messages_lock:
        message = {"id": next_message_id, "message": message_text.strip(), "reply": reply.strip()}
        messages.append(message)
        next_message_id += 1
        result = message.copy()
    return jsonify(result), 201


@app.get("/api/messages")
def list_messages():
    with messages_lock:
        result = [message.copy() for message in messages]
    return jsonify(result)


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    with messages_lock:
        message = find_message(message_id)
        if message is None:
            return jsonify({"error": "聊天记录不存在"}), 404
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "请求体必须是 JSON 对象"}), 400
        message_text = data.get("message")
        if not isinstance(message_text, str) or not message_text.strip():
            return jsonify({"error": "message 必须是非空字符串"}), 400
        message["message"] = message_text.strip()
        result = message.copy()
    return jsonify(result)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    with messages_lock:
        message = find_message(message_id)
        if message is None:
            return jsonify({"error": "聊天记录不存在"}), 404
        messages.remove(message)
    return jsonify({"id": message_id, "message": "删除成功"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5001")),
            debug=False, threaded=True, use_reloader=False)
