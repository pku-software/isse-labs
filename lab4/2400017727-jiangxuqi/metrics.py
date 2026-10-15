"""聊天业务指标：不包含静态资源、状态检查或指标采集。"""
from prometheus_client import Counter, Gauge, Histogram

REQUESTS = Counter("chat_requests_total", "Completed chat requests", ["outcome"])
for outcome in ("success", "error"):
    REQUESTS.labels(outcome=outcome)
INPROGRESS = Gauge("chat_inprogress_requests", "Chat requests currently being processed")
DURATION = Histogram(
    "chat_request_duration_seconds", "Server chat processing duration in seconds",
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 3, 5, 10, 15),
)
