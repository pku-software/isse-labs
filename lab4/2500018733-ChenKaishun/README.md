# Lab4：聊天应用指标监控

陈楷舜，2500018733。应用源自个人 Lab3 提交 `f69e8df3`，保留会话及消息的增删改查、原前端与聊天接口。

## Windows 本地启动

在个人 Fork 的 `isse-labs` 根目录使用 PowerShell：

```powershell
python -m venv lab4/2500018733-ChenKaishun/.venv
& ./lab4/2500018733-ChenKaishun/.venv/Scripts/python.exe -m pip install -r lab4/2500018733-ChenKaishun/requirements.txt
& ./lab4/2500018733-ChenKaishun/start-app.ps1
```

使用 Python 3.13.5 验证；本次安装 Flask 3.1.3、requests 2.34.2、prometheus-client 0.26.0。
应用以单进程多线程运行，监听 `127.0.0.1:5001`。端口占用时为启动脚本传入 `-Port <可用端口>`，并同步修改 `prometheus.yml` 中的目标地址。

- 聊天页面：`http://127.0.0.1:5001/`
- 指标文本：`http://127.0.0.1:5001/metrics`
- 实验状态：`http://127.0.0.1:5001/api/lab/status`

应用数据写入个人目录的 `.runtime/app/conversations.json`，该目录和 `.venv/`、`.tools/` 均被忽略，不纳入提交。运行路径依据脚本位置确定，不受当前终端目录影响。

## mock 与 real 模式

默认 `CHAT_MODE=mock`：返回固定测试回复，不读取 `.env`，不调用外部模型。实验状态接口返回 `{"mode":"mock","external_model_calls":false}`。

原 `POST /api/messages` 和 `POST /api/conversations/<id>/messages` 接口支持以下 JSON：

```json
{"message":"非敏感测试消息","mock_delay_seconds":0.1,"mock_force_error":false}
```

延迟必须是 0～30 秒的有限数字，失败开关必须为布尔值。延迟在后端处理期间发生，强制失败返回 HTTP 503 和明确的错误 JSON。成功返回 HTTP 201，包含 `id`、`message`、`reply`。mock 仍执行原来的请求校验、会话查找与成功结果保存。

显式传入 `-Mode real` 才启用原 DeepSeek 调用，此时密钥仅从 `DEEPSEEK_API_KEY` 环境变量取得，实验状态接口返回 404，mock 参数不影响真实调用。监控实验使用 mock。

原存储锁及同一会话历史变化检查保留，多个会话可并发处理；同一会话同时修改历史可能返回 HTTP 409。

## 指标

| 指标 | 类型 | 记录范围 |
| --- | --- | --- |
| `chat_requests_total{outcome="success或error"}` | Counter | 聊天 POST 完成后的成功或失败次数；两种标签初始化为 0 |
| `chat_inprogress_requests` | Gauge | 当前尚未结束的聊天 POST 数量 |
| `chat_request_duration_seconds` | Histogram | 每次聊天处理的服务端耗时，包含失败；单位秒 |

计数范围涵盖原聊天处理函数的校验、模型回复和保存。`finally` 负责记录耗时与结果，并减少在途数量，包含预期 HTTP 错误和未处理异常。耗时不含客户端网络传输。

Histogram 桶边界为 0.05、0.1、0.25、0.5、1、2、3、5、10、20、30、60 秒及正无穷。`_bucket` 记录不超过各边界的累计样本数，`_sum` 记录耗时总和，`_count` 记录样本总数。

页面、`/metrics`、状态接口及会话/消息的查询、修改、删除不计入聊天指标。标签不含消息内容、会话 ID 或用户身份。

## 应用验证

在仓库根目录运行：

```powershell
& ./lab4/2500018733-ChenKaishun/.venv/Scripts/python.exe -m unittest discover -s lab4/2500018733-ChenKaishun -p test_app.py -v
```

测试使用独立临时聊天数据，覆盖成功与失败指标、异常收尾、输入校验、非聊天接口排除、原 CRUD、real/mock 路径区分，以及两个慢请求并发时的指标读取。测试禁止实际外部模型调用。

`simulate_traffic.py`、`project_adapter.py` 和 `prometheus.yml` 是课程 `63c1038` 版本的个人副本。访问适配器尚未实现，`ADAPTER_READY=False`，调度器会拒绝运行。
