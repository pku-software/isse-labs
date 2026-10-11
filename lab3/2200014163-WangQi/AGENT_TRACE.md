
# 引导完成 Lab 3 全流程

> 请完整阅读 lab3/AGENTS.md 和 lab3/README.md，从准备个人工作目录开始，按顺序引导我完成 Lab 3。

<details><summary>2 previous messages</summary>

> 我先完整阅读这两个文件，然后按顺序引导你。
>
> <details><summary>Explored 2 files, ran 3 commands</summary>
>
> <details><summary>Explored 2 files</summary>
>
> - Read `./lab3/AGENTS.md`
> - Read `./lab3/README.md`
>
> </details>
>
> - Ran `git remote -v; git branch -a; git status --short; git log --oneline -5`
>
> - Ran `Get-ChildItem -Force lab3 | Select-Object Mode,Name`
>
> - Ran `Get-ChildItem -Recurse -Force lab2 | Select-Object FullName | Format-Table -AutoSize -Wrap`
>
> </details>
</details>

我们正式开始 Lab 3。在动任何命令之前，我想先把这次实验到底在解决什么问题、用到的几样东西彼此是什么关系讲清楚，这样后面每一步你都能知道“为什么这么做”。

**Lab 2 留下了什么问题？**

你在 Lab 2 做的聊天应用，只运行在你自己的电脑上。你在本机浏览器能打开它，不代表别人用另一台设备也能访问——别人没有你这份正在运行的进程。更进一步说，就算你把代码复制到另一台电脑上，也很可能跑不起来：那台电脑的 Python 版本可能不同、依赖库没装齐、启动方式也不一样，任何一环对不上就会失败。所以 Lab 3 不再给聊天功能加新东西，而是解决两件事：第一，怎样把现有应用**稳定地交给另一台机器运行**；第二，怎样把它放到云端，让公网上的设备都能访问。这两件事性质不同，需要两类工具。

**Docker 解决“把应用连同环境一起带走”**

Docker 是一套把应用连同它运行所需的环境打包、并以“容器”方式运行的工具和规范。对咱们这个 Flask 聊天程序来说，光有 `app.py` 远远不够，还需要 Python 解释器、`requirements.txt` 里那些库、前端文件，以及一条正确的启动命令。**Dockerfile** 就是一份文本说明书，写清楚“选什么基础环境、复制哪些文件、安装什么依赖、运行什么命令”。按照 Dockerfile 构建出来的结果叫**镜像**，你可以把它理解成一个带版本号的应用包；把镜像真正启动起来、正在处理请求的那个进程，才叫**容器**。所以这四者不是一回事：Docker 是打包和运行的机制，Dockerfile 是说明书，镜像是构建的产物，容器是运行中的实例。还要记住一点：你改了源码之后，旧镜像和旧容器不会自己跟着变，必须重新构建。

容器里还需要一个真正监听网络端口、接收浏览器请求的程序。这里我们用 **Gunicorn** 来启动 Flask 应用：Flask 负责页面和 API 的处理逻辑，Gunicorn 负责把它作为一个 Web 服务跑起来、对外监听端口。Lab 2 里用的 Flask 自带 debug 服务器适合本地开发，但这次我们不会拿它直接对公网服务。这些都会写进 Dockerfile。要注意的是，**我们不会要求你在自己电脑上安装 Docker**，这一点放心。

**云计算解决“让公网能访问”**

云计算说白了，就是按需使用云厂商提供的远程计算和网络资源。Docker 镜像解决了“把应用和环境一起带走”，但它不会自动把应用放到公网。阿里云的 **ECS** 相当于一台由你全程管理的云服务器，像租了一台远程电脑：系统要你自己维护、环境要自己装、程序要自己部署。而 **ECI** 是弹性容器实例：你只要把一个现成的镜像交给它，云平台就替你启动容器，省去管理整台服务器的工作。本实验选 ECI，就是为了集中体验“把镜像交给云端运行”这件事。它常被归为 Serverless 一类，但“无需管理服务器”不等于免费——实例在运行期间，即使没人访问也可能持续计费，这点我们后面会特别留意。

**镜像从哪里来，各组件如何分工**

源码和 Dockerfile 放在你的个人 GitHub Fork 仓库里。阿里云 **ACR（容器镜像服务）** 从你指定的 GitHub 分支在云端构建镜像，并把镜像和不同版本保存起来，像一个镜像仓库；接着 **ECI** 拉取这个镜像并运行容器，我们再给它配上公网入口，让浏览器通过公网 IP 访问。这样职责就分清楚了：**GitHub 放代码，ACR 构建并存放镜像，ECI 运行镜像，容器里的 Gunicorn/Flask 处理网页和 API**。我们选这条路径，是为了完整练习“代码 → 可部署的镜像 → 云端运行”，而不必先去学维护 ECS 服务器。

最终你会亲自在浏览器里打开云上的聊天页面，并能解释为什么它不再依赖自己的电脑一直开机。分工上，我负责本地代码、Dockerfile、Git 分支和目录的准备以及排错；你亲自操作需要账号授权和费用确认的阿里云/GitHub 控制台，并验证公网访问。实验用的 Key 只在 ECI 运行时由你在后端设置；具体的公网使用提醒我会在部署和访问时再讲，PR 提交后必须删除计费实例。

接下来我们按下面四步推进，每一步有明确的产物：

1. 准备个人目录，把 Lab 2 代码整理进来，并编写 Dockerfile；
2. Push 代码，让 ACR 在云端构建镜像；
3. 用 ECI 运行镜像，你从浏览器访问，并留下两张规定截图；
4. 用中文提交 PR，并删除计费实例。

第一步我需要先知道你是谁，才能为你创建个人分支和同名目录。请你提供**姓名和学号**——我会据此生成拼音或合适的英文名称，亲自创建个人分支和同名目录。本次实验的分支和目录名要用英文字符，所以姓名写拼音、学号照写数字。请把姓名和学号发给我。

> 王琪-2200014163

<details><summary>8 previous messages</summary>

