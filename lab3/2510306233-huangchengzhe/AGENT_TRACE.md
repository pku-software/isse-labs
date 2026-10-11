# Lab 3 对话轨迹
# 引导完成 Lab 3 Docker 与 ECI 部署

> 请完整阅读 lab3/AGENTS.md 和 lab3/README.md，从准备个人工作目录开始，按顺序引导我完成 Lab 3。

<details><summary>1 previous message</summary>

> <details><summary>Explored 2 files, ran a command</summary>
>
> - Ran `Get-ChildItem -Force lab3 | Select-Object Mode,Length,Name`
>
> <details><summary>Explored 2 files</summary>
>
> - Read `./lab3/AGENTS.md`
> - Read `./lab3/README.md`
>
> </details>
>
> </details>
</details>

Lab 2 结束时，你的聊天应用只是“在自己这台电脑上能跑”。本机浏览器能打开，不代表别人能访问；哪怕把代码原样复制到另一台电脑，也可能因为 Python 版本、依赖库或启动方式不同而失败。所以 Lab 3 不再增加聊天功能，而是解决两件事：第一，让应用连同它需要的环境一起被打包，换机器也能稳定运行；第二，把这个应用放到云端，让公网里的人能真正访问到。

我们先说“稳定打包”。Docker 是一套把应用和运行环境一起打包、并以“容器”方式运行的工具和规范。对你的 Flask 聊天程序来说，只有 `app.py` 并不够，它还需要 Python、`requirements.txt` 里的库、前端文件以及正确的启动命令。Dockerfile 就是一份说明书，写清楚“用哪个基础环境、复制哪些文件、安装哪些依赖、最后运行什么命令”。根据 Dockerfile 构建出来的结果叫镜像，可以理解为带版本号的应用包；把镜像启动起来、正在处理请求的那个实例，才叫容器。简单说，Docker 是机制，Dockerfile 是说明书，镜像是构建产物，容器是运行中的实例。改完源码后，旧镜像和旧容器不会自动更新，必须重新构建。

容器里还需要一个真正监听端口、接收浏览器请求的程序。这里由 Gunicorn 来启动 Flask 应用：Flask 负责页面和 API 的处理逻辑，Gunicorn 负责把 Flask 当作一个 Web 服务运行起来。Lab 2 里 Flask 自带的 debug 服务器只适合开发，不适合直接对公网提供服务。我们会在 Dockerfile 里把这些内容准备好，而且本实验不需要你在自己电脑上安装 Docker。

再解决“放到云端”。云计算简单说就是按需使用云厂商提供的远程计算和网络资源。Docker 镜像解决了“把应用和环境一起带走”，但它不会自动把应用放到公网。阿里云 ECS 更像租一台远程电脑，需要你自己维护系统、安装环境、部署程序；而 ECI 是弹性容器实例，你把已经构建好的镜像交给它，云平台直接替你启动容器，不需要你管理整台服务器。本实验选择 ECI 来集中体验容器部署。它常被归为 Serverless，但“不用管理服务器”不等于免费：实例只要在运行，即使没人访问也可能持续计费。

那么镜像从哪里来？你的个人 GitHub Fork 存放源码和 Dockerfile。阿里云 ACR 是容器镜像服务，它从你指定的 GitHub 分支在云端完成构建，并保存镜像和版本，相当于镜像仓库；随后 ECI 拉取这个镜像并运行容器，再配置公网入口，让你通过公网 IP 访问。这样职责就很清楚：GitHub 放代码，ACR 构建并存镜像，ECI 运行镜像，Gunicorn 和 Flask 在容器里处理网页与 API。选择这条路径，是为了完整练习“代码 → 可部署镜像 → 云端运行”，而不必先去学习维护 ECS 服务器。

最终你会亲自在浏览器打开云上的聊天页面，并且能解释它为什么不再依赖你自己的电脑一直开机。整个 Lab 3 会按四个阶段推进：

① 准备个人目录并整理 Lab 2 代码，理解并编写 Dockerfile。产物是你的个人目录、应用代码和一份可用的 Dockerfile。

② 把代码 Push 到你的个人分支，让 ACR 从 GitHub 在云端构建镜像。产物是 ACR 里的镜像和对应版本标签。

③ 创建按量计费的 ECI，配置公网入口并运行镜像，你从浏览器实际访问，并留下两张规定截图。产物是运行中的云端应用和验证结果。

④ 提交中文 PR，然后删除 ECI 并核对相关计费资源已释放。产物是提交完成的作业和已经清理的云资源。

现在只需要你先提供两样信息：你的姓名和学号。我会根据它们生成英文名称，并亲自创建你的个人分支 `lab3/<学号>-<姓名拼音>` 和同名个人目录。请把姓名和学号发给我。

> 姓名：黄诚哲，学号：2510306233

<details><summary>2 previous messages</summary>

