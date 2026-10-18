"""项目适配点：把课程调度器的通用动作翻译成本项目的 HTTP 请求。

调度器不假设学生使用 /chat 还是 /api/messages，也不假设 JSON 字段；
本文件按个人项目的实际接口填写，已通过单请求验证。

本项目接口：
- GET  /api/status   实验状态接口，返回 {"mode": ..., "external_model_calls": ...}
- POST /api/messages 聊天接口，请求 {"message": ..., "delay_seconds": ..., "force_error": ...}
  成功返回 201 和 {"id": ..., "message": ..., "reply": ...}；
  模拟失败返回 503 和 {"error": ...}

禁止用随机修改指标代替 HTTP 访问，禁止在此填入真实 API Key。
"""

import json
from urllib.parse import urlsplit
from urllib.request import (
    HTTPRedirectHandler,
    ProxyHandler,
    Request,
    build_opener,
)


class _NoRedirect(HTTPRedirectHandler):
    """拒绝重定向，防止状态检查被带到其他主机。"""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


# 三个适配函数实现并通过单请求验证后，由 Agent 改成 True。
ADAPTER_READY = True


def _read_json(url, timeout):
    """GET 一个本地地址并按 JSON 解析；不跟随重定向，不做代理。"""
    opener = build_opener(ProxyHandler({}), _NoRedirect())
    with opener.open(url, timeout=timeout) as response:
        if urlsplit(response.geturl())[:2] != urlsplit(url)[:2]:
            raise ValueError("响应不是来自请求的本地地址")
        body = response.read(64 * 1024)
    return json.loads(body.decode("utf-8"))


def confirm_mock_mode(base_url: str, timeout: float) -> bool:
    """ADAPT 1：通过实际 HTTP GET 核验应用正在使用模拟模型。

    只有状态接口明确报告 mode=mock 且 external_model_calls=false 才返回 True；
    real 模式、接口不可达或返回内容不符合预期都返回 False，
    调度器会因此拒绝发送聊天请求。
    """
    try:
        status = _read_json(base_url.rstrip("/") + "/api/status", timeout)
    except Exception:
        return False

    return (
        isinstance(status, dict)
        and status.get("mode") == "mock"
        and status.get("external_model_calls") is False
    )


def build_chat_request(
    base_url: str, message: str, delay_seconds: float, force_error: bool
) -> Request:
    """ADAPT 2：构造访问本项目聊天接口的请求。

    路径为 /api/messages，JSON 字段与本项目 app.py 一致；
    delay_seconds 与 force_error 只在后端 mock 模式下生效，
    延迟由后端在处理期间真实等待，不是客户端 sleep 冒充。
    """
    payload = {
        "message": message,
        "delay_seconds": delay_seconds,
        "force_error": bool(force_error),
    }
    return Request(
        base_url.rstrip("/") + "/api/messages",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )


def response_is_success(status_code: int, body: bytes) -> bool:
    """ADAPT 3：根据 HTTP 状态和响应 JSON 判断聊天是否成功。

    本项目成功时返回 201 且 reply 为非空字符串；
    503 模拟错误、400 校验错误以及其他状态都算失败。只判断，不输出正文。
    """
    if status_code != 201:
        return False

    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return False

    if not isinstance(data, dict):
        return False
    reply = data.get("reply")
    return isinstance(reply, str) and bool(reply.strip())
