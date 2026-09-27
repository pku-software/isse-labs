# Lab 2：与 Coding Agent 协作构建 AI 聊天 Web 应用

> **截止时间：9 月 27 日 23:59**

## 如何开始

本 Lab 推荐使用 Codex Desktop App 完成。后续需要在同一个 Codex 任务中使用终端、浏览器和代码编辑能力。

如果使用 Codex CLI 或 IDE Extension，也可以完成代码和终端操作；需要观察网页时，请使用本机浏览器。

Codex 的工作目录统一设置为个人 Fork 仓库的根目录 `isse-labs/`。

- 在 Codex Desktop App 中打开 `isse-labs/` 并创建一个新任务；
- 或使用 Codex CLI 时，先进入仓库根目录再启动：

```bash
cd isse-labs
codex
```

进入 Codex 后发送：

```text
请完整阅读 lab2/AGENTS.md 和 lab2/README.md，从准备个人工作目录开始严格单步执行。
```

除非任务意外中断，整个 Lab 应在同一个 Codex 对话中完成。

> 如果你是人类，则不必再继续阅读本 README 文件，后续任务只需在 Codex 中交互完成。
> 请不要修改本文件与同路径下的 AGENTS.md 文件。

---

## Coding Agent 执行协议

> 本 README 是一个交互式实验流程，不是要求一次性完成的开发规格。
> 如果你是 Coding Agent，请严格遵守 AGENTS.md 下的每一条规则

---

## 作业目标

通过 Coding Agent 分阶段完成一个最小但完整的 Web 应用，并在过程中理解前端、后端、HTTP、JSON、API、RESTful API、网络服务、第三方 API、API Key 与数据持久化之间的关系。

最终我们可以达成：

- 在浏览器访问 `http://localhost:5001/` 可以打开前端页面；
- 前端使用 HTML + CSS + JavaScript；
- 后端使用 Python + Flask，并监听 `5001` 端口；
- 前端通过 `fetch()` 调用自己的 Flask API；
- Flask 后端调用 DeepSeek API 获得真实 AI 回复；
- DeepSeek API Key 只保存在后端，通过 `.env` 管理；
- 以“一次问答”为一条聊天记录，实现 Create / Read / Update / Delete；
- 选做：将聊天记录保存到 JSON 文件；
- 选做：支持多个聊天会话和多轮对话。

## 开发与学习规则

1. 本 Lab 要求使用 Coding Agent 辅助开发，但必须按照任务顺序逐步完成。
2. Agent 生成代码后，必须在 Codex 终端或浏览器中实际运行和观察，不能只以 Agent 声称“完成”为准。
3. 思考题必须由学生先回答，再由 Agent 进行反馈和整理。
4. 每完成一个必做里程碑，创建一次阶段性 Commit。
5. 严禁将真实 DeepSeek API Key 提交到 Git、写入代码或发送到对话中。
6. 如果真实 Key 曾经进入 Git 历史或 Codex 对话，应立即废弃并重新生成。

---

## 提交要求

### 1. 分支与目录

从课程仓库最新主分支创建 Lab 2 分支，分支应命名为：

```text
lab2/<姓名>-<学号>
```

在仓库的 `lab2/` 下创建个人目录：

```text
lab2/<姓名>-<学号>/
```

所有个人作业文件都放在自己的目录中，不要修改 Lab README 或其他目录。

### 2. 必须提交的文件

```text
<姓名>-<学号>/
├── app.py
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── AGENT_TRACE.md
```

如果完成选做任务 1，可根据当前项目的数据结构额外提交：

```text
data/messages.json
或 data/conversations.json
```

如果完成选做任务 2，请在个人 README 中说明 conversation 数据结构和 API 设计。

### 3. 个人 README

个人 README 作为项目本身的使用说明，它最终应说明：

- 项目实现了什么；
- 如何安装依赖；
- 如何从 `.env.example` 创建本地 `.env`；
- 如何启动 Flask；
- 浏览器访问地址；
- 实现了哪些 API；
- 如何进行最简单的 API 测试；
- 完成了哪些选做功能。

### 4. Agent 协作轨迹

本 Lab 不要求提交截图。运行与验证过程应直接在当前 Codex 任务的终端和浏览器中完成。

