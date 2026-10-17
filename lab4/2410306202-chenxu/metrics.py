"""Lab 4 监控指标定义。"""

from prometheus_client import Counter, Gauge, Histogram

CHAT_REQUESTS_TOTAL = Counter(
    "chat_requests_total",
    "聊天请求处理完成的总次数",
    ["outcome"],
)
CHAT_REQUESTS_TOTAL.labels(outcome="success")
CHAT_REQUESTS_TOTAL.labels(outcome="error")

CHAT_INPROGRESS_REQUESTS = Gauge(
    "chat_inprogress_requests",
    "当前正在处理的聊天请求数量",
)

CHAT_REQUEST_DURATION_SECONDS = Histogram(
    "chat_request_duration_seconds",
    "聊天请求的服务端处理耗时（秒）",
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0),
)
