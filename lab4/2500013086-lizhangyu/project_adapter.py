"""Adapter for the Lab 4 traffic scheduler and Li Zhangyu's Flask chat app."""

import json
import threading
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


# Set True only after mock verification and both chat outcomes have been checked.
ADAPTER_READY = True


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _local_origin(base_url: str):
    parts = urlsplit(base_url)
    if parts.scheme != "http" or parts.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("Lab 4 adapter accepts only a local HTTP service")
    if parts.username or parts.password or parts.query or parts.fragment:
        raise ValueError("base URL must not contain credentials, query, or fragment")
    return parts


def _open(request: Request, timeout: float):
    opener = build_opener(ProxyHandler({}), NoRedirect())
    try:
        with opener.open(request, timeout=timeout) as response:
            return response.status, response.read(1024 * 1024)
    except HTTPError as error:
        with error:
            return error.code, error.read(1024 * 1024)


def confirm_mock_mode(base_url: str, timeout: float) -> bool:
    """Read the app's real runtime status; fail closed for errors or redirects."""
    try:
        parts = _local_origin(base_url)
        url = parts._replace(path="/api/lab4/status", query="", fragment="").geturl()
        status, body = _open(Request(url, method="GET"), timeout)
        payload = json.loads(body.decode("utf-8"))
        return (
            status == 200
            and isinstance(payload, dict)
            and payload.get("mode") == "mock"
            and payload.get("external_model_calls") is False
        )
    except (OSError, URLError, ValueError, json.JSONDecodeError):
        return False


_conversation_lock = threading.Lock()
_conversation_ids = {}


def _get_conversation_id(base_url: str, timeout: float = 10) -> int:
    """Create one dedicated simulation conversation per local app/run process."""
    key = base_url.rstrip("/")
    with _conversation_lock:
        if key in _conversation_ids:
            return _conversation_ids[key]
        payload = json.dumps({"title": "Lab 4 监控模拟"}, ensure_ascii=False).encode("utf-8")
        request = Request(
            key + "/api/conversations",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        status, body = _open(request, timeout)
        if status != 201:
            raise RuntimeError("Could not create a Lab 4 simulation conversation")
        response = json.loads(body.decode("utf-8"))
        conversation_id = response.get("id") if isinstance(response, dict) else None
        if isinstance(conversation_id, bool) or not isinstance(conversation_id, int):
            raise RuntimeError("The conversation API returned an invalid ID")
        _conversation_ids[key] = conversation_id
        return conversation_id


def build_chat_request(
    base_url: str, message: str, delay_seconds: float, force_error: bool
) -> Request:
    """Build the original conversation-message HTTP request in mock mode."""
    parts = _local_origin(base_url)
    conversation_id = _get_conversation_id(base_url)
    payload = {
        "message": message,
        "lab4_delay_seconds": delay_seconds,
        "lab4_force_error": force_error,
    }
    url = parts._replace(
        path=f"/api/conversations/{conversation_id}/messages", query="", fragment=""
    ).geturl()
    return Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )


def response_is_success(status_code: int, body: bytes) -> bool:
    """Accept only a successful Flask response with a non-empty assistant reply."""
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return False
    if status_code != 201 or not isinstance(payload, dict):
        return False
    assistant = payload.get("assistant_message")
    return (
        isinstance(assistant, dict)
        and isinstance(assistant.get("content"), str)
        and bool(assistant["content"].strip())
    )