全部任务完成后，在 Codex 侧边栏对话列表中，选择当前对话历史条目右键，选择“复制”→“复制为 Markdown”，将完整对话粘贴到个人目录的 `AGENT_TRACE.md`。该文件用于保留真实的人机协作过程，不由 Agent 分阶段生成或事后总结。

如果使用 ChatGPT 账号登录 Codex，并且当前任务支持分享，也可以右键对话选择“分享”，将分享链接写在 `AGENT_TRACE.md` 顶部，无需粘贴对话内容。

粘贴后必须检查其中没有真实 API Key、`.env` 内容或其他敏感信息，再将 `AGENT_TRACE.md` 作为最后一次 Commit 提交。

### 5. API Key 安全检查

提交前必须确认：

- `.env` 没有被 Git 跟踪；
- `.env.example` 中只有示例值；
- HTML、JavaScript 和 Python 源代码中没有真实 Key；
- `AGENT_TRACE.md` 中没有真实 Key；
- Git 历史中没有真实 Key。

如果真实 API Key 曾经被提交，不要只删除文件或添加 `.gitignore`；应立即废弃该 Key 并重新创建。

### 6. Commit 与 Pull Request

推荐使用以下阶段性 Commit：

```text
lab2: scaffold frontend and flask api
lab2: connect frontend with message crud
lab2: integrate deepseek api
lab2: finalize documentation
lab2: add codex conversation trace
```

完成后 Push 自己的分支并创建 Pull Request。PR 标题使用：

```text
[Lab2] 姓名 学号
```

---

## 准备个人工作目录

> [AGENT ACTION]

先确认目前工作目录为isse-labs/，若不是则提醒用户在该目录下创建新的工作会话。

第一次回复先详细说明上面提及的作业目标、三个主要阶段和人机分工，再引导用户创建个人分支及同名目录。

介绍完成后，在同一条回复中一次性引导用户完成下面两项准备，不要拆成多轮确认。

请你直接打开 Codex 内置终端，再显示需要用户亲自输入的命令。示例路径统一写作 `lab2/<姓名>-<学号>`。

只用让用户输入

```bash
git switch -c lab2/<姓名>-<学号>
mkdir -p lab2/<姓名>-<学号>
```

即可，其他由你来进行操作。

还要提醒用户，在 Codex 页面右上角环境信息框中可以直接创建并检出新分支。

同时提示用户如果使用 Codex 桌面版用户可以通过右上角按钮打开内置终端或浏览器。

> [STUDENT ACTION]

1. 从课程仓库最新主分支创建个人 Lab 2 分支；
2. 在 `lab2/` 下创建与分支名最后一部分完全相同的个人目录。

两项都完成后，只需回复“已完成”。

> [AGENT ACTION]

用户确认后：

1. 确认当前 Git 仓库是 `isse-labs`；
2. 在内部读取当前分支名，确认格式为 `lab2/<姓名>-<学号>`；
3. 仅使用分支名中 `lab2/` 后面的部分，解析唯一工作目录 `lab2/<姓名>-<学号>/`；
4. 确认这个目录已经存在；如果格式或目录不正确，停止写入，并一次性告诉用户需要修正什么；
5. 后续所有文件创建、编辑、读取和 Git 检查都必须明确限定在这个解析出的目录中；
6. 禁止将 `stat`、工具输出、临时目录、仓库根目录或其他任意目录当作个人目录；
7. 创建个人 README，只写入项目名称和项目说明所需的基本结构，不加入 Lab 进度、Agent 轨迹或思考题；

> [STUDENT ACTION]
> 下面介绍即将搭建的前后端骨架，介绍文件目录、前后端要求和 RESTful API 的设计，等待用户确认后继续

---

## 任务 1：分别搭建前端与后端骨架

本任务先让前端和后端分别工作：

- 前端页面已经存在，但没有真正的交互逻辑；
- Flask 后端能够独立运行并响应最简单的 API；
- CRUD API 只有 Route 骨架；
- 前端和后端暂时没有接通。

### T1-S1：创建项目骨架

> [AGENT ACTION]

在从当前分支名唯一解析出的个人目录中创建一个最小的 AI 聊天 Web 项目骨架。每次文件操作都必须使用该目录下的明确路径，不得依赖模糊的“当前目录”。

