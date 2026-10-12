# Lab 4：杨沐之的聊天应用监控

本项目来自 `lab3/2500013091-yangmuzhi/`，保留 Flask 后端、原前端、会话管理和聊天记录的增删改查。在原聊天请求处理流程中加入 mock 回复与 Prometheus 指标，不需要真实模型 Key 即可本地运行。

## 本地运行

当前环境为 Windows x64、PowerShell 7、Python 3.9.12。以下命令从 `isse-labs` 仓库根目录执行；Python 要求 3.9 或更高版本。全局 pip 需支持 `--python`（本机为 26.0.1），它只负责向指定的个人虚拟环境安装依赖。

```powershell
$lab4 = Join-Path (Get-Location) 'lab4/2500013091-yangmuzhi'
python -m venv "$lab4/.venv"
python -m pip --python "$lab4/.venv/Scripts/python.exe" install -r "$lab4/requirements-lock.txt"
& "$lab4/start-app.ps1"
```

`requirements.txt` 声明直接依赖，`requirements-lock.txt` 记录本次实际安装的完整版本。若需要通过本机已配置的代理访问 PyPI，可在安装命令追加 `--index-url https://pypi.org/simple --proxy http://127.0.0.1:7897`；该代理端口是本机设置，其他电脑应使用自身可用的网络配置。

启动脚本明确使用 mock 模式，默认监听 `127.0.0.1:5001`。指定其他端口可运行 `& "$lab4/start-app.ps1" -Port 5002`。应用采用单进程、多线程，关闭 debug、自动重载和 `.env` 自动加载。终端前台运行时，按 Ctrl+C 停止。

- 聊天页面：<http://127.0.0.1:5001/>
- 指标文本：<http://127.0.0.1:5001/metrics>
- 实验状态：<http://127.0.0.1:5001/api/lab/status>

## mock 与 real

`LAB4_MODEL_MODE` 默认为 `mock`。原有 `generate_reply()` 在此模式下返回固定测试回复，不读取模型 Key、不导入或创建真实模型客户端，也不调用外部模型。实验状态接口实际检查启动配置，仅在 mock 模式返回 `{"mode":"mock","external_model_calls":false}`。

原有 real 模型调用代码保留。显式设置 `LAB4_MODEL_MODE=real` 时，它才会从进程环境变量读取 `DEEPSEEK_API_KEY` 并使用原有模型调用逻辑；本实验不运行 real 聊天。real 模式下实验状态接口返回 404，mock 参数不参与真实调用。任何模式均不自动读取 `.env`。

页面发送消息使用 `POST /api/conversations/<id>/messages`；独立聊天接口仍为 `POST /api/messages`，返回 HTTP 201 与包含 `id`、`message`、`reply` 的 JSON。两种聊天入口都接受 `message` 字符串。mock 模式可额外提供：

```json
{
  "message": "监控实验测试消息",
  "mock": {
    "delay_seconds": 0.1,
    "force_error": false
  }
}
```

延迟必须是 0～30 秒的有限数值，默认 0.1 秒；失败开关必须为布尔值。延迟发生在后端处理期间，强制失败在等待后返回 HTTP 503 和明确的 `error` JSON。共享存储的读取、修改和落盘受锁保护，等待回复时释放存储锁。会话数据位于个人 `.runtime/app/conversations.json`，不复制原实验聊天数据，也不提交本地聊天记录。

## 应用指标

| 指标 | 类型 | 含义 |
| --- | --- | --- |
| `chat_requests_total{outcome="success"}` | Counter | 成功完成的聊天请求累计次数 |
| `chat_requests_total{outcome="error"}` | Counter | 失败完成的聊天请求累计次数，包括参数错误与模拟失败 |
| `chat_inprogress_requests` | Gauge | 当前正在处理的聊天请求数 |
| `chat_request_duration_seconds` | Histogram | 每次聊天处理的服务端耗时，包括失败请求 |

指标只记录两个 POST 聊天入口，状态检查、页面、静态资源、CRUD 和 `/metrics` 采集本身不计入聊天数量。成功与错误计数都初始化为 0。响应构造或业务处理抛出异常时仍记录错误、耗时并收尾在途数量。标签只有 `outcome`，不包含用户信息或消息正文。

Histogram 的有限桶边界为 0.05、0.1、0.25、0.5、1、2、3、5、10、20、30 秒，另有 `+Inf` 桶；`_bucket` 是耗时不超过对应边界的累计样本数，`_sum` 是累计耗时，`_count` 是累计请求样本数。以上数据保存在应用内存，应用进程重启后重新累计。

实现见 `metrics.py` 与 `app.py`。Prometheus Python 客户端的指标类型说明见[官方文档](https://prometheus.github.io/client_python/instrumenting/)。

## 本地文件位置

工具下载包和校验文件位于 `.tools/downloads/`，工具目录为 `.tools/prometheus/` 与 `.tools/grafana/`。Prometheus 数据使用 `.runtime/prometheus/`，Grafana 数据、日志和插件使用 `.runtime/grafana/` 下的子目录，应用运行文件使用 `.runtime/app/`，Python 环境为 `.venv/`。这些路径均由个人 `.gitignore` 排除。

配置、仪表盘、`results/*.json` 和截图保留在可提交的位置。`simulate_traffic.py`、`project_adapter.py` 和 `prometheus.yml` 来自课程 starter，适配器通过验证前禁止运行模拟。

## 检查应用

从仓库根目录运行：

```powershell
& 'lab4/2500013091-yangmuzhi/.venv/Scripts/python.exe' -m unittest discover -s 'lab4/2500013091-yangmuzhi' -p 'test_app.py' -v
```

检查覆盖 mock 状态与输入校验、非聊天请求不计数、成功/失败与未捕获异常的指标收尾、原会话 CRUD，以及真实本地 HTTP 下的并发和慢请求期间的指标响应。测试进程独立于正在运行的实验应用；测试仅使用临时的本地数据文件。

本次环境的 5 项检查全部通过。在并发检查中，4 个后端延迟 1.5 秒的聊天请求同时处理中，`/metrics` 在 1 秒内响应并返回在途数 4；3 次成功与 1 次模拟失败结束后，在途数回到 0。独立启动的实验应用另经一次 HTTP 201 和一次 HTTP 503 验证，随后成功计数为 1、错误计数为 1、耗时样本数为 2、在途数为 0。这些连接检查也计入该应用进程的指标。

随后通过聊天页面发送 3 条测试消息，浏览器观察与实际读取的 `/metrics` 一致：成功计数为 4、错误计数为 1、耗时样本数为 5、在途数为 0。复现这组数值需从新启动的应用开始，依次执行上述两次连接检查，再通过页面发送 3 条成功消息。
