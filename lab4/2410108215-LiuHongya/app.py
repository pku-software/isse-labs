from pathlib import Path
import json
import os
import threading
import time

import requests
from flask import Flask, Response, jsonify, request, send_from_directory
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

import metrics

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__)
app.json.ensure_ascii = False

FRONTEND_DIR = str(BASE_DIR / "frontend")
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "messages.json"

APP_MODE = os.getenv("APP_MODE", "mock").lower()
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"
MAX_MOCK_DELAY_SECONDS = 8.0

messages = []
next_id = 1
MESSAGES_LOCK = threading.Lock()


def load_messages():
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        return []

    if not isinstance(data, list):
        return []

    return [record for record in data if isinstance(record, dict)]


def persist_messages_unlocked():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(messages, file, ensure_ascii=False, indent=2)


def get_deepseek_reply(message):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DeepSeek API Key is not configured")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [{"role": "user", "content": message}],
        "stream": False,
    }

    response = requests.post(
        DEEPSEEK_API_URL,
        headers=headers,
        json=payload,
        timeout=30,
    )
    if response.status_code != 200:
        raise RuntimeError("DeepSeek model call failed")

    try:
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError):
        raise RuntimeError("DeepSeek returned an unexpected format")


def get_mock_reply(_message):
    return "This is a local mock reply."


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/style.css")
def style_css():
    return send_from_directory(FRONTEND_DIR, "style.css")


@app.get("/app.js")
def app_js():
    return send_from_directory(FRONTEND_DIR, "app.js")


@app.get("/api/hello")
def hello():
    return jsonify({"message": "hello"})


@app.get("/api/status")
def status():
    return jsonify({
        "mode": APP_MODE,
        "external_model_calls": APP_MODE != "mock",
    })


@app.get("/metrics")
def metrics_endpoint():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.post("/api/messages")
def create_message():
    global next_id

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not str(data.get("message", "")).strip():
        return jsonify({"error": "message cannot be empty"}), 400

    user_message = str(data["message"]).strip()

    if APP_MODE == "mock":
        try:
            delay_seconds = float(data.get("delay_seconds", 0.0))
        except (TypeError, ValueError):
            return jsonify({"error": "delay_seconds must be a number"}), 400
        force_error = data.get("force_error", False)
        if not isinstance(force_error, bool):
            return jsonify({"error": "force_error must be a boolean"}), 400
    else:
        delay_seconds = 0.0
        force_error = False

    if not 0 <= delay_seconds <= MAX_MOCK_DELAY_SECONDS:
        return jsonify({"error": "delay_seconds is outside the allowed range"}), 400

    started = time.perf_counter()
    metrics.CHAT_INPROGRESS.inc()
    outcome = "success"

    try:
        if APP_MODE == "mock":
            if delay_seconds:
                time.sleep(delay_seconds)
            if force_error:
                outcome = "error"
                return jsonify({"error": "simulated chat failure"}), 503
            reply = get_mock_reply(user_message)
        else:
            reply = get_deepseek_reply(user_message)

        record = {
            "id": None,
            "message": user_message,
            "reply": reply,
        }
        with MESSAGES_LOCK:
            record["id"] = next_id
            messages.append(record)
            next_id += 1
            persist_messages_unlocked()
        return jsonify(record), 201
    except Exception:
        outcome = "error"
        return jsonify({"error": "chat request failed"}), 502
    finally:
        metrics.CHAT_DURATION.observe(time.perf_counter() - started)
        metrics.CHAT_INPROGRESS.dec()
        metrics.CHAT_REQUESTS.labels(outcome=outcome).inc()


@app.get("/api/messages")
def list_messages():
    with MESSAGES_LOCK:
        snapshot = list(messages)
    return jsonify(snapshot)


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not str(data.get("message", "")).strip():
        return jsonify({"error": "message cannot be empty"}), 400

    new_message = str(data["message"]).strip()
    with MESSAGES_LOCK:
        for record in messages:
            if record["id"] == message_id:
                record["message"] = new_message
                persist_messages_unlocked()
                return jsonify(record)

    return jsonify({"error": "message not found"}), 404


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    with MESSAGES_LOCK:
        for index, record in enumerate(messages):
            if record["id"] == message_id:
                del messages[index]
                persist_messages_unlocked()
                return jsonify({"deleted": message_id})

    return jsonify({"error": "message not found"}), 404


messages = load_messages()
next_id = max((int(record.get("id", 0)) for record in messages), default=0) + 1


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False, threaded=True)