> 收到，你的姓名是王琪、学号 2200014163。我按“WangQi”作为姓名拼音，个人分支和个人目录就用 `lab3/2200014163-WangQi`。
>
> 我先自己检查一下仓库的远端、主分支和工作区状态，并读一下你 Lab 2 的应用代码，然后开始创建分支和目录。
>
> <details><summary>Explored a file, ran 3 commands</summary>
>
> - Ran `git fetch origin 2>&1; git status; git rev-parse --abbrev-ref HEAD; git rev-parse HEAD origin/main`
>
> <details><summary>Explored a file</summary>
>
> - Read `./lab2/王琪-2200014163/app.py`
>
> </details>
>
> - Ran `Get-Content -Raw 'lab2\王琪-2200014163\requirements.txt'; Write-Output '----- gitignore -----'; Get-Content -Raw 'lab2\王琪-2200014163\.gitignore'; Write-Output '----- env.example -----'; Get-Content -Raw 'lab2\王琪-2200014163\.env.example'`
>
> - Ran `Get-Content -Raw 'lab2\王琪-2200014163\frontend\app.js'; Write-Output '----- index.html -----'; Get-Content -Raw 'lab2\王琪-2200014163\frontend\index.html'`
>
> </details>
>
> 代码我已读完，工作区是干净的，本地 `main` 已经和 `origin/main` 一致。现在我来创建个人分支和同名目录，并把 Lab 2 里运行应用所需的文件迁移过来（不含 `.env`、真实聊天数据和 `AGENT_TRACE.md`）。
>
> <details><summary>Ran 2 commands</summary>
>
> - Ran `git checkout -b lab3/2200014163-WangQi
> New-Item -ItemType Directory -Path 'lab3\2200014163-WangQi' -Force | Out-Null
> Copy-Item 'lab2\王琪-2200014163\app.py' 'lab3\2200014163-WangQi\app.py'
> Copy-Item 'lab2\王琪-2200014163\requirements.txt' 'lab3\2200014163-WangQi\requirements.txt'
> Copy-Item 'lab2\王琪-2200014163\.env.example' 'lab3\2200014163-WangQi\.env.example'
> Copy-Item 'lab2\王琪-2200014163\.gitignore' 'lab3\2200014163-WangQi\.gitignore'
> Copy-Item -Recurse 'lab2\王琪-2200014163\frontend' 'lab3\2200014163-WangQi\frontend'`
> - Ran `git branch --show-current; Get-ChildItem -Force 'lab3\2200014163-WangQi' | Select-Object Mode,Name`
>
> </details>
>
> 我发现一个环境限制：当前沙箱把 `.git` 目录设成了只读，所以创建分支时写不进分支引用。这是正常 Git 工作所必需的写入，我需要请求一次提权来完成分支创建。
>
> <details><summary>Ran a command</summary>
>
> - Ran `git checkout -b lab3/2200014163-WangQi`
>
> </details>
>
> 分支已创建，现在处于 `lab3/2200014163-WangQi`。目录和迁移文件也都就位了。我确认一下 Git 状态：
>
> <details><summary>Ran a command</summary>
>
> - Ran `git status --short; git branch --show-current`
>
> </details>
</details>

分支和目录已就绪，情况如下：

- 个人分支：`lab3/2200014163-WangQi`（从最新 `main` 切出，工作区之前是干净的）
- 个人目录：`lab3/2200014163-WangQi/`，已迁移 `app.py`、`frontend/`（index.html、app.js、style.css）、`requirements.txt`、`.env.example`、`.gitignore`
- 刻意没有复制：`.env`、`data/`（真实聊天数据）、`__pycache__/`、Lab 2 的 `AGENT_TRACE.md`

在动手写 Dockerfile 之前，我先把你的应用现在是怎么工作的、以及我接下来要改哪些地方讲清楚，你确认后我再进入“写 Dockerfile”这一步。

**你的应用现在如何提供页面和 API**

后端是 Flask，启动时把 `frontend/` 作为静态目录，访问 `/` 返回 `index.html`，页面里的 `style.css` 和 `app.js` 也由同一个 Flask 提供。前端 `app.js` 里所有请求都用 `fetch()` 加**同源相对路径**（比如 `/api/conversations`、`/api/conversations/1/messages`），没有写死 IP 或域名，所以换到云上、用公网 IP 访问时，请求会自动发到同一个地址，不需要改前端。

API 这一侧是一套会话和消息的增删改查：新建/列出/改名/删除会话，发送消息后由后端调用 DeepSeek 生成回复，还有 `/api/hello` 这个健康检查接口。聊天数据目前写在本机的 `data/conversations.json` 里。

**为什么继续让后端读 Key**

你的 `app.py` 用 `os.getenv("DEEPSEEK_API_KEY")` 从环境变量读 Key，调用 DeepSeek 时把它放在请求头里，前端从头到尾都不接触这个 Key。这个设计在云上依然正确：Key 应该只存在服务器端，由你在 ECI 运行时把它设成容器的环境变量。所以我们**不改**这部分，也不会把 Key 写进代码或 Dockerfile。

**我接下来会改/新建哪些文件**

- `requirements.txt`：加上 `gunicorn`（其余 Flask、python-dotenv、requests 保持不变）
- 新建 `Dockerfile`：完整写好，我会逐行给你讲
- 新建 `.dockerignore`：排除 `.env`、`__pycache__`、`data/` 等不该进镜像的东西
- 更新 `.gitignore`：在原有基础上补上 `data/`，避免本地运行时产生的聊天数据被提交
- `app.py` 和 `frontend/`：**基本不动**，因为 Gunicorn 会直接导入 `app.py` 里的 `app` 对象来启动，现有代码已经兼容

**会怎么打包和运行**

Dockerfile 会用带 Python 的官方基础镜像，在构建阶段安装依赖、复制代码，在运行阶段用 Gunicorn 以单 worker 监听 `0.0.0.0:5001` 启动你的 Flask 应用，页面、静态资源和 API 都由这一个容器提供。

如果你对这个计划没有异议，回复“继续”，我就开始写 Dockerfile 并逐行讲解。若你对 `WangQi` 这个姓名拼写有别的写法，也请一并告诉我。

> 继续

<details><summary>2 previous messages</summary>

