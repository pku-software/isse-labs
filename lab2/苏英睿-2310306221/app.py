from flask import Flask, jsonify


app = Flask(__name__)
app.json.ensure_ascii = False


@app.get("/api/hello")
def hello():
    return jsonify({"message": "你好"})


def not_implemented():
    """Return the temporary response used by the CRUD route skeletons."""
    return jsonify({"error": "Not implemented", "detail": "TODO: implement message storage."}), 501


@app.post("/api/messages")
def create_message():
    return not_implemented()


@app.get("/api/messages")
def list_messages():
    return not_implemented()


@app.patch("/api/messages/<int:message_id>")
def update_message(message_id):
    return not_implemented()


@app.delete("/api/messages/<int:message_id>")
def delete_message(message_id):
    return not_implemented()


if __name__ == "__main__":
    app.run(port=5001, debug=True)
