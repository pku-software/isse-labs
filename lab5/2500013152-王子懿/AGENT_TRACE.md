# 交互式完成 Lab5

> 请完整阅读 lab5/AGENTS.md 和 lab5/README.md，按交互式流程带我完成 Lab5。

<details><summary>8 previous messages</summary>

> 我会先完整阅读 `lab5/AGENTS.md` 和 `lab5/README.md`，并检查仓库的上层说明，再按其中的交互流程带你逐步完成。
>
> <details><summary>Ran a command</summary>
>
> - Ran `Get-Location; rg --files -g AGENTS.md -g README.md -g '!node_modules' -g '!.git'`
>
> </details>
>
> 接下来完整读取两份实验说明，确认交互顺序和需要由你亲自完成的环节。
>
> <details><summary>Ran 3 commands</summary>
>
> - Ran `Get-Content -LiteralPath 'lab5/README.md' -Raw -Encoding UTF8`
> - Ran `Get-Content -LiteralPath 'lab5/AGENTS.md' -Raw -Encoding UTF8`
> - Ran `$taskPath = Get-Item -LiteralPath .; while ($null -ne $taskPath) { $taskAgent = Join-Path $taskPath.FullName 'AGENTS.md'; if (Test-Path -LiteralPath $taskAgent) { Write-Output $taskAgent; Get-Content -LiteralPath $taskAgent -Raw -Encoding UTF8 }; $taskPath = $taskPath.Parent }; git status --short`
>
> </details>
>
> 我已完整读完两份指引。Lab5 会沿用你的 Lab2 应用，依次完成自动测试、云端 CI、失败与修复、冒烟检查和本机 runner；课程仓库用于交作业，另建的个人仓库用于运行实验。我负责讲解、代码和排错，你亲自执行命令、提交推送并观察日志。现在先核对课程仓库的分支和远端，确定个人目录名称。
>
> <details><summary>Ran 2 commands</summary>
>
> - Ran `Get-Content -LiteralPath 'README.md' -Raw -Encoding UTF8`
> - Ran `git branch --show-current
> git remote -v
> git config user.name
> git log -1 --format='%h %s'
> Get-ChildItem -LiteralPath 'lab5' -Force | Select-Object Mode,Name`
>
> </details>
>
> 已确认当前目录是你的课程 Fork：`atribert/isse-labs`，当前分支为 `main`，工作区没有未提交改动。接下来准备课程分支、个人目录和独立实验仓库；我会打开内置终端，由你执行这一阶段的命令。
>
> <details><summary>Called a tool</summary>
>
> Tool call
>
> Tool: open_in_codex
> Status: completed
>
> </details>
</details>

我已完整阅读 [lab5/AGENTS.md](./lab5/AGENTS.md) 和 [lab5/README.md](./lab5/README.md)。我们按其中的交互流程推进：每次讲解当前步骤，你操作并反馈真实结果后，再进入下一步。

Lab2 中，你已经做出了可以通过网页操作的聊天应用。以后修改接口、调整数据结构或增加功能，都需要检查原来的功能是否正常。持续集成（CI）就是把这些检查写成自动流程，让代码提交后及时得到检查结果。

这次会先为你的应用编写自动测试，再让 GitHub Actions 在推送后运行测试，并要求后端覆盖率达到 70%。之后故意改坏一处被测试覆盖的功能，观察失败并修复；再加入检查服务能否启动的冒烟脚本，最后让相同检查在你自己的电脑上运行。

我们使用两个仓库：

- **课程 Fork `atribert/isse-labs`**：最后提交应用副本、截图和真实对话轨迹，通过 PR 交作业。
- **新建的个人实验仓库**：保存 Lab2 应用，运行 GitHub Actions，保留成功、失败和修复的记录。

我负责讲解、阅读和编写当前阶段的代码、配置以及排错；你负责亲自运行命令、提交推送、操作 GitHub 与本机 runner，并解释观察到的日志。按照实验指引，我们先完成准备，再进入测试。

目前已确认课程仓库绝对路径为：

```text
C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-labs
```

当前分支是 `main`，远端是 `https://github.com/atribert/isse-labs.git`，工作区干净。还需要你的学号和姓名，才能确定课程分支 `lab5/<学号>-<姓名>` 与同名个人目录。我已请求打开内置终端；如果面板未出现，可在当前目录打开本机 PowerShell。

**现在请完成这一步：**

