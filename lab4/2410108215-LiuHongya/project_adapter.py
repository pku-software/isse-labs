"""Project adapter for this student's chat application.

The scheduler does not assume /chat or /api/messages. These three functions
translate its generic actions into this project's actual HTTP endpoints.
"""

import json
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


ADAPTER_READY = True

STATUS_PATH = "/api/status"
CHAT_PATH = "/api/messages"


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _get_json(url: str, timeout: float):
    opener = build_opener(ProxyHandler({}), _NoRedirect())
    request = Request(url, method="GET")
    try:
        with opener.open(request, timeout=timeout) as response:
            code = response.status
            raw = response.read(1024 * 1024)
    except HTTPError as error:
        with error:
            code = error.code
            raw = error.read(1024 * 1024)
    except (URLError, TimeoutError, OSError):
        return None

    if code != 200:
        return None

    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def confirm_mock_mode(base_url: str, timeout: float) -> bool:
    """Check the live status endpoint, never assume mock mode locally."""
    url = base_url.rstrip("/") + STATUS_PATH
    data = _get_json(url, timeout)
    if not isinstance(data, dict):
        return False
    return data.get("mode") == "mock" and data.get("external_model_calls") is False


def build_chat_request(
    base_url: str, message: str, delay_seconds: float, force_error: bool
) -> Request:
    """Build a POST request for the original chat endpoint."""
    payload = {
        "message": message,
        "delay_seconds": delay_seconds,
        "force_error": bool(force_error),
    }
    data = json.dumps(payload).encode("utf-8")
    url = base_url.rstrip("/") + CHAT_PATH
    return Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )


def response_is_success(status_code: int, body: bytes) -> bool:
    """Return True only for a valid successful chat response."""
    if status_code != 201:
        return False

    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return False

    return isinstance(data, dict) and "reply" in data and "id" in data
