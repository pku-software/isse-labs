from functools import wraps
from time import perf_counter

from flask import make_response
from prometheus_client import Counter, Gauge, Histogram


chat_requests = Counter(
    "chat_requests_total", "Completed chat requests", ["outcome"]
)
chat_requests.labels(outcome="success")
chat_requests.labels(outcome="error")
chat_inprogress = Gauge("chat_inprogress_requests", "Chat requests being processed")
chat_duration = Histogram(
    "chat_request_duration_seconds",
    "Server-side chat processing duration in seconds, including failures",
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 3, 5, 10, 20, 30),
)


def track_chat_request(handler):
    @wraps(handler)
    def tracked(*args, **kwargs):
        started = perf_counter()
        outcome = "error"
        chat_inprogress.inc()
        try:
            response = make_response(handler(*args, **kwargs))
            if 200 <= response.status_code < 300:
                outcome = "success"
            return response
        finally:
            # 提前返回和异常也必须记账，不能把请求永远留在“处理中”。
            chat_duration.observe(perf_counter() - started)
            chat_requests.labels(outcome=outcome).inc()
            chat_inprogress.dec()

    return tracked