> 我先检查仓库状态和你的 Lab 2 成果，然后创建你的 Lab 3 个人分支与同名目录。
>
> <details><summary>Explored a file, ran 11 commands</summary>
>
> - Ran `git rev-parse --abbrev-ref HEAD; git status --short; git remote -v; git log -1 --oneline`
>
> - Ran `Get-ChildItem -Directory | Select-Object -ExpandProperty Name`
>
> - Ran `Get-ChildItem -Force lab2 -ErrorAction SilentlyContinue | Select-Object Mode,Length,Name`
>
> - Ran `git fetch origin --quiet; git rev-parse origin/main; git rev-parse main; git status --short --branch`
>
> - Ran `Get-ChildItem -Recurse -Force 'lab2/黄诚哲-2510306233' | Select-Object FullName,Length | Format-Table -AutoSize`
>
> - Ran `git branch --list 'lab3/2510306233-huangchengzhe'; git branch --all --list '*2510306233*'`
>
> <details><summary>Explored a file</summary>
>
> - Read `./lab2/黄诚哲-2510306233/app.py`
>
> </details>
>
> - Ran `Get-Content -Raw 'lab2/黄诚哲-2510306233/requirements.txt'; Get-Content -Raw 'lab2/黄诚哲-2510306233/.gitignore'; Get-Content -Raw 'lab2/黄诚哲-2510306233/.env.example'`
>
> - Ran `Get-Content -Raw 'lab2/黄诚哲-2510306233/frontend/app.js'; Get-Content -Raw 'lab2/黄诚哲-2510306233/frontend/index.html'`
>
> - Ran `git switch -c 'lab3/2510306233-huangchengzhe'`
>
> - Ran `git switch -c 'lab3/2510306233-huangchengzhe'`
>
> - Ran `New-Item -ItemType Directory -Force 'lab3/2510306233-huangchengzhe' | Out-Null; Copy-Item 'lab2/黄诚哲-2510306233/app.py' 'lab3/2510306233-huangchengzhe/app.py'; Copy-Item -Recurse 'lab2/黄诚哲-2510306233/frontend' 'lab3/2510306233-huangchengzhe/frontend'; Copy-Item 'lab2/黄诚哲-2510306233/requirements.txt' 'lab3/2510306233-huangchengzhe/requirements.txt'; Copy-Item 'lab2/黄诚哲-2510306233/.env.example' 'lab3/2510306233-huangchengzhe/.env.example'; Get-ChildItem -Recurse -Force 'lab3/2510306233-huangchengzhe' | Select-Object FullName,Length`
>
> </details>
</details>

你的 Lab 3 个人分支和目录已经准备好了：

- 分支：`lab3/2510306233-huangchengzhe`
- 目录：`lab3/2510306233-huangchengzhe/`

我已经把你 Lab 2 里运行应用必需的文件迁到了这个新目录，包括 `app.py`、`frontend/`、`requirements.txt` 和 `.env.example`。我没有复制 `.env`、真实聊天数据，也没有复制 Lab 2 的 `AGENT_TRACE.md`。

在动手改代码之前，先说明一下你当前应用的工作方式。现在 Flask 在同一个服务里承担三件事：访问 `/` 时返回 `frontend/index.html`，`/style.css` 和 `/app.js` 分别返回静态样式与脚本，`/api/conversations` 等接口负责会话和消息的新建、查询、修改、删除。前端 JavaScript 里全部使用 `/api/...` 这种同源相对路径请求，没有写死服务器地址。真正调用 DeepSeek 的代码在 `app.py` 的 `call_deepseek()` 里，它通过 `os.getenv("DEEPSEEK_API_KEY")` 从后端环境变量读取 Key。也就是说，Key 一直留在后端，浏览器不需要知道，也不应该知道。

进入容器后我们会继续沿用这个方式，原因很直接：Key 只在服务器端使用，不放进前端代码或网页请求里，这样既符合应用逻辑，也避免把真实密钥暴露给浏览器。到 ECI 运行时，会由你在云控制台的环境变量里手动填入 Key，我全程不接触它。

接下来我计划做这些事：

1. 给 `requirements.txt` 增加 `gunicorn`，用来在容器里把 Flask 当作 Web 服务运行。
2. 小改 `app.py`：让数据在 Gunicorn 导入应用时就加载完成，并保留原有页面、静态资源和全部 API 行为。
3. 新增一份完整的 `Dockerfile`，让它以单 worker 的 Gunicorn 监听 `0.0.0.0:5001`，同一个容器继续提供页面、静态资源和 API。
4. 新增 `.dockerignore`、`.gitignore` 和你的 Lab 3 `README.md`，确保 `.env`、缓存、真实数据不会进入镜像或提交。

我先不写 Dockerfile，也不动 `app.py`，等你确认这个计划。确认后我会先展示 Dockerfile 并逐行讲解，再修改代码。请告诉我是否按这个方案继续。

> 按这个方案继续

<details><summary>1 previous message</summary>

