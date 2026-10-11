# Lab 3：一问 AI 聊天应用的容器化部署

基于本人 Lab 2 的 HTML/CSS/JavaScript + Flask 聊天应用，保留网页问答、查看、修改和删除记录功能。目标是由阿里云 ACR 从个人 GitHub Fork 构建镜像，再用 ECI 运行同一个提供网页、静态文件和 API 的容器。

## 模型接口与课程示例的差异

本项目沿用 Lab 2 的中转接口 `https://ctmoai.com/v1/responses` 和模型 `gpt-5.5`，使用 Responses API 格式，设置 `store: false`，没有改用课程示例的 DeepSeek。运行时环境变量为 `OPENAI_API_KEY`，需要对应中转站的有效密钥；不能填入无关服务的密钥。前端不接收密钥，Flask 后端在发出模型请求时读取环境变量。

## 运行结构与数据

浏览器通过同源相对路径 `/api/messages` 调用 Flask，后端请求中转模型接口后返回结果。Gunicorn 在 `0.0.0.0:5001` 监听请求，通过 `app:app` 加载 `app.py` 中的 Flask 对象。

使用一个工作进程，避免多进程分别维护内存中的记录和 ID；设置 180 秒工作进程超时，给原有模型接口的 10 秒连接、120 秒读取超时留出余量。

保留 Lab 2 的 JSON 写入逻辑，首次运行从空记录开始，写入时创建 `data/messages.json`。本次不配置持久化卷；应用进程重启时可能从同一文件恢复记录，但容器或实例被重建、删除后，不保证记录保留。旧聊天数据不复制、不提交，也不进入镜像。

## Dockerfile 与构建上下文

构建上下文必须是本个人目录 `lab3/2400018814-jiangyinan/`。Dockerfile 中的相对源路径以此为起点。

| 指令 | 作用与选择理由 |
| --- | --- |
| `FROM python:3.12-slim` | 使用包含 Python 3.12 的精简基础环境。 |
| `WORKDIR /app` | 将容器内工作目录设为 `/app`。 |
| `COPY requirements.txt ./` | 先复制依赖清单，使单纯源码修改有机会复用安装依赖的缓存。 |
| `RUN pip install --no-cache-dir -r requirements.txt` | 构建时安装 Flask、requests、python-dotenv 和 Gunicorn，不保留 pip 下载缓存。 |
| `COPY app.py ./` | 复制后端源码。 |
| `COPY frontend/ ./frontend/` | 复制 HTML、CSS 和 JavaScript，保留 Flask 查找静态文件所需的目录结构。 |
| `EXPOSE 5001` | 声明预期服务端口；不会自动配置公网 IP 或放行网络。 |
| `CMD [...]` | 容器启动时运行单进程 Gunicorn；不启动 Flask debug 服务器。 |

Docker 按顺序构建。某一步失败后，后续步骤不执行，需要修复后重新触发构建。构建器可能复用前面未变化的缓存；依赖文件改变时，安装依赖及后续步骤通常需要重做。缓存不是保证断点续跑，`--no-cache-dir` 关闭的是 pip 下载缓存，不是 Docker 层缓存。

`.dockerignore` 排除 `.env` 及其变体、虚拟环境、缓存、聊天数据、截图和 Markdown 文档（包括对话轨迹）。Dockerfile 只显式复制依赖清单、后端和前端，不使用 `COPY . .`。`.gitignore` 则防止本机配置和运行数据进入 Git，保留只有占位值的 `.env.example`。

## 本地检查方式

在本个人目录创建并激活 Python 虚拟环境，执行 `python -m pip install -r requirements.txt`。可用以下命令检查与云端相同的启动配置：

```bash
gunicorn --workers 1 --bind 0.0.0.0:5001 --timeout 180 app:app
```

访问 `http://localhost:5001/` 查看网页，`http://localhost:5001/api/hello` 检查服务。没有配置密钥时，网页和读取接口仍可访问，发送消息返回 503。可在本地自行根据 `.env.example` 配置 `.env`，已有配置不要覆盖；真实值不进入仓库或对话。

