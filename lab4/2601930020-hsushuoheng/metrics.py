from prometheus_client import Counter, Gauge, Histogram

# 1. 聊天請求累計計數器（按 outcome 分為 success 與 error）
CHAT_REQUESTS_TOTAL = Counter(
    "chat_requests_total",
    "Total number of chat requests processed, partitioned by outcome.",
    ["outcome"],
)
# 初始化兩種 outcome 為 0，確保未出錯前也能查詢到 error 指標
CHAT_REQUESTS_TOTAL.labels(outcome="success")
CHAT_REQUESTS_TOTAL.labels(outcome="error")

# 2. 正在處理中的聊天請求計數器（Gauge）
CHAT_INPROGRESS_REQUESTS = Gauge(
    "chat_inprogress_requests",
    "Number of chat requests currently being processed.",
)

# 3. 聊天處理耗時直方圖（Histogram）
# 涵蓋 0.05s、0.1s、0.25s、0.5s、1.0s、2.5s、3.5s、5.0s、10.0s 的桶分佈
CHAT_REQUEST_DURATION_SECONDS = Histogram(
    "chat_request_duration_seconds",
    "Server-side duration of chat request processing in seconds.",
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 3.5, 5.0, 10.0),
)
