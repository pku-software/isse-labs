"""Only chat creation requests contribute to these business metrics."""

from prometheus_client import Counter, Gauge, Histogram

CHAT_REQUESTS = Counter(
    "chat_requests_total", "Completed chat requests", ["outcome"]
)
for outcome in ("success", "error"):
    CHAT_REQUESTS.labels(outcome=outcome)

CHAT_INPROGRESS = Gauge("chat_inprogress_requests", "Chat requests being processed")
CHAT_DURATION = Histogram(
    "chat_request_duration_seconds", "Server-side chat processing time",
    buckets=(0.05, 0.1, 0.2, 0.5, 1, 2, 3, 5, 10, 20, 30),
)
