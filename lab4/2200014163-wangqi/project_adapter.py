"""项目适配点：把课程访问调度器接到本人的聊天应用（Lab 4）。

三个适配函数都通过真实 HTTP 请求验证后才启用 ADAPTER_READY。
适配依据（王琪 2200014163 的项目）：
- 聊天接口：POST /api/conversations/<会话id>/messages，JSON 字段 message；
- 实验选项：delay_seconds（0~10，mock 模式后端真实 sleep）、force_error（mock 模式模拟失败）；
- 状态接口：GET /api/experiment/status 返回 {"mode": "mock", "external_model_calls": false}；
- 成功响应：HTTP 201 且 body 为 {"id": int, "role": "assistant", "content": "..."}。
"""

import json
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


# 三个适配函数实现并通过单请求验证后，由 Agent 改成 True。
ADAPTER_READY = True

_CONVERSATION_ID = None


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _request_json(request: Request, timeout: float):
    """发送一次适配设置请求；不使用代理、不跟随重定向。"""
    opener = build_opener(ProxyHandler({}), _NoRedirect())
    try:
        with opener.open(request, timeout=timeout) as response:
            status_code = response.status
            body = response.read(1024 * 1024)
    except HTTPError as error:
        with error:
            status_code = error.code
            body = error.read(1024 * 1024)
    except (URLError, TimeoutError, OSError):
        return None, None

    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return status_code, None
    return status_code, payload


def confirm_mock_mode(base_url: str, timeout: float) -> bool:
    """ADAPT 1：通过实际 HTTP GET 核验应用正在使用模拟模型，并准备一个会话。"""
    global _CONVERSATION_ID

    base_url = base_url.rstrip("/")
    status_code, payload = _request_json(
        Request(f"{base_url}/api/experiment/status", method="GET"), timeout
    )
    if not (
        status_code == 200
        and isinstance(payload, dict)
        and payload.get("mode") == "mock"
        and payload.get("external_model_calls") is False
    ):
        return False

    # 复用已有会话，没有则创建一个供后续聊天请求使用。
    status_code, conversations = _request_json(
        Request(f"{base_url}/api/conversations", method="GET"), timeout
    )
    if status_code == 200 and isinstance(conversations, list):
        valid_ids = [
            item.get("id")
            for item in conversations
            if isinstance(item, dict)
            and isinstance(item.get("id"), int)
            and not isinstance(item.get("id"), bool)
            and item["id"] > 0
        ]
        if valid_ids:
            _CONVERSATION_ID = valid_ids[0]
            return True

    request_body = json.dumps(
        {"title": "Lab 4 流量模拟"}, ensure_ascii=False
    ).encode("utf-8")
    status_code, conversation = _request_json(
        Request(
            f"{base_url}/api/conversations",
            data=request_body,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        ),
        timeout,
    )
    if not (
        status_code == 201
        and isinstance(conversation, dict)
        and isinstance(conversation.get("id"), int)
        and not isinstance(conversation.get("id"), bool)
        and conversation["id"] > 0
    ):
        return False
    _CONVERSATION_ID = conversation["id"]
    return True


def build_chat_request(
    base_url: str, message: str, delay_seconds: float, force_error: bool
) -> Request:
    """ADAPT 2：构造访问本人聊天接口的 urllib.request.Request。"""
    if _CONVERSATION_ID is None:
        raise RuntimeError("请先调用 confirm_mock_mode 完成会话准备")

    request_body = json.dumps(
        {
            "message": message,
            "delay_seconds": delay_seconds,
            "force_error": force_error,
        },
        ensure_ascii=False,
    ).encode("utf-8")
    return Request(
        f"{base_url.rstrip('/')}/api/conversations/{_CONVERSATION_ID}/messages",
        data=request_body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )


def response_is_success(status_code: int, body: bytes) -> bool:
    """ADAPT 3：结合 HTTP 状态和实际 JSON 判断聊天业务是否成功。"""
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
        and payload.get("role") == "assistant"
        and isinstance(payload.get("content"), str)
        and bool(payload["content"].strip())
    )
