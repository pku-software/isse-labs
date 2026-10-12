from prometheus_client import Counter, Gauge, Histogram


chat_requests = Counter("chat_requests_total", "Completed chat requests", ["outcome"])
chat_requests.labels(outcome="success")
chat_requests.labels(outcome="error")
chat_inprogress = Gauge("chat_inprogress_requests", "Chat requests currently being processed")
chat_duration = Histogram(
    "chat_request_duration_seconds",
    "Server-side chat processing duration in seconds",
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 3, 5, 10, float("inf")),
)
