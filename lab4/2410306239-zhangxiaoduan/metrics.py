"""监控指标定义与 /metrics 接口。

只统计聊天消息处理（POST /api/conversations/<id>/messages）；
Prometheus 的周期采集、状态接口、CRUD 与静态资源都不计入。
"""

from flask import Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

# 聊天消息处理累计次数，按结果区分；两种 outcome 初始化为 0，错误出现前也能查询
chat_requests_total = Counter(
    "chat_requests_total",
    "聊天消息处理次数，按处理结果区分",
    ["outcome"],
)
chat_requests_total.labels(outcome="success")
chat_requests_total.labels(outcome="error")

# 正在处理的聊天消息请求数：开始处理时 +1，结束（含异常路径）时 -1
chat_inprogress_requests = Gauge(
    "chat_inprogress_requests",
    "正在处理的聊天消息请求数",
)

# 聊天消息处理的服务端耗时（秒）；桶覆盖 0.1 秒左右的正常请求和数秒的慢请求
chat_request_duration_seconds = Histogram(
    "chat_request_duration_seconds",
    "聊天消息处理的服务端耗时（秒）",
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0),
)


def metrics_response():
    """以 Prometheus 文本格式返回当前全部指标"""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
