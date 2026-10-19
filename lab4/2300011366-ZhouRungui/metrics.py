"""指标定义：只跟踪聊天创建请求，不把指标采集和静态资源访问算进去。"""

from prometheus_client import Counter, Gauge, Histogram


CHAT_REQUESTS = Counter(
    "chat_requests_total",
    "Total chat creation requests by outcome.",
    labelnames=("outcome",),
)
for _outcome in ("success", "error"):
    CHAT_REQUESTS.labels(outcome=_outcome)

CHAT_IN_PROGRESS = Gauge(
    "chat_inprogress_requests",
    "Number of chat creation requests currently being processed.",
)

CHAT_REQUEST_DURATION = Histogram(
    "chat_request_duration_seconds",
    "Time spent processing each chat creation request in seconds.",
    buckets=(0.1, 0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0),
)