> 好的，现在进入核心环节：写 Dockerfile 和相关配置。我会把这些文件全部写完整，然后逐行讲解。
>
> <details><summary>Created 2 files, edited 2 files, ran 2 commands</summary>
>
> - Wrote `./lab3/2200014163-WangQi/.dockerignore` (+9 -0)
> - Wrote `./lab3/2200014163-WangQi/.gitignore` (+4 -1)
> - Wrote `./lab3/2200014163-WangQi/Dockerfile` (+13 -0)
> - Wrote `./lab3/2200014163-WangQi/requirements.txt` (+1 -0)
> - Ran `Get-ChildItem -Force 'lab3\2200014163-WangQi' | Select-Object Mode,Name; Write-Output '----- Dockerfile -----'; Get-Content -Raw 'lab3\2200014163-WangQi\Dockerfile'; Write-Output '----- gitignore -----'; Get-Content -Raw 'lab3\2200014163-WangQi\.gitignore'; Write-Output '----- requirements -----'; Get-Content -Raw 'lab3\2200014163-WangQi\requirements.txt'`
> - Ran `git ls-files | Select-String -Pattern '(^|/)\.env$'; if ($LASTEXITCODE -eq 1) { Write-Output 'no tracked .env found' }`
>
> </details>
</details>

我把需要改写的几个文件都写好了。先看最终内容，再逐行讲。

