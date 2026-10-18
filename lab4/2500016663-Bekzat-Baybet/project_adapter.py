"""项目适配点：把课程调度器的通用动作翻译成本聊天应用的 HTTP 请求。

调度器不假设学生使用 /chat 还是 /api/messages，也不假设 JSON 字段，
这些差异全部由本文件消化。禁止用随机修改指标代替 HTTP 访问，禁止填入真实 API Key。

对应本项目（Lab 2/3 的 Flask 聊天应用）：
- 状态接口  GET  /api/status   ->  {"mode": "mock", "external_model_calls": false}
- 聊天接口  POST /api/messages ->  请求 {"message", "delay_seconds", "force_error"}
                                  成功 201 {"id", "message", "reply"}
                                  模拟失败 503 {"error"}
"""

import json
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


# 三个适配函数实现并通过单请求验证后，由 Agent 改成 True。
ADAPTER_READY = True


class _NoRedirect(HTTPRedirectHandler):
    """核验状态接口时不允许跟随重定向，避免被引导到其他主机。"""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def confirm_mock_mode(base_url: str, timeout: float) -> bool:
    """ADAPT 1：通过实际 HTTP GET 核验应用正在使用模拟模型。

    读取 /api/status，只有服务确实报告 mock 模式、且明确声明没有外部模型调用时
    才返回 True；请求失败、响应不是预期结构、或服务处于 real 模式时一律返回 False。
    """
    request = Request(f"{base_url}/api/status", method="GET")
    try:
        opener = build_opener(ProxyHandler({}), _NoRedirect())
        with opener.open(request, timeout=timeout) as response:
            if response.status != 200:
                return False
            status = json.loads(response.read(64 * 1024).decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, UnicodeDecodeError):
        return False

    if not isinstance(status, dict):
        return False
    # 必须是精确的 False，0 或缺失都不算通过。
    return status.get("mode") == "mock" and status.get("external_model_calls") is False


def build_chat_request(
    base_url: str, message: str, delay_seconds: float, force_error: bool
) -> Request:
    """ADAPT 2：构造访问本项目聊天接口的 urllib.request.Request。

    走原应用的 POST /api/messages，请求体沿用原来的 message 字段，
    另外带上后端在 mock 模式下识别的 delay_seconds 与 force_error 实验选项。
    延迟由后端在处理期间真实消耗，客户端这里不做 sleep。
    """
    body = json.dumps(
        {
            "message": message,
            "delay_seconds": delay_seconds,
            "force_error": bool(force_error),
        }
    ).encode("utf-8")

    return Request(
        f"{base_url}/api/messages",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )


def response_is_success(status_code: int, body: bytes) -> bool:
    """ADAPT 3：结合 HTTP 状态和实际 JSON 判断聊天业务是否成功。

    201 且响应里带非空 reply 才算成功；模拟失败返回 503，其余状态一律算失败。
    只做判断，不输出聊天正文。
    """
    if status_code != 201:
        return False

    try:
        payload = json.loads(body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return False

    if not isinstance(payload, dict):
        return False

    reply = payload.get("reply")
    return isinstance(reply, str) and bool(reply.strip())
