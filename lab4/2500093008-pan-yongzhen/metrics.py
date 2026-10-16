"""仅统计聊天处理，不使用消息内容或用户身份作为标签。"""
from prometheus_client import Counter, Gauge, Histogram

CHAT_REQUESTS = Counter("chat_requests_total", "Completed chat requests", ["outcome"])
for outcome in ("success", "error"):
    CHAT_REQUESTS.labels(outcome=outcome)
CHAT_INPROGRESS = Gauge("chat_inprogress_requests", "Chat requests currently processing")
CHAT_DURATION = Histogram(
    "chat_request_duration_seconds", "Server-side chat duration in seconds",
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 3, 5, 10, 15),
)