1. 打开[你的课程 Fork](https://github.com/atribert/isse-labs)，检查 **Sync fork**，有上游更新时先同步。随后在课程仓库根目录执行：

   ```powershell
   git switch main
   git pull --ff-only origin main
   ```

   如果命令报错，先把输出发来；成功后继续：

   ```powershell
   $lab5Student = Read-Host '请输入学号-姓名，姓名写法与此前作业保持一致'
   git switch -c "lab5/$lab5Student"
   New-Item -ItemType Directory -Path "lab5/$lab5Student"
   git branch --show-current
   ```

   分支用于隔离这次作业的提交，个人目录用于存放最终材料。预期最后显示 `lab5/你输入的学号-姓名`。

2. 在 GitHub 新建个人仓库，建议命名为 `isse-lab5-chat-ci`。勾选添加 README，让仓库有初始提交，并确认默认分支为 `main`。

3. 将实验仓库克隆到课程仓库之外。如果采用上述名称和当前 GitHub 账号，可在同一个终端执行：

   ```powershell
   Set-Location ..
   git clone https://github.com/atribert/isse-lab5-chat-ci.git
   Set-Location isse-lab5-chat-ci
   Get-Location
   git branch --show-current
   git remote -v
   ```

   预期实验仓库与 `isse-labs` 是同级目录；分支显示 `main`，远端指向新建的实验仓库。

完成后，请发来：**你的学号和姓名、自己的 Lab2 应用目录、实验仓库链接和本地绝对路径，以及上述分支与远端检查的输出**。下一步我会阅读你的 Lab2 入口、聊天接口、模型调用和存储方式，再协助复制应用，保留原 Lab2 作业。

> (base) PS C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-labs> $lab5Student = Read-Host '2500013152-王子懿'
> 2500013152-王子懿:
> (base) PS C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-labs> git switch -c "lab5/$lab5Student"
> fatal: 'lab5/' is not a valid branch name
> hint: See `man git check-ref-format`
> hint: Disable this message with "git config set advice.refSyntax false"

这个报错是因为 `$lab5Student` 为空。`Read-Host '2500013152-王子懿'` 中引号里的文字只是**提示语**；出现 `2500013152-王子懿:` 后，还要输入内容。如果直接按回车，变量就会变成空字符串，下一条命令实际执行的是 `git switch -c "lab5/"`，因此失败。

现在直接给变量赋值即可。在当前课程仓库目录依次执行：

```powershell
$lab5Student = '2500013152-王子懿'
git switch -c "lab5/$lab5Student"
```

预期看到：

```text
Switched to a new branch 'lab5/2500013152-王子懿'
```

成功后，创建个人提交目录并检查分支：

```powershell
New-Item -ItemType Directory -Path "lab5/$lab5Student" -Force
git branch --show-current
```

最后应显示 `lab5/2500013152-王子懿`，目录为 `lab5/2500013152-王子懿/`。刚才失败的命令没有创建分支，无需撤销操作。

把执行结果发给我；如果已创建并克隆个人实验仓库，也一起发来仓库链接和本地绝对路径，我们就继续导入你的 Lab2 应用。

> 可视性选择private还是public

建议选 **Public（公开）**。这是课程实验仓库，公开后方便助教查看代码和 Actions 的成功、失败及修复记录，而且 GitHub 标准云端 runner 对公开仓库免费。

创建时选择：

- 仓库名：`isse-lab5-chat-ci`
- 可见性：**Public**
- 勾选 **Add a README file**
- `.gitignore` 和 License 暂时保持默认，后面按应用情况配置

真实 `.env` 和 API Key 留在本机，不提交到仓库。创建完成后，把仓库链接发给我，再继续克隆。

> 已完成 2500013152 王子懿 lab2目录：C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-labs\lab2\王子懿-2500013152 实验仓库链接：[https://github.com/atribert/isse-lab5-chat-ci](https://github.com/atribert/isse-lab5-chat-ci)

<details><summary>7 previous messages</summary>

> 收到，你的课程身份是 2500013152 王子懿，实验仓库是 atribert/isse-lab5-chat-ci。接下来先核对课程分支、实验仓库的本地位置，并阅读 Lab2 的代码和依赖。代码、依赖清单和示例配置会复制到实验仓库；虚拟环境则由依赖清单重新安装，原 Lab2 作业保留。确认入口、接口和数据位置后，我再说明具体复制哪些文件。
>
> <details><summary>Ran 2 commands</summary>
>
> - Ran `git branch --show-current
> git remote -v
> git status --short
> Get-ChildItem -LiteralPath 'lab5' -Force | Select-Object Mode,Name
> $lab5Repo = Join-Path (Split-Path -Parent (Get-Location).Path) 'isse-lab5-chat-ci'; if (Test-Path -LiteralPath $lab5Repo) { Write-Output $lab5Repo; git -C $lab5Repo branch --show-current; git -C $lab5Repo remote -v; git -C $lab5Repo status --short; Get-ChildItem -LiteralPath $lab5Repo -Force | Select-Object Mode,Name }`
> - Ran `rg --files --hidden 'lab2/王子懿-2500013152' -g '!.env' -g '!.env.*' -g '.env.example' -g '!*.json' -g '!.git' -g '!node_modules' -g '!venv' -g '!.venv' -g '!__pycache__'
> Get-Content -LiteralPath 'lab2/王子懿-2500013152/README.md' -Raw -Encoding UTF8`
>
> </details>
>
> 已确认：课程分支已创建为 `lab5/2500013152-王子懿`，实验仓库已克隆到课程仓库同级目录，当前为 `main` 且远端正确。你的 Lab2 是单会话 Flask 应用，入口预计为 `app.py`，接口是 `/api/hello`、`/api/messages` 的 CRUD，数据保存在 `data/messages.json`。我现在读取实际代码，避免按模板假设接口。
>
> <details><summary>Ran 3 commands</summary>
>
> - Ran `Get-Content -LiteralPath 'lab2/王子懿-2500013152/app.py' -Raw -Encoding UTF8`
> - Ran `Get-ChildItem -LiteralPath 'lab2/王子懿-2500013152' -Force -Recurse | Select-Object FullName,Length,Mode`
> - Ran `Get-Content -LiteralPath 'lab2/王子懿-2500013152/requirements.txt' -Raw -Encoding UTF8; Write-Output '--- .gitignore ---'; if (Test-Path 'lab2/王子懿-2500013152/.gitignore') { Get-Content -LiteralPath 'lab2/王子懿-2500013152/.gitignore' -Raw -Encoding UTF8 }; Write-Output '--- env example ---'; Get-Content -LiteralPath 'lab2/王子懿-2500013152/.env.example' -Raw -Encoding UTF8`
>
> </details>
>
> 你的应用结构与实验要求匹配：
>
> - 入口：`app.py` 中的 Flask 对象 `app`
> - 前端：`frontend/`
> - 运行依赖：`requirements.txt`
> - 模型调用：`create_message()` 中创建 `OpenAI` 客户端并调用 `client.chat.completions.create(...)`
> - 数据：模块加载时读取 `data/messages.json`，创建、修改、删除后写回
> - 接口：`GET /`、`GET /api/hello`，以及 `/api/messages` 的创建、查询、修改、删除
>
> 自动测试会用 Flask `test_client()`，直接在测试进程内发 HTTP 请求，不需要先启动服务。模型调用会被 mock 成固定回复，避免真实 API Key、网络和费用影响测试。`.env`、真实 Key、`__pycache__` 和虚拟环境只留在本机；实验仓库只保留 `.env.example`。由于原 `data/messages.json` 可能包含个人聊天记录，我会在实验仓库创建空数据文件 `[]`，避免把旧聊天内容带入新仓库。
>
> 现在将 `app.py`、`frontend/`、`requirements.txt`、`.env.example`、`README.md` 和空的 `data/messages.json` 复制到实验仓库，并建立适合本实验的 `.gitignore`。这一步不会读取或复制 `.env`。
>
> <details><summary>Ran a command</summary>
>
> - Ran `$src = 'C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-labs\lab2\王子懿-2500013152'; $dst = 'C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-lab5-chat-ci'; Copy-Item -LiteralPath (Join-Path $src 'app.py') -Destination (Join-Path $dst 'app.py') -Force; Copy-Item -LiteralPath (Join-Path $src 'requirements.txt') -Destination (Join-Path $dst 'requirements.txt') -Force; Copy-Item -LiteralPath (Join-Path $src '.env.example') -Destination (Join-Path $dst '.env.example') -Force; Copy-Item -LiteralPath (Join-Path $src 'README.md') -Destination (Join-Path $dst 'README.md') -Force; Copy-Item -LiteralPath (Join-Path $src 'frontend') -Destination (Join-Path $dst 'frontend') -Recurse -Force; New-Item -ItemType Directory -Path (Join-Path $dst 'data') -Force | Out-Null; Set-Content -LiteralPath (Join-Path $dst 'data/messages.json') -Value '[]' -Encoding UTF8; @('.env','__pycache__/','.venv/','.pytest_cache/','htmlcov/','.coverage','*.pyc','data/*.json','!data/messages.json') | Set-Content -LiteralPath (Join-Path $dst '.gitignore') -Encoding UTF8; Get-ChildItem -LiteralPath $dst -Force -Recurse | Where-Object { $_.FullName -notmatch '\.git($|\\)' } | Select-Object FullName,Length,Mode; git -C $dst status --short`
>
> </details>
>
> 应用已复制到实验仓库，未复制 `.env`、旧聊天记录或缓存；空数据文件和忽略规则已准备好。接下来由你检查并提交初始版本：`commit` 只记录在本地，`push` 才会上传到 GitHub。推送后，仓库网页应能看到 Flask 入口、前端、依赖、示例配置和空数据文件。
</details>

应用导入已完成，实验仓库本地路径为：

```text
C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-lab5-chat-ci
```

已复制：

- `app.py`
- `frontend/`
- `requirements.txt`
- `.env.example`
- `README.md`
- `data/messages.json`（空数组）
- `.gitignore`

没有复制真实 `.env`、旧聊天记录、虚拟环境或 Python 缓存。

你的应用会通过 `app.py` 中的 `app` 启动；创建接口是 `POST /api/messages`，查询、修改、删除接口分别是 `GET`、`PATCH`、`DELETE /api/messages`。后续测试会用 Flask `test_client()` 调用这些接口，并把 `OpenAI` 模型调用替换为固定 mock 回复。这样测试只验证应用逻辑，不依赖真实 API Key 或网络。

请在实验仓库目录执行：

```powershell
Set-Location 'C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-lab5-chat-ci'

Get-ChildItem -Force
git status --short
git check-ignore -v .env __pycache__/ .pytest_cache/ data/messages.json
```

重点检查：

- `.env` 被忽略；
- `__pycache__` 和测试缓存被忽略；
- `data/messages.json` 没有被忽略；
- 没有看到真实 Key 或旧聊天记录。

然后安装运行依赖：

```powershell
python -m pip install -r requirements.txt
```

确认没有问题后提交并推送初始应用：

```powershell
git add app.py frontend requirements.txt .env.example .gitignore README.md data/messages.json
git commit -m "feat: import Lab2 chat application"
git push -u origin main
```

在 GitHub 仓库页面确认这些文件已经出现。请把以下内容发给我：

1. `git status --short` 的结果；
2. `git push` 的结果；
3. GitHub 页面中初始提交的链接或截图。

确认导入完成后，我们进入第一个重点：编写聊天记录 CRUD 测试和一类非法输入测试。

> (base) PS C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-lab5-chat-ci> git status --short\
> &#x20;M README.md\
> ?? .env.example\
> ?? .gitignore\
> ?? app.py\
> ?? data/\
> ?? frontend/\
> ?? requirements.txt(base) PS C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-lab5-chat-ci> git push -u origin main\
> Enumerating objects: 15, done.\
> Counting objects: 100% (15/15), done.\
> Delta compression using up to 16 threads\
> Compressing objects: 100% (10/10), done.\
> Writing objects: 100% (13/13), 7.42 KiB | 2.47 MiB/s, done.\
> Total 13 (delta 0), reused 0 (delta 0), pack-reused 0 (from 0)\
> To https\://github.com/atribert/isse-lab5-chat-ci.git\
> &#x20;  2941550..04e9806  main -> main\
> branch 'main' set up to track 'origin/main'.链接：[https://github.com/atribert/isse-lab5-chat-ci](https://github.com/atribert/isse-lab5-chat-ci)

<details><summary>7 previous messages</summary>

> 初始版本已经成功推送到 GitHub，`main` 已跟踪 `origin/main`。你贴出的 `status` 是提交前的状态，推送结果说明这些文件随后已经进入提交；我先核对远端提交和工作区，再进入测试阶段。测试阶段会把一次完整 CRUD 串起来：创建后查询、修改、再次确认、删除后确认消失；另测一类非法输入，并用 mock 固定模型回复。
>
> <details><summary>Ran 2 commands</summary>
>
> - Ran `$dst='C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-lab5-chat-ci'; git -C $dst status --short; git -C $dst log -2 --oneline --decorate; git -C $dst ls-files`
> - Ran `$dst='C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-lab5-chat-ci'; git -C $dst show --stat --oneline HEAD; git -C $dst check-ignore -v .env __pycache__/ .pytest_cache/ data/messages.json 2>&1`
>
> </details>
>
> 导入验证通过：远端提交 `04e9806` 已包含应用文件，工作区干净；`.env`、缓存被忽略，`data/messages.json` 已被跟踪。
>
> 测试的关键是隔离状态。当前应用在导入时读取固定的 `data/messages.json`，如果测试直接使用它，不同测试会互相污染。因此我会让数据目录支持环境变量 `LAB5_DATA_DIR`，默认仍然使用原来的 `data/`；测试 fixture 会把 `MESSAGES_FILE` 指到临时目录，并重置内存列表和 ID。模型调用则替换成固定的 `"固定测试回复"`。
>
> 这两个测试分别验证：
>
> 1. `POST` 创建后拿到记录 ID，`GET` 能查到，`PATCH` 能更新，`DELETE` 后再次 `GET` 为空；
> 2. 空白消息返回 `400` 和错误提示，并且记录列表仍为空。
>
> 我现在添加这个小型可配置改动、`requirements-dev.txt` 和 `tests/test_chat_api.py`，然后运行测试。
>
> <details><summary>Created 2 files, edited a file, ran a command</summary>
>
> - Wrote `~/Documents/pdf/大二上/智能化软件系统与工程/isse-lab5-chat-ci/app.py` (+2 -1)
> - Wrote `~/Documents/pdf/大二上/智能化软件系统与工程/isse-lab5-chat-ci/requirements-dev.txt` (+2 -0)
> - Wrote `~/Documents/pdf/大二上/智能化软件系统与工程/isse-lab5-chat-ci/tests/test_chat_api.py` (+64 -0)
> - Ran `python -m pip install -r requirements.txt -r requirements-dev.txt
> python -m pytest -q`
>
> </details>
>
> 测试代码已写好，但本机安装开发依赖时遇到环境问题：现有镜像 `mirrors.tuna.tsinghua.edu.cn` 的 SSL 连接失败，导致 `pytest` 没装上，随后 `python -m pytest` 报 `No module named pytest`。这不是应用或测试失败，而是包索引连接失败。我会先尝试官方 PyPI 索引；如果仍失败，你可在本机网络可用时重复同一安装命令。
>
> <details><summary>Ran 2 commands</summary>
>
> - Ran `python -m pip install --index-url https://pypi.org/simple -r requirements.txt -r requirements-dev.txt`
> - Ran `Get-Command pytest -ErrorAction SilentlyContinue | Select-Object Source,Version; conda list pytest; python -c "import sys; print(sys.executable); import flask; print(flask.__version__)"; Get-ChildItem -Path 'C:\Users\16256\miniconda3\Lib\site-packages' -Filter 'pytest*' -ErrorAction SilentlyContinue | Select-Object Name`
>
> </details>
>
> 官方 PyPI 也因当前环境的 SSL 连接问题无法访问，因此暂时无法在这台环境里安装 `pytest`。测试和应用改动本身已经写入实验仓库，下一步需要先恢复 Python 包索引连接，再执行测试。你可以使用课程允许的网络或已有镜像；不要把任何 Key 写进命令或仓库。
</details>

初始应用已成功推送到实验仓库：

[https://github.com/atribert/isse-lab5-chat-ci](https://github.com/atribert/isse-lab5-chat-ci)

我已添加：

- `LAB5_DATA_DIR` 配置支持，默认仍使用 `data/messages.json`
- `requirements-dev.txt`
- `tests/test_chat_api.py`

测试设计如下：

- 使用 Flask `test_client()`，不启动真实服务；
- mock `OpenAI`，固定返回 `固定测试回复`；
- CRUD 测试：创建、查询、修改、删除，再确认记录为空；
- 非法输入测试：空白消息返回 `400`，并确认没有新增记录；
- 每个测试使用临时数据文件和独立内存状态。

当前唯一阻塞是本机安装 `pytest` 时的 SSL 网络错误：

```text
Could not fetch URL ... /simple/pytest/
No matching distribution found for pytest
```

这表示依赖没有安装成功，暂时还不能运行测试。请在网络或 Python 包索引可用后，在实验仓库目录执行：

```powershell
Set-Location 'C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-lab5-chat-ci'

python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q
```

预期结果：

```text
2 passed
```

如果仍使用当前镜像失败，可以先检查：

```powershell
python -m pip config list
python -m pip index versions pytest
```

不要把 API Key 写入命令、测试或 Git 仓库。安装成功并运行测试后，把完整输出发给我；我们再根据真实结果补充必要测试并查看覆盖率。

> 已显示2passed，已完成

<details><summary>4 previous messages</summary>

> 很好，两个重点测试都通过了。现在进入覆盖率阶段：测试通过只说明断言满足；覆盖率还要确认测试实际执行了多少后端语句。我们会统计 `app.py`，报告 `Missing` 行，并设置 70% 门槛。先运行准确命令，依据真实报告决定是否需要补充测试。
>
> <details><summary>Ran a command</summary>
>
> - Ran `python -m pytest -q --cov=app --cov-report=term-missing --cov-fail-under=70`
>
> </details>
>
> 覆盖率通过：`app.py` 共 94 条可执行语句，执行了 75 条，覆盖率约 79.79%，高于 70% 门槛；两个测试均通过。`Missing` 中主要是异常分支、Key 缺失和不存在记录等未覆盖路径，本实验不要求扩展成全面测试项目。
>
> 现在把同一条验证命令放进 GitHub Actions。工作流中的 `on` 定义 push/PR 触发条件，`runs-on` 选择云端 runner，`uses` 复用官方检出和 Python 环境 Action，`run` 执行依赖安装与覆盖率测试。先使用 `ubuntu-latest`，为后面的云端成功记录保留基线。冒烟检查将在本地完成后再加入同一份工作流。
>
> <details><summary>Created a file, ran a command</summary>
>
> - Wrote `~/Documents/pdf/大二上/智能化软件系统与工程/isse-lab5-chat-ci/.github/workflows/ci.yml` (+26 -0)
> - Ran `git status --short
> git diff -- app.py requirements-dev.txt tests/test_chat_api.py .github/workflows/ci.yml`
>
> </details>
</details>

覆盖率检查已通过：

```text
2 passed
app.py: 94 statements, 80% coverage
Required test coverage of 70% reached
```

`Cover` 表示执行到的代码比例，`Missing` 表示没有被这两个重点测试走到的行。当前 80% 已超过要求，不需要把测试扩展成完整测试项目。

我已添加 GitHub Actions 工作流：

```text
.github/workflows/ci.yml
```

它会在以下情况触发：

- 推送到 `main`
- 向 `main` 发起 Pull Request

云端 job 使用 `ubuntu-latest` 和 Python 3.11，依次检出代码、安装依赖，并运行：

```bash
python -m pytest -q --cov=app --cov-report=term-missing --cov-fail-under=70
```

请在实验仓库执行：

```powershell
Set-Location 'C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-lab5-chat-ci'

git add app.py requirements-dev.txt tests .github/workflows/ci.yml
git commit -m "test: add chat API coverage and CI workflow"
git push
```

然后打开：

[实验仓库 Actions](https://github.com/atribert/isse-lab5-chat-ci/actions)

进入最新运行，展开 job 和 **Run tests and coverage** 步骤，确认测试通过、覆盖率至少 70%，并核对运行对应的提交。

请发来：

1. 最新 Actions 运行链接；
2. 测试步骤中的通过与覆盖率日志；
3. 如果有截图，也可以直接发来，后面会整理为 `cloud-passed.png`。

确认云端成功后，我们开始“失败与修复”实验。

> [https://github.com/atribert/isse-lab5-chat-ci/actions/runs/39362203956](https://github.com/atribert/isse-lab5-chat-ci/actions/runs/39362203956) 已显示通过

<details><summary>2 previous messages</summary>

> 云端成功运行已确认：Actions 使用 `ubuntu-latest` 执行了当前提交，测试和 70% 覆盖率检查通过。现在进行一次真实回归失败实验。
>
> 我们选择删除接口，因为 CRUD 测试在删除后再次查询，明确要求记录消失。故意修改 `delete_message()`，让它仍返回成功响应，但暂时不从 `messages` 列表移除记录。这样测试预期保持不变，CI 应该在同一个 CRUD 测试的最后断言处失败。失败日志要看三件事：失败测试名、预期值和实际值，以及它们如何对应这次代码改动。请保存这次失败运行的截图和链接，后续作为 `failed.png` 证据。
>
> <details><summary>Edited a file, ran a command</summary>
>
> - Wrote `~/Documents/pdf/大二上/智能化软件系统与工程/isse-lab5-chat-ci/app.py` (+2 -1)
> - Ran `python -m pytest -q`
>
> </details>
</details>

云端成功运行已确认：运行链接是：

[Actions run 39362203956](https://github.com/atribert/isse-lab5-chat-ci/actions/runs/39362203956)

现在已故意制造失败：删除接口仍返回 `200`，但不再执行 `messages.remove(record)`。CRUD 测试的预期没有改变，因此它会在删除后查询时发现记录仍存在。

本机复现结果为：

```text
1 failed, 1 passed
FAILED tests/test_chat_api.py::test_message_crud_flow
AssertionError: ... == []
```

这说明：

- 失败测试：`test_message_crud_flow`
- 预期：删除后查询结果为 `[]`
- 实际：仍返回包含该记录的列表
- 原因：删除接口没有从内存列表移除记录

请提交并推送这次故意失败的版本：

```powershell
Set-Location 'C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-lab5-chat-ci'

git add app.py
git commit -m "test: demonstrate delete regression"
git push
```

然后打开新的 Actions 运行，进入失败 job 的测试步骤，保存：

1. 失败测试名；
2. 预期与实际结果；
3. 本次提交对应的运行链接；
4. 失败截图。

请把失败运行链接和截图发给我，并用自己的话解释“为什么删除接口返回成功，但测试仍失败”。我会先整理为 `failed.png`，再修复 `messages.remove(record)` 并重新推送。

> [**test: demonstrate delete regression**](https://github.com/atribert/isse-lab5-chat-ci/actions/runs/39362718933)  预期1failed, 1passed，检验不通过，[https://github.com/atribert/isse-lab5-chat-ci/actions/runs/39362718933](https://github.com/atribert/isse-lab5-chat-ci/actions/runs/39362718933)
>
> User context
>
> Images:
> - `~/AppData/Local/Temp/codex-clipboard-5c7de99d-f36f-4fbd-b9e7-7ba6fe898136.png`

<details><summary>2 previous messages</summary>

> 你的解释和截图已经证明失败实验完成：运行 `39362718933` 由提交 `2b6b0c1` 触发，job 以退出码 1 结束；截图中的 Node.js 弃用提示是警告，真正导致失败的是测试进程非零退出。失败原因正是删除接口返回成功后，记录仍存在。
>
> 我会把这张原图保存到课程个人目录的 `screenshots/failed.png`，然后恢复 `messages.remove(record)`。修复后本机重新运行测试和覆盖率，确认同一条测试恢复通过；你再提交并推送修复版本，观察新的 Actions 运行。
>
> <details><summary>Edited a file, ran 3 commands</summary>
>
> - Ran `$course='C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-labs'; $shotDir=Join-Path $course 'lab5\2500013152-王子懿\screenshots'; New-Item -ItemType Directory -Path $shotDir -Force | Out-Null; Copy-Item -LiteralPath 'C:\Users\16256\AppData\Local\Temp\codex-clipboard-5c7de99d-f36f-4fbd-b9e7-7ba6fe898136.png' -Destination (Join-Path $shotDir 'failed.png') -Force; Get-Item -LiteralPath (Join-Path $shotDir 'failed.png') | Select-Object FullName,Length`
> - Wrote `~/Documents/pdf/大二上/智能化软件系统与工程/isse-lab5-chat-ci/app.py` (+1 -2)
> - Ran `python -m pytest -q --cov=app --cov-report=term-missing --cov-fail-under=70`
> - Ran `git status --short
> git diff -- app.py`
>
> </details>
</details>

失败证据已保存为：

[failed.png](./lab5/2500013152-王子懿/screenshots/failed.png)

你的分析正确：

- 预期：删除后查询结果为空；
- 实际：记录仍存在；
- 原因：删除接口返回成功，但没有执行 `messages.remove(record)`；
- Node.js 弃用提示只是警告，不是失败原因。

我已恢复删除逻辑：

```python
messages.remove(record)
```

本机修复验证通过：

```text
2 passed
Total coverage: 79.79%
Required test coverage of 70% reached
```

现在请推送修复版本：

```powershell
Set-Location 'C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-lab5-chat-ci'

git add app.py
git commit -m "fix: restore message deletion"
git push
```

然后打开新的 Actions 运行，确认：

- 测试通过；
- 覆盖率至少 70%；
- 这是修复提交对应的新运行。

把修复后的 Actions 链接发给我。接下来我们会复制并适配课程提供的 `templates/smoke_test.py`。

> 测试通过，[https://github.com/atribert/isse-lab5-chat-ci/actions/runs/39362946653](https://github.com/atribert/isse-lab5-chat-ci/actions/runs/39362946653)，
>
> User context
>
> Images:
> - `~/AppData/Local/Temp/codex-clipboard-a5139910-698c-45f4-86c8-f208c1868c66.png`

<details><summary>4 previous messages</summary>

> 修复运行已通过，截图显示 `fix: restore message deletion` 对应提交成功；我会保存为 `cloud-passed.png`。接下来进入冒烟检查：它会真正启动 Flask 进程，再通过 HTTP 访问首页 `/` 和连通性接口 `/api/hello`，检查进程启动、HTTP 服务和响应内容。课程骨架已经负责启动、等待、请求和清理，我们只适配入口与路径。
>
> <details><summary>Ran 4 commands</summary>
>
> - Ran `Get-Content -LiteralPath 'lab5/templates/smoke_test.py' -Raw -Encoding UTF8`
> - Ran `$course='C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-labs'; $shotDir=Join-Path $course 'lab5\2500013152-王子懿\screenshots'; Copy-Item -LiteralPath 'C:\Users\16256\AppData\Local\Temp\codex-clipboard-a5139910-698c-45f4-86c8-f208c1868c66.png' -Destination (Join-Path $shotDir 'cloud-passed.png') -Force; Get-Item -LiteralPath (Join-Path $shotDir 'cloud-passed.png') | Select-Object FullName,Length`
> - Ran `$src='C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-labs\lab5\templates\smoke_test.py'; $dst='C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-lab5-chat-ci\scripts\smoke_test.py'; New-Item -ItemType Directory -Path (Split-Path -Parent $dst) -Force | Out-Null; Copy-Item -LiteralPath $src -Destination $dst -Force; Get-Content -LiteralPath $dst -TotalCount 25`
> - Ran `python scripts/smoke_test.py`
>
> </details>
>
> 冒烟脚本已适配并在本机通过：
>
> ```text
> PASS /
> PASS /api/hello
> ```
>
> 终端中的中文提示因当前 PowerShell 编码显示为乱码，但两个 HTTP 检查均为 `PASS`，脚本也正常结束。脚本使用临时端口和临时 `LAB5_DATA_DIR`，不会修改正式数据。
>
> 现在把 `Run smoke test` 加到同一份 `ci.yml`，放在测试与覆盖率步骤之后。这样新的云端运行会同时证明：业务测试通过、覆盖率达标、服务能够启动并响应 HTTP。
>
> <details><summary>Edited a file</summary>
>
> - Wrote `~/Documents/pdf/大二上/智能化软件系统与工程/isse-lab5-chat-ci/.github/workflows/ci.yml` (+3 -0)
>
> </details>
</details>

修复运行已通过：

[Actions run 39362946653](https://github.com/atribert/isse-lab5-chat-ci/actions/runs/39362946653)

我已保存成功截图：

[cloud-passed.png](./lab5/2500013152-王子懿/screenshots/cloud-passed.png)

冒烟检查的作用是验证应用能作为真正的 HTTP 服务启动。它与 Flask `test_client()` 的区别是：除了业务处理，还检查进程启动、监听端口和外部 HTTP 响应。课程脚本已经负责启动、等待、请求和清理，我们只确认了：

```text
APP_IMPORT = "app:app"
HOME_PATH = "/"
HELLO_PATH = "/api/hello"
EXPECTED_HELLO = {"message": "你好"}
```

本机运行结果中两个检查均通过：

```text
PASS /
PASS /api/hello
```

我已将脚本复制到：

```text
scripts/smoke_test.py
```

并在同一份工作流中增加：

```yaml
- name: Run smoke test
  run: python scripts/smoke_test.py
```

请提交并推送：

```powershell
Set-Location 'C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-lab5-chat-ci'

git add scripts/smoke_test.py .github/workflows/ci.yml
git commit -m "ci: add smoke test"
git push
```

然后打开新的 Actions 运行，确认：

- 测试通过；
- 覆盖率至少 70%；
- `Run smoke test` 中出现 `PASS /` 和 `PASS /api/hello`；
- 服务正常停止，整个 job 成功。

把新的云端运行链接和截图发给我。之后进入本机 self-hosted runner 阶段。

> 测试通过，[https://github.com/atribert/isse-lab5-chat-ci/actions/runs/39363156899](https://github.com/atribert/isse-lab5-chat-ci/actions/runs/39363156899)
>
> User context
>
> Images:
> - `~/AppData/Local/Temp/codex-clipboard-bf875e41-0f11-4d0a-9a65-9c2db8fb070b.png`

<details><summary>2 previous messages</summary>

> <details><summary>Ran a command</summary>
>
> - Ran `$course='C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-labs'; $shotDir=Join-Path $course 'lab5\2500013152-王子懿\screenshots'; Copy-Item -LiteralPath 'C:\Users\16256\AppData\Local\Temp\codex-clipboard-bf875e41-0f11-4d0a-9a65-9c2db8fb070b.png' -Destination (Join-Path $shotDir 'cloud-passed-2.png') -Force; Get-Item -LiteralPath (Join-Path $shotDir 'cloud-passed-2.png') | Select-Object FullName,Length`
>
> </details>
>
> 云端冒烟检查运行 `39363156899` 已通过；这张截图已整理到课程个人目录的 `screenshots/`，当前目录还保留了上一张同阶段截图副本，最终会按序保留。现在开始本机 runner。
>
> runner 是执行 job 的程序。`self-hosted` 表示 GitHub 不再分配临时云端机器，而把同一份工作流交给你电脑上在线的 runner。注册分为下载、关联仓库、启动三步；注册 token 只在你自己的终端使用，不能发到对话或截图中。runner 程序和仓库代码分开保存，建议放在仓库之外。
</details>

云端冒烟检查已通过：

[Actions run 39363156899](https://github.com/atribert/isse-lab5-chat-ci/actions/runs/39363156899)

这次运行证明同一份工作流已经完成：

- Flask 测试通过；
- 覆盖率至少 70%；
- 冒烟检查通过；
- 服务能够启动并响应 `/` 与 `/api/hello`。

现在进入本机 self-hosted runner 阶段。

self-hosted runner 是安装在你电脑上的 GitHub Actions 执行程序。之前 `runs-on: ubuntu-latest` 使用 GitHub 临时云端机器；后面将改成 `runs-on: self-hosted`，让相同的测试、覆盖率和冒烟检查在你的电脑上执行。runner 会在自己的工作区重新检出仓库，与你平时编辑应用的目录不同。

请按以下步骤操作：

1. 打开仓库设置：

   [实验仓库 Settings](https://github.com/atribert/isse-lab5-chat-ci/settings/actions/runners)

   进入：

   ```text
   Settings → Actions → Runners → New self-hosted runner
   ```

2. 选择：

   ```text
   Operating system: Windows
   Architecture: x64
   ```

3. 在仓库之外创建 runner 目录，例如：

   ```powershell
   New-Item -ItemType Directory -Path 'C:\Users\16256\actions-runner\isse-lab5' -Force
   Set-Location 'C:\Users\16256\actions-runner\isse-lab5'
   ```

4. 按 GitHub 页面显示的当前命令下载并解压 runner。注册命令中的 URL、名称和 token 使用页面提供的内容。token 只在本机终端输入，不要发给我，也不要截图显示。

5. 注册完成后，前台启动：

   ```powershell
   .\run.cmd
   ```

   保持这个终端窗口打开。网页应显示 runner 为 **Idle/Online**，终端应显示正在等待任务。

不要把 runner 程序放进实验仓库，也不要提交 runner 目录。完成后请告诉我：

- GitHub 页面是否显示 runner 在线；
- runner 的名称；
- 本机终端是否显示等待任务。

不要发送注册 token。确认 runner 在线后，我会把同一份 `.github/workflows/ci.yml` 的 `runs-on` 切换为 `self-hosted`，并根据 Windows runner 调整依赖安装步骤。

> 这一步下载到哪里

下载到**仓库之外的独立目录**，不要放进 `isse-lab5-chat-ci` 或课程仓库。推荐：

```text
C:\Users\16256\actions-runner\isse-lab5
```

在 PowerShell 执行：

```powershell
New-Item -ItemType Directory -Path 'C:\Users\16256\actions-runner\isse-lab5' -Force
Set-Location 'C:\Users\16256\actions-runner\isse-lab5'
```

然后回到 GitHub 的 **New self-hosted runner → Windows → x64** 页面：

1. 点击下载 runner；
2. 将下载的 `.zip` 保存或移动到上述目录；
3. 在该目录解压；
4. 继续执行 GitHub 页面提供的配置命令；
5. 最后运行：

```powershell
.\run.cmd
```

目录中会出现 `config.cmd`、`run.cmd`、`_work` 等 runner 文件。不要把这个目录提交到 Git，也不要截图暴露注册 token。

> 目录中已出现这些文件，现在显示√ Connected to GitHub
>
> Current runner version: '2.337.0'
> 2026-10-20 03:23:45Z: Listening for Jobs

<details><summary>2 previous messages</summary>

> runner 已成功连接 GitHub，并处于 `Listening for Jobs`，说明注册和启动完成。现在只切换同一份工作流的执行位置：把 `runs-on` 从 `ubuntu-latest` 改为 `self-hosted`。测试命令、覆盖率门槛和冒烟脚本都保持不变；`setup-python` 会在 Windows runner 上准备 Python 3.11，随后安装依赖。推送后，runner 终端应从 `Listening for Jobs` 变成接收任务并显示步骤输出，Actions 页面也会显示 self-hosted 标签。
>
> <details><summary>Edited a file, ran 2 commands</summary>
>
> - Wrote `~/Documents/pdf/大二上/智能化软件系统与工程/isse-lab5-chat-ci/.github/workflows/ci.yml` (+1 -1)
> - Ran `Get-Content -LiteralPath '.github/workflows/ci.yml' -Raw -Encoding UTF8; git status --short`
> - Ran `git status --short; Get-ChildItem -LiteralPath 'lab5/2500013152-王子懿/screenshots' -Force | Select-Object Name,Length`
>
> </details>
</details>

runner 状态正确：

```text
Connected to GitHub
Listening for Jobs
```

我已将工作流改为：

```yaml
runs-on: self-hosted
```

其余测试、覆盖率和冒烟步骤保持不变。请在实验仓库目录的另一个 PowerShell 窗口执行：

```powershell
Set-Location 'C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-lab5-chat-ci'

git add .github/workflows/ci.yml
git commit -m "ci: run checks on self-hosted runner"
git push
```

保持 runner 窗口继续运行，观察它从：

```text
Listening for Jobs
```

变为接收任务、检出代码、安装依赖并执行测试。GitHub Actions 页面中应看到：

- runner 类型为 `self-hosted`
- 测试通过；
- 覆盖率至少 70%；
- `Run smoke test` 通过；
- 整个 job 成功。

如果任务长时间排队，检查仓库 Settings 中 runner 是否仍为 Online；如果 runner 窗口出现错误，把错误文字发来。

任务成功后，请发：

1. self-hosted Actions 运行链接和截图；
2. runner 终端接收并完成任务的截图。

不要截图或发送注册 token。完成取证后再运行 `Ctrl+C` 停止 runner。

> 已成功，[https://github.com/atribert/isse-lab5-chat-ci/actions/runs/39364245822](https://github.com/atribert/isse-lab5-chat-ci/actions/runs/39364245822)，
>
> User context
>
> Images:
> - `~/AppData/Local/Temp/codex-clipboard-8b17cfda-a878-4a0b-8ca9-4eb6d468b30a.png`
> - `~/AppData/Local/Temp/codex-clipboard-13877d91-5a3e-4ebf-bb4d-71937412d3a8.png`

<details><summary>4 previous messages</summary>

> 本机 runner 已成功完成任务，终端显示 `Job test completed with result: Succeeded`，Actions 运行也为绿色。截图中的 `Administrator privilege required` 是 `setup-python` 在 Windows 自托管环境尝试管理工具缓存时的提示；最终 job 仍成功，并完成了测试和冒烟检查。两张截图分别保存为本机 Actions 和本机终端证据。接下来停止 runner，再整理课程提交目录。
>
> <details><summary>Ran a command</summary>
>
> - Ran `Copy-Item -LiteralPath 'C:\Users\16256\AppData\Local\Temp\codex-clipboard-8b17cfda-a878-4a0b-8ca9-4eb6d468b30a.png' -Destination 'C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-labs\lab5\2500013152-王子懿\screenshots\self-hosted-actions.png' -Force
> Copy-Item -LiteralPath 'C:\Users\16256\AppData\Local\Temp\codex-clipboard-13877d91-5a3e-4ebf-bb4d-71937412d3a8.png' -Destination 'C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-labs\lab5\2500013152-王子懿\screenshots\self-hosted-terminal.png' -Force
> Get-ChildItem -LiteralPath 'C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-labs\lab5\2500013152-王子懿\screenshots' | Select-Object Name,Length`
>
> </details>
>
> 本机成功证据已保存：
>
> - `self-hosted-actions.png`
> - `self-hosted-terminal.png`
>
> 现在请在 runner 终端按 **Ctrl+C**，看到进程退出后告诉我。停止 runner 是收尾要求；它不会删除注册配置，之后需要时可以再次运行 `.\run.cmd`。同时我会整理最终应用副本和课程目录结构。
>
> <details><summary>Ran 2 commands</summary>
>
> - Ran `$src='C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-lab5-chat-ci'; $dst='C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-labs\lab5\2500013152-王子懿\app'; New-Item -ItemType Directory -Path $dst -Force | Out-Null; foreach ($file in @('app.py','requirements.txt','requirements-dev.txt','.env.example','.gitignore','README.md')) { Copy-Item -LiteralPath (Join-Path $src $file) -Destination (Join-Path $dst $file) -Force }; foreach ($dir in @('frontend','tests','scripts','.github','data')) { Copy-Item -LiteralPath (Join-Path $src $dir) -Destination (Join-Path $dst $dir) -Recurse -Force }; Get-ChildItem -LiteralPath $dst -Force -Recurse | Where-Object { $_.FullName -notmatch '\\(__pycache__|\.pytest_cache|htmlcov)($|\\)' } | Select-Object FullName,Length,Mode`
> - Ran `python -c "from pathlib import Path; p=Path(r'C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-labs\lab5\2500013152-王子懿\screenshots'); (p/'cloud-passed.png').unlink(missing_ok=True); (p/'cloud-passed-2.png').replace(p/'cloud-passed.png')"; Get-ChildItem -LiteralPath 'C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-labs\lab5\2500013152-王子懿\screenshots' | Select-Object Name,Length`
>
> </details>
</details>

本机 runner 任务已成功完成：

[Actions run 39364245822](https://github.com/atribert/isse-lab5-chat-ci/actions/runs/39364245822)

两项证据已保存：

- [self-hosted-actions.png](./lab5/2500013152-王子懿/screenshots/self-hosted-actions.png)
- [self-hosted-terminal.png](./lab5/2500013152-王子懿/screenshots/self-hosted-terminal.png)

终端显示：

```text
Job test completed with result: Succeeded
```

Actions 截图中出现的 `Administrator privilege required` 是 Windows `setup-python` 的工具缓存提示；最终 job 仍成功，说明测试、覆盖率和冒烟检查均已完成。

我已将最终 self-hosted 版本复制到：

```text
C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-labs\lab5\2500013152-王子懿\app
```

包含：

- `app.py`
- `frontend/`
- `requirements.txt`
- `requirements-dev.txt`
- `.env.example`
- `.gitignore`
- `tests/`
- `scripts/smoke_test.py`
- `.github/workflows/ci.yml`
- `data/messages.json`

截图目录目前包含：

- [failed.png](./lab5/2500013152-王子懿/screenshots/failed.png)
- [cloud-passed.png](./lab5/2500013152-王子懿/screenshots/cloud-passed.png)
- [self-hosted-actions.png](./lab5/2500013152-王子懿/screenshots/self-hosted-actions.png)
- [self-hosted-terminal.png](./lab5/2500013152-王子懿/screenshots/self-hosted-terminal.png)

请现在在 runner 终端按：

```text
Ctrl+C
```

确认看到 runner 停止后，执行课程仓库检查：

```powershell
Set-Location 'C:\Users\16256\Documents\pdf\大二上\智能化软件系统与工程\isse-labs'

git status --short
Get-ChildItem -LiteralPath 'lab5/2500013152-王子懿' -Force -Recurse |
  Select-Object FullName,Length
```

最后还需要你从当前 Codex 对话导出真实 Markdown 轨迹，保存为：

```text
lab5/2500013152-王子懿/AGENT_TRACE.md
```

导出时删去或省略 API Key、runner 注册 token 等凭据。保存后把结果发给我，我会检查材料完整性并给出最终提交和 PR 命令。