**Dockerfile（`lab3/2200014163-WangQi/Dockerfile`）**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "1", "app:app"]
```

**逐行讲它在做什么、为什么这么写**

`FROM python:3.11-slim` 选一个已经装好 Python 的基础镜像作为起点。`slim` 是精简版，体积小，但对我们的 Flask、requests、gunicorn 完全够用。这个基础镜像里当然不含你的实验 Key，Key 也不会进镜像。

`WORKDIR /app` 设定容器里的工作目录为 `/app`。之后所有相对路径都相对于这里，后面 `COPY` 到的位置、Flask 的静态文件路径都保持一致，不容易出错。

`COPY requirements.txt .` 先把依赖清单单独复制进镜像。注意构建上下文是你的个人目录 `lab3/2200014163-WangQi/`，所以这里的 `.` 指的就是那个目录，不是仓库根目录。

`RUN pip install --no-cache-dir -r requirements.txt` 在**构建镜像的阶段**安装依赖。`--no-cache-dir` 是不把 pip 下载的缓存留在镜像里，让镜像更小。这一步会装进 Flask、python-dotenv、requests 和 gunicorn。

`COPY . .` 再把剩下的东西（`app.py`、`frontend/`）复制进来。到底哪些不复制，由 `.dockerignore` 控制。

`EXPOSE 5001` 是一句“说明”：声明这个容器预期对外提供的端口是 5001。它本质是**元数据**，本身不会打开任何公网入口、也不会做端口映射——真正让应用监听 5001 的是下一行的 Gunicorn，而公网能不能进来还要靠 ECI 配公网 IP 和允许访问的网络规则。

`CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "1", "app:app"]` 是容器启动时执行的命令：用 Gunicorn 以**单 worker** 监听 `0.0.0.0:5001`，启动 `app.py` 里的 `app` 对象。`0.0.0.0` 表示监听容器内所有网卡，这样外部流量才进得来；这里**没有**用 Flask 的 debug 服务器对公网服务。

**构建阶段和运行阶段的区别**

`FROM`、`WORKDIR`、两条 `COPY`、`RUN` 都属于**构建阶段**，它们执行完、把结果固化下来，就得到了**镜像**；`CMD` 属于**运行阶段**，只有把镜像启动成容器时才执行。所以“构建镜像”和“运行容器”是两件事。

**逐步构建、失败/中断与缓存**

Dockerfile 的指令是**按顺序**执行的，每一步生成一层。如果某一步失败，后面的步骤就不会继续，你必须修正原因后**重新触发构建**。再次构建时，构建器可能复用前面没有变化的步骤的缓存；一旦某一步的指令或它依赖的文件变了，从这一步开始、包括它后面的步骤通常都要重做。要提醒的是，ACR 的云端构建不保证像本地那样“断点续跑”，所以失败后要重新发起构建。

**`.dockerignore` 排除了什么**

我写了 `.env`、`__pycache__/`、`*.pyc`、`.venv/`、`venv/`、`data/`、`.git/`、`AGENT_TRACE.md`、`screenshots/`。目的很明确：真实 Key 所在的 `.env` 绝不进镜像，缓存和虚拟环境不进，本机聊天数据 `data/` 不进，Git 元数据和轨迹、截图也不进。`.gitignore` 同理加了 `data/`、`*.pyc`、`venv/`，防止本地运行产生的聊天数据被提交。

到这里，文件已就绪。按流程，在创建代码 Commit 之前，有两道情境题想先听你用自己的话回答，我不急着给答案：

1. 为什么在 Dockerfile 里要把 `requirements.txt` 的复制和安装，放在复制源码 `COPY . .` **之前**？请结合真实开发里“源码和依赖各自多久改一次”，以及 Dockerfile 构建机制来解释。

2. 假设 Dockerfile 里写的是 `EXPOSE 5001`，浏览器也访问 `5001`，但 Gunicorn 实际监听的是 `0.0.0.0:5002`，网页会出什么问题？只改 `EXPOSE` 能解决吗？

你先回答这两题，我听完再和你讨论，之后再创建这次代码的 Commit。

> 1.依赖应该是固有的很少改动，除非新功能有新依赖才需要改，而源码改动可能很平凡。需要先创建一个运行的环境，也就是安装好依赖，其他代码才能运行整个项目才可以构建起来。2. 无法完成输入输出的交互，我认为可以解决

你的第 1 题思路对了一大半：依赖清单确实很少改，只有引入新功能、加新库时才动；源码则是每次迭代都可能改。把这个“改的频率”和 Docker 的构建机制联系起来就完整了——想想 Docker 是按**层缓存**的，每条 `COPY`/`RUN` 都是一层，这样把依赖放前面会带来什么具体好处？你可以再补一句。

第 2 题，你判断“交互会失败”是对的：浏览器敲 `5001`，但应用在 `5002` 监听，`5001` 上根本没人听，连接会被拒绝。但“只改 `EXPOSE` 就能解决”不成立。`EXPOSE` 只是一句声明/元数据，它**不会改变应用真正监听的端口**——真正决定监听端口的是 `CMD` 里 Gunicorn 的 `--bind 0.0.0.0:5001`。所以只把 `EXPOSE` 从 `5001` 改成 `5002`，应用依旧还在 `5002`，而浏览器还是访问 `5001`，问题不会消失。

给你两个小提示，你按自己的话重新回答一下：

1. 补充第 1 题：依赖放前面，和“Docker 按层缓存”结合后，对你**反复改源码、反复重新构建**这件事有什么实际帮助？
2. 修正第 2 题：要让浏览器访问 `5001` 时页面和 API 正常工作，正确做法是改 `EXPOSE` 还是改 Gunicorn 的 `--bind`？为什么？

> 1.之后更新的时候前面不需要重新构建了，只需要从源码层开始重新构建。2.需要监听`--bind 0.0.0.0:5001`

<details><summary>4 previous messages</summary>

> 两题都答对了。
>
> 第 1 题补充一点细节：依赖层能被缓存复用的前提是 `requirements.txt` 没变；一旦依赖清单真的改了，`pip install` 这一层和它后面都会重做。你平时改源码、反复重新构建时，因为依赖没动，前面这些层就能直接复用，只有 `COPY . .` 这层往后重建，这正是“依赖放前面”的价值。
>
> 第 2 题正确：真正决定监听端口的是 Gunicorn 的 `--bind`，`EXPOSE` 只是文档性声明。要修就改 `--bind` 让它和访问端口一致。我们的 Dockerfile 里 `--bind 0.0.0.0:5001` 和 `EXPOSE 5001` 本来就是一致的。
>
> 现在创建这次代码的 Commit。我需要写入 `.git`，先请求提权：
>
> <details><summary>Ran a command</summary>
>
> - Ran `git add lab3/2200014163-WangQi
> git commit -m "lab3: 新增 Dockerfile 与容器化配置"`
>
> </details>
>
> 提交成功，9 个文件，没有 `.env`、没有 `data/`、没有 `__pycache__`，符合预期。我确认一下提交内容和工作区状态：
>
> <details><summary>Ran a command</summary>
>
> - Ran `git show --stat --oneline HEAD; git status --short`
>
> </details>
</details>

代码 Commit 已创建（`f1b949b`），工作区干净，提交里只有预期的 9 个文件，没有 `.env`、没有真实聊天数据、没有轨迹和截图。

下一步是把这些代码 Push 到你的个人 Fork，让 ACR 能从你的分支上读到代码和 Dockerfile。这一步需要你的 GitHub 账号授权，所以由你来执行。

在 Windows PowerShell 里运行：

```powershell
git push -u origin lab3/2200014163-WangQi
```

它会推送到你的个人仓库 `QiWang3569/isse-labs`。如果弹出 GitHub 登录或授权，按浏览器提示完成即可；`-u` 会把本地分支和远端分支关联起来，之后推送更省事。

推送完成后告诉我一声，我会去核实这个分支确实已经出现在你的远端仓库里，然后我们再进入 ACR 云端构建。

> 完成了

<details><summary>5 previous messages</summary>

> 我来核实一下远端分支是否已经可见。
>
> <details><summary>Ran a command</summary>
>
> - Ran `git ls-remote origin lab3/2200014163-WangQi`
>
> </details>
>
> 网络在沙箱里被限制了，我需要提权来读取远端仓库状态，以核实分支是否已推送成功。
>
> <details><summary>Ran a command</summary>
>
> - Ran `git ls-remote origin lab3/2200014163-WangQi`
>
> </details>
>
> Stream error
>
> Reconnecting 1/5
> stream disconnected before completion: Transport error: network error: error decoding response body
</details>

远端核实通过：`refs/heads/lab3/2200014163-WangQi` 已存在，指向的提交 `f1b949b…` 和你本地最新提交完全一致。代码这一环没问题了。

接下来进入第二步：让 ACR 在云端构建镜像。

**ACR 做什么**

阿里云 ACR（容器镜像服务）在这里承担两件事：一是**从你的 GitHub 分支读取源码和 Dockerfile，在云端执行构建**，二是把构建出来的**镜像连同版本标签保存起来**，像一个镜像仓库。所以分工是：代码在 GitHub，构建发生在 ACR 云端，镜像保存在 ACR 仓库；之后的 ECI 再从 ACR 把这个镜像拉去运行。

**地域选择**

新建 ACR **个人版**实例时优先选**华北 2（北京）**，因为后面的 ECI 也要在北京，同一地域拉取镜像更快、也避免跨地域的麻烦。如果你账号里已经有一个其他地域的个人版实例，先告诉我，我们一起按实际情况商量同地域部署，**不要**为了这个实验购买企业版或 ACK/ALB/NAT/ECS。

**控制台操作顺序（请按这个顺序点，不要先急着填构建规则）**

先打开 ACR 控制台（[cr.console.aliyun.com](https://cr.console.aliyun.com/)），把地域切到**华北 2（北京）**。

1. 准备命名空间，并**创建私有镜像仓库**。创建仓库时，第 2 步“代码源”选 **GitHub**；GitHub 命名空间选你自己的用户名 **QiWang3569**，仓库选 **isse-labs**（你的个人 Fork），按提示完成授权后创建仓库。注意这里别选成课程官方仓库。
2. 创建完进入这个仓库，点左侧**“构建”**，优先开启**“海外机器构建”**，其他设置保持默认。海外机器构建能缓解拉取海外基础镜像和依赖源慢的问题，但不是百分百成功。
3. 在“构建”页点**“添加构建规则”**，按下表填写并保存，最后点**“立即构建”**。注意：保存规则不等于已经构建，一定要点“立即构建”。

| 项目 | 本 Lab 填法 |
| --- | --- |
| 代码源 / 仓库 | 刚绑定的个人 GitHub `isse-labs` |
| 分支 | `lab3/2200014163-WangQi`（不是 main） |
| 构建上下文目录 | `/lab3/2200014163-WangQi/` |
| Dockerfile 路径 | `Dockerfile`（相对于上面的上下文目录） |
| 镜像版本（标签） | `lab3-f1b949b` |
| 自动构建 | 关闭，手动点“立即构建” |

构建页显示成功后，直接告诉我“构建成功”即可，这一步**不需要截图或复制日志**。如果失败了，就把构建日志复制给我，我们一起判断是“拉取依赖失败”还是“把镜像推回北京仓库失败”。

> 构建成功

构建成功，很好。在把这一步写进 README 之前，先请你用自己的话回答一个小问题，帮我确认你对“代码 → 镜像”这条链路已经清楚了：

1. 现在的这套流程里，**代码存放在哪里、构建发生在哪里、镜像又保存在哪里**？
2. 假设你之后又改了代码，想让 ACR 构建出包含新代码的镜像——除了在本地**提交**代码更新之外，还需要做什么，ACR 才能构建到你的新代码？

你先回答这两点，我听完再和你讨论，然后把 ACR 的地域、仓库、分支、上下文和镜像标签写进你的 README。

> 1. 代码再github仓库，构建在阿里云平台镜像中，保存在了云服务器。2. 先同步到github上，再到阿里云平台重新构建从源码层面的docker

<details><summary>2 previous messages</summary>

> 你的回答我帮你校正两处措辞，思路基本对。
>
> 第 1 题：代码在**你个人的 GitHub Fork**（`QiWang3569/isse-labs`）——对；构建发生在**阿里云 ACR 的云端构建服务**里，它按 Dockerfile 执行构建——对（不是“在镜像中”，而是“按 Dockerfile 构建出镜像”）；但最后一句“保存在了云服务器”不准确。镜像保存在 **ACR 的镜像仓库**里，带版本标签，它是一个“仓库/存储”，不是一台会跑应用的云服务器。真正把镜像跑起来的是下一阶段的 ECI，所以“存镜像的地方”和“跑应用的服务器”要分开。
>
> 第 2 题：对。本地提交后必须**先 push 到 GitHub 的个人分支**，让远端分支指向你的新提交，然后再到 ACR 点**“立即构建”**重新构建。只本地 commit 不 push，ACR 读不到新代码，构建出来的还是旧版本。
>
> 我现在把已知的 ACR 信息写进你的 README（镜像仓库的完整地址等 ECI 选镜像时再补记）。
>
> <details><summary>Created a file, ran a command</summary>
>
> - Wrote `./lab3/2200014163-WangQi/README.md` (+32 -0)
> - Ran `git add lab3/2200014163-WangQi/README.md
> git commit -m "lab3: 记录 ACR 构建信息到 README"`
>
> </details>
</details>

README 已写好并提交（`4836656`），记录了地域、代码源、分支、上下文和镜像标签，镜像仓库地址留到 ECI 选镜像时再补。

下一步就是创建 **ECI（弹性容器实例）** 来运行这个镜像。先提醒一句：ECI 是**按量计费**的，实例运行期间即使没人访问也可能持续计费，所以这一步会涉及费用确认。等你准备好了，我们就开始；到时我会带你按控制台页面的实际顺序一步步操作，并在创建前把公网访问的风险讲清楚。

> 开始吧

好，我们开始创建 ECI。先把这一步是什么、以及开始前必须知道的几点讲清楚。

**ECI 是什么**

ECI（弹性容器实例）就是把你在 ACR 里构建好的镜像拉过来、作为**正在运行的容器**跑起来。它不是 ECS 云服务器——ECS 要你自己维护整台机器和系统环境，ECI 则是“把镜像交给云平台，它替你启动容器”。但注意：按量计费意味着**实例在运行期间，即使没人访问也可能持续计费**。

**创建前先提醒你几点**

- 这次公网入口用的是 **HTTP**，浏览器到 ECI 的聊天内容**没有加密**，所以测试时不要输入任何敏感信息。
- 你的 Key 一直留在后端，不会随前端请求传输；但这个聊天 API **没有鉴权**，别人如果知道公网地址，也可能调用你的后端，从而消耗你的 DeepSeek 额度。
- 创建前请核对页面展示的实际价格，**由你本人确认费用后再创建**。
- 安全组先用页面默认设置，等访问失败了我们再检查端口，不必预先改规则。

**进入控制台**

打开北京地域的 ECI 控制台（[eci.console.aliyun.com](https://eci.console.aliyun.com/#/eci/)），在左侧点**“容器组”**，再点**“创建弹性容器组”**。创建向导按 **基础配置 → 其他设置（选填）→ 确认订单** 三步走，下面逐项说明，没提到的就保持默认。

**第 1 步：基础配置（按页面从上到下）**

| 页面项目 | 本 Lab 怎么选 |
| --- | --- |
| 付费模式、实例类型 | 按量付费、普通实例 |
| 地域 | 华北 2（北京），与 ACR 同地域 |
| 专有网络 VPC、交换机 | 选北京地域已有的 VPC 和其中一个交换机 |
| 安全组 | 先用当前默认选择，不预先改规则 |
| 容器组配置 → 基础模式 | 算力类别选**经济型**；CPU、内存选页面允许的**最低组合**；名称用英文/数字，如 `lab3-2200014163`；“容器运行退出后”保持默认“总是重启” |
| 容器配置 → 容器名称 | 默认即可，本 Lab 只用一个容器 |
| 容器配置 → 镜像、镜像版本 | 点“选择容器镜像”→“我的镜像”，选你刚建的 ACR 仓库；再点“选择镜像版本”，选标签 `lab3-f1b949b` |
| 容器配置 → 镜像拉取策略、启动命令 | 拉取策略保持默认；启动命令/参数**留空**，沿用 Dockerfile 的 `CMD`，不要重复写 Gunicorn 命令 |
| 容器配置 → 容器高级配置 → 环境变量 | 展开该容器的高级配置，打开“环境变量”，由你添加：名称 `DEEPSEEK_API_KEY`，值填你的实验 Key。**值不要发给我，也不要截图包含值的页面** |
| 数据缓存 | 不配置 |

注意：当前北京创建页**没有**单独的“容器端口 / 协议”必填框，应用监听 `5001` 是 Dockerfile 里 Gunicorn 的 `--bind` 决定的，`EXPOSE` 不会自动开放公网。若你的页面版本出现了可选端口设置，再按实际界面配置 `5001/TCP`。填完点“下一步：其他设置”。

**第 2 步：其他设置（选填）**

| 页面项目 | 本 Lab 怎么选 |
| --- | --- |
| 弹性公网 IP | 选**“自动创建”**，留意默认带宽峰值和按流量计费的提示——这一步才是给 ECI 配公网入口，后面务必确认 EIP 是否还在计费 |
| 镜像仓库访问凭证 | 使用同一阿里云账号的“我的镜像”时**留空**，不要填写 ACR/GitHub 密码 |
| 实例 RAM 角色、标签、资源组 | 无特殊需求，保留默认 |

点“配置确认”进入第 3 步。**确认订单时逐项核对**：地域、镜像及标签 `lab3-f1b949b`、经济型规格、环境变量**名称**（只看名称，不显示值）、自动创建的 EIP，以及页面展示的 ECI 与 EIP 费用。确认无误后，由你本人点创建。

创建后等实例变成**“运行中”**，在实例详情/列表界面截一张**原始截图**（能看出实例已创建和状态，不要包含 Key），把截图发给我，并把**公网 IP** 一起告诉我。我先去用这个 IP 做一次非敏感接口的自测，再带你从浏览器访问。

> 我已经截图放进去了。公网ip是
>
> | <br>[101.200.204.113(弹性)](https://vpc.console.aliyun.com/eip/cn-beijing/eips?EipAddress=101.200.204.113) | 172.26.113.195 (内) |
> | -------------------------------------------------------------------------------------------------------- | ------------------ |

<details><summary>10 previous messages</summary>

> 收到，公网 IP 是 `101.200.204.113`。我先做两件事：找到你放进来的截图文件，并且亲自用这个 IP 测一下服务是否真的能从公网访问。
>
> <details><summary>Ran 2 commands</summary>
>
> - Ran `Get-ChildItem -Path 'D:\Files\Desktop\isse-labs' -Recurse -File -Include *.png,*.jpg,*.jpeg,*.webp,*.bmp -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-2) } | Select-Object FullName,Length,LastWriteTime | Format-Table -AutoSize -Wrap`
> - Ran `try { $r = Invoke-WebRequest -Uri 'http://101.200.204.113:5001/api/hello' -UseBasicParsing -TimeoutSec 15; Write-Output ('STATUS ' + $r.StatusCode); Write-Output $r.Content } catch { Write-Output ('ERROR: ' + $_.Exception.Message) }`
>
> </details>
>
> 截图我找到了，在你的个人目录根下：`lab3/2200014163-WangQi/Screenshot 2026-09-29 190023.png`。我先校验它是不是有效的图片文件，再把它移到规范的 `screenshots/eci-created.png` 位置。
>
> <details><summary>Ran a command</summary>
>
> - Ran `$bytes = [System.IO.File]::ReadAllBytes('D:\Files\Desktop\isse-labs\lab3\2200014163-WangQi\Screenshot 2026-09-29 190023.png')[0..7]
> $sig = ($bytes | ForEach-Object { $_.ToString('X2') }) -join ' '
> Write-Output ("PNG signature: " + $sig)
> Add-Type -AssemblyName System.Drawing
> $img = [System.Drawing.Image]::FromFile('D:\Files\Desktop\isse-labs\lab3\2200014163-WangQi\Screenshot 2026-09-29 190023.png')
> Write-Output ("Dimensions: " + $img.Width + " x " + $img.Height)
> $img.Dispose()
> New-Item -ItemType Directory -Path 'lab3\2200014163-WangQi\screenshots' -Force | Out-Null
> Move-Item 'lab3\2200014163-WangQi\Screenshot 2026-09-29 190023.png' 'lab3\2200014163-WangQi\screenshots\eci-created.png'
> Get-ChildItem 'lab3\2200014163-WangQi\screenshots' | Select-Object Name,Length`
>
> </details>
>
> 截图是有效的 PNG（1920×1020，签名正确），已保存为 `screenshots/eci-created.png`。
>
> 现在我用公网 IP 亲自测一下服务是否真的对外可访问（需要网络访问，请求提权）：
>
> <details><summary>Ran a command</summary>
>
> - Ran `foreach ($path in @('/api/hello', '/', '/app.js')) {
>   try {
>     $resp = Invoke-WebRequest -Uri ("http://101.200.204.113:5001" + $path) -UseBasicParsing -TimeoutSec 15
>     Write-Output ("[{0}] status={1} len={2}" -f $path, $resp.StatusCode, $resp.Content.Length)
>     if ($path -eq '/api/hello') { Write-Output ("  body: " + $resp.Content) }
>   } catch {
>     Write-Output ("[{0}] ERROR: {1}" -f $path, $_.Exception.Message)
>   }
> }`
>
> </details>
>
> 公网 HTTP 请求全部超时了，说明 `101.200.204.113:5001` 目前连不上。超时通常意味着端口没被放行，而不是服务拒绝连接。我做个 TCP 层的连通性测试来区分，需要网络访问：
>
> <details><summary>Ran a command</summary>
>
> - Ran `function Test-Port($host, $port) {
>   $client = New-Object System.Net.Sockets.TcpClient
>   try {
>     $result = $client.BeginConnect($host, $port, $null, $null)
>     $ok = $result.AsyncWaitHandle.WaitOne(5000)
>     if ($ok) { $client.EndConnect($result); return "OPEN" } else { return "TIMEOUT" }
>   } catch { return ("REFUSED: " + $_.Exception.Message) }
>   finally { $client.Close() }
> }
> Write-Output ("port 5001 -> " + (Test-Port '101.200.204.113' 5001))
> Write-Output ("port 80   -> " + (Test-Port '101.200.204.113' 80))
> Write-Output ("port 22   -> " + (Test-Port '101.200.204.113' 22))`
>
> </details>
>
> 参数名 `$host` 和 PowerShell 内置变量冲突了，我换一个变量名重试：
>
> <details><summary>Ran a command</summary>
>
> - Ran `function Test-Port($addr, $port) {
>   $client = New-Object System.Net.Sockets.TcpClient
>   try {
>     $result = $client.BeginConnect($addr, $port, $null, $null)
>     $ok = $result.AsyncWaitHandle.WaitOne(5000)
>     if ($ok) { $client.EndConnect($result); return "OPEN" } else { return "TIMEOUT" }
>   } catch { return ("REFUSED: " + $_.Exception.Message) }
>   finally { $client.Close() }
> }
> Write-Output ("port 5001 -> " + (Test-Port '101.200.204.113' 5001))
> Write-Output ("port 80   -> " + (Test-Port '101.200.204.113' 80))
> Write-Output ("port 22   -> " + (Test-Port '101.200.204.113' 22))`
>
> </details>
</details>

我的自测结果说明了问题所在：对公网 IP 做 TCP 连通性测试，端口 `5001` 和 `80` 都是**超时（被丢弃）**，而端口 `22` 返回的是**“积极拒绝”**。这个组合说明：实例和网络本身是通的（22 能收到主机的拒绝响应），但 `5001` 的入方向流量被**安全组丢弃**了——默认安全组没有放行 5001，这正好对应我们之前说的“安全组先默认，访问失败再查端口”。

请你在控制台做一步放行：

1. ECI 控制台 → 左侧“容器组” → 点进你这个实例的详情页，找到**“安全组”**（一般在网络信息里）。
2. 点进该安全组 → 切到**“入方向”** → 手动添加一条规则：
   - 授权策略：允许
   - 协议类型：TCP
   - 端口范围：`5001/5001`
   - 授权对象（源）：`0.0.0.0/0`（本实验教学演示这样即可）
3. 保存。

同时请在实例详情里确认一下**容器状态是“运行中”**（而不是反复重启或启动失败），如果状态异常也一并告诉我。

改完安全组并确认容器运行后，告诉我一声，我立刻重新用 `http://101.200.204.113:5001/` 测一遍。

