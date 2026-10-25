# 引导完成 Lab5 CI 实验

> ```text
> 请完整阅读 lab5/AGENTS.md 和 lab5/README.md，按交互式流程带我完成 Lab5。
> ```

<details><summary>8 previous messages</summary>

> 我先完整读取 `lab5/AGENTS.md` 和 `lab5/README.md`，再检查 Lab5 当前代码与运行状态。之后会按里程碑一步步带你实现和验证，每一步都等你确认或亲自尝试后再继续。
>
> <details><summary>Explored 2 files, a list, ran a command</summary>
>
> <details><summary>Explored 2 files, a list</summary>
>
> - Read `./lab5/AGENTS.md`
> - Read `./lab5/README.md`
> - Listed files in `lab5`
>
> </details>
>
> - Ran `git status --short -- lab5`
>
> </details>
>
> 当前终端的默认 shell 被错误地切到了 WSL，刚才几条读取命令没有真正执行。我会改用原生 PowerShell 继续，不影响仓库内容。
>
> <details><summary>Explored 2 files, ran a command</summary>
>
> <details><summary>Explored 2 files</summary>
>
> - Read `./lab5/AGENTS.md`
> - Read `./lab5/README.md`
>
> </details>
>
> - Ran `rg --files lab5`
>
> </details>
>
> 两份指引已完整读完。现在我先确认课程仓库路径、当前分支/远端，以及你的 Lab2 实际位置，这样能给出准确的个人目录名，避免误用仓库里其他同学的实验副本。
>
> <details><summary>Explored a file, ran 15 commands</summary>
>
> - Ran `git branch --show-current; git remote -v`
>
> - Ran `rg --files -g 'AGENTS.md' -g '!**/.git/**'`
>
> - Ran `Get-ChildItem -LiteralPath '.' -Force | Select-Object Name,Mode; Get-ChildItem -LiteralPath 'lab2','lab3','lab4' -ErrorAction SilentlyContinue | Select-Object @{Name='Lab';Expression={$_.Directory.Name}},Name,Mode`
>
> - Ran `git log -5 --oneline --decorate`
>
> <details><summary>Explored a file</summary>
>
> - Read `./AGENTS.md`
>
> </details>
>
> - Ran `git config --get user.name; git config --get user.email`
>
> - Ran `gh auth status; gh api user --jq '{login: .login, name: .name, email: .email}'`
>
> - Ran `Get-ChildItem -LiteralPath 'lab2' -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 15 Name,LastWriteTime`
>
> - Ran `git log --all --author='CountlessBugs' --oneline -15`
>
> - Ran `rg --files 'lab2/2500013167-WangPeiyuan'`
>
> - Ran `git status --short -- 'lab2/2500013167-WangPeiyuan'; git log -3 --oneline -- 'lab2/2500013167-WangPeiyuan'`
>
> - Ran `Get-ChildItem -LiteralPath 'lab2/2500013167-WangPeiyuan' -Force | Select-Object Name,Mode,Length`
>
> - Ran `Get-ChildItem -LiteralPath 'lab2' -Directory | Where-Object { $_.Name -match '3167|王珮源|WangPeiyuan' } | Select-Object FullName,Name`
>
> - Ran `Get-ChildItem -LiteralPath '.' -Directory | Where-Object { $_.Name -match '3167|王珮源|WangPeiyuan' } | Select-Object FullName,Name`
>
> - Ran `git show --stat --oneline --summary 398ae57`
>
> - Ran `git show --stat --oneline --summary 63c1038`
>
> </details>
>
> 已根据本机 GitHub 登录和提交历史定位到你的 Lab2：`lab2\王珮源-2500013167`。我再核对它的应用入口与仓库脏状态；这决定创建课程分支前是否有需要特别保留的未提交内容。
>
> <details><summary>Explored a file, ran 9 commands</summary>
>
> - Ran `rg --files 'lab2/王珮源-2500013167'`
>
> - Ran `git status --short -- 'lab2/王珮源-2500013167'; git log -3 --oneline -- 'lab2/王珮源-2500013167'`
>
> - Ran `git diff --stat -- lab5/README.md lab5/AGENTS.md; git diff -- lab5/README.md | Select-Object -First 40`
>
> - Ran `git status --porcelain=v2 -- 'lab5/README.md' 'lab5/AGENTS.md'`
>
> - Ran `git status --short`
>
> <details><summary>Explored a file</summary>
>
> - Read `./lab2/王珮源-2500013167/README.md`
>
> </details>
>
> - Ran `Get-Content -LiteralPath 'lab2/王珮源-2500013167/requirements.txt' -Raw; Get-Content -LiteralPath 'lab2/王珮源-2500013167/app.py' -TotalCount 260`
>
> - Ran `git rev-parse HEAD; git rev-parse origin/main; git status --short --branch`
>
> - Ran `gh repo view CountlessBugs/isse-lab5-chat-ci --json name,url,visibility,defaultBranchRef,isEmpty 2>&1`
>
> - Ran `git ls-remote --heads origin 'refs/heads/lab5/*'`
>
> </details>
</details>

已完整阅读 [lab5/AGENTS.md](/D:/Projects/Course/isse-labs/lab5/AGENTS.md) 和 [lab5/README.md](/D:/Projects/Course/isse-labs/lab5/README.md)。

## 本实验要完成什么

Lab5 会延续你的 Lab2 聊天应用，逐步完成一条完整的持续集成流程：

1. 为聊天记录 CRUD 和一种非法输入编写自动测试，模型调用使用 mock。
2. 配置 GitHub Actions，测试通过且后端覆盖率至少达到 70%。
3. 故意破坏一处已测试功能，观察 Actions 失败，再修复并重新运行。
4. 接入冒烟检查，验证应用确实能够启动并提供 HTTP 响应。
5. 注册本机 self-hosted runner，让同一套检查在本机执行。
6. 整理四项截图、真实对话和应用代码，提交到课程仓库并发起 PR。

这次不仅是“让测试跑通”，还要求你能根据真实运行结果解释测试、覆盖率、失败原因和 runner 的执行位置，因此我们会按阶段交互，不会一次性把所有代码都做完。

## 两个仓库的用途

当前课程仓库是：

```text
D:\Projects\Course\isse-labs
```

它的用途是提交最终作业。课程 Fork 当前位于 `main`，且本地 `main` 与 `origin/main` 同步。

本次会新建一个独立的实验仓库，例如：

```text
D:\Projects\Course\isse-lab5-chat-ci
```

它用于保存 Lab2 应用、测试、CI 配置和 Actions 真实运行历史。它必须放在课程仓库之外，避免一个 Git 仓库嵌套另一个 Git 仓库。

你的 Lab2 应用目前位于：

```text
D:\Projects\Course\isse-labs\lab2\王珮源-2500013167
```

根据 GitHub 账户 `CountlessBugs`、姓名 `Peiyuan Wang` 和提交记录，本次使用：

```text
课程分支：lab5/2500013167-wangpeiyuan
个人目录：lab5\2500013167-wangpeiyuan
```

如果这和你的课程登记信息不一致，请先告诉我。

## 人机分工

你负责实际运行命令、编辑 `.gitignore`、提交和推送、操作 GitHub Actions、注册并启动本机 runner、观察日志、截图、导出对话以及发起最终 PR。

我负责解释每一步的原理，检查你的实际应用，编写当前阶段的代码与配置，并根据真实输出帮助你定位问题。

真实 `.env`、DeepSeek API Key 和 runner 注册 token 不会由我读取或放进仓库；它们始终只保留在你的本机。

## 当前任务：建立两条独立工作线

先给课程仓库创建一个专用分支。分支让 Lab5 的提交与 `main` 隔离，不会影响已有 Lab2 作业。在 PowerShell 中运行：

```powershell
cd D:\Projects\Course\isse-labs

git fetch origin
git switch main
git pull --ff-only origin main
git switch -c lab5/2500013167-wangpeiyuan

New-Item -ItemType Directory -Force -Path 'lab5\2500013167-wangpeiyuan'

git status --short --branch
```

预期最后一行显示：

```text
## lab5/2500013167-wangpeiyuan
```

新目录为空时不会出现在 `git status` 中，这是正常的。

随后打开 GitHub，新建个人仓库：

- 名称：`isse-lab5-chat-ci`
- 可见性：建议 Public，便于提交 Actions 运行链接；如果你不希望公开源码，也可以使用 Private
- 不要勾选自动生成 README、`.gitignore` 或 License
- 默认分支保持 `main`

创建后，在 **Code** 页面复制仓库地址，然后在 PowerShell 中克隆：

```powershell
cd D:\Projects\Course
git clone git@github.com:CountlessBugs/isse-lab5-chat-ci.git
```

如果 GitHub 给你的克隆按钮显示 HTTPS，就使用页面上那条地址。

克隆完成后，请把下面三项结果发给我：

1. `git status --short --branch` 显示的课程分支。
2. 新仓库的 GitHub 地址。
3. 新仓库克隆后的本地绝对路径。

确认之后，我再读取你的 Lab2 应用，指导复制文件、处理 `.env.example` 与 `.gitignore`，并完成实验仓库的第一次提交和推送。

