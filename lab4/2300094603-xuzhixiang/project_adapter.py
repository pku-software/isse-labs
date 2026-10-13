"""HTTP adaptation for this Flask project's existing chat API."""

import ipaddress
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import (
    HTTPRedirectHandler,
    ProxyHandler,
    Request,
    build_opener,
)


# Set True only after the local status endpoint and chat request are verified.
ADAPTER_READY = True


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _local_base(base_url: str) -> str:
    parts = urlsplit(base_url)
    if (
        parts.scheme not in ("http", "https")
        or not parts.hostname
        or parts.username
        or parts.password
        or parts.query
        or parts.fragment
        or parts.path not in ("", "/")
    ):
        raise ValueError("base_url 必须是没有路径或凭据的本地 HTTP(S) 根地址")

    hostname = parts.hostname.lower()
    if hostname != "localhost":
        try:
            address = ipaddress.ip_address(hostname)
        except ValueError as error:
            raise ValueError("适配器只允许访问 localhost、127.0.0.1 或 ::1") from error
        if not address.is_loopback:
            raise ValueError("适配器只允许访问本机地址")
    return base_url.rstrip("/")


def confirm_mock_mode(base_url: str, timeout: float) -> bool:
    """Read the app's actual Lab 4 status endpoint without following redirects."""
    try:
        base = _local_base(base_url)
        request = Request(f"{base}/api/lab4/status", method="GET")
        opener = build_opener(ProxyHandler({}), _NoRedirect())
        with opener.open(request, timeout=timeout) as response:
            if response.status != 200:
                return False
            payload = json.loads(response.read(64 * 1024).decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, UnicodeDecodeError):
        return False

    return (
        isinstance(payload, dict)
        and payload.get("mode") == "mock"
        and payload.get("external_model_calls") is False
    )


def build_chat_request(
    base_url: str, message: str, delay_seconds: float, force_error: bool
) -> Request:
    """Translate a scheduled request to POST /api/messages for the Flask app."""
    base = _local_base(base_url)
    body = json.dumps(
        {
            "message": message,
            "lab4_delay_seconds": delay_seconds,
            "lab4_force_error": force_error,
        },
        ensure_ascii=False,
    ).encode("utf-8")
    return Request(
        f"{base}/api/messages",
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )


def response_is_success(status_code: int, body: bytes) -> bool:
    """Accept a valid chat reply, recognize the expected mock failure, reject others."""
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("聊天接口返回了无效 JSON") from error

    if not isinstance(payload, dict):
        raise ValueError("聊天接口 JSON 顶层必须是对象")

    if status_code == 201:
        message_id = payload.get("id")
        if (
            isinstance(message_id, int)
            and not isinstance(message_id, bool)
            and isinstance(payload.get("message"), str)
            and isinstance(payload.get("reply"), str)
            and payload["reply"].strip()
        ):
            return True
        raise ValueError("聊天成功响应缺少有效 id、message 或 reply")

    if (
        status_code == 503
        and isinstance(payload.get("error"), str)
        and payload["error"].strip() == "这是监控实验触发的模拟错误。"
    ):
        return False

    raise ValueError(f"聊天接口返回了非预期响应（HTTP {status_code}）")