> 你先重试一下，刚才可能是我网络不好，如果不行的话我在操作ECI

<details><summary>1 previous message</summary>

> <details><summary>Ran a command</summary>
>
> - Ran `foreach ($path in @('/api/hello', '/', '/app.js')) {
>   try {
>     $resp = Invoke-WebRequest -Uri ("http://101.200.204.113:5001" + $path) -UseBasicParsing -TimeoutSec 15
>     Write-Output ("[{0}] status={1} len={2}" -f $path, $resp.StatusCode, $resp.Content.Length)
>     if ($path -eq '/api/hello') { Write-Output ("  body: " + $resp.Content) }
>   } catch {
>     Write-Output ("[{0}] ERROR: {1}" -f $path, $_.Exception.Message)
>   }
> }`
>
> </details>
</details>

我重试了，`/api/hello`、`/` 和 `/app.js` 三个请求仍然全部超时，所以这不是你本地网络的问题——是 `5001` 端口在公网上确实没被放行（或容器没监听）。

请你按刚才的步骤操作一下 ECI：

1. 实例详情里确认**容器状态是“运行中”**；
2. 找到该实例的**安全组**，在“入方向”添加一条：协议 TCP、端口 `5001/5001`、授权对象 `0.0.0.0/0`、策略允许。

两步都完成后告诉我，我再测一次。如果容器状态不是“运行中”，也请把详情里的状态或错误信息告诉我。

