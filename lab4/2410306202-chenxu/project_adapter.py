"""项目适配点：把课程调度脚本的通用动作翻译成本项目的 HTTP 请求。

对应应用：本目录下的 Flask 聊天应用（Lab 2/3 应用 + Lab 4 指标与 mock 模式）。

- 状态接口：`GET /api/status`，如实返回当前模式与是否调用外部模型。
- 聊天接口：`POST /api/messages`，是应用原有的聊天接口（兼容接口），
  自动作用在默认会话上，返回这一轮问答记录，请求体为 `{"message": "..."}`。
- 实验选项：请求体里的 `delay_seconds` / `force_error`，只在 mock 模式生效，
  延迟由后端在处理期间真正等待。

脚本只通过 HTTP 访问应用，不直接读写指标；这里也不保存任何 Key。
"""

import json
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


# 三个适配函数实现并通过单请求验证后由 Agent 改成 True。
ADAPTER_READY = True

STATUS_PATH = "/api/status"
CHAT_PATH = "/api/messages"


class NoRedirect(HTTPRedirectHandler):
    """拒绝跟随重定向，避免状态检查被引到其他主机。"""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def confirm_mock_mode(base_url: str, timeout: float) -> bool:
    """ADAPT 1：通过实际 HTTP GET 核验应用正在使用模拟模型。

    只有状态接口确实返回 mock、且明确外部模型调用关闭时才返回 True；
    读取失败、被重定向或内容不符都返回 False。
    """
    status_url = base_url.rstrip("/") + STATUS_PATH

    try:
        opener = build_opener(ProxyHandler({}), NoRedirect())
        with opener.open(Request(status_url, method="GET"), timeout=timeout) as response:
            if response.status != 200:
                return False
            body = response.read(64 * 1024)
    except (HTTPError, URLError, TimeoutError, OSError, ValueError):
        return False

    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return False

    if not isinstance(payload, dict):
        return False

    return payload.get("mode") == "mock" and payload.get("external_model_calls") is False


def build_chat_request(
    base_url: str, message: str, delay_seconds: float, force_error: bool
) -> Request:
    """ADAPT 2：构造访问本项目聊天接口的 urllib 请求。

    走应用原有的聊天处理逻辑；模拟延迟与失败选项交给后端在实验模式下处理，
    不在客户端 sleep 冒充接口变慢，也不携带任何 Key。
    """
    url = base_url.rstrip("/") + CHAT_PATH
    payload = {
        "message": message,
        "delay_seconds": max(0.0, float(delay_seconds)),
        "force_error": bool(force_error),
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    return Request(
        url,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )


def response_is_success(status_code: int, body: bytes) -> bool:
    """ADAPT 3：结合 HTTP 状态和实际 JSON 判断聊天业务是否成功。

    本项目成功时返回 201 和这一轮问答记录；模拟失败返回 503 与错误 JSON，
    其他状态或无法解析的内容都算失败。只判断，不输出聊天正文。
    """
    if status_code != 201:
        return False

    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return False

    if not isinstance(payload, dict):
        return False

    reply = payload.get("reply")
    return isinstance(payload.get("id"), int) and isinstance(reply, str) and bool(reply.strip())
