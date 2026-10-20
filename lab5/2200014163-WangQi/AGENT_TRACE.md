# 按交互流程完成 Lab5

> 请完整阅读 lab5/AGENTS.md 和 lab5/README.md，按交互式流程带我完成 Lab5。

<details><summary>6 previous messages</summary>

> 我先完整阅读这两个文件，然后带你按流程走。
>
> <details><summary>Explored 2 files</summary>
>
> - Read `./lab5/AGENTS.md`
> - Read `./lab5/README.md`
>
> </details>
>
> 我先了解一下当前工作区的状态：课程仓库的位置、分支、以及 Lab2 应用在哪。
>
> <details><summary>Ran 4 commands</summary>
>
> - Ran `Get-ChildItem -Force | Select-Object Mode,Length,Name | Format-Table -AutoSize`
> - Ran `git remote -v; git branch -a; git status -sb`
> - Ran `Get-ChildItem -Recurse -Depth 3 -Force 'lab5' | Select-Object FullName | Format-Table -AutoSize`
> - Ran `Get-ChildItem -Recurse -Depth 4 -Force 'lab2' | Select-Object FullName | Format-Table -AutoSize`
>
> </details>
>
> 现在读取你自己的 Lab2 应用代码和课程提供的冒烟骨架，以便后续讲解时能结合真实代码。
>
> <details><summary>Explored 3 files, ran 3 commands</summary>
>
> <details><summary>Explored a file</summary>
>
> - Read `./lab2/王琪-2200014163/app.py`
>
> </details>
>
> - Ran `Get-Content -Raw -LiteralPath 'lab2/王琪-2200014163/requirements.txt'; Write-Output '---ENVEXAMPLE---'; Get-Content -Raw -LiteralPath 'lab2/王琪-2200014163/.env.example'; Write-Output '---GITIGNORE---'; Get-Content -Raw -LiteralPath 'lab2/王琪-2200014163/.gitignore'`
>
> <details><summary>Explored a file</summary>
>
> - Read `./lab5/templates/smoke_test.py`
>
> </details>
>
> - Ran `Get-Content -Raw -LiteralPath 'lab2/王琪-2200014163/frontend/app.js'; Write-Output '---INDEX---'; Get-Content -Raw -LiteralPath 'lab2/王琪-2200014163/frontend/index.html'`
>
> <details><summary>Explored a file</summary>
>
> - Read `./.gitignore`
>
> </details>
>
> - Ran `git log --oneline -3; Write-Output '---'; git rev-parse HEAD; git rev-parse origin/main`
>
> </details>
</details>

我已完整读完了 `lab5/AGENTS.md` 和 `lab5/README.md`，也把你 Lab2 的应用代码看了一遍。下面先把这轮实验的目标、两个仓库的分工以及我们第一步要做的事讲清楚。

## 这次 Lab5 要做什么

延续你自己的 Lab2 聊天应用，完成一次完整的持续集成（CI）实践，一共五个阶段：

1. 准备：把 Lab2 应用放进一个全新的个人仓库。
2. 测试与 CI：为「一条聊天记录的创建、查询、修改、删除」和「一类非法输入」写自动测试，模型调用用 mock 代替，并让后端行覆盖率达到 70%，推送后由 GitHub Actions 自动运行。
3. 失败与修复：故意改坏一处功能，让测试在云端失败，学会从 Actions 日志定位问题，再修复并通过。
4. 冒烟检查：适配课程提供的脚本骨架，确认应用能作为 HTTP 服务启动、首页和连通性接口正常。
5. 本机 runner：把同一份工作流从云端切到你自己电脑上的 runner 执行，并留存截图。

最终把应用代码、四张截图和本次真实对话轨迹整理回课程仓库的个人目录，发起 PR。

## 两个仓库分别干什么

这里有两个仓库，职责不同，别混在一起：

- 课程仓库（现在这个工作区）：`D:\Files\Desktop\isse-labs`，远端是你的 Fork `https://github.com/QiWang3569/isse-labs`。它只用来最后交作业——在 `lab5/学号-姓名/` 目录里放代码、截图和对话轨迹，然后向课程主分支发 PR。原 Lab2 作业保持不动。
- 个人实验仓库（待新建）：例如 `isse-lab5-chat-ci`。它放 Lab2 应用、测试、CI 工作流，并承载云端 Actions 和本机 runner。它要克隆到课程仓库之外，平时跑实验都在这里。

人机分工是：我负责讲解原理、读代码、写测试和配置文件、帮你排错；你负责实际运行命令、提交推送、看日志、操作 GitHub 和本机 runner。

## 你当前的状况（我已核对）

- 课程仓库 `main` 与远端 `origin/main` 一致，最新提交是 `88c718d`，可以安全切分支。
- 你的身份：王琪，学号 `2200014163`。
- 你的 Lab2 应用是 Flask + 多会话 + JSON 持久化：入口 `app.py`，模型调用在 `call_deepseek()`，数据存在 `data/conversations.json`，已有 `/api/hello` 连通性接口。这些后面写测试都会用到。

按课程命名惯例（参考已有示例 `2500017738-ZhengZixuan`），我建议你的目录和分支都用 `2200014163-WangQi`。

## 准备阶段：先搭好实验位置

持续集成解决的是「每次改动后都要重新确认老功能没坏」这件事——把这些检查写成程序，让代码一提交就自动跑。所以第一步不是写代码，而是把两个工作位置准备好：课程仓库里开好自己的 Lab5 目录，另建一个独立仓库专门跑 CI。

请你依次完成下面三组操作。

第一组，在课程仓库创建分支和个人目录。在当前目录 `D:\Files\Desktop\isse-labs` 打开终端执行：

```powershell
git fetch origin
git checkout main
git pull origin main
git checkout -b lab5/2200014163-WangQi
New-Item -ItemType Directory -Path "lab5/2200014163-WangQi" -Force
```

第二组，在 GitHub 新建个人仓库：仓库名 `isse-lab5-chat-ci`，默认分支 `main`，可以先不勾选 README/.gitignore/license（保持空仓库方便后面推送）。公开或私有都可以，建议私有更稳妥。

第三组，把它克隆到课程仓库之外，例如：

```powershell
git clone https://github.com/QiWang3569/isse-lab5-chat-ci.git D:\Files\Desktop\isse-lab5-chat-ci
```

注意：我的写权限目前只覆盖课程仓库目录。如果实验仓库克隆到了别的位置，请在 Codex 里把 `D:\Files\Desktop\isse-lab5-chat-ci`（或你实际选的路径）添加为工作目录，这样我才能在里面写代码和测试；如果暂时加不了也没关系，我们到时再处理。

## 完成后反馈给我

请告诉我两样东西：个人仓库的完整地址（URL），以及它在本地的绝对路径。确认课程分支 `lab5/2200014163-WangQi` 已切好、`lab5/2200014163-WangQi` 目录已创建后，我们进入下一步：把你的 Lab2 应用复制进实验仓库。

