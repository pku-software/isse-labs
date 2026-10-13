"""将课程调度器接到本项目的 mock 状态接口和原有聊天接口。"""

import json
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


# 已通过实际 mock 状态、非 mock 拒绝及正常/强制失败的单请求验证。
ADAPTER_READY = True


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def confirm_mock_mode(base_url: str, timeout: float) -> bool:
    """实际读取状态；连接失败、重定向或非明确 mock 状态均拒绝。"""
    request = Request(base_url.rstrip("/") + "/api/lab/status",
                      headers={"Accept": "application/json"}, method="GET")
    opener = build_opener(ProxyHandler({}), NoRedirect())
    try:
        with opener.open(request, timeout=timeout) as response:
            if response.status != 200:
                return False
            body = response.read(65537)
            if len(body) > 65536:
                return False
            status = json.loads(body)
    except HTTPError as error:
        error.close()
        return False
    except (URLError, OSError, ValueError, UnicodeError):
        return False
    return (isinstance(status, dict) and status.get("mode") == "mock"
            and status.get("external_model_calls") is False)


def build_chat_request(
    base_url: str, message: str, delay_seconds: float, force_error: bool
) -> Request:
    """通过原 POST /api/messages 接口请求，延迟和失败由后端执行。"""
    body = json.dumps({
        "message": message,
        "mock": {"delay_seconds": delay_seconds, "force_error": force_error},
    }, ensure_ascii=False, allow_nan=False).encode("utf-8")
    return Request(base_url.rstrip("/") + "/api/messages", data=body,
                   headers={"Content-Type": "application/json",
                            "Accept": "application/json"}, method="POST")


def response_is_success(status_code: int, body: bytes) -> bool:
    """成功应为 HTTP 201 和有效聊天记录；错误响应或空回复均失败。"""
    if status_code != 201:
        return False
    try:
        record = json.loads(body)
    except (ValueError, UnicodeError):
        return False
    return (isinstance(record, dict) and "error" not in record
            and type(record.get("id")) is int and record["id"] > 0
            and isinstance(record.get("message"), str) and bool(record["message"].strip())
            and isinstance(record.get("reply"), str) and bool(record["reply"].strip()))
