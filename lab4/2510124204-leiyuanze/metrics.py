"""聊天应用的 Prometheus 指标定义（Lab 4）。

本模块只定义指标对象；真正的计数/计时发生在 app.py 的聊天请求处理流程里。
指标只统计聊天处理，不统计 /metrics、状态接口与静态资源访问。
"""

from prometheus_client import Counter, Gauge, Histogram

CHAT_REQUESTS = Counter(
    "chat_requests_total",
    "聊天请求处理累计次数，按结果区分",
    ["outcome"],
)
# 两种 outcome 先初始化为 0，方便错误出现前也能查询到序列。
CHAT_REQUESTS.labels(outcome="success")
CHAT_REQUESTS.labels(outcome="error")

CHAT_INPROGRESS = Gauge(
    "chat_inprogress_requests",
    "当前正在处理的聊天请求数量",
)

CHAT_REQUEST_DURATION = Histogram(
    "chat_request_duration_seconds",
    "聊天请求的服务端处理耗时（秒）",
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0, float("inf")),
)