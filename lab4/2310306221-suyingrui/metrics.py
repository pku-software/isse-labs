"""Metrics for completed POST /api/messages requests, including failures."""

from functools import wraps
from time import perf_counter

from flask import make_response
from prometheus_client import Counter, Gauge, Histogram


CHAT_REQUESTS = Counter(
    "chat_requests_total", "Completed chat requests", ("outcome",)
)
for outcome in ("success", "error"):
    CHAT_REQUESTS.labels(outcome=outcome)

CHAT_INPROGRESS = Gauge("chat_inprogress_requests", "Chat requests being handled")
CHAT_DURATION = Histogram(
    "chat_request_duration_seconds",
    "Server-side chat handling duration, including failures",
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 3, 5, 10, 20, 30),
)


def track_chat_request(handler):
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
            CHAT_INPROGRESS.dec()
            CHAT_REQUESTS.labels(outcome=outcome).inc()

    return measured
