from functools import wraps
from time import perf_counter

from flask import make_response
from prometheus_client import Counter, Gauge, Histogram


CHAT_REQUESTS = Counter("chat_requests_total", "Completed chat requests", ["outcome"])
for outcome in ("success", "error"):
    CHAT_REQUESTS.labels(outcome=outcome)
CHAT_INPROGRESS = Gauge("chat_inprogress_requests", "Chat requests currently running")
CHAT_DURATION = Histogram(
    "chat_request_duration_seconds", "Server chat handling duration in seconds",
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 3, 5, 10, float("inf")),
)


def measure_chat(function):
    @wraps(function)
    def measured(*args, **kwargs):
        started = perf_counter()
        outcome = "error"
        CHAT_INPROGRESS.inc()
        try:
            response = make_response(function(*args, **kwargs))
            if 200 <= response.status_code < 300:
                outcome = "success"
            return response
        finally:
            CHAT_REQUESTS.labels(outcome=outcome).inc()
            CHAT_DURATION.observe(perf_counter() - started)
            CHAT_INPROGRESS.dec()
    return measured