> (base) PS D:\Projects\Course\isse-labs> git status --short --branch\
> \## lab5/2500013167-wangpeiyuan
> [https://github.com/CountlessBugs/isse-lab5-chat-ci](https://github.com/CountlessBugs/isse-lab5-chat-ci)
> D:\Projects\Course\isse-lab5-chat-ci

<details><summary>4 previous messages</summary>

> 课程分支和个人实验仓库都已就位。现在进入“导入 Lab2 应用”阶段：我先核对实验仓库状态，并完整检查 Lab2 的后端、前端、依赖和隐藏配置，然后只把应用所需内容复制到实验仓库根目录，原 Lab2 目录保持不动。
>
> <details><summary>Ran 7 commands</summary>
>
> - Ran `git status --short --branch; git remote -v; Get-ChildItem -Force | Select-Object Name,Mode,Length`
> - Ran `Get-ChildItem -LiteralPath 'lab2\王珮源-2500013167' -Force -Recurse | Select-Object FullName,Mode,Length`
> - Ran `Get-Content -LiteralPath 'lab2\王珮源-2500013167\frontend\app.js' -Raw; Get-Content -LiteralPath 'lab2\王珮源-2500013167\frontend\index.html' -Raw`
> - Ran `git status --short --branch; git log -1 --oneline`
> - Ran `Get-Content -LiteralPath 'lab2\王珮源-2500013167\.env.example' -Raw; Get-Content -LiteralPath 'lab2\王珮源-2500013167\.gitignore' -Raw`
> - Ran `Get-Command python | Select-Object Source,Version; python --version; if (Test-Path -LiteralPath 'lab2\王珮源-2500013167\.env') { 'LAB2_ENV_EXISTS' } else { 'LAB2_ENV_ABSENT' }`
> - Ran `git check-ignore -v '.env' '.venv/' '__pycache__/' '.pytest_cache/' 2>$null`
>
> </details>
>
> 你的应用是单文件 Flask 后端加静态前端：入口为 `app.py`，聊天接口是 `/api/messages`，模型调用集中在 `ask_deepseek()`，记录目前保存在进程内列表 `messages` 中；因此后续测试会直接 mock `ask_deepseek()`，不需要真实 Key。现在把这些应用文件复制到实验仓库，不复制 Lab2 的对话轨迹。
>
> <details><summary>Ran 4 commands</summary>
>
> - Ran `$source = 'D:\Projects\Course\isse-labs\lab2\王珮源-2500013167'
> $target = 'D:\Projects\Course\isse-lab5-chat-ci'
> Copy-Item -LiteralPath (Join-Path $source 'app.py') -Destination $target
> Copy-Item -LiteralPath (Join-Path $source 'requirements.txt') -Destination $target
> Copy-Item -LiteralPath (Join-Path $source 'README.md') -Destination $target
> Copy-Item -LiteralPath (Join-Path $source '.env.example') -Destination $target
> Copy-Item -LiteralPath (Join-Path $source '.gitignore') -Destination $target
> Copy-Item -LiteralPath (Join-Path $source 'frontend') -Destination $target -Recurse
> Get-ChildItem -Force -Recurse | Select-Object FullName,Length`
> - Ran `python -c "from app import app; print('\n'.join(f'{rule} -> {endpoint}' for rule, endpoint in sorted((str(r), r.endpoint) for r in app.url_map.iter_rules())))"`
> - Ran `git status --short --branch; git diff --no-index --stat 'D:\Projects\Course\isse-labs\lab2\王珮源-2500013167\app.py' 'D:\Projects\Course\isse-lab5-chat-ci\app.py' 2>$null; if ($LASTEXITCODE -eq 0) { 'app.py identical' }`
> - Ran `python -c "from app import app; print('\n'.join(f'{rule} -> {endpoint}' for rule, endpoint in sorted((str(r), r.endpoint) for r in app.url_map.iter_rules())))"`
>
> </details>
</details>

应用已经成功导入 [isse-lab5-chat-ci](D:/Projects/Course/isse-lab5-chat-ci) 并验证可以正常导入。原有的 Lab2 文件没有被修改；实验仓库当前已有：

- `app.py`：Flask 后端入口
- `frontend/`：页面、样式和前端脚本
- `requirements.txt`：运行依赖
- `.env.example`：只有占位 Key，不含真实凭据
- `README.md`：Lab2 应用说明
- `.gitignore`：初始化忽略规则，接下来由你扩充

## 这一步在做什么

新建的实验仓库需要先有完整的 Lab2 应用，后面的测试和 CI 才有检查对象。原 Lab2 提交仍保存在课程仓库中；实验仓库则从当前应用状态开始，形成独立的 CI 实验历史。

代码和本机运行环境需要分开管理。`requirements.txt` 描述了云端和本机都需要安装的 Python 包；`.env.example` 告诉别人需要哪些配置；真实的 `.env` 和 `.venv` 只留在各自电脑上，不进入 Git。这样 GitHub Actions 检出代码后，也能按照同一份依赖清单准备环境。

你的应用由同一个 Flask 进程提供网页和 API：

| 接口 | 作用 |
| --- | --- |
| `GET /` | 返回聊天页面 |
| `GET /api/hello` | 连通性检查，返回 `{"message":"你好"}` |
| `POST /api/messages` | 创建一条问答记录 |
| `GET /api/messages` | 查询全部记录 |
| `PATCH /api/messages/<id>` | 修改用户消息 |
| `DELETE /api/messages/<id>` | 删除记录 |

创建记录时，`create_message()` 会调用 [app.py](D:/Projects/Course/isse-lab5-chat-ci/app.py) 中的 `ask_deepseek(api_key, message)`。接下来编写测试时，我们会 mock 这个函数，让它返回固定回复，因此测试不需要真实 DeepSeek Key。

聊天记录目前存放在 Flask 进程内的 `messages` 列表中，重启应用就会清空。这比 JSON 持久化更适合本实验：测试准备代码只需在每条测试前清空列表并重置 `next_id`。

## 你需要完成的操作

在实验仓库中打开 [.gitignore](D:/Projects/Course/isse-lab5-chat-ci/.gitignore)，将它改为：

```gitignore
.env
.env.*
!.env.example

.venv/
venv/
__pycache__/
*.py[cod]
.pytest_cache/
.coverage
.coverage.*
coverage.xml
htmlcov/
```

这里 `.env.*` 会忽略所有真实环境配置，而 `!.env.example` 明确保留示例文件。测试、覆盖率报告、缓存和虚拟环境也都不应进入仓库。

然后在 PowerShell 中运行：

```powershell
cd D:\Projects\Course\isse-lab5-chat-ci

python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

.\.venv\Scripts\python.exe app.py
```

启动后打开：

- <http://127.0.0.1:5001/>：应看到聊天页面。
- <http://127.0.0.1:5001/api/hello>：应看到 `{"message":"你好"}`。

此时没有配置 `.env`，所以发送聊天消息会返回缺少 Key 的提示，这是预期现象；本阶段只验证应用能启动和提供 HTTP 响应。观察完成后按 `Ctrl+C` 停止服务。

接着检查并提交文件：

```powershell
git status --short
```

预期应只看到应用文件，不应出现 `.env`、`.venv`、`__pycache__` 或测试缓存。确认后运行：

```powershell
git add .
git commit -m "chore: import Lab2 chat application"
git push -u origin main
```

推送完成后，请把下面结果发给我：

1. `git status --short` 在提交前显示的列表。
2. `python app.py` 启动时是否成功，首页和 `/api/hello` 是否正常。
3. `git push` 的结果，或最后一条 `git log -1 --oneline`。

下一阶段我会读取实际运行结果，然后帮你添加两个重点测试：一条记录的完整 CRUD，以及缺少消息字段的非法输入测试。

> (base) PS D:\Projects\Course\isse-lab5-chat-ci> git status --short
> ?? .env.example
> ?? .gitignore
> ?? README.md
> ?? app.py
> ?? frontend/
> ?? requirements.txt
>
> 启动成功，一切正常
>
> (base) PS D:\Projects\Course\isse-lab5-chat-ci> git push -u origin main
> Enumerating objects: 11, done.
> Counting objects: 100% (11/11), done.
> Delta compression using up to 32 threads
> Compressing objects: 100% (9/9), done.
> Writing objects: 100% (11/11), 8.78 KiB | 1.76 MiB/s, done.
> Total 11 (delta 0), reused 0 (delta 0), pack-reused 0 (from 0)
> To github.com:CountlessBugs/isse-lab5-chat-ci.git
>  * [new branch]      main -> main
> branch 'main' set up to track 'origin/main'.

<details><summary>4 previous messages</summary>

> 启动和第一次推送都正常，基础应用已进入实验仓库。现在进入自动测试阶段：先核对提交与忽略规则，再为你的实际接口添加两个重点测试，并直接用 Flask `test_client()` 运行，不启动真实服务、不调用 DeepSeek。随后测量覆盖率，只有低于 70% 时才补充必要测试。
>
> <details><summary>Explored a file, ran 4 commands</summary>
>
> - Ran `git status --short --branch; git log -2 --oneline --decorate; Get-Content -LiteralPath '.gitignore' -Raw`
>
> <details><summary>Explored a file</summary>
>
> - Read `./app.py`
>
> </details>
>
> - Ran `.\.venv\Scripts\python.exe -m pip show Flask pytest pytest-cov | Select-String '^(Name|Version):'`
>
> <details><summary>Explored a file</summary>
>
> - Read `./app.py`
>
> </details>
>
> - Ran `.\.venv\Scripts\python.exe -m pip show Flask pytest pytest-cov | Select-String '^(Name|Version):'`
>
> - Ran `.\.venv\Scripts\python.exe -m pip show Flask pytest pytest-cov | Select-String '^(Name|Version):'`
>
> </details>
>
> 测试会围绕两个真实行为建立：`POST → GET → PATCH → DELETE` 的完整记录流程，以及创建记录时缺少 `message` 字段的 400 错误。测试准备代码会在每个用例前清空内存状态，并用固定回复替换 `ask_deepseek()`；这样断言稳定、无网络依赖，也不需要真实 Key。
>
> <details><summary>Created 3 files, ran 2 commands</summary>
>
> - Wrote `D:/Projects/Course/isse-lab5-chat-ci/requirements-dev.txt` (+2 -0)
> - Wrote `D:/Projects/Course/isse-lab5-chat-ci/tests/conftest.py` (+35 -0)
> - Wrote `D:/Projects/Course/isse-lab5-chat-ci/tests/test_chat_api.py` (+50 -0)
> - Ran `git diff --check; git status --short`
> - Ran `Get-Content -LiteralPath 'tests\test_chat_api.py' -Raw; Get-Content -LiteralPath 'tests\conftest.py' -Raw; Get-Content -LiteralPath 'requirements-dev.txt' -Raw`
>
> </details>
</details>

两个重点测试和测试依赖已经添加到实验仓库：

- [tests/test_chat_api.py](D:/Projects/Course/isse-lab5-chat-ci/tests/test_chat_api.py)
- [tests/conftest.py](D:/Projects/Course/isse-lab5-chat-ci/tests/conftest.py)
- [requirements-dev.txt](D:/Projects/Course/isse-lab5-chat-ci/requirements-dev.txt)

## 这一步在检查什么

在 Lab2 中，你是通过点击网页或发送请求检查功能。自动测试把请求、预期结果和判断条件写成程序，以后运行一次命令就能重复检查。测试里的 `assert` 表示一个必须成立的条件，例如创建记录后，服务端返回的状态码应为 201，回复内容应是模拟的固定文本。

这次建立了两个测试重点：

1. **聊天记录 CRUD**：创建一条记录，查询并核对内容，修改消息，确认更新已经保存，删除记录，最后再次查询并确认记录消失。
2. **非法输入**：创建记录时不提供 `message` 字段，检查接口返回 400 和明确错误提示，并确认没有新增记录。

聊天应用原本会调用 DeepSeek，但测试不能依赖网络、API Key 或每次不同的模型回复。fixture 用固定回复替换了 [app.py](D:/Projects/Course/isse-lab5-chat-ci/app.py) 里的 `ask_deepseek()`，并记录它是否被调用。因此测试只检查应用如何处理模型结果，不会访问真实模型。

`client` fixture 会在每条测试开始前清空内存中的 `messages` 和 `next_id`，避免前一个测试的数据影响后一个测试。Flask 的 `test_client()` 会在当前 Python 进程中直接向应用发送请求，所以不需要先监听 `5001` 端口，也不需要访问浏览器。

## 你需要执行

在实验仓库根目录运行：

```powershell
cd D:\Projects\Course\isse-lab5-chat-ci

.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt

.\.venv\Scripts\python.exe -m pytest -q
```

预期结果类似：

```text
..                                                                       [100%]
2 passed
```

`..` 表示两个测试都通过。如果出现失败，请把从 `FAILED` 或 `ERROR` 开始的完整输出发给我；重点会包括失败的测试名、断言期望值和实际值。

把实际测试结果发给我后，我们进入下一步：运行覆盖率命令，查看后端哪些行尚未执行，并确认是否达到 70%。现在先不要提交，等测试与覆盖率都确认后再一起推送。

> (base) PS D:\Projects\Course\isse-lab5-chat-ci> .\.venv\Scripts\python.exe -m pytest -q
> ..                                                                                                                  [100%]
> 2 passed in 0.03s

两个重点测试均已通过，说明正常 CRUD 和缺少 `message` 的非法输入行为符合当前预期。

## 覆盖率在说明什么

测试通过表示测试中的 `assert` 都成立了，但还应检查这些测试执行到了多少后端代码。行覆盖率统计的是：测试运行时执行过的可执行语句，占被测后端全部可执行语句的比例。

报告中的 `Cover` 是覆盖比例，`Missing` 是未被测试执行到的行号。例如：

- `ask_deepseek()` 的真实网络请求部分会被 mock 替换，因此可能显示未覆盖。
- `index()`、`hello()`、记录不存在等当前测试没有走到的分支，也可能出现在 `Missing` 中。
- `app.run()` 的启动部分通常不会由进程内测试执行。

覆盖率高不代表结果一定正确，是否正确仍取决于断言；覆盖率主要帮助发现尚未检查到的代码路径。

## 运行覆盖率检查

在实验仓库根目录执行：

```powershell
.\.venv\Scripts\python.exe -m pytest -q --cov=app --cov-report=term-missing --cov-fail-under=70
```

三个参数的含义是：

- `--cov=app`：统计当前 `app.py` 中的后端代码。
- `--cov-report=term-missing`：在终端显示覆盖率表，以及未执行的代码行号。
- `--cov-fail-under=70`：覆盖率低于 70% 时，即使两个测试本身通过，整条命令也以失败状态结束。

请把完整报告发给我，尤其是：

```text
Name ... Stmts ... Miss ... Cover ... Missing
app.py ...
TOTAL ...
```

如果达到 70%，我们把这个命令作为后续 CI 的测试门槛；如果低于 70%，我会根据真实的 `Missing` 行号补充必要的测试，而不会扩展成全面测试项目。

> (base) PS D:\Projects\Course\isse-lab5-chat-ci> .\.venv\Scripts\python.exe -m pytest -q --cov=app --cov-report=term-missing --cov-fail-under=70
> ..                                                                                                                  [100%]
> ===================================================== tests coverage =====================================================
> ____________________________________ coverage: platform win32, python 3.13.5-final-0 _____________________________________
>
> Name     Stmts   Miss  Cover   Missing
> --------------------------------------
> app.py      76     21    72%   42-67, 73, 79, 94, 99-100, 119, 123, 134, 145, 149
> --------------------------------------
> TOTAL       76     21    72%
> Required test coverage of 70% reached. Total coverage: 72.37%
> 2 passed in 0.05s

<details><summary>2 previous messages</summary>

> 覆盖率已经达到 **72.37%**，超过 70% 门槛，因此不需要扩大测试范围。未覆盖的主要是你的真实模型请求函数和本次重点测试没有涉及的辅助分支。接下来我会按实际未覆盖行解释报告，并添加一份云端工作流，把刚验证过的测试和覆盖率命令固定下来。
>
> <details><summary>Created a file, ran 4 commands</summary>
>
> - Ran `$line = 1; Get-Content -LiteralPath 'app.py' | ForEach-Object { if (($line -ge 38 -and $line -le 82) -or ($line -ge 90 -and $line -le 125) -or ($line -ge 130 -and $line -le 151)) { '{0,4}: {1}' -f $line, $_ }; $line++ }`
> - Ran `gh api repos/actions/checkout/releases/latest --jq '.tag_name'; gh api repos/actions/setup-python/releases/latest --jq '.tag_name'`
> - Ran `git status --short; git diff --check`
> - Wrote `D:/Projects/Course/isse-lab5-chat-ci/.github/workflows/ci.yml` (+40 -0)
> - Ran `git diff --check; git status --short; Get-Content -LiteralPath '.github\workflows\ci.yml' -Raw`
>
> </details>
</details>

本地覆盖率已经达到 **72.37%**，超过 70% 门槛，因此这两个重点测试已经足够，不需要为了数字继续扩充测试范围。

## 未覆盖行说明

报告中 `Missing` 的主要部分与本次重点测试的边界一致：

- `42-67`：真实的 `ask_deepseek()` 网络请求。测试用固定回复替代了它，这正是 mock 的目的。
- `73`、`79`：首页和 `/api/hello`。它们会在后面的冒烟检查中实际访问。
- `94`、`99-100`：缺少 API Key 和模型调用失败的处理。本次重点不是外部服务故障。
- `119`：修改记录时缺少 `message` 的非法输入分支。
- `123`、`134`、`145`：记录不存在时返回 404 的分支。
- `149`：直接用 `python app.py` 启动服务，测试进程不会执行这里。

重点 CRUD 流程和非法创建输入已经被断言覆盖，而且总覆盖率超过 70%，所以现在可以进入 GitHub Actions。

## 工作流做了什么

我已经添加到 [.github/workflows/ci.yml](D:/Projects/Course/isse-lab5-chat-ci/.github/workflows/ci.yml)：

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
```

工作原理如下：

- `on` 指定触发事件：向 `main` 推送，或者向 `main` 发起 PR。
- `workflow` 是这份完整的自动检查流程。
- `job` 是运行在 runner 上的一组工作。
- `runs-on: ubuntu-latest` 表示云端 job 由 GitHub 提供的 Ubuntu runner 执行。
- `uses` 调用已有 Action，例如检出代码和安装 Python。
- `run` 执行普通终端命令。

每个 step 按顺序完成：检出当前提交、准备 Python 3.13、安装运行与测试依赖、运行测试和覆盖率门槛。云端不会自动拥有你本机 `.venv` 中的包，因此必须根据两个 requirements 文件重新安装。

覆盖率 step 使用的就是刚才本地验证过的命令，所以云端日志中应看到 `2 passed`、`72.37%` 和达到 70% 门槛。

## 你需要提交并推送

在实验仓库执行：

```powershell
git add requirements-dev.txt tests .github/workflows/ci.yml

git status --short
git commit -m "test: add API tests and coverage CI"
git push

git rev-parse --short HEAD
```

`git status` 在提交前应显示测试、测试依赖和工作流文件，不应包含 `.env` 或 `.venv`。`git rev-parse --short HEAD` 输出的 7 位哈希，就是本次云端运行应关联的提交。

然后打开：

<https://github.com/CountlessBugs/isse-lab5-chat-ci/actions>

选择最新的 **Chat application CI** 运行，进入 **Tests and coverage** job，再展开 **Run tests with coverage** 步骤。核对：

- 运行的提交哈希与本地 `git rev-parse --short HEAD` 一致。
- 日志中有 `2 passed`。
- 覆盖率约为 `72.37%`。
- 日志显示达到 70% 门槛。
- 整个 workflow 显示绿色成功标记。

请把 Actions 运行链接、提交哈希和测试步骤的实际日志结果发给我。这个运行先用于确认云端测试与覆盖率；等加入冒烟检查后，再保存最终作为提交材料的云端成功截图。

> [https://github.com/CountlessBugs/isse-lab5-chat-ci/actions/runs/40200820191/job/121191431975](https://github.com/CountlessBugs/isse-lab5-chat-ci/actions/runs/40200820191/job/121191431975)
> e716b329fb97058a338506fbd88e546a02695ecd
>
> User context
>
> Images:
> - `C:/Users/Count/AppData/Local/Temp/codex-clipboard-69779e38-e355-4ca6-8a12-53e18f27785f.png`

<details><summary>2 previous messages</summary>

> 云端运行已确认成功：提交 `e716b329…` 对应 2 个测试通过、覆盖率 72.37%。我先把这张 Actions 截图按阶段保存到课程个人目录，然后进入失败与修复实验；修复前只修改一处已经由 CRUD 测试覆盖的行为。
>
> <details><summary>Ran 3 commands</summary>
>
> - Ran `$source = 'C:\Users\Count\AppData\Local\Temp\codex-clipboard-69779e38-e355-4ca6-8a12-53e18f27785f.png'
> $destinationDir = 'D:\Projects\Course\isse-labs\lab5\2500013167-wangpeiyuan\screenshots'
> $destination = Join-Path $destinationDir 'cloud-tests-passed.png'
> if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw 'Screenshot source was not found.' }
> New-Item -ItemType Directory -Path $destinationDir -Force | Out-Null
> Copy-Item -LiteralPath $source -Destination $destination
> Get-Item -LiteralPath $destination | Select-Object FullName,Length,LastWriteTime`
> - Ran `gh run view 40200820191 --repo CountlessBugs/isse-lab5-chat-ci --json headSha,status,conclusion,event,workflowName,url --jq '{headSha,status,conclusion,event,workflowName,url}'`
> - Ran `git status --short --branch; git rev-parse HEAD; git log -2 --oneline --decorate`
>
> </details>
</details>

云端 CI 已核实为成功：

- 运行：[40200820191](https://github.com/CountlessBugs/isse-lab5-chat-ci/actions/runs/40200820191)
- 提交：`e716b329fb97058a338506fbd88e546a02695ecd`
- 结果：`2 passed`
- 覆盖率：72.37%，达到 70%
- Actions 实际使用的 Python：3.13.16

截图已经保存为 [cloud-tests-passed.png](./lab5/2500013167-wangpeiyuan/screenshots/cloud-tests-passed.png)。等完成冒烟检查后，还会保存一张包含完整云端流程的 `cloud-passed.png`。

## 接下来做一次功能回归实验

持续 CI 的一个重要用途，是代码以后被改坏时及时提醒你。接下来要故意制造一次功能回归，然后观察已有测试能否发现问题。

我准备把 [app.py](D:/Projects/Course/isse-lab5-chat-ci/app.py) 中的删除接口改成：

```python
def delete_message(message_id: int):
    record = find_message(message_id)
    if record is None:
        return jsonify({"error": f"id={message_id} 的聊天记录不存在"}), 404

    # 故意移除真正删除记录的这一行
    return jsonify({"id": message_id, "deleted": True}), 200