> <details><summary>Created 4 files, edited 2 files, ran 2 commands</summary>
>
> - Wrote `./lab3/2510306233-huangchengzhe/.dockerignore` (+11 -0)
> - Wrote `./lab3/2510306233-huangchengzhe/.gitignore` (+6 -0)
> - Wrote `./lab3/2510306233-huangchengzhe/Dockerfile` (+14 -0)
> - Wrote `./lab3/2510306233-huangchengzhe/README.md` (+24 -0)
> - Wrote `./lab3/2510306233-huangchengzhe/app.py` (+5 -3)
> - Wrote `./lab3/2510306233-huangchengzhe/requirements.txt` (+4 -3)
> - Ran `python -m py_compile 'lab3/2510306233-huangchengzhe/app.py'; if ($LASTEXITCODE -eq 0) { 'py_compile: OK' }`
> - Ran `git ls-files 'lab3/2510306233-huangchengzhe'; git ls-files '*/.env' '*.env'; git status --short`
>
> </details>
</details>

我已经把计划落地，但还没有提交。下面是实际文件和每一处的作用。

当前目录结构新增了这些文件：

```text
app.py
frontend/
requirements.txt
Dockerfile
.dockerignore
.gitignore
.env.example
README.md
```

`app.py` 只做了一处必要修改：把 `load_data()` 提前到模块导入时执行。这样 Gunicorn 导入 `app.py` 后，会话数据会先加载完成，再开始接收请求；本地用 `python app.py` 时仍会走原来的 `if __name__ == "__main__"` 分支启动开发服务器。

`requirements.txt` 现在多了：

```text
gunicorn>=21.2
```

真正的容器构建说明是这份 Dockerfile：

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY frontend ./frontend

EXPOSE 5001

CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "1", "app:app"]
```

逐行解释一下：

`FROM python:3.12-slim` 选择包含 Python 的官方基础镜像，`slim` 表示去掉很多不必要软件，镜像更小。基础镜像本身不含你的实验 Key。

`WORKDIR /app` 把容器里的工作目录设为 `/app`，后面的相对路径都基于这里。这样 `frontend`、`data` 和 Flask 里的相对路径才能保持一致。

`COPY requirements.txt .` 先把依赖清单复制进镜像。注意这里构建上下文是 `lab3/2510306233-huangchengzhe/`，不是仓库根目录，所以写的是这个目录里的 `requirements.txt`。

`RUN pip install --no-cache-dir -r requirements.txt` 在构建镜像的阶段安装依赖，`--no-cache-dir` 避免把 pip 缓存留在镜像里。这一步会一并安装 `flask`、`python-dotenv`、`requests` 和 `gunicorn`。

`COPY app.py .` 和 `COPY frontend ./frontend` 把应用源码和前端目录复制进去。到这一步，镜像里既有依赖，也有完整应用。

`EXPOSE 5001` 是元数据，声明“这个容器预期使用 5001 端口”。它本身不会创建公网入口，也不会替你开放端口；真正监听必须由后面的 Gunicorn 完成，ECI 还要另外配置公网 IP 和允许访问的网络条件。

`CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "1", "app:app"]` 是容器启动时执行的命令。`app:app` 前一个 `app` 是 Python 模块名，后一个 `app` 是其中的 Flask 对象；单 worker 监听 `0.0.0.0:5001`，表示任何网络接口都能访问，而不是只允许容器内部访问。这样我们就不会把 Flask 的 debug 服务器直接暴露到公网。

构建和运行的区别也很关键。`COPY`、`RUN` 这些指令发生在构建阶段，它们在生成镜像时执行；`CMD` 发生在运行阶段，只有把镜像启动成容器时才执行。所以 `pip install` 是“构建时安装”，Gunicorn 是“运行时启动”。

构建是按顺序执行的。如果某一步失败，后面的步骤不会继续，必须修正原因并重新触发构建。再次构建时，前面没有变化的步骤可能复用缓存；一旦某一步的指令或它依赖的文件变了，从这一步开始以及后面的步骤通常都要重新执行。ACR 云端构建也遵循这个原理，但不保证每次都断点续跑。

`.dockerignore` 排除了 `.env`、`__pycache__/`、`*.pyc`、`.venv/`、`venv/`、`data/`、`.git/` 以及文档和截图等。这样本地虚拟环境、缓存、真实聊天数据和密钥不会进入构建上下文。`.env.example` 仍然保留，因为里面只有变量名和占位值，没有真实 Key。我也检查过：当前个人目录里的 `.env` 没有被 Git 跟踪，`.gitignore` 已经包含 `.env` 和 `data/`，`app.py` 也通过了 Python 语法检查。

在提交代码前，请先按你的理解回答两个问题，不着急写命令：

1. 为什么 Dockerfile 要先把 `requirements.txt` 复制并安装依赖，之后才复制 `app.py` 和 `frontend`？结合源码和依赖哪个变化更频繁，以及构建缓存来想。

2. 如果 Dockerfile 里写的是 `EXPOSE 5001`，浏览器也访问 5001，但 Gunicorn 实际监听的是 `0.0.0.0:5002`，访问时可能遇到什么问题？只把 `EXPOSE` 改回 5001 能解决吗？

你回答完这两题后，我再继续讨论并进入 Git 提交。

> 1、因为 Docker 构建是分层的，每条指令一层；如果某条指令和它依赖的文件没变，下次构建就直接用缓存，一旦变了，从这层开始后面全部要重新执行。依赖清单 requirements.txt 里的东西基本不变，而源码是经常改的。把复制并安装 requirements.txt 放在前面，改代码时依赖安装那几层还能命中缓存，只有最后复制源码的层重做，构建很快。反过来先复制 app.py 的话，每次改一行代码都会让后面 pip install 的缓存失效，每次都要重新下载安装全部依赖，浪费时间。2、访问 5001 会直接连接被拒绝，打不开页面。因为 EXPOSE 只是元数据，用来声明容器预期用哪个端口，它不会让程序监听端口，也不做端口转发；真正监听端口的是启动命令里的 Gunicorn。Gunicorn 绑在 5002 上，5001 上没有任何进程在听，请求自然失败。只把 EXPOSE 改回 5001 解决不了问题，因为 EXPOSE 本来就不控制实际监听；正确的做法是把 Gunicorn 的 --bind 改成 0.0.0.0:5001，让进程真正在 5001 上监听，EXPOSE 保持一致只是让说明不误导人。

<details><summary>1 previous message</summary>

> <details><summary>Ran 3 commands</summary>
>
> - Ran `git add -- 'lab3/2510306233-huangchengzhe/app.py' 'lab3/2510306233-huangchengzhe/frontend' 'lab3/2510306233-huangchengzhe/requirements.txt' 'lab3/2510306233-huangchengzhe/Dockerfile' 'lab3/2510306233-huangchengzhe/.dockerignore' 'lab3/2510306233-huangchengzhe/.gitignore' 'lab3/2510306233-huangchengzhe/.env.example' 'lab3/2510306233-huangchengzhe/README.md'`
> - Ran `git diff --cached --name-only; git status --short`
> - Ran `git commit -m "Lab3: prepare Flask app and Dockerfile"`
>
> </details>
</details>

你的两个回答都正确，而且把机制讲得很清楚。

第一题的关键点你说到了：构建按指令分层，前面没变化的层可以复用缓存，源码变化频繁、依赖变化较少。先复制并安装 `requirements.txt`，改源码时只有后面的复制步骤重新执行；如果先复制源码，任何一行改动都会让后面的 `pip install` 层失效，每次都要重新安装依赖。

第二题也正确：`EXPOSE` 只是镜像里的端口声明，不负责监听、不负责转发。真正决定“哪个端口在接收连接”的是 Gunicorn 的 `--bind`。如果实际监听 5002，却访问 5001，请求会因为该端口没有进程监听而失败；只改 `EXPOSE` 没有用，必须把 Gunicorn 改成监听 `0.0.0.0:5001`，`EXPOSE` 再和它保持一致。

我已经创建了本次代码 Commit：

```text
1983d95 Lab3: prepare Flask app and Dockerfile
```

提交里包含 10 个文件，分别是应用代码、前端、依赖、Dockerfile、忽略规则和初始 README。`.env` 和 `data/` 都不在其中。

下一步由你亲自把当前分支 Push 到你的个人 GitHub Fork。请在你的 Windows PowerShell 中运行：

```powershell
git push -u origin "lab3/2510306233-huangchengzhe"
```

预期会看到类似 `Branch 'lab3/2510306233-huangchengzhe' set up to track ...` 的提示。运行完成后告诉我“已 Push”，我会检查远端分支是否确实可见，然后进入 ACR 云端构建阶段。

> 已push

<details><summary>1 previous message</summary>

> <details><summary>Ran 2 commands</summary>
>
> - Ran `git ls-remote --heads origin "refs/heads/lab3/2510306233-huangchengzhe"`
> - Ran `git ls-remote --heads origin "refs/heads/lab3/2510306233-huangchengzhe"`
>
> </details>
</details>

远端分支已经确认可见，而且远端提交号和本地一致，说明 Push 成功。现在进入第二阶段：让阿里云 ACR 从你的 GitHub 分支在云端构建镜像。

先理解一下 ACR 的角色。ACR 是阿里云的容器镜像服务，负责两件事：从你指定的 GitHub 分支读取源码和 Dockerfile，在云端执行构建；把构建出来的镜像和版本标签保存起来。ECI 只负责运行镜像，不负责构建。所以现在我们要先在 ACR 创建仓库并触发一次构建。

请在浏览器登录阿里云控制台，按下面顺序操作。地域统一选择“华北 2（北京）”，后面 ECI 也会在北京。

第一步：创建 ACR 个人版实例和私有仓库

1. 打开 ACR 控制台，确认当前地域是“华北 2（北京）”。如果没有可用的个人版实例，先按页面提示创建一个个人版实例，不要购买企业版。
2. 在个人版实例中准备一个命名空间，建议用英文或数字，例如 `isse-labs`。
3. 创建镜像仓库，仓库也建议用英文或数字。仓库类型选“私有”。
4. 创建仓库流程走到“代码源”时，选择 GitHub；GitHub 命名空间填你自己的用户名 `hcccz`，仓库选 `isse-labs`，然后完成页面要求的 GitHub 授权并创建仓库。注意这里的 GitHub 命名空间是你的 GitHub 用户名，不是 ACR 里的镜像命名空间。

第二步：开启构建并添加构建规则

5. 进入刚创建的这个仓库，点击左侧“构建”。
6. 优先开启“海外机器构建”，其他设置先保持默认。海外构建机器通常更容易访问基础镜像和依赖源，但不代表一定成功；如果后面失败，我会根据日志判断。
7. 在构建页点击“添加构建规则”，按下面内容填写：

| 项目 | 填写内容 |
| --- | --- |
| 代码源 / 仓库 | 刚绑定的个人 GitHub `isse-labs` |
| 分支 | `lab3/2510306233-huangchengzhe` |
| 构建上下文目录 | `/lab3/2510306233-huangchengzhe/` |
| Dockerfile 路径 | `Dockerfile` |
| 镜像版本 | `lab3-1983d95` |
| 自动构建 | 关闭 |

8. 保存规则后，点击“立即构建”。注意“保存规则”不等于已经构建，必须看到构建任务真正开始，并且最终显示成功。

构建成功后，直接在对话里告诉我“构建成功”即可，这一步不需要截图或复制日志。如果失败，请把构建日志里的关键报错复制给我，我来帮你定位。

> 构建成功

构建成功，第二阶段的关键动作已经完成。先别急着进入 ECI，请按你的理解回答两个问题：

1. 现在你的应用代码在哪里？镜像构建发生在哪里？构建好的镜像又保存在哪里？

2. 以后如果你在本地修改了代码并提交，要让 ACR 构建到这份新代码，除了本地提交之外，还需要做什么？

你回答后我会把当前已知的 ACR 信息写进个人 README 并创建文档提交，然后进入创建 ECI 的步骤。

> 1、代码在我的个人 GitHub fork（hcccz/isse-labs）的 lab3/2510306233-huangchengzhe 分支上。构建发生在阿里云 ACR 的云端构建机器上，也就是我开启的海外构建机器，不在本地也不在 GitHub。构建出来的镜像保存在 ACR 个人版实例（北京地域）的私有镜像仓库里，版本标签是 lab3-1983d95，之后 ECI 会从这个仓库拉取镜像来运行。2、因为 ACR 是从我 GitHub fork 的分支读代码构建的，看不到我本地仓库，所以本地提交后首先要 git push 把新提交推到 GitHub 的 lab3/2510306233-huangchengzhe 分支。另外这次实验把自动构建关了，所以 push 之后还需要到 ACR 构建页面手动点一次立即构建，才会构建出新镜像；如果以后想省掉手动这步，也可以把规则里的自动构建打开。

<details><summary>1 previous message</summary>

> <details><summary>Edited a file, ran 2 commands</summary>
>
> - Wrote `./lab3/2510306233-huangchengzhe/README.md` (+12 -0)
> - Ran `git add -- 'lab3/2510306233-huangchengzhe/README.md'`
> - Ran `git commit -m "Lab3: document ACR build settings"`
>
> </details>
</details>

你的回答都正确。代码在个人 Fork 的分支上，构建由 ACR 的云端构建机器完成，镜像保存在北京地域的 ACR 私有仓库中；本地修改代码后除了 `git commit`，还要 `git push` 到 GitHub 分支，再回到 ACR 手动点击“立即构建”。自动构建关闭，所以 push 之后不会自动出镜像。

我已经把已知的 ACR 地域、代码源、分支、构建上下文、Dockerfile 路径和镜像版本写进了个人 README，并创建了文档提交：

```text
921aae4 Lab3: document ACR build settings
```

镜像仓库的完整地址等后面在 ECI 选择“我的镜像”时再补记，这样不会凭空写错。

下面进入第三阶段：创建按量计费的 ECI，让它运行刚才的镜像。ECI 不是一台由你维护系统的 ECS 云服务器，而是直接把 ACR 镜像启动成容器，省去管理整台机器的过程。但“不用管理服务器”不等于免费：实例只要在运行，即使没人访问也可能持续计费，自动创建的 EIP 也可能单独计费。

在创建之前必须提醒你：这个实验用公网 HTTP 做短时演示，浏览器到 ECI 的聊天内容没有加密，请不要发送密码、身份证等敏感信息。Key 会留在后端，不会随前端请求传输；但公开的聊天 API 没有鉴权，其他人如果知道公网地址，也可能调用你的后端并消耗实验模型额度。因此测试后要立即删除 ECI 并核对 EIP。

请打开北京地域的 ECI 控制台：

[https://eci.console.aliyun.com/#/eci/](https://eci.console.aliyun.com/#/eci/)

进入左侧“容器组”，点击“创建弹性容器组”。页面会按“基础配置 → 其他设置（选填）→ 确认订单”进行，没有提到的设置就保持默认。

第 1 步：基础配置，按页面从上到下选择。

| 项目 | 本实验怎么选 |
| --- | --- |
| 付费模式、实例类型 | 按量付费、普通实例 |
| 地域 | 华北 2（北京） |
| VPC、交换机 | 选择北京地域当前可用的默认 VPC 和其中一个交换机 |
| 安全组 | 先保持页面默认；访问失败时再检查端口 |
| 容器组配置 | 基础模式；算力类别选“经济型”，CPU 和内存选当前允许的最低组合，名称用 `lab3-2510306233` |
| 容器配置 → 镜像 | 点“选择容器镜像”→“我的镜像”，选你的 ACR 仓库，再选版本标签 `lab3-1983d95` |
| 容器配置 → 镜像拉取策略、启动命令 | 保持默认；启动命令和参数留空，沿用 Dockerfile 里的 Gunicorn 命令 |
| 容器配置 → 容器高级配置 → 环境变量 | 展开高级配置，打开环境变量，由你添加名称 `DEEPSEEK_API_KEY` 和你的实验 Key；不要把值发给我，也不要截含值的图 |
| 数据缓存 | 不额外配置持久化存储 |

当前北京页面没有单独的“容器端口 / 协议”必填项，不需要虚构一个去找。应用实际监听 `5001`，来自 Dockerfile 里的 Gunicorn 启动命令；如果页面版本出现了可选端口设置，就按实际界面配置 `5001/TCP`。配置完点击“下一步：其他设置”。

第 2 步：其他设置（选填）

| 项目 | 本实验怎么选 |
| --- | --- |
| 弹性公网 IP | 选“自动创建”，注意页面显示的带宽和流量计费提示 |
| 镜像仓库访问凭证 | 使用同一阿里云账号的“我的镜像”时先留空 |
| RAM 角色、标签、资源组 | 本实验不需要，保持默认 |

第 3 步：确认订单

创建前请逐项核对地域、镜像及标签、经济型规格、环境变量名称、自动创建的 EIP，以及页面显示的 ECI 与 EIP 费用。你本人确认价格后，再点击创建。不要替我做资源付费决定。

实例显示“运行中”后，请在实例详情或列表界面截一张图，要求能看到实例已创建及状态，且不要包含 Key 或其他凭据；同时把公网 IP 告诉我。收到后我会先自己访问这个公网地址做基础测试，再继续下一步。

> IP地址：101.200.60.217（弹性），172.27.99.62（内）

<details><summary>1 previous message</summary>

> <details><summary>Ran 7 commands</summary>
>
> - Ran `try { $r = Invoke-WebRequest -UseBasicParsing -Uri 'http://101.200.60.217:5001/' -TimeoutSec 20; "STATUS=$($r.StatusCode)"; $r.Content.Substring(0, [Math]::Min(200, $r.Content.Length)) } catch { "ERROR: $($_.Exception.Message)" }`
> - Ran `try { $r = Invoke-WebRequest -UseBasicParsing -Uri 'http://101.200.60.217:5001/api/hello' -TimeoutSec 20; "STATUS=$($r.StatusCode)"; $r.Content } catch { "ERROR: $($_.Exception.Message)" }`
> - Ran `try { $r = Invoke-WebRequest -UseBasicParsing -Uri 'http://101.200.60.217:5001/app.js' -TimeoutSec 20; "STATUS=$($r.StatusCode)"; "LENGTH=$($r.RawContentLength)" } catch { "ERROR: $($_.Exception.Message)" }`
> - Ran `try { $r = Invoke-WebRequest -UseBasicParsing -Uri 'http://101.200.60.217:5001/' -TimeoutSec 20; "STATUS=$($r.StatusCode)"; $r.Content.Substring(0, [Math]::Min(200, $r.Content.Length)) } catch { "ERROR: $($_.Exception.Message)" }`
> - Ran `try { $r = Invoke-WebRequest -UseBasicParsing -Uri 'http://101.200.60.217:5001/api/hello' -TimeoutSec 20; "STATUS=$($r.StatusCode)"; $r.Content } catch { "ERROR: $($_.Exception.Message)" }`
> - Ran `try { $r = Invoke-WebRequest -UseBasicParsing -Uri 'http://101.200.60.217:5001/app.js' -TimeoutSec 20; "STATUS=$($r.StatusCode)"; "LENGTH=$($r.RawContentLength)" } catch { "ERROR: $($_.Exception.Message)" }`
> - Ran `curl.exe -v --max-time 20 'http://101.200.60.217:5001/api/hello'`
>
> </details>
</details>

我按你给的公网 IP 做了基础探测，但在我当前环境里访问 `http://101.200.60.217:5001/` 连接超时，既没有拿到页面，也拿不到 `/api/hello`。这暂时无法区分是我这边的出网限制，还是 ECI 的安全组、实例状态或 5001 端口没有放通。

