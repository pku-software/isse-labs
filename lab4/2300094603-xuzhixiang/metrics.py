"""Prometheus metrics for the Flask chat request only."""

from functools import wraps
import time

from flask import make_response
from prometheus_client import Counter, Gauge, Histogram


CHAT_REQUESTS = Counter(
    "chat_requests_total",
    "Completed chat requests, split by outcome.",
    labelnames=("outcome",),
)
CHAT_REQUESTS.labels(outcome="success")
CHAT_REQUESTS.labels(outcome="error")

CHAT_INPROGRESS = Gauge(
    "chat_inprogress_requests",
    "Chat requests currently being processed.",
)

CHAT_REQUEST_DURATION = Histogram(
    "chat_request_duration_seconds",
    "Server-side duration of each chat request in seconds.",
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 3, 5, 10),
)


def track_chat_request(view):
    """Count one POST /api/messages request and always close its measurements."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        started = time.perf_counter()
        outcome = "error"
        CHAT_INPROGRESS.inc()
        try:
            response = make_response(view(*args, **kwargs))
            if 200 <= response.status_code < 400:
                outcome = "success"
            return response
        finally:
            CHAT_REQUESTS.labels(outcome=outcome).inc()
            CHAT_REQUEST_DURATION.observe(time.perf_counter() - started)
            CHAT_INPROGRESS.dec()

    return wrapped
