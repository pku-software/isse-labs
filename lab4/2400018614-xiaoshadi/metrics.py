"""Lab 4 监控指标：只统计聊天请求的处理过程。

三个指标分别回答三个问题：

- Counter：到目前为止处理了多少次聊天请求，成功和失败各多少；
- Gauge：此刻有多少个聊天请求正在处理中（会随请求开始/结束上下浮动）；
- Histogram：每次聊天处理的服务端耗时分布。

指标在这里集中定义，app.py 在处理聊天请求时更新它们；
/metrics 接口按 prometheus_client 的标准格式把当前数值返回给 Prometheus。
"""

from prometheus_client import Counter, Gauge, Histogram

# 聊天请求的累计处理次数，按结果区分；两种 outcome 先初始化为 0，
# 这样在第一次失败出现之前，查询里也能看到 error 这条时间序列。
CHAT_REQUESTS = Counter(
    "chat_requests_total",
    "聊天请求处理完成的总次数",
    ["outcome"],
)
CHAT_REQUESTS.labels(outcome="success")
CHAT_REQUESTS.labels(outcome="error")

# 当前正在处理、尚未结束的聊天请求数量。开始处理时加一，结束时减一，
# 因此它是"此刻"的瞬时值，会在慢请求期间明显升高。
CHAT_INPROGRESS = Gauge(
    "chat_inprogress_requests",
    "当前正在处理的聊天请求数量",
)

# 聊天处理的服务端耗时（秒）。桶覆盖很短的请求和数秒的慢请求，
# 便于用 sum/count 求平均，也保留分布信息。
CHAT_DURATION = Histogram(
    "chat_request_duration_seconds",
    "聊天请求的服务端处理耗时（秒）",
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0),
)
