# Lab 3：AI 聊天应用的容器部署

作者：陈浩文（Chen Haowen），学号：2600921006。本项目沿用个人 Lab 2 的 HTML、CSS、JavaScript 与 Flask 聊天应用，通过 ACR 从个人 GitHub Fork 构建镜像，再由 ECI 运行。

## 应用架构

Gunicorn 在容器中监听 `0.0.0.0:5001`，加载 `app.py` 中的 Flask 对象 `app`。Flask 同时提供 `/` 聊天页面、`/static/` 静态资源和 `/api/` JSON 接口；前端使用同源相对地址，不需要单独部署前端服务器。

应用支持会话创建、切换、更名和删除，以及会话内问答记录的创建、查看、修改和删除。修改问题不重新生成已有回答；发送新问题时，后端只携带当前会话的历史请求 DeepSeek。

后端在处理聊天请求时读取 `DEEPSEEK_API_KEY` 环境变量，使用 DeepSeek 兼容接口和 `deepseek-flash` 模型。沿用的 `python-dotenv` 支持读取应用同目录的本地配置文件，但镜像不包含 `.env`；ECI 中由使用者在容器运行时环境变量中设置 Key，前端不接收或保存 Key。

会话数据在运行时写入 `data/conversations.json`，初次启动自动创建空的默认会话。镜像不携带历史聊天数据，本实验不配置持久化存储；容器重建或实例删除后不能保证数据保留。使用单个 Gunicorn worker，使请求共用同一份进程内会话状态和文件锁，不适合直接增加多个 worker 共写该 JSON 文件。

## Dockerfile

构建上下文必须是本个人目录 `lab3/2600921006-chenhaowen/`，不能使用仓库根目录。

| 指令 | 作用 |
| --- | --- |
| `FROM python:3.12-slim-bookworm` | 提供 Python 3.12 和精简 Debian 运行环境。 |
| `COPY --from=ghcr.io/astral-sh/uv:0.10.2 /uv /usr/local/bin/uv` | 从官方镜像复制固定版本的 uv 可执行文件。 |
| `WORKDIR /app` | 设置后续指令和应用启动时的工作目录。 |
| `COPY requirements.txt ./` | 先复制依赖清单，使依赖安装层可以独立于源码层缓存。 |
| `RUN uv pip install --system --no-cache -r requirements.txt` | 在构建阶段将依赖安装进镜像内的 Python 环境，不保留 uv 下载缓存。 |
| `COPY app.py ./`、`COPY frontend/ ./frontend/` | 在依赖安装后复制后端与前端代码。 |
| `EXPOSE 5001` | 声明应用预期端口，不创建公网入口或修改网络放行规则。 |
| `CMD [...]` | 容器运行时启动单 worker 的 Gunicorn，监听 `0.0.0.0:5001`，加载 `app:app`。 |

Gunicorn 的 worker 超时设为 90 秒，避免其默认 30 秒超时先于应用设置的 60 秒模型请求超时结束工作进程；网络库的超时不等同于严格的请求总耗时上限。容器启动使用 Gunicorn，不使用 Flask debug 服务器。

构建按指令依次执行；某一步失败或中断，后续步骤不会继续，修复后需要重新触发构建。构建器可能复用前面未变化步骤的缓存，指令或依赖文件改变后，相应步骤及后续步骤通常需要重做。ACR 不保证断点续跑。

`.dockerignore` 排除 `.env` 及其变体、虚拟环境、Python 缓存、聊天数据、Git 元数据、对话轨迹、截图和 README，使其不进入构建上下文。Dockerfile 只显式复制依赖清单、应用文件与前端目录。`.gitignore` 排除运行时配置、虚拟环境、缓存和聊天数据，同时允许提交只有占位值的 `.env.example`。

## 本地非敏感检查

以下命令适用于 macOS / Linux，在本个人目录中运行。使用 uv 创建环境、安装依赖和启动 Gunicorn，不需要 Docker Desktop。

```bash
uv venv --python 3.12
uv pip install --python .venv/bin/python -r requirements.txt
uv run --no-project --python .venv/bin/python gunicorn --workers 1 --bind 127.0.0.1:5001 --timeout 90 app:app
```

本地检查仅绑定回环地址；容器中的 `CMD` 绑定所有容器网络接口，以便 ECI 接收请求。在另一个终端访问 `http://127.0.0.1:5001/` 或执行 `curl http://127.0.0.1:5001/api/hello`。健康接口预期返回 `{"message":"你好"}`，页面、静态资源和会话管理不需要模型 Key。缺少 Key 时，发送消息返回 503 和运行时环境变量配置提示。