请你帮我做两件事：

1. 在你自己的浏览器打开：

```text
http://101.200.60.217:5001/
```

告诉我页面是否加载。如果能打开，说明应用在你那边是通的，只是我的运行环境无法直连公网 IP，我后续会以你的浏览器结果和截图为准继续。如果打不开，也把现象告诉我，比如“一直转圈”“连接超时”“拒绝连接”或页面报错。

2. 把 ECI 实例创建成功或列表页的原始截图发给我，要求能看到实例名称、状态为“运行中”，并且截图里不要包含 Key 或其他凭据。你刚才只发了 IP，我还需要这张截图才能存档并继续。

> Codex 不支持图片上传，我已把两张原始截图手动放到个人目录的 screenshots/ 下：eci-created.png（ECI 实例运行中）和 public-page.png（浏览器公网访问，含地址栏，页面已验证聊天和模型回复正常）。请核验文件。同时，我刚才在安全组中做了一个修改，现在你应该可以访问上述网址进行验证了。

<details><summary>1 previous message</summary>

> <details><summary>Ran 9 commands</summary>
>
> - Ran `Get-ChildItem -Force 'lab3/2510306233-huangchengzhe/screenshots' | Select-Object Name,Length,LastWriteTime`
> - Ran `try { $r = Invoke-WebRequest -UseBasicParsing -Uri 'http://101.200.60.217:5001/' -TimeoutSec 20; "ROOT_STATUS=$($r.StatusCode)"; "ROOT_LENGTH=$($r.RawContentLength)"; ($r.Content -match '<title>AI 聊天</title>') } catch { "ROOT_ERROR: $($_.Exception.Message)" }`
> - Ran `try { $r = Invoke-WebRequest -UseBasicParsing -Uri 'http://101.200.60.217:5001/api/hello' -TimeoutSec 20; "HELLO_STATUS=$($r.StatusCode)"; "HELLO_BODY=$($r.Content)" } catch { "HELLO_ERROR: $($_.Exception.Message)" }`
> - Ran `try { $r = Invoke-WebRequest -UseBasicParsing -Uri 'http://101.200.60.217:5001/api/conversations' -TimeoutSec 20; "CONVERSATIONS_STATUS=$($r.StatusCode)"; "CONVERSATIONS_BODY=$($r.Content.Substring(0, [Math]::Min(300, $r.Content.Length)))" } catch { "CONVERSATIONS_ERROR: $($_.Exception.Message)" }`
> - Ran `Add-Type -AssemblyName System.Drawing; $f='lab3/2510306233-huangchengzhe/screenshots/eci-created.png'; $img=[System.Drawing.Image]::FromFile((Resolve-Path $f)); "eci-created: $($img.Width)x$($img.Height) $($img.RawFormat)"; $img.Dispose()`
> - Ran `Add-Type -AssemblyName System.Drawing; $f='lab3/2510306233-huangchengzhe/screenshots/public-page.png'; $img=[System.Drawing.Image]::FromFile((Resolve-Path $f)); "public-page: $($img.Width)x$($img.Height) $($img.RawFormat)"; $img.Dispose()`
> - Ran `Get-Command tesseract -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source`
> - Ran `python -c "import importlib.util; print('PIL', bool(importlib.util.find_spec('PIL'))); print('pytesseract', bool(importlib.util.find_spec('pytesseract'))); print('cv2', bool(importlib.util.find_spec('cv2')))"`
> - Ran `$files = 'lab3/2510306233-huangchengzhe/screenshots/eci-created.png','lab3/2510306233-huangchengzhe/screenshots/public-page.png'; foreach ($f in $files) { $bytes = [System.IO.File]::ReadAllBytes((Resolve-Path $f))[0..7]; $sig = [System.BitConverter]::ToString($bytes); $matches = Select-String -Path $f -Pattern 'DEEPSEEK|sk-[A-Za-z0-9]|api[_-]?key|secret|password|token' -CaseSensitive:$false -AllMatches -ErrorAction SilentlyContinue; "$f SIG=$sig SECRET_MATCHES=$($matches.Count)" }`
>
> </details>
</details>

