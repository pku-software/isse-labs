# Lab 3：从代码到云端——ACR 构建与 ECI 部署

本 Lab 延续 Lab 2 的 HTML/CSS/JavaScript + Flask + DeepSeek 聊天应用。你将与 Coding Agent 协作编写 `Dockerfile`，把代码提交到个人 GitHub Fork；然后使用阿里云容器镜像服务（ACR）根据代码**在云端构建镜像**，弹性容器实例（ECI）拉取并运行镜像。最后，你从自己的浏览器访问云端应用。

## 开始前

以个人 Fork 的 `isse-labs/` 根目录打开 Codex Desktop App 新任务，发送：

```text
请完整阅读 lab3/AGENTS.md 和 lab3/README.md，从准备个人工作目录开始，按顺序引导我完成 Lab 3。
```

建议全程使用同一个 Codex 对话。课程 `lab3/README.md` 和 `lab3/AGENTS.md` 只读；个人代码和文档放在 `lab3/<学号>-<姓名>/`。人类读到这里即可进入 Codex；下文是供 Agent 逐步执行的流程。

### 实验边界与安全

- **沿用 Lab 2 的后端 Key 方式**：Flask 在运行时从 `DEEPSEEK_API_KEY` 环境变量读取 Key。前端不输入、不接收、不保存 Key；真实 Key 不得进入 GitHub、Dockerfile、构建上下文、镜像、ACR 构建参数、日志或 Codex 对话。
- 本 Lab 为短时教学演示，公网入口使用 **HTTP**。浏览器发出的聊天内容未加密，不要输入敏感信息。Key 不随浏览器请求传输；但公开的聊天 API **没有鉴权**，别人仍可能借后端 Key 调用模型。只使用专门创建的实验 Key，并尽量缩短公网开放时间。这不是正式服务的安全部署方案。
- 测试后**废除实验 Key**，并**释放本实验创建且不再使用的 ECI 等计费资源**。

## 作业目标与提交内容

完成后，你应能解释代码、Dockerfile、镜像、ACR、ECI、公网入口和后端 Key 的关系；亲自看到 ACR 构建成功、ECI 运行成功，并从浏览器实际访问聊天应用。

从个人 Fork 的最新主分支创建 `lab3/<学号>-<姓名>` 分支，在仓库 `lab3/` 下建立同名个人目录。所有个人文件只放在该目录，最后 Push 个人分支并发起标题为 `<学号>-<姓名>` 的 PR。至少提交：

```text
lab3/<学号>-<姓名>/
├── app.py
├── frontend/                 # 沿用 Lab 2 前端
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore                # 忽略 .env、虚拟环境等
├── .env.example              # 只有变量名与占位值
├── README.md                 # 项目、ACR 构建、ECI 配置与验证说明
└── AGENT_TRACE.md            # 最后由学生复制真实对话或填写分享链接
```

原项目需要的其他**非敏感**文件可以保留。不得提交 `.env`、真实 Key、云账号/仓库密码、真实聊天记录或本地虚拟环境。完成阶段性验证后创建有意义的 Commit；不要制造空 Commit。**不要求截图**，过程以真实 Codex 对话轨迹与个人 README 记录。

> 如果你是人类，则不必再继续阅读本 README 文件，后续任务只需在 Codex 中交互完成。
请不要修改本文件与同路径下的 AGENTS.md 文件。

## Agent 执行协议

> 本 README 是交互式实验流程，不是一次性开发规格。`[AGENT ACTION]`、`[STUDENT ACTION]`、`[REFLECTION]`、`[AGENT STOP]` 仅供内部控制，不要在正常对话中播报。每次只推进当前阶段；先说明下一件事及预期结果，遇到学生操作或思考题就暂停。学生的“已完成”只是核验请求：主动尝试读取本次终端、浏览器或控制台结果；无法读取时请求脱敏输出或截图。未经核验，不宣称成功、不进入下一阶段。严格遵守同目录 `AGENTS.md`。

## 准备个人工作目录与 Lab 2 成果

> [AGENT ACTION]

首次回复向学生说明最终目标、云端构建路线和人机分工，再引导学生亲自切换或创建个人 Lab 3 分支及同名目录。若已有对应分支，不要重复创建。Codex 工作目录始终是个人 Fork 的 `isse-labs/` 根目录。尽量打开内置终端；不要要求学生在对话中发送姓名学号。

> [STUDENT ACTION]

学生亲自在个人 Fork 的最新主分支上创建 `lab3/<学号>-<姓名>` 分支，并在 `lab3/` 下建立对应个人目录；已有正确分支则直接切换。完成后回复 Agent。

> [AGENT ACTION]

核对 Git 远端是学生的个人 Fork、当前分支格式正确、目录存在，并从分支名唯一解析个人目录。找到对应 Lab 2 成果；若不在当前分支，先只读定位，再迁移应用代码、前端、依赖和必要的非敏感文件。不得复制 `.env`、真实 Key、虚拟环境、真实聊天数据或 Lab 2 轨迹，也不得修改原 Lab 2 目录。找不到来源就请学生指出。

