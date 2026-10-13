"""项目适配点：由 Coding Agent 读完学生应用后补齐，仅修改个人副本。

调度器不假设学生使用 /chat 还是 /api/messages，也不假设 JSON 字段。
禁止用随机修改指标代替 HTTP 访问，禁止在此填入真实 API Key。
"""

from urllib.request import Request


# 三个适配函数实现并通过单请求验证后，由 Agent 改成 True。
ADAPTER_READY = False


def confirm_mock_mode(base_url: str, timeout: float) -> bool:
    """ADAPT 1：通过实际 HTTP GET 核验应用正在使用模拟模型。

    Agent 在应用增加只在实验模式生效的状态接口，然后在此读取它。
    推荐状态 JSON：{"mode": "mock", "external_model_calls": false}。
    只有当前服务确实处于 mock 模式且禁用外部模型调用，才返回 True。
    不得直接 return True，也不能仅检查客户端环境变量或打印一行文字。
    读取状态接口时禁止跟随到其他主机的重定向；失败时返回 False 或报错。
    """
    raise NotImplementedError("请先实现 ADAPT 1：核验当前服务的模拟模式")


def build_chat_request(
    base_url: str, message: str, delay_seconds: float, force_error: bool
) -> Request:
    """ADAPT 2：构造访问学生实际聊天接口的 urllib.request.Request。

    由 Agent 填写路径、HTTP 方法、Content-Type 和实际 JSON 字段。
    模拟延迟/失败选项须由后端在实验模式下处理；延迟发生在后端，
    不用客户端 sleep 冒充接口变慢。正常请求仍经过应用的聊天处理逻辑。
    消息只使用脚本提供的非敏感测试文本，不携带 API Key。
    """
    raise NotImplementedError("请先实现 ADAPT 2：聊天接口和请求正文")


def response_is_success(status_code: int, body: bytes) -> bool:
    """ADAPT 3：结合 HTTP 状态和实际 JSON 判断聊天业务是否成功。

    应识别有效回复、模拟错误及无效响应，不能只要有响应就返回 True。
    推荐模拟错误返回 503 和明确的错误 JSON。只判断，不输出聊天正文。
    """
    raise NotImplementedError("请先实现 ADAPT 3：成功/失败响应判断")
