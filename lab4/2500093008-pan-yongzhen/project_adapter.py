"""课程调度器到本项目 HTTP 接口的适配，不直接操作指标。"""
import ipaddress
import json
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import Request, HTTPRedirectHandler, ProxyHandler, build_opener

ADAPTER_READY = True


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def local_base(base_url):
    parts = urlsplit(base_url)
    if (parts.scheme not in ("http", "https") or not parts.hostname
            or parts.username or parts.password or parts.query or parts.fragment
            or parts.path not in ("", "/")):
        raise ValueError("必须使用不含凭据的本机服务根地址")
    if parts.hostname.lower() != "localhost":
        if not ipaddress.ip_address(parts.hostname).is_loopback:
            raise ValueError("仅允许本机地址")
    return base_url.rstrip("/")


def confirm_mock_mode(base_url: str, timeout: float) -> bool:
    """实际 GET 状态接口；禁止代理和重定向，严格核验两个状态字段。"""
    try:
        req = Request(local_base(base_url) + "/api/lab/status", method="GET")
        opener = build_opener(ProxyHandler({}), NoRedirect())
        with opener.open(req, timeout=timeout) as response:
            if response.status != 200:
                return False
            data = json.loads(response.read(65536))
        return (isinstance(data, dict) and data.get("mode") == "mock"
                and data.get("external_model_calls") is False)
    except (URLError, OSError, ValueError):
        return False


def build_chat_request(
    base_url: str, message: str, delay_seconds: float, force_error: bool
) -> Request:
    """访问原有兼容聊天入口，延迟与失败由后端 mock 分支处理。"""
    body = {"message": message, "mock_delay_seconds": delay_seconds,
            "mock_force_error": force_error}
    return Request(local_base(base_url) + "/api/messages",
                   data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
                   headers={"Content-Type": "application/json"}, method="POST")


def response_is_success(status_code: int, body: bytes) -> bool:
    """只将原接口的 201 与有效回复判为成功，不打印正文。"""
    if status_code != 201:
        return False
    try:
        data = json.loads(body)
    except (ValueError, UnicodeError):
        return False
    return (isinstance(data, dict) and "error" not in data
            and type(data.get("id")) is int and data["id"] > 0
            and isinstance(data.get("reply"), str) and bool(data["reply"].strip())
            and isinstance(data.get("message"), str) and bool(data["message"].strip()))