创建：

- `app.py`
- `frontend/index.html`
- `frontend/style.css`
- `frontend/app.js`
- `requirements.txt`

前端要求：

- 只使用 HTML + CSS + JavaScript；
- 包含聊天记录区域、输入框和发送按钮；
- 为每条聊天记录预留修改和删除入口；
- 不依赖 `alert()`、`prompt()`、`confirm()` 等浏览器弹窗，后续交互所需的输入、确认和反馈都应通过页面内元素呈现；
- 本阶段只完成页面结构和样式；
- JavaScript 暂时不调用后端或第三方 API。

后端要求：

- 使用 Python + Flask；
- 实现 `GET /api/hello`，返回 `{"message":"你好"}`；
- 创建 Flask app 后设置 `app.json.ensure_ascii = False`；
- 使用 `app.run(port=5001, debug=True)`；
- 暂时不返回前端页面；
- 暂时不接入 DeepSeek；
- 暂时不保存数据。

保留下列 CRUD Route 骨架，并统一返回 `501 Not Implemented`，同时留下清晰的 TODO：

- `POST /api/messages`
- `GET /api/messages`
- `PATCH /api/messages/<id>`
- `DELETE /api/messages/<id>`

完成编码后解释文件结构，不要运行项目。

> [AGENT STOP]

完成编码后停止，并自然地请用户观察刚生成的静态前端，不得提及步骤编号或控制标记。

### T1-S2：观察静态前端

> [STUDENT ACTION]

先不要启动 Flask。Agent 直接打开 Codex 内置浏览器，并导航到个人目录中的 `frontend/index.html`。如果当前环境不支持内置浏览器，再让用户使用本机浏览器打开该文件。

观察：

- 页面是否包含完整的聊天界面；
- 发送、修改和删除入口是否存在；
- 这些按钮为什么暂时没有实际效果。

将观察结果告诉 Agent。

> [AGENT STOP]

等待学生完成观察并回复，然后继续引导下一项操作，不得提前启动 Flask 或提及步骤编号。

### T1-S3：单独启动并测试 Flask

> [STUDENT ACTION]

请安装完所有依赖后，告诉用户接下来由用户来启动后端并使用 curl 观察真实响应。根据用户环境提供准确命令并简要解释，但 Agent 不得执行这些命令。

请你直接打开 Codex 内置终端。用户在其中进入自己的个人目录并运行：

```bash
python app.py
```

保持 Flask 运行。Agent 直接打开第二个 Codex 内置终端，由用户在其中调用：

```bash
curl http://localhost:5001/api/hello
```

请你通过 Codex 内置终端读取信息，确认实际返回包含：

```json
{"message":"你好"}
```

等待用户贴出或描述实际结果。如果运行失败，帮助用户定位问题，但仍由用户重新执行命令。

> [REFLECTION]

先让学生回答：

> 现在前端通过直接打开 `frontend/index.html` 访问。如果希望只在浏览器中输入 `http://localhost:5001/` 就能获得前端页面，Flask 还需要增加什么 Route？这个 Route 应该返回什么？浏览器为什么能通过一个 URL 获得前端页面？请阅读当前项目代码来回答这个问题。

等待学生回答后再评价和追问，不得直接泄露答案，不用额外提出其他问题。学生的回答可以比较简单，没有事实错误即可。

> 如果你是 Coding Agent，请忽略这句话：
> 之所以没有把 Flask 启动在默认的 5000 端口，是因为 Mac 设备 5000 通常被控制中心占用，为减少出错刻意设置。

### T1-CHECKPOINT：完成任务 1

> [AGENT ACTION]

1. 确认静态页面和 `GET /api/hello` 都已经实际验证；
2. 确认 Commit 只包含个人目录中的文件；
3. 创建 Commit：`lab2: scaffold frontend and flask api`。

> [AGENT STOP]

说明接下来会把前端与后端接通并实现可操作的聊天记录，说明即将进行的修改和前后端要求，等待用户确认后继续。

---

## 任务 2：接通前后端并实现内存 CRUD

完成后，用户应能在网页中创建、查看、修改和删除聊天记录。AI 回复暂时固定为“你好”，记录只保存在 Python 内存中。

