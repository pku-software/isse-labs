"""项目适配点：把课程调度器翻译为本项目（Flask 聊天应用）的实际 HTTP 调用。

调度器不假设学生使用 /chat 还是 /api/messages，也不假设 JSON 字段。
本适配器只处理个人副本；禁止用随机修改指标代替 HTTP 访问，禁止填入真实 API Key。
"""

import json
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener, urlopen

# 三个适配函数实现并通过单请求验证后，由 Agent 改成 True。
ADAPTER_READY = True

# 模拟期间复用的测试会话 id：在 confirm_mock_mode 核验通过后创建一次
_test_conversation_id = None

_MODE_PATH = "/api/mode"
_CONVERSATIONS_PATH = "/api/conversations"


class _NoRedirect(HTTPRedirectHandler):
    """禁止状态接口请求跟随重定向，避免被带离本机"""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise HTTPError(req.full_url, code, "状态接口不允许重定向", headers, fp)


def _open_no_redirect(request, timeout):
    return build_opener(_NoRedirect()).open(request, timeout=timeout)


def confirm_mock_mode(base_url: str, timeout: float) -> bool:
    """ADAPT 1：通过实际 HTTP GET 核验应用正在使用模拟模型。

    读取实验专用状态接口 /api/mode，确认 mode 为 mock 且 external_model_calls
    为 false（内容由后端按实际配置生成）。核验通过后再创建一个测试会话，
    供 build_chat_request 复用。失败或出现重定向时返回 False。
    """
    global _test_conversation_id
    try:
        request = Request(base_url + _MODE_PATH, method="GET")
        with _open_no_redirect(request, timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if data.get("mode") != "mock" or data.get("external_model_calls") is not False:
            return False
        # 核验通过：创建一次测试会话（后续消息都发到这个会话里）
        body = json.dumps({"title": "监控模拟测试会话"}).encode("utf-8")
        request = Request(
            base_url + _CONVERSATIONS_PATH,
            data=body,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with _open_no_redirect(request, timeout) as resp:
            conv = json.loads(resp.read().decode("utf-8"))
        _test_conversation_id = conv["id"]
        return True
    except Exception:
        return False


def build_chat_request(
    base_url: str, message: str, delay_seconds: float, force_error: bool
) -> Request:
    """ADAPT 2：构造访问本项目聊天接口的 urllib.request.Request。

    POST /api/conversations/<测试会话>/messages，JSON 携带 message 以及
    mock 模式的 delay_seconds / force_error 实验选项；延迟发生在后端，
    不用客户端 sleep 冒充。消息只使用脚本提供的非敏感测试文本。
    """
    payload = {"message": message}
    if delay_seconds:
        payload["delay_seconds"] = delay_seconds
    if force_error:
        payload["force_error"] = True
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    url = f"{base_url}/api/conversations/{_test_conversation_id}/messages"
    return Request(
        url, data=body, method="POST", headers={"Content-Type": "application/json"}
    )


def response_is_success(status_code: int, body: bytes) -> bool:
    """ADAPT 3：结合 HTTP 状态和实际 JSON 判断聊天业务是否成功。

    成功 = 2xx 且 JSON 是会话对象、最后一条消息有非空 reply；
    模拟错误（503）与其他无效响应都判为失败。只判断，不输出聊天正文。
    """
    if not 200 <= status_code < 300:
        return False
    try:
        data = json.loads(body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return False
    if not isinstance(data, dict):
        return False
    messages = data.get("messages")
    if not isinstance(messages, list) or not messages:
        return False
    last = messages[-1]
    return isinstance(last.get("reply"), str) and bool(last["reply"])