阅读实际 `app.py`、前端 `fetch()`、`requirements.txt` 和 Key 读取方式。在修改代码前，解释：① 本 Lab 保留后端持有实验 Key，前端不传 Key；② 公网开放期间无鉴权接口可能被其他人调用；③ 需要准备 Dockerfile、云端构建、ECI 运行与短时验证；④ 将对实际文件做哪些最小改动。等待学生确认这个计划，再开始改造。

> [AGENT STOP]

## 任务 1：准备适合云端构建的项目

> [AGENT ACTION]

在已确认的个人目录中完成最小容器化准备：

1. 保留原前端、Flask API、CRUD 及已有选做功能。若原项目已从 `.env`/环境变量读取 `DEEPSEEK_API_KEY`，沿用；否则只做使后端在运行时读取环境变量所需的最小修正。不要改成前端输入 Key。
2. `requirements.txt` 增加 Gunicorn。编写 `Dockerfile` 安装依赖，由单个 Gunicorn worker 在容器内监听 `0.0.0.0:5001`，提供页面、静态文件和 API。不要用 Flask debug 开发服务器对公网服务，不额外引入 Nginx、数据库或复杂拆分。
3. **在 Push 与 ACR 构建之前**准备 `.gitignore` 和 `.dockerignore`：排除 `.env`、凭据、虚拟环境、缓存、真实聊天数据、`AGENT_TRACE.md` 等；检查 Dockerfile 不包含真实 Key，也不使用 `ARG/ENV` 写入 Key。`.env.example` 只能包含占位值。
4. 若前端原本独立启动，做最小调整，使页面与 API 从同一个 Flask 容器提供，`fetch()` 使用同源相对路径。容器的工作目录与 `COPY` 路径以个人目录作为 ACR 构建上下文来设计。

向学生解释 Dockerfile 是镜像的构建说明、镜像与运行中的容器有何区别，以及为何 Key 只在 ECI **运行时**注入。此阶段不要求安装或运行本地 Docker。

> [STUDENT ACTION]

学生亲自在本机查看生成的文件，并在终端检查个人目录下 `.env` 未被 Git 跟踪、`Dockerfile` 与 `.dockerignore` 已准备好。Agent 主动核验本次 Git 状态及文件；不得读取 `.env`。学生确认后，Agent 创建代码准备 Commit；学生亲自将个人分支 Push 到**个人 Fork**，Agent 核验远端分支可见。ACR 构建只能读取已 Push 的内容，不能读取本机未 Push 的修改。

> [REFLECTION]

先问学生：为什么真实 API Key 不应写入 Dockerfile 或提交到 GitHub？此时 GitHub 上有源码和 Dockerfile，但为什么 ECI 还不能直接运行它们？学生回答后再反馈。

> [AGENT STOP]

说明下一步会让 ACR 从这个分支构建镜像，等待学生确认。

## 任务 2：让 ACR 从个人 GitHub 分支构建镜像

> [AGENT ACTION]