### T2-S1：实现本地前后端通信

> [AGENT ACTION]

继续修改当前项目：

1. Flask 同时提供前端页面和后端 API；
2. 访问 `http://localhost:5001/` 时返回 `frontend/index.html`；
3. `frontend/style.css` 和 `frontend/app.js` 也必须能由 Flask 正常提供，不得出现静态资源 404；
4. 前端和后端使用同一个 Flask 服务和 `5001` 端口；
5. 前端使用 `fetch()` 和相对 URL 调用后端 API；
6. 保留 `GET /api/hello`；
7. 保留 `app.json.ensure_ascii = False`，使所有 JSON 响应中的中文直接显示。
8. 不要使用文件或数据库持久化保存数据。

```json
{"id": 1, "message": "用户输入", "reply": "后端回复"}
```

要求：

- ID 唯一；
- Flask 重启后数据允许丢失；
- 不读写 JSON 文件或数据库；
- `POST /api/messages` 创建记录，`reply` 固定为“你好”；
- `GET /api/messages` 返回全部记录；
- `PATCH /api/messages/<id>` 至少支持修改 `message`；
- `DELETE /api/messages/<id>` 删除记录；
- 缺少数据或 ID 不存在时，返回清晰的 JSON 错误和合理的 HTTP 状态码。

前端要求：

- 页面打开时加载已有记录；
- 发送消息时调用 POST；
- 将返回的 `message` 和 `reply` 显示到聊天区域；
- 每条记录提供修改和删除入口；
- 修改或删除后及时更新页面；
- 不使用 `alert()`、`prompt()`、`confirm()` 完成修改、删除确认或错误提示，相关交互和反馈全部显示在页面中；
- 所有数据操作都通过 API 完成。

本阶段不要接入 DeepSeek、API Key、数据库或 JSON 文件持久化。完成代码后解释前端如何调用后端，但不要运行测试。

> [AGENT STOP]

完成编码后停止，并自然地询问用户是否现在运行和验证页面，不得提及步骤编号或控制标记。

### T2-S2：运行并验证 CRUD

> [STUDENT ACTION]

告诉用户接下来要亲自启动 Flask，并通过浏览器验证页面是否真正完成 CRUD。Agent 负责打开内置终端和导航内置浏览器，但不得执行命令、点击页面或填写内容。

Agent 先直接打开 Codex 内置终端，由用户在其中进入个人目录并重新启动 Flask：

```bash
python app.py
```

用户确认服务已经启动后，Agent 直接打开 Codex 内置浏览器并导航到：

```text
http://localhost:5001/
```

引导用户亲自完成：

1. 创建一条聊天记录；
2. 确认后端固定回复“你好”；
3. 创建多条记录；
4. 刷新页面并确认记录能从当前 Flask 进程重新加载；
5. 修改一条记录；
6. 删除一条记录。

不要仅通过阅读代码判断成功。等待用户描述实际观察结果。

> [REFLECTION]

先让学生回答：

> 网页来自 `http://localhost:5001/`，为什么 JavaScript 中写 `fetch("/api/messages")` 时不需要再写 `http://localhost:5001`？如果前端页面运行在 `http://localhost:5173/`，而 Flask 仍然运行在 `http://localhost:5001/`，那么 `fetch("/api/messages")` 又会请求到哪里？

本题只需要学生理解相对 URL 会基于当前网页地址解析，不需要展开其他浏览器网络机制。

等待学生回答后再评价和追问，确认学生理解即可。

### T2-CHECKPOINT：完成任务 2

> [AGENT ACTION]

1. 确认 Create、Read、Update、Delete 都已经在浏览器中实际验证；
2. 确认 Commit 只包含个人目录中的文件；
3. 创建 Commit：`lab2: connect frontend with message crud`。

> [AGENT STOP]
> 向用户说明接下来会准备 API Key 的安全配置，讲解具体流程，等待用户确认后继续。

---

## 任务 3：让 Flask 调用 DeepSeek API

本任务把固定回复“你好”替换为真实模型回复。前端仍然只调用自己的 Flask API，第三方 API 由 Flask 后端调用。

### T3-S1：先准备安全配置

> [STUDENT ACTION]

