from prometheus_client import Counter, Gauge, Histogram

CHAT_REQUESTS = Counter(
    "chat_requests_total",
    "Completed chat requests by outcome.",
    ["outcome"],
)
CHAT_REQUESTS.labels("success").inc(0)
CHAT_REQUESTS.labels("error").inc(0)

CHAT_INPROGRESS = Gauge(
    "chat_inprogress_requests",
    "Chat requests currently being handled.",
)

CHAT_DURATION = Histogram(
    "chat_request_duration_seconds",
    "Time spent handling chat requests in seconds.",
    buckets=(0.05, 0.1, 0.2, 0.5, 1, 2, 3, 5, 10),
)