> 是不是因为我没有钱

大概率不是钱的问题，我们把两种情况的“症状”区分一下：

**如果是余额不足/欠费**，通常是实例根本创建不出来，或者创建后被欠费停机——那整个实例就没了，公网 IP 上**所有端口都会超时**（因为已经没有机器在响应了）。

**但我们现在看到的现象是**：端口 `22` 能收到“目标计算机积极拒绝”的响应，说明 `101.200.204.113` 后面**确实有一台在运行的机器**、网络也是通的；只是 `5001`（和 `80`）的入方向流量被**悄悄丢弃**了。这个“22 有回应、5001 被丢弃”的组合，指向的是**安全组没有放行 5001**，而不是欠费。

所以先麻烦你在控制台确认两件事，把结果告诉我：

1. 在“容器组”列表里，你这个实例的状态是不是**“运行中”**？旁边有没有“欠费”“异常”之类的提示？
2. 如果状态是运行中，就按之前说的，在实例的**安全组 → 入方向**加一条 TCP `5001/5001`、授权对象 `0.0.0.0/0` 的允许规则。

顺带说一句，ECI 按量付费、我们选最低的经济型规格，一次短时实验的费用通常很低；如果余额真的不足，控制台会有明确的欠费提示字样，不会以“端口连不上”这种形式表现。你把实例状态和有没有欠费提示告诉我，我们就能确定下一步。