我重新测试了你的公网地址，现在应用已经可以访问。核验结果如下：

- `http://101.200.60.217:5001/` 返回 HTTP 200，页面内容是 AI 聊天首页。
- `http://101.200.60.217:5001/api/hello` 返回 HTTP 200，内容为 `{"message":"你好"}`。
- `http://101.200.60.217:5001/api/conversations` 返回 HTTP 200，能看到会话数据。
- `screenshots/eci-created.png` 是有效 PNG，尺寸为 2088×292。
- `screenshots/public-page.png` 是有效 PNG，尺寸为 3186×1902。
- 两张图片的 PNG 签名正确，我扫描后未发现 `DEEPSEEK_API_KEY`、`sk-...`、`password`、`token` 等嵌入式敏感文本。

页面和 API 我已经亲自通过公网核验，浏览器访问截图也已落盘；模型实际回复这一项以你刚才的浏览器验证结果为准，我不额外调用你的实验 Key。

现在你已经实际看到了：别人只要拿到这个公网地址，也有可能访问它。所以在继续整理之前，请回答下面几个问题：

1. 你在浏览器输入 `http://101.200.60.217:5001/` 后，请求是怎样一路到达 ECI 容器里的 Flask 的？

2. 为什么换另一台设备、甚至手机，只要在公网上，也能访问同一个地址？

