# 课程访问脚本模板

供 Agent 复制到学生个人目录并适配。课程原件只读，不直接在这里实现某个学生的接口。

## 已经写好的部分

`simulate_traffic.py` 使用 Python 3.9+ 标准库实现 HTTP 调度、有限并发、五阶段切换、错误计数、起止时间、JSON 结果与中断处理，不需要第三方压测框架。默认五阶段各 30 秒，最后等待 10 秒；慢请求收尾会略延长运行。

| 参数 | 默认 | 含义 |
| --- | --- | --- |
| `--base-url` | `http://127.0.0.1:5001` | 实际应用的本地根地址，只允许本机。 |
| `--scenario` | `all` | 可单跑 baseline / burst / slow / errors / recovery。 |
| `--phase-seconds` | `30` | 每阶段发出请求的持续时间。 |
| `--baseline-rate` | `1` | 正常、错误、恢复阶段的目标每秒请求数。 |
| `--burst-rate` | `4` | 访问增多阶段的目标频率。 |
| `--slow-rate` | `2` | 慢回复阶段的目标频率。 |
| `--slow-delay` | `3` | 让后端模拟等待的秒数。 |
| `--concurrency` | `6` | 最多在途请求数；满时跳过调度机会，不无限排队。 |
| `--error-every` | `3` | 错误阶段每第几个请求强制模拟失败。 |
| `--timeout` | `10` | 单次 HTTP 请求的超时。 |
| `--settle-seconds` | `10` | 结束后等待采集记录回落。 |
| `--output` | `simulation_results.json` | 真实结果 JSON 路径；正式实验分别指定 first-run / changed-run。 |

脚本输出实际开始/结束时间（UTC，Grafana 可按本地时区显示）、成功/失败/网络错误/跳过数量。HTTP 或业务失败中可包含预期模拟错误；预期结果匹配且没有网络错误则退出码为 0。适配未完成或运行失败为 2，响应不符合预期或网络错误为 1，Ctrl+C 为 130。中断时只保存已完成的阶段，不伪造未完成结果。

## 必须补齐的项目部分

`project_adapter.py` 三处 `NotImplementedError` 刻意留空：

1. `confirm_mock_mode(base_url, timeout)`：请求本地服务的实际状态接口，核验模拟模式和禁用外部模型调用。不得无条件返回 True。
2. `build_chat_request(base_url, message, delay_seconds, force_error)`：按学生实际接口构造标准库 `Request`，包括 JSON 编码、Content-Type 与后端识别的实验选项。
3. `response_is_success(status_code, body)`：按实际 JSON 结构判断业务结果，不输出正文。

**Agent 先读原项目，再在个人副本补齐这三处**，验证通过后设置 `ADAPTER_READY=True`。模拟选项仅 mock 模式有效；脚本没有模型 Key 参数。不要让所有学生改成模板预设的 /chat 或 /api/messages；适配器应该尊重原来的正确接口。

脚本帮助 `--help` 和参数解析可以在未适配时使用，真正访问前会拒绝未完成适配。Agent 先做单请求验证，随后按课程流程等待学生预测，再运行完整场景。

`prometheus.yml` 是本地采集配置模板，复制后把 target 改成实际应用端口；Grafana 的数据源则指向 Prometheus，不能错填应用地址。
