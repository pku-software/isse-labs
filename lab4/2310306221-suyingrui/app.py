import argparse
import json
import os
from pathlib import Path
import threading
import time

from flask import Flask, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from metrics import track_chat_request


app = Flask(__name__, static_folder="frontend", static_url_path="")
app.json.ensure_ascii = False
MODEL_MODE = os.environ.get("CHAT_MODE", "mock").strip().lower()
if MODEL_MODE not in {"mock", "real"}:
    raise ValueError("CHAT_MODE must be mock or real")
DATA_FILE = Path(__file__).parent / ".runtime" / "app" / "messages.json"
messages_lock = threading.RLock()


def load_messages():
    if not DATA_FILE.exists() or DATA_FILE.stat().st_size == 0:
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            records = json.load(file)
    except (OSError, json.JSONDecodeError):
        return []

    if not isinstance(records, list):
        return []

    return [
        record
        for record in records
        if isinstance(record, dict)
        and isinstance(record.get("id"), int)
        and isinstance(record.get("message"), str)
        and isinstance(record.get("reply"), str)
    ]


def save_messages():
    # Callers hold messages_lock. Replace atomically to avoid partial JSON files.
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary = DATA_FILE.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8") as file:
        json.dump(messages, file, ensure_ascii=False, indent=2)
    temporary.replace(DATA_FILE)


messages = load_messages()
next_message_id = max((record["id"] for record in messages), default=0) + 1


def error_response(message, status_code):
    return jsonify({"error": message}), status_code


def get_message_text(payload):
    if not isinstance(payload, dict):
        return None

    message = payload.get("message")
    if not isinstance(message, str) or not message.strip():
        return None

    return message.strip()


def find_message(message_id):
    return next((item for item in messages if item["id"] == message_id), None)


def get_ai_reply(message, payload):
    if MODEL_MODE == "mock":
        delay = payload.get("mock_delay", 0.1)
        force_error = payload.get("mock_error", False)
        if (
            isinstance(delay, bool)
            or not isinstance(delay, (int, float))
            or not 0 <= delay <= 30
            or not isinstance(force_error, bool)
        ):
            return None, error_response(
                "mock_delay must be 0..30 seconds and mock_error must be boolean", 400
            )
        time.sleep(delay)
        if force_error:
            return None, error_response("Simulated model failure", 503)
        return "这是本地模拟回复，未调用外部模型。", None

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return None, error_response("DeepSeek API key is not configured", 503)

    try:
        # Imported and constructed only in real mode; no .env file is loaded.
        from openai import OpenAI

        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        completion = client.chat.completions.create(
            model="deepseek-flash",
            messages=[{"role": "user", "content": message}],
        )
        reply = completion.choices[0].message.content
    except Exception:
        return None, error_response("DeepSeek request failed", 502)

    if not reply:
        return None, error_response("DeepSeek returned an empty reply", 502)

    return reply, None


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


@app.get("/api/lab/status")
def lab_status():
    if MODEL_MODE != "mock":
        return error_response("Lab status is only available in mock mode", 404)
    return jsonify({"mode": MODEL_MODE, "external_model_calls": False})


@app.get("/metrics")
def metrics():
    return app.response_class(generate_latest(), content_type=CONTENT_TYPE_LATEST)


@app.post("/api/messages")
@track_chat_request
def create_message():
    global next_message_id

    payload = request.get_json(silent=True)
    message = get_message_text(payload)
    if message is None:
        return error_response("message must be a non-empty string", 400)

    # Never hold the storage lock while waiting for a model response.
    reply, failure_response = get_ai_reply(message, payload)
    if failure_response is not None:
        return failure_response

    with messages_lock:
        record = {"id": next_message_id, "message": message, "reply": reply}
        messages.append(record)
        try:
            save_messages()
        except OSError:
            messages.pop()
            return error_response("Unable to save message", 500)

        next_message_id += 1
        return jsonify(record), 201


@app.get("/api/messages")
def list_messages():
    with messages_lock:
        return jsonify(messages)


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    message = get_message_text(request.get_json(silent=True))
    if message is None:
        return error_response("message must be a non-empty string", 400)

    with messages_lock:
        record = find_message(message_id)
        if record is None:
            return error_response("message not found", 404)
        previous_message = record["message"]
        record["message"] = message
        try:
            save_messages()
        except OSError:
            record["message"] = previous_message
            return error_response("Unable to save message", 500)

        return jsonify(record)


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    with messages_lock:
        record = find_message(message_id)
        if record is None:
            return error_response("message not found", 404)

        record_index = messages.index(record)
        messages.pop(record_index)
        try:
            save_messages()
        except OSError:
            messages.insert(record_index, record)
            return error_response("Unable to save message", 500)

        return jsonify({"message": "deleted", "id": message_id})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Local Lab 4 chat application")
    parser.add_argument("--port", type=int, default=5001)
    args = parser.parse_args()
    app.run(host="127.0.0.1", port=args.port, debug=False, threaded=True,
            use_reloader=False, load_dotenv=False)
