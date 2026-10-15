"""项目适配点：把课程访问调度器接到本人的聊天应用（Lab 4）。

三个适配函数都经过真实 HTTP 单请求验证后才启用 ADAPTER_READY。
适配依据：
- 聊天接口：POST /api/conversations/<会话id>/messages，JSON 字段 message；
- 实验选项：delay_seconds（0~10，模拟后端耗时）、force_error（模拟失败），只在 mock 模式生效；
- 状态接口：GET /api/status 返回 {"mode": "mock", "external_model_calls": false}。
"""

import ipaddress
import json
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

ADAPTER_READY = True

# 访问脚本每个阶段都向同一个会话追加消息，固定使用第一个会话。
CONVERSATION_ID = 1


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _local_origin(base_url: str):
    """与调度器一致的本地地址检查，避免把凭据或外部主机带进请求。"""
    parts = urlsplit(base_url)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise ValueError("目标必须为本地 http/https 地址")
    if parts.username or parts.password or parts.query or parts.fragment:
        raise ValueError("地址不得包含凭据、查询参数或片段")
    host = parts.hostname.lower()
    if host != "localhost":
        try:
            is_local = ipaddress.ip_address(host).is_loopback
        except ValueError:
            is_local = False
        if not is_local:
            raise ValueError("本实验仅访问 localhost、127.0.0.1 或 ::1")
    return parts.scheme, host, parts.port or (443 if parts.scheme == "https" else 80)


def confirm_mock_mode(base_url: str, timeout: float) -> bool:
    """ADAPT 1：通过实际 HTTP GET 核验应用正在使用模拟模型。"""
    scheme, host, port = _local_origin(base_url)
    status_url = f"{scheme}://{host}:{port}/api/status"
    request = Request(status_url, method="GET")
    try:
        opener = build_opener(ProxyHandler({}), _NoRedirect())
        with opener.open(request, timeout=timeout) as response:
            if response.status != 200:
                return False
            payload = json.loads(response.read(65536).decode("utf-8"))
    except Exception:
        return False

    return (
        isinstance(payload, dict)
        and payload.get("mode") == "mock"
        and payload.get("external_model_calls") is False
    )


def build_chat_request(
    base_url: str, message: str, delay_seconds: float, force_error: bool
) -> Request:
    """ADAPT 2：构造访问本人聊天接口的 urllib.request.Request。"""
    scheme, host, port = _local_origin(base_url)
    chat_url = (
        f"{scheme}://{host}:{port}"
        f"/api/conversations/{CONVERSATION_ID}/messages"
    )
    payload = {
        "message": message,
        "delay_seconds": delay_seconds,
        "force_error": force_error,
    }
    return Request(
        chat_url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
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
        and isinstance(payload.get("reply"), str)
        and payload["reply"].strip() != ""
    )