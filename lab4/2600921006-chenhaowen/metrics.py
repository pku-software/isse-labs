"""Metrics for completed and in-flight chat requests only."""

from functools import wraps
from time import perf_counter

from flask import make_response
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram


REGISTRY = CollectorRegistry()
CHAT_REQUESTS = Counter(
    "chat_requests_total", "Completed chat requests by outcome.",
    ["outcome"], registry=REGISTRY,
)
for outcome in ("success", "error"):
    CHAT_REQUESTS.labels(outcome=outcome)

CHAT_INPROGRESS = Gauge(
    "chat_inprogress_requests", "Chat requests currently being processed.",
    registry=REGISTRY,
)
CHAT_DURATION = Histogram(
    "chat_request_duration_seconds", "Server-side chat processing duration in seconds.",
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 3, 5, 10, 20, 30), registry=REGISTRY,
)


def track_chat(handler):
    @wraps(handler)
    def measured(*args, **kwargs):
        started = perf_counter()
        outcome = "error"
        CHAT_INPROGRESS.inc()
        try:
            response = make_response(handler(*args, **kwargs))
            if 200 <= response.status_code < 300:
                outcome = "success"
            return response
        finally:
            CHAT_DURATION.observe(perf_counter() - started)
            CHAT_REQUESTS.labels(outcome=outcome).inc()
            CHAT_INPROGRESS.dec()

    return measured
