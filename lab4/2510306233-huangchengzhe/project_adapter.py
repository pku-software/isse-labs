"""项目适配点：已根据黄诚哲的 Flask 聊天应用补齐，仅用于个人副本。

应用接口：
- 状态接口：GET /api/lab-status -> {"mode":"mock","external_model_calls":false}
- 聊天接口：POST /api/conversations/<id>/messages
  请求体 {"message": str, "delay": float, "fail": bool}
  成功返回 201 + 会话 JSON；模拟错误返回 503 + {"error": ...}
"""

import ipaddress
import json
import threading
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


# 三个适配函数实现并通过单请求验证后，由 Agent 改成 True。
ADAPTER_READY = True

_conversation_id = None
_conversation_lock = threading.Lock()


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def local_base_url(base_url: str) -> str:
    """校验并归一化本机服务根地址。"""
    parts = urlsplit(base_url)
    if (parts.scheme not in ("http", "https") or not parts.hostname
            or parts.username or parts.password or parts.query or parts.fragment
            or parts.path not in ("", "/")):
        raise ValueError("仅允许不含凭据、查询参数或片段的本地服务根地址")
    if parts.hostname.lower() != "localhost":
        try:
            local = ipaddress.ip_address(parts.hostname).is_loopback
        except ValueError:
            local = False
        if not local:
            raise ValueError("本实验仅访问本机服务")
    _ = parts.port
    return base_url.rstrip("/")


def _ensure_conversation(base_url: str, timeout: float = 10.0) -> int:
    """为监控实验创建（并缓存）一个专用会话，消息需要挂在会话下。"""
    global _conversation_id
    if _conversation_id is not None:
        return _conversation_id
    with _conversation_lock:
        if _conversation_id is not None:
            return _conversation_id
        target = local_base_url(base_url) + "/api/conversations"
        body = json.dumps({"title": "监控实验会话"}, ensure_ascii=False).encode("utf-8")
        request = Request(target, data=body, method="POST",
                          headers={"Content-Type": "application/json"})
        opener = build_opener(ProxyHandler({}), NoRedirect())
        with opener.open(request, timeout=timeout) as response:
            record = json.loads(response.read(65536))
        _conversation_id = int(record["id"])
        return _conversation_id


def confirm_mock_mode(base_url: str, timeout: float) -> bool:
    """ADAPT 1：通过实际 HTTP GET 核验应用正在使用模拟模型。"""
    try:
        target = local_base_url(base_url) + "/api/lab-status"
        opener = build_opener(ProxyHandler({}), NoRedirect())
        with opener.open(Request(target, method="GET"), timeout=timeout) as response:
            if response.status != 200:
                return False
            state = json.loads(response.read(65536))
        return (isinstance(state, dict) and state.get("mode") == "mock"
                and state.get("external_model_calls") is False)
    except (HTTPError, URLError, TimeoutError, OSError, ValueError):
        return False


def build_chat_request(
    base_url: str, message: str, delay_seconds: float, force_error: bool
) -> Request:
    """ADAPT 2：构造访问聊天接口的 urllib.request.Request。"""
    base = local_base_url(base_url)
    conversation_id = _ensure_conversation(base)
    target = f"{base}/api/conversations/{conversation_id}/messages"
    body = json.dumps({
        "message": message,
        "delay": delay_seconds,
        "fail": force_error,
    }, ensure_ascii=False).encode("utf-8")
    return Request(target, data=body, method="POST",
                   headers={"Content-Type": "application/json"})


def response_is_success(status_code: int, body: bytes) -> bool:
    """ADAPT 3：结合 HTTP 状态和实际 JSON 判断聊天业务是否成功。"""
    if status_code != 201:
        return False
    try:
        record = json.loads(body)
    except (ValueError, UnicodeDecodeError):
        return False
    if not isinstance(record, dict) or "error" in record:
        return False
    return (isinstance(record.get("id"), int) and not isinstance(record["id"], bool)
            and record["id"] > 0 and isinstance(record.get("messages"), list))
