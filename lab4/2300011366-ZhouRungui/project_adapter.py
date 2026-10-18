"""Map the Lab 4 traffic scheduler onto this Flask application's HTTP API."""

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import HTTPRedirectHandler, Request, build_opener


# Keep False until the adapter has passed the required single-request check.
ADAPTER_READY = True

STATUS_PATH = "/api/lab4/status"
CHAT_PATH = "/api/messages"


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _local_endpoint(base_url: str, path: str) -> str:
    return urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))


def confirm_mock_mode(base_url: str, timeout: float) -> bool:
    """Read the running app's mode endpoint and verify external calls are off."""
    req = Request(
        _local_endpoint(base_url, STATUS_PATH),
        headers={"Accept": "application/json"},
        method="GET",
    )
    try:
        with build_opener(_NoRedirect).open(req, timeout=timeout) as response:
            if response.status != 200:
                return False
            status = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, UnicodeDecodeError):
        return False
    return (
        isinstance(status, dict)
        and status.get("mode") == "mock"
        and status.get("external_model_calls") is False
    )


def build_chat_request(
    base_url: str, message: str, delay_seconds: float, force_error: bool
) -> Request:
    """Build a JSON POST to the existing chat endpoint with mock-only controls."""
    body = json.dumps(
        {
            "message": message,
            "delay_seconds": delay_seconds,
            "force_error": force_error,
        },
        ensure_ascii=False,
    ).encode("utf-8")
    return Request(
        _local_endpoint(base_url, CHAT_PATH),
        data=body,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
        },
        method="POST",
    )


def response_is_success(status_code: int, body: bytes) -> bool:
    """Accept only a successful HTTP response with a non-empty reply field."""
    if status_code not in {200, 201}:
        return False
    try:
        payload = json.loads(body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return False
    return (
        isinstance(payload, dict)
        and isinstance(payload.get("reply"), str)
        and bool(payload["reply"].strip())
    )
