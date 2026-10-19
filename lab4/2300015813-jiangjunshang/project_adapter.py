"""项目适配点：由 Coding Agent 读完学生应用后补齐，仅修改个人副本。

调度器不假设学生使用 /chat 还是 /api/messages，也不假设 JSON 字段。
禁止用随机修改指标代替 HTTP 访问，禁止在此填入真实 API Key。
"""

import ipaddress
import json
from threading import local
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


# 三个适配函数实现并通过单请求验证后，由 Agent 改成 True。
ADAPTER_READY = True
_thread_state = local()


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def local_base(base_url):
    """Validate before the adapter itself makes any preparatory HTTP request."""
    parts = urlsplit(base_url)
    if (
        parts.scheme not in ("http", "https")
        or not parts.hostname
        or parts.username is not None
        or parts.password is not None
        or parts.path not in ("", "/")
        or parts.query
        or parts.fragment
    ):
        raise ValueError("需要不含凭据的本地服务根地址")
    if parts.hostname.lower() != "localhost":
        if not ipaddress.ip_address(parts.hostname).is_loopback:
            raise ValueError("仅允许访问本机")
    _ = parts.port  # Reject malformed ports before any HTTP request.
    return base_url.rstrip("/")


def open_json(request, timeout):
    opener = build_opener(ProxyHandler({}), NoRedirect())
    with opener.open(request, timeout=timeout) as response:
        return json.loads(response.read(1024 * 1024))


def confirm_mock_mode(base_url: str, timeout: float) -> bool:
    """ADAPT 1：通过实际 HTTP GET 核验应用正在使用模拟模型。

    Agent 在应用增加只在实验模式生效的状态接口，然后在此读取它。
    推荐状态 JSON：{"mode": "mock", "external_model_calls": false}。
    只有当前服务确实处于 mock 模式且禁用外部模型调用，才返回 True。
    不得直接 return True，也不能仅检查客户端环境变量或打印一行文字。
    读取状态接口时禁止跟随到其他主机的重定向；失败时返回 False 或报错。
    """
    try:
        base = local_base(base_url)
        status = open_json(Request(base + "/api/lab/status"), timeout)
        return (
            isinstance(status, dict)
            and status.get("mode") == "mock"
            and status.get("external_model_calls") is False
        )
    except (URLError, OSError, ValueError):
        return False


def build_chat_request(
    base_url: str, message: str, delay_seconds: float, force_error: bool
) -> Request:
    """ADAPT 2：构造访问学生实际聊天接口的 urllib.request.Request。

    由 Agent 填写路径、HTTP 方法、Content-Type 和实际 JSON 字段。
    模拟延迟/失败选项须由后端在实验模式下处理；延迟发生在后端，
    不用客户端 sleep 冒充接口变慢。正常请求仍经过应用的聊天处理逻辑。
    消息只使用脚本提供的非敏感测试文本，不携带 API Key。
    """
    base = local_base(base_url)
    # A pool worker sends requests sequentially and owns its conversation.
    # Reusing it avoids per-chat setup writes without sharing concurrent
    # conversation history between workers. CRUD is not a chat metric.
    if not hasattr(_thread_state, "conversations"):
        _thread_state.conversations = {}
    if base not in _thread_state.conversations:
        create = Request(
            base + "/api/conversations",
            data=json.dumps({"title": "Lab4 traffic test"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        conversation = open_json(create, timeout=10)
        if not isinstance(conversation, dict) or type(conversation.get("id")) is not int or conversation["id"] < 1:
            raise ValueError("测试会话创建响应无效")
        _thread_state.conversations[base] = conversation["id"]
    conversation_id = _thread_state.conversations[base]
    body = {
        "message": message,
        "mock_delay_seconds": delay_seconds,
        "mock_force_error": force_error,
    }
    return Request(
        base + f"/api/conversations/{conversation_id}/messages",
        data=json.dumps(body, ensure_ascii=False, allow_nan=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )


def response_is_success(status_code: int, body: bytes) -> bool:
    """ADAPT 3：结合 HTTP 状态和实际 JSON 判断聊天业务是否成功。

    应识别有效回复、模拟错误及无效响应，不能只要有响应就返回 True。
    推荐模拟错误返回 503 和明确的错误 JSON。只判断，不输出聊天正文。
    """
    try:
        result = json.loads(body)
    except (ValueError, UnicodeError):
        return False
    return (
        status_code == 201
        and isinstance(result, dict)
        and "error" not in result
        and type(result.get("id")) is int
        and result["id"] > 0
        and isinstance(result.get("message"), str)
        and bool(result["message"].strip())
        and isinstance(result.get("reply"), str)
        and bool(result["reply"].strip())
    )
