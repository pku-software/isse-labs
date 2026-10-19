"""将课程访问调度器适配到本项目的 Flask 聊天 HTTP 接口。"""

import json
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


# 调度器仍会在每次运行前通过 HTTP 核验 mock 模式。
ADAPTER_READY = True


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def confirm_mock_mode(base_url: str, timeout: float) -> bool:
    """读取实际状态接口；拒绝重定向、错误响应和未明确禁用外部调用的服务。"""
    request = Request(base_url.rstrip("/") + "/api/lab-status",
                      headers={"Accept": "application/json"}, method="GET")
    opener = build_opener(ProxyHandler({}), _NoRedirect())
    try:
        with opener.open(request, timeout=timeout) as response:
            if response.status != 200:
                return False
            status = json.load(response)
    except (OSError, ValueError):
        return False
    return (isinstance(status, dict) and status.get("mode") == "mock"
            and status.get("external_model_calls") is False)


def build_chat_request(
    base_url: str, message: str, delay_seconds: float, force_error: bool
) -> Request:
    """通过原 /api/messages 接口发送固定测试消息及后端模拟参数。"""
    body = json.dumps({
        "message": message,
        "mock_delay_seconds": delay_seconds,
        "mock_force_error": force_error,
    }, ensure_ascii=False).encode("utf-8")
    return Request(base_url.rstrip("/") + "/api/messages", data=body,
                   headers={"Content-Type": "application/json", "Accept": "application/json"},
                   method="POST")


def response_is_success(status_code: int, body: bytes) -> bool:
    """HTTP 201 且 JSON 包含非空 reply、没有 error 字段才算成功。"""
    if status_code != 201:
        return False
    try:
        response = json.loads(body)
    except (ValueError, TypeError):
        return False
    if not isinstance(response, dict) or "error" in response:
        return False
    reply = response.get("reply")
    return isinstance(reply, str) and bool(reply.strip())