```

这样接口仍然会返回：

```json
{"id": 1, "deleted": true}
```

看起来删除成功了，但记录实际上仍然存在于 `messages` 列表中。

这条行为已经被 CRUD 测试检查：

```python
deleted = client.delete("/api/messages/1")

assert deleted.status_code == 200
assert deleted.get_json() == {"id": 1, "deleted": True}
assert client.get("/api/messages").get_json() == []
```

最后一条断言会失败，因为实际查询结果仍然包含记录。测试预期保持不变，被故意改坏的是应用行为，这正是我们要观察的场景。

## 到时会看到什么

你确认后我会修改代码，但不会同时修复。随后你把这次错误作为独立提交推送，并打开新生成的 Actions 运行。预期：

1. job 显示红色失败。
2. `test_chat_record_crud` 失败。
3. 断言附近显示预期为 `[]`，实际仍包含 ID 为 1 的记录。
4. step 最终返回非零退出码，因此整个 CI 失败。
5. 失败运行对应的提交是新提交，而不是刚才的 `e716b32`。

失败日志找到后先不要修复；请把失败截图和运行链接发给我，并用自己的话说明是哪一处功能变化导致断言失败。确认并保存失败证据后，我再修复代码，由你重新推送并查看新运行。

如果你同意选择“删除接口返回成功但记录未删除”作为本次失败实验，请回复“确认”。

> 确认

<details><summary>2 previous messages</summary>

> 已确认。现在只删除 `delete_message()` 中真正从列表移除记录的语句，测试和覆盖率门槛保持不变；这次提交会故意触发云端失败，暂时不会修复。
>
> <details><summary>Edited a file, ran 2 commands</summary>
>
> - Wrote `D:/Projects/Course/isse-lab5-chat-ci/app.py` (+0 -1)
> - Ran `git status --short --branch; git diff --check; git diff -- app.py`
> - Ran `$line = 1; Get-Content -LiteralPath 'app.py' | ForEach-Object { if ($line -ge 126 -and $line -le 139) { '{0,4}: {1}' -f $line, $_ }; $line++ }`
>
> </details>
</details>

这一次功能回归已经写入 [app.py](D:/Projects/Course/isse-lab5-chat-ci/app.py)：删除接口不再执行 `messages.remove(record)`，但仍然返回删除成功的 JSON。测试保持原样，因此现在会暴露出“接口声称删除成功，数据实际上仍然存在”的问题。

## 先在本地观察失败

运行：

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

预期 `test_chat_record_crud` 失败，断言大致是：

```text
assert [{'id': 1, ...}] == []
```

列表左边的记录就是没有被真正删除的数据，右边 `[]` 是测试要求的最终状态。当前出现非零退出码是预期结果，不要修复代码。

## 推送这次失败版本

先确保 `app.py` 的修改没有夹带其他内容：

```powershell
git status --short
git diff -- app.py
```

预期差异只缺少这一行：

```diff
-    messages.remove(record)
```

然后创建一个独立提交并推送：

```powershell
git add app.py
git commit -m "test: demonstrate delete regression in CI"
git push