在创建真实 `.env` 之前，Agent 先说明 `.gitignore` 的作用，再请用户自行在个人项目根目录创建或编辑 `.gitignore`，至少加入：

```gitignore
.env
__pycache__/
.venv/
```

Agent 应根据已经解析出的个人目录提供准确路径，但不得代替用户创建或修改 `.gitignore`，也不要要求用户在终端中使用 `nano` 或其他指定编辑器。用户自行选择创建方式，完成后只需回复“`.gitignore` 已完成”。

> [AGENT ACTION]

用户确认后：

1. 读取并确认个人目录的 `.gitignore` 已包含 `.env`；
2. 创建 `.env.example`，只包含 `DEEPSEEK_API_KEY=your_api_key_here`；
3. 在需要时更新 `requirements.txt`，加入 `python-dotenv` 和调用 DeepSeek 所需的依赖；
4. 使用 `git check-ignore .env` 确认将要创建的 `.env` 会被忽略；
5. 不创建、不读取真实 `.env`。

完成后说明 `.env` 和 `.env.example` 的区别。

> [AGENT STOP]

完成安全配置后停止，并自然地引导用户申请 API Key 和创建 `.env`，不得提及步骤编号或控制标记。

### T3-S2：学生创建 API Key 与 `.env`

> [STUDENT ACTION]

Agent 先直接打开 Codex 内置浏览器并导航到 DeepSeek 开放平台。用户亲自完成注册、登录和 API Key 创建，Agent 不得点击、输入、查看或复述生成的 Key。

1. 进入 DeepSeek 开放平台注册、登录并创建 API Key；
2. 在个人项目根目录自行创建 `.env`，不要求使用终端或指定编辑器；
3. 写入 `DEEPSEEK_API_KEY=你的真实APIKey`；
4. 不要把真实 Key 发送给 Agent；
5. 完成后只告诉 Agent：“`.env` 已创建”。

