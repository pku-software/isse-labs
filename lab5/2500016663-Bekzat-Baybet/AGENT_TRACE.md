
> 请完整阅读 lab5/AGENTS.md 和 lab5/README.md，按交互式流程带我完成 Lab5。

● I'll start by reading the lab materials.

  Thought for 6s, searched for 3 patterns, read 2 files, listed 2 directories (ctrl+o to expand)

● Bash(cd "c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Lab/isse-labs" &&
      git log --oneline -20 && echo "--- BRANCHES ---" && git branch -a && echo
      "--- STATUS ---" && git sta…)
  ⎿  (No output)

  Thought for 1s, listed 1 directory (ctrl+o to expand)

● Bash(cd "c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Lab/isse-labs" &&
      echo "=== remote branches with lab5 ===" && git branch -a --list "*lab5*"
      && echo "=== lab5 in origin…)
  ⎿  (No output)

● Bash(cd "c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Lab" && find .
      -iname "*lab5*" -not -path "*/node_modules/*" -not -path "*/.git/*"
      2>/dev/null | head -40; echo "=== se…)
  ⎿  (No output)

  Thought for 3s (ctrl+o to expand)

● Bash(cd "c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Lab/isse-labs" &&
      git remote -v && echo "=== last fetch ===" && ls -la .git/FETCH_HEAD
      2>/dev/null)
  ⎿  (No output)

  Thought for 1s, searched for 1 pattern, listed 1 directory (ctrl+o to expand)

● Bash(cd "c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Lab/isse-labs" &&
      timeout 60 git fetch upstream --prune 2>&1 | tail -20; echo "=== after
      fetch, lab5 in upstream/main =…)
  ⎿  (No output)

  Thought for 4s (ctrl+o to expand)

● Found it — lab5/ in your working tree is empty, but the materials were just
  added on upstream/main (your local branch is behind). Let me pull them out and
  read them.

● Bash(cd "c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Lab/isse-labs" &&
      mkdir -p /tmp/lab5-materials && git show upstream/main:lab5/AGENTS.md >
      /tmp/lab5-materials/AGENTS.md…)
  ⎿  (No output)

  Thought for 1s, read 2 files (ctrl+o to expand)

● Bash(cd /tmp/lab5-materials && pwd -W 2>/dev/null || cygpath -w
      /tmp/lab5-materials)
  ⎿  (No output)

  Thought for 4s, read 2 files (ctrl+o to expand)

● Both files are read. Let me check your Lab2 app and current git state so my
  walkthrough uses your real paths.

● Bash(cd "c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Lab/isse-labs" &&
      echo "=== lab2 personal dir ===" && ls -la
      "lab2/别克扎提·拜别提-2500016663" 2>/dev/null && echo "=== lab4 p…)
  ⎿  (No output)

● Bash(python --version 2>&1; echo "---"; python -c "import sys;
      print(sys.executable)" 2>&1; echo "=== gh ==="; gh --version 2>&1 | head
      -3; gh auth status 2>&1 | hea…)
  ⎿  (No output)

  Thought for 3s, read 1 file (ctrl+o to expand)

● Bash(cd "c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Lab/isse-labs/lab2/
      别克扎提·拜别提-2500016663" && echo "=== requirements.txt ===" && cat
      requirements.txt && echo "=== .env.ex…)
  ⎿  (No output)

  Thought for 7s (ctrl+o to expand)

● Bash(cd "c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Lab/isse-labs" &&
      git show upstream/main:lab5/templates/smoke_test.py >
      /tmp/lab5-materials/smoke_test.py && echo saved…)
  ⎿  (No output)

  Thought for 5s (ctrl+o to expand)

● Bash(cd "c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Lab/isse-labs" &&
      echo "local main = $(git rev-parse --short main)"; echo "origin/main =
      $(git rev-parse --short origin…)
  ⎿  (No output)
  Thought for 6s (ctrl+o to expand)

● 已完整读完 lab5/AGENTS.md 和 lab5/README.md（并通过 upstream/main
  取到）。开始前有一个必须先处理的实际情况：

  你本地看不到 lab5 材料。 你的工作目录里 lab5/ 只有一个
  .gitkeep，因为当前检出的是 lab4/2500016663-Bekzat-Baybet 分支。我刚从 upstream
  拉取了最新提交
  9eb35f8，lab5/AGENTS.md、lab5/README.md、lab5/templates/smoke_test.py 都在里面
  —— 所以第一步是同步 Fork 主分支，材料才会出现在你的工作目录里。

  ---

  阶段一：准备应用

  本阶段要做什么

  Lab2 里你做出了一个能在网页上操作的聊天应用。以后只要改接口、改数据结构、加功
  能，都得回头重新检查原有功能是否还正常。持续集成（CI）
  就是把这些检查写成自动运行的流程，让代码提交后立刻拿到检查结果。

  这次实验分四步走：先给聊天应用写自动测试，再让 GitHub Actions
  在推送代码后自动跑这些测试；然后故意改坏一处功能，看测试能否发现、日志怎么定位
  、修复后如何恢复通过；接着适配课程提供的冒烟脚本，确认应用能真正启动并响应
  HTTP；最后把同一份工作流切换到本机 runner，让任务在你自己的电脑上执行。

  两个仓库的分工

  ┌────────────────────────┬────────────────────────────────────────────────┐
  │          仓库          │                      用途                      │
  ├────────────────────────┼────────────────────────────────────────────────┤
  │ 课程仓库（你的 Fork Be │ 最后交作业用。在 lab5/<学号>-<姓名> 分支的个人 │
  │ kzat070101/isse-labs） │ 目录里放应用副本、截图和对话轨迹，最后向       │
  │                        │ pku-software/isse-labs 提 PR                   │
  ├────────────────────────┼────────────────────────────────────────────────┤
  │ 新建的个人实验仓库（例 │ 跑 CI 用。放你的 Lab2 应用代码，GitHub Actions │
  │ 如 isse-lab5-chat-ci） │  和本机 runner                                 │
  │                        │ 都配置在这里，运行历史也留在这里               │
  └────────────────────────┴────────────────────────────────────────────────┘

  两个仓库分开是刻意的：实验仓库会频繁推送、触发大量 Actions 运行，还挂着 runner
  配置；课程仓库只需要留下一份干净的最终材料。

  人机分工

  - 我负责：讲解概念、按你的真实代码编写测试和配置、根据运行输出帮你排错。
  - 你负责：亲自敲命令、提交推送、在 GitHub 网页上操作、观察日志和
    runner。这是实验要考核的部分，我不会代跑你的命令。

  ---

  你现在要做的事

  1. 同步 Fork 主分支并创建课程分支

  在 VSCode 终端里执行（isse-labs/ 就是课程仓库根目录）：

  cd "C:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Lab/isse-labs"
  git fetch upstream
  git checkout main
  git merge --ff-only upstream/main
  git push origin main
  git checkout -b lab5/2500016663-Bekzat-Baybet

  假设你终端当前就在 isse-labs/ 下，前几条也可省去：

  git checkout -b lab5/2500016663-Bekzat-Baybet

  执行后请确认：git log --oneline -1 显示的应该是上游最新提交，git status
  干净，并且 ls lab5/ 能看到 AGENTS.md、README.md、templates/。你的 main 目前是
  dd59203，比上游落后，所以这条同步是必须的。

  2. 创建个人目录

  在 isse-labs/ 下新建空目录
  lab5/2500016663-Bekzat-Baybet/（名字必须和分支一致，助教按这个解析）。

  3. 新建个人实验仓库

  到 GitHub 网页新建一个仓库，建议命名 isse-lab5-chat-ci，默认分支
  main，可以设为 Private（你的机器上没有 gh 命令行工具，所以走网页创建）。

  创建后克隆到课程仓库之外的目录，例如：

  cd "C:/Users/Aa233/Desktop/课程/智能化软件系统与工程"
  git clone https://github.com/<你的用户名>/isse-lab5-chat-ci.git

  不要克隆到 isse-labs/ 里面，否则会出现仓库嵌套。

  ---

  需要你反馈的内容

  完成后告诉我三件事：

  1. 课程分支是否创建成功，lab5/ 下是否已能看到课程材料；
  2. 实验仓库的 GitHub 地址和本地绝对路径；
  3. 一个选择：下一步我要把你自己的聊天应用复制进实验仓库。默认按实验要求使用
     Lab2 版本（lab2/别克扎提·拜别提-2500016663/app.py
     (isse-labs/lab2/别克扎提·拜别提-2500016663/app.py)，内存存储、接口最干净，
     测试和覆盖率最容易讲清楚）。如果你希望沿用 Lab4
     里已经加了指标和持久化的那版，也告诉我，我会按那个来。

  顺带说明：复制时我只会带 app.py、frontend/、requirements.txt、.env.example
  和忽略规则，不会碰你 lab2/ 目录下那个含真实 Key 的 .env —— 实验里用测试占位
  Key，真实 Key 留在你本地。

> 1、创建成功
  2、https://github.com/Bekzat070101/isse-lab5-chat-ci
  C:\Users\Aa233\Desktop\课程\智能化软件系统与工程\Rep
  3、就按照Lab2那一版吧，方便我理解

  Thought for 3s (ctrl+o to expand)

● Bash(ls -la "c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Rep" 2>&1 | head
      -30; echo "=== git info ==="; cd
      "c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Rep" 2>/dev/null && git
      rev…)
  ⎿  Error: Exit code 128
     total 4
     drwxr-xr-x 1 Aa233 197609 0 Oct 25 18:10 .
     drwxr-xr-x 1 Aa233 197609 0 Oct 25 18:09 ..
     drwxr-xr-x 1 Aa233 197609 0 Oct 25 18:10 isse-lab5-chat-ci
     === git info ===
     fatal: not a git repository (or any of the parent directories): .git

● Bash(cd "c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Lab/isse-labs" &&
      echo "=== current branch ===" && git rev-parse --abbrev-ref HEAD && echo
      "=== lab5 tree ===" && git l…)
  ⎿  (No output)

  Thought for 1s (ctrl+o to expand)

● Bash(cd
      "c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Rep/isse-lab5-chat-ci"
      && pwd && git rev-parse --show-toplevel && echo "=== remotes ===" && git
      remote -v && echo "===…)
  ⎿  Error: Exit code 128
     /c/Users/Aa233/Desktop/课程/智能化软件系统与工程/Rep/isse-lab5-chat-ci
     C:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Rep/isse-lab5-chat-ci
     === remotes ===
     origin  https://github.com/Bekzat070101/isse-lab5-chat-ci.git (fetch)
     origin  https://github.com/Bekzat070101/isse-lab5-chat-ci.git (push)
     === branches ===
     === log ===
     fatal: your current branch 'main' does not have any commits yet

  Thought for 6s (ctrl+o to expand)

● 路径确认：实验仓库实际在 Rep/isse-lab5-chat-ci（Rep
  是它的上级目录），而且是个空仓库——main 分支还没有任何提交，这很正常，因为你在
  GitHub 建仓库时没勾选初始化文件。课程分支和 lab5/2500016663-Bekzat-Baybet/
  都建好了。

  现在我来把 Lab2 应用复制过去。

● Bash(SRC="c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Lab/isse-labs/lab2/
      别克扎提·拜别提-2500016663"
      DST="c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Rep/isse-lab5-chat-c
      i"…)
  ⎿  (No output)

  Thought for 4s (ctrl+o to expand)

● 已复制完成。实验仓库现在长这样：

  Rep/isse-lab5-chat-ci/
  ├── app.py
  ├── frontend/  (index.html, app.js, style.css)
  ├── requirements.txt
  └── .env.example

  含真实 Key 的 .env 没有复制过去，符合实验要求。

  ---

  阶段一（续）：把应用放进实验仓库

  为什么要这样放

  新建的实验仓库需要先有应用，后面的测试和 CI
  才有检查对象。我们把后端、前端、依赖清单和配置示例带过来，Lab2
  的提交仍然保留在课程仓库里，不影响原作业。

  这里有个关键区分：应用代码 和 本机运行环境 是两回事。

  - 进仓库的：源代码、依赖清单（requirements.txt）、配置示例（.env.example）。这
    些是"需要什么"的声明，体积小、与环境无关。
  - 留在本地的：.env（含真实 Key）、虚拟环境
    .venv/、__pycache__/。这些是"在某台机器上装出来的东西"，体积大或含敏感信息。

  云端 runner 拿到你的代码时，它是没有你的虚拟环境的，只能根据依赖清单自己装一遍
  。所以依赖清单必须准确、必须进仓库 —— 这是 CI 能跑起来的前提。.env.example
  的作用是告诉使用者需要哪些配置项；真实的 .env 由每个人自己创建。.gitignore
  就是把这些不该进仓库的东西挡在外面。

  还有两个 Git 概念要分清：commit 是在本地记录一个版本快照，push
  才是把这些提交上传到 GitHub。CI 是在 GitHub 收到推送后才触发的，所以只 commit
  不 push，Actions 不会有任何反应。

  你的应用：代码结构对照

  ┌─────────┬────────────────────────────────────────┬─────────────────────┐
  │  内容   │                  位置                  │        说明         │
  ├─────────┼────────────────────────────────────────┼─────────────────────┤
  │ 应用入  │ app.py (isse-labs/lab2/别克扎提·拜别提 │ 测试和冒烟脚本要导  │
  │ 口      │ -2500016663/app.py) 的 app =           │ 入的对象，即        │
  │         │ Flask(__name__)                        │ app:app             │
  ├─────────┼────────────────────────────────────────┼─────────────────────┤
  │         │ app.py:38 (isse-labs/lab2/别克扎提·拜  │ 返回                │
  │ 首页    │ 别提-2500016663/app.py#L38)            │ frontend/index.html │
  │         │ serve_index()                          │                     │
  ├─────────┼────────────────────────────────────────┼─────────────────────┤
  │ 连通性  │ app.py:83 (isse-labs/lab2/别克扎提·拜  │ 返回 {"message":    │
  │ 接口    │ 别提-2500016663/app.py#L83) /api/hello │ "你好"}，冒烟检查会 │
  │         │                                        │ 用它                │
  ├─────────┼────────────────────────────────────────┼─────────────────────┤
  │ 前端目  │ frontend/                              │ 由 Flask 同源提供， │
  │ 录      │                                        │ 不是独立服务        │
  ├─────────┼────────────────────────────────────────┼─────────────────────┤
  │ 依赖清  │ requirements.txt                       │ flask、python-doten │
  │ 单      │                                        │ v、requests         │
  ├─────────┼────────────────────────────────────────┼─────────────────────┤
  │         │ app.py:57 (isse-labs/lab2/别克扎提·拜  │ 真正发 HTTP 请求给  │
  │ 模型调  │ 别提-2500016663/app.py#L57)            │ DeepSeek ——         │
  │ 用函数  │ call_deepseek(message)                 │ 后面测试要 mock     │
  │         │                                        │ 的就是它            │
  ├─────────┼────────────────────────────────────────┼─────────────────────┤
  │ 数据存  │ app.py:30-32 (isse-labs/lab2/别克扎提- │ 内存存储，Flask     │
  │ 储      │ 拜别提-2500016663/app.py#L30-L32) 的   │ 重启即清空          │
  │         │ messages 列表和 next_id                │                     │
  └─────────┴────────────────────────────────────────┴─────────────────────┘

  你的接口

  ┌────────┬────────────────────┬────────────────────────────────────────────┐
  │  方法  │        路径        │                    行为                    │
  ├────────┼────────────────────┼────────────────────────────────────────────┤
  │ GET    │ /api/hello         │ 健康检查                                   │
  ├────────┼────────────────────┼────────────────────────────────────────────┤
  │ POST   │ /api/messages      │ 创建一条记录，reply 由模型生成，成功返回   │
  │        │                    │ 201 + 完整记录                             │
  ├────────┼────────────────────┼────────────────────────────────────────────┤
  │ GET    │ /api/messages      │ 返回全部记录                               │
  ├────────┼────────────────────┼────────────────────────────────────────────┤
  │ PATCH  │ /api/messages/<id> │ 修改 message 字段                          │
  ├────────┼────────────────────┼────────────────────────────────────────────┤
  │ DELETE │ /api/messages/<id> │ 删除，成功返回 204（无正文）               │
  └────────┴────────────────────┴────────────────────────────────────────────┘

  这五个接口正好构成一次完整的 CRUD，这就是任务 1
  里那个"一条聊天记录的创建、查询、修改、删除"测试要串起来的流程。call_deepseek
  是唯一会碰外部网络的地方，把它 mock 掉，测试就能离线、免费、结果稳定地跑。

  ---

  你现在要做的事

  1. 创建 .gitignore

  在实验仓库根目录
  C:\Users\Aa233\Desktop\课程\智能化软件系统与工程\Rep\isse-lab5-chat-ci\ 下新建
  .gitignore（文件名前面有个点），写入以下内容：

  gitignore
  # 环境变量与密钥
  .env

  # 虚拟环境
  .venv/
  venv/

  # Python 缓存
  __pycache__/
  *.py[cod]

  # 测试缓存与覆盖率产物
  .pytest_cache/
  .coverage
  htmlcov/

  2. 安装依赖、提交并推送

  在 Git Bash 终端执行：

  cd "C:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Rep/isse-lab5-chat-ci"

  python -m venv .venv
  source .venv/Scripts/activate
  python -m pip install -r requirements.txt

  git add -A
  git commit -m "Lab5: 导入 Lab2 聊天应用"
  git push -u origin main

  第一次推送需要 -u origin main，它把这台本地分支和 GitHub 上的 main
  关联起来，之后直接 git push 就行。

  3. 观察重点

  - git status 里应该没有 .venv/ —— 说明 .gitignore 生效了；
  - 推送成功后刷新 https://github.com/Bekzat070101/isse-lab5-chat-ci
    ，应该能看到
    app.py、frontend/、requirements.txt、.env.example、.gitignore，而 .venv
    不会出现；
  - 这个仓库现在还没有 .github/ 目录，所以还不会触发任何 Actions 运行，页面上的
    Actions 标签是空的，这是正常的。

  需要你反馈的内容

  1. 推送是否成功，GitHub 网页上能看到哪些文件；
  2. python -m pip install -r requirements.txt 有没有报错；
  3. 如果想顺手确认环境没问题，可以执行 python app.py 然后访问
     http://localhost:5001/ ，看聊天页面能否正常打开（.env
     没配，所以发消息会失败，只看页面加载即可，不必强求）。这一步可选，做完按
     Ctrl+C 停掉服务。

  确认后我们就进入任务 1：自动测试与云端 CI。

> source : 无法将“source”项识别为 cmdlet、函数、脚本文件或可运行程序的名称。请
  检查名称的拼写，如果包括路径，请确保路径正确，然后再试一次。
  所在位置 行:2 字符: 1
  - source .venv/Scripts/activate
  -
    + CategoryInfo          : ObjectNotFound: (source:String) [],
  CommandNotFoundException
    + FullyQualifiedErrorId : CommandNotFoundException
   弹出了这个，我看了一下.venv没出现，但是.gitignore也没有出现；其他的都有了

  Thought for 6s (ctrl+o to expand)

● 这是 PowerShell 和 Git Bash
  的语法差异，不影响进度。先看一下仓库现在到底是什么状态。

● Bash(cd
      "c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Rep/isse-lab5-chat-ci"
      && echo "=== 磁盘上的文件（含隐藏） ===" && ls -A && echo "=== .gitignore
      是否存在 ===" && test -f .gitignore &…)
  ⎿  (No output)

  Thought for 6s (ctrl+o to expand)

● Bash(cd
      "c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Rep/isse-lab5-chat-ci"
      && echo "=== 已提交的文件 ===" && git ls-files && echo "===
      提交中包含的文件数 ===" && git ls-files | wc -l &&…)
  ⎿  (No output)

  Thought for 4s (ctrl+o to expand)

● Bash(cd
      "c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Rep/isse-lab5-chat-ci"
      && echo "=== 谁在忽略 .venv ===" && git check-ignore -v .venv 2>&1; echo
      "=== 全局 excludesFile ===" &…)
  ⎿  (No output)

  Thought for 4s (ctrl+o to expand)

● Bash(cd
      "c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Rep/isse-lab5-chat-ci"
      && echo "=== .venv 内容 ===" && ls -A .venv 2>&1 && echo "=== 文件总数
      ===" && find .venv -type f 2>/d…)
  ⎿  (No output)

  Thought for 5s (ctrl+o to expand)

● Bash(cd
      "c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Rep/isse-lab5-chat-ci"
      && echo "=== .venv 内置的 .gitignore 内容 ===" && cat .venv/.gitignore
      2>&1 && echo "=== 已安装的包 ===" &…)
  ⎿  (No output)

  Thought for 7s (ctrl+o to expand)

● 状态已经查清楚了，其实比看起来要好——代码已经提交并推送成功了，只差两件小事。

  刚才发生了什么

  ┌───────────────────────────────────────┬──────────────┬──────────────────┐
  │                 项目                  │     状态     │       说明       │
  ├───────────────────────────────────────┼──────────────┼──────────────────┤
  │ app.py、frontend/、requirements.txt、 │ ✅           │ 提交 ec2c780，共 │
  │ .env.example                          │ 已提交推送   │  6 个文件        │
  ├───────────────────────────────────────┼──────────────┼──────────────────┤
  │ .venv/                                │ ✅ 已创建，  │ 869 个文件，但被 │
  │                                       │ 未进仓库     │ 自动忽略了       │
  ├───────────────────────────────────────┼──────────────┼──────────────────┤
  │ 依赖安装                              │ ❌ 没执行    │ .venv 里只有     │
  │                                       │              │ pip，没有 flask  │
  ├───────────────────────────────────────┼──────────────┼──────────────────┤
  │ .gitignore                            │ ❌ 还没创建  │ 所以你在 GitHub  │
  │                                       │              │ 上看不到它       │
  └───────────────────────────────────────┴──────────────┴──────────────────┘

  关于 .venv 为什么没出现：Python 3.13 在创建虚拟环境时会自动在里面写一个
  .venv/.gitignore，内容就是一行
  *，意思是"这个目录里所有东西都忽略"。所以它压根没被 git add -A
  加进去——这正是我们想要的结果。但你项目根目录自己的 .gitignore
  仍然是作业要求的交付物（最终目录结构里有它），需要补上。

  关于 source 报错：source 是 bash 的语法，你现在用的是 PowerShell。两种 shell
  的虚拟环境激活命令不一样：

  ┌──────────────────────────┬───────────────────────────────┐
  │          Shell           │           激活命令            │
  ├──────────────────────────┼───────────────────────────────┤
  │ Git Bash / Linux / macOS │ source .venv/Scripts/activate │
  ├──────────────────────────┼───────────────────────────────┤
  │ PowerShell               │ .\.venv\Scripts\Activate.ps1  │
  ├──────────────────────────┼───────────────────────────────┤
  │ CMD                      │ .venv\Scripts\activate.bat    │
  └──────────────────────────┴───────────────────────────────┘

  不过我更建议干脆不激活，直接用虚拟环境里 Python 的完整路径调用：

  .\.venv\Scripts\python.exe -m pip install -r requirements.txt

  激活只是把 python 这个命令临时指向 .venv 里的解释器。写全路径效果完全一样，而
  且不会因为忘记激活、或者终端切来切去而误装到全局 Python 上。后面配置本机
  runner 时也会用到这种"显式指定解释器"的思路。

  ---

  你现在要做的事

  1. 补上 .gitignore

  在 C:\Users\Aa233\Desktop\课程\智能化软件系统与工程\Rep\isse-lab5-chat-ci\
  下新建 .gitignore（注意文件名开头的点），写入：

  gitignore
  # 环境变量与密钥
  .env

  # 虚拟环境
  .venv/
  venv/

  # Python 缓存
  __pycache__/
  *.py[cod]

  # 测试缓存与覆盖率产物
  .pytest_cache/
  .coverage
  htmlcov/

  ▎ 小提示：Windows 资源管理器默认隐藏以点开头的文件。如果你创建后"看不见"，在资
  ▎ 源管理器里勾选「查看 → 显示 → 隐藏的项目」即可。用 ls -A（Git Bash）或
  ▎ Get-ChildItem -Force（PowerShell）也能列出来。

  2. 安装依赖

  cd "C:\Users\Aa233\Desktop\课程\智能化软件系统与工程\Rep\isse-lab5-chat-ci"
  .\.venv\Scripts\python.exe -m pip install -r requirements.txt

  3. 验证依赖装好了

  .\.venv\Scripts\python.exe -c "import flask, dotenv, requests; print('ok',
  flask.__version__)"

  4. 提交并推送

  git status
  git add -A
  git commit -m "Lab5: 添加 .gitignore"
  git push

  观察重点

  - git status 应该只列出 .gitignore 一个未跟踪文件，不应该出现 .venv/；
  - 推送后刷新 GitHub 仓库页面，文件列表里应该多出 .gitignore；
  - Actions 标签页仍然是空的 —— 因为还没有 .github/workflows/，这正常。

  需要你反馈的内容

  1. pip install 的输出最后一行是什么（是否 Successfully installed ...）；
  2. 第 3 步的验证命令是否打印出 ok 和版本号；
  3. 推送后 GitHub 上是否能看到 .gitignore。

  这些确认完，就正式进入任务 1：写测试、看覆盖率、配云端 CI。

> gitignore还在呀，但我还是没有在GitHub上看到这个文件C:\Users\Aa233\Desktop\课
  程\智能化软件系统与工程\Lab\isse-labs\lab5\2500016663-Bekzat-Baybet\.gitignor
  e
  PS C:\Users\Aa233\Desktop\课程\智能化软件系统与工程\Lab> cd
  "C:\Users\Aa233\Desktop\课程\智能化软件系统与工程\Rep\isse-lab5-chat-ci"
  >> .\.venv\Scripts\python.exe -m pip install -r requirements.txt
  Collecting flask (from -r requirements.txt (line 1))
    Using cached flask-3.1.3-py3-none-any.whl.metadata (3.2 kB)
  Collecting python-dotenv (from -r requirements.txt (line 2))
    Using cached python_dotenv-1.2.4-py3-none-any.whl.metadata (29 kB)
  Collecting requests (from -r requirements.txt (line 3))
    Using cached requests-2.34.2-py3-none-any.whl.metadata (4.8 kB)
  Collecting blinker>=1.9.0 (from flask->-r requirements.txt (line 1))
    Using cached blinker-1.9.0-py3-none-any.whl.metadata (1.6 kB)
  Collecting click>=8.1.3 (from flask->-r requirements.txt (line 1))
    Using cached click-8.5.0-py3-none-any.whl.metadata (2.6 kB)
  Collecting itsdangerous>=2.2.0 (from flask->-r requirements.txt (line 1))
    Using cached itsdangerous-2.2.0-py3-none-any.whl.metadata (1.9 kB)
  Collecting jinja2>=3.1.2 (from flask->-r requirements.txt (line 1))
    Using cached jinja2-3.1.6-py3-none-any.whl.metadata (2.9 kB)
  Collecting markupsafe>=2.1.1 (from flask->-r requirements.txt (line 1))
    Using cached markupsafe-3.0.4-cp313-cp313-win_amd64.whl.metadata (2.8 kB)
  Collecting werkzeug>=3.1.0 (from flask->-r requirements.txt (line 1))
    Using cached werkzeug-3.1.9-py3-none-any.whl.metadata (4.1 kB)
  Collecting charset_normalizer<4,>=2 (from requests->-r requirements.txt (line
  3))
    Using cached charset_normalizer-3.5.2-cp313-cp313-win_amd64.whl.metadata
  (47 kB)
  Collecting idna<4,>=2.5 (from requests->-r requirements.txt (line 3))
    Using cached idna-3.20-py3-none-any.whl.metadata (7.2 kB)
  Collecting urllib3<3,>=1.26 (from requests->-r requirements.txt (line 3))
    Using cached urllib3-2.8.0-py3-none-any.whl.metadata (7.4 kB)
  Collecting certifi>=2023.5.7 (from requests->-r requirements.txt (line 3))
    Downloading certifi-2026.10.23-py3-none-any.whl.metadata (2.5 kB)
  Using cached flask-3.1.3-py3-none-any.whl (103 kB)
  Using cached python_dotenv-1.2.4-py3-none-any.whl (23 kB)
  Using cached requests-2.34.2-py3-none-any.whl (73 kB)
  Using cached charset_normalizer-3.5.2-cp313-cp313-win_amd64.whl (206 kB)
  Using cached idna-3.20-py3-none-any.whl (69 kB)
  Using cached urllib3-2.8.0-py3-none-any.whl (135 kB)
  Using cached blinker-1.9.0-py3-none-any.whl (8.5 kB)
  Downloading certifi-2026.10.23-py3-none-any.whl (135 kB)
  Using cached click-8.5.0-py3-none-any.whl (125 kB)
  Using cached itsdangerous-2.2.0-py3-none-any.whl (16 kB)
  Using cached jinja2-3.1.6-py3-none-any.whl (134 kB)
  Using cached markupsafe-3.0.4-cp313-cp313-win_amd64.whl (14 kB)
  Using cached werkzeug-3.1.9-py3-none-any.whl (228 kB)
  Installing collected packages: urllib3, python-dotenv, markupsafe,
  itsdangerous, idna, click, charset_normalizer, certifi, blinker, werkzeug,
  requests, jinja2, flask
  Successfully installed blinker-1.9.0 certifi-2026.10.23
  charset_normalizer-3.5.2 click-8.5.0 flask-3.1.3 idna-3.20 itsdangerous-2.2.0
  jinja2-3.1.6 markupsafe-3.0.4 python-dotenv-1.2.4 requests-2.34.2
  urllib3-2.8.0 werkzeug-3.1.9

  [notice] A new release of pip is available: 25.2 -> 26.2.2
  [notice] To update, run: C:\Users\Aa233\Desktop\课程\智能化软件系统与工程\Rep
  \isse-lab5-chat-ci\.venv\Scripts\python.exe -m pip install --upgrade pip
  PS C:\Users\Aa233\Desktop\课程\智能化软件系统与工程\Rep\isse-lab5-chat-ci>
  .\.venv\Scripts\python.exe -c "import flask, dotenv, requests; print('ok',
  flask.__version__)"
  <string>:1: DeprecationWarning: The '__version__' attribute is deprecated and
  will be removed in Flask 3.2. Use feature detection or
  'importlib.metadata.version("flask")' instead.
  ok 3.1.3
  PS C:\Users\Aa233\Desktop\课程\智能化软件系统与工程\Rep\isse-lab5-chat-ci>
  git status
  >> git add -A
  >> git commit -m "Lab5: 添加 .gitignore"
  >> git push
  On branch main
  Your branch is up to date with 'origin/main'.

  nothing to commit, working tree clean
  On branch main
  Your branch is up to date with 'origin/main'.

  nothing to commit, working tree clean
  Everything up-to-date
  PS C:\Users\Aa233\Desktop\课程\智能化软件系统与工程\Rep\isse-lab5-chat-ci>
  git status
  On branch main
  Your branch is up to date with 'origin/main'.

  nothing to commit, working tree clean
  PS C:\Users\Aa233\Desktop\课程\智能化软件系统与工程\Rep\isse-lab5-chat-ci>

  Thought for 4s (ctrl+o to expand)

● 找到问题了——你把 .gitignore
  建到了另一个仓库里。你给的路径是课程仓库的个人目录：

  Lab\isse-labs\lab5\2500016663-Bekzat-Baybet\.gitignore   ← 建在这里了

  而我们要提交的是实验仓库：

  Rep\isse-lab5-chat-ci\.gitignore                          ← 应该是这里

  所以实验仓库的 git status 才会显示 "nothing to
  commit"。先确认一下两边的实际状态：

  Thought for 5s, listed 1 directory (ctrl+o to expand)
● 确认了：.gitignore 建在了课程个人目录里，实验仓库根目录没有。我把它移到正确的
  位置（移动而不是重写，内容不变）：

● Bash(SRC="c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Lab/isse-labs/lab5/
      2500016663-Bekzat-Baybet/.gitignore"
      DST="c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Rep/isse-lab5-chat-c
      …)
  ⎿  (No output)

  Thought for 4s (ctrl+o to expand)

● 依赖装好了：Successfully installed ... flask-3.1.3 python-dotenv-1.2.4
  requests-2.34.2 ...，验证也打印了 ok 3.1.3。（那句 __version__ 的
  DeprecationWarning 是 Flask 3.2 的弃用提醒，与我们无关，忽略即可。）

  .gitignore 我已经移到实验仓库根目录，现在 git status 正确显示它了：

  ?? .gitignore

  关于刚才那个弯路

  这个错误值得记一下，因为后面配本机 runner 时会反复遇到：

  两个仓库的目录长得像，但 Git 只认自己所在的那棵树。
  你在课程个人目录里创建文件，那个文件属于课程仓库；在实验仓库里执行 git
  status，当然看不到它。Git
  命令永远只作用于当前工作目录所属的那个仓库，不会跨仓库。

  三个防止走错的方法：

  1. 看提示符 —— 你的 PowerShell 提示符 PS C:\...\Rep\isse-lab5-chat-ci>
     已经告诉你在哪了；
  2. git status 的第一行会写 On branch main，配合 git remote -v 看远端是
     isse-lab5-chat-ci 还是 isse-labs；
  3. 最直接的一条：

  git rev-parse --show-toplevel

  它打印当前目录所属仓库的根目录。不确定自己在哪的时候，先跑这一条。

  顺带说明：课程个人目录 lab5/2500016663-Bekzat-Baybet/
  现在恢复成空目录了。这是对的——按作业要求，它的内容是最后整理阶段才填进去的（ap
  p/、screenshots/、AGENT_TRACE.md），实验过程中的所有提交都发生在实验仓库里。

  ---

  你现在要做的事

  在实验仓库里提交并推送 .gitignore：

  cd "C:\Users\Aa233\Desktop\课程\智能化软件系统与工程\Rep\isse-lab5-chat-ci"
  git add .gitignore
  git commit -m "Lab5: 添加 .gitignore"
  git push

  观察重点

  - git add 后再跑 git status，.gitignore 应从 ?? .gitignore 变成 new file:
    .gitignore，同时 .venv/ 依然不该出现；
  - git commit 的输出应显示 1 file changed；
  - git push 应输出 1 file changed 类似的统计，而不是 Everything
    up-to-date（如果又看到 up-to-date，说明又提交到了别的仓库）；
  - 刷新 GitHub 页面，文件列表里应该出现 .gitignore。

  需要你反馈的内容

  推送后 GitHub 上能否看到 .gitignore，以及 git push 的输出内容。

  确认后我们进入任务 1：自动测试与云端 CI。第一步我会读完你的
  app.py，跟你讲解要测哪两个重点、为什么模型调用要
  mock，然后把测试代码写进实验仓库的 tests/test_chat_api.py，由你运行 pytest
  看结果。

> ok没问题了

  Thought for 27s (ctrl+o to expand)

● 实验仓库状态正常，依赖也装好了。现在进入任务
  1，我先讲清楚要测什么、为什么，再把测试写进去。

  先确认一下我读到的你的接口实现细节（已读过 app.py
  (isse-labs/lab2/别克扎提·拜别提-2500016663/app.py)）：messages
  是模块级列表、next_id 是模块级计数器，create_message 里用 global next_id
  递增，模型调用集中在 call_deepseek()。这决定了测试要怎么写。

● Write(c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Rep/isse-lab5-chat-ci/t
       ests/test_chat_api.py)
  ⎿  Wrote 76 lines to c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Rep
     /isse-lab5-chat-ci/tests/test_chat_api.py
      1 """聊天应用后端的行为测试。
      2
      3 运行方式（在仓库根目录）：
      4
      5     python -m pytest -q
      6
      7 测试直接使用 Flask 的 test client 发请求，不需要先启动服务，也不
        会
      8 访问真实的 DeepSeek 接口。
      9 """
     … +70 lines (ctrl+o to expand)

● Write(c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Rep/isse-lab5-chat-ci/r
       equirements-dev.txt)
  ⎿  Wrote 2 lines to c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Rep/
     isse-lab5-chat-ci/requirements-dev.txt
      1 pytest
      2 pytest-cov

  Thought for 5s (ctrl+o to expand)

● 两个文件已经写进实验仓库了：

  Rep/isse-lab5-chat-ci/
  ├── tests/test_chat_api.py     ← 新增：两个重点测试
  └── requirements-dev.txt       ← 新增：pytest、pytest-cov

  ---

  任务 1：自动测试与云端 CI

  1. 为什么要把检查写成程序

  在 Lab2 里，你是通过点击网页或发 curl 请求来确认功能正常的。这种方式的问题是：
  每次改代码你都得手动重做一遍，而且很容易漏掉几条。自动测试把"发什么请求、期望
  什么结果、怎么判断"写成程序，之后运行一条命令就能重复检查全部内容。

  测试里的 assert 表示一个应该成立的条件。比如创建记录之后：

  assert created.status_code == 201
  assert record["reply"] == "这是一条固定回复"

  只要有一行不成立，pytest 就会把这条用例标记为失败，并打印出实际值和预期值。测
  试的价值不在于"跑过了"，而在于"不成立时它会告诉你" —— 这正是任务 2
  要利用的性质。

  2. 两个测试重点

  作业要求的必做测试收敛为两个，覆盖两类风险：

  ┌──────────┬──────────────────┬──────────────────────────────────────────┐
  │   测试   │     检查什么     │                  为什么                  │
  ├──────────┼──────────────────┼──────────────────────────────────────────┤
  │ 聊天记录 │ 创建 → 查询 →    │ 走完整条主流程，确认四个接口协同工作，改 │
  │  CRUD    │ 修改 → 删除，每  │ 动字段真的存下来了                       │
  │          │ 步都断言实际内容 │                                          │
  ├──────────┼──────────────────┼──────────────────────────────────────────┤
  │ 一类非法 │ 只含空白的       │ 确认错误路径的响应格式，同时确认非法请求 │
  │ 输入     │ message 应返回 4 │ 不会污染数据                             │
  │          │ 00，且不新增记录 │                                          │
  └──────────┴──────────────────┴──────────────────────────────────────────┘

  第二个测试里的 assert client.get("/api/messages").get_json() == []
  是很多人会漏掉的一句：光检查"返回了
  400"还不够，还要确认它没有偷偷把脏数据存进去。

  3. 为什么必须 mock 模型调用

  你的 call_deepseek()（app.py:57
  (isse-labs/lab2/别克扎提·拜别提-2500016663/app.py#L57)）会真的向
  api.deepseek.com 发 HTTP 请求。如果测试直接调它，会带来三个问题：

  - 要联网 —— 网络抖动会让测试偶发失败，而 CI 上失败原因会变得难以判断；
  - 要花钱、要 Key —— 每次 CI 运行都消耗额度，还得把真实 Key 配到 GitHub 上；
  - 回复不固定 —— 模型每次返回的文本可能不同，assert 就没法写确定的预期值。

  所以测试里用一个固定回复替掉真实调用：

  monkeypatch.setattr(chat, "call_deepseek", lambda message: "这是一条固定回复")

  这里有两处细节值得注意：

  - 替换的是 chat.call_deepseek，即 app 模块上的属性。 因为 create_message()
    内部是按模块全局名字去找 call_deepseek
    的，替换模块属性才能生效；如果你在测试文件顶部写 from app import
    call_deepseek 再替换那个名字，接口里用的仍然是原函数，mock 会失效。
  - 被替换掉的是"调用外部服务"这一层，接口其余逻辑（参数校验、记录 id
    分配、存储、响应格式）全部照常执行。我们测的正是这些自己的逻辑。

  monkeypatch 是 pytest 的
  fixture，它在每条用例结束后自动还原被替换的属性，不会污染其他测试。

  4. 为什么要重置数据

  你的应用把记录存在模块级的全局变量里（app.py:30-32
  (isse-labs/lab2/别克扎提·拜别提-2500016663/app.py#L30-L32)）：messages 列表和
  next_id
  计数器。这意味着上一条用例创建的记录，会残留到下一条用例里，第二次运行时
  next_id 还会从 2 开始，断言就会莫名其妙地失败。

  client fixture 在每次测试开始前把它们清回初始状态：

  chat.messages.clear()
  chat.next_id = 1

  这就是 fixture 的作用：让每条用例都从一个明确的、可重复的起点开始。测试之间不
  共享状态，任何一条都能单独运行、反复运行。

  5. test_client 为什么不用先启动服务

  Flask 的 app.test_client() 在同一个进程内直接向 WSGI 应用发请求，不经过 TCP
  端口。所以：

  - 不需要先 python app.py，也不会占用 5001 端口；
  - 不需要处理"服务还没起来"的等待问题；
  - 速度快，一条命令就能跑完。

  代价是它不检查真实进程启动和 HTTP 服务这一层 —— 这正是任务 3
  要补的冒烟检查要做的事。

  ---

  你现在要做的事

  安装测试依赖并运行测试：

  cd "C:\Users\Aa233\Desktop\课程\智能化软件系统与工程\Rep\isse-lab5-chat-ci"
  .\.venv\Scripts\python.exe -m pip install -r requirements.txt -r
  requirements-dev.txt
  .\.venv\Scripts\python.exe -m pytest -q

  观察重点

  - 输出结尾应该是 2 passed in ...s，表示两条用例的全部断言都成立；
  - 注意每条用例的 . 或 F：. 通过、F 失败，失败时会接着打印断言详情，包括 assert
    500 == 201 这样"实际值 vs 预期值"的对比；
  - 这条命令没有加覆盖率参数，所以现在只报告测试通过与否，不看覆盖了多少代码 ——
    覆盖率是下一步的事。

  一个容易踩的坑

  请用 python -m pytest 而不要直接敲 pytest。测试文件里写的是 import app，而
  python -m pytest 会把当前目录（仓库根）加进模块搜索路径，app.py
  才能被找到；直接跑 pytest 时搜索路径里可能没有仓库根，就会报
  ModuleNotFoundError: No module named 'app'。

  需要你反馈的内容

  把 pytest 的实际输出发我，特别是最后那一行统计结果。如果出现失败，把失败详情一
  起贴过来——那正好是我们下一步要一起看的东西。

> platform win32 -- Python 3.13.6, pytest-9.1.1, pluggy-1.6.0
  rootdir:
  C:\Users\Aa233\Desktop\课程\智能化软件系统与工程\Rep\isse-lab5-chat-ci
  plugins: anyio-4.13.0, langsmith-0.14.4
  collected 2 items



  tests\test_chat_api.py ..

                                                       [100%]

  =============================================================================
  ==================== 2 passed in 0.95s ======================================
  ============================================================

  Thought for 15s (ctrl+o to expand)

● 两条用例全部通过，2 passed。进入下一步之前，我先确认一个输出里的细节——你的
  pytest 报告了 anyio 和 langsmith 两个插件，但它们并不在 requirements-dev.txt
  里，我查一下这个环境是否会和你后面在 CI 上跑出的结果不一致：

● Bash(cd
      "c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Rep/isse-lab5-chat-ci"
      && echo "=== pyvenv.cfg ===" && cat .venv/pyvenv.cfg && echo "=== venv
      里的包 ===" && ./.venv/Scrip…)
  ⎿  (No output)

  Thought for 8s (ctrl+o to expand)

● Bash(cd
      "c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Rep/isse-lab5-chat-ci"
      && ./.venv/Scripts/python.exe -c "import site, sys;
      print('ENABLE_USER_SITE =', site.ENABLE_USER…)
  ⎿  (No output)

  Thought for 8s (ctrl+o to expand)

● ENABLE_USER_SITE 是
  False，用户目录里也没有这两个包。但有一个更关键的线索：你的 venv 里明明装了
  pytest-cov 7.1.0，而 pytest 报告的插件列表里没有 cov。我怀疑你实际用的是全局
  Python 而不是 venv 里的：

● Bash(echo "=== 全局 Python 的相关包 ===" &&
      "C:/Users/Aa233/AppData/Local/Programs/Python/Python313/python.exe" -m pip
      list 2>&1 | grep -iE "^(pytest|pytest-cov|langsmith|…)
  ⎿  (No output)

  Thought for 9s (ctrl+o to expand)

● 确认了。你的测试其实是在全局 Python 上跑的，不是我们准备的 venv：

  ┌──────────────────────────────────┬──────────────┬─────────────┐
  │                                  │ venv (.venv) │ 全局 Python │
  ├──────────────────────────────────┼──────────────┼─────────────┤
  │ anyio 4.13.0                     │ ✗            │ ✓           │
  ├──────────────────────────────────┼──────────────┼─────────────┤
  │ langsmith 0.14.4                 │ ✗            │ ✓           │
  ├──────────────────────────────────┼──────────────┼─────────────┤
  │ pytest-cov                       │ ✓ 7.1.0      │ ✗ 没装      │
  ├──────────────────────────────────┼──────────────┼─────────────┤
  │ flask / requests / python-dotenv │ ✓            │ ✓           │
  └──────────────────────────────────┴──────────────┴─────────────┘

  你的输出里插件列表是 anyio-4.13.0,
  langsmith-0.14.4，正好和全局环境一模一样；而 venv 里的 pytest-cov
  没有出现在列表中。所以那次运行用的是
  C:\Users\Aa233\AppData\Local\Programs\Python\Python313\python.exe。

  为什么这次"侥幸通过"值得停下来讲

  测试仍然通过了，因为全局 Python 恰好也装了
  flask、requests、python-dotenv（大概是你做 Lab2
  时装的）。但这是一次运气，不是设计：

  - 你敲的命令解析到了哪个 python，就决定了用哪套依赖。这台机器上两套环境碰巧都
    够用，换一台机器就不一定了；
  - 全局环境里那些无关的包（langsmith 这类）会跟着被 pytest
    加载，让运行结果依赖机器状态；
  - 最直接的后果：全局环境没装 pytest-cov，你下一步跑覆盖率命令会直接报
    unrecognized arguments: --cov。

  这正是 CI 要解决的问题：云端 runner 上不会有你机器上这套全局环境，它只会按
  requirements.txt 从零装一遍。所以从现在起，本地也统一用显式路径调用 venv
  里的解释器，让本地和云端的行为尽可能一致：

  .\.venv\Scripts\python.exe -m pytest -q

  ---

  任务 1（续）：查看覆盖率

  1. 覆盖率在衡量什么

  测试通过，只说明这些测试里的判断条件被满足了。但你不知道它们到底执行了多少后端
  代码——也许只走了最顺的那条路径，一半的分支从没被碰过。

  行覆盖率统计的是：测试运行时，执行过的可执行语句占被测代码全部可执行语句的比例
  。它能帮你找出"从没被跑到的代码路径"。

  报告里的四列：

  ┌─────────┬────────────────────────────────────────────────┐
  │   列    │                      含义                      │
  ├─────────┼────────────────────────────────────────────────┤
  │ Stmts   │ 可执行语句总数（空行、注释、纯文档字符串不算） │
  ├─────────┼────────────────────────────────────────────────┤
  │ Miss    │ 没被执行到的语句数                             │
  ├─────────┼────────────────────────────────────────────────┤
  │ Cover   │ 覆盖比例，即 (Stmts - Miss) / Stmts            │
  ├─────────┼────────────────────────────────────────────────┤
  │ Missing │ 未执行到的行号，最有价值的一列                 │
  └─────────┴────────────────────────────────────────────────┘

  举个对你的应用很具体的例子：如果测试只发过合法消息，那么处理"message
  为空"的那几行就永远不会执行，Missing
  里会出现它们的行号。看到行号后，再决定要不要补一条用例。

  重要的认知：覆盖率高不等于结果正确。覆盖率只回答"这段代码被执行过吗"，不回答"
  执行结果对不对"。结果是否正确，靠的是
  assert。一个把所有分支都跑到、却断言写错的测试套件，覆盖率可以是 100%。

  2. 三个参数的作用

  这次在 pytest 命令后加三个参数：

  ┌─────────────────────────┬───────────────────────────────────────────────┐
  │          参数           │                     作用                      │
  ├─────────────────────────┼───────────────────────────────────────────────┤
  │                         │ 指定被测对象是 app 模块（即                   │
  │ --cov=app               │ app.py）。不指定的话，pytest                  │
  │                         │ 只会告诉你测试通过，不统计任何覆盖            │
  ├─────────────────────────┼───────────────────────────────────────────────┤
  │ --cov-report=term-missi │ 在终端打印报告表格，并列出每一行未覆盖的具体  │
  │ ng                      │ 行号                                          │
  ├─────────────────────────┼───────────────────────────────────────────────┤
  │ --cov-fail-under=70     │ 设置通过门槛：覆盖率低于 70%                  │
  │                         │ 时，命令以非零状态码退出                      │
  └─────────────────────────┴───────────────────────────────────────────────┘

  第三个参数有个关键效果：可能出现测试断言全部通过，但整条命令仍然失败。比如 2
  passed 之后跟着 FAIL Required test coverage of 70% not reached。这不是
  bug，而是刻意设计——CI
  只看命令的退出码，这样"代码没被测试覆盖够"和"测试失败"一样能拦住提交。

  3. 结合你的项目

  你的后端是单文件的
  app.py，没有拆成多个模块，所以统计范围就是它一个：--cov=app。tests/ 和
  frontend/ 不在范围内（前端是 JavaScript，Python 覆盖率工具也管不了它）。

  基于我已经读过的代码，我预计 Missing 里会出现这几处：

  - call_deepseek() 的函数体 —— 因为测试里把它 mock 掉了，那几行从未真正执行；
  - create_message() 里的异常分支（Key 缺失返回 500、请求失败返回
    502、响应结构异常返回 502）—— 我们的两条用例都没触发；
  - 静态文件路由 serve_index / serve_frontend_file —— 测试没请求过 /。

  这些都是"知道会发生"的，先看真实报告再决定补什么。

  ---

  你现在要做的事

  先用 venv 的解释器重跑一次测试，顺便确认环境对了；然后跑覆盖率命令：

  cd "C:\Users\Aa233\Desktop\课程\智能化软件系统与工程\Rep\isse-lab5-chat-ci"
  .\.venv\Scripts\python.exe -m pytest -q
  .\.venv\Scripts\python.exe -m pytest -q --cov=app --cov-report=term-missing
  --cov-fail-under=70

  观察重点

  - 第一条命令的插件列表里这次应该出现 cov-7.1.0，这就是环境切换成功的标志；
  - 第二条命令会打印一张表格，最后一行是 TOTAL，给出总覆盖率和总结论；
  - 注意命令结束后的退出码：PowerShell 里可以紧接着执行 $LASTEXITCODE 查看，非 0
    表示覆盖率没到 70%；
  - 对照 Missing 列的行号，看看是不是我给的那几处。

  需要你反馈的内容

  1. 覆盖率表格的完整内容（Name / Stmts / Miss / Cover / Missing 那几行）；
  2. 命令最后的结论：是通过，还是报了覆盖率不足；
  3. 你自己对 Missing 里那些行号的判断——它们分别对应什么样的请求或场景没被测到。

  拿到真实报告后，如果需要补测试，我会结合未覆盖的行来加。

> 2 passed in 0.26s
  ..

                                                       [100%]
  =============================================================================
  ====================== tests coverage =======================================
  ============================================================
  _____________________________________________________________________________
  _____ coverage: platform win32, python 3.13.6-final-0 _______________________
  ____________________________________________________________

  Name     Stmts   Miss  Cover   Missing
  --------------------------------------
  app.py      73     22    70%   41, 51, 59-77, 86, 96, 105-113, 137, 141, 148,
  160, 164
  --------------------------------------
  TOTAL       73     22    70%
  FAIL Required test coverage of 70% not reached. Total coverage: 69.86%
  2 passed in 0.36s

  最后报了覆盖率不足。两条测试都是passed，但是实际覆盖率是69.86%，没有达到要求
  的70%，所以命令最后还是失败了

  Thought for 18s (ctrl+o to expand)

● 你的分析完全正确：73 条可执行语句里漏了 22 条，51/73 = 69.86%，差 1
  条语句就能到 70%。这正是 --cov-fail-under
  的设计意图——断言全过，但覆盖率不达标，命令照样失败。

  先看一下首页内容，好写一条有意义的断言：

  Thought for 5s, read 1 file (ctrl+o to expand)

● 你的判断准确。现在按 Missing
  中的行号补测试——只补必要的，不扩展成全面测试项目。

● Update(c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Rep/isse-lab5-chat-ci/
        tests/test_chat_api.py)
  ⎿  Added 78 lines
       74      assert "不能为空" in response.get_json()["error"]
       75      # 非法输入不能留下脏数据
       76      assert client.get("/api/messages").get_json() == []
       77 +                                                              
       78 +                                                              
       79 +# ------------------------------------------------------------
          +---------------                                               
       80 +# 下面几条是为了覆盖上面两个重点测试走不到的分支：            
       81 +# 首页与静态文件、健康检查、请求体格式错误、模型配置缺失、记录
          +不存在。                                                      
       82 +# ------------------------------------------------------------
          +---------------                                               
       83 +                                                              
       84 +                                                              
       85 +def test_hello_endpoint(client):                              
       86 +    """健康检查接口应固定返回问候语。"""                      
       87 +    response = client.get("/api/hello")                       
       88 +                                                              
       89 +    assert response.status_code == 200                        
       90 +    assert response.get_json() == {"message": "你好"}         
       91 +                                                              
       92 +                                                              
       93 +def test_home_page_and_static_file_are_served(client):        
       94 +    """首页和 frontend/ 下的静态文件都由 Flask 直接提供。"""  
       95 +    home = client.get("/")                                    
       96 +    assert home.status_code == 200                            
       97 +    assert "AI 聊天助手" in home.get_data(as_text=True)       
       98 +                                                              
       99 +    stylesheet = client.get("/style.css")                     
      100 +    assert stylesheet.status_code == 200                      
      101 +                                                              
      102 +                                                              
      103 +def test_create_rejects_non_json_body(client):                
      104 +    """请求体不是 JSON 对象时返回 400。"""                    
      105 +    response = client.post(                                   
      106 +        "/api/messages", data="这不是 JSON", content_type="tex
          +t/plain"                                                      
      107 +    )                                                         
      108 +                                                              
      109 +    assert response.status_code == 400                        
      110 +    assert "JSON" in response.get_json()["error"]             
      111 +                                                              
      112 +                                                              
      113 +def test_create_without_api_key_returns_500(client, monkeypatc
          +h):                                                           
      114 +    """缺少模型 Key 属于服务端配置错误，应返回 500 而不是 400 
          +。                                                            
      115 +                                                              
      116 +    这条用例故意不 mock，让 call_deepseek 真正执行到"检查 Key"
          +那一步；                                                      
      117 +    因为 Key 被删掉了，它会在发网络请求之前就抛出 ValueError。
      118 +    """                                                       
      119 +    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)     
      120 +                                                              
      121 +    response = client.post("/api/messages", json={"message": "
          +你好"})                                                       
      122 +                                                              
      123 +    assert response.status_code == 500                        
      124 +    assert "DEEPSEEK_API_KEY" in response.get_json()["error"] 
      125 +    # 调用失败时不能留下半条记录                              
      126 +    assert client.get("/api/messages").get_json() == []       
      127 +                                                              
      128 +                                                              
      129 +def test_update_rejects_invalid_payload(client):              
      130 +    """修改接口同样要挡住非 JSON 请求体和空白 message。"""    
      131 +    non_json = client.patch(                                  
      132 +        "/api/messages/1", data="这不是 JSON", content_type="t
          +ext/plain"                                                    
      133 +    )                                                         
      134 +    assert non_json.status_code == 400                        
      135 +                                                              
      136 +    blank = client.patch("/api/messages/1", json={"message": "
          +   "})                                                        
      137 +    assert blank.status_code == 400                           
      138 +    assert "不能为空" in blank.get_json()["error"]            
      139 +                                                              
      140 +                                                              
      141 +def test_update_missing_record_returns_404(client):           
      142 +    """修改不存在的记录返回 404。"""                          
      143 +    response = client.patch("/api/messages/999", json={"messag
          +e": "改一下"})                                                
      144 +                                                              
      145 +    assert response.status_code == 404                        
      146 +    assert "不存在" in response.get_json()["error"]           
      147 +                                                              
      148 +                                                              
      149 +def test_delete_missing_record_returns_404(client):           
      150 +    """删除不存在的记录返回 404。"""                          
      151 +    response = client.delete("/api/messages/999")             
      152 +                                                              
      153 +    assert response.status_code == 404                        
      154 +    assert "不存在" in response.get_json()["error"]           

  Thought for 5s (ctrl+o to expand)

● 新增了 7 条用例，每条都对应 Missing 里的一段行号——补测试的依据是"哪段代码从没
  被执行过"，而不是"数字不够随便加几条"：

  ┌────────┬──────────────────────┬────────────────────────────────────────┐
  │ Missin │       对应代码       │                新增用例                │
  │ g 行号 │                      │                                        │
  ├────────┼──────────────────────┼────────────────────────────────────────┤
  │ 41, 51 │ 首页和静态文件路由   │ test_home_page_and_static_file_are_ser │
  │        │                      │ ved                                    │
  ├────────┼──────────────────────┼────────────────────────────────────────┤
  │ 86     │ /api/hello 的返回    │ test_hello_endpoint                    │
  ├────────┼──────────────────────┼────────────────────────────────────────┤
  │        │ call_deepseek 里检查 │                                        │
  │ 59-62, │  Key →               │ test_create_without_api_key_returns_50 │
  │  107   │ create_message 捕获  │ 0                                      │
  │        │ ValueError 返回 500  │                                        │
  ├────────┼──────────────────────┼────────────────────────────────────────┤
  │ 96     │ 创建接口收到非 JSON  │ test_create_rejects_non_json_body      │
  │        │ 请求体的 400         │                                        │
  ├────────┼──────────────────────┼────────────────────────────────────────┤
  │ 137,   │ 修改接口的两种非法输 │ test_update_rejects_invalid_payload    │
  │ 141    │ 入 400               │                                        │
  ├────────┼──────────────────────┼────────────────────────────────────────┤
  │ 148    │ 修改不存在的记录 404 │ test_update_missing_record_returns_404 │
  ├────────┼──────────────────────┼────────────────────────────────────────┤
  │ 160    │ 删除不存在的记录 404 │ test_delete_missing_record_returns_404 │
  └────────┴──────────────────────┴────────────────────────────────────────┘

  几个设计上的考虑：

  500 那条故意不用 mock。 其他用例都把 call_deepseek 换成了固定回复，这条却用
  monkeypatch.delenv 把 Key 删掉，让真实函数执行。这样它会走到"没有 Key → 抛
  ValueError"这一行，然后被 create_message 的 except ValueError 捕获，返回
  500。这验证了一个重要区分：缺少 Key
  是服务端配置问题（500），不是用户请求有问题（400）。同时断言"失败时没有留下半
  条记录"——因为你的代码是先拿到回复、再存记录，这个顺序值得锁住。

  404 类和 400 类分开测。
  它们走的是不同的代码路径：非法输入在查表之前就被拦下，404
  则是查遍列表没找到。合并成一条会让人分不清是哪段逻辑出的问题。

  补完之后仍有三处覆盖不到，这是正常的：

  - 63-77 —— call_deepseek 真正发 HTTP 请求、解析响应的部分。要覆盖它就得连
    requests.post 也 mock，那样测的其实是"我们怎么拼请求"，收益不大；
  - 110, 113 —— 请求失败 502、响应结构异常 502，同样依赖真实网络行为；
  - 164 —— app.run(...)，只在直接执行 python app.py 时才会运行，pytest
    里永远不会走到。

  作业要求是"按覆盖率输出补充必要测试"，不是追求
  100%。把这些外部依赖和入口启动的代码留在外面，是合理的取舍。

  ---

  你现在要做的事

  重新跑覆盖率：

  cd "C:\Users\Aa233\Desktop\课程\智能化软件系统与工程\Rep\isse-lab5-chat-ci"
  .\.venv\Scripts\python.exe -m pytest -q --cov=app --cov-report=term-missing
  --cov-fail-under=70

  观察重点

  - 用例数应从 2 条变成 9 条；
  - Cover 应该在 85%~90% 左右（22 条未覆盖里补上了 12 条）；
  - 这次命令不应再出现 FAIL Required test coverage of 70% not
    reached，$LASTEXITCODE 应为 0；
  - 剩余 Missing 应只剩 63-77、110-113、164 这几处。

  需要你反馈的内容

  新的覆盖率表格和最终结论。确认通过后，我们就把这条已经验证过的命令写进
  .github/workflows/ci.yml，推到 GitHub 上去看云端运行——这是任务 1 的最后一步。

> =============================================================================
  ====================== tests coverage =======================================
  ============================================================
  _____________________________________________________________________________
  _____ coverage: platform win32, python 3.13.6-final-0 _______________________
  ____________________________________________________________

  Name     Stmts   Miss  Cover   Missing
  --------------------------------------
  app.py      73      9    88%   64-77, 108-113, 164
  --------------------------------------
  TOTAL       73      9    88%
  Required test coverage of 70% reached. Total coverage: 87.67%
  9 passed in 0.48s
  现在9条测试全部通过了，实际覆盖率是87.67%，已经超过70%的要求。

  剩下没覆盖的代码，我理解主要是DeepSeek真实请求和响应处理、请求失败或响应异常
  的情况，还有直接运行app.py时的启动入口。不过具体每一段代码我还不太清楚。

  Thought for 13s (ctrl+o to expand)

● 先把你问的三处未覆盖代码讲透。

  未覆盖的三段分别是什么

  64-77 —— call_deepseek() 的网络部分

  64    response = requests.post(          # 向 DeepSeek 发 HTTP POST
  65        DEEPSEEK_API_URL,              #
  https://api.deepseek.com/chat/completions
  66        headers={"Authorization": f"Bearer {api_key}"},
  67        json={
  68            "model": DEEPSEEK_MODEL,   # deepseek-chat
  69            "messages": [{"role": "user", "content": message}],
  70        },
  71        timeout=30,
  72    )
  74    response.raise_for_status()        # 4xx/5xx → 抛 HTTPError
  75    data = response.json()             # 响应体解析成 JSON
  77    return data["choices"][0]["message"]["content"]

  - 64-72 是一次完整的出站请求：把 API Key 放进 Authorization
    头，把模型名和用户消息放进请求体，timeout=30 防止卡死。
  - 74 把 HTTP 状态码转换成异常。没有这句，500、401
    这类错误会被当成正常响应继续往下走，最后在 75 行莫名其妙地失败。
  - 75-77 是从返回结构里取回复文本的固定路径。

  为什么测不到：9 条用例里，凡是走创建流程的都把整个 call_deepseek 替换成了
  lambda，函数体一行都没执行；唯一没 mock 的那条在 62 行就因为缺 Key
  抛异常提前返回了，从没走到 64。

  要覆盖它需要：把 requests.post mock 成一个返回假响应对象的函数，让 64-77
  真实执行。这样就变成在测"请求怎么拼、返回怎么解析"——有价值，但超出"必要测试"的
  范围。

  108-113 —— create_message() 的两个 502 分支

  108    except requests.RequestException as exc:   # 网络错误、超时、HTTPError
  110        return jsonify({"error": f"调用 DeepSeek API 失败：{exc}"}), 502
  111    except (KeyError, IndexError):              # 响应结构不是预期的样子
  113        return jsonify({"error": "DeepSeek 返回了无法解析的响应"}), 502

  - 108-110：模型服务连不上、超时、或者返回 4xx/5xx 时走这里。
  - 111-113：请求成功了，但返回的 JSON 里没有 choices[0].message.content
    这条路径，data["choices"][0] 会抛 KeyError 或 IndexError。

  为什么测不到：模型调用被 mock 了就不会抛异常；缺 Key 走的是 107 行的
  ValueError 分支，跟这两条无关。

  顺带讲清 500 和 502 的区别 —— 这也是 REST 语义里很实用的一个点：

  ┌────────┬──────────────────────────────────┬──────────────────────────────┐
  │ 状态码 │               含义               │           你的场景           │
  ├────────┼──────────────────────────────────┼──────────────────────────────┤
  │ 500    │ 服务端自己出了问题               │ 忘了配 DEEPSEEK_API_KEY      │
  ├────────┼──────────────────────────────────┼──────────────────────────────┤
  │ 502    │ 服务端正常，但依赖的上游出了问题 │ DeepSeek                     │
  │        │                                  │ 挂机、超时、返回格式变了     │
  └────────┴──────────────────────────────────┴──────────────────────────────┘

  164 —— app.run(...)

  163    if __name__ == "__main__":
  164        app.run(port=5001, debug=True)

  __name__ 的值取决于模块怎么被加载：直接执行 python app.py 时它是
  "__main__"，所以 164 会执行、服务启动；而 pytest 是 import app，__name__ 是
  "app"，条件不成立，这一行永远不执行。

  这是 Python
  的标准入口写法，不需要也不应该为它写测试。覆盖率报告里它永远缺席，是正常的。

  ---

  任务 1（最后一步）：添加工作流并推送

  为什么需要工作流

  现在测试能在本地跑，但每次改完代码，仍然要你记得手动执行那条命令。CI
  的价值是把这条命令挂到代码推送这个动作上：只要有人 push 或发起 PR，GitHub
  就自动跑一遍，每个提交都有一份检查结果，而不是靠自觉。

  一个工作流的四个层次

  工作流是一个 YAML 文件，放在仓库根目录的 .github/workflows/ 下。GitHub
  只会从这个目录发现工作流。

  ┌─────────────────┬─────────────────────────────────────┬─────────────┐
  │      层次       │                含义                 │  对应配置   │
  ├─────────────────┼─────────────────────────────────────┼─────────────┤
  │ event 事件      │ 什么时候触发                        │ on:         │
  ├─────────────────┼─────────────────────────────────────┼─────────────┤
  │ workflow 工作流 │ 一个 YAML 文件，可以由多个 job 组成 │ 文件本身    │
  ├─────────────────┼─────────────────────────────────────┼─────────────┤
  │ job 任务        │ 一组工作，在一个 runner 上执行      │ jobs.test   │
  ├─────────────────┼─────────────────────────────────────┼─────────────┤
  │ step 步骤       │ job 内按顺序执行的最小单位          │ - name: ... │
  └─────────────────┴─────────────────────────────────────┴─────────────┘

  用到的几个关键字：

  - on —— 触发条件，如 push 到 main、向 main 发 PR；
  - runs-on —— 用哪台机器执行（ubuntu-latest 是 GitHub 提供的云端虚拟机）；
  - uses —— 调用别人写好的现成 Action（检出代码、安装 Python）；
  - run —— 直接执行 shell 命令。

  云端环境是干净的：runner 上既没有你的 .venv，也没有你机器上那个碰巧装了 flask
  的全局 Python。所以 job 里必须显式做三件事：检出代码 → 准备 Python →
  按依赖清单安装。这就是前面反复强调"依赖清单必须准确、必须进仓库"的原因。

  我把命令写成和你本地验证过的完全一致的那条——本地能过，云端才有同样的判断标准。
● Write(c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Rep/isse-lab5-chat-ci/.
       github/workflows/ci.yml)
  ⎿  Wrote 35 lines to c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Rep
     /isse-lab5-chat-ci/.github/workflows/ci.yml
       1 name: CI
       2
       3 # 什么时候触发：推送 main 分支、或向 main 发 Pull Request
       4 on:
       5   push:
       6     branches: [main]
       7   pull_request:
       8     branches: [main]
       9
      10 jobs:
     … +28 lines (ctrl+o to expand)

  Thought for 2s (ctrl+o to expand)

● 工作流已写好：.github/workflows/ci.yml。

  ┌────────┬───────────────────────┬───────────────────────────────────────┐
  │  配置  │       本次取值        │                 说明                  │
  ├────────┼───────────────────────┼───────────────────────────────────────┤
  │ 触发   │ push / PR 到 main     │ 推送到其他分支不会触发                │
  ├────────┼───────────────────────┼───────────────────────────────────────┤
  │ runs-o │ ubuntu-latest         │ GitHub 提供的云端虚拟机，每次运行都是 │
  │ n      │                       │ 一台全新机器                          │
  ├────────┼───────────────────────┼───────────────────────────────────────┤
  │ Python │ 3.13                  │ 与你本地 3.13.6 对齐；云端默认版本可  │
  │        │                       │ 能不同，必须显式指定                  │
  ├────────┼───────────────────────┼───────────────────────────────────────┤
  │ 依赖   │ requirements.txt +    │ 运行依赖和测试依赖分开装              │
  │        │ requirements-dev.txt  │                                       │
  ├────────┼───────────────────────┼───────────────────────────────────────┤
  │ 测试   │ 和本地完全相同的那条  │ 本地能过，云端才有同样的判断标准      │
  │        │ 命令                  │                                       │
  └────────┴───────────────────────┴───────────────────────────────────────┘

  ---

  你现在要做的事

  1. 提交并推送

  cd "C:\Users\Aa233\Desktop\课程\智能化软件系统与工程\Rep\isse-lab5-chat-ci"
  git add .github/workflows/ci.yml
  git commit -m "Lab5: 添加 GitHub Actions 工作流"
  git push

  2. 查看云端运行

  推送后打开：

  https://github.com/Bekzat070101/isse-lab5-chat-ci/actions

  观察重点

  - 刚推送完，列表里会出现一条以你提交信息命名（Lab5: 添加 GitHub Actions
    工作流）的运行，状态先是黄色圆点（排队或执行中），几十秒后变成绿色对勾；
  - 点进去，左侧能看到 job 名称 test，点击后展开右侧的步骤列表，应该依次是
    Checkout → Set up Python → Install dependencies → Run tests with coverage；
  - 点开 Run tests with coverage
    这一步的日志，拖到最后，应该看到和本地一样的内容：9 passed、TOTAL 73 9
    88%、Required test coverage of 70% reached. Total coverage: 87.67%；
  - 核对提交：详情页顶部会显示这次运行对应的 commit SHA
    和提交信息，确认它就是你刚才推的那个提交，而不是更早的；
  - 如果某一步是红色叉号，点开那一步看日志末尾的报错——最常见的是依赖装不上或路径
    不对。

  需要你反馈的内容

  1. 这次运行是否成功（绿色），共跑了几步；
  2. Run tests with coverage 步骤日志里的测试数量和覆盖率数字；
  3. 这次运行对应的 commit SHA 或提交信息，以及运行链接。

  这一步暂时不用截图。按作业要求，cloud-passed.png
  要展示"云端通过的覆盖率与冒烟日志"，等任务 3
  把冒烟检查加进工作流之后再一起截。现在只要把这次运行的链接留住即可。

  确认云端通过后，进入任务 2：故意改坏一处功能，观察失败并修复。

> 我已经push了，GitHub Actions也成功触发了，但是这次云端运行没有通过。

  Thought for 5s (ctrl+o to expand)

● Bash(cd
      "c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Rep/isse-lab5-chat-ci"
      && echo "=== 已推送到远端的文件 ===" && git ls-tree -r --name-only
      origin/main && echo "" && echo "=== 本地…)
  ⎿  (No output)

  Thought for 6s (ctrl+o to expand)

● 找到原因了，是我这边的疏漏——写测试的时候没有提醒你提交它们。

  看远端实际收到的东西：

  已推送到 origin/main：
    .env.example
    .github/workflows/ci.yml
    .gitignore
    app.py
    frontend/...
    requirements.txt          ← 只有运行依赖

  本地未提交：
    ?? requirements-dev.txt   ← 测试依赖没推上去
    ?? tests/                 ← 测试文件也没推上去

  工作流第一步 Install dependencies 执行的是：

  python -m pip install -r requirements.txt -r requirements-dev.txt

  云端拿到的是一个没有 requirements-dev.txt 的仓库，pip 会直接报错退出：

  ERROR: Could not open requirements file:
  [Errno 2] No such file or directory: 'requirements-dev.txt'

  这一步非零退出，job 立即中止，后面的测试步骤根本不会执行。

  这个失败很典型，值得记住

  本地一切正常、云端必然失败，原因就一条：云端只有你 push
  上去的那个提交里的文件。

  你本地磁盘上有 tests/ 和 requirements-dev.txt，但提交历史里没有。Git
  的提交是按你 git add 时明确选中的路径来打包的——你上次执行的是 git add
  .github/workflows/ci.yml，只加了那一个文件。git status 当时其实已经列出了两个
  ??（未跟踪），那就是警示信号。

  这也是 CI
  的第一个实际价值：它替你发现了"本地能跑但仓库不完整"这类问题。如果没有
  CI，这个问题要等到助教拉取代码时才会暴露。

  ---

  你现在要做的事

  1. 先去看日志，确认失败位置

  打开 https://github.com/Bekzat070101/isse-lab5-chat-ci/actions
  ，点进那条红色运行 → 左侧 job test → 找到带红叉的步骤。

  需要确认：红叉出现在哪一步，报错文字是不是上面那段 Could not open requirements
  file。

  2. 补提交并推送

  cd "C:\Users\Aa233\Desktop\课程\智能化软件系统与工程\Rep\isse-lab5-chat-ci"
  git status
  git add -A
  git commit -m "Lab5: 添加测试与测试依赖"
  git push

  git add -A 会把所有改动（新增、修改、删除）都加进暂存区，适合这种"补遗漏"的场
  景。提交前先看 git status，确认列出的正是 requirements-dev.txt 和 tests/
  两项，没有别的东西混进去。

  观察重点

  - 推送后会新出现一条运行，它不是旧的变绿，而是对应新提交 SHA
    的一条新记录。旧的那条永远保持红色——它检查的是 62b4644
    那个残缺的提交，而这个提交的历史不会因为后面的补提交而改变；
  - 新运行的 Install dependencies 应该成功，Run tests with coverage 里应出现 9
    passed 和 87.67%；
  - 刷新仓库首页的文件列表，应该能看到 tests/ 目录和 requirements-dev.txt。

  需要你反馈的内容

  1. 旧运行里红叉具体在哪一步、报错文字；
  2. 新运行是否变绿，Run tests with coverage 的测试数与覆盖率；
  3. 新运行的链接。

  说明两点：

  - 这次失败是环境缺文件，不能当作任务 2 的 failed.png
    证据。那张截图要求能看清"失败的测试名和断言"，所以任务 2
    的"故意改坏一处功能"我们还要正式做一遍；
  - 但这次经历正好预演了任务 2 的核心：失败 → 读日志定位 → 修复 → 新提交 →
    新运行通过。

> On branch main
  Your branch is up to date with 'origin/main'.

  Untracked files:
    (use "git add <file>..." to include in what will be committed)
          requirements-dev.txt
          tests/

  nothing added to commit but untracked files present (use "git add" to track)
  warning: in the working copy of 'requirements-dev.txt', LF will be replaced
  by CRLF the next time Git touches it
  warning: in the working copy of 'tests/test_chat_api.py', LF will be replaced
  by CRLF the next time Git touches it
  [main c6ef544] Lab5: 添加测试与测试依赖
   2 files changed, 156 insertions(+)
   create mode 100644 requirements-dev.txt
   create mode 100644 tests/test_chat_api.py
  Enumerating objects: 6, done.
  Counting objects: 100% (6/6), done.
  Delta compression using up to 24 threads
  Compressing objects: 100% (3/3), done.
  Writing objects: 100% (5/5), 2.50 KiB | 2.50 MiB/s, done.
  Total 5 (delta 1), reused 0 (delta 0), pack-reused 0 (from 0)
  remote: Resolving deltas: 100% (1/1), completed with 1 local object.
  To https://github.com/Bekzat070101/isse-lab5-chat-ci.git
     62b4644..c6ef544  main -> main

  是不是git push这一步出现的问题

  Thought for 5s (ctrl+o to expand)

● 不是。git push 这一步是成功的，看最后一行：

  62b4644..c6ef544  main -> main

  这表示远端 main 从 62b4644 前进到了 c6ef544，两个新文件已经推上去了。

  问题发生在 git add / git commit，不在 push

  关键在于理解 Git 的文件流转路径：

  ┌──────────┬────────────┬──────────────────────────────────┐
  │   阶段   │    命令    │             发生什么             │
  ├──────────┼────────────┼──────────────────────────────────┤
  │ 工作区   │ 你编辑文件 │ 文件只存在于磁盘上，Git 不管     │
  ├──────────┼────────────┼──────────────────────────────────┤
  │ 暂存区   │ git add    │ 明确告诉 Git："这些改动我要提交" │
  ├──────────┼────────────┼──────────────────────────────────┤
  │ 本地仓库 │ git commit │ 打包成一个版本快照，带 SHA       │
  ├──────────┼────────────┼──────────────────────────────────┤
  │ 远端     │ git push   │ 把已提交的快照上传               │
  └──────────┴────────────┴──────────────────────────────────┘

  git push 只能上传提交，不能上传文件。 如果一个文件从没被 git add + git commit
  过，它在 Git 眼里就不存在——push 的时候压根没有东西可以发送，也不会报错。

  所以之前那次失败的分界线很清楚：tests/ 和 requirements-dev.txt
  在工作区待着，从没进入暂存区，也就没进入任何提交，云端仓库自然没有它们。你刚才
  的输出也印证了这一点：

  Untracked files:
          requirements-dev.txt
          tests/
  nothing added to commit but untracked files present

  Untracked 就是"Git 看见了，但你没有让它跟踪"。

  判断自己是不是漏了东西，最可靠的方法是推送前看一眼 git status：只要还有
  Untracked files 或 Changes not staged，就说明还有内容没进这次提交。

  关于那两条 CRLF 警告

  warning: in the working copy of 'requirements-dev.txt', LF will be replaced by
  CRLF

  这是 Windows 上 Git 的换行符自动转换（core.autocrlf=true：仓库里存
  LF，检出到本地转成 CRLF）。对你的 Python 和 YAML 文件没有影响，pytest 和
  GitHub Actions 都能正常解析，不需要处理。

  ---

  你现在要做的事

  去 Actions 页面确认新运行：

  https://github.com/Bekzat070101/isse-lab5-chat-ci/actions

  观察重点

  - 列表里应该多了一条对应提交 c6ef544（提交信息 Lab5:
    添加测试与测试依赖）的运行；
  - 它应该走完全部 4 个步骤并变成绿色；
  - 点开 Run tests with coverage 看日志末尾：9 passed、TOTAL 73 9 88%、87.67%；
  - 对比一下：62b4644 那条仍是红色，两条运行对应不同提交，各自检查各自的代码。

  需要你反馈的内容

  1. 新运行是否变绿，共几个步骤全部通过；
  2. Run tests with coverage 的测试数和覆盖率；
  3. 新运行的链接。

  确认通过后，我们正式进入任务 2：故意改坏一处已被测试覆盖的功能，观察 CI
  如何失败，再从日志定位原因并修复。

> 这次云端运行已经成功了，状态是绿色的，commit是c6ef544，提交信息是Lab5:
  添加测试与测试依赖，整个运行耗时23秒，test这个job也显示通过了。
  https://github.com/Bekzat070101/isse-lab5-chat-ci/actions/runs/40188851592

  Thought for 11s (ctrl+o to expand)

● 云端通过，提交 c6f544 → 链接记下了。现在进入任务 2。

  任务 2：故意制造一次功能回归

  为什么要做这件事

  CI 最有价值的时刻不是"通过"，而是**"有人改坏了东西，它立刻拦住了"**。但你可能
  从没亲眼见过它拦住的样子——所以这次我们主动制造一次失败。

  这次实验的规则要记清楚：

  - 修改应用代码，引入一个真实的 bug；
  - 测试一个字都不改，它保持原来对功能的要求；
  - 推送 → 观察失败 → 从日志定位 → 修复 → 再次推送。

  这不是在"测试写得不好"，恰恰相反：测试守住的是一条已经约定好的功能契约，代码没
  兑现契约，测试就该红。

  我准备改哪一处

  DELETE /api/messages/<id> 接口，当前实现（app.py:151-160
  (isse-labs/lab2/别克扎提·拜别提-2500016663/app.py#L151-L160)）：

  @app.route("/api/messages/<int:message_id>", methods=["DELETE"])
  def delete_message(message_id):
      for index, record in enumerate(messages):
          if record["id"] == message_id:
              messages.pop(index)          # 真的从列表里移除
              return "", 204
      return jsonify({"error": f"id 为 {message_id} 的记录不存在"}), 404

  我打算改成：接口仍然返回 204 表示成功，但不再真正删除记录——也就是把
  messages.pop(index) 拿掉，直接 return "", 204。

          if record["id"] == message_id:
              # 实验：故意不删除，但仍然返回成功
              return "", 204

  哪个测试会抓住它

  test_message_crud_flow 的最后三行：

  deleted = client.delete(f"/api/messages/{message_id}")
  assert deleted.status_code == 204                              # ← 仍然成立
  assert client.get("/api/messages").get_json() == []            # ← 在这里失败

  注意这个细节：第一条断言依然会通过，因为接口确实返回了 204。真正发现问题的是第
  二条——它不看接口自己说成没成功，而是回头再查一遍数据，确认记录真的没了。

  这就是"只检查状态码不够"的实际例子，也是为什么 CRUD 测试要在删除之后再加一次
  GET。

  预期你会在日志里看到

  失败时 pytest 会打印类似：

  FAILED tests/test_chat_api.py::test_message_crud_flow
      assert [{'id': 1, 'message': '改过的内容', 'reply': '这是一条固定回复'}]
  == []
  1 failed, 8 passed

  预期值 []（应该没有记录了）vs
  实际值（那条记录还在）——一眼就能看出是删除没生效。

  注意 8 passed 说明其他 8 条用例仍然通过：这才是好测试的特征，一个 bug
  只让一条相关的用例变红，而不是把整个套件炸掉。

  ---

  需要你确认

  改动方案就是上面这一处（拿掉 messages.pop(index)）。确认后我就修改代码，然后你
  负责提交、推送、看日志、截图。

  另外提前说明三件事，免得你到时候困惑：

  1. 不要改测试。哪怕你觉得"测试太严格了"也不要动——这次的实验对象就是应用代码；
  2. 不要 --force
     推送或回退历史。正常提交新版本即可，失败的那条运行要保留下来作为证据；
  3. 失败后不要急着修复。先把失败日志看清楚、截好图，我们对照着解释完，再改回来
     。

  如果你同意，回复我一声，我就改代码。

> 我没问题

  Thought for 3s, read 1 file (ctrl+o to expand)

● Update(c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Rep/isse-lab5-chat-ci/
        app.py)
  ⎿  Added 1 line, removed 1 line
      153      """删除指定 id 的记录。"""
      154      for index, record in enumerate(messages):
      155          if record["id"] == message_id:
      156 -            messages.pop(index)                               
      156 +            # 实验：故意不真正删除，但仍然返回成功            
      157              # 204 No Content：表示删除成功，响应没有正文
      158              return "", 204
      159  

  Thought for 1s (ctrl+o to expand)

● Bash(cd
      "c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Rep/isse-lab5-chat-ci"
      && git diff && echo "=== 测试文件是否被改动 ===" && git status --short
      tests/)
  ⎿  (No output)

  Thought for 5s (ctrl+o to expand)

● 代码已改好，diff 确认只有一行、测试文件完全没动：

       for index, record in enumerate(messages):
           if record["id"] == message_id:
  -            messages.pop(index)
  +            # 实验：故意不真正删除，但仍然返回成功
               # 204 No Content：表示删除成功，响应没有正文
               return "", 204

  ---

  你现在要做的事

  1. 提交并推送这次改动

  cd "C:\Users\Aa233\Desktop\课程\智能化软件系统与工程\Rep\isse-lab5-chat-ci"
  git status
  git add app.py
  git commit -m "Lab5: 删除接口仍返回成功但不再移除记录"
  git push

  这里用 git add app.py 而不是 git add
  -A，是为了精确控制这次提交只包含这一处改动。提交前 git status 应该只显示
  modified: app.py。

  2. 打开 Actions 查看这次运行

  https://github.com/Bekzat070101/isse-lab5-chat-ci/actions

  3. 顺着日志往下找，理解每一层信息

  失败日志的信息是分层递进的，从外到内看：

  ┌────────┬─────────────────────────────────────┬──────────────────────────┐
  │  层次  │            你会看到什么             │      它回答什么问题      │
  ├────────┼─────────────────────────────────────┼──────────────────────────┤
  │ 运行列 │ 红色叉号 + 提交信息                 │ 哪次提交出问题了         │
  │ 表     │                                     │                          │
  ├────────┼─────────────────────────────────────┼──────────────────────────┤
  │ job    │ test 显示失败                       │ 哪个任务失败了           │
  ├────────┼─────────────────────────────────────┼──────────────────────────┤
  │ step   │ Run tests with coverage 上有红叉    │ 是哪一步失败（前面三步都 │
  │        │                                     │ 成功了）                 │
  ├────────┼─────────────────────────────────────┼──────────────────────────┤
  │ 测试输 │ FAILED tests/test_chat_api.py::test │ 哪条用例失败             │
  │ 出     │ _message_crud_flow                  │                          │
  ├────────┼─────────────────────────────────────┼──────────────────────────┤
  │ 断言详 │ assert [...] == []                  │ 哪一行断言、差在哪       │
  │ 情     │ 加上方框里的预期/实际               │                          │
  ├────────┼─────────────────────────────────────┼──────────────────────────┤
  │ 汇总行 │ 1 failed, 8 passed in ...           │ 影响范围——只有这一条受影 │
  │        │                                     │ 响                       │
  ├────────┼─────────────────────────────────────┼──────────────────────────┤
  │ 退出码 │ step 末尾的 exit code 1             │ 为什么整个 job 被判失败  │
  └────────┴─────────────────────────────────────┴──────────────────────────┘

  特别留意最后一项：pytest 进程以非零状态码退出，GitHub Actions
  才把它判定为失败。CI 不看你说"我通过了"，只看命令的退出码——这也是为什么
  --cov-fail-under=70 能让覆盖率不足变成一次"失败"。

  点击日志详情时，GitHub 会高亮显示失败行（红色背景），并给出 Expected / Actual
  的对照。

  4. 截图

  截一张能同时看清失败用例名、断言代码、预期值和实际值
  的图。如果一屏放不下，可以截两张，我会按顺序保存。

  截图里不要包含任何 Key 或 token（这次日志里不会有，放心）。

  ---

  需要你反馈的内容

  1. 失败出现在哪一步、哪条测试用例；
  2. 失败的那行断言是什么，预期值和实际值分别是什么；
  3. 汇总行（几条失败几条通过）；
  4. 你自己的解释：为什么接口返回了
     204、表面上"操作成功"，测试却仍然认为功能坏了；
  5. 失败运行的链接；
  6. 截图（发到这个对话里，我会保存到
     lab5/2500016663-Bekzat-Baybet/screenshots/failed.png）。

  先别修复。等我们一起把这条日志解释清楚、截图存好，再还原代码。

[Image #1]
  ⎿  [Image #2]

> 失败发生在Run tests with
  coverage这一步，前面的环境配置和依赖安装应该都通过了。
  失败的测试是tests/test_chat_api.py::test_message_crud_flow，出错位置是第66行
  ：
  最后的汇总是1 failed, 8 passed in 0.35s。覆盖率是87.50%，仍然超过70%的要求，
  但因为有一条测试失败，所以整个CI还是失败了。
  我理解是，接口返回204只能说明它返回了表示删除成功的状态码，但不代表数据真的被
  删除了。我们后面又用GET请求查询了一次，发现记录还在，所以测试就发现了这个问题
  。也就是说，如果只检查204这个状态码，就会漏掉这个bug。
  失败运行的链接：https://github.com/Bekzat070101/isse-lab5-chat-ci/actions/run
  s/40188851592

  Thought for 9s (ctrl+o to expand)

● 分析得很准确。先纠正一个小地方：你贴的运行链接是之前那次成功的运行（4018885159
  2），这次失败的是 #3，链接不一样，稍后麻烦从失败页面复制一下地址栏。

  先把截图存进课程目录：

● Bash(SRC="C:/Users/Aa233/AppData/Local/Temp/claude/c--Users-Aa233-Desktop-----
      ----------Lab/0c9152e8-80de-4f28-a6d0-5073f099f270/images"
      DST="c:/Users/Aa233/Desktop/…)
  ⎿  (No output)

  Thought for 5s (ctrl+o to expand)

● 两张截图已保存到课程个人目录：

  lab5/2500016663-Bekzat-Baybet/screenshots/
  ├── failed-1.png   ← 运行编号、失败 job、用例名 test_message_crud_flow
  └── failed-2.png   ← 断言详情、预期/实际 diff、汇总行、exit code 1

  日志与代码的对应关系

  你的判断基本到位，我再把它补完整。

  失败链条

  ┌────────────────────────────────┬─────────────────────┬──────────────────┐
  │          日志里的证据          │     对应的代码      │       说明       │
  ├────────────────────────────────┼─────────────────────┼──────────────────┤
  │ test_message_crud_flow         │ tests/test_chat_api │ 一条用例，做     │
  │                                │ .py 第 43-66 行     │ CRUD 全流程      │
  ├────────────────────────────────┼─────────────────────┼──────────────────┤
  │ 第 66 行 assert client.get("/a │ 测试的最后一条断言  │ 删除之后再查一次 │
  │ pi/messages").get_json() == [] │                     │ 列表             │
  ├────────────────────────────────┼─────────────────────┼──────────────────┤
  │ Left contains one more item:   │ app.py 的           │                  │
  │ {'id': 1, 'message':           │ delete_message      │ 记录没被移除     │
  │ '改过的内容', ...}             │                     │                  │
  ├────────────────────────────────┼─────────────────────┼──────────────────┤
  │ - [] / + [{...}]               │ 预期空列表，实际还  │ 差异一目了然     │
  │                                │ 有一条              │                  │
  ├────────────────────────────────┼─────────────────────┼──────────────────┤
  │ 1 failed, 8 passed             │ 只有这条用例受影响  │ 其他功能完好     │
  └────────────────────────────────┴─────────────────────┴──────────────────┘

  你的结论需要再深一层

  你说的是对的：204 只代表接口"声称"删除成功，不代表数据真的变了。

  我想再往前推一步，说明这个实验教的到底是什么：

  接口的返回值，是代码对自己行为的描述，不是对事实的陈述。 一个 bug
  完全可以是"返回值正确、内部状态错误"。所以测试的正确姿势是——不要相信接口说了什
  么，而要自己去查一遍实际状态。

  这正是 test_message_crud_flow 最后两条断言的分工：

  assert deleted.status_code == 204                    # 相信"它说自己删了"
  assert client.get("/api/messages").get_json() == []  # 亲自验证"真的删了没"

  第二条断言用的是外部可观察的状态（再发一次请求看看还剩什么），而不是接口的自述
  。这个思路在测试里非常通用：验证结果，而不是验证回执。

  一个很有意思的旁证

  注意覆盖率：

  ┌────────────────────┬───────┬──────┬────────┐
  │        状态        │ Stmts │ Miss │ Cover  │
  ├────────────────────┼───────┼──────┼────────┤
  │ 修复前（正常代码） │ 73    │ 9    │ 87.67% │
  ├────────────────────┼───────┼──────┼────────┤
  │ 出 bug 时          │ 72    │ 9    │ 87.50% │
  └────────────────────┴───────┴──────┴────────┘

  代码坏了一个功能，覆盖率几乎没变（只因为少了一条 messages.pop 语句，总数从 73
  掉到 72）。覆盖率对"逻辑写错了"这类问题完全不敏感——那几行代码照样被执行，只是
  行为变了。

  这就是我之前说的"覆盖率不等于正确性"最直接的实证：覆盖率回答"测到没有"，断言回
  答"对不对"。两者缺一不可。

  这个 bug 在真实产品里长什么样

  用户点"删除"，前端收到 204，把那条记录从界面上抹掉——看起来删成功了。但数据其实
  还在。用户刷新页面、或者换台设备打开，那条"已删除"的记录又出现了。这类问题往往
  要过很久才被发现，而且极难复现——因为从接口层面看，一切都"成功"了。

  ---

  现在开始修复

  修复的目标很明确：恢复原来约定的功能，让同一条测试重新通过。测试保持不动。

● Update(c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Rep/isse-lab5-chat-ci/
        app.py)
  ⎿  Added 1 line, removed 1 line
      153      """删除指定 id 的记录。"""
      154      for index, record in enumerate(messages):
      155          if record["id"] == message_id:
      156 -            # 实验：故意不真正删除，但仍然返回成功            
      156 +            messages.pop(index)                               
      157              # 204 No Content：表示删除成功，响应没有正文
      158              return "", 204
      159  

  Thought for 2s (ctrl+o to expand)

● Bash(cd
      "c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Rep/isse-lab5-chat-ci"
      && git diff && echo "=== 当前提交 ===" && git log --oneline -3)
  ⎿  (No output)

  Thought for 4s (ctrl+o to expand)
● 修复已完成，diff 就是把那一行恢复回去：

  -            # 实验：故意不真正删除，但仍然返回成功
  +            messages.pop(index)

  当前提交历史：

  a46452f ← 故意引入 bug（失败的那次）
  c6ef544 ← 添加测试（成功）
  62b4644 ← 添加工作流

  你现在要做的事

  1. 提交并推送修复

  cd "C:\Users\Aa233\Desktop\课程\智能化软件系统与工程\Rep\isse-lab5-chat-ci"
  git status
  git add app.py
  git commit -m "Lab5: 修复删除接口，恢复真正移除记录"
  git push

  2. 观察新运行

  https://github.com/Bekzat070101/isse-lab5-chat-ci/actions

  观察重点（这次有两点特别值得看）

  1. 旧的失败运行 #3 不会变绿。 它对应 a46452f 这个提交，检查的是当时那个有 bug
     的代码。GitHub 不会因为你现在提交了修复就回去重跑它——历史是不可变的，每次运
     行都锚定在它开始时的那个提交上。想看它变绿，只能点右上角 Re-run
     jobs，而那检查的仍然是同一份坏代码。
  2. 新运行对应新的 SHA。点进去核对提交信息是 Lab5:
     修复删除接口，恢复真正移除记录，而不是 a46452f。

  其他要确认的：
  - Run tests with coverage 里 9 passed；
  - 覆盖率回到 87.67%（Stmts 恢复成 73，Miss 仍是 9）；
  - 失败运行和新运行并排留在列表里，这就是"失败 → 修复"的完整证据。

  需要你反馈的内容

  1. 失败运行的链接（#3 那个，从地址栏复制，与之前贴的那条不同）；
  2. 新运行是否变绿，测试数与覆盖率；
  3. 新运行的链接。

  这一步不用截图。 按作业要求，failed.png
  只截失败测试和断言（已保存），云端成功的那张 cloud-passed.png
  要同时展示覆盖率和冒烟检查——冒烟检查还没做，等任务 3 完成后一起截。

> 修复已经推送了，这次GitHub Actions重新变绿了。
  87.67%
  https://github.com/Bekzat070101/isse-lab5-chat-ci/actions/runs/40189748170

  Thought for 6s (ctrl+o to expand)

● 云端恢复绿色，覆盖率回到 87.67%。任务 2 完成——失败证据和修复证据都在 Actions
  历史里了。

  （回头请把 #3 那个失败运行的链接补给我，材料里要成对记录。）

  现在进入任务 3。先读课程提供的冒烟脚本骨架：

  Thought for 8s, read 1 file (ctrl+o to expand)

● Bash(SRC="C:/Users/Aa233/AppData/Local/Temp/lab5-materials/smoke_test.py"
      DST="c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Rep/isse-lab5-chat-c
      i/scripts/smoke_test.py"…)
  ⎿  (No output)

  Thought for 5s (ctrl+o to expand)

● 骨架已复制到 scripts/smoke_test.py。

  任务 3：冒烟检查

  它和 pytest 测的不是一回事

  前面的测试用 test_client，它在同一个进程内直接把请求交给 Flask
  处理，不经过网络、不启动服务。它验证的是"Flask
  对象收到请求后的处理逻辑对不对"。

  但真实部署还有一整层可能出问题的地方：

  - 应用能不能作为服务启动起来（入口配置、flask run 参数、依赖是否齐全）；
  - 端口能不能监听、进程会不会启动后立刻崩溃；
  - HTTP 层是否正常（响应头、Content-Type、状态码）；
  - 静态文件路径在不同的工作目录下还能不能找到。

  冒烟检查（smoke test）就是快速确认"这堆东西点火之后能不能冒烟"——不深入验证每个
  功能，只确认应用能启动、能对外响应最基本的请求。

  你的 app.py
  里就有一个真实的隐患值得这类检查覆盖：send_from_directory("frontend",
  "index.html") 用的是相对路径，它会相对于进程的当前工作目录来解析。test_client
  测试时工作目录恰好是仓库根，所以能过；但如果换成别的启动方式、从别的目录启动，
  这个路径就可能失效。冒烟脚本在 PROJECT_ROOT 下启动进程，正好把这一层也覆盖到。

  骨架已经帮你做了什么

  ┌─────────┬─────────────────┬────────────────────────────────────────────┐
  │  环节   │      函数       │                    作用                    │
  ├─────────┼─────────────────┼────────────────────────────────────────────┤
  │ 选端口  │ choose_port()   │ 向系统要一个空闲临时端口，避免和你开发时占 │
  │         │                 │ 用的 5001 冲突                             │
  ├─────────┼─────────────────┼────────────────────────────────────────────┤
  │ 启动    │ subprocess.Pope │ 用 python -m flask --app app:app run       │
  │         │ n               │ 真正拉起一个进程                           │
  ├─────────┼─────────────────┼────────────────────────────────────────────┤
  │ 等待就  │ wait_for_server │ 反复尝试连接端口，最多等 20                │
  │ 绪      │ ()              │ 秒；进程提前退出会立即报错并打印启动日志   │
  ├─────────┼─────────────────┼────────────────────────────────────────────┤
  │ 检查    │ check_http()    │ 请求首页（要 HTML）和连通性接口（要 JSON   │
  │         │                 │ 且内容相符）                               │
  ├─────────┼─────────────────┼────────────────────────────────────────────┤
  │ 清理    │ finally         │ 无论成功失败都终止进程，5 秒不退则强杀     │
  ├─────────┼─────────────────┼────────────────────────────────────────────┤
  │ 判定    │ sys.exit(1)     │ 任何一步抛异常 → 非零退出码 → CI 判定失败  │
  └─────────┴─────────────────┴────────────────────────────────────────────┘

  脚本还通过环境变量给子进程准备了 DEEPSEEK_API_KEY=lab5-test-placeholder（占位
  Key，不是真实密钥）和
  LAB5_DATA_DIR（临时数据目录）。因为你的应用是内存存储，LAB5_DATA_DIR
  实际不会被读取；如果应用改成 JSON
  持久化，就要在初始化时读这个变量，让检查用独立的数据目录、不污染真实数据。

  你的四项配置——已经全部匹配，不需要改

  打开 scripts/smoke_test.py 第 18-22 行，逐项对照你的应用：

  ┌────────────────┬──────────────┬──────────┬──────────────────────────────┐
  │      配置      │  骨架默认值  │ 你的应用 │             依据             │
  ├────────────────┼──────────────┼──────────┼──────────────────────────────┤
  │                │              │          │ app.py 里是模块级变量 app =  │
  │ APP_IMPORT     │ "app:app"    │ ✅ 匹配  │ Flask(__name__)，即"模块 app │
  │                │              │          │  中的对象 app"               │
  ├────────────────┼──────────────┼──────────┼──────────────────────────────┤
  │ HOME_PATH      │ "/"          │ ✅ 匹配  │ serve_index() 返回           │
  │                │              │          │ frontend/index.html          │
  ├────────────────┼──────────────┼──────────┼──────────────────────────────┤
  │ HELLO_PATH     │ "/api/hello" │ ✅ 匹配  │ hello() 路由                 │
  ├────────────────┼──────────────┼──────────┼──────────────────────────────┤
  │ EXPECTED_HELLO │ {"message":  │ ✅ 匹配  │ hello() 的返回内容           │
  │                │ "你好"}      │          │                              │
  └────────────────┴──────────────┴──────────┴──────────────────────────────┘

  如果哪天你把应用改成了工厂函数 create_app()，第一项就要写成
  "app:create_app()"。这次不用动。

  ---

  你现在要做的事

  在仓库根目录运行冒烟脚本：

  cd "C:\Users\Aa233\Desktop\课程\智能化软件系统与工程\Rep\isse-lab5-chat-ci"
  .\.venv\Scripts\python.exe scripts\smoke_test.py

  一定要用 venv 的解释器。 脚本内部是用 sys.executable 去拉起子进程的——你用什么
  python 跑这个脚本，子进程就用哪个 python 启动 Flask。用 venv
  的，才能保证子进程里也有 flask。

  观察重点

  正常应该依次看到四行：

  服务已就绪
  PASS /
  PASS /api/hello
  服务已停止
  冒烟检查通过

  - 服务已就绪 —— 端口已经能连上，说明进程真的起来了；
  - 两行 PASS —— 首页返回了 HTML，/api/hello 返回了预期的 JSON；
  - 服务已停止 —— 清理逻辑执行了，没有残留进程占着端口；
  - 最后可以用 $LASTEXITCODE 确认退出码是 0。

  如果失败，脚本会打印 --- 应用启动日志 --- 和 Flask
  自己的报错——那通常是依赖缺失或入口写错，比 pytest 的报错更容易直接定位。

  需要你反馈的内容

  1. 脚本的完整输出；
  2. 是否出现了两行 PASS 和最后的 冒烟检查通过；
  3. 如果失败，把 应用启动日志 那段一起贴过来。

  本地跑通之后，下一步把它作为 Run smoke test 步骤加进
  ci.yml，推送后就能在云端拿到"测试 + 覆盖率 + 冒烟"三项都通过的
  cloud-passed.png 证据。

> PASS /
  PASS /api/hello
  服务已停止
  冒烟检查通过

  Thought for 7s (ctrl+o to expand)

● 冒烟检查本地通过。补一句：正常输出第一行应该是 服务已就绪（脚本在检查 HTTP
  之前就打这一行），你贴的内容里没包含它——可能是复制时漏掉了。方便的话确认一下它
  确实出现过。

  现在把它加进工作流。

● Update(c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Rep/isse-lab5-chat-ci/
        .github/workflows/ci.yml)
  ⎿  Added 5 lines
      33        - name: Run tests with coverage
      34          run: |
      35            python -m pytest -q --cov=app --cov-report=term-missi
          ng --cov-fail-under=70
      36 +                                                               
      37 +      # 真正启动一次服务，检查首页与连通性接口                 
      38 +      # 前面的步骤通过后才会执行到这里；本步失败同样会让整个 jo
         +b 失败                                                         
      39 +      - name: Run smoke test                                   
      40 +        run: python scripts/smoke_test.py                      

  Thought for 4s (ctrl+o to expand)

● 任务 3（续）：把冒烟检查加入 CI

  为什么要放进工作流

  本地跑通只说明你这台机器能启动应用。云端 runner 是一台全新的 Linux
  机器，它只有你通过 requirements.txt
  安装的依赖、只有仓库里的文件，工作目录也是它自己检出的位置。

  冒烟检查加进 CI 之后，每次推送都会额外回答一个问题：这次提交的代码，在一个干净
  环境里还能不能启动起来对外服务？

  pytest 那一层回答不了这个问题——test_client 根本不启动进程、不碰端口、不检查工
  作目录下的静态文件路径。两层检查覆盖的是不同的失效方式。

  它放在哪、怎么生效

  新步骤加在 Run tests with coverage 之后：

        - name: Run tests with coverage
          run: |
            python -m pytest -q --cov=app --cov-report=term-missing
  --cov-fail-under=70

        - name: Run smoke test
          run: python scripts/smoke_test.py

  GitHub Actions 的 step 是顺序执行、失败即停的：如果测试那一步失败（就像任务 2
  那样），冒烟步骤会显示为跳过、根本不会执行。只有前面全绿，才会走到启动服务这一
  步。反过来，冒烟脚本退出码非零时，它自己也会把这步标红、整个 job 判失败。

  云端为什么能跑得起来

  脚本只需要两样东西，云端都有：

  - Python 解释器 —— setup-python 装的 3.13；
  - flask 命令 —— 已经通过 requirements.txt 装好了。脚本内部用 sys.executable -m
    flask 启动，用的就是 CI 里那个 python；
  - 其余全是标准库（socket、subprocess、urllib、tempfile），不需要额外依赖。

  ---

  你现在要做的事

  1. 提交并推送

  cd "C:\Users\Aa233\Desktop\课程\智能化软件系统与工程\Rep\isse-lab5-chat-ci"
  git status
  git add .github/workflows/ci.yml scripts/smoke_test.py
  git commit -m "Lab5: 添加冒烟检查"
  git push

  注意 scripts/smoke_test.py 是新增文件，git status 里会显示为 ??
  scripts/。上次漏提交 tests/ 的教训在这里同样适用——git add
  时明确把路径列出来，提交前用 git status 核对。

  2. 看新的运行

  https://github.com/Bekzat070101/isse-lab5-chat-ci/actions

  观察重点

  - job test 的步骤列表里应该多出第五步 Run smoke test；
  - 点开它的日志，应该看到和本地一样的四行：服务已就绪、PASS /、PASS
    /api/hello、服务已停止，最后 冒烟检查通过；
  - Run tests with coverage 里仍然是 9 passed + 87.67%；
  - 整个 job 绿了，说明五项检查在云端一次跑完。

  3. 截图（这次要两张）

  一张截图只能显示一个步骤的日志，所以要分开截：

  ┌─────────────────────────────────────────────────────┬────────────────────┐
  │                      截图内容                       │     我会保存为     │
  ├─────────────────────────────────────────────────────┼────────────────────┤
  │ Run tests with coverage 日志末尾：9                 │                    │
  │ passed、覆盖率表格、Required test coverage of 70%   │ cloud-passed-1.png │
  │ reached                                             │                    │
  ├─────────────────────────────────────────────────────┼────────────────────┤
  │ Run smoke test 日志：服务已就绪、两行               │ cloud-passed-2.png │
  │ PASS、服务已停止、冒烟检查通过                      │                    │
  └─────────────────────────────────────────────────────┴────────────────────┘

  如果能在一张图里同时看到步骤列表（五个都带绿勾）会更好，可以在截步骤日志时带上
  左侧。

  ---

  需要你反馈的内容

  1. 新运行是否变绿，五个步骤是否都通过；
  2. Run smoke test 的日志内容；
  3. 运行链接；
  4. 两张截图。

  还要麻烦你补上任务 2 失败运行（#3）的链接，那个材料里需要。

  这些齐了，就进入最后一个、也是这次实验最有意思的部分：把同一份工作流切换到本机
  runner，让 CI 跑在你自己这台 Windows 电脑上。

[Image #3]
  ⎿  [Image #4]
  ⎿  [Image #5]

> https://github.com/Bekzat070101/isse-lab5-chat-ci/actions/runs/40195625462/jo
  b/121175717868
  Run python scripts/smoke_test.py
  服务已就绪
  PASS /
  PASS /api/hello
  服务已停止
  冒烟检查通过
  失败链接：https://github.com/Bekzat070101/isse-lab5-chat-ci/actions/runs/4018
  9239157

  Thought for 14s (ctrl+o to expand)

● 三张截图收到。先存进课程目录，并确认一下你的 CPU 架构（决定下载哪个 runner
  包）：

● Bash(SRC="C:/Users/Aa233/AppData/Local/Temp/claude/c--Users-Aa233-Desktop-----
      ----------Lab/0c9152e8-80de-4f28-a6d0-5073f099f270/images"
      DST="c:/Users/Aa233/Desktop/…)
  ⎿  (No output)

  Thought for 8s (ctrl+o to expand)

● 截图已保存：

  screenshots/
  ├── cloud-passed-1.png   ← 云端 #5：五个步骤全绿 + 覆盖率 87.67%
  ├── cloud-passed-2.png   ← Run smoke test 日志：服务已就绪 / PASS / PASS /
  已停止
  ├── failed-1.png         ← 任务 2 失败：job 与用例名
  └── failed-2.png         ← 任务 2 失败：断言、预期/实际、exit code 1

  失败链接也记下了：runs/40189239157（#3）。

  你的 CPU 是 x86_64 / AMD64，所以 runner 要选 Windows + x64。

  ---

  任务 4：切换到本机 runner

  runner 到底是什么

  前面所有检查都跑在 ubuntu-latest 上——那是 GitHub
  提供的一台云端虚拟机，每次运行都是全新的，用完即弃。

  runner 就是真正执行 job 的那个程序。 到目前为止，GitHub 自动提供并管理着这些
  runner。self-hosted runner 则是你在自己的电脑上安装并启动的程序：它主动连到
  GitHub，说"我在线，有任务就发给我"，然后 GitHub 把这个仓库的 job 派给它执行。

  这里有个重要的方向性：runner 是主动去 GitHub 拉任务的，不是 GitHub
  连进你的电脑。所以你的电脑不需要公网 IP、不需要开放端口，家里的网络也能用。

  三步：下载、注册、启动

  ┌──────┬───────────────────────────────┬──────────────────────────────────┐
  │ 步骤 │            做什么             │               结果               │
  ├──────┼───────────────────────────────┼──────────────────────────────────┤
  │ 下载 │ 取得适合你系统和 CPU 架构的   │ 得到一个可执行程序目录           │
  │      │ runner 程序                   │                                  │
  ├──────┼───────────────────────────────┼──────────────────────────────────┤
  │ 注册 │ 把这个 runner                 │ 仓库的 Runners                   │
  │      │ 关联到你的实验仓库            │ 列表里出现一个条目               │
  ├──────┼───────────────────────────────┼──────────────────────────────────┤
  │ 启动 │ 让 runner 连上 GitHub         │ 网页显示在线，终端显示 Listening │
  │      │ 并等待任务                    │  for Jobs                        │
  └──────┴───────────────────────────────┴──────────────────────────────────┘

  注册 token 是什么：config.cmd 命令里那个 --token
  是一张临时通行证，证明你有权限往这个仓库添加 runner。它由 GitHub
  在注册页面上临时生成（约 1 小时后失效），用完即弃。

  所以有三条纪律：

  - token 只用于本机终端，不要粘到对话里、不要截图、不要提交到仓库；
  - 注册完成后它就作废了，别人捡到也没用（但正在有效期内捡到就能往你仓库挂
    runner，所以还是别外传）；
  - 后面任务的截图里，如果终端正好显示过 token，注意避让。

  装在哪里

  runner 程序必须放在代码仓库之外。 它会在自己的目录里建一个 _work
  工作区，检出代码、跑命令都在那里。这个目录和你的开发目录完全是两回事——下面这一
  点马上就会变得很关键：

  ▎ runner 检出的是它自己的工作区副本，不是你在 Rep\isse-lab5-chat-ci
  ▎ 里编辑的那一份。
  ▎
  ▎ 这意味着你开发时用的那个 .venv（在
  ▎ Rep\isse-lab5-chat-ci\.venv）对本机任务的执行毫无帮助。runner 在 _work
  ▎ 里拿到一份干净的代码，它需要自己准备 Python 和依赖——这就是下一步我们要改
  ▎ ci.yml 的原因。

  我们统一装在 C:\actions-runner，它不在任何仓库里。

  ---

  你现在要做的事

  1. 创建目录并下载

  先打开一个新的终端窗口（后面要一直开着它跑 runner，别占用你开发用的那个）：

  mkdir C:\actions-runner
  cd C:\actions-runner

  如果提示权限不足，改成装到用户目录下：mkdir
  "$HOME\actions-runner"，后面路径相应替换。

  2. 从 GitHub 页面复制下载命令

  打开：

  https://github.com/Bekzat070101/isse-lab5-chat-ci/settings/actions/runners/new

  在 Runner image 一栏选择 Windows +
  x64，页面会给出当前版本的下载链接和命令，用页面上的实际版本号（下面的 2.XXX.X
  只是占位）：

  Invoke-WebRequest -Uri https://github.com/actions/runner/releases/download/v2.
  XXX.X/actions-runner-win-x64-2.XXX.X.zip -OutFile actions-runner-win-x64.zip

  Add-Type -AssemblyName System.IO.Compression.FileSystem
  [System.IO.Compression.ZipFile]::ExtractToCurrentDirectory((Resolve-Path
  .\actions-runner-win-x64.zip))

  3. 注册

  页面 Configure 一栏给的就是这条命令，token 直接复制页面上显示的：

  ./config.cmd --url https://github.com/Bekzat070101/isse-lab5-chat-ci --token
  <页面上的token>

  配置过程中会问几个问题，这样回答：

  ┌────────────┬─────────────────┬─────────────────────────────────────────┐
  │    提示    │      说明       │                  建议                   │
  ├────────────┼─────────────────┼─────────────────────────────────────────┤
  │ Enter the  │                 │                                         │
  │ name of    │ runner 的名字   │ 直接回车用默认值（你的电脑名）          │
  │ the runner │                 │                                         │
  ├────────────┼─────────────────┼─────────────────────────────────────────┤
  │ Enter any  │ 额外标签，用于  │ 直接回车，保持默认（self-hosted、Window │
  │ additional │ 在 runs-on      │ s、X64 会自动带上）                     │
  │  labels    │ 里精确匹配      │                                         │
  ├────────────┼─────────────────┼─────────────────────────────────────────┤
  │ Enter name │                 │                                         │
  │  of work   │ 工作区目录      │ 直接回车用 _work                        │
  │ folder     │                 │                                         │
  ├────────────┼─────────────────┼─────────────────────────────────────────┤
  │ 询问是否作 │ 服务方式会常驻  │                                         │
  │ 为 Windows │ 后台            │ 不选，我们前台运行即可                  │
  │  服务运行  │                 │                                         │
  └────────────┴─────────────────┴─────────────────────────────────────────┘

  4. 启动

  ./run.cmd

  观察重点

  - 注册结束时：应看到 √ Runner successfully added 和 √ Runner connection is
    good；
  - 网页上：回到
    https://github.com/Bekzat070101/isse-lab5-chat-ci/settings/actions/runners
    ，列表里会出现一条 runner 记录；此时状态是 Idle（在线待命，绿色圆点）；
  - 终端里：会持续显示 Listening for
    Jobs——这就是在等待任务。这个窗口现在起要保持打开；
  - 这个阶段还不会有任何任务被派过来：工作流里写的还是 runs-on:
    ubuntu-latest，GitHub 只会把任务发给云端。要让本机 runner
    接到活，必须改工作流。

  ---

  需要你反馈的内容

  1. 注册是否成功（Runner successfully added / connection is good）；
  2. 网页 Runners 列表里的状态（Idle / Offline）和 labels（应该是 self-hosted,
     Windows, X64 三个）；
  3. 终端是否停在 Listening for Jobs；
  4. 遇到任何报错，把报错文字发我——注意先检查里面有没有 token，有的话删掉再发。

  暂时不用截图。 本机 runner 的截图要等下一步改完
  ci.yml、任务真正在本机跑完之后再一起截（self-hosted-actions.png 和
  self-hosted-terminal.png 要能对应同一次任务）。

  runner 在线后告诉我，我讲下一步：把同一份 ci.yml 从 ubuntu-latest
  切到本机，并处理"本机怎么准备 Python 和依赖"这个问题。

> 注册成功
  Idle self-hosted Windows X64
  是的
  没有报错

  Thought for 24s (ctrl+o to expand)

● runner 在线（Idle，标签 self-hosted / Windows / X64），可以切工作流了。

● Write(c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Rep/isse-lab5-chat-ci/.
       github/workflows/ci.yml)
  ⎿  Added 16 lines, removed 15 lines
       9  
      10  jobs:
      11    test:
      12 -    # 在 GitHub 提供的 ubuntu 云端机器上执行                   
      13 -    runs-on: ubuntu-latest                                     
      12 +    # 切到本机 runner：self-hosted 会匹配到注册时自动带上的    
      13 +    # self-hosted / Windows / X64 这三个标签                   
      14 +    runs-on: self-hosted                                       
      15  
      16      steps:
      16 -      # 把当前提交的代码检出到 runner 的工作区                 
      17 +      # 把当前提交的代码检出到 runner 自己的工作区             
      18        - name: Checkout
      19          uses: actions/checkout@v4
      20  
      20 -      # 准备 Python。云端默认的 python 版本不一定是我们要的，显
         -式指定                                                         
      21 -      - name: Set up Python                                    
      22 -        uses: actions/setup-python@v5                          
      23 -        with:                                                  
      24 -          python-version: "3.13"                               
      21 +      # 本机执行用电脑上已安装的 Python，先确认它的版本和位置  
      22 +      - name: Show local Python                                
      23 +        run: |                                                 
      24 +          python --version                                     
      25 +          where.exe python                                     
      26  
      26 -      # 按依赖清单安装运行依赖与测试依赖                       
      27 -      - name: Install dependencies                             
      27 +      # runner 的工作区与日常开发目录不同，依赖要在工作区里重新
         +准备                                                           
      28 +      - name: Prepare virtual environment                      
      29          run: |
      29 -          python -m pip install --upgrade pip                  
      30 -          python -m pip install -r requirements.txt -r requirem
         -ents-dev.txt                                                   
      30 +          python -m venv .venv                                 
      31 +          .\.venv\Scripts\python.exe -m pip install --upgrade p
         +ip                                                             
      32 +          .\.venv\Scripts\python.exe -m pip install -r requirem
         +ents.txt -r requirements-dev.txt                               
      33  
      34        # 与本地验证过的命令完全一致：测试 + 覆盖率门槛
      35        - name: Run tests with coverage
      34 -        run: |                                                 
      35 -          python -m pytest -q --cov=app --cov-report=term-missi
         -ng --cov-fail-under=70                                         
      36 +        run: .\.venv\Scripts\python.exe -m pytest -q --cov=app 
         +--cov-report=term-missing --cov-fail-under=70                  
      37  
      38        # 真正启动一次服务，检查首页与连通性接口
      39        # 前面的步骤通过后才会执行到这里；本步失败同样会让整个 jo
          b 失败
      40        - name: Run smoke test
      40 -        run: python scripts/smoke_test.py                      
      41 +        run: .\.venv\Scripts\python.exe scripts\smoke_test.py  

  Thought for 7s (ctrl+o to expand)

● 工作流已改成本机执行。关键差异如下：

  ┌──────────┬────────────────────────┬────────────────────────────────────┐
  │    项    │        云端版本        │              本机版本              │
  ├──────────┼────────────────────────┼────────────────────────────────────┤
  │ runs-on  │ ubuntu-latest          │ self-hosted                        │
  ├──────────┼────────────────────────┼────────────────────────────────────┤
  │ Python   │ actions/setup-python   │ 展示电脑上已装的 Python（python    │
  │ 准备     │ 下载一个               │ --version + where.exe python）     │
  ├──────────┼────────────────────────┼────────────────────────────────────┤
  │ 依赖安装 │ 直接 pip install       │ 在工作区建 .venv 再装              │
  │          │ 到系统 Python          │                                    │
  ├──────────┼────────────────────────┼────────────────────────────────────┤
  │ 执行命令 │ python -m pytest ...   │ .\.venv\Scripts\python.exe -m      │
  │          │                        │ pytest ...                         │
  ├──────────┼────────────────────────┼────────────────────────────────────┤
  │ Shell    │ bash                   │ PowerShell（Windows runner 默认）  │
  │ 语法     │                        │                                    │
  └──────────┴────────────────────────┴────────────────────────────────────┘

  ---

  任务 4（续）：让同一份工作流跑在本机

  为什么改 runs-on 就够了

  runs-on 就是"这个 job 交给哪台机器跑"的筛选条件。GitHub 拿到 job
  后，会在所有注册到这个仓库的 runner 里找标签匹配的那一个：

  - 你刚注册的 runner 自动带了三个标签：self-hosted、Windows、X64；
  - 工作流写 runs-on: self-hosted，云端那些 ubuntu-latest 的 runner
    不匹配，只有你这台匹配；
  - 于是 job 被派到你电脑上执行。

  触发条件（on:）一个字都没改——同样的提交事件，只是执行的机器变了。

  为什么不能沿用云端那套准备步骤

  这是本阶段最核心的一点，值得单独讲清楚：

  ▎ runner 检出的是它自己的工作区副本，不是你在 Rep\isse-lab5-chat-ci
  ▎ 里编辑的那一份。

  runner 在 C:\actions-runner\_work\isse-lab5-chat-ci\isse-lab5-chat-ci\
  这样的目录里检出代码。这个目录：

  - 和你的开发目录完全是两处。你在开发目录里改的文件、建的
    .venv、装的依赖，runner 一点都看不到；
  - 每次运行前会被清理。actions/checkout 默认会执行 git clean
    -ffdx，把工作区里所有未跟踪的文件删掉——包括上一次运行留下的 .venv。

  所以"我以为电脑上装过了"这个假设完全不成立。job
  里必须把准备动作完整写一遍：准备 Python → 建虚拟环境 → 装依赖 →
  再执行命令。这也是为什么本机版本的 Prepare virtual environment
  步骤每次都要重跑（第一次会比较慢，几十秒）。

  云端的 setup-python 在这里也不再合适：本机 runner 就用电脑上已经装好的 Python
  3.13.6。Show local Python 那一步把版本和路径打印出来，万一以后环境出问题，日志
  里能立刻看到当时用的是哪个解释器。

  一个要知道的后果

  runs-on 是写在唯一那份工作流里的，所以从这次推送开始，所有新任务都会发给本机
  runner。等会儿取证结束、你按 Ctrl+C 停掉 runner
  之后，再推送代码的话，运行会一直停在 Queued / Waiting——因为没有任何在线的
  runner 能接。想恢复就跑 C:\actions-runner 下的 run.cmd 重新启动。

  先前的云端运行记录不会消失，它们仍然留在 Actions 历史里，作为"切换 runner
  之前"的证据。作业也明确说了：两种环境不要求是同一个提交。

  ---

  你现在要做的事

  1. 提交并推送

  cd "C:\Users\Aa233\Desktop\课程\智能化软件系统与工程\Rep\isse-lab5-chat-ci"
  git status
  git add .github/workflows/ci.yml
  git commit -m "Lab5: 工作流切换到本机 self-hosted runner"
  git push

  2. 同时盯两个地方

  A. 运行 runner 的那个终端窗口 —— 保持它可见。推送后应该很快看到变化：

  √ Connected to GitHub

  Current runner version: ...
  2026-10-25 ...  Running job: test
  2026-10-25 ...  Job test completed with result: Succeeded

  中间会滚动各步骤的日志，包括它检出的工作区路径——留意那个路径，它会明确显示这不
  是你的开发目录。

  B. Actions 页面 —— https://github.com/Bekzat070101/isse-lab5-chat-ci/actions

  打开最新那条运行，重点看：

  - job test 的详情页上，Runner 一栏显示的应该是你本机的 runner 名字（Idle
    列表里那个名字），而不是 GitHub Actions；
  - 五个步骤依次变绿；
  - Show local Python 的日志里能看到 Python 3.13.6 和你电脑上 python
    的实际路径；
  - Run tests with coverage 里应该还是 9 passed + 87.67%；
  - Run smoke test 里应该还是 服务已就绪 / 两行 PASS / 冒烟检查通过。

  3. 截图（两张，必须对应同一次运行）

  ┌───────────────────────────────────────────────┬──────────────────────────┐
  │                   截图内容                    │          保存为          │
  ├───────────────────────────────────────────────┼──────────────────────────┤
  │ Actions 页面上本机运行的结果：能看到 runner   │ self-hosted-actions.png  │
  │ 名称、五个步骤全绿                            │                          │
  ├───────────────────────────────────────────────┼──────────────────────────┤
  │ 本机终端接收任务并完成：Running job: test 到  │ self-hosted-terminal.png │
  │ completed with result: Succeeded              │                          │
  └───────────────────────────────────────────────┴──────────────────────────┘

  两张都要能看出是同一次任务（比如都出现同一个 job 名和时间）。

  4. 取证完成后停止 runner

  回到运行 runner 的终端，按 Ctrl+C 停止。停掉之后：

  - GitHub 上的 runner 状态会变成 Offline（这正常）；
  - 之后再推送代码，运行会一直排队等待，直到你重新启动 runner。

  ---

  需要你反馈的内容

  1. 本机终端有没有出现 Running job: test 和 completed with result: Succeeded；
  2. Actions 上那条运行的 Runner 名称、五个步骤是否全绿；
  3. 本机运行里 Run tests with coverage 的测试数与覆盖率；
  4. 运行链接；
  5. 两张截图。

  如果网页上运行长时间停在 Queued，或者终端里一直没有反应，先检查：runner
  是否还是 Idle、标签是不是 self-hosted、以及 job 详情页有没有提示 waiting for a
  runner to pick up this job。

[Image #6]
  ⎿  [Image #7]

> 1、有
  2、REVO；是的
  3、73      9    88%
  4、https://github.com/Bekzat070101/isse-lab5-chat-ci/actions/runs/40196744350
  /job/121179103371

  Thought for 23s (ctrl+o to expand)

● Bash(SRC="C:/Users/Aa233/AppData/Local/Temp/claude/c--Users-Aa233-Desktop-----
      ----------Lab/0c9152e8-80de-4f28-a6d0-5073f099f270/images"
      DST="c:/Users/Aa233/Desktop/…)
  ⎿  (No output)

  Thought for 3s (ctrl+o to expand)
● 本机运行成功——runner REVO 接收了任务，五个步骤全绿，73 statements / 9 missed /
  88%，1 分 2 秒完成。

  Actions 那张已保存为 self-hosted-actions.png。

  ---

  ⚠️ 先处理一件事：你的终端截图里有注册 token

  你发的第二张图（终端截图）里，--token
  后面的注册凭据是明文可见的。这张图不要放进提交材料，也不要发到任何地方。

  按作业要求，截图里必须省略注册 token——这张我需要你重拍一张。

  关于风险，实际情况是这样：

  - 这是注册 token，不是长期密钥。它在生成后约 1
    小时自动失效，你的截图里显示生成时间是 13:09，也就是说它已经快到期了；
  - 在有效期内，拿到它的人可以往你的仓库挂一个 runner；
  - 过期后它就完全没用了。所以不需要惊慌，也不需要重建仓库——但这一小时内不要外传
    这张图。

  我没有保存这张截图，课程目录里目前只有那张不含 token 的 Actions 截图。

  以后有个更省心的习惯：在启动 runner 之前先 Clear-Host 清屏。注册命令和 token
  留在滚动缓冲区里，很容易在后续截图时被一起带出来。

  ---

  这次运行里值得注意的细节

  ┌─────────────────────────────┬──────┬────────────────────────────────┐
  │            步骤             │ 耗时 │              说明              │
  ├─────────────────────────────┼──────┼────────────────────────────────┤
  │ Checkout                    │ 7s   │ 在 runner 自己的工作区检出代码 │
  ├─────────────────────────────┼──────┼────────────────────────────────┤
  │ Show local Python           │ 1s   │ 打印本机 Python 版本和路径     │
  ├─────────────────────────────┼──────┼────────────────────────────────┤
  │ Prepare virtual environment │ 37s  │ 最长的一步——建 .venv + 装依赖  │
  ├─────────────────────────────┼──────┼────────────────────────────────┤
  │ Run tests with coverage     │ 4s   │ 9 passed、88%                  │
  ├─────────────────────────────┼──────┼────────────────────────────────┤
  │ Run smoke test              │ 1s   │ 服务启动 → 两项 PASS → 停止    │
  └─────────────────────────────┴──────┴────────────────────────────────┘

  Prepare virtual environment 花 37
  秒，正好印证了前面讲的：每次运行都要从零准备依赖。因为 actions/checkout
  默认会清理工作区里所有未跟踪的文件，上一次运行留下的 .venv
  已经被删掉了。相比之下云端那一步只要 9 秒，因为云端机器有 pip
  缓存和更快的网络。

  还有一点：Checkout 花 7 秒、总耗时从云端的 17 秒变成 1 分 2 秒。本机 runner
  并不总是更快——它的价值在于"任务跑在你自己的机器上"这个事实本身：可以用本机特有
  的工具、内网资源、私有硬件，代价是自己维护环境。

  ---

  需要你补两样东西

  1. 重拍终端截图（不含 token）

  cd C:\actions-runner
  Clear-Host
  ./run.cmd

  清屏后启动，等它显示 Listening for Jobs。然后到 Actions 页面打开刚才那条运行
  #6，点右上角 Re-run all jobs —— 本机的新任务会立刻被 runner
  接到，终端会重新滚出这次执行的日志。

  这次截图只截 Running job: test 到 Job test completed with result: Succeeded
  这一段就够，不要往上滚到 config.cmd 那行。完成后按 Ctrl+C 停掉 runner。

  2. 补一张能看到 runner 名字的截图

  self-hosted-actions.png
  只显示了步骤列表。要证明任务确实跑在本机，最有说服力的是 Set up job
  步骤的日志——它会打印：

  Runner name: 'REVO'
  Machine name: 'REVO'

  在 Actions 页面上展开 Set up job 那一步，截下包含这两行的内容。我会存成
  self-hosted-actions-2.png。

  ---

  需要你反馈的内容

  1. 重拍的终端截图（确认里面没有 --token）；
  2. Set up job 日志的截图（含 Runner name / Machine name）；
  3. 重跑后终端里是否再次出现 completed with result: Succeeded。

  这两张齐了，本机 runner
  阶段的四项证据就完整了。之后剩下最后一段收尾：把最终应用复制到课程个人目录的
  app/、整理截图、导出对话轨迹到 AGENT_TRACE.md，然后发起课程 PR。

[Image #8]
  ⎿  [Image #9]

> 3、是的

  Thought for 17s (ctrl+o to expand)

● 终端截图这张没有 token（配置那一行被截在画面外），Actions 那张也把 Set up job
  里的 Runner name: 'REVO' / Machine name: 'REVO'
  显示出来了。两张对应同一次任务（#6，时间戳一致）。开始整理材料：

● Bash(SRC="C:/Users/Aa233/AppData/Local/Temp/claude/c--Users-Aa233-Desktop-----
      ----------Lab/0c9152e8-80de-4f28-a6d0-5073f099f270/images"
      DST="c:/Users/Aa233/Desktop/…)
  ⎿  (No output)

● Bash(SRC="c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Rep/isse-lab5-chat-
      ci"
      DST="c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Lab/isse-labs/lab5/2
      500016663-Bekzat-Baybet/app"…)
  ⎿  (No output)

  Thought for 13s (ctrl+o to expand)

● Bash(cd "c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Lab/isse-labs" &&
      echo "=== 当前分支 ===" && git rev-parse --abbrev-ref HEAD && echo "===
      待提交内容 ===" && git status --short…)
  ⎿  (No output)

  Thought for 9s (ctrl+o to expand)

● 材料已全部就位。这是本次实验的最后一段。

  整理材料并提交

  已经放好的内容

  lab5/2500016663-Bekzat-Baybet/
  ├── screenshots/
  │   ├── failed-1.png             任务 2：失败的 job 与用例名
  │   ├── failed-2.png             任务 2：断言、预期/实际、exit code 1
  │   ├── cloud-passed-1.png       任务 3：云端五步全绿 + 覆盖率 87.67%
  │   ├── cloud-passed-2.png       任务 3：冒烟检查日志
  │   ├── self-hosted-actions.png  任务 4：Set up job 显示 Runner/Machine = REVO
  │   └── self-hosted-terminal.png 任务 4：本机终端 Running job → Succeeded
  └── app/
      ├── app.py                         应用代码
      ├── frontend/                      前端页面
      ├── requirements.txt               运行依赖
      ├── requirements-dev.txt           测试依赖
      ├── .env.example                   配置示例
      ├── .gitignore                     忽略规则
      ├── .github/workflows/ci.yml       ← 隐藏目录，已保留（本机 self-hosted
  版本）
      ├── tests/test_chat_api.py         9 条测试
      └── scripts/smoke_test.py          冒烟检查

  刻意没有复制的东西，以及原因：

  ┌─────────────────────────┬───────────────────────────────────────────────┐
  │          内容           │              为什么留在实验仓库               │
  ├─────────────────────────┼───────────────────────────────────────────────┤
  │ .git/                   │ 复制进来会形成嵌套仓库，课程仓库无法正常记录  │
  │                         │ 里面的文件                                    │
  ├─────────────────────────┼───────────────────────────────────────────────┤
  │ .venv/                  │ 几百个文件，且依赖清单已说明该装什么          │
  ├─────────────────────────┼───────────────────────────────────────────────┤
  │ .env                    │ 含真实 Key，绝不能进任何仓库                  │
  ├─────────────────────────┼───────────────────────────────────────────────┤
  │ __pycache__/、.pytest_c │ 运行产物，无意义且体积大                      │
  │ ache/                   │                                               │
  ├─────────────────────────┼───────────────────────────────────────────────┤
  │ .git 历史与 Actions     │ 实验仓库仍然保存着完整的运行历史              │
  │ 运行记录                │                                               │
  └─────────────────────────┴───────────────────────────────────────────────┘

  为什么材料要分成两份

  这是本次实验一直在维护的区分：

  - 实验仓库（isse-lab5-chat-ci）保存过程：每一次推送、每一次成败、每一次修复。
    助教如果要复核"失败是不是真的、修复是不是真的"，看那里的历史；
  - 课程个人目录保存最终结果：一份能直接阅读的应用副本 + 四项截图 +
    真实对话轨迹。助教不需要翻你的 Actions 就能判断作业完成情况。

  .github/workflows/ci.yml 我保留在 app/ 里了——它是隐藏目录，用普通方式复制容易
  被漏掉，但它正是这次实验的核心产物，必须能看到。

  关于对话轨迹

  AGENT_TRACE.md 要记录的是这次实验真实发生的过程：你对覆盖率报告的分析、对失败
  原因的解释、我们关于 mock 和 runner 工作区的讨论——这些都只在对话里。

  这一步必须由你完成，我不能代替。原因很直接：这份轨迹的证明力来自"它是一次真实
  交互的记录"。如果用总结或重写的内容冒充，它就失去了作为过程证据的意义，反而变
  成一份普通的实验报告。

  ---

  你现在要做的事

  1. 导出对话到 AGENT_TRACE.md

  在 lab5/2500016663-Bekzat-Baybet/ 下新建 AGENT_TRACE.md，把本次对话导出为
  Markdown 粘贴进去。做法取决于你使用的客户端：

  - 如果有「复制为 Markdown」之类的导出功能，直接复制整段对话；
  - 如果支持生成分享链接，也可以把可访问的链接写进 AGENT_TRACE.md 代替粘贴全文；
  - 多个会话按时间顺序依次保留。

  2. 提交前自检

  逐项确认：

  - [ ] AGENT_TRACE.md 里没有任何 API Key、.env 内容或 runner 注册 token；
  - [ ] screenshots/ 六张图都在，self-hosted-terminal.png 那张不含 --token；
  - [ ] app/ 里没有 .env、.venv、__pycache__；
  - [ ] 运行 runner 的终端已经按 Ctrl+C 停止（GitHub 上状态变成 Offline
    是正常的）；
  - [ ] app/.github/workflows/ci.yml 里的 runs-on 是
    self-hosted（本机版本才是最终版）。

  3. 提交并推送课程分支

  cd "C:\Users\Aa233\Desktop\课程\智能化软件系统与工程\Lab\isse-labs"
  git status
  git add lab5/2500016663-Bekzat-Baybet
  git commit -m "Lab5: 2500016663-Bekzat-Baybet GitHub Actions持续集成"
  git push -u origin lab5/2500016663-Bekzat-Baybet

  git status 提交前应该只显示 ?? lab5/2500016663-Bekzat-Baybet/
  一项，确认没有别的东西混进去。

  4. 发起 PR

  推送后 GitHub 通常会在仓库页面上方直接给出 Compare & pull request
  按钮。或者手动到：

  https://github.com/pku-software/isse-labs/compare/main...Bekzat070101:isse-lab
  s:lab5/2500016663-Bekzat-Baybet

  标题格式：

  [Lab5] 2500016663-Bekzat-Baybet GitHub Actions持续集成

  注意 base 是 pku-software/isse-labs 的 main，head 是你 Fork 的
  lab5/2500016663-Bekzat-Baybet 分支——跨仓库 PR 时这一项容易点错。

  ---

  验收要点自检

  按作业要求逐条对照：

  ┌───────────────────────────────────────────┬─────────────────────────────┐
  │                   要点                    │            状态             │
  ├───────────────────────────────────────────┼─────────────────────────────┤
  │ 使用自己的 Lab2 应用，完成 CRUD           │ ✅ 9 条测试，call_deepseek  │
  │ 测试和一类非法输入测试，模型调用用 mock   │ 被 monkeypatch 替换         │
  ├───────────────────────────────────────────┼─────────────────────────────┤
  │ 测试通过，后端行覆盖率至少 70%            │ ✅ 87.67%（73 语句 / 9      │
  │                                           │ 未覆盖）                    │
  ├───────────────────────────────────────────┼─────────────────────────────┤
  │ 对话中说明一次功能失败与修复，保留前后运  │ ✅ 失败                     │
  │ 行链接                                    │ runs/40189239157，修复后    │
  │                                           │ runs/40189748170            │
  ├───────────────────────────────────────────┼─────────────────────────────┤
  │                                           │ ✅ 云端                     │
  │ 冒烟骨架已适配，云端和本机均执行成功      │ runs/40195625462，本机      │
  │                                           │ runs/40196744350            │
  ├───────────────────────────────────────────┼─────────────────────────────┤
  │ 四项截图证据与应用代码齐全，真实对话轨迹  │ ⏳ 截图与应用已就位，轨迹待 │
  │ 已导出                                    │ 你导出                      │
  ├───────────────────────────────────────────┼─────────────────────────────┤
  │ 本机 runner 已停止，材料位于个人 Lab5     │ ⏳ 待你确认停止并推送       │
  │ 目录                                      │                             │
  └───────────────────────────────────────────┴─────────────────────────────┘

  ---

  需要你反馈的内容

  1. AGENT_TRACE.md 是否已导出并放好；
  2. 自检五项是否都通过；
  3. 课程分支是否推送成功、PR 是否创建（把 PR 链接发我）；
  4. 最后确认 runner 已停止。

  假如 git status 里出现了意料之外的文件，或者 PR
  页面显示的改动列表不对，把内容发我，我们再看。

> agent_trace我没看到欸，是因为这是ClaudeCode吗，我是不是要自己粘贴聊天记录

  Thought for 22s, listed 1 directory (ctrl+o to expand)

● 这是 Claude Code，不是 Codex——两者的导出方式不一样，所以你在界面上找不到 Codex
  那个"复制为 Markdown"。先确认一下你这边可用的导出途径：

● Bash(cd "c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Lab" && timeout 45
      claude --help 2>&1 | head -50)
  ⎿  (No output)

  Thought for 5s (ctrl+o to expand)

● Bash(cd "c:/Users/Aa233/Desktop/课程/智能化软件系统与工程/Lab" && timeout 45
      claude --help 2>&1 | grep -iE "export|resume|continue|markdown" ; echo
      "--- 检查本会话记录文件 ---"; ls -la "…)
  ⎿  (No output)

  Thought for 8s (ctrl+o to expand)

● claude-code-guide(Verify Claude Code export options)
  ⎿  Backgrounded agent (↓ to manage · ctrl+o to expand)

● Bash(F="C:/Users/Aa233/.claude/projects/c--Users-Aa233-Desktop---------------L
      ab/0c9152e8-80de-4f28-a6d0-5073f099f270.jsonl"
      echo "=== 总行数 ===" && wc -l "$F"…)
  ⎿  (No output)

  Thought for 5s (ctrl+o to expand)

● Bash(F="C:/Users/Aa233/.claude/projects/c--Users-Aa233-Desktop---------------L
      ab/0c9152e8-80de-4f28-a6d0-5073f099f270.jsonl"
      python -c "…)
  ⎿  (No output)

  Thought for 12s (ctrl+o to expand)

● 是的，这是 Claude Code，不是 Codex——Codex 那个"复制为
  Markdown"在这里不存在，所以你在界面上找不到它。但轨迹确实不能由我代写：它的价
  值就在于"这是一次真实交互的记录"，我如果用自己的话总结一遍，它就变成一份普通实
  验报告了。所以这一步得用工具导出，不能靠复述。

  好消息是不需要手动一点点粘贴。有两条路：

  路线一：/export 斜杠命令

  在对话框里直接输入：

  /export

  这是 Claude Code 自带的会话导出命令。我已经让一个专门查 Claude Code
  功能的助手去核实它在你这个版本（2.1.310，VS Code
  扩展）里的确切行为——导出到文件还是复制到剪贴板、文件落在哪个路径、是否包含工具
  调用记录。等它回话我再给你确定的操作方式，免得让你去试一个不确定的命令。

  路线二：从原始会话记录转换（保底方案）

  Claude Code 会把每一轮对话原样写进本地记录文件。你这次会话的记录在：

  C:\Users\Aa233\.claude\projects\c--Users-Aa233-Desktop---------------Lab\0c915
  2e8-80de-4f28-a6d0-5073f099f270.jsonl

  （5 MB，524 条记录，其中你的消息 90 条、我的回复 174
  条，还有工具调用和附件索引。）

  这是未经加工的原始轨迹——里面的内容就是这次实验实际发生的事。如果 /export
  不方便，我可以写个脚本把它按时间顺序转成可读的 Markdown，忠实地输出你我说过的
  每一句，不加概括、不删改。我已经确认过它的记录结构，转换是可行的。

  这条路线和"我重写一份总结"有本质区别：转换只是换了个格式，内容是原始的；总结则
  是重新创作。

  ---

  两条路线的共同注意事项

  导出后务必自己通读一遍，确认不含以下内容再提交：

  - 任何 API Key（本次对话里没有出现过真实 Key，但也检查一下）；
  - runner 注册 token ——
    它只出现在你那张被拦下的终端截图里，文字记录里应该没有，但值得一眼扫过；
  - 你机器上的其他私人信息。

  另外提醒一句：轨迹要按时间顺序保留完整会话。如果你后面又开了新会话继续做
  Lab5（比如换了工作目录），多个会话按顺序依次保留在同一个 AGENT_TRACE.md 里。

  ---

  请先等一下我核实 /export 的结果。如果你现在就想动手，也可以先试着在输入框敲
  /export 看看有没有反应——有的话把它产生的内容贴到
  lab5/2500016663-Bekzat-Baybet/AGENT_TRACE.md 里就行。