3. 如果一个陌生人知道了这个公网地址，可能造成什么后果？

> 1、浏览器向 101.200.60.217 的 5001 端口发起 TCP 连接，请求包经过公网路由到达阿里云北京地域，先到绑定在 ECI 实例上的弹性公网 IP；然后经过安全组的入方向规则检查（就是我们放行的 5001/TCP），通过后进入 ECI 实例的虚拟网卡；容器里监听 5001 的是 Gunicorn，它接收连接后把请求交给 WSGI 方式运行的 Flask 应用，Flask 按路径匹配路由并返回 HTML，响应再沿原路回到浏览器。2、因为这个应用已经不跑在我自己的电脑上，而是跑在阿里云的 ECI 里，EIP 给它的是一个公网上全球可达的 IP。任何设备只要能上网，向这个 IP 的 5001 端口发请求，都会经过同样的公网路由、安全组和容器的链路得到响应。URL 指向的是公网上的服务器而不是我本机，所以换手机或别的电脑访问结果一样，只取决于服务器在不在、端口通不通。3、这个地址的聊天 API 没有鉴权，陌生人拿到地址就可以使用页面和接口发消息，后端会用我的 Key 调 DeepSeek，额度消耗算在我头上；他还能查看、修改或删除聊天记录，因为 CRUD 接口也是开放的。另外服务用的是 HTTP 明文传输，聊天内容不加密，路上被截获就能看到。所以实验要求不输入敏感信息，做完后马上删除 ECI 实例，并建议之后把实验 Key 作废。