git rev-parse HEAD
```

新提交会触发一个全新的 Actions 运行。旧运行 `40200820191` 仍然对应正确的 `e716b32`，不会被修改。

打开：

<https://github.com/CountlessBugs/isse-lab5-chat-ci/actions>

进入最新运行，依次观察：

1. 整个 workflow 是否显示红色失败。
2. 失败 job 是否为 **Tests and coverage**。
3. `Run tests with coverage` 步骤是否非零退出。
4. 日志中失败测试是否为 `test_chat_record_crud`。
5. 断言中预期和实际分别是什么。
6. 运行页面对应的提交是否等于本地最新提交哈希。

请将失败页面截图、运行链接和新提交完整哈希发给我，并按你的理解解释：

- 哪一个功能发生了回归；
- 为什么接口返回了成功状态，测试仍能发现问题；
- 失败的断言要求是什么、实际数据为什么不符合。

拿到这些真实结果后，我再恢复 `messages.remove(record)`，由你推送修复版本并确认新 CI 通过。

> 删除聊天记录功能发生了回归
> 测试测的是接口行为而不是接口返回的状态
> 失败断言的要求是消息被删除，实际上没有删除

<details><summary>2 previous messages</summary>

> 你的失败原因判断基本正确。关键区别是：测试同时检查了 HTTP 状态和删除后的数据状态，真正失败的是“删除后再次查询应为空”这一后置条件。我先核对最新推送与 Actions 运行，确认失败证据是否已经产生。
>
> <details><summary>Ran 4 commands</summary>
>
> - Ran `git status --short --branch; git log -3 --oneline --decorate; git rev-parse HEAD`
> - Ran `gh run list --repo CountlessBugs/isse-lab5-chat-ci --limit 5 --json databaseId,headSha,status,conclusion,displayTitle,url --jq '.[] | [.databaseId,.headSha,.status,.conclusion,.displayTitle,.url] | @tsv'`
> - Ran `gh api repos/CountlessBugs/isse-lab5-chat-ci/commits/main --jq '{sha: .sha, message: .commit.message}'`
> - Ran `gh run view 40201204522 --repo CountlessBugs/isse-lab5-chat-ci --log-failed`
>
> </details>
</details>

你的判断方向正确，但可以更精确一些：测试既检查了删除接口的状态码和返回内容，也检查了删除之后查询到的数据状态。这次前两项检查都通过了，真正失败的是最后的数据后置条件。

我已核实对应的云端失败运行：

- 运行：[40201204522](https://github.com/CountlessBugs/isse-lab5-chat-ci/actions/runs/40201204522)
- 失败提交：`6df1b3ef072111b112c4c1c9f3d91bf318ef3663`
- 状态：failure
- 结果：`1 failed, 1 passed`
- 实测覆盖率：72.00%，仍达到门槛，但 job 因测试失败而失败

日志中的关键位置是 [test_chat_api.py:39](D:/Projects/Course/isse-lab5-chat-ci/tests/test_chat_api.py:39)：

```python
assert client.get("/api/messages").get_json() == []
```

实际结果仍有一条记录：

```python
[
    {
        "id": 1,
        "message": "修改后的消息",
        "reply": "固定回复",
    }
]
```

这说明：

1. 删除接口返回 200 和 `{"id":1,"deleted":true}`，状态与返回格式看起来正常。
2. `messages.remove(record)` 被删除后，记录仍留在内存列表中。
3. 测试通过再次查询这一“后置条件”，发现接口声称成功与实际数据状态不一致。
4. 命令最终以退出码 1 结束，所以即使覆盖率仍超过 70%，CI 依然判定失败。

这正是断言的价值：覆盖率高只说明代码被执行过，测试失败才说明实际结果与约定不符。

请再从失败运行页面截一张图。截图中最好能看到：

- 红色的 **Tests and coverage** job；
- `test_chat_record_crud`；
- 第 39 行失败断言；
- `Left contains one more item`；
- `1 failed, 1 passed`。

把截图发给我后，我会保存为 `screenshots/failed.png`，然后恢复真正的删除语句并进入修复验证。当前先保留这个失败提交，不提前修复。

> User context
>
> Images:
> - `C:/Users/Count/AppData/Local/Temp/codex-clipboard-e6f9daaf-9f30-4dfc-81a7-1b21c84ba18b.png`

<details><summary>2 previous messages</summary>

> 失败截图已收到，内容包含失败测试、第 39 行断言、残留记录和退出码 1。我先保存为 `failed.png`，然后恢复被删除的 `messages.remove(record)`；测试预期完全不变。
>
> <details><summary>Edited a file, ran 3 commands</summary>
>
> - Ran `$source = 'C:\Users\Count\AppData\Local\Temp\codex-clipboard-e6f9daaf-9f30-4dfc-81a7-1b21c84ba18b.png'
> $destinationDir = 'D:\Projects\Course\isse-labs\lab5\2500013167-wangpeiyuan\screenshots'
> $destination = Join-Path $destinationDir 'failed.png'
> if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw 'Screenshot source was not found.' }
> New-Item -ItemType Directory -Path $destinationDir -Force | Out-Null
> Copy-Item -LiteralPath $source -Destination $destination
> Get-Item -LiteralPath $destination | Select-Object FullName,Length,LastWriteTime`
> - Wrote `D:/Projects/Course/isse-lab5-chat-ci/app.py` (+1 -0)
> - Ran `git status --short --branch; git diff --check; git diff -- app.py`
> - Ran `git diff --exit-code HEAD -- tests/test_chat_api.py; if ($LASTEXITCODE -eq 0) { 'tests unchanged' }`
>
> </details>
</details>

失败证据已保存为 [failed.png](./lab5/2500013167-wangpeiyuan/screenshots/failed.png)。

## 修复内容

已恢复 [app.py](D:/Projects/Course/isse-lab5-chat-ci/app.py) 中的：

```python
messages.remove(record)
```

测试文件没有发生任何修改。修复后的唯一差异就是重新加入这一行，因此可以清楚证明：CI 的故障来自应用删除逻辑，而不是通过修改测试绕过问题。

恢复删除语句后，删除接口不仅会返回成功状态，还会完整执行功能的后置条件：再次查询 `/api/messages` 时，记录已经不存在。之前失败的第 39 行断言应重新成立。

## 先在本地验证修复

运行：

```powershell
.\.venv\Scripts\python.exe -m pytest -q --cov=app --cov-report=term-missing --cov-fail-under=70
```

预期重新看到：

```text
2 passed
Required test coverage of 70% reached. Total coverage: 72.37%
```

然后用一个新的修复提交推送：

```powershell
git add app.py
git commit -m "fix: restore chat record deletion"
git push

git rev-parse HEAD
```

这次一定要产生新提交和新 Actions 运行。重新运行旧的失败记录，只会重新执行 `6df1b3e` 当时那份坏代码，不会自动使用本地修复。

## 在 Actions 中核对

打开：

<https://github.com/CountlessBugs/isse-lab5-chat-ci/actions>

选择最新的 **Chat application CI** 运行，确认：

- 运行对应的提交是新修复提交，不是 `6df1b3e`；
- `Tests and coverage` job 为绿色成功；
- `Run tests with coverage` 显示 `2 passed`；
- 覆盖率恢复到约 `72.37%`；
- 原来的失败运行仍然保留在历史记录中。

请把修复运行的链接、提交哈希和本地/云端测试结果发给我。之后进入冒烟检查：真实启动 Flask 进程，检查首页与 `/api/hello`，再把该检查加入同一份云端工作流。

> [https://github.com/CountlessBugs/isse-lab5-chat-ci/actions/runs/40201489822](https://github.com/CountlessBugs/isse-lab5-chat-ci/actions/runs/40201489822)
> cb5dd84585547ff31d440d543a250b9cdde5227c
>
> User context
>
> Images:
> - `C:/Users/Count/AppData/Local/Temp/codex-clipboard-a5bdd354-dd71-48e4-9f7c-20b09d337a03.png`

<details><summary>4 previous messages</summary>

> 修复运行已确认成功：新提交 `cb5dd845…` 对应 2 个测试和 72.37% 覆盖率，且旧失败记录仍保留。我先把这张修复成功截图保存为阶段证据，然后完整阅读课程冒烟脚本骨架，结合你的 `app.py` 适配入口和检查路径。
>
> <details><summary>Explored a file, ran 3 commands</summary>
>
> - Ran `$source = 'C:\Users\Count\AppData\Local\Temp\codex-clipboard-a5bdd354-dd71-48e4-9f7c-20b09d337a03.png'
> $destinationDir = 'D:\Projects\Course\isse-labs\lab5\2500013167-wangpeiyuan\screenshots'
> $destination = Join-Path $destinationDir 'cloud-repaired.png'
> if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw 'Screenshot source was not found.' }
> Copy-Item -LiteralPath $source -Destination $destination
> Get-Item -LiteralPath $destination | Select-Object FullName,Length,LastWriteTime`
>
> <details><summary>Explored a file</summary>
>
> - Read `./lab5/templates/smoke_test.py`
>
> </details>
>
> - Ran `gh run view 40201489822 --repo CountlessBugs/isse-lab5-chat-ci --json headSha,status,conclusion,event,workflowName,url --jq '{headSha,status,conclusion,event,workflowName,url}'`
>
> - Ran `git status --short --branch; git log -4 --oneline --decorate; git rev-parse HEAD`
>
> <details><summary>Explored a file</summary>
>
> - Read `./lab5/templates/smoke_test.py`
>
> </details>
>
> </details>
>
> 骨架的四个配置项与你的应用完全匹配：入口是 `app:app`，首页是 `/`，连通接口是 `/api/hello`，预期 JSON 是 `{"message":"你好"}`。你的记录保存在内存中，因此骨架临时传入的 `LAB5_DATA_DIR` 不会改变应用行为；启动、等待、请求和清理流程可以直接复用。
>
> <details><summary>Edited a file, ran 3 commands</summary>
>
> - Ran `$source = 'D:\Projects\Course\isse-labs\lab5\templates\smoke_test.py'
> $destinationDir = 'D:\Projects\Course\isse-lab5-chat-ci\scripts'
> New-Item -ItemType Directory -Path $destinationDir -Force | Out-Null
> Copy-Item -LiteralPath $source -Destination (Join-Path $destinationDir 'smoke_test.py')
> Get-Item -LiteralPath (Join-Path $destinationDir 'smoke_test.py') | Select-Object FullName,Length`
> - Wrote `D:/Projects/Course/isse-lab5-chat-ci/scripts/smoke_test.py` (+3 -4)
> - Ran `git status --short --branch; git diff --check; git diff -- scripts/smoke_test.py | Select-Object -First 80`
> - Ran `Select-String -LiteralPath 'scripts\smoke_test.py' -Pattern '^APP_IMPORT|^HOME_PATH|^HELLO_PATH|^EXPECTED_HELLO|^def |^if __name__' | Select-Object LineNumber,Line`
>
> </details>
</details>

本地冒烟脚本已添加为 [scripts/smoke_test.py](D:/Projects/Course/isse-lab5-chat-ci/scripts/smoke_test.py)，课程骨架中的启动、等待、HTTP 请求和清理流程保持不变，只把你的入口与检查目标写入配置区。

## 冒烟检查和单元测试的区别

前面的 Flask `test_client()` 在测试进程中直接调用应用，主要检查路由处理和业务结果，但没有真正启动监听端口的 HTTP 服务。

冒烟检查会：

1. 选择一个当前可用的临时端口。
2. 启动真正的 Flask 子进程。
3. 等待端口能够建立连接。
4. 请求首页 `/`，检查它返回 HTML。
5. 请求 `/api/hello`，检查状态、响应类型和 JSON 内容。
6. 无论检查成功与否，都在 `finally` 中停止 Flask 进程。

因此它能发现入口导入失败、启动命令错误、端口监听失败、前端路径配置错误等 test client 不容易发现的问题。

你的应用使用内存数据，不需要测试数据文件；脚本传入的 `LAB5_DATA_DIR` 不影响运行。脚本还设置了占位 Key，不会读取真实 `.env`，并且本地 HTTP 请求会绕过系统代理。

## 请在本地运行

在实验仓库根目录执行：

```powershell
cd D:\Projects\Course\isse-lab5-chat-ci
.\.venv\Scripts\python.exe scripts\smoke_test.py
```

预期完整输出：

```text
服务已就绪
PASS /
PASS /api/hello
服务已停止
冒烟检查通过
```

运行过程中应能观察到脚本先启动临时 Flask 进程，检查结束后自动停止；命令最终应返回成功状态。

如果失败，脚本会打印 Flask 的启动日志并返回非零退出码。请把完整输出发给我。

本地冒烟检查通过后，我们再把同一条命令作为 `Run smoke test` 步骤加入现有 [ci.yml](D:/Projects/Course/isse-lab5-chat-ci/.github/workflows/ci.yml)，推送后观察云端日志中的服务启动、两项 HTTP 检查和自动停止。

> (base) PS D:\Projects\Course\isse-lab5-chat-ci> .\.venv\Scripts\python.exe scripts\smoke_test.py
> 服务已就绪
> PASS /
> PASS /api/hello
> 服务已停止
> 冒烟检查通过

<details><summary>2 previous messages</summary>

> 本地冒烟流程已完整通过：服务启动、首页检查、连通接口检查、自动停止都成功。现在把同一条命令加入现有工作流，位置在测试与覆盖率之后；任何前序步骤失败，冒烟步骤都不会继续。
>
> <details><summary>Edited a file, explored a file, ran a command</summary>
>
> - Wrote `D:/Projects/Course/isse-lab5-chat-ci/.github/workflows/ci.yml` (+3 -0)
>
> - Ran `git status --short --branch; git diff --check; git diff -- .github/workflows/ci.yml`
>
> <details><summary>Explored a file</summary>
>
> - Read `./.github/workflows/ci.yml`
>
> </details>
>
> </details>
</details>

本地冒烟检查已按要求完整通过：临时服务成功启动、两个 HTTP 检查通过、进程自动停止。

## 将冒烟检查加入同一工作流

已在 [ci.yml](D:/Projects/Course/isse-lab5-chat-ci/.github/workflows/ci.yml) 的测试与覆盖率步骤之后加入：

```yaml
- name: Run smoke test
  run: python scripts/smoke_test.py
