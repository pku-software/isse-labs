# Lab 4 聊天应用监控

作者：盛仁杰（2400017748，Dranix123）。应用源自本人 Lab 3 分支 `lab3/2400017748-shengrenjie` 的提交 `7667854`，保留原前端、消息及会话 CRUD。

## 本地运行

当前环境为 macOS arm64、zsh、conda 环境 `isse-lab2`（Python 3.11.16）。在本目录运行：

```sh
conda run --no-capture-output -n isse-lab2 python -m pip install -r requirements.txt
CHAT_MODE=mock conda run --no-capture-output -n isse-lab2 python app.py
```

应用默认使用 mock，监听 `127.0.0.1:5001`，以单进程多线程处理请求。可用 `PORT` 调整端口。网页地址为 `http://127.0.0.1:5001/`，指标地址为 `http://127.0.0.1:5001/metrics`。

mock 使用固定测试回复，不创建模型客户端，不读取 `.env`。`GET /api/lab-status` 返回实际 mock 状态和 `external_model_calls: false`。聊天请求可携带 `mock_delay_seconds`（0～10 秒，默认 0.1 秒）及 `mock_force_error`（布尔值，默认 false）；强制失败等待指定延迟后返回 HTTP 503。输入无效返回 HTTP 400。

real 模式保留原 DeepSeek 功能，需显式设置 `CHAT_MODE=real` 并通过进程环境提供 `DEEPSEEK_API_KEY`；本实验不运行 real 调用。real 模式忽略 mock 参数，实验状态接口返回 404。

## 接口与存储

前端使用 `POST /api/conversations/<id>/messages`，JSON 字段为 `message`，成功返回包含 `message` 和 `reply` 的 JSON。旧接口 `POST /api/messages` 同时保留，成功返回 HTTP 201 和消息记录。

新产生的测试数据及应用日志放在 `.runtime/app/`，不提交。共享存储操作使用线程锁；模型等待期间释放存储锁，让其他请求和指标接口仍可响应。没有复制原实验聊天数据。

## 指标

`metrics.py` 定义以下指标，对两个 POST 聊天接口记录；页面、状态、采集和其他 CRUD 接口不计入聊天指标。

| 指标 | 类型 | 含义 |
| --- | --- | --- |
| `chat_requests_total{outcome="success"或"error"}` | Counter | 按完成结果累计，两个标签初始为零 |
| `chat_inprogress_requests` | Gauge | 当前正在处理的聊天请求数 |
| `chat_request_duration_seconds` | Histogram | 服务端处理耗时，包含失败请求；桶边界为 0.05、0.1、0.25、0.5、1、2、3、5、10、+Inf 秒 |

异常路径也记录失败和耗时，并减少在途数；标签不包含聊天内容。`/metrics` 使用 `prometheus_client` 的标准文本和内容类型，另含该库默认的进程、Python 指标。