## API

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| GET | `/api/hello` | 非敏感服务检查。 |
| GET | `/api/messages` | 读取问答记录。 |
| POST | `/api/messages` | 接收 `message`，调用模型并保存问答。 |
| PATCH | `/api/messages/<id>` | 修改提问文字，不重新生成回复。 |
| DELETE | `/api/messages/<id>` | 删除问答记录。 |

写入请求使用 JSON。无效输入返回 400，记录不存在返回 404，未配置密钥返回 503，模型服务失败返回 502，模型超时返回 504，文件写入失败返回 500。

## 已完成的本地验证

- 在独立 Python 3.12 虚拟环境安装依赖成功。
- 按 Dockerfile 的实际 `CMD` 临时启动 Gunicorn，网页、CSS、JavaScript、问候接口和空记录接口均返回 200；无密钥的发送请求返回 JSON 503，验证后已关闭测试进程。
- 在临时目录模拟模型响应，验证创建、查询、修改、删除、JSON 保存和重新加载，以及无效输入、缺失 ID、上游失败和超时。
- 确认 `.env` 被 Git 忽略且未跟踪；打包采用显式文件复制，并排除配置、虚拟环境、运行数据和轨迹。未读取真实密钥、未请求真实模型，也未将测试数据写入作业目录。
- 本地没有执行 Docker 镜像构建；Linux 镜像构建结果以随后 ACR 的实际构建为准。

## ACR 构建与云端验证

- 代码源：个人 Fork `CarrieJiang-X/isse-labs`，分支 `lab3/2400018814-jiangyinan`。
- ACR：华北 2（北京）个人版，私有仓库按 `carrie-isse-labs/lab3-chat` 配置；构建上下文为 `/lab3/2400018814-jiangyinan/`，文件名为 `Dockerfile`，镜像标签为 `lab3-b3cb1c8`，对应应用提交 `b3cb1c8`。开启海外机器构建，关闭代码变更自动构建，保留构建缓存。
- 本人已在 ACR 控制台执行构建并确认构建成功。后续仅修改说明文档无需重新构建该应用镜像。ECI 实际使用的镜像为 `crpi-5rral4udbdsr3umm-vpc.cn-beijing.personal.cr.aliyuncs.com/carrie-isse-labs/lab3-chat:lab3-b3cb1c8`。
- ECI：华北 2（北京）可用区 F，名称 `lab3-2400018814`，实例 ID 为 `eci-2ze2nowldezs21prdh03`，经济型，0.25 vCPU / 512 MiB；实例列表与容器均显示“运行中”，原始截图保存为 `screenshots/eci-created.png`。部署使用 Dockerfile 启动命令，应用监听 5001 端口；运行时环境变量名为 `OPENAI_API_KEY`。
- 公网演示地址为 `http://47.93.61.238:5001/`。控制台确认 EIP `eip-2ze3dd3fp8xgrqtcw94wz` 绑定到上述 ECI。该地址仅在实验资源运行期间有效。
- 首次访问超时。核查发现 ECI 使用的安全组 `sg-2zeh0rhts5l46pwnbdvx` 仅有默认 ICMP、TCP 22 和 TCP 3389 入方向规则，缺少 TCP 5001；为短时公网演示添加来源 `0.0.0.0/0`、目的端口 `5001/5001` 的允许规则后，公网检查通过。`EXPOSE 5001` 只声明端口，不会自动放行安全组。
- 2026 年 10 月 12 日，Agent 从公网检查 `/`、`/style.css`、`/app.js`、`/api/hello`、`/api/messages`，全部返回 HTTP 200；首页包含“一问”，问候接口返回“你好”，记录接口返回空列表。此检查未调用模型。
- 本人已在浏览器发送“请用一句话解释容器和镜像的区别。”并收到回复：“镜像是运行容器所需的只读模板，而容器是镜像启动后形成的可运行实例。”Agent 随后通过公网 GET `/api/messages` 核对记录 #1，提问和回复与本人截图一致，确认真实问答已保存。
- 待完成：本人浏览器验证修改、删除及刷新，保存带公网地址栏的原始网页截图，并补充实际验证结果。当前已提供的聊天截图未包含地址栏，尚不能作为最终公网网页截图。
- 本实验仅作短时 HTTP 演示，不加密聊天内容且 API 无鉴权。提交后需要删除本实验 ECI，并核实关联 EIP 等计费资源已经释放。