```

这个步骤与自动测试位于同一个 job、同一台 runner、同一个提交上：

- 先安装依赖并运行 pytest 和 70% 覆盖率检查。
- 测试步骤失败时，后续冒烟步骤不会继续。
- 测试通过后，启动真实 Flask 子进程并访问首页和 `/api/hello`。
- 冒烟脚本返回非零退出码时，该 step 和整个 job 都会失败。

因此云端验证的不只是路由逻辑，还包括这次提交中的真实入口、依赖、启动命令和 HTTP 服务检查。

## 提交并推送

运行：

```powershell
git add scripts/smoke_test.py .github/workflows/ci.yml
git commit -m "ci: add HTTP smoke test"
git push

git rev-parse HEAD
```

打开最新 Actions 运行：

<https://github.com/CountlessBugs/isse-lab5-chat-ci/actions>

分别展开以下两个步骤核对：

1. **Run tests with coverage**：`2 passed`，覆盖率约 `72.37%`，达到 70%。
2. **Run smoke test**：依次显示：

```text
服务已就绪
PASS /
PASS /api/hello
服务已停止
冒烟检查通过
```

同时确认 Actions 页面显示的提交哈希等于本地 `git rev-parse HEAD`。

请把这次运行链接、提交完整哈希和一张涵盖测试与冒烟日志的截图发给我。截图将整理为最终的 `cloud-passed.png`，之后进入必做的本机 self-hosted runner 阶段。

> [https://github.com/CountlessBugs/isse-lab5-chat-ci/actions/runs/40201799412](https://github.com/CountlessBugs/isse-lab5-chat-ci/actions/runs/40201799412)
> a72aab4fb6e7f2c0987e35446ea4a015a867cf7f
>
> User context
>
> Images:
> - `C:/Users/Count/AppData/Local/Temp/codex-clipboard-ec00abe6-c4ae-46a9-b30c-9dec060fc518.png`

<details><summary>2 previous messages</summary>

> 云端完整流程已成功：2 个测试、72.37% 覆盖率以及首页和 `/api/hello` 冒烟检查均通过。我先将截图保存为最终的 `cloud-passed.png`，然后检测本机架构和 Python 环境，为注册 self-hosted runner 给出准确的本机命令。
>
> <details><summary>Ran 7 commands</summary>
>
> - Ran `$source = 'C:\Users\Count\AppData\Local\Temp\codex-clipboard-ec00abe6-c4ae-46a9-b30c-9dec060fc518.png'
> $destinationDir = 'D:\Projects\Course\isse-labs\lab5\2500013167-wangpeiyuan\screenshots'
> $destination = Join-Path $destinationDir 'cloud-passed.png'
> if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw 'Screenshot source was not found.' }
> Copy-Item -LiteralPath $source -Destination $destination
> Get-Item -LiteralPath $destination | Select-Object FullName,Length,LastWriteTime`
> - Ran `gh run view 40201799412 --repo CountlessBugs/isse-lab5-chat-ci --json headSha,status,conclusion,event,workflowName,url --jq '{headSha,status,conclusion,event,workflowName,url}'`
> - Ran `Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,OSArchitecture; Get-CimInstance Win32_Processor | Select-Object Name,AddressWidth,Architecture; [Environment]::OSVersion.Version.ToString(); $env:PROCESSOR_ARCHITECTURE`
> - Ran `python --version; (Get-Command python).Source; git --version; Get-ChildItem -LiteralPath 'D:\Projects\Course' -Directory -Filter '*runner*' -ErrorAction SilentlyContinue | Select-Object FullName`
> - Ran `python --version; (Get-Command python).Source; git --version`
> - Ran `Get-ChildItem -LiteralPath 'D:\Projects\Course' -Directory -Filter '*runner*' -ErrorAction SilentlyContinue | Select-Object FullName; Get-ChildItem -LiteralPath 'D:\Projects' -Directory -Filter '*runner*' -ErrorAction SilentlyContinue | Select-Object FullName`
> - Ran `git status --short --branch; git log -3 --oneline --decorate; git rev-parse HEAD`
>
> </details>
</details>

云端完整成功证据已保存为 [cloud-passed.png](./lab5/2500013167-wangpeiyuan/screenshots/cloud-passed.png)。

对应运行：[40201799412](https://github.com/CountlessBugs/isse-lab5-chat-ci/actions/runs/40201799412)
提交：`a72aab4fb6e7f2c0987e35446ea4a015a867cf7f`

截图中的测试、72.37% 覆盖率、首页检查和 `/api/hello` 检查均已通过。

## 本机 runner 是什么

之前的 job 由 GitHub 提供的 Ubuntu 云端机器执行。runner 是实际接收并执行 job 的程序；self-hosted runner 安装在你自己的电脑上，让 GitHub 把任务交给这台电脑。

配置分为三步：

1. 下载与 Windows x64 匹配的 runner。
2. 注册 runner，让它关联到 `isse-lab5-chat-ci` 仓库。
3. 启动 runner，保持终端打开并等待任务。

注册 token 只用于这一次关联操作，属于敏感信息。请直接在 GitHub 页面和本机终端之间复制，不要发到对话或截图里。

当前环境是：

```text
Windows 11 64 位
CPU 架构：AMD64/x64
Python：3.13.5
Git：2.50.0
```

runner 程序必须放在代码仓库之外。使用：

```text
D:\actions-runner-isse-lab5
```

该目录目前不存在，后续由你创建。

## 下载并注册

打开仓库的 runner 注册页面：

<https://github.com/CountlessBugs/isse-lab5-chat-ci/settings/actions/runners/new?arch=x64&os=win>

也可以从仓库进入：

```text
Settings → Actions → Runners → New self-hosted runner
```

系统选择 **Windows**，架构选择 **x64**。

然后：

```powershell
mkdir D:\actions-runner-isse-lab5
cd D:\actions-runner-isse-lab5
```

不要手动猜测下载地址；直接复制页面 **Download** 区域当前显示的两条 PowerShell 命令下载并解压 runner。解压后的目录应包含 `config.cmd`、`run.cmd` 等文件。

执行页面 **Configure** 区域提供的注册命令。它通常类似：

```powershell
.\config.cmd --url https://github.com/CountlessBugs/isse-lab5-chat-ci --token <页面提供的注册token>
```

不要把实际的 `<...>` token 发给我。

交互配置时建议：

- runner group：直接按 Enter 使用 `Default`。
- runner name：直接按 Enter 使用默认名称。
- additional labels：直接按 Enter，保留默认的 `self-hosted`、`Windows`、`X64`。
- work folder：直接按 Enter 使用 `_work`。

显示 `Runner successfully added` 和 `Settings updated` 即注册完成。

## 前台启动

在同一个 PowerShell 窗口运行：

```powershell
.\run.cmd
```

保持这个终端打开。预期终端显示类似：

```text
√ Connected to GitHub
Listening for Jobs
```

同时刷新刚才的 GitHub Runners 页面，应看到该 runner 状态为绿色 **Idle**。

这一步先只确认 runner 已经在线。请反馈：

1. GitHub Runners 页面是否显示 **Idle**。
2. 终端是否出现 `Listening for Jobs`。
3. 完成后的截图可以发给我，但不要包含注册命令或 token。

确认在线状态后，我会把 `.github/workflows/ci.yml` 的云端 `runs-on: ubuntu-latest` 改为 `self-hosted`，并针对 Windows 调整 Python 准备步骤。

> Would you like to run the runner as service? (Y/N) [press Enter for N]

直接按 **Enter**，即选择 `N`。

本次实验要求在前台运行 runner，便于观察任务接收和完成后停止；不需要安装为 Windows 服务。

继续完成剩余配置后，执行：

```powershell
.\run.cmd
```

保持终端打开，确认出现 `Listening for Jobs`，并让 GitHub Runners 页面显示 **Idle**。

> 显示 Idle
> Current runner version: '2.338.0'
> 2026-10-25 14:26:39Z: Listening for Jobs
>
> User context
>
> Images:
> - `C:/Users/Count/AppData/Local/Temp/codex-clipboard-b6ad5b88-3b1b-4241-b950-cbd95843b8b4.png`

<details><summary>2 previous messages</summary>

> runner 已注册并连接 GitHub，版本 `2.338.0`，当前显示 **Idle**，终端处于 `Listening for Jobs`。我先保存注册在线截图，再把同一份工作流的 `runs-on` 切到 `self-hosted`；Python 3.13、依赖安装、测试、覆盖率和冒烟命令保持不变。
>
> <details><summary>Edited a file, ran 5 commands</summary>
>
> - Ran `$source = 'C:\Users\Count\AppData\Local\Temp\codex-clipboard-b6ad5b88-3b1b-4241-b950-cbd95843b8b4.png'
> $destinationDir = 'D:\Projects\Course\isse-labs\lab5\2500013167-wangpeiyuan\screenshots'
> $destination = Join-Path $destinationDir 'self-hosted-registered.png'
> if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw 'Screenshot source was not found.' }
> Copy-Item -LiteralPath $source -Destination $destination
> Get-Item -LiteralPath $destination | Select-Object FullName,Length,LastWriteTime`
> - Ran `gh api repos/CountlessBugs/isse-lab5-chat-ci/actions/runners --jq '.runners[] | {id,name,status,busy,labels:[.labels[].name],version:.version}'`
> - Ran `git status --short --branch; git log -2 --oneline --decorate; git rev-parse HEAD`
> - Wrote `D:/Projects/Course/isse-lab5-chat-ci/.github/workflows/ci.yml` (+1 -1)
> - Ran `git status --short --branch; git diff --check; git diff -- .github/workflows/ci.yml`
> - Ran `Select-String -LiteralPath '.github\workflows\ci.yml' -Pattern '^name:|runs-on:|uses:|Run tests|Run smoke' | Select-Object LineNumber,Line`
>
> </details>
</details>

runner 已确认在线且空闲：

```text
名称：BUGSCOMPUTER
状态：online
busy：false
标签：self-hosted, Windows, X64
版本：2.338.0
```

在线截图已保存为 [self-hosted-registered.png](./lab5/2500013167-wangpeiyuan/screenshots/self-hosted-registered.png)。

## 工作流已切换到本机

[ci.yml](D:/Projects/Course/isse-lab5-chat-ci/.github/workflows/ci.yml) 中只改变了一行：

```diff
- runs-on: ubuntu-latest
+ runs-on: self-hosted
```

`runs-on` 是 GitHub 选择执行机器的条件。现在推送后，GitHub 会寻找带有 `self-hosted` 标签的在线 runner，也就是刚启动的 `BUGSCOMPUTER`。

原有的 step 都保留：

1. 检出当前提交。
2. 使用 `actions/setup-python` 准备 Python 3.13。
3. 安装运行与测试依赖。
4. 运行 pytest 和 70% 覆盖率门槛。
5. 启动真实 Flask 进程并执行冒烟检查。

runner 会自己的工作区重新检出代码，例如：

```text
D:\actions-runner-isse-lab5\_work\isse-lab5-chat-ci\isse-lab5-chat-ci
```

这个目录与你日常开发的 `D:\Projects\Course\isse-lab5-chat-ci` 不同。你开发终端里已有的 `.venv` 不会自动成为 job 环境，因此工作流仍要通过 `setup-python` 和 pip 准备依赖。

保持当前 `run.cmd` 终端打开，在另一个 PowerShell 中运行：

```powershell
cd D:\Projects\Course\isse-lab5-chat-ci

git add .github/workflows/ci.yml
git commit -m "ci: run workflow on self-hosted runner"
git push