> 我设置了安全组，是运行中

<details><summary>4 previous messages</summary>

> 好，我重新测一下：
>
> <details><summary>Ran a command</summary>
>
> - Ran `foreach ($path in @('/api/hello', '/', '/app.js')) {
>   try {
>     $resp = Invoke-WebRequest -Uri ("http://101.200.204.113:5001" + $path) -UseBasicParsing -TimeoutSec 15
>     Write-Output ("[{0}] status={1} len={2}" -f $path, $resp.StatusCode, $resp.Content.Length)
>     if ($path -eq '/api/hello') { Write-Output ("  body: " + $resp.Content) }
>   } catch {
>     Write-Output ("[{0}] ERROR: {1}" -f $path, $_.Exception.Message)
>   }
> }`
>
> </details>
>
> 服务已经通了：
>
> - `/api/hello` → 200，返回 `{"message":"你好"}`
> - `/` → 200，页面正常返回
> - `/app.js` → 200，静态资源正常
>
> 我再最短地确认一下用户接口也能从公网访问：
>
> <details><summary>Ran a command</summary>
>
> - Ran `$resp = Invoke-WebRequest -Uri 'http://101.200.204.113:5001/api/conversations' -UseBasicParsing -TimeoutSec 15
> Write-Output ("status=" + $resp.StatusCode + " body=" + $resp.Content)`
>
> </details>
</details>

我的公网自测全部通过，你的应用已经真正跑在云端了：

- 页面 `/` → 200
- 静态资源 `/app.js` → 200
- 健康检查 `/api/hello` → 200，返回 `{"message":"你好"}`
- 用户接口 `/api/conversations` → 200，返回 `[]`

这证明 ECI 已经成功拉取镜像、启动 Gunicorn，并能从公网提供服务。

下一步由你亲自访问。请在浏览器打开：

