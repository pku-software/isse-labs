"""将课程调度器适配到个人 Flask 应用；只访问已核验的本机 mock 服务。"""

import ipaddress
import json
import threading
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


ADAPTER_READY = True
_confirmed_base = None
_timeout = 10.0
_workers = threading.local()


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def local_base(base_url):
    parts = urlsplit(base_url)
    if (parts.scheme not in ("http", "https") or not parts.hostname
            or parts.username or parts.password or parts.query or parts.fragment
            or parts.path not in ("", "/")):
        raise ValueError("目标必须是无凭据的本机服务根地址")
    if parts.hostname.lower() != "localhost":
        if not ipaddress.ip_address(parts.hostname).is_loopback:
            raise ValueError("仅允许本机地址")
    # 访问 port 属性同时检查非法端口。
    _ = parts.port
    return base_url.rstrip("/")


def opener():
    return build_opener(ProxyHandler({}), NoRedirect())


def read_json(response):
    body = response.read(1024 * 1024 + 1)
    if len(body) > 1024 * 1024:
        raise ValueError("响应过大")
    return json.loads(body)


def confirm_mock_mode(base_url: str, timeout: float) -> bool:
    """从实际 HTTP 状态接口核验，不跟随任何重定向。"""
    global _confirmed_base, _timeout, _workers
    _confirmed_base = None
    _workers = threading.local()
    try:
        base = local_base(base_url)
        with opener().open(base + "/api/lab/status", timeout=timeout) as response:
            state = read_json(response)
            confirmed = (response.status == 200 and isinstance(state, dict)
                         and state.get("mode") == "mock"
                         and state.get("external_model_calls") is False)
        if confirmed:
            _confirmed_base = base
            _timeout = timeout
        return confirmed
    except HTTPError as error:
        error.close()
        return False
    except (URLError, OSError, ValueError, TypeError):
        return False


def build_chat_request(
    base_url: str, message: str, delay_seconds: float, force_error: bool
) -> Request:
    """每个工作线程使用独立会话，避免同一会话的并发历史冲突。"""
    base = local_base(base_url)
    if base != _confirmed_base:
        raise ValueError("发送请求前必须通过 HTTP 核验此服务处于 mock 模式")
    conversation_id = getattr(_workers, "conversation_id", None)
    if conversation_id is None:
        create = Request(base + "/api/conversations", method="POST",
                         data=json.dumps({"title": "Lab4 模拟访问"}).encode("utf-8"),
                         headers={"Content-Type": "application/json"})
        with opener().open(create, timeout=_timeout) as response:
            result = read_json(response)
            if (response.status != 201 or not isinstance(result, dict)
                    or type(result.get("id")) is not int or result["id"] < 1):
                raise ValueError("创建模拟会话失败")
            conversation_id = result["id"]
        _workers.conversation_id = conversation_id
    payload = {"message": message, "mock_delay_seconds": delay_seconds,
               "mock_force_error": force_error}
    return Request(base + f"/api/conversations/{conversation_id}/messages", method="POST",
                   data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                   headers={"Content-Type": "application/json"})


def response_is_success(status_code: int, body: bytes) -> bool:
    """要求原接口的 HTTP 201、有效记录 ID 和非空回复；不输出正文。"""
    if status_code != 201:
        return False
    try:
        result = json.loads(body)
    except (ValueError, TypeError):
        return False
    return (isinstance(result, dict) and "error" not in result
            and type(result.get("id")) is int and result["id"] > 0
            and isinstance(result.get("message"), str)
            and isinstance(result.get("reply"), str) and bool(result["reply"].strip()))