> [https://github.com/QiWang3569/isse-lab5-chat-ci](https://github.com/QiWang3569/isse-lab5-chat-ci) "D:\Files\Desktop\isse-lab5-chat-ci"

<details><summary>2 previous messages</summary>

> 收到。我先核对两个仓库的实际状态，确认分支和目录都已就位，并检查我对实验仓库目录有没有写权限。
>
> <details><summary>Ran 3 commands</summary>
>
> - Ran `git branch --show-current; Get-ChildItem -Force 'lab5/2200014163-WangQi' -ErrorAction SilentlyContinue | Select-Object Name; Test-Path 'lab5/2200014163-WangQi'`
> - Ran `git remote -v; git branch --show-current; git status -sb; Get-ChildItem -Force | Select-Object Mode,Name`
> - Ran `New-Item -ItemType File -Path '.write-probe' -Force -ErrorAction Stop | Out-Null; Remove-Item -LiteralPath '.write-probe' -Force; Write-Output 'WRITE_OK'`
>
> </details>
</details>

两边都核对过了，状态如下。

课程仓库已经就位：当前分支是 `lab5/2200014163-WangQi`，`lab5/2200014163-WangQi/` 目录也已经建好。

实验仓库也正常：远端指向 `https://github.com/QiWang3569/isse-lab5-chat-ci.git`，当前在 `main` 分支，还是空仓库、没有提交，正好用来放首次提交。

不过有个小障碍需要你处理一下：我探测发现，我没有对 `D:\Files\Desktop\isse-lab5-chat-ci` 这个目录的写权限（系统返回 Access denied）。我现在的写权限只覆盖课程仓库目录，所以后面往实验仓库写代码、测试和 CI 文件之前，需要先让 Codex 认识这个新目录。

请在 Codex 里把 `D:\Files\Desktop\isse-lab5-chat-ci` 添加为工作目录（通过界面里的“添加文件夹 / 工作目录”入口，选中这个克隆出来的文件夹即可）。加好之后回复我一声，我会重新探测写权限；通过后就立刻开始把你的 Lab2 应用复制进实验仓库，并讲解这次复制的文件与原因。

> 添加了

<details><summary>5 previous messages</summary>

> <details><summary>Created a file, ran a command</summary>
>
> - Ran `New-Item -ItemType File -Path '.write-probe' -Force -ErrorAction Stop | Out-Null; Remove-Item -LiteralPath '.write-probe' -Force; Write-Output 'WRITE_OK'`
> - Wrote `D:/Files/Desktop/isse-lab5-chat-ci/.write-probe` (+1 -0)
>
> </details>
>
> apply_patch 已经能写进实验仓库了，说明工作目录加好了。我清理一下探测文件，再确认一下终端命令的写权限，然后开始复制应用。
>
> <details><summary>Deleted a file, ran 2 commands</summary>
>
> - Deleted `D:/Files/Desktop/isse-lab5-chat-ci/.write-probe` (+0 -1)
> - Ran `Get-Content -Raw -LiteralPath 'lab2/王琪-2200014163/data/conversations.json'; Write-Output '---STYLE---'; Get-Content -Raw -LiteralPath 'lab2/王琪-2200014163/frontend/style.css'`
> - Ran `New-Item -ItemType File -Path '.write-probe' -Force -ErrorAction Stop | Out-Null; Remove-Item -LiteralPath '.write-probe' -Force; Write-Output 'WRITE_OK'`
>
> </details>
>
> 终端命令对实验仓库还是没有写权限（`apply_patch` 可以，但批量复制文件用它容易出错）。我需要申请一次提权，用系统复制命令把你的 Lab2 应用原样搬过去，这样最不容易出现抄写错误。复制时我会避开 `.env`（真实 Key）和你的个人聊天记录。
>
> <details><summary>Created a file, ran 3 commands</summary>
>
> - Ran `$src = 'D:\Files\Desktop\isse-labs\lab2\王琪-2200014163'
> $dst = 'D:\Files\Desktop\isse-lab5-chat-ci'
> New-Item -ItemType Directory -Force -Path "$dst\frontend" | Out-Null
> Copy-Item -LiteralPath "$src\app.py" -Destination "$dst\app.py" -Force
> Copy-Item -LiteralPath "$src\requirements.txt" -Destination "$dst\requirements.txt" -Force
> Copy-Item -LiteralPath "$src\.env.example" -Destination "$dst\.env.example" -Force
> Copy-Item -LiteralPath "$src\frontend\index.html" -Destination "$dst\frontend\index.html" -Force
> Copy-Item -LiteralPath "$src\frontend\app.js" -Destination "$dst\frontend\app.js" -Force
> Copy-Item -LiteralPath "$src\frontend\style.css" -Destination "$dst\frontend\style.css" -Force
> Get-ChildItem -Recurse -File -LiteralPath $dst | Select-Object FullName, Length`
> - Ran `$src = 'D:\Files\Desktop\isse-labs\lab2\王琪-2200014163'
> $dst = 'D:\Files\Desktop\isse-lab5-chat-ci'
> $files = 'app.py','requirements.txt','.env.example','frontend\index.html','frontend\app.js','frontend\style.css'
> foreach ($f in $files) {
>   $a = (Get-FileHash -LiteralPath (Join-Path $src $f) -Algorithm SHA256).Hash
>   $b = (Get-FileHash -LiteralPath (Join-Path $dst $f) -Algorithm SHA256).Hash
>   $match = if ($a -eq $b) { 'OK' } else { 'MISMATCH' }
>   Write-Output ("{0}  {1}" -f $match, $f)
> }`
> - Wrote `D:/Files/Desktop/isse-lab5-chat-ci/data/conversations.json` (+1 -0)
> - Ran `New-Item -ItemType Directory -Force -Path 'D:\Files\Desktop\isse-lab5-chat-ci\data' | Out-Null; Write-Output 'DIR_OK'`
> - Wrote `D:/Files/Desktop/isse-lab5-chat-ci/data/conversations.json` (+1 -0)
>
> </details>
</details>

应用代码已经复制进实验仓库了，并且逐一校验过哈希，确认和你 Lab2 的原始文件完全一致。我特意排除了 `.env`（里面有你的真实 Key）和 `data/conversations.json` 里的个人聊天记录，另放了一份空的 `[]` 作为演示数据。

## 这一步在做什么

新建的实验仓库要先有 Lab2 应用，后面的测试和 CI 才有对象可查。这里直接沿用你已经做好的应用，把后端、前端、依赖和配置示例带过去，原 Lab2 作业保持不动。

要区分两件事：应用代码和运行环境。代码、依赖清单（`requirements.txt`）和配置示例（`.env.example`）进仓库；虚拟环境不提交，而是每台机器按依赖清单现装。`.env.example` 告诉使用者需要哪些配置项，`.gitignore` 则让真正的 `.env`、虚拟环境和缓存留在本地。这样云端拿到代码后，也能照着依赖清单准备环境。

`commit` 是在本地记录一个版本，`push` 才把这些提交上传到 GitHub。现在实验仓库还是空仓库，所以这次是它的首次提交。

## 我已经放进实验仓库的文件

`app.py`（后端入口，聊天接口、`call_deepseek()` 模型调用、JSON 持久化都在这里）、`frontend/`（三个前端文件）、`requirements.txt`、`.env.example`，以及一份空的 `data/conversations.json`。

## 现在轮到你做三件事

第一，编辑实验仓库根目录的 `.gitignore`。仓库里现在还没有这个文件，请新建并写入：

```gitignore
.env
__pycache__/
*.py[cod]
.venv/
venv/
.pytest_cache/
.coverage
htmlcov/
```

这几行分别忽略真实环境变量、Python 字节码缓存、虚拟环境目录，以及后面会出现的 pytest 和覆盖率缓存。

第二，在本机终端安装依赖（我给你的命令直接用虚拟环境里的 python，避免 PowerShell 执行策略问题）：

```powershell
cd D:\Files\Desktop\isse-lab5-chat-ci
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

第三，提交并推送首次版本：

```powershell
git add .
git status
git commit -m "导入 Lab2 聊天应用"
git push -u origin main
```

## 观察重点

- `git status` 里不应出现 `.env`、`.venv/`、`__pycache__/`，说明忽略规则生效了。
- `pip install` 应显示成功安装 Flask、python-dotenv、requests。
- 推送后打开仓库页面，应能看到 `app.py`、`frontend/`、`requirements.txt`、`.env.example`、`data/` 和 `.gitignore`；`data/conversations.json` 应为空 `[]`，页面上也绝不应出现 `.env`。

完成后把 `git status` 的输出和推送结果告诉我（或截图仓库页面），确认无误我们就进入任务 1：写两个重点测试。

> 现在网络不行，推送不上去

<details><summary>10 previous messages</summary>

> 网络问题很常见，别急。推送失败不代表进度丢失——只要本地 `git commit` 成功了，版本就在你电脑里。我先帮你看几个常见原因：代理设置和到 GitHub 的连通性。
>
> <details><summary>Ran 2 commands</summary>
>
> - Ran `git config --global --get http.proxy; git config --global --get https.proxy; git config --global --get url."https://github.com/".insteadOf; Write-Output '---ENV---'; Write-Output "HTTP_PROXY=$env:HTTP_PROXY"; Write-Output "HTTPS_PROXY=$env:HTTPS_PROXY"`
> - Ran `Test-NetConnection github.com -Port 443 -InformationLevel Quiet`
>
> </details>
>
> 可以先进行下一步吗
>
> <details><summary>Ran a command</summary>
>
> - Ran `git status -sb; Write-Output '---LOG---'; git log --oneline -5 2>$null; Write-Output '---REMOTE---'; git remote -v`
>
> </details>
>
> 可以，网络问题不阻塞本地工作。本地的首次提交已经存在（`5df1020 导入 Lab2 聊天应用`），推送等网络恢复后再补。我们先推进任务 1：写测试、装 dev 依赖、跑 pytest。这一步除了 `pip install` 需要网络，其余都能本地做——我先看看你机器上 Python 和 pytest 的现状，好决定怎么装。
>
> <details><summary>Ran 2 commands</summary>
>
> - Ran `python --version; python -m pytest --version 2>&1; python -m pip --version 2>&1`
> - Ran `python -m pip list 2>&1 | Select-String -Pattern 'Flask|pytest|cov|requests|dotenv'`
>
> </details>
>
> 环境我摸清了：这台机器有 Python 3.9 + 已装好的 Flask / python-dotenv / requests，但还没有 pytest 和 pytest-cov（装这两个才需要网络，后面我用国内镜像帮你绕过）。我先做我的部分：给 `app.py` 加一个数据目录配置开关（测试和冒烟检查要用），再写两个重点测试和 `requirements-dev.txt`。
>
> 先做 `app.py` 的小重构，并在实验仓库建 `tests/` 目录。
>
> <details><summary>Created 2 files, edited a file, ran a command</summary>
>
> - Wrote `D:/Files/Desktop/isse-lab5-chat-ci/app.py` (+3 -1)
> - Ran `New-Item -ItemType Directory -Force -Path 'D:\Files\Desktop\isse-lab5-chat-ci\tests' | Out-Null; Write-Output 'DIR_OK'`
> - Wrote `D:/Files/Desktop/isse-lab5-chat-ci/requirements-dev.txt` (+2 -0)
> - Wrote `D:/Files/Desktop/isse-lab5-chat-ci/tests/test_chat_api.py` (+85 -0)
>
> </details>
>
> 写完了。我快速做个语法自检，确认 `app.py` 重构和测试文件没有语法问题。
>
> <details><summary>Ran 3 commands</summary>
>
> - Ran `python -c "import ast; ast.parse(open('app.py', encoding='utf-8').read()); ast.parse(open('tests/test_chat_api.py', encoding='utf-8').read()); print('SYNTAX_OK')"`
> - Ran `Get-Content -LiteralPath 'app.py' -TotalCount 22; Write-Output '---TESTS---'; Get-ChildItem -Recurse -File | Where-Object { $_.FullName -notmatch '\\.git\\' } | Select-Object FullName, Length`
> - Ran `Get-Content -LiteralPath '.gitignore'; Write-Output '---STATUS---'; git status -sb; Write-Output '---VENV PYTEST---'; .\.venv\Scripts\python.exe -m pytest --version 2>&1`
>
> </details>
</details>

进展顺利——顺便说下，我看到你已经把 `.gitignore` 建好了（内容完全正确），也建了 `.venv` 并装好了 Flask 等运行依赖，首次提交 `5df1020` 也已在本地。只是 venv 里还没有 pytest，下面装一下就行。

## 任务 1.1 在做什么

Lab2 里你是靠点网页、发 curl 来验证功能的。自动测试就是把「请求、预期结果、判断条件」写成程序，以后一条命令就能重复检查。测试里的 `assert` 是一个「应当成立」的条件，比如「创建记录后，返回内容应包含刚发出去的消息」。

我们只做两个重点测试：

1. 一条聊天记录的完整 CRUD：创建、查询、修改、删除，每一步都核对实际内容。
2. 一类非法输入：空消息、缺少 `message` 字段都要被拒绝，并且确认没有新增记录。

聊天接口会调外部模型，但每次测试都真去请求模型，会受到网络、费用和回复随机性的影响。所以这里用 mock：把模型调用临时换成固定回复，检查的是应用如何处理这条回复。fixture 则负责每个测试开始前准备独立数据，让每次测试都从干净状态出发。

Flask 的 `test_client()` 可以在测试进程里直接向应用发请求，所以这一步不用先启动监听端口的服务，也不需要真实 DeepSeek Key。

## 我结合你的代码做了什么

你的应用是「多会话 + 消息」结构，所以测试会先建一个会话，再对会话里的消息做增删改查。具体接口是：`POST /api/conversations` 建会话，`POST .../messages` 发消息（内部调用 `call_deepseek()`），`GET .../<cid>` 查询，`PATCH .../messages/<mid>` 修改，`DELETE .../messages/<mid>` 删除。

为了测试和后面的冒烟检查能用独立数据，我在 `app.py` 做了一处小重构：数据目录改为先读 `LAB5_DATA_DIR` 环境变量，没设置时仍用原来的 `data/`。这样测试可以用临时目录，不碰你真实数据。

我新写了两个文件：

- `tests/test_chat_api.py`：两个重点测试。fixture 里先设 `LAB5_DATA_DIR` 为临时目录、设一个测试占位 Key，重载应用让数据从空状态加载，再把 `app.call_deepseek` mock 成返回 `"模拟回复"`。
- `requirements-dev.txt`：`pytest` 和 `pytest-cov`。

以 CRUD 测试为例，一条关键断言是：发消息 `{"message":"你好"}` 后，GET 会话应同时看到角色为 `user`、内容为 `你好` 的消息，以及角色为 `assistant`、内容为 `模拟回复` 的回复；删除用户消息后，GET 会话的消息列表应为空。

## 现在轮到你运行

在仓库根目录 `D:\Files\Desktop\isse-lab5-chat-ci` 打开终端，先装 dev 依赖：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

如果这条因为网络失败（很可能，因为 GitHub 现在不通，PyPI 也许也不稳），改用清华镜像：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

装好后运行测试：

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## 观察重点

- 应看到 `2 passed`，说明两个重点测试都通过。
- 如果失败，留意是哪条断言没满足，把完整输出发我。
- 想确认 mock 真的没访问外部模型，可以注意：测试全程没有真实请求 DeepSeek，也不需要真实 Key。

把 `pip install` 和 `pytest` 的实际输出发给我，我们再一起看结果，然后进入覆盖率检查。

> PS D:\Files\Desktop\isse-lab5-chat-ci> .\.venv\Scripts\python.exe -m pytest -q
> ..                                             [100%]
> 2 passed in 0.91s 应该没问题，刚才我也都推送上去了

<details><summary>2 previous messages</summary>

> 测试通过，很好。我先确认一下你刚才推送的状态（本地提交和远端是否同步），然后进入覆盖率检查。
>
> <details><summary>Ran a command</summary>
>
> - Ran `git status -sb; Write-Output '---LOG---'; git log --oneline -5`
>
> </details>
</details>

先澄清一下推送状态：你推到 GitHub 上的是最早的「导入 Lab2 聊天应用」提交（`5df1020`），它已经成功上去了。而刚才我改的 `app.py`、新加的 `tests/` 和 `requirements-dev.txt` 目前还只是本地改动（还没提交）。这不影响进度，按流程我们等加好 CI 工作流后，把这些和 `ci.yml` 一起提交推送。测试 `2 passed` 没问题，进入下一步。

## 任务 1.2：看覆盖率

测试通过只说明这些测试里的判断条件都满足了。接下来要看它们到底执行到了多少后端代码。行覆盖率统计的是「测试运行时执行过的可执行语句」占「被测可执行语句」的比例，能帮我们找到还没走到的代码路径。

覆盖率报告里，`Cover` 是覆盖百分比，`Missing` 列出没执行到的行号。比如你的测试只发了合法消息，那么处理非法消息的代码就可能没执行；`/api/hello`、重命名会话、删除会话这些没测到的接口也会出现在 `Missing` 里。覆盖率高不代表结果一定正确——结果是否符合预期靠的还是 `assert`。

这次命令加三个参数：

- `--cov=app`：指定被测模块是你的后端 `app.py`。
- `--cov-report=term-missing`：在终端显示未覆盖的行号。
- `--cov-fail-under=70`：把 70% 设为通过门槛。

所以可能出现「断言全部通过，但因为覆盖率低于 70%，整个命令退出码非零、显示 FAIL」的情况，这是正常的。

在仓库根目录运行：

```powershell
.\.venv\Scripts\python.exe -m pytest -q --cov=app --cov-report=term-missing --cov-fail-under=70
```

## 观察重点

把输出里的这几样发给我：末尾的 `Name / Stmts / Miss / Cover` 一行，以及 `Missing` 列出的行号；如果最后有 `FAIL Required test coverage of 70% not met`，也一并说明。

我会根据真实的 `Cover` 和 `Missing` 判断：达到 70% 就继续；不足的话，我会对着行号补充最少量的测试。我预计只靠这两个重点测试，覆盖率可能在 60% 出头，大概率需要补两三条（比如会话的列表、重命名、删除和 `/api/hello`），到时我们一起看实际数字再定。

> ERROR: Coverage failure: total of 69 is less than fail-under=70
>                                                [100%]
> ================== tests coverage ===================
> __ coverage: platform win32, python 3.9.1-final-0 ___
>
> Name     Stmts   Miss  Cover   Missing
> --------------------------------------
> app.py     171     53    69%   30-31, 33, 38-42, 59, 63-78, 83, 88, 107, 114, 120-131, 136-142, 151, 154, 171-174, 190, 194, 198, 207, 212-213, 218-219, 224-226, 240, 250, 254
> --------------------------------------
> TOTAL      171     53    69%
> FAIL Required test coverage of 70% not reached. Total coverage: 69.01%
> 2 passed in 1.06s

<details><summary>4 previous messages</summary>

> 69% 只差一口气，很好。我对着行号看下具体是哪些代码没走到，然后补最少量的测试。
>
> <details><summary>Ran a command</summary>
>
> - Ran `$i=0; Get-Content -LiteralPath 'app.py' | ForEach-Object { $i++; '{0,4}: {1}' -f $i, $_ }`
>
> </details>
>
> 69.01%，就差一点。我把 `Missing` 行号对到代码上看，未覆盖的主要是这几类：
>
> - `63-78` 是 `call_deepseek()` 函数体——它被 mock 替换了，测试里本就不会真正执行，这属于正常情况，不需要管。
> - `83` 首页 `/`、`88` 连通性 `/api/hello`、`107` 会话列表——这三个接口一个测试都没发过请求。
> - `120-131` 会话重命名、`136-140` 删除会话——没测到。
> - 其余大多是各种 404/400/502 错误分支和「消息不是 user 角色」这类边界情况。
>
> 按课程要求「按覆盖率补充必要测试即可」，我不做成大而全的测试集，只补一条会话管理的小测试，正好把上面这些接口覆盖掉，就能过 70% 门槛。
>
> <details><summary>Edited a file</summary>
>
> - Wrote `D:/Files/Desktop/isse-lab5-chat-ci/tests/test_chat_api.py` (+21 -0)
>
> </details>
</details>

我在 `tests/test_chat_api.py` 里补了一个 `test_conversation_management`，它做四件事：访问首页 `/`、连通性接口 `/api/hello`，创建会话后检查列表，重命名会话，最后删除会话并确认列表为空。这样就把 `83`、`88`、`107`、`120-131`、`136-140` 这些没覆盖的行补齐了。`call_deepseek` 的函数体和各错误分支这次依然不会执行——那是 mock 和聚焦测试的自然结果，不影响门槛。

请再跑一次同样的覆盖率命令：

```powershell
.\.venv\Scripts\python.exe -m pytest -q --cov=app --cov-report=term-missing --cov-fail-under=70
```

## 观察重点

- 应看到 `3 passed`。
- 末尾 `app.py` 的 `Cover` 应 ≥ 70%（我预计在 77% 左右），命令退出码为 0，不再出现 `FAIL Required test coverage...`。
- 把新的 `Name / Stmts / Miss / Cover` 一行和 `Missing` 发给我确认。

达标后我们就进入任务 1.3：写 `ci.yml` 工作流并推送，让 GitHub Actions 在云端自动跑这条测试与覆盖率命令。

> ...                                            [100%]
> ================== tests coverage ===================
> __ coverage: platform win32, python 3.9.1-final-0 ___
>
> Name     Stmts   Miss  Cover   Missing
> --------------------------------------
> app.py     171     37    78%   30-31, 33, 38-42, 59, 63-78, 114, 122, 127, 142, 151, 154, 171-174, 190, 194, 198, 207, 212-213, 218-219, 224-226, 240, 250, 254
> --------------------------------------
> TOTAL      171     37    78%
> Required test coverage of 70% reached. Total coverage: 78.36%
> 3 passed in 1.27s

<details><summary>2 previous messages</summary>

> 78.36%，达标了。现在进入任务 1.3：把这条测试命令写进 GitHub Actions 工作流，让每次推送都自动跑。
>
> 我先在实验仓库建好 `.github/workflows/` 目录。
>
> <details><summary>Created a file, ran 2 commands</summary>
>
> - Ran `New-Item -ItemType Directory -Force -Path 'D:\Files\Desktop\isse-lab5-chat-ci\.github\workflows' | Out-Null; Write-Output 'DIR_OK'`
> - Wrote `D:/Files/Desktop/isse-lab5-chat-ci/.github/workflows/ci.yml` (+23 -0)
> - Ran `Get-Content -Raw -LiteralPath '.github/workflows/ci.yml'; Write-Output '---STATUS---'; git status -sb`
>
> </details>
</details>

`ci.yml` 已经写好并放到 `.github/workflows/` 下，当前待提交的就是 `app.py` 重构、`tests/`、`requirements-dev.txt` 和 `.github/workflows/` 这四块。

## 任务 1.3 在做什么

现在测试在本地能跑，但每次改代码后还得你记得手动执行。GitHub Actions 就是把这条命令放进自动工作流：一旦推送代码或发起 PR，就自动跑一遍，让每个提交都有一份检查结果。

工作流是一个 YAML 文件，放在仓库根目录的 `.github/workflows/` 里。几个关键概念：

- `on` 是触发事件，这里配了「push 到 main」和「向 main 发 PR」两种。
- 工作流（workflow）下面是 job（一组工作），job 由 runner 上的进程执行；job 里的 step（步骤）按顺序完成「检出代码 → 准备 Python → 装依赖 → 跑测试」。
- `runs-on: ubuntu-latest` 选的是 GitHub 提供的云端 Linux 机器。
- `uses` 是调用现成 Action：`actions/checkout@v4` 把当前提交的代码取下来，`actions/setup-python@v5` 装 Python。
- `run` 是直接执行命令。

关键点是：云端机器不会自带你本地虚拟环境里的依赖，所以工作流要按 `requirements.txt` 和 `requirements-dev.txt` 重新装。我们这份 `ci.yml` 用的 Python 是 `3.11`（与你的 Flask 3.1 兼容），最后一步就是你在本地验证过的同一条测试与覆盖率命令。

## 现在轮到你提交并推送

在仓库根目录执行：

```powershell
git add .
git status
git commit -m "添加自动化测试与 CI 工作流"
git push
```

推送后打开仓库页面的 `Actions` 标签，找到这次新提交触发的运行，点进去，再点开名为 `test` 的 job，展开 `Run tests with coverage` 步骤。

## 观察重点

- 日志里应出现 `3 passed`，以及 `Cover ... 78%`、`Required test coverage of 70% reached`。
- 确认这次运行对应的是你刚推送的新提交（把本地 `git log --oneline` 的最新 SHA 和 Actions 页面显示的 commit 对一下）。
- 如果某一步失败（例如安装依赖或测试失败），把失败步骤的日志完整发我。

把 Actions 运行结果（可以截图，也可以贴关键日志）和运行链接发给我，确认云端 CI 通过后，我们就做任务 2：故意改坏一处功能，观察失败再修复。

> PS D:\Files\Desktop\isse-lab5-chat-ci> git push
> Enumerating objects: 11, done.
> Counting objects: 100% (11/11), done.
> Delta compression using up to 8 threads
> Compressing objects: 100% (5/5), done.
> Writing objects: 100% (9/9), 2.17 KiB | 554.00 KiB/s, done.
> Total 9 (delta 2), reused 0 (delta 0), pack-reused 0 (from 0)
> remote: Resolving deltas: 100% (2/2), completed with 2 local objects.
> To https://github.com/QiWang3569/isse-lab5-chat-ci.git
>    5df1020..62e570b  main -> main

<details><summary>1 previous message</summary>

> <details><summary>Ran a command</summary>
>
> - Ran `git log --oneline -3; Write-Output '---'; git status -sb`
>
> </details>
</details>

推送成功，`62e570b` 已经上到 GitHub，本地工作区也干净了。现在 GitHub 会立刻为这个提交排队跑一次 CI。

请打开 https://github.com/QiWang3569/isse-lab5-chat-ci/actions ，点最新那一次运行（对应提交 `62e570b 添加自动化测试与 CI 工作流`），进入后：

1. 点开左侧 job 名 `test`。
2. 依次展开 `Set up job`、`Checkout`、`Set up Python`、`Install dependencies`、`Run tests with coverage`。
3. 重点看 `Run tests with coverage`：应看到 `3 passed` 和 `Cover ... 78%`、`Required test coverage of 70% reached`。
4. 整次运行结束是绿色对勾（成功）。

第一次云端运行可能要等一两分钟（安装依赖比较耗时）。把结果告诉我：成功的就把 Actions 运行链接和 `Run tests with coverage` 步骤截图发我；失败的就把失败步骤的完整日志发我，我来帮你定位。确认云端通过后，我们进入任务 2，故意改坏一处功能看 CI 怎么抓住它。

> [https://github.com/QiWang3569/isse-lab5-chat-ci/actions/runs/39381963525/job/118493468267](https://github.com/QiWang3569/isse-lab5-chat-ci/actions/runs/39381963525/job/118493468267) 图片在"D:\Files\Desktop\isse-lab5-chat-ci\575b3130-6f94-446a-bcaf-4bd2d1ef54c3.png"

<details><summary>2 previous messages</summary>

> 收到，我看一下你的截图确认云端结果。
>
> <details><summary>Ran 2 commands</summary>
>
> - Ran `Get-Item -LiteralPath '575b3130-6f94-446a-bcaf-4bd2d1ef54c3.png' | Select-Object Name, Length, LastWriteTime`
> - Ran `gh --version 2>&1; Write-Output '---AUTH---'; gh auth status 2>&1`
>
> </details>
</details>

截图我收到了（`575b3130-...png`，约 97KB 的 PNG）。说明一下：当前这个会话里我没法直接查看图片内容，所以请你用一句话帮我确认这次运行的结果，我据此继续：

- 整次运行是否绿色成功？
- 展开 `Run tests with coverage`，是否看到 `3 passed`，以及 `Cover 78%`、`Required test coverage of 70% reached`？

你只要回我「成功，3 passed，78%」即可。确认后我立刻带你做任务 2：我会先挑一处已经被测试覆盖到的功能，把改动点和对应断言讲给你看，你确认后我们再提交推送，让 CI 在云端失败一次，然后从日志定位原因、修复、重新通过。

> Run python -m pytest -q --cov=app --cov-report=term-missing --cov-fail-under=70
> ...                                                                      [100%]
> ================================ tests coverage ================================
> _______________ coverage: platform linux, python 3.11.17-final-0 _______________
>
> Name     Stmts   Miss  Cover   Missing
> --------------------------------------
> app.py     171     37    78%   30-31, 33, 38-42, 59, 63-78, 114, 122, 127, 142, 151, 154, 171-174, 190, 194, 198, 207, 212-213, 218-219, 224-226, 240, 250, 254
> --------------------------------------
> TOTAL      171     37    78%
> Required test coverage of 70% reached. Total coverage: 78.36%
> 3 passed in 0.48s

云端 CI 通过确认了：Linux 环境、Python 3.11，`3 passed`，`78.36%`，达到 70% 门槛。任务 1 完成。

## 任务 2：观察失败并修复

持续集成的价值之一，就是在改动破坏已有功能时及时提醒我们。这一步做一次「回归实验」：在已经通过检查的代码里，故意改坏一处被测试覆盖的行为，看原来的测试能不能抓住它。

我选的是消息删除接口。现在的 `delete_message` 会真正把消息从 `conv["messages"]` 里移除；我们要把它改成「仍然返回成功，但实际上不再删任何东西」——这正是「返回状态正常、数据却没变」的典型 bug。

准备这样改（`app.py` 的 `delete_message`，删掉两行 `pop`）：

```python
# 改之前
    for index, msg in enumerate(conv["messages"]):
        if msg["id"] == message_id:
            removed = conv["messages"].pop(index)
            if removed["role"] == "user" and index < len(conv["messages"]) and conv["messages"][index]["role"] == "assistant":
                conv["messages"].pop(index)
            save_conversations()
            return jsonify({"deleted": message_id})

# 改之后
    for index, msg in enumerate(conv["messages"]):
        if msg["id"] == message_id:
            save_conversations()
            return jsonify({"deleted": message_id})
```

对应抓它的是 CRUD 测试里的最后一段：删除后重新查询会话，断言消息列表为空。改坏之后，这条断言会失败——

```python
resp = client.delete(f"/api/conversations/{conv_id}/messages/{user_msg['id']}")
assert resp.status_code == 200            # 仍然通过
messages = client.get(f"/api/conversations/{conv_id}").get_json()["messages"]
assert messages == []                     # 这里会失败：实际还有 user 和 assistant 两条
```

失败时你会看到：预期 `[]`，实际是删之前的用户消息和助手回复。测试本身不改，保持原来的预期。

确认的话我就把 `delete_message` 改成上面「改之后」的版本，然后你提交推送、去 Actions 看失败日志。确认吗？

> 可以

<details><summary>3 previous messages</summary>

> <details><summary>Edited a file</summary>
>
> - Wrote `D:/Files/Desktop/isse-lab5-chat-ci/app.py` (+0 -3)
>
> </details>
>
> 改动已应用。我先在本地确认一下这条测试确实会失败，这样能提前告诉你失败长什么样。
>
> <details><summary>Ran 2 commands</summary>
>
> - Ran `.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider 2>&1`
> - Ran `$i=0; Get-Content -LiteralPath 'app.py' | ForEach-Object { $i++; if ($i -ge 236 -and $i -le 250) { '{0,4}: {1}' -f $i, $_ } }`
>
> </details>
</details>

改好了，`delete_message` 现在是「找到消息就返回成功，但不再执行删除」。注意：我这边环境没法直接替你跑 pytest（临时目录写入受限），所以由你在自己的终端验证。

先在你终端快速确认失败（可选，但推荐）：

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

预期看到 `1 failed`，失败的是 `test_message_crud_flow`，断言行是删除后的 `assert messages == []`：预期 `[]`，实际是两条消息（user 的「修改后的内容」和 assistant 的「模拟回复」）。

然后提交并推送这次「坏」改动：

```powershell
git add app.py
git commit -m "故意改坏消息删除功能"
git push
```

推送后打开 Actions 里这次新运行，进入失败 job，展开 `Run tests with coverage`。

## 你要找的四个东西

- 失败测试名：`test_message_crud_flow`
- 断言行：删除后重新查询的 `assert messages == []`
- 预期：`[]`
- 实际：仍包含 user 和 assistant 两条消息

把失败步骤的截图（这张会成为 `failed.png`）和运行链接发我，并用一句话解释失败原因：为什么测试没通过、和这次改动有什么关系。然后我们就修复、重新推送，对照两次运行。

> 因为把原有正确功能改错了，所以测试没通过，删除用户消息时什么都没删除。[https://github.com/QiWang3569/isse-lab5-chat-ci/actions/runs/39383476794](https://github.com/QiWang3569/isse-lab5-chat-ci/actions/runs/39383476794) 截图在"D:\Files\Desktop\isse-lab5-chat-ci\fe98e064-7627-4a22-9207-a8d55f106e5d.png"

<details><summary>2 previous messages</summary>

> 你的解释完全正确：删除接口返回了成功，但实际没有从数据里移除消息，所以测试在「删除后再次查询应为空」这条断言上失败。我现在把你发的失败截图保存到课程个人目录的 `screenshots/failed.png`，然后修复代码。
>
> <details><summary>Edited a file, ran 2 commands</summary>
>
> - Ran `$src = 'D:\Files\Desktop\isse-lab5-chat-ci\fe98e064-7627-4a22-9207-a8d55f106e5d.png'
> if (-not (Test-Path -LiteralPath $src)) { throw "截图不存在: $src" }
> $dstDir = 'D:\Files\Desktop\isse-labs\lab5\2200014163-WangQi\screenshots'
> New-Item -ItemType Directory -Force -Path $dstDir | Out-Null
> Copy-Item -LiteralPath $src -Destination (Join-Path $dstDir 'failed.png') -Force
> Get-Item -LiteralPath (Join-Path $dstDir 'failed.png') | Select-Object FullName, Length`
> - Wrote `D:/Files/Desktop/isse-lab5-chat-ci/app.py` (+3 -0)
> - Ran `$i=0; Get-Content -LiteralPath 'app.py' | ForEach-Object { $i++; if ($i -ge 236 -and $i -le 252) { '{0,4}: {1}' -f $i, $_ } }`
>
> </details>
</details>

截图已保存到课程个人目录 [failed.png](/D:/Files/Desktop/isse-labs/lab5/2200014163-WangQi/screenshots/failed.png)（86 KB）。代码也已经修复。

## 这次失败说明什么

失败日志和我们做的事正好对得上：测试名 `test_message_crud_flow` 告诉我们是哪项行为出了问题，断言 `assert messages == []` 显示「预期为空、实际仍有两条」，再结合这次提交删掉的两行 `pop`，就能把问题定位到 `delete_message`——它返回了成功，却没有执行删除。这正是「返回状态正常、但数据没变」的回归。

修复就是恢复原来的约定：删除用户消息时真正把它从列表里移除，并连带删掉紧随其后的助手回复。这样同一条测试的 `assert messages == []` 重新成立。

## 现在轮到你提交并推送修复

```powershell
git add app.py
git commit -m "修复消息删除功能"
git push
```

## 观察重点

- 这次是「新提交触发的全新运行」——重新跑旧的失败记录不会看到修复，因为它对应的是旧代码。
- 新运行应恢复绿色：`3 passed`、覆盖率 `78%`、`Required test coverage of 70% reached`。
- 失败和修复是两次独立运行，把这次修复成功的运行链接也发我（和之前失败的链接一起保留，就是前后对照的完整轨迹）。

确认修复后的运行通过，我们就进入任务 3：适配冒烟检查脚本，并把它加进工作流。

> [https://github.com/QiWang3569/isse-lab5-chat-ci/actions/runs/39383709861](https://github.com/QiWang3569/isse-lab5-chat-ci/actions/runs/39383709861)

<details><summary>2 previous messages</summary>

> 收到修复运行的链接。我先把课程提供的冒烟脚本骨架复制进实验仓库，为任务 3 做准备；顺便你确认一下这次修复运行是不是绿色成功（`3 passed`、78%）——如果不是，把失败日志发我。
>
> <details><summary>Ran 2 commands</summary>
>
> - Ran `$src = 'D:\Files\Desktop\isse-labs\lab5\templates\smoke_test.py'
> if (-not (Test-Path -LiteralPath $src)) { throw "模板不存在: $src" }
> $dstDir = 'D:\Files\Desktop\isse-lab5-chat-ci\scripts'
> New-Item -ItemType Directory -Force -Path $dstDir | Out-Null
> Copy-Item -LiteralPath $src -Destination (Join-Path $dstDir 'smoke_test.py') -Force
> Get-Item -LiteralPath (Join-Path $dstDir 'smoke_test.py') | Select-Object FullName, Length`
> - Ran `$a = (Get-FileHash -LiteralPath 'D:\Files\Desktop\isse-labs\lab5\templates\smoke_test.py' -Algorithm SHA256).Hash
> $b = (Get-FileHash -LiteralPath 'D:\Files\Desktop\isse-lab5-chat-ci\scripts\smoke_test.py' -Algorithm SHA256).Hash
> Write-Output ("hash_match={0}" -f ($a -eq $b))
> Write-Output '---CONFIG---'
> Get-Content -LiteralPath 'D:\Files\Desktop\isse-lab5-chat-ci\scripts\smoke_test.py' | Select-Object -First 24`
>
> </details>
</details>

冒烟脚本已复制到实验仓库 `scripts/smoke_test.py`，哈希校验和课程模板完全一致。而且好消息是：这四项配置的默认值正好就是你的应用——

```python
APP_IMPORT = "app:app"      # 你的 app.py 里就是 app = Flask(...)
HOME_PATH = "/"
HELLO_PATH = "/api/hello"
EXPECTED_HELLO = {"message": "你好"}
```

所以脚本不需要改配置，真正要做的「适配」就是我们之前在 `app.py` 里加的 `LAB5_DATA_DIR` 支持：脚本启动应用时会临时指定一个独立数据目录，不碰你的真实数据。

## 任务 3 在做什么

前面的 `test_client` 测试是在同一个进程里检查 Flask 收到请求后的处理逻辑。冒烟检查则不同：它真的启动一个临时 Flask 进程，再通过本机 HTTP 地址去访问首页和连通性接口，多检查了「进程能启动、HTTP 服务能响应」这一层，适合发现入口配置、启动依赖或路径上的明显问题。

课程骨架已经帮你写好了启动、等待就绪、发送请求、判断响应和停止清理这几部分，你只需要确认入口和检查内容。首页和接口正常，不代表浏览器里所有按钮交互都被验证——冒烟只做最基本的「能起来、能响应」。

## 现在轮到你本地运行

在仓库根目录执行：

```powershell
.\.venv\Scripts\python.exe scripts\smoke_test.py
```

预期依次看到：

```
服务已就绪
PASS /
PASS /api/hello
服务已停止
冒烟检查通过
```

如果服务起不来或某项检查失败，脚本会打印启动日志并退出非零，把完整输出发我。

同时麻烦你确认一句：刚才那次修复运行（runs/39383709861）是不是绿色成功？确认后，本地冒烟也通过的话，我就把 `Run smoke test` 这一步加进 `ci.yml`，让你推送后云端也跑冒烟。

> 是绿色的，通过了

好，任务 2 完成。两次运行都留在对话里了：失败 `runs/39383476794`，修复 `runs/39383709861`，正好是前后对照的完整轨迹。

现在请在你终端跑一下冒烟检查，把输出发我：

```powershell
.\.venv\Scripts\python.exe scripts\smoke_test.py
```

应该依次看到 `服务已就绪`、`PASS /`、`PASS /api/hello`、`服务已停止`、`冒烟检查通过`。通过后我就把这一步加进 `ci.yml`，让你推送后在云端也执行冒烟。

> PS D:\Files\Desktop\isse-lab5-chat-ci> .\.venv\Scripts\python.exe scripts\smoke_test.py
> 服务已就绪
> PASS /
> PASS /api/hello
> 服务已停止
> 冒烟检查通过

<details><summary>2 previous messages</summary>

> 本地冒烟通过，很好。现在把冒烟检查加进工作流。
>
> <details><summary>Edited a file</summary>
>
> - Wrote `D:/Files/Desktop/isse-lab5-chat-ci/.github/workflows/ci.yml` (+3 -0)
>
> </details>
</details>

`ci.yml` 已更新：在 `Run tests with coverage` 之后新增了一个 `Run smoke test` 步骤，执行的就是你本地刚跑通的同一条命令。

## 这一步在做什么

冒烟检查在本地已经通过，现在把它纳入 CI，这样每次推送后，除了检查接口的业务逻辑，还能确认这次提交在云端环境里能真正启动应用。前面步骤都通过后，工作流会继续做服务启动检查；冒烟脚本一旦返回失败，这一步就会被判定为失败。

## 现在轮到你提交推送

```powershell
git add scripts/smoke_test.py .github/workflows/ci.yml
git status
git commit -m "添加冒烟检查并接入 CI"
git push
```

推送后在 Actions 打开新运行，进入 job，分别展开两个步骤：

- `Run tests with coverage`：`3 passed`、覆盖率 `78%`。
- `Run smoke test`：依次 `服务已就绪`、`PASS /`、`PASS /api/hello`、`服务已停止`、`冒烟检查通过`。

## 观察重点

这一次完整通过（测试 + 覆盖率 + 冒烟）的运行，就是我们要留存的「云端成功」证据。请把这次运行的截图发我（可以一张长截图同时拍到覆盖率行和冒烟步骤，也可以多张），加上运行链接。我会把它保存成课程个人目录里的 `cloud-passed.png`，然后进入任务 4：注册并启动你本机的 runner。

> [https://github.com/QiWang3569/isse-lab5-chat-ci/actions/runs/39384053568/job/118499563287](https://github.com/QiWang3569/isse-lab5-chat-ci/actions/runs/39384053568/job/118499563287) "D:\Files\Desktop\isse-lab5-chat-ci\5146d62f-4160-411a-98ed-8e9e62b84b13.png" 都通过了

<details><summary>2 previous messages</summary>

> 云端测试 + 覆盖率 + 冒烟都通过了，Task 3 完成。我先把这次成功运行的截图保存成 `cloud-passed.png`。
>
> <details><summary>Ran a command</summary>
>
> - Ran `$src = 'D:\Files\Desktop\isse-lab5-chat-ci\5146d62f-4160-411a-98ed-8e9e62b84b13.png'
> if (-not (Test-Path -LiteralPath $src)) { throw "截图不存在: $src" }
> $dstDir = 'D:\Files\Desktop\isse-labs\lab5\2200014163-WangQi\screenshots'
> New-Item -ItemType Directory -Force -Path $dstDir | Out-Null
> Copy-Item -LiteralPath $src -Destination (Join-Path $dstDir 'cloud-passed.png') -Force
> Get-Item -LiteralPath (Join-Path $dstDir 'cloud-passed.png') | Select-Object FullName, Length`
>
> </details>
</details>

截图已保存：[cloud-passed.png](/D:/Files/Desktop/isse-labs/lab5/2200014163-WangQi/screenshots/cloud-passed.png)。到目前为止，课程个人目录里已有 `failed.png` 和 `cloud-passed.png` 两张证据。

## 任务 4.1：注册并启动本机 runner

此前的检查都跑在 GitHub 提供的云端机器上。runner 是真正执行 job 的程序；self-hosted runner 则是安装并运行在你自己电脑上的 runner，让 GitHub 把任务交给这台机器执行。检查内容不变，这一步重点是观察「执行位置」如何从云端变成你的电脑。

配置分三步：下载、注册、启动。

- 下载：取得适合你本机系统与 CPU 架构的程序。你的机器是 Windows，绝大多数情况选 `Windows` + `x64`（如果你的机器是 ARM 芯片就选 ARM64）。
- 注册：把这个 runner 关联到你的实验仓库。注册命令里会带一个 `--token`，这是本次关联用的临时凭据，只在你本机终端里用，截图和对话里都不要出现它。
- 启动：启动后 runner 会连上 GitHub 并等待任务。注册成功后网页会列出这个 runner；启动并连接后，网页显示在线（Idle），本机终端出现「Listening for Jobs」之类的等待提示。

## 现在轮到你操作

打开实验仓库的 `Settings → Actions → Runners → New self-hosted runner`，选择 `Windows` 和 `x64`，按页面给出的命令执行（页面会自动生成带正确版本号和 token 的命令，以页面为准）：

1. 在课程仓库之外建一个目录放 runner，例如 `D:\Files\Desktop\actions-runner`，下载并解压 runner 压缩包。
2. 运行 `./config.cmd --url https://github.com/QiWang3569/isse-lab5-chat-ci --token <页面上的token>`。过程中询问名称、标签、工作目录时直接回车用默认值即可（默认标签包含 `self-hosted`，后面工作流就是靠它匹配）。
3. 运行 `./run.cmd`，保持这个终端窗口开着（前台运行）。

## 观察重点

- 网页 `Runners` 列表出现你的 runner，状态为 Idle（在线）。
- 终端出现等待任务的提示，且不要关闭窗口。
- 注册 token 不要在截图或对话里出现。

确认网页显示在线、终端显示等待后告诉我。接着我就把同一份 `ci.yml` 的 `runs-on` 从 `ubuntu-latest` 改成 `self-hosted`，并适配本机 Python 环境，然后你推送观察任务在你电脑上执行。

> 帮我下载吧：Download
>
> We recommend configuring the runner under "\actions-runner". This will help avoid issues related to service identity folder permissions and long path restrictions on Windows.
>
> `# Create a folder under the drive root`\
> `$ mkdir actions-runner; cd actions-runner`
>
> `# Download the latest runner package`\
> `$ Invoke-WebRequest -Uri https://github.com/actions/runner/releases/download/v2.337.0/actions-runner-win-x64-2.337.0.zip -OutFile actions-runner-win-x64-2.337.0.zip`
>
> `# Optional: Validate the hash`\
> `$ if((Get-FileHash -Path actions-runner-win-x64-2.337.0.zip -Algorithm SHA256).Hash.ToUpper() -ne '1150692afa94e71f872017e254ea55b6eece1eece3fe7e3a6d4c93d0a1b85cfc'.ToUpper()){ throw 'Computed checksum did not match' }`
>
> `# Extract the installer`\
> `$ Add-Type -AssemblyName System.IO.Compression.FileSystem ; [System.IO.Compression.ZipFile]::ExtractToDirectory("$PWD/actions-runner-win-x64-2.337.0.zip", "$PWD")`
>
> ## Configure
>
> `# Create the runner and start the configuration experience`\
> `$ ./config.cmd --url https://github.com/QiWang3569/isse-lab5-chat-ci --token ***REDACTED***`
>
> `# Run it!`\
> `$ ./run.cmd`
>
> ## Using your self-hosted runner
>
> `# Use this YAML in your workflow file for each job`\
> `runs-on: self-hosted` 地址"D:\Files\Desktop\isse-lab5-chat-ci\actions-runner"

<details><summary>2 previous messages</summary>

> 注意两件事：runner 不能放在代码仓库里面，GitHub 也建议放在盘符根目录，所以我放到 `D:\actions-runner`（你写的是 `isse-lab5-chat-ci\actions-runner`，那会让 runner 程序和仓库代码混在一起，还会带来路径长度问题）。另外，注册 token 请不要贴到对话里，我也不会使用或复述它——这个 token 很快会过期，你在自己终端里用即可。
>
> 我现在帮你下载、校验哈希并解压。
>
> <details><summary>Ran a command</summary>
>
> - Ran `$ProgressPreference = 'SilentlyContinue'
> $dir = 'D:\actions-runner'
> New-Item -ItemType Directory -Force -Path $dir | Out-Null
> $zip = Join-Path $dir 'actions-runner-win-x64-2.337.0.zip'
> if (-not (Test-Path -LiteralPath $zip)) {
>   Invoke-WebRequest -Uri 'https://github.com/actions/runner/releases/download/v2.337.0/actions-runner-win-x64-2.337.0.zip' -OutFile $zip
> }
> $hash = (Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToUpper()
> $expected = '1150692AFA94E71F872017E254EA55B6EE1CEE1CE3FE7E3A6D4C93D0A1B85CFC'
> if ($hash -ne $expected) { throw "SHA256 mismatch: $hash" }
> Add-Type -AssemblyName System.IO.Compression.FileSystem
> [System.IO.Compression.ZipFile]::ExtractToDirectory($zip, $dir)
> Get-ChildItem -LiteralPath $dir | Select-Object Name, Length`
>
> </details>
</details>

> "D:\Files\Desktop\actions-runner" 这个地址，写错了

<details><summary>7 previous messages</summary>

> <details><summary>Ran a command</summary>
>
> - Ran `Write-Output '--- D:\actions-runner ---'; if (Test-Path -LiteralPath 'D:\actions-runner') { Get-ChildItem -Force -LiteralPath 'D:\actions-runner' | Select-Object Name, Length } else { Write-Output 'not exists' }
> Write-Output '--- D:\Files\Desktop\actions-runner ---'; if (Test-Path -LiteralPath 'D:\Files\Desktop\actions-runner') { Get-ChildItem -Force -LiteralPath 'D:\Files\Desktop\actions-runner' | Select-Object Name, Length } else { Write-Output 'not exists' }`
>
> </details>
>
> 明白了，目标改为 `D:\Files\Desktop\actions-runner`（这个在代码仓库之外，没问题）。刚才那次中断在 `D:\actions-runner` 只留下一个 0 字节的压缩包，我会顺手清掉，再把 runner 下载到正确位置。
>
> <details><summary>Ran 3 commands</summary>
>
> - Ran `$ProgressPreference = 'SilentlyContinue'
> if (Test-Path -LiteralPath 'D:\actions-runner\actions-runner-win-x64-2.337.0.zip') { Remove-Item -LiteralPath 'D:\actions-runner\actions-runner-win-x64-2.337.0.zip' -Force }
> if (Test-Path -LiteralPath 'D:\actions-runner') { Remove-Item -LiteralPath 'D:\actions-runner' -Force }
> $dir = 'D:\Files\Desktop\actions-runner'
> New-Item -ItemType Directory -Force -Path $dir | Out-Null
> $zip = Join-Path $dir 'actions-runner-win-x64-2.337.0.zip'
> if (-not (Test-Path -LiteralPath $zip)) {
>   Invoke-WebRequest -Uri 'https://github.com/actions/runner/releases/download/v2.337.0/actions-runner-win-x64-2.337.0.zip' -OutFile $zip
> }
> $hash = (Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToUpper()
> $expected = '1150692AFA94E71F872017E254EA55B6EE1CEE1CE3FE7E3A6D4C93D0A1B85CFC'
> if ($hash -ne $expected) { throw "SHA256 mismatch: $hash" }
> Add-Type -AssemblyName System.IO.Compression.FileSystem
> [System.IO.Compression.ZipFile]::ExtractToDirectory($zip, $dir)
> Get-ChildItem -LiteralPath $dir | Select-Object Name, Length`
> - Ran `Get-Item -LiteralPath 'D:\Files\Desktop\actions-runner\actions-runner-win-x64-2.337.0.zip' -ErrorAction SilentlyContinue | Select-Object Name, Length, LastWriteTime`
> - Ran `Get-Item -LiteralPath 'D:\Files\Desktop\actions-runner\actions-runner-win-x64-2.337.0.zip' -ErrorAction SilentlyContinue | Select-Object Name, Length, LastWriteTime`
>
> </details>
>
> 下载进行中，目前已到约 76MB（runner 包总共约 180MB，速度偏慢，估计还要几分钟）。我继续等待，完成后会自动校验哈希并解压。
>
> <details><summary>Ran a command</summary>
>
> - Ran `Write-Output '--- D:\actions-runner ---'
> if (Test-Path -LiteralPath 'D:\actions-runner') { Get-ChildItem -Force -LiteralPath 'D:\actions-runner' | Select-Object Name, Length } else { Write-Output 'not exists' }
> Write-Output '--- downloaded zip ---'
> Get-Item -LiteralPath 'D:\Files\Desktop\actions-runner\actions-runner-win-x64-2.337.0.zip' -ErrorAction SilentlyContinue | Select-Object Name, Length`
>
> </details>
>
> 下载其实已经完成了，哈希「不匹配」是我在命令里把预期哈希抄错了一个字符，文件本身没问题。正确的预期哈希以 GitHub 页面为准。我现在用正确哈希重新校验并解压，同时清掉第一次中断残留的那个重复下载（在 `D:\actions-runner`）。
>
> <details><summary>Ran a command</summary>
>
> - Ran `$ProgressPreference = 'SilentlyContinue'
> if (Test-Path -LiteralPath 'D:\actions-runner\actions-runner-win-x64-2.337.0.zip') { Remove-Item -LiteralPath 'D:\actions-runner\actions-runner-win-x64-2.337.0.zip' -Force }
> if (Test-Path -LiteralPath 'D:\actions-runner') { Remove-Item -LiteralPath 'D:\actions-runner' -Force }
> $dir = 'D:\Files\Desktop\actions-runner'
> $zip = Join-Path $dir 'actions-runner-win-x64-2.337.0.zip'
> $hash = (Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToLower()
> $expected = '1150692afa94e71f872017e254ea55b6eece1eece3fe7e3a6d4c93d0a1b85cfc'
> if ($hash -ne $expected) { throw "SHA256 mismatch: $hash" }
> Add-Type -AssemblyName System.IO.Compression.FileSystem
> [System.IO.Compression.ZipFile]::ExtractToDirectory($zip, $dir)
> Get-ChildItem -LiteralPath $dir | Select-Object Name, Length`
>
> </details>
</details>

runner 下载、校验、解压都完成了，放在 `D:\Files\Desktop\actions-runner`（代码仓库之外）。里面已经有 `config.cmd` 和 `run.cmd`，第一次中断留下的重复下载也清掉了。

现在轮到你注册并启动。打开一个终端：

```powershell
cd D:\Files\Desktop\actions-runner
.\config.cmd --url https://github.com/QiWang3569/isse-lab5-chat-ci --token <GitHub页面上的token>
```

注册过程中它会问三样东西，全部直接回车用默认值即可：

- runner 名称（默认是电脑名）
- 标签（默认包含 `self-hosted`，后面工作流就靠它匹配）
- 工作目录（默认 `_work`，这是 runner 检出代码的地方，和你平时编辑应用的目录不同）

注册完成后前台启动：

```powershell
.\run.cmd
```

保持这个窗口开着。

## 观察重点

- 网页 `Settings → Actions → Runners` 里出现你的 runner，状态 `Idle`（在线）。
- 终端出现类似 `Listening for Jobs` 的等待提示，并且不要关闭窗口。
- 两个提醒：token 是临时凭据（约一小时过期），只在你的终端里用；之前你把它贴进对话了，后面导出对话轨迹时记得把这一处 token 删掉，截图里也别出现。

确认网页显示在线、终端显示等待后告诉我。然后我把 `ci.yml` 的 `runs-on` 改成 `self-hosted` 并适配本机 Python，你推送后就能看到任务在你电脑上跑了。

> PS D:\Files\Desktop\isse-labs> cd D:\Files\Desktop\actions-runner
> PS D:\Files\Desktop\actions-runner> ./config.cmd --url https://github.com/QiWang3569/isse-lab5-chat-ci --token ***REDACTED***
>
> --------------------------------------------------------------------------------
> |        ____ _ _   _   _       _          _        _   _                      |
> |       / ___(_) |_| | | |_   _| |__      / \   ___| |_(_) ___  _ __  ___      |
> |      | |  _| | __| |_| | | | | '_ \    / _ \ / __| __| |/ _ \| '_ \/ __|     |
> |      | |_| | | |_|  _  | |_| | |_) |  / ___ \ (__| |_| | (_) | | | \__ \     |
> |       \____|_|\__|_| |_|\__,_|_.__/  /_/   \_\___|\__|_|\___/|_| |_|___/     |
> |                                                                              |
> |                       Self-hosted runner registration                        |
> |                                                                              |
> --------------------------------------------------------------------------------
>
> # Authentication
>
> √ Connected to GitHub
>
> # Runner Registration
>
> Enter the name of the runner group to add this runner to: [press Enter for Default]
>
> Enter the name of runner: [press Enter for BEICHEN]
>
> This runner will have the following labels: 'self-hosted', 'Windows', 'X64'
> Enter any additional labels (ex. label-1,label-2): [press Enter to skip]
>
> √ Runner successfully added
>
> # Runner settings
>
> Enter name of work folder: [press Enter for _work]
>
> √ Settings Saved.
>
> Would you like to run the runner as service? (Y/N) [press Enter for N]
> PS D:\Files\Desktop\actions-runner> ./config.cmd --url https://github.com/QiWang3569/isse-lab5-chat-ci --token ***REDACTED***
>
> --------------------------------------------------------------------------------
> |        ____ _ _   _   _       _          _        _   _                      |
> |       / ___(_) |_| | | |_   _| |__      / \   ___| |_(_) ___  _ __  ___      |
> |      | |  _| | __| |_| | | | | '_ \    / _ \ / __| __| |/ _ \| '_ \/ __|     |
> |      | |_| | | |_|  _  | |_| | |_) |  / ___ \ (__| |_| | (_) | | | \__ \     |
> |       \____|_|\__|_| |_|\__,_|_.__/  /_/   \_\___|\__|_|\___/|_| |_|___/     |
> |
>                          |
> |                       Self-hosted runner registration                        |
> |
>                          |
> --------------------------------------------------------------------------------
> Cannot configure the runner because it is already configured. To reconfigure the runner, run 'config.cmd remove' or './config.sh remove' first.
> PS D:\Files\Desktop\actions-runner>

注册成功了：runner 名 `BEICHEN`，标签 `self-hosted, Windows, X64`，工作目录 `_work`，设置已保存。你第二次再跑 `config.cmd` 提示「already configured」是正常的，因为第一次已经注册好了，不用管它。

现在只差启动这一步，在同一个终端里执行：

```powershell
.\run.cmd
```

然后保持这个窗口开着，不要关闭。

## 观察重点

- 终端出现类似 `Listening for Jobs` 的等待提示。
- 网页 `Settings → Actions → Runners` 里 `BEICHEN` 显示 `Idle`（在线）。

确认这两点后告诉我，我就把 `ci.yml` 改成 `runs-on: self-hosted` 并适配本机 Python 环境，然后你推送，任务就会发到这台电脑上执行。

（另外再提醒一次：token 已经出现在对话里，最后导出 `AGENT_TRACE.md` 时记得把两处 token 都删掉。）

> 是的，是的

<details><summary>2 previous messages</summary>

> runner 在线了，很好。现在把同一份 `ci.yml` 切换到本机执行。
>
> <details><summary>Edited a file, explored a file</summary>
>
> - Wrote `D:/Files/Desktop/isse-lab5-chat-ci/.github/workflows/ci.yml` (+12 -10)
>
> <details><summary>Explored a file</summary>
>
> - Read `./.github/workflows/ci.yml`
>
> </details>
>
> </details>
</details>

`ci.yml` 已切换完成。现在这份工作流的 `runs-on` 是 `self-hosted`，同一次推送事件会把 job 交给你的本机 runner。

## 这一步在做什么

runner 在线了，但原工作流之前还写着 `runs-on: ubuntu-latest`。改成 `self-hosted` 后，相同的提交事件就会匹配到带 `self-hosted` 标签的本地 runner。

本机执行同样要自己准备 Python 和依赖。关键区别是：runner 会在自己的工作目录（`_work\isse-lab5-chat-ci\isse-lab5-chat-ci`）检出代码，这个目录和你平时编辑应用的目录不是同一个；你在开发终端里激活的 `.venv` 也不会自动变成 runner 任务的环境。所以工作流里我明确做了这几步：先 `python --version` 展示本机 Python，再在 runner 工作区新建一个 `.venv`，按依赖清单安装，最后跑和之前完全相同的测试、70% 覆盖率和冒烟命令。另外我加了 `shell: powershell`，确保在 Windows 上用的是本机 PowerShell。

之前云端成功的记录还留在历史提交里，我们始终只用这一份 `ci.yml`。

## 现在轮到你提交推送

```powershell
git add .github/workflows/ci.yml
git commit -m "切换到自托管 runner 执行 CI"
git push
```

推送后，同时观察两个地方：

- 本机终端：从 `Listening for Jobs` 变成接到任务、逐步执行，最后显示任务完成。
- 网页 Actions：这次运行显示 runner 是本机（self-hosted / 你的机器名），各步骤依次通过。

## 观察重点

- 如果任务一直排队（queued），先确认 runner 是否 Idle、标签是否包含 `self-hosted`。
- 第一次本机运行会慢一点（要建虚拟环境、装依赖），耐心等它完成。
- 完成后把两张截图发我：一张网页 Actions 结果（`self-hosted-actions.png`）、一张本机终端接到并完成任务（`self-hosted-terminal.png`），加上运行链接。两张要能对应同一次任务。

完成后我们就收尾：停止 runner、整理应用副本和截图、导出对话轨迹、发课程 PR。

> 失败了Run python --version&#x20;
> . : File D:\Files\Desktop\actions-runner\\\_work\\\_temp\23fa19db-a099-4da6-a9a7-b31eb1dc2648.ps1 cannot be loaded because &#x20;
> running scripts is disabled on this system. For more information, see about_Execution_Policies at https\:/go.microsoft.c&#x20;
> om/fwlink/?LinkID=135170.&#x20;
> At line:1 char:3&#x20;
> \+ . 'D:\Files\Desktop\actions-runner\\\_work\\\_temp\23fa19db-a099-4da6-a9a ...&#x20;
> \+   \~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~&#x20;
> &#x20;   \+ CategoryInfo          : SecurityError: (:) [], PSSecurityException&#x20;
> &#x20;   \+ FullyQualifiedErrorId : UnauthorizedAccess&#x20;
> **Error:&#x20;**&#x50;rocess completed with exit code 1.

<details><summary>2 previous messages</summary>

> 这个失败是 Windows PowerShell 执行策略导致的：runner 会用 PowerShell 去执行一个临时 `.ps1` 脚本，但你系统的执行策略是 Restricted（禁止运行脚本），所以第一步 `python --version` 就挂了。这和你的代码无关，是运行环境的问题。
>
> 最省事、也最干净的做法是不走 PowerShell，改用 `cmd` 作为 run 步骤的 shell——命令本身都是通用的，改完就绕开了执行策略限制，也不用动你系统的安全设置。
>
> <details><summary>Edited a file</summary>
>
> - Wrote `D:/Files/Desktop/isse-lab5-chat-ci/.github/workflows/ci.yml` (+1 -1)
>
> </details>
</details>

改好了：`run` 步骤的 shell 现在是 `cmd`，不再依赖 PowerShell 脚本执行。如果你以后想保留 PowerShell，也可以在终端跑一次 `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`，但这次用 `cmd` 就够了，不用动系统设置。

请重新提交推送：

```powershell
git add .github/workflows/ci.yml
git commit -m "本机 runner 使用 cmd shell 避免执行策略限制"
git push
```

推送后照旧同时盯两个地方：本机终端从等待变成接到任务并逐步执行，网页 Actions 显示 runner 是本机、各步骤通过。第一次本机运行要建虚拟环境装依赖，会稍慢。把结果（两张截图 + 运行链接）发我。

> [https://github.com/QiWang3569/isse-lab5-chat-ci/actions/runs/39394007503](https://github.com/QiWang3569/isse-lab5-chat-ci/actions/runs/39394007503)"D:\Files\Desktop\isse-lab5-chat-ci\6efda55a-b96a-4e4f-a049-2c84bdf56129.png"

<details><summary>2 previous messages</summary>

> 我先查一下这次运行的权威状态（用 GitHub API，避免只靠截图），确认是否成功。
>
> <details><summary>Ran a command</summary>
>
> - Ran `$ProgressPreference = 'SilentlyContinue'
> $h = @{ 'User-Agent' = 'codex' }
> $r = Invoke-RestMethod -Uri 'https://api.github.com/repos/QiWang3569/isse-lab5-chat-ci/actions/runs/39394007503' -Headers $h
> Write-Output ('run status={0} conclusion={1} event={2} head={3}' -f $r.status, $r.conclusion, $r.event, $r.head_sha)
> $jobs = Invoke-RestMethod -Uri 'https://api.github.com/repos/QiWang3569/isse-lab5-chat-ci/actions/runs/39394007503/jobs' -Headers $h
> foreach ($j in $jobs.jobs) {
>   Write-Output ('job name={0} status={1} conclusion={2} runner={3}' -f $j.name, $j.status, $j.conclusion, $j.runner_name)
>   foreach ($s in $j.steps) {
>     Write-Output ('  step name={0} conclusion={1}' -f $s.name, $s.conclusion)
>   }
> }`
>
> </details>
</details>

API 返回 404（你的实验仓库应该是私有仓库，无认证读不到），所以我看不到权威状态，得靠你确认。

请告诉我这次运行（runs/39394007503）的结果：

1. 是绿色成功还是失败？如果失败，把失败步骤的日志贴给我（重点看 `python --version` 之后哪一步出问题）。
2. 另外把本机终端接到任务并执行完成的截图也发我——这张要和 Actions 里同一次运行对应（就是 `self-hosted-terminal.png`）。

确认成功后，我会把你发来的 Actions 截图存成 `self-hosted-actions.png`、终端截图存成 `self-hosted-terminal.png`，然后进入收尾：停止 runner、整理应用副本、导出对话轨迹、发课程 PR。

> 成功了"D:\Files\Desktop\isse-lab5-chat-ci\32b6a857-9bfd-4f59-a07e-a2bafdd38851.png"是本机终端接到任务并执行完成的截图

<details><summary>6 previous messages</summary>

> 太好了，Task 4 完成。我先把两张本机截图存进课程个人目录。
>
> <details><summary>Explored a file, ran a command</summary>
>
> - Ran `$dstDir = 'D:\Files\Desktop\isse-labs\lab5\2200014163-WangQi\screenshots'
> New-Item -ItemType Directory -Force -Path $dstDir | Out-Null
> $pairs = @(
>   @{ src='D:\Files\Desktop\isse-lab5-chat-ci\6efda55a-b96a-4e4f-a049-2c84bdf56129.png'; dst='self-hosted-actions.png' },
>   @{ src='D:\Files\Desktop\isse-lab5-chat-ci\32b6a857-9bfd-4f59-a07e-a2bafdd38851.png'; dst='self-hosted-terminal.png' }
> )
> foreach ($p in $pairs) {
>   if (-not (Test-Path -LiteralPath $p.src)) { throw "缺少截图: $($p.src)" }
>   Copy-Item -LiteralPath $p.src -Destination (Join-Path $dstDir $p.dst) -Force
> }
> Get-ChildItem -LiteralPath $dstDir | Select-Object Name, Length`
>
> <details><summary>Explored a file</summary>
>
> - Read `D:/Files/Desktop/isse-lab5-chat-ci/data/conversations.json`
>
> </details>
>
> </details>
>
> 数据文件是空的 `[]`，没有个人聊天记录，可以安全复制。现在把最终本机成功版本的应用复制到课程个人目录 `app/`。
>
> <details><summary>Ran a command</summary>
>
> - Ran `$src = 'D:\Files\Desktop\isse-lab5-chat-ci'
> $dst = 'D:\Files\Desktop\isse-labs\lab5\2200014163-WangQi\app'
> New-Item -ItemType Directory -Force -Path $dst | Out-Null
> Copy-Item -LiteralPath "$src\app.py" -Destination "$dst\app.py" -Force
> Copy-Item -LiteralPath "$src\requirements.txt" -Destination "$dst\requirements.txt" -Force
> Copy-Item -LiteralPath "$src\requirements-dev.txt" -Destination "$dst\requirements-dev.txt" -Force
> Copy-Item -LiteralPath "$src\.env.example" -Destination "$dst\.env.example" -Force
> Copy-Item -LiteralPath "$src\.gitignore" -Destination "$dst\.gitignore" -Force
> Copy-Item -LiteralPath "$src\frontend" -Destination "$dst\frontend" -Recurse -Force
> Copy-Item -LiteralPath "$src\.github" -Destination "$dst\.github" -Recurse -Force
> Copy-Item -LiteralPath "$src\tests" -Destination "$dst\tests" -Recurse -Force
> Copy-Item -LiteralPath "$src\scripts" -Destination "$dst\scripts" -Recurse -Force
> Copy-Item -LiteralPath "$src\data" -Destination "$dst\data" -Recurse -Force
> Get-ChildItem -Recurse -File -LiteralPath $dst | ForEach-Object { $_.FullName.Substring($dst.Length + 1) }`
>
> </details>
>
> 复制基本完成，但发现带进来一个 `tests\__pycache__` 缓存文件（你本地跑 pytest 生成的），这不属于提交材料，我清掉它。
>
> <details><summary>Ran 2 commands</summary>
>
> - Ran `$cache = 'D:\Files\Desktop\isse-labs\lab5\2200014163-WangQi\app\tests\__pycache__'
> if (Test-Path -LiteralPath $cache) {
>   $resolved = (Resolve-Path -LiteralPath $cache).Path
>   $within = 'D:\Files\Desktop\isse-labs\lab5\2200014163-WangQi\app'
>   if ($resolved.StartsWith($within, [System.StringComparison]::OrdinalIgnoreCase)) {
>     Remove-Item -LiteralPath $resolved -Recurse -Force
>     Write-Output "removed: $resolved"
>   } else {
>     throw "target outside expected dir: $resolved"
>   }
> }
> Get-ChildItem -Recurse -File -LiteralPath 'D:\Files\Desktop\isse-labs\lab5\2200014163-WangQi\app' | ForEach-Object { $_.FullName.Substring('D:\Files\Desktop\isse-labs\lab5\2200014163-WangQi\app'.Length + 1) }`
> - Ran `git branch --show-current; git status -sb; Write-Output '---个人目录内容---'; Get-ChildItem -Recurse -Force -LiteralPath 'lab5/2200014163-WangQi' | ForEach-Object { $_.FullName.Substring((Get-Location).Path.Length + 1) }`
>
> </details>
</details>

收尾材料基本齐了。当前课程分支 `lab5/2200014163-WangQi` 下已有完整结构：

- `app/`：应用代码（`app.py`、`frontend/`、`tests/`、`scripts/smoke_test.py`、`.github/workflows/ci.yml`、依赖文件、`.env.example`、`.gitignore`、空的 `data/conversations.json`），已清掉 `__pycache__`。
- `screenshots/`：`failed.png`、`cloud-passed.png`、`self-hosted-actions.png`、`self-hosted-terminal.png` 四张都在。

还差最后几件由你完成的事：

## 1. 停止本机 runner

在运行 `run.cmd` 的那个终端里按 `Ctrl+C` 停掉 runner，确认网页 `Runners` 里 `BEICHEN` 变成离线（Offline）。

## 2. 导出对话轨迹到 AGENT_TRACE.md

沿用前面 Lab 的方式，把本次真实对话导出成 Markdown，保存到 `lab5/2200014163-WangQi/AGENT_TRACE.md`（或填一个可访问的分享链接）。重点：导出前把对话里出现过的两处注册 token 全部删掉（就是 GitHub 页面生成、你贴进对话的那串），截图里也不要带 token。

## 3. 自查材料

确认 `app/` 里没有真实 `.env`（确实没有）、没有真实 API Key、`data/conversations.json` 是空的 `[]`，runner 程序也不在仓库里（它在 `D:\Files\Desktop\actions-runner`）。

一个提醒：`self-hosted-terminal.png` 只有约 1.6KB，有点小，请你打开看一眼是否清楚显示「终端接到任务并执行完成」；如果不清楚，重截一张发我，我重新保存。

## 4. 提交、推送并发 PR

在课程仓库根目录执行：

```powershell
git add lab5/2200014163-WangQi
git status
git commit -m "Lab5：GitHub Actions 持续集成（2200014163 王琪）"
git push -u origin lab5/2200014163-WangQi
```

然后到你的 Fork（`QiWang3569/isse-labs`）向 `pku-software/isse-labs` 的 `main` 分支发起 PR，标题：

```text
[Lab5] 2200014163-王琪 GitHub Actions持续集成
```

完成以上四步后告诉我结果（PR 链接、runner 已停止、token 已清理），我再帮你做最后核对。
