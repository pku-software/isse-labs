from prometheus_client import Counter, Gauge, Histogram

CHAT_REQUESTS = Counter(
    "chat_requests_total",
    "Total completed chat requests.",
    ["outcome"],
)
CHAT_INPROGRESS = Gauge(
    "chat_inprogress_requests",
    "Number of chat requests currently being processed.",
)
CHAT_DURATION = Histogram(
    "chat_request_duration_seconds",
    "Server-side chat processing duration in seconds.",
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0),
)

CHAT_REQUESTS.labels(outcome="success").inc(0)
CHAT_REQUESTS.labels(outcome="error").inc(0)