2026-09-28 已在本地 Python 3.12 环境完成非敏感检查：使用 Dockerfile 的 Gunicorn 启动参数并将监听地址改为回环临时端口，验证页面、JavaScript、CSS、健康接口、会话创建/查询/更名/删除、输入校验及缺少 Key 时的 503 响应；Python 与 JavaScript 语法、依赖兼容性和 Git 忽略规则检查通过。检查未调用真实模型，验证服务已停止；镜像构建与 ECI 公网验证尚未进行。

## API

| 方法 | 路径 | 作用 |
| --- | --- | --- |
| GET | `/api/hello` | 非敏感健康检查。 |
| GET / POST | `/api/conversations` | 列出会话 / 以 `{"title":"名称"}` 建立会话。 |
| GET / PATCH / DELETE | `/api/conversations/<id>` | 查看、更名或删除会话；更名使用 `title` 字段。 |
| GET / POST | `/api/conversations/<id>/messages` | 列出问答 / 以 `{"message":"问题"}` 请求模型回复。 |
| PATCH / DELETE | `/api/conversations/<id>/messages/<message_id>` | 修改问题或删除问答；修改使用 `message` 字段。 |

保留 Lab 2 的 `/api/messages` 兼容接口，其操作限定为 ID 为 1 的默认会话。错误响应使用 `{"error":"说明"}`，不返回供应商原始鉴权错误或 Key。

## 云端构建与部署

源码仓库为个人 Fork `HaoWen46/isse-labs`，构建分支为 `lab3/2600921006-chenhaowen`，构建上下文为 `/lab3/2600921006-chenhaowen/`，Dockerfile 文件名为 `Dockerfile`。本次构建对应源码提交 `7d7703d`，指导配置的镜像标签为 `lab3-7d7703d`，开启海外机器构建并关闭自动构建；代码更新后需先 Commit、Push，再手动点击“立即构建”。

2026-10-04，学生在 ACR 控制台确认构建成功。随后从实际控制台核实：镜像仓库为 `haowen46/lab3-chat`，位于华北 2（北京），类型为私有。ACR 的构建机器负责执行 Dockerfile，镜像仓库负责保存构建结果。仅更新本说明不需要重新构建应用镜像。

公网镜像仓库地址为 `crpi-qa9h3r7rc8yih8od.cn-beijing.personal.cr.aliyuncs.com/haowen46/lab3-chat`，专有网络地址为 `crpi-qa9h3r7rc8yih8od-vpc.cn-beijing.personal.cr.aliyuncs.com/haowen46/lab3-chat`。ECI 选择镜像时使用实际仓库名 `lab3-chat`，并选择对应的构建版本。

2026-10-04，学生提供的 ECI 控制台原始截图显示实例 `eci-2ze0ipfu87frugxylvnv` 中的 `container-1` 为“运行中”，重启次数为 0；所用镜像为 `crpi-qa9h3r7rc8yih8od-vpc.cn-beijing.personal.cr.aliyuncs.com/haowen46/lab3-chat:lab3-7d7703d`。截图保存在 [screenshots/eci-created.png](screenshots/eci-created.png)。

学生提供的弹性公网 IP 为 `39.106.108.253`，应用访问地址为 [http://39.106.108.253:5001/](http://39.106.108.253:5001/)。初次公网连接超时，控制台的入方向规则只允许 TCP 22、TCP 3389 和 ICMP。学生随后添加了允许 TCP 5001、来源 `0.0.0.0/0` 的入方向规则。

2026-10-04，Agent 通过该公网 IP 实际检查 `/`、`/static/app.js`、`/static/style.css`、`/api/hello` 和 `/api/conversations`，均获得 HTTP 200 且内容符合预期；健康接口返回 `{"message":"你好"}`。此检查未调用模型。学生浏览器中的真实模型回复、页面操作及第二张截图尚待验证。

本实例用于短时 HTTP 演示：聊天内容在浏览器与实例之间未加密，聊天 API 无鉴权，其他人可通过公网地址调用后端并消耗模型额度。`DEEPSEEK_API_KEY` 仅由后端在运行时读取，不进入前端、镜像或 Git。测试仅使用非敏感内容，提交 PR 后由学生删除本实验 ECI，并核实关联 EIP 是否也已释放。

ECI 容器组规格、学生浏览器验证与最终资源释放记录将在取得实际信息并验证后补充。

## 参考资料

- [Dockerfile 指令参考](https://docs.docker.com/reference/dockerfile/)
- [Docker 构建缓存失效规则](https://docs.docker.com/build/cache/invalidation/)
- [uv 的 Docker 集成](https://docs.astral.sh/uv/guides/integration/docker/)
- [Gunicorn 配置](https://gunicorn.org/reference/settings/)
