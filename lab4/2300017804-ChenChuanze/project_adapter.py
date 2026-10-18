"""把课程调度器的动作转换为本项目的 mock 聊天 HTTP 请求。"""

import json
from urllib.error import URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


# 已通过真实 HTTP 的 mock 核验、成功请求及强制失败验证。
ADAPTER_READY = True


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def confirm_mock_mode(base_url: str, timeout: float) -> bool:
    """读取实际状态接口；关闭系统代理和重定向，核验失败则拒绝发请求。"""
    request = Request(
        base_url.rstrip("/") + "/api/status",
        headers={"Accept": "application/json"},
        method="GET",
    )
    opener = build_opener(ProxyHandler({}), NoRedirect())
    try:
        with opener.open(request, timeout=timeout) as response:
            if response.status != 200:
                return False
            body = response.read(16 * 1024 + 1)
            if len(body) > 16 * 1024:
                return False
            status = json.loads(body)
    except (URLError, OSError, ValueError):
        return False
    return (
        isinstance(status, dict)
        and status.get("mode") == "mock"
        and status.get("external_model_calls") is False
    )


def build_chat_request(
    base_url: str, message: str, delay_seconds: float, force_error: bool
) -> Request:
    """使用原单消息接口，延迟和模拟失败由后端执行。"""
    body = json.dumps(
        {"message": message, "mock_delay": delay_seconds, "mock_error": force_error},
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return Request(
        base_url.rstrip("/") + "/api/messages",
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )


def response_is_success(status_code: int, body: bytes) -> bool:
    """成功须为 HTTP 201 和完整聊天记录；错误或无效正文返回 False。"""
    if status_code != 201:
        return False
    try:
        record = json.loads(body)
    except (ValueError, TypeError):
        return False
    return (
        isinstance(record, dict)
        and "error" not in record
        and record.get("code") != "mock_error"
        and type(record.get("id")) is int
        and record["id"] > 0
        and isinstance(record.get("message"), str)
        and bool(record["message"].strip())
        and isinstance(record.get("reply"), str)
        and bool(record["reply"].strip())
    )
