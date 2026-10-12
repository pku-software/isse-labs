"""Chat-only metrics; no message content or request IDs appear in labels."""

from functools import wraps
from time import perf_counter

from flask import make_response
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram

REGISTRY = CollectorRegistry()
CHAT_REQUESTS = Counter(
    "chat_requests_total", "Completed chat requests by outcome",
    ["outcome"], registry=REGISTRY,
)
for outcome in ("success", "error"):
    CHAT_REQUESTS.labels(outcome=outcome)
CHAT_INPROGRESS = Gauge(
    "chat_inprogress_requests", "Chat requests currently being processed",
    registry=REGISTRY,
)
CHAT_DURATION = Histogram(
    "chat_request_duration_seconds", "Server-side chat processing duration",
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 3, 5, 10, 30), registry=REGISTRY,
)


def track_chat(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        started = perf_counter()
        outcome = "error"
        CHAT_INPROGRESS.inc()
        try:
            response = make_response(view(*args, **kwargs))
            if 200 <= response.status_code < 300:
                outcome = "success"
            return response
        finally:
            CHAT_REQUESTS.labels(outcome=outcome).inc()
            CHAT_DURATION.observe(perf_counter() - started)
            CHAT_INPROGRESS.dec()
    return wrapped