```
http://101.200.204.113:5001/
```

确认页面正常加载，然后做一次基本操作：新建会话 → 发送一条**非敏感内容**的消息（比如“你好”），确认能得到模型回复，顺便试一下改标题/删除这类 CRUD。你也可以用手机等**另一台设备**访问同一个地址，直观感受它已经不再只跑在你本机。

完成后，请截一张**包含地址栏**的图——地址栏里要能看到 `101.200.204.113` 和 `5001`，同时页面要确实加载出来了；不要截到 Key 或敏感聊天内容。把这张原始截图发给我，我核看后会保存为 `public-page.png`，并在那时再和你讲一次公网开放的风险。

> 我完成了，截取了

<details><summary>2 previous messages</summary>

> 我来找到你刚截的这张图。
>
> <details><summary>Ran 2 commands</summary>
>
> - Ran `Get-ChildItem -Path 'D:\Files\Desktop\isse-labs' -Recurse -File -Include *.png,*.jpg,*.jpeg,*.webp,*.bmp -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-1) -and $_.FullName -like '*2200014163*' } | Select-Object FullName,Length,LastWriteTime | Sort-Object LastWriteTime | Format-Table -AutoSize -Wrap`
> - Ran `$bytes = [System.IO.File]::ReadAllBytes('D:\Files\Desktop\isse-labs\lab3\2200014163-WangQi\Screenshot 2026-09-29 191454.png')[0..7]
> $sig = ($bytes | ForEach-Object { $_.ToString('X2') }) -join ' '
> Write-Output ("PNG signature: " + $sig)
> Add-Type -AssemblyName System.Drawing
> $img = [System.Drawing.Image]::FromFile('D:\Files\Desktop\isse-labs\lab3\2200014163-WangQi\Screenshot 2026-09-29 191454.png')
> Write-Output ("Dimensions: " + $img.Width + " x " + $img.Height)
> $img.Dispose()
> Move-Item 'lab3\2200014163-WangQi\Screenshot 2026-09-29 191454.png' 'lab3\2200014163-WangQi\screenshots\public-page.png'
> Get-ChildItem 'lab3\2200014163-WangQi\screenshots' | Select-Object Name,Length`
>
> </details>
</details>

两张截图都齐了，已保存并核对为有效的 PNG 文件：

- `screenshots/eci-created.png`
- `screenshots/public-page.png`

同时我此前已用公网 IP 独立验证过页面、静态资源和 API 都返回 200，说明这个地址确实在对外提供服务。

现在你已经成功从公网访问到了自己的应用，我要把开放风险再讲清楚一次：这个 `101.200.204.113:5001` 是**公开地址，别人也可能访问到**；你的聊天 API **没有鉴权**，别人若知道这个地址，同样能调用你的后端，消耗你实验用的 DeepSeek 额度；而且这是 **HTTP**，聊天内容不加密，所以测试时不要输入任何敏感信息。**提交 PR 后必须删除这个 ECI**，并确认关联的 EIP 也释放。

在你把结论写进 README 之前，请先用你自己的话回答一个小问题：

1. 你在浏览器里访问 `http://101.200.204.113:5001/`，这个请求是**怎样一步步到达 ECI 里的 Flask** 的？
2. 为什么换一台设备（比如手机）也能打开？
3. 如果陌生人知道了这个公网地址，可能造成什么后果？

你回答完，我再和你讨论，然后把访问方式、验证结论写进 README 并创建这一阶段的 Commit。

> 1.通过http发送请求到ECI 2.因为这个网站放在公有网络上，大家都能访问 3.可能会刷我的api额度

<details><summary>2 previous messages</summary>

> 你的回答我帮你补全第 1 题，第 2、3 题方向都对。
>
> 第 1 题，把链路说完整是这样的：浏览器先拿到公网 IP `101.200.204.113`，向它的 `5001` 端口发起 HTTP 请求；流量经过**弹性公网 IP** 进入 ECI，先被**安全组**检查——我们刚才放行了 TCP 5001，所以能进来；进入容器后，**Gunicorn 监听 `0.0.0.0:5001`** 接收这个请求，再交给 **Flask** 处理并返回响应。这一串里，EIP 负责“公网入口”，安全组负责“放行”，Gunicorn 的 `--bind 0.0.0.0:5001` 负责“在容器里听这个端口”，缺一不可。
>
> 第 2 题对：它跑在公网上、有公网 IP，所以任何联网设备都能访问，不再依赖你本机。
>
> 第 3 题对，主要是刷你的 DeepSeek 额度；另外因为是无鉴权且走 HTTP，别人不仅可能白嫖调用，链路上的明文内容也不加密，所以测试内容一定要用非敏感信息。
>
> 现在我把访问方式和验证结论写进 README。
>
> <details><summary>Edited a file, ran 2 commands</summary>
>
> - Wrote `./lab3/2200014163-WangQi/README.md` (+14 -3)
> - Ran `git status --short lab3/2200014163-WangQi/`
> - Ran `git add lab3/2200014163-WangQi/README.md lab3/2200014163-WangQi/screenshots/
> git commit -m "lab3: 记录 ECI 部署验证并提交截图"`
>
> </details>
</details>

验证结论和两张截图已提交（`9290520`），README 现在也完整覆盖了架构、Dockerfile、ACR、ECI 和验证。

现在进入最后阶段。下一步是**保存本次真实对话轨迹**，这是必交内容。请你在 Codex 左侧**侧边栏里本次对话的标题上右击**，选择“复制”→“复制为 Markdown”，把复制到的真实对话粘贴到 `lab3/2200014163-WangQi/AGENT_TRACE.md` 文件里。

如果你的 Codex 订阅账号支持分享，也可以在同处右击选择“分享”，把得到的**真实分享链接**写进 `AGENT_TRACE.md`（这样就不用粘贴整段 Markdown）。分享前留意一下对话里不要包含个人信息；真实 Key 本来也不应该出现在对话里。

保存好轨迹后告诉我，我会检查这份轨迹里没有 Key 或密码（不做摘要代替），然后创建最后的轨迹 Commit。之后再由你 Push 个人分支、发起中文标题和正文的 PR，并在 PR 提交后删除 ECI、释放 EIP。