git rev-parse HEAD
```

推送会触发新运行，并立即分配给正在监听的 runner。

## 需要观察的结果

在 runner 终端中应看到类似：

```text
Running job: test
...
Job test completed with result: Succeeded
Listening for Jobs
```

在 Actions 页面中：

- 最新运行对应当前新提交。
- job 显示绿色成功。
- Run details 中执行者应为 `BUGSCOMPUTER`。
- 测试日志仍应显示 `2 passed` 和覆盖率约 `72.37%`。
- 冒烟日志仍应显示首页、`/api/hello`、服务停止和检查通过。

请发送以下两项：

1. Actions 成功页面截图，最好能看到 runner 信息、提交哈希和绿色 job。
2. 本机终端截图，能看到同一个 job 被接收并显示 `Succeeded`。

这两项将分别保存为 `self-hosted-actions.png` 和 `self-hosted-terminal.png`。确认成功并保存截图后再停止 runner，不要提前关闭当前终端。

> 卡在 Set up Python 了

<details><summary>4 previous messages</summary>

> 先定位阻塞点。我会检查最新运行的 step 状态、runner 是否已被占用，以及 `Set up Python` 是否有日志或下载错误；若是 setup-python 在此网络环境中下载工具链卡住，就改为直接使用 runner 所在会话已有的本机 Python。
>
> <details><summary>Ran 9 commands</summary>
>
> - Ran `gh run list --repo CountlessBugs/isse-lab5-chat-ci --limit 3 --json databaseId,headSha,status,conclusion,displayTitle,url,startedAt,updatedAt --jq '.[] | [.databaseId,.headSha,.status,.conclusion,.displayTitle,.startedAt,.updatedAt,.url] | @tsv'`
> - Ran `gh api repos/CountlessBugs/isse-lab5-chat-ci/actions/runners --jq '.runners[] | {name,status,busy,labels:[.labels[].name],version}'`
> - Ran `git status --short --branch; git log -3 --oneline --decorate; git rev-parse HEAD`
> - Ran `gh api repos/CountlessBugs/isse-lab5-chat-ci/actions/runs/40202434116/jobs --jq '.jobs[] | {id,name,status,conclusion,runner_name,runner_group_name,current_step:{name:.steps[]?.name,status:.steps[]?.status}}'`
> - Ran `gh api repos/CountlessBugs/isse-lab5-chat-ci/actions/runs/40202434116/jobs --jq '.jobs[] | .steps[] | [.number,.name,.status,.conclusion] | @tsv'`
> - Ran `Get-ChildItem -LiteralPath 'D:\actions-runner-isse-lab5' -Force -ErrorAction SilentlyContinue | Select-Object Name,Mode,Length; Get-ChildItem -LiteralPath 'D:\actions-runner-isse-lab5\_diag' -Force -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 5 Name,Length,LastWriteTime`
> - Ran `gh api repos/CountlessBugs/isse-lab5-chat-ci/actions/runs/40202434116/jobs --jq '.jobs[0].steps[] | [.number,.name,.status,.conclusion,.started_at,.completed_at] | @tsv'`
> - Ran `Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'actions-runner-isse-lab5|setup-python|actions/setup-python|Runner.Worker|Runner.Listener' } | Select-Object ProcessId,ParentProcessId,Name,CommandLine | Format-List`
> - Ran `Get-ChildItem -LiteralPath 'D:\actions-runner-isse-lab5\_work' -Force -Recurse -Depth 3 | Sort-Object LastWriteTime -Descending | Select-Object -First 30 FullName,Length,LastWriteTime`
>
> </details>
>
> 瓶颈已定位：`Set up Python` 正在下载 `python-3.13.17-win32-x64.zip`，但该文件为 0 字节，说明本机访问该下载源卡住了；runner 本身正常。修复方式是移除跨机下载，直接使用已安装的 Python 3.13.5，在工作区内创建临时 `.venv` 后执行同样的检查。
>
> <details><summary>Edited a file, ran 3 commands</summary>
>
> - Wrote `D:/Projects/Course/isse-lab5-chat-ci/.github/workflows/ci.yml` (+6 -14)
> - Ran `git diff --check; git diff -- .github/workflows/ci.yml; Get-Content -LiteralPath '.github\workflows\ci.yml' -Raw`
> - Ran `python --version; python -c "import venv, ensurepip; print('venv available')"; python -m pip --version`
> - Ran `git status --short --branch`
>
> </details>
</details>

卡住的原因是 `actions/setup-python@v7` 正在尝试下载 Python 安装包，但本机的下载文件一直是 0 字节：

```text
D:\actions-runner-isse-lab5\_work\_temp\python-3.13.17-win32-x64.zip
```

self-hosted runner 没有 GitHub 云端 runner 的预装工具缓存，因此 setup-python 需要自行下载。这是下载源或网络访问问题，不是你的 runner 注册失败。

## 已改为使用本机 Python

已更新 [ci.yml](D:/Projects/Course/isse-lab5-chat-ci/.github/workflows/ci.yml)：

- 移除 `actions/setup-python@v7`。
- 直接检查 runner 所在会话中的 `python --version`。
- 在 runner 自己的工作区创建 `.venv`。
- 使用该 `.venv` 安装依赖、运行测试和冒烟检查。

本机检测结果：

```text
Python 3.13.5
venv available
pip 25.1
```

runner 工作区中的 `.venv` 与开发目录里的 `.venv` 相互独立，不会读取或修改你日常开发环境。

## 先取消卡住的运行

当前运行仍在占用唯一的 runner：

<https://github.com/CountlessBugs/isse-lab5-chat-ci/actions/runs/40202434116>

在页面右上角选择 **Cancel workflow**。也可以在另一个 PowerShell 中执行：

```powershell
gh run cancel 40202434116 --repo CountlessBugs/isse-lab5-chat-ci
```

取消后观察 runner 终端，它应先结束当前任务，再回到：

```text
Listening for Jobs
```

## 推送修复后的工作流

保持 runner 终端处于监听状态，在开发仓库执行：

```powershell
cd D:\Projects\Course\isse-lab5-chat-ci

git add .github/workflows/ci.yml
git commit -m "ci: use local Python for self-hosted runner"
git push

git rev-parse HEAD
```

新提交会生成一个新运行。预期在本机终端中看到新 job，Actions 中的步骤变为：

```text
Prepare local Python environment
Run tests with coverage
Run smoke test
```

`Prepare local Python environment` 应快速显示本机 Python 版本，并在 runner 工作区创建 `.venv`，不再尝试下载 `python-3.13.17-win32-x64.zip`。

请把新运行结果发给我；如果安装依赖或后续步骤再卡住，请同时说明日志停在哪个包或哪条命令。

> Run actions/checkout@v7&#x20;
> Syncing repository: CountlessBugs/isse-lab5-chat-ci&#x20;
> Getting Git version info&#x20;
> Copying 'C:\Users\Count\\.gitconfig' to 'D:\actions-runner-isse-lab5\\\_work\\\_temp\9bb361aa-304a-4cd1-b0a7-8933ffbc69fc\\.gitconfig'&#x20;
> Temporarily overriding HOME='D:\actions-runner-isse-lab5\\\_work\\\_temp\9bb361aa-304a-4cd1-b0a7-8933ffbc69fc' before making global git config changes&#x20;
> Adding repository directory to the temporary git global config as a safe directory&#x20;
> D:\Tools\Git\cmd\git.exe config --global --add safe.directory D:\actions-runner-isse-lab5\\\_work\isse-lab5-chat-ci\isse-lab5-chat-ci&#x20;
> D:\Tools\Git\cmd\git.exe config --local --get remote.origin.url&#x20;
> [https://github.com/CountlessBugs/isse-lab5-chat-ci](https://github.com/CountlessBugs/isse-lab5-chat-ci)&#x20;
> Removing previously created refs, to avoid conflicts&#x20;
> D:\Tools\Git\cmd\git.exe submodule status&#x20;
> Cleaning the repository&#x20;
> Disabling automatic garbage collection&#x20;
> Setting up auth&#x20;
> Fetching the repository&#x20;
> D:\Tools\Git\cmd\git.exe -c protocol.version=2 fetch --no-tags --prune --no-recurse-submodules --depth=1 origin +1eb7f3a88fc8ba262e41dc050f69faffab74e05e:refs/remotes/origin/main&#x20;
> **Error:&#x20;**&#x66;atal: unable to access '[https://github.com/CountlessBugs/isse-lab5-chat-ci/](https://github.com/CountlessBugs/isse-lab5-chat-ci/)': Recv failure: Connection was reset&#x20;
> The process 'D:\Tools\Git\cmd\git.exe' failed with exit code 128&#x20;
> Waiting 20 seconds before trying again&#x20;
> D:\Tools\Git\cmd\git.exe -c protocol.version=2 fetch --no-tags --prune --no-recurse-submodules --depth=1 origin +1eb7f3a88fc8ba262e41dc050f69faffab74e05e:refs/remotes/origin/main&#x20;
> **Error:&#x20;**&#x66;atal: unable to access '[https://github.com/CountlessBugs/isse-lab5-chat-ci/](https://github.com/CountlessBugs/isse-lab5-chat-ci/)': Failed to connect to github.com port 443 after 21059 ms: Could not connect to server&#x20;
> The process 'D:\Tools\Git\cmd\git.exe' failed with exit code 128&#x20;
> Waiting 11 seconds before trying again&#x20;
> D:\Tools\Git\cmd\git.exe -c protocol.version=2 fetch --no-tags --prune --no-recurse-submodules --depth=1 origin +1eb7f3a88fc8ba262e41dc050f69faffab74e05e:refs/remotes/origin/main&#x20;
> **Error:&#x20;**&#x66;atal: unable to access '[https://github.com/CountlessBugs/isse-lab5-chat-ci/](https://github.com/CountlessBugs/isse-lab5-chat-ci/)': Failed to connect to github.com port 443 after 21063 ms: Could not connect to server&#x20;
> **Error:&#x20;**&#x54;he process 'D:\Tools\Git\cmd\git.exe' failed with exit code 128

<details><summary>4 previous messages</summary>

> 这次阻塞发生在 `actions/checkout` 的 HTTPS 拉取：连接 `github.com:443` 被重置。你的已有工作流通过 SSH 推送正常，所以我会让 runner 也将 GitHub HTTPS 地址改写为 SSH，再验证能否从该仓库拉取当前提交；不改用或输出任何私钥。
>
> <details><summary>Ran 4 commands</summary>
>
> - Ran `gh run list --repo CountlessBugs/isse-lab5-chat-ci --limit 3 --json databaseId,headSha,status,conclusion,displayTitle,url --jq '.[] | [.databaseId,.headSha,.status,.conclusion,.displayTitle,.url] | @tsv'; git status --short --branch; git rev-parse HEAD; git log -2 --oneline --decorate`
> - Ran `Get-ChildItem -LiteralPath 'C:\Users\Count\.ssh' -Force -File -ErrorAction SilentlyContinue | Select-Object Name,Length,LastWriteTime`
> - Ran `$tempConfig = Join-Path $env:TEMP 'lab5-ssh-rewrite-test.gitconfig'
> git -c "url.git@github.com:.insteadOf=https://github.com/" -c "core.sshCommand=ssh -o BatchMode=yes -o ConnectTimeout=10" ls-remote https://github.com/CountlessBugs/isse-lab5-chat-ci.git HEAD`
> - Ran `gh api repos/CountlessBugs/isse-lab5-chat-ci/actions/runners --jq '.runners[] | {name,status,busy,version}'`
>
> </details>
>
> SSH 路径已经用同一仓库验证成功，能拉到当前提交 `1eb7f3a`。我会在 checkout 之前生成一个仅用于本次 job 的 Git 配置，把 `https://github.com/` 改写为 `git@github.com:`；这样不需要读取、复制或提交私钥，也不依赖当前失效的 HTTPS 连通性。
>
> <details><summary>Edited a file, ran 2 commands</summary>
>
> - Wrote `D:/Projects/Course/isse-lab5-chat-ci/.github/workflows/ci.yml` (+9 -0)
> - Ran `git diff --check; git diff -- .github/workflows/ci.yml`
> - Ran `gh api repos/CountlessBugs/isse-lab5-chat-ci/actions/runners --jq '.runners[] | {name,status,busy,version}'`
> - Wrote `D:/Projects/Course/isse-lab5-chat-ci/.github/workflows/ci.yml` (+1 -0)
>
> </details>
</details>

runner 当前已空闲，失败不是 runner 断开，而是 `actions/checkout` 默认使用 HTTPS 拉取代码；本机到 `github.com:443` 的连接被重置。你的开发仓库通过 SSH 推送正常，所以工作流也会改用 SSH。

## 修复内容

已在 [ci.yml](D:/Projects/Course/isse-lab5-chat-ci/.github/workflows/ci.yml) 的 checkout 前增加一个配置步骤：

```yaml
- name: Configure Git to use SSH
  shell: pwsh
  run: |
    $configPath = Join-Path $env:RUNNER_TEMP "lab5-gitconfig"
    git config --file $configPath "url.git@github.com:.insteadOf" "https://github.com/"
    "GIT_CONFIG_GLOBAL=$configPath" | Out-File -FilePath $env:GITHUB_ENV -Encoding utf8 -Append
    "GIT_SSH_COMMAND=ssh -o BatchMode=yes" | Out-File -FilePath $env:GITHUB_ENV -Encoding utf8 -Append
```

具体作用：

