"""Lab 4 监控指标定义。

只统计聊天处理本身：Prometheus 周期访问的 /metrics、状态接口和前端静态资源
都不计入聊天数量，也不把消息内容、姓名、请求 ID 之类的信息放进标签。
"""

from prometheus_client import Counter, Gauge, Histogram

# 聊天请求处理完成的总次数，按结果区分成功与失败。
CHAT_REQUESTS = Counter(
    "chat_requests_total",
    "聊天请求处理完成的总次数",
    ["outcome"],
)

# 预先为两个 outcome 各创建一次实例，让它们在错误出现前就能被查询到。
CHAT_REQUESTS.labels(outcome="success")
CHAT_REQUESTS.labels(outcome="error")

# 当前正在处理中的聊天请求数量：开始处理时加一，处理结束（含异常）时减一。
CHAT_INPROGRESS = Gauge(
    "chat_inprogress_requests",
    "正在处理中的聊天请求数量",
)

# 聊天处理的服务端耗时（秒）。桶覆盖 baseline 的 0.1 秒和 slow 阶段的数秒慢请求。
CHAT_DURATION = Histogram(
    "chat_request_duration_seconds",
    "聊天请求的服务端处理耗时（秒）",
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0),
)
