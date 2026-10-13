"""Adapter for the personal Lab 4 copy of the Lab 3 Flask chat app."""

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


# Set True only after the status and success/error request checks pass.
ADAPTER_READY = True


class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, request, file_pointer, code, message, headers, new_url):
        return None


def _local_base_url(base_url: str) -> str:
    parsed = urlsplit(base_url)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("实验脚本只允许访问本机 HTTP 地址")
    if parsed.username or parsed.password:
        raise ValueError("本地地址中不能包含用户信息")
    return base_url.rstrip("/")


def confirm_mock_mode(base_url: str, timeout: float) -> bool:
    """Verify the live app reports mock mode and that model calls are disabled."""
    try:
        url = f"{_local_base_url(base_url)}/__lab4/status"
        request = Request(url, headers={"Accept": "application/json"}, method="GET")
        with build_opener(_NoRedirectHandler()).open(request, timeout=timeout) as response:
            if response.status != 200:
                return False
            payload = json.loads(response.read().decode("utf-8"))
        return (
            isinstance(payload, dict)
            and payload.get("mode") == "mock"
            and payload.get("external_model_calls") is False
        )
    except (OSError, ValueError, HTTPError, URLError, json.JSONDecodeError):
        return False


def build_chat_request(
    base_url: str, message: str, delay_seconds: float, force_error: bool
) -> Request:
    """Build a request for the original POST /api/messages chat endpoint."""
    url = f"{_local_base_url(base_url)}/api/messages"
    payload = {
        "message": message,
        "lab4_delay_seconds": delay_seconds,
        "lab4_force_error": force_error,
    }
    return Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
        },
        method="POST",
    )


def response_is_success(status_code: int, body: bytes) -> bool:
    """Accept only a created chat record with a non-empty mock reply."""
    if status_code != 201:
        return False
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return False
    return (
        isinstance(payload, dict)
        and isinstance(payload.get("id"), int)
        and not isinstance(payload.get("id"), bool)
        and isinstance(payload.get("message"), str)
        and isinstance(payload.get("reply"), str)
        and bool(payload["reply"].strip())
    )