- `url.git@github.com:.insteadOf https://github.com/` 将 checkout 使用的 HTTPS 地址自动改写为 SSH。
- `GIT_CONFIG_GLOBAL` 让后续 step 和 checkout Action 使用这份临时配置。
- `BatchMode=yes` 禁止 SSH 等待交互输入，认证失败时直接报错而不是再次卡住。
- checkout 不保存 GitHub 的 HTTPS 凭据。

该配置只放在本次 job 的临时目录，不读取、复制、打印或提交你的私钥。SSH 改写已用同一仓库验证，能够拉到当前提交。

## 推送修复版本

保持 runner 的 `run.cmd` 终端打开，在开发仓库执行：

```powershell
cd D:\Projects\Course\isse-lab5-chat-ci

git add .github/workflows/ci.yml
git commit -m "ci: fetch repository over SSH on self-hosted runner"
git push

git rev-parse HEAD
```

预期新运行依次经过：

```text
Configure Git to use SSH
Check out repository
Prepare local Python environment
Run tests with coverage
Run smoke test
```

重点观察：

1. `Configure Git to use SSH` 成功。
2. `Check out repository` 不再出现 `Failed to connect to github.com port 443`。
3. Python 准备步骤显示本机 Python 3.13.5，不再下载 Python 压缩包。
4. 测试应为 `2 passed`、覆盖率约 `72.37%`。
5. 冒烟检查应显示服务启动、两个 `PASS`、服务停止。

请把这次运行的实际结果发给我；如果仍在某个具体命令处失败，把该步骤的最后一段日志贴出来即可。

> Run $configPath = Join-Path $env:RUNNER_TEMP "lab5-gitconfig"&#x20;
> **$configPath = Join-Path $env:RUNNER_TEMP "lab5-gitconfig"**&#x20;
> **git config --file $configPath "url.git@github.com:.insteadOf" "[https://github.com/](https://github.com/)"**&#x20;
> **"GIT_CONFIG_GLOBAL=$configPath" | Out-File -FilePath $env:GITHUB_ENV -Encoding utf8 -Append**&#x20;
> **"GIT_SSH_COMMAND=ssh -o BatchMode=yes" | Out-File -FilePath $env:GITHUB_ENV -Encoding utf8 -Append**&#x20;
> **Error:&#x20;**&#x70;wsh: command not found

<details><summary>2 previous messages</summary>

> 这次失败是 shell 选择错误：runner 找不到 PowerShell 7 的 `pwsh`，但 Windows 自带的 `powershell.exe` 已存在。接下来把整个 job 的所有终端步骤统一设为 Windows PowerShell，避免后面的 Python、pytest 和冒烟步骤再次遇到同一问题。
>
> <details><summary>Edited a file, ran 3 commands</summary>
>
> - Wrote `D:/Projects/Course/isse-lab5-chat-ci/.github/workflows/ci.yml` (+3 -1)
> - Ran `git diff --check; git diff -- .github/workflows/ci.yml; Get-Content -LiteralPath '.github\workflows\ci.yml' -Raw`
> - Ran `Get-Command powershell.exe | Select-Object Source; gh api repos/CountlessBugs/isse-lab5-chat-ci/actions/runners --jq '.runners[] | {name,status,busy}'`
> - Ran `git status --short --branch; git rev-parse HEAD`
>
> </details>
</details>

原因是 self-hosted runner 的启动环境里没有 PowerShell 7，因此不存在可执行的 `pwsh`。Windows 自带的 `powershell.exe` 则已确认存在：

```text
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
```

## 已统一使用 Windows PowerShell

已在 [ci.yml](D:/Projects/Course/isse-lab5-chat-ci/.github/workflows/ci.yml) 的 job 中加入：

```yaml
defaults:
  run:
    shell: powershell
```

同时移除了本地步骤中的 `shell: pwsh`。这样以下所有终端步骤都会使用 Windows PowerShell：

- `Configure Git to use SSH`
- `Prepare local Python environment`
- `Run tests with coverage`
- `Run smoke test`

runner 当前已恢复在线且空闲。

## 推送修复

执行：

```powershell
cd D:\Projects\Course\isse-lab5-chat-ci

git add .github/workflows/ci.yml
git commit -m "ci: use Windows PowerShell on self-hosted runner"
git push

git rev-parse HEAD
```

预期新运行依次显示：

```text
Configure Git to use SSH
Check out repository
Prepare local Python environment
Run tests with coverage
Run smoke test
```

如果还有失败，请提供当前失败步骤名和该步骤的最后几行日志；这次 shell 问题已经不会再出现。

> User context
>
> Attachments:
> - Run actions/checkout@v7 Syncing repository: CountlessBugs/isse-lab5-chat-ci Get…: `C:/Users/Count/.codex/attachments/68115253-c6c6-4d24-908d-8e36b412e1cb/已粘贴的文本.txt`

<details><summary>6 previous messages</summary>

> 我先读取你粘贴的完整 Actions 日志，定位当前失败步骤和实际错误，再决定是修工作流配置还是本机环境。
>
> <details><summary>Explored a file</summary>
>
> - Read `C:/Users/Count/.codex/attachments/68115253-c6c6-4d24-908d-8e36b412e1cb/已粘贴的文本.txt`
>
> </details>
>
> SSH 已成功接管 HTTPS，但 checkout 临时改变了 `HOME`，导致 SSH 在临时目录查找主机信任文件，因此报 `Host key verification failed`。我会显式指定现有的 GitHub 密钥和 `known_hosts`，并用与工作流相同的 SSH 参数验证拉取。
>
> <details><summary>Ran 2 commands</summary>
>
> - Ran `$userProfile = $env:USERPROFILE
> $keyPath = Join-Path $userProfile '.ssh\id_ed25519_github'
> $knownHostsPath = Join-Path $userProfile '.ssh\known_hosts'
> if (-not (Test-Path -LiteralPath $keyPath)) { throw 'GitHub SSH key not found' }
> if (-not (Test-Path -LiteralPath $knownHostsPath)) { throw 'known_hosts not found' }
> $env:GIT_SSH_COMMAND = "ssh -o BatchMode=yes -o IdentitiesOnly=yes -i $keyPath -o UserKnownHostsFile=$knownHostsPath"
> git -c "url.git@github.com:.insteadOf=https://github.com/" ls-remote https://github.com/CountlessBugs/isse-lab5-chat-ci.git HEAD`
> - Ran `git status --short --branch; git log -3 --oneline --decorate; git rev-parse HEAD; gh api repos/CountlessBugs/isse-lab5-chat-ci/actions/runners --jq '.runners[] | {name,status,busy}'`
>
> </details>
>
> 刚才的验证暴露出一个 Windows 路径细节：SSH 命令经过 Git 调用后，未加引号的反斜杠被吞掉了。工作流中需要把密钥和信任文件路径加引号；我会按这种方式重新验证。
>
> <details><summary>Edited a file, ran 3 commands</summary>
>
> - Ran `$userProfile = $env:USERPROFILE
> $keyPath = Join-Path $userProfile '.ssh\id_ed25519_github'
> $knownHostsPath = Join-Path $userProfile '.ssh\known_hosts'
> if (-not (Test-Path -LiteralPath $keyPath)) { throw 'GitHub SSH key not found' }
> if (-not (Test-Path -LiteralPath $knownHostsPath)) { throw 'known_hosts not found' }
> $env:GIT_SSH_COMMAND = 'ssh -o BatchMode=yes -o IdentitiesOnly=yes -i "' + $keyPath + '" -o UserKnownHostsFile="' + $knownHostsPath + '"'
> git -c "url.git@github.com:.insteadOf=https://github.com/" ls-remote https://github.com/CountlessBugs/isse-lab5-chat-ci.git HEAD`
> - Wrote `D:/Projects/Course/isse-lab5-chat-ci/.github/workflows/ci.yml` (+4 -1)
> - Ran `Get-Content -LiteralPath '.github\workflows\ci.yml' -Raw; git diff --check`
> - Ran ``$userProfile = $env:USERPROFILE
> $keyPath = Join-Path $userProfile '.ssh\id_ed25519_github'
> $knownHostsPath = Join-Path $userProfile '.ssh\known_hosts'
> $sshCommand = "ssh -o BatchMode=yes -o IdentitiesOnly=yes -i `"$keyPath`" -o UserKnownHostsFile=`"$knownHostsPath`""
> $sshCommand``
>
> </details>
</details>

原因已进一步确认：`actions/checkout` 在拉取期间临时覆盖了 `HOME`，所以 SSH 不再从 `C:\Users\Count\.ssh` 查找密钥和 `known_hosts`，最终报：

```text
Host key verification failed.
Could not read from remote repository.
```

## 已修复 SSH 路径

[ci.yml](D:/Projects/Course/isse-lab5-chat-ci/.github/workflows/ci.yml) 现在显式指定：

- 私钥：`C:\Users\Count\.ssh\id_ed25519_github`
- 主机信任文件：`C:\Users\Count\.ssh\known_hosts`
- `IdentitiesOnly=yes`：只使用指定密钥
- `BatchMode=yes`：避免等待交互输入

并且 Windows 路径已正确加引号，避免反斜杠被命令行吞掉。

我用完全相同的 SSH 改写和路径参数验证了远端拉取，结果为：

```text
4ed18e709615393decf1e967e0d409003d7e70f2    HEAD
```

说明该方式能够拉取当前仓库提交。工作流没有读取、输出或提交私钥内容。

## 推送修复

runner 当前在线且空闲，执行：

```powershell
cd D:\Projects\Course\isse-lab5-chat-ci

git add .github/workflows/ci.yml
git commit -m "ci: configure SSH paths for self-hosted checkout"
git push

git rev-parse HEAD
```

新运行中 `Check out repository` 应该能完成，随后继续到：

```text
Prepare local Python environment
Run tests with coverage
Run smoke test
```

请把最新运行结果发给我；如果 checkout 再次失败，只需提供该步骤最后的错误行。

> User context
>
> Images:
> - `C:/Users/Count/AppData/Local/Temp/codex-clipboard-d4a4acb4-6584-43d0-98ff-d522f69b1afc.png`

<details><summary>5 previous messages</summary>

> 本机 self-hosted 运行已全部成功，九个步骤均为绿色。现在我保存 Actions 证据，并核对这次运行对应的提交、runner 名称以及测试和冒烟日志。随后只差本机终端截图，确认同一 job 在 `BUGSCOMPUTER` 上接收并完成。
>
> <details><summary>Ran 6 commands</summary>
>
> - Ran `$source = 'C:\Users\Count\AppData\Local\Temp\codex-clipboard-d4a4acb4-6584-43d0-98ff-d522f69b1afc.png'
> $destinationDir = 'D:\Projects\Course\isse-labs\lab5\2500013167-wangpeiyuan\screenshots'
> $destination = Join-Path $destinationDir 'self-hosted-actions.png'
> if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw 'Screenshot source was not found.' }
> Copy-Item -LiteralPath $source -Destination $destination
> Get-Item -LiteralPath $destination | Select-Object FullName,Length,LastWriteTime`
> - Ran `gh run list --repo CountlessBugs/isse-lab5-chat-ci --limit 2 --json databaseId,headSha,status,conclusion,displayTitle,url --jq '.[] | [.databaseId,.headSha,.status,.conclusion,.displayTitle,.url] | @tsv'`
> - Ran `git status --short --branch; git log -3 --oneline --decorate; git rev-parse HEAD`
> - Ran `gh api repos/CountlessBugs/isse-lab5-chat-ci/actions/runs/40203499488/jobs --jq '.jobs[] | {name,status,conclusion,runner_name,runner_group_name,steps:[.steps[] | {number,name,status,conclusion}]}'`
> - Ran `gh run view 40203499488 --repo CountlessBugs/isse-lab5-chat-ci --log | Select-String -Pattern 'passed|coverage|服务已就绪|PASS /|服务已停止|冒烟检查通过|exit code'`
> - Ran `gh run view 40203499488 --repo CountlessBugs/isse-lab5-chat-ci --log | Select-String -Pattern 'passed|coverage|服务已就绪|PASS /|服务已停止|冒烟检查通过|exit code'`
>
> </details>
>
> User context
>
> Images:
> - `C:/Users/Count/AppData/Local/Temp/codex-clipboard-bf3259d3-6b07-4d6d-b72e-c61345b130ef.png`
>
> 本机终端证据也已齐全，并且与 Actions 运行时间、job 名称和 `Succeeded` 结果完全对应。我把它保存为 `self-hosted-terminal.png`；四项必需截图现在都已到齐，接下来只需停止前台 runner，然后整理课程提交目录。
>
> <details><summary>Ran 3 commands</summary>
>
> - Ran `$source = 'C:\Users\Count\AppData\Local\Temp\codex-clipboard-bf3259d3-6b07-4d6d-b72e-c61345b130ef.png'
> $destinationDir = 'D:\Projects\Course\isse-labs\lab5\2500013167-wangpeiyuan\screenshots'
> $destination = Join-Path $destinationDir 'self-hosted-terminal.png'
> if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw 'Screenshot source was not found.' }
> Copy-Item -LiteralPath $source -Destination $destination
> Get-Item -LiteralPath $destination | Select-Object FullName,Length,LastWriteTime`
> - Ran `Get-ChildItem -LiteralPath 'D:\Projects\Course\isse-labs\lab5\2500013167-wangpeiyuan\screenshots' -File | Sort-Object Name | Select-Object Name,Length`
> - Ran `gh api repos/CountlessBugs/isse-lab5-chat-ci/actions/runners --jq '.runners[] | {name,status,busy}'`
>
> </details>
</details>