解释 ACR 是镜像仓库和云端构建服务，不是运行网站的服务器。参考[ACR 个人版构建指南](https://help.aliyun.com/zh/acr/user-guide/create-a-repository-and-build-images)，根据学生实际控制台引导；不要假设按钮或地域必然相同。建议 ACR 与后续 ECI 选择同一地域。先确认个人版可用，**不要为完成本 Lab 擅自升级购买企业版**。

明确构建配置：绑定学生自己的 GitHub Fork；代码源指向个人仓库；构建规则绑定**当前个人 Lab 3 分支**；构建上下文设为 `lab3/<学号>-<姓名>/`，Dockerfile 使用该目录中的 `Dockerfile`。以控制台对“构建上下文目录”的实际说明为准，不要误选仓库根目录或 `main`。镜像仓库保持私有；使用可识别的版本标签，不依赖反复覆盖 `latest`。ACR 个人版构建存在功能与时长限制，失败时先查看构建日志，不能直接声称镜像可用。

> [STUDENT ACTION]

学生亲自在阿里云控制台准备 ACR 个人版实例、命名空间和镜像仓库，授权绑定自己的 GitHub Fork，按上述规则触发一次构建。无需本机 `docker build`、`docker login` 或 `docker push`。学生在控制台检查构建日志显示成功、镜像版本列表出现所选标签，并把**非敏感**镜像地址和标签告诉 Agent；不要发送 GitHub/阿里云密码。Agent 尽量自行观察控制台或索取脱敏结果，核验确实是当前分支、当前提交所构建的镜像。

> [REFLECTION]

先问学生：这一步代码在哪里、镜像在哪里、构建发生在哪里？如果只改了本地文件但没有 Push，ACR 会构建到新代码吗？学生回答后再反馈。

> [AGENT ACTION]

把实际镜像地址、标签、构建分支和上下文等非敏感信息写进个人 README；如有文件变化，创建阶段 Commit。若个人 README 改动需要被 ACR 看到，再由学生 Push；不要为了文档变化无意义地重新构建镜像。

> [AGENT STOP]

说明下一步会创建按量计费的 ECI、公网 IP 和安全组规则，请学生先核对费用，等待确认。

## 任务 3：用 ECI 运行镜像并验证公网应用

> [AGENT ACTION]

引导学生在[ECI 控制台](https://eci.console.aliyun.com/)创建**一个**小规格、按量付费的实例，选择刚刚构建的 ACR 镜像及确切标签，设置容器端口 `5001`、合适的 VPC/交换机和安全组。为本 Lab 的短时公网验证绑定 EIP；安全组入方向只开放应用所需的 TCP `5001`，不用额外创建 ACK、ALB、NAT 或 ECS。实例需要出网访问 DeepSeek；如无法连通，应检查实际 EIP/出方向规则而不是猜测模型故障。参考：[ECI 公网连接](https://help.aliyun.com/zh/eci/user-guide/enable-internet-access)、[ECI 安全组](https://help.aliyun.com/zh/eci/user-guide/assign-a-security-group-2)。

创建前再次提醒：ECI 运行期间即使无人访问仍计费；公网聊天 API 没有鉴权，别人可能在开放期间消耗后端实验 Key；HTTP 聊天内容不加密。Key 只由学生在 ECI **容器运行时环境变量**中填写 `DEEPSEEK_API_KEY`；不要交给 Agent、放进镜像/构建参数或截图。控制台有权限查看容器配置的人可能接触该值，因此使用实验专用 Key。

> [STUDENT ACTION]

学生亲自核对购买页费用、地域、镜像版本、端口、EIP、安全组和环境变量名称，再创建实例。确认 ECI 运行中后，从自己的浏览器访问 `http://<ECI公网IP>:5001/`，检查页面、静态文件、健康检查、原有 CRUD，以及一次非敏感的真实模型回复。Agent 尽可能打开内置浏览器并读取可见的容器状态、日志或脱敏输出，但不替学生输入 Key 或发送消息；不能看到时请学生提供脱敏证据。失败时按“构建镜像/CPU 架构 → 容器启动和端口 → 环境变量是否存在（不显示值）→ EIP → 安全组 → DeepSeek 出网”排查。

> [REFLECTION]

先问学生：浏览器请求如何到达 ECI 内的 Flask？Key 是否随浏览器请求发送？陌生人在实例释放前知道公网地址，可能造成什么？学生回答后再反馈。

> [AGENT ACTION]

将**实际**公网验证结果、访问方式和非敏感配置写入个人 README；有文件变化时创建阶段 Commit。不要把真实 Key、聊天敏感内容或控制台凭据写进去。

> [AGENT STOP]

说明下一步会完成文档、废除实验 Key 和释放不再使用的资源，等待学生确认。

## 任务 4：提交与资源收尾

> [AGENT ACTION]

补全个人 README：项目来源、简要架构、ACR 构建分支/上下文/标签、ECI 镜像与环境变量**名称**、HTTP 访问与验证方式、无鉴权/HTTP 风险、Key 废除和云资源清理方式。说明云端容器文件不保证持久化。检查个人目录、Git 状态、提交文件与阶段 Commit，不得提交 `.env` 或真实凭据；文档有变化才创建 Commit。

> [STUDENT ACTION]

学生完成验证后亲自在 DeepSeek 控制台废除本次实验 Key，并在阿里云控制台释放本 Lab 创建且不再使用的 ECI 和相关 EIP；核对资源及费用状态。Agent 不代为删除，不凭一句“已释放”声称完成；若资源并非本 Lab 独占，先确认用途再决定，不误删。释放后公网地址不能再作为实时验收入口，验收依赖此前的真实验证轨迹及项目说明。[停止 ECI 计费指导](https://help.aliyun.com/zh/eci/product-overview/how-to-disable-eci-services-or-stop-billing)。

> [REFLECTION]

先问学生：为什么释放 ECI 后网页不可访问，但仍要另外废除 DeepSeek Key？如果更新了代码，ACR 中旧镜像及运行中的 ECI 会自动变成新版本吗？学生回答后再反馈。

最后引导学生在 Codex 对话列表中右键本次对话，选择“复制”→“复制为 Markdown”，粘贴到个人 `AGENT_TRACE.md`；若当前任务支持分享，也可把分享链接写进该文件。Agent 不生成摘要冒充对话记录。学生保存后，Agent 检查文件不含真实 Key、密码或其他凭据，再创建**最后一次轨迹 Commit**。学生亲自 Push 分支并发起标题为 `<学号>-<姓名>` 的 PR，Agent 核验可见结果。

> [AGENT STOP]

说明实际验证与提交状态，以及是否仍有计费资源；不得声称未核验的清理或 PR 已成功。
