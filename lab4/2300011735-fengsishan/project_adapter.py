"""项目适配点：由 Coding Agent 读完学生应用后补齐，仅修改个人副本。

调度器不假设学生使用 /chat 还是 /api/messages，也不假设 JSON 字段。
禁止用随机修改指标代替 HTTP 访问，禁止在此填入真实 API Key。
"""

import ipaddress
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


# 已通过真实 HTTP mock 核验、正常/失败单请求和 real 模式拒绝检查。
ADAPTER_READY = True


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def local_base_url(base_url: str) -> str:
    """The adapter independently rejects remote hosts and non-root URLs."""
    parts = urlsplit(base_url)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise ValueError("目标必须为本地 HTTP/HTTPS 地址")
    if parts.username or parts.password or parts.query or parts.fragment or parts.path not in ("", "/"):
        raise ValueError("目标必须为不含凭据、查询参数或片段的服务根地址")
    if parts.hostname.lower() != "localhost":
        try:
            is_local = ipaddress.ip_address(parts.hostname).is_loopback
        except ValueError:
            is_local = False
        if not is_local:
            raise ValueError("本实验只访问本机服务")
    # Validate port syntax before constructing a request.
    _ = parts.port
    return base_url.rstrip("/")


def confirm_mock_mode(base_url: str, timeout: float) -> bool:
    """ADAPT 1：通过实际 HTTP GET 核验应用正在使用模拟模型。

    Agent 在应用增加只在实验模式生效的状态接口，然后在此读取它。
    推荐状态 JSON：{"mode": "mock", "external_model_calls": false}。
    只有当前服务确实处于 mock 模式且禁用外部模型调用，才返回 True。
    不得直接 return True，也不能仅检查客户端环境变量或打印一行文字。
    读取状态接口时禁止跟随到其他主机的重定向；失败时返回 False 或报错。
    """
    try:
        target = local_base_url(base_url) + "/api/lab/status"
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
    """ADAPT 2：构造访问学生实际聊天接口的 urllib.request.Request。

    由 Agent 填写路径、HTTP 方法、Content-Type 和实际 JSON 字段。
    模拟延迟/失败选项须由后端在实验模式下处理；延迟发生在后端，
    不用客户端 sleep 冒充接口变慢。正常请求仍经过应用的聊天处理逻辑。
    消息只使用脚本提供的非敏感测试文本，不携带 API Key。
    """
    target = local_base_url(base_url) + "/api/messages"
    body = json.dumps({
        "message": message,
        "mock": {"delay_seconds": delay_seconds, "force_error": force_error},
    }, ensure_ascii=False).encode("utf-8")
    return Request(target, data=body, method="POST", headers={"Content-Type": "application/json"})


def response_is_success(status_code: int, body: bytes) -> bool:
    """ADAPT 3：结合 HTTP 状态和实际 JSON 判断聊天业务是否成功。

    应识别有效回复、模拟错误及无效响应，不能只要有响应就返回 True。
    推荐模拟错误返回 503 和明确的错误 JSON。只判断，不输出聊天正文。
    """
    if status_code != 201:
        return False
    try:
        record = json.loads(body)
    except (ValueError, UnicodeDecodeError):
        return False
    if not isinstance(record, dict) or "error" in record:
        return False
    return (isinstance(record.get("id"), int) and not isinstance(record["id"], bool)
            and record["id"] > 0 and isinstance(record.get("message"), str)
            and bool(record["message"].strip()) and isinstance(record.get("reply"), str)
            and bool(record["reply"].strip()))