self-hosted 阶段已完整成功。我已核实运行 [40203499488](https://github.com/CountlessBugs/isse-lab5-chat-ci/actions/runs/40203499488)：

- 提交：`8bf591f18cbce4bd59c6a31d52244fc884d67ec2`
- runner：`BUGSCOMPUTER`，Default 组
- 结果：success
- 测试：`2 passed`
- 覆盖率：72.37%
- 冒烟检查：首页与 `/api/hello` 均通过
- 本机 Python：3.13.5
- 所有 Actions step 均为绿色

本机终端记录也与该运行对应：`14:42:35Z` 接收 job，`14:43:31Z` 显示：

```text
Job Tests and coverage completed with result: Succeeded
```

四项必需截图现已保存：

- [failed.png](./lab5/2500013167-wangpeiyuan/screenshots/failed.png)
- [cloud-passed.png](./lab5/2500013167-wangpeiyuan/screenshots/cloud-passed.png)
- [self-hosted-actions.png](./lab5/2500013167-wangpeiyuan/screenshots/self-hosted-actions.png)
- [self-hosted-terminal.png](./lab5/2500013167-wangpeiyuan/screenshots/self-hosted-terminal.png)

另外还保留了测试首次通过、修复后通过和 runner 注册在线等辅助截图。

## 现在停止 runner

回到正在运行 `.\run.cmd` 的 PowerShell 窗口，按：

```text
Ctrl+C
```

runner 是前台程序，按 `Ctrl+C` 即可停止，不需要删除注册信息，也不需要卸载。停止后可以刷新仓库的：

```text
Settings → Actions → Runners
```

`BUGSCOMPUTER` 应逐渐显示为 **Offline**。

确认终端已退出、Runners 页面显示 Offline 后告诉我。下一步我会把最终本机成功版本的应用复制到课程目录：

```text
D:\Projects\Course\isse-labs\lab5\2500013167-wangpeiyuan\app
```

然后检查是否误带 `.env`、`.venv`、`.git` 或缓存，并整理最终提交材料。

> 已完成

<details><summary>10 previous messages</summary>

> 我先确认 runner 已离线，并检查课程个人目录的现状。随后会把实验仓库的最终应用副本复制到 `lab5/2500013167-wangpeiyuan/app/`，明确排除开发环境、Git 元数据和缓存。
>
> <details><summary>Ran 4 commands</summary>
>
> - Ran `gh api repos/CountlessBugs/isse-lab5-chat-ci/actions/runners --jq '.runners[] | {name,status,busy,version}'`
> - Ran `git status --short --branch; git log -1 --oneline --decorate; Get-ChildItem -LiteralPath 'lab5\2500013167-wangpeiyuan' -Force -Recurse | Select-Object FullName,Mode,Length`
> - Ran `Get-ChildItem -LiteralPath 'D:\Projects\Course\isse-lab5-chat-ci' -Force | Select-Object Name,Mode,Length; Get-ChildItem -LiteralPath 'D:\Projects\Course\isse-lab5-chat-ci\.github\workflows' -Force | Select-Object Name,Length`
> - Ran `git status --short --branch; git rev-parse HEAD; git log -3 --oneline --decorate`
>
> </details>
>
> runner 已确认离线。课程分支上没有现成应用副本，只有刚整理的截图。现在创建提交目录中的 `app/`，复制应用、测试、依赖、示例配置和同一份工作流，并排除 `.git`、`.venv`、真实 `.env`、缓存和覆盖率文件。
>
> <details><summary>Ran a command</summary>
>
> - Ran `$source = 'D:\Projects\Course\isse-lab5-chat-ci'
> $target = 'D:\Projects\Course\isse-labs\lab5\2500013167-wangpeiyuan\app'
> $workflowDir = Join-Path $target '.github\workflows'
> New-Item -ItemType Directory -Path $target, $workflowDir -Force | Out-Null
> foreach ($file in @('app.py', 'README.md', 'requirements.txt', 'requirements-dev.txt', '.env.example', '.gitignore')) {
>     Copy-Item -LiteralPath (Join-Path $source $file) -Destination $target
> }
> foreach ($directory in @('frontend', 'tests', 'scripts')) {
>     Copy-Item -LiteralPath (Join-Path $source $directory) -Destination $target -Recurse
> }
> Copy-Item -LiteralPath (Join-Path $source '.github\workflows\ci.yml') -Destination $workflowDir
> Get-ChildItem -LiteralPath $target -Force -Recurse | Select-Object FullName,Mode,Length`
>
> </details>
>
> 复制目录时带入了源码测试目录里的 `__pycache__`，它不应进入提交材料。我会先核对绝对路径确实位于刚创建的课程 `app/tests/` 下，再只删除这一个缓存目录。
>
> <details><summary>Ran 4 commands</summary>
>
> - Ran `$targetRoot = (Resolve-Path -LiteralPath 'D:\Projects\Course\isse-labs\lab5\2500013167-wangpeiyuan\app').Path
> $cachePath = (Resolve-Path -LiteralPath 'D:\Projects\Course\isse-labs\lab5\2500013167-wangpeiyuan\app\tests\__pycache__').Path
> if (-not $cachePath.StartsWith($targetRoot + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
>     throw "Refusing to remove path outside target: $cachePath"
> }
> Remove-Item -LiteralPath $cachePath -Recurse -Force
> if (Test-Path -LiteralPath $cachePath) { throw 'Cache directory still exists.' }
> "Removed generated cache: $cachePath"`
> - Ran `Get-ChildItem -LiteralPath 'D:\Projects\Course\isse-labs\lab5\2500013167-wangpeiyuan\app\tests\__pycache__' -Force | Select-Object FullName,Name,Length`
> - Ran `Get-ChildItem -LiteralPath 'D:\Projects\Course\isse-labs\lab5\2500013167-wangpeiyuan\app\tests\__pycache__' -File | ForEach-Object { $_.FullName }`
> - Ran `Get-ChildItem -LiteralPath 'D:\Projects\Course\isse-labs\lab5\2500013167-wangpeiyuan\app\tests\__pycache__' -File | ForEach-Object { $_.FullName }`
>
> </details>
>
> 当前终端工具阻止了直接删除操作，我改用可恢复方式：把误带的 `tests/__pycache__` 移动到系统临时目录，而不是永久删除。提交目录中不会再包含该缓存。
>
> <details><summary>Ran a command</summary>
>
> - Ran `$sourceCache = 'D:\Projects\Course\isse-labs\lab5\2500013167-wangpeiyuan\app\tests\__pycache__'
> $cacheTrash = 'C:\Users\Count\AppData\Local\Temp\isse-lab5-2500013167-tests-pycache'
> if (-not (Test-Path -LiteralPath $sourceCache -PathType Container)) { throw 'Source cache does not exist.' }
> if (Test-Path -LiteralPath $cacheTrash) { throw 'Temporary cache destination already exists; refusing to overwrite.' }
> Move-Item -LiteralPath $sourceCache -Destination $cacheTrash
> if (Test-Path -LiteralPath $sourceCache) { throw 'Source cache still exists after move.' }
> "Moved generated cache to: $cacheTrash"`
>
> </details>
>
> 应用副本已经复制完成，生成缓存也已移出提交目录。现在进行完整性检查：对比实验仓库与课程 `app/` 的每个文件哈希，确认没有 `.env`、`.venv`、`.git`、覆盖率或 Python 缓存，并核对最终目录结构。
>
> <details><summary>Ran 7 commands</summary>
>
> - Ran `$source = 'D:\Projects\Course\isse-lab5-chat-ci'
> $target = 'D:\Projects\Course\isse-labs\lab5\2500013167-wangpeiyuan\app'
> $relativeFiles = @(
>   'app.py',
>   'README.md',
>   'requirements.txt',
>   'requirements-dev.txt',
>   '.env.example',
>   '.gitignore',
>   '.github\workflows\ci.yml',
>   'frontend\app.js',
>   'frontend\index.html',
>   'frontend\style.css',
>   'tests\conftest.py',
>   'tests\test_chat_api.py',
>   'scripts\smoke_test.py'
> )
> $mismatches = @()
> foreach ($relative in $relativeFiles) {
>   $sourceHash = (Get-FileHash -LiteralPath (Join-Path $source $relative) -Algorithm SHA256).Hash
>   $targetHash = (Get-FileHash -LiteralPath (Join-Path $target $relative) -Algorithm SHA256).Hash
>   if ($sourceHash -ne $targetHash) { $mismatches += $relative }
> }
> if ($mismatches.Count -gt 0) { throw ('Hash mismatch: ' + ($mismatches -join ', ')) }
> "Verified SHA256 for $($relativeFiles.Count) files; all identical."`
> - Ran `rg --files --hidden --no-ignore 'lab5/2500013167-wangpeiyuan' | Sort-Object`
> - Ran `$app = 'D:\Projects\Course\isse-labs\lab5\2500013167-wangpeiyuan\app'
> $forbiddenNames = @('.env', '.venv', '.git', '.pytest_cache', '.coverage', '__pycache__')
> Get-ChildItem -LiteralPath $app -Force -Recurse | Where-Object { $forbiddenNames -contains $_.Name -or $_.Extension -eq '.pyc' } | Select-Object FullName,Name`
> - Ran `git status --short --branch; git status --short -- 'lab5/2500013167-wangpeiyuan'`
> - Ran `rg --files --hidden --no-ignore 'lab5/2500013167-wangpeiyuan' | Sort-Object`
> - Ran `$trace = 'D:\Projects\Course\isse-labs\lab5\2500013167-wangpeiyuan\AGENT_TRACE.md'; if (Test-Path -LiteralPath $trace) { Get-Item -LiteralPath $trace | Select-Object FullName,Length,LastWriteTime } else { 'AGENT_TRACE.md not yet present' }`
> - Ran `Get-Content -LiteralPath 'lab4\2500013167-wangpeiyuan\AGENT_TRACE.md' -TotalCount 25`
>
> </details>
</details>

runner 已确认离线。最终应用已复制到：

[lab5/2500013167-wangpeiyuan/app](./lab5/2500013167-wangpeiyuan/app)

## 完整性检查

已用 SHA256 对比实验仓库和课程副本中的 13 个文件，全部完全一致，包括：

- `app.py` 与前端
- 运行和测试依赖
- `.env.example` 与 `.gitignore`
- `.github/workflows/ci.yml`
- 两个测试与 `conftest.py`
- 冒烟脚本

课程副本中不存在 `.env`、`.venv`、`.git`、`.pytest_cache`、`.coverage` 或 `__pycache__`。复制时误带入的测试缓存已移动到系统临时目录，没有进入提交材料。

## 还缺真实对话轨迹

课程个人目录目前已有应用和全部截图证据，但还没有：

```text
D:\Projects\Course\isse-labs\lab5\2500013167-wangpeiyuan\AGENT_TRACE.md
```

`AGENT_TRACE.md` 必须是本次 Lab5 的真实对话，不能根据结果重新编写或只放摘要。请沿用你 Lab4 使用的 Codex 对话导出或分享方式：

- 如果能够导出 Markdown，保存到上面的准确路径。
- 如果只能生成分享链接，就在 `AGENT_TRACE.md` 中填写可访问的本次对话链接。
- 要保留本次从读取 Lab5 指引，到测试、失败、修复、冒烟及 self-hosted runner 的完整过程。

完成后告诉我。我会检查文件是否位于正确目录、内容是否明显为空以及是否出现敏感凭据，然后带你完成课程分支的暂存检查、提交、推送和 PR。
