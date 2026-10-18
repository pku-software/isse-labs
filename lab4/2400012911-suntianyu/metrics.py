"""Metrics for the original chat creation endpoint."""

from prometheus_client import Counter, Gauge, Histogram


CHAT_REQUESTS = Counter(
    "chat_requests_total",
    "Completed chat requests by outcome.",
    ["outcome"],
)
for outcome in ("success", "error"):
    CHAT_REQUESTS.labels(outcome=outcome)

CHAT_INPROGRESS = Gauge(
    "chat_inprogress_requests",
    "Chat requests currently being processed.",
)

CHAT_DURATION = Histogram(
    "chat_request_duration_seconds",
    "Server-side chat request duration in seconds.",
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 3, 5, 10),
)
