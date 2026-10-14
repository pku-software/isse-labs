"""Lab 4 业务指标定义。

只统计聊天处理流程，不包含 /metrics、状态接口与静态资源访问。
"""

from prometheus_client import Counter, Gauge, Histogram


chat_requests_total = Counter(
    "chat_requests_total",
    "聊天请求累计处理次数，按结果（success/error）区分",
    ["outcome"],
)

# 两种结果都先初始化，保证错误出现前也能查询到。
chat_requests_total.labels(outcome="success")
chat_requests_total.labels(outcome="error")

chat_inprogress_requests = Gauge(
    "chat_inprogress_requests",
    "当前正在处理的聊天请求数",
)

chat_request_duration_seconds = Histogram(
    "chat_request_duration_seconds",
    "聊天请求服务端处理耗时（秒），含模拟失败",
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 3.0, 5.0],
)
