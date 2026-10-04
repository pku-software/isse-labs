# Lab 3：AI 聊天应用的容器化与云端部署

姓名：WangZiYi（王子懿）

学号：2500013152

## 项目来源与架构

本项目沿用 `lab2/王子懿-2500013152/` 中的 HTML/CSS/JavaScript + Flask 聊天应用，保留发送、查看、修改和删除聊天记录的功能。

同一 Flask 应用提供 `/` 页面、前端静态文件和 `/api/messages` 等 API。前端通过同源相对路径调用 API；后端从运行时环境变量 `DEEPSEEK_API_KEY` 读取凭据并调用 DeepSeek，前端不接收凭据。

部署流程：个人 GitHub Fork 保存代码 → ACR 从个人分支云端构建并保存镜像 → ECI 拉取镜像 → Gunicorn 启动 Flask 并处理请求。

聊天记录写入容器内的 `data/messages.json`。镜像不包含 Lab 2 的真实聊天数据，首次启动为空。本实验没有配置云端持久化；容器重建或实例释放后不保证记录保留。

## Dockerfile 配置

- 基础镜像：`python:3.11-slim`。
- 工作目录：`/app`。
- 先复制 `requirements.txt` 并安装 Flask、OpenAI SDK 和 Gunicorn，再复制 `app.py` 与 `frontend/`。
- `PYTHONDONTWRITEBYTECODE=1` 禁止生成 Python 字节码缓存，`PYTHONUNBUFFERED=1` 让 Python 日志及时输出。
- `EXPOSE 5001` 声明预期端口；容器启动后由 Gunicorn 实际监听 `0.0.0.0:5001`。
- Gunicorn 入口为 `app:app`，使用单 worker，超时设为 120 秒；单 worker 与当前进程内聊天记录状态相匹配。
- `.dockerignore` 排除 `.env` 类文件、虚拟环境、缓存、日志、聊天数据、截图、README 和对话轨迹。Dockerfile 只复制应用所需文件。
- 构建不使用真实 Key，也不设置含 Key 的 `ARG` 或 `ENV`。`.env.example` 仅说明变量名称，本应用不会自动加载 `.env`。

构建按 Dockerfile 顺序执行，失败或中断后需要修复并重新触发构建，后续步骤不会继续。构建器可能复用此前未变化步骤的缓存；ACR 不保证断点续跑。

## API

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| GET | `/` | 聊天页面 |
| GET | `/api/hello` | 非敏感连通性检查 |
| GET | `/api/messages` | 查看聊天记录 |
| POST | `/api/messages` | 调用 DeepSeek 并创建问答记录 |
| PATCH | `/api/messages/<id>` | 修改用户消息 |
| DELETE | `/api/messages/<id>` | 删除记录 |

## ACR 构建记录

个人分支已 Push，远端提交已核验为 `8d20293`。学生已在 ACR 构建页确认构建成功，实际配置如下。

| 项目 | 配置或状态 |
| --- | --- |
| 个人 Fork | `atribert/isse-labs` |
| 构建分支 | `lab3/2500013152-WangZiYi` |
| 构建上下文 | `/lab3/2500013152-WangZiYi/` |
| Dockerfile | 个人目录中的 `Dockerfile`，具体字段按页面路径约定填写 |
| 地域 | 华北 2（北京），`cn-beijing` |
| ACR 命名空间 | `atribert` |
| 私有镜像仓库 | `isse-lab3` |
| 规则镜像标签 | `lab3-8d20293`（按本次指导设置，ECI 选择时确认） |
| 构建方式 | GitHub 代码源；按指导开启海外机器构建，关闭自动构建，手动立即构建 |
| 构建结果 | 学生报告构建成功 |
| 完整镜像地址 | 待 ECI 选择镜像时补记 |

本实验由 ACR 在云端构建，不要求本地安装 Docker 或执行 Docker 构建、登录和推送。

后续代码修改需先 Commit，再 Push 到上述个人分支；自动构建关闭时还需手动触发 ACR 构建，并使用新标签区分版本。本阶段只有 README 变化，无需为这次文档提交重新构建镜像。

## 本地检查

已使用 Flask 测试客户端检查首页、CSS、JavaScript、`/api/hello`、空聊天列表、缺少 Key 时的响应、无效输入、聊天 CRUD 和数据序列化。模型返回与存储写入使用模拟对象，未读取真实 Key、调用模型或生成聊天数据文件。模拟模型调用失败时，API 正确返回 502。

已检查个人目录的 `.env` 忽略规则生效且未被 Git 跟踪，`.env.example` 可提交。前端保留同源 API 路径与页面内操作反馈。上述检查使用本机 Python 3.9.1；ACR 云端构建已完成，容器实际运行和真实模型回复仍待 ECI 部署后验证。

## ECI 配置与访问验证

尚未创建实例。后续记录实际地域、规格、镜像版本、网络与公网访问结果。

- 运行命令：沿用 Dockerfile 的 `CMD`。
- 应用端口：`5001`。
- 运行时环境变量名称：`DEEPSEEK_API_KEY`，真实值仅由学生在 ECI 中手动设置。
- 本实验使用公网 HTTP，浏览器与 ECI 之间的聊天内容不加密，不应输入敏感信息。Key 留在后端，不随前端请求传输；但聊天 API 没有鉴权，其他人可能调用并消耗实验模型额度。
- 创建前由学生核对控制台显示的 ECI 与 EIP 实际费用。ECI 运行期间即使无人访问也可能持续计费。
- 实例状态、页面和静态资源、聊天 CRUD、模型回复：待实际验证。
- 必交截图：`screenshots/eci-created.<真实扩展名>` 和 `screenshots/public-page.<真实扩展名>`，当前尚未取得。

## 提交与清理

实际部署和验证后补全本 README，提交两张原始截图。实验末尾由学生保存真实对话到 `AGENT_TRACE.md`，提交中文 PR；PR 提交后释放本实验创建的 ECI，并核实关联 EIP 是否需要单独释放。

当前尚未创建 PR 或云端计费资源。
