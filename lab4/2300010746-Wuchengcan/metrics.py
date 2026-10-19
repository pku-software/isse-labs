from prometheus_client import Counter, Gauge, Histogram

# 两个 outcome 在第一次请求前就登记，错误还没出现时也能查询到 0。
chat_requests_total = Counter(
    "chat_requests_total",
    "已处理完成的聊天请求次数",
    ["outcome"],
)
chat_requests_total.labels(outcome="success").inc(0)
chat_requests_total.labels(outcome="error").inc(0)

chat_inprogress_requests = Gauge(
    "chat_inprogress_requests",
    "正在处理的聊天请求数",
)

# 覆盖约 0.1 秒的普通回复，以及数秒的慢回复。
chat_request_duration_seconds = Histogram(
    "chat_request_duration_seconds",
    "聊天请求的服务端处理耗时（秒）",
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 3, 5, 10, 30),
)