DeepSeek 官方 API 文档：[https://api-docs.deepseek.com/zh-cn/](https://api-docs.deepseek.com/zh-cn/)

> [AGENT ACTION]

用户确认后，只能检查 `.env` 是否存在、是否被 Git 忽略，不得读取内容或输出变量值。

Coding Agent 不得：

- 打开或读取 `.env`；
- 执行 `cat .env`；
- 使用 `env` 或 `printenv` 输出 Key；
- 搜索并输出疑似 Key；
- 在回复、命令、日志或代码中复述真实 Key。

Coding Agent 可以让 Python 应用通过 `load_dotenv()` 自行读取环境变量，也可以判断变量是否存在，但不得输出值。

确认 `.env` 存在且已被忽略后，不再询问“是否继续”。自然说明接下来会在 Flask 后端接入 DeepSeek，然后直接执行下一项 Agent 编码动作。

### T3-S3：在 Flask 后端接入 DeepSeek

> [AGENT ACTION]

按照 DeepSeek 当前官方文档，将 `POST /api/messages` 中固定返回“你好”的逻辑替换为真实模型调用。

要求：

1. 使用 `python-dotenv` 和 `load_dotenv()`；
2. 使用 `os.getenv("DEEPSEEK_API_KEY")` 读取 Key；
3. 不在源代码中写死真实 Key；
4. 使用官方当前的 base URL、模型名和必要参数；
5. 将收到的 `message` 作为 user 消息发送给模型；
6. 将模型返回文本作为记录的 `reply`；
7. 将 `{id, message, reply}` 保存到现有内存列表；
8. Flask 仍返回刚创建的完整 JSON 记录；
9. Key 缺失或模型调用失败时返回清晰的 JSON 错误，不让 Flask 直接崩溃；
10. 不改变现有前端和 Flask API 的接口约定；
11. 不实现数据库或 JSON 文件持久化。

保持代码简单。完成编码后，解释 Key 如何被后端程序读取，以及浏览器、Flask 和 DeepSeek 之间的调用方向，但不要运行测试。

> [AGENT STOP]

完成编码后停止，并自然地询问用户是否进行实际验证，不得提及步骤编号或控制标记。

### T3-S4：用终端和浏览器验证

> [STUDENT ACTION]

告诉用户接下来要亲自通过 curl 和浏览器验证完整调用链。Agent 负责打开内置终端和导航内置浏览器，但不得启动 Flask、执行 curl、点击页面或填写内容。

Agent 先直接打开 Codex 内置终端，由用户在其中进入个人目录并重新启动 Flask：

```bash
python app.py
```

保持 Flask 运行。Agent 直接打开第二个 Codex 内置终端，由用户在其中执行：

```bash
curl -X POST http://localhost:5001/api/messages \
  -H "Content-Type: application/json" \
  -d '{"message":"请用一句话介绍北京大学"}'
```

确认返回中包含真实模型生成的 `reply`，且不包含 API Key。

curl 验证完成后，Agent 直接打开 Codex 内置浏览器并导航到：

```text
http://localhost:5001/
```

引导用户亲自确认：

- 新消息不再固定回复“你好”；
- 查看、修改和删除仍然正常；
- 终端和浏览器中没有显示真实 API Key。

等待用户描述实际观察结果。

> [REFLECTION]

依次提出下面两题，每题都必须等待学生先回答，再评价和追问。

1. 为什么不让浏览器前端直接调用 DeepSeek API，而要经过 Flask 后端？请从 API Key 安全角度解释。
2. 停止并重新启动 Flask 后，为什么原有聊天记录会消失？记录原本保存在哪里？如果希望长期保留，需要增加什么机制？

确认学生理解即可，不要把答案另行整理到项目文件中。

### T3-CHECKPOINT：完成任务 3

> [AGENT ACTION]

1. 确认 curl 和浏览器中的真实模型回复都已经实际验证；
2. 再次确认 `.env` 被忽略且未被 Git 跟踪；
3. 确认 Commit 只包含个人目录中的文件；
4. 创建 Commit：`lab2: integrate deepseek api`。

> [AGENT STOP]

告诉用户必做部分已经完成，并介绍两个选做任务。用户可以任选一个先做、两个都做或全部跳过；不得自动开始选做任务或提交前检查。

---

## 选做任务 1：使用 JSON 文件持久化

目标是让 Flask 重启后仍能读取当前应用中的聊天数据。本任务可以在选做任务 2 之前或之后完成。

> [AGENT ACTION]

在不改变当前前端调用方式和 API Path 的前提下，根据项目当前的数据结构实现：

- 如果尚未完成多会话功能，使用 `data/messages.json` 保存聊天记录；
- 如果已经完成多会话功能，使用 `data/conversations.json` 保存 conversation 及其 messages；
- Flask 启动时读取文件；
- 文件不存在或为空时，从与当前数据结构匹配的空数据开始；
- 创建、修改或删除消息、会话后及时写回文件；
- 新记录 ID 不与已有记录冲突；
- 不使用数据库；
- 不改变 DeepSeek 调用逻辑。

完成代码后停止，不要直接宣称验证成功。

> [STUDENT ACTION]

在 Codex 中依次完成：创建聊天数据 → 确认 JSON 文件更新 → 停止 Flask → 重启 Flask → 刷新页面 → 确认原有数据仍然存在。

> [REFLECTION]

让学生打开实际生成的 JSON 文件并结合后端代码回答一个问题：

> 简要回答，这个 JSON 文件最外层是什么数据结构，CRUD 后文件如何变化？为什么 Flask 重启后还能恢复这些数据？

等待学生回答后再评价和追问，帮助其把页面操作、Flask 中的内存数据和 JSON 文件之间的关系解释清楚，不得直接先给答案。

> [AGENT ACTION]

确认学生理解后，在个人 README 中说明实际采用的 JSON 数据结构和文件位置，并创建 Commit：

```text
lab2: persist messages in json
```

> [AGENT STOP]

等待用户决定是否继续另一个尚未完成的选做任务，或进入提交前检查。不得假定选做任务必须按编号完成。

---

## 选做任务 2：支持多个聊天会话

必做部分把每次问答看作独立记录。真正的多轮聊天需要应用管理一个会话中的历史消息，并在后续模型调用时提供必要上下文。本任务可以在选做任务 1 之前或之后完成。

> [AGENT ACTION]

在现有项目中增加多个聊天会话：

- 一个 conversation 包含多轮 user/assistant messages；
- 用户可以创建、查看、重命名、删除会话；
- 用户可以选择会话并继续聊天；
- DeepSeek 回答时获得该会话必要的历史消息；
- 前端增加会话列表；
- API Key 仍然只在 Flask 后端；
- 如果已经实现 JSON 持久化，同时持久化 conversations；否则可以使用内存。

建议 API：

- `POST /api/conversations`
- `GET /api/conversations`
- `GET /api/conversations/<id>`
- `PATCH /api/conversations/<id>`
- `DELETE /api/conversations/<id>`
- `POST /api/conversations/<id>/messages`

完成代码后停止，不要直接宣称验证成功。

> [STUDENT ACTION]

让用户亲自在浏览器中创建两个会话，在两个会话中分别进行不同主题的对话，再切换回其中一个会话继续追问，确认历史消息和模型上下文不会混到另一个会话中。如果已经实现 JSON 持久化，还要重启 Flask 并确认会话仍然存在。

> [REFLECTION]

结合实际 DeepSeek 调用代码，让学生回答一个问题：

> 当你在某个会话中发送一次新问题时，Flask 向 DeepSeek API 发出的这一次请求具体携带了哪些内容？为什么要这样做？

等待学生回答后再评价和追问，帮助其说明 `messages` 数组、`role` 和当前 conversation 历史之间的关系，不得直接先给答案。

> [AGENT ACTION]

确认实际验证成功且学生理解后，在个人 README 中说明 conversation/message 数据结构、API 设计以及传给 DeepSeek 的上下文组成，并创建 Commit：

```text
lab2: add multiple conversations
```

> [AGENT STOP]

等待用户决定是否继续另一个尚未完成的选做任务，或进入提交前检查。即使选做任务 2 已完成，也允许随后继续选做任务 1；不得提及步骤编号或控制标记。

---

## 提交前检查

> [AGENT ACTION]

逐项完成以下检查，但不得读取 `.env`：

1. 根据已经实际完成的项目补全个人 README，只写项目功能、配置和使用方法，不写 Lab 进度、Agent 过程或思考题；
2. 检查除 `AGENT_TRACE.md` 外的必需文件是否齐全；
3. 检查安装、启动、浏览器访问和 curl 测试说明是否清楚；
4. 检查 `.env.example` 只有示例值；
5. 使用安全命令确认 `.env` 被忽略且未被 Git 跟踪；
6. 检查当前 `git status` 和阶段性 Commit；
7. 创建 Commit：`lab2: finalize documentation`。

> [AGENT ACTION]

文档 Commit 完成后，Agent 在个人目录创建空的 `AGENT_TRACE.md` 并在 Codex 中打开该文件，但不得自动生成、总结或改写对话内容。如果可以，请调出 Codex 内置文件浏览器跳转到该文件。

> [STUDENT ACTION]

文件打开后，引导用户亲自完成：

1. 在当前 Codex 对话页面右键；
2. 选择“复制”→“复制为 Markdown”；
3. 将复制的完整对话粘贴到 `AGENT_TRACE.md`；
4. 如果使用 ChatGPT 账号登录 Codex，并且右键菜单中可以选择“分享”，可以将分享链接写在文件顶部，无需再粘贴完整对话；
5. 保存文件并告诉 Agent“对话轨迹已粘贴”。

> [AGENT ACTION]

用户确认后：

1. 检查 `AGENT_TRACE.md` 已包含复制得到的真实对话，而不是 Agent 生成的总结；
2. 检查其中没有真实 API Key、`.env` 内容或其他敏感信息；
3. 如果发现敏感信息，停止提交并引导用户删除；真实 Key 曾进入对话时，还应提醒用户立即废弃并重新生成；
4. 确认本次 Commit 只加入 `AGENT_TRACE.md`；
5. 创建最后一次 Commit：`lab2: add codex conversation trace`。

最后向用户展示：

- 已完成和未完成的任务；
- Commit 列表；
- 尚未提交的文件；
- API Key 安全检查结果；
- `AGENT_TRACE.md` 检查结果；
- Pull Request 标题和下一步操作。

> [AGENT STOP]

等待用户确认后，再引导其 Push 分支并创建 Pull Request。不得替用户声称 PR 已成功提交。
