"""Prometheus metrics for the chat request path."""

from prometheus_client import Counter, Gauge, Histogram


CHAT_REQUESTS = Counter(
    "chat_requests_total",
    "Completed chat requests grouped by outcome.",
    ("outcome",),
)
CHAT_INPROGRESS = Gauge(
    "chat_inprogress_requests",
    "Chat requests currently being processed.",
)
CHAT_REQUEST_DURATION = Histogram(
    "chat_request_duration_seconds",
    "Server-side duration of chat request processing.",
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 10.0),
)

# Expose both series before the first request so PromQL can find them immediately.
for outcome in ("success", "error"):
    CHAT_REQUESTS.labels(outcome=outcome).inc(0)