<details><summary>1 previous message</summary>

> <details><summary>Edited a file, ran 5 commands</summary>
>
> - Wrote `./lab3/2510306233-huangchengzhe/README.md` (+13 -0)
> - Ran `git status --short`
> - Ran `git add -- 'lab3/2510306233-huangchengzhe/README.md' 'lab3/2510306233-huangchengzhe/screenshots/eci-created.png' 'lab3/2510306233-huangchengzhe/screenshots/public-page.png'`
> - Ran `git commit -m "Lab3: document ECI deployment and screenshots"`
> - Ran `git status --short; git ls-files 'lab3/2510306233-huangchengzhe'; git log --oneline -5`
> - Ran `Add-Type -AssemblyName System.Drawing; foreach ($f in 'lab3/2510306233-huangchengzhe/screenshots/eci-created.png','lab3/2510306233-huangchengzhe/screenshots/public-page.png') { $img=[System.Drawing.Image]::FromFile((Resolve-Path $f)); "$f $($img.Width)x$($img.Height) $($img.RawFormat)"; $img.Dispose() }`
>
> </details>
</details>

你的回答很完整，链路、跨设备访问原因和开放风险都讲清楚了。ECI 部署验证说明和两张截图已经提交，当前个人目录的 Git 状态是干净的，且提交文件里没有 `.env` 或密钥。

目前你的分支已经有三个有意义的提交：

```text
1983d95 Lab3: prepare Flask app and Dockerfile
921aae4 Lab3: document ACR build settings
0d211d2 Lab3: document ECI deployment and screenshots
```

两张截图也已经跟踪提交，格式和尺寸都再次核验过，可以正常打开。

接下来进入最后整理阶段。请你现在保存真实 Codex 对话轨迹：

在 Codex 桌面应用的侧边栏，找到当前这次对话的标题，**右键点击标题**，选择“复制” → “复制为 Markdown”，然后把复制到的内容粘贴到下面这个文件里：

```text
lab3/2510306233-huangchengzhe/AGENT_TRACE.md
```

如果你的 Codex 账号支持分享，也可以改为右键对话标题选择“分享”，把真实分享链接写进同一个文件，这样就不必粘贴整段 Markdown。不要由我生成摘要代替真实记录。

保存完成后告诉我“轨迹已保存”。我会检查这个文件里没有 Key、密码或令牌等敏感信息，然后创建最后一个轨迹提交。之后再指导你 Push 分支、发起中文 PR，并删除 ECI 和核对 EIP。
