# 开始 Lab5 实验

> 开始lab5

<details><summary>4 previous messages</summary>

> Lab5 的目标是把你已有的聊天应用接入自动化测试和 CI，依次完成云端运行、故意失败与修复、冒烟检查和本机 runner，最后整理提交材料。
>
> 课程仓库用于保存个人实验材料并提交课程 PR；独立实验仓库用于开发应用、提交代码和运行 GitHub Actions。我负责解释、编写测试与配置、协助排错；你亲自运行命令、提交推送、观察日志，并操作 GitHub 和 runner。我先完整阅读 README，确认准备阶段的要求，再带你准备课程分支与个人目录。
>
> <details><summary>Explored a file, ran a command</summary>
>
> <details><summary>Explored a file</summary>
>
> - Read `./README.md`
>
> </details>
>
> - Ran `pwd && git rev-parse --show-toplevel && git branch --show-current && git remote -v && git status --short`
>
> </details>
>
> 已完整读完 README。当前课程仓库是 `/home/jxq/playground/isse-labs`，位于 `main` 分支，远端是你的 Fork `Ciang-ks/isse-labs`，工作区干净。准备阶段先同步主分支，再创建 `lab5/<学号>-<姓名>` 分支和同名目录；我会打开内置终端，命令由你执行。
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

Lab5 会延续你的 Lab2 聊天应用：先编写自动测试，再让 GitHub Actions 在推送代码后自动检查；随后故意改坏一处功能，观察测试失败并修复，再加入冒烟检查，最后在自己的电脑上运行 runner。

持续集成（CI）把重复检查写成自动流程，让修改接口、数据结构或功能后能及时发现问题。

这次使用两个仓库：

- **课程仓库**：`/home/jxq/playground/isse-labs`，用于最终保存应用副本、截图和真实对话轨迹，并提交课程 PR。
- **独立实验仓库**：接下来新建，放入 Lab2 应用，用于开发和运行 Actions，原 Lab2 作业保留。

我负责讲解、编写当前阶段的代码和配置、协助排错；你负责运行命令、提交推送、观察日志，以及操作 GitHub 和本机 runner。

当前课程仓库在 `main` 分支，远端是 `Ciang-ks/isse-labs`，工作区干净。现在先准备实验位置。

1. 在 GitHub 打开你的课程 Fork，使用 **Sync fork → Update branch** 同步课程主分支。
2. 我已请求打开内置终端；若未显示，使用本机终端。将下面的 `你的学号-你的姓名` 替换成实际信息后执行：

   ```bash
   cd /home/jxq/playground/isse-labs
   git pull --ff-only origin main
   git switch -c lab5/你的学号-你的姓名
   mkdir -p lab5/你的学号-你的姓名
   git branch --show-current
   ```

   最后应显示 `lab5/学号-姓名`。空目录暂时不会出现在 Git 的待提交列表，这是正常现象。

3. 在 GitHub 新建个人实验仓库，例如 `isse-lab5-chat-ci`，默认分支使用 `main`。可以勾选初始化 README，再克隆到课程仓库之外：

   ```bash
   cd /home/jxq/playground
   git clone git@github.com:Ciang-ks/isse-lab5-chat-ci.git
   ```

完成后，请反馈：**学号与姓名、上述命令结果、实验仓库地址和本地绝对路径，以及原 Lab2 应用路径**。下一步我们根据你的实际应用确认需要复制的文件。

> 2400017727 蒋徐祺, 其余你使用我内置的 gh, 和git进行操作

<details><summary>6 previous messages</summary>

> 好的，后续准备仓库、运行命令和提交推送，我会按你的授权使用内置 `gh` 和 `git` 完成；每个教学阶段仍会停下来，让你结合真实结果解释观察到的现象。
>
> 当前先准备 `lab5/2400017727-蒋徐祺` 分支和个人目录。课程 Fork 保存最终交作业的材料，独立实验仓库保存应用开发与 Actions 运行历史。我会先核对仓库指引、远端和 GitHub 登录状态，再同步课程主分支并创建实验位置。
>
> <details><summary>Explored 3 files, a list, ran 5 commands</summary>
>
> - Ran `pwd && git status --short && git branch --show-current && git remote -v && gh auth status`
>
> - Ran `rg --files -g AGENTS.md -g README.md -g app.py -g requirements.txt -g '!node_modules' /home/jxq/playground/isse-labs /home/jxq/playground 2>/dev/null`
>
> <details><summary>Explored 3 files, a list</summary>
>
> - Read `~/playground/isse-labs/AGENTS.md`
> - Listed files in `蒋徐祺-2400017727`
> - Read `~/playground/isse-labs/lab2/蒋徐祺-2400017727/app.py`
> - Read `~/playground/isse-labs/lab2/蒋徐祺-2400017727/requirements.txt`
>
> </details>
>
> - Ran `gh repo view Ciang-ks/isse-labs --json nameWithOwner,defaultBranchRef,parent && gh api repos/Ciang-ks/isse-lab5-chat-ci --jq '{full_name, default_branch, private}'`
>
> - Ran `gh repo sync Ciang-ks/isse-labs --source pku-software/isse-labs --branch main`
>
> - Ran `git pull --ff-only origin main && git switch -c 'lab5/2400017727-蒋徐祺'`
>
> </details>
>
> 课程主分支已同步，并已切换到 `lab5/2400017727-蒋徐祺`。也找到了你的原应用：`/home/jxq/playground/isse-labs/lab2/蒋徐祺-2400017727`。
>
> 导入时会带上后端 `app.py`、`frontend/`、依赖清单和配置示例。应用通过 `ask_deepseek()` 调用模型，聊天记录保存在内存列表 `messages` 中，重启后清空。代码与本机环境分开保存：仓库记录依赖和配置示例，每台机器根据清单安装环境；`.gitignore` 排除凭据、虚拟环境和缓存。
>
> 我会创建独立的私有仓库 `Ciang-ks/isse-lab5-chat-ci`，复制这些文件并安装依赖，再完成初始提交和推送。后续测试会模拟模型回复，无需真实 Key。
>
> <details><summary>Ran 5 commands</summary>
>
> - Ran `mkdir -p '2400017727-蒋徐祺/screenshots' && cat '/home/jxq/playground/isse-labs/lab2/蒋徐祺-2400017727/.gitignore' && cat '/home/jxq/playground/isse-labs/lab2/蒋徐祺-2400017727/README.md'`
> - Ran `gh repo create Ciang-ks/isse-lab5-chat-ci --private --description 'Lab5: Flask chat application tests and GitHub Actions CI' --add-readme`
> - Ran `gh repo clone Ciang-ks/isse-lab5-chat-ci /home/jxq/playground/isse-lab5-chat-ci && git -C /home/jxq/playground/isse-lab5-chat-ci branch --show-current && git -C /home/jxq/playground/isse-lab5-chat-ci remote -v`
> - Ran `python3 - <<'PY'
> from pathlib import Path
> import shutil
> src = Path('/home/jxq/playground/isse-labs/lab2/蒋徐祺-2400017727')
> dst = Path('/home/jxq/playground/isse-lab5-chat-ci')
> for name in ['app.py', 'requirements.txt', 'README.md']:
>     shutil.copy2(src / name, dst / name)
> shutil.copytree(src / 'frontend', dst / 'frontend')
> (dst / '.env.example').write_text('DEEPSEEK_API_KEY=replace-with-your-api-key\n', encoding='utf-8')
> (dst / '.gitignore').write_text('.env\n.venv/\nvenv/\n__pycache__/\n*.py[cod]\n.pytest_cache/\n.coverage\n.coverage.*\nhtmlcov/\n', encoding='utf-8')
> print('Copied app.py, frontend/, requirements.txt, README.md; prepared .env.example and .gitignore')
> PY
> python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt`
> - Ran `command -v uv; command -v virtualenv; python3 --version; git -C /home/jxq/playground/isse-lab5-chat-ci status --short`
>
> </details>
>
> 应用文件已导入，原 Lab2 保持不变。创建虚拟环境时发现系统 Python 缺少 `ensurepip`，因此 `python3 -m venv` 未成功；本机已有 `uv`，我会用它准备 `.venv` 并安装同一份依赖。
>
> 初始版本只包含应用、依赖、配置示例和忽略规则。完成推送后先停在准备阶段，下一阶段再编写 CRUD 与非法输入测试。
>
> <details><summary>Ran 4 commands</summary>
>
> - Ran `uv venv --clear .venv && uv pip install --python .venv/bin/python -r requirements.txt && .venv/bin/python -c 'import sys; from importlib.metadata import version; print(sys.version); print({name: version(name) for name in ("Flask", "python-dotenv", "requests")})' && git add app.py frontend requirements.txt README.md .env.example .gitignore && git diff --cached --stat && git commit -m 'Import Lab2 chat application for Lab5' && git push origin main`
> - Ran `/home/jxq/.local/bin/uv venv --clear .venv && /home/jxq/.local/bin/uv pip install --python .venv/bin/python -r requirements.txt && .venv/bin/python -c 'import sys; from importlib.metadata import version; print(sys.version); print({name: version(name) for name in ("Flask", "python-dotenv", "requests")})' && git add app.py frontend requirements.txt README.md .env.example .gitignore && git diff --cached --stat && git commit -m 'Import Lab2 chat application for Lab5' && git push origin main`
> - Ran `git branch --show-current && git status --short && git remote -v && test -d '2400017727-蒋徐祺/screenshots' && git diff --exit-code -- 'lab2/蒋徐祺-2400017727'`
> - Ran `git -C /home/jxq/playground/isse-lab5-chat-ci status --short && git -C /home/jxq/playground/isse-lab5-chat-ci log -1 --format='%h %s' && gh repo view Ciang-ks/isse-lab5-chat-ci --json url,isPrivate,defaultBranchRef`
>
> </details>
</details>

准备阶段已完成，已按你的授权使用 `gh` 和 `git` 操作。

| 用途 | 本地路径 | 分支 |
|---|---|---|
| 课程提交 | `/home/jxq/playground/isse-labs` | `lab5/2400017727-蒋徐祺` |
| 独立实验 | `/home/jxq/playground/isse-lab5-chat-ci` | `main` |

课程主分支已同步，个人目录已创建。独立的[实验仓库](https://github.com/Ciang-ks/isse-lab5-chat-ci)已创建为私有仓库，初始应用已推送，提交为 `b53acba`，工作区干净。

CI 会把原来靠网页点击或手动请求完成的检查写成自动流程，让代码修改后及时得到反馈。课程仓库保存最终作业材料，实验仓库保存应用开发和 Actions 运行历史。

这次导入沿用你的 Lab2 应用：入口是 `app.py`，前端位于 `frontend/`，`ask_deepseek()` 负责模型调用，聊天记录存在内存列表 `messages` 中，重启后清空。已复制代码、README 和依赖清单，准备 `.env.example` 与 `.gitignore`；原 Lab2 未修改。

代码与运行环境分别管理：仓库保存依赖清单和配置示例，虚拟环境按清单安装，并通过忽略规则排除凭据和缓存。本机系统 Python 缺少 `ensurepip`，已改用现有 `uv` 创建 `.venv`，实际使用 Python **3.13.11**，三项运行依赖均安装成功。`commit` 记录本地版本，`push` 将版本上传 GitHub，因此现在仓库页面已能看到应用代码。

本步无需再运行命令。请打开实验仓库确认文件，然后用自己的话回答：**为什么要把 `requirements.txt` 提交到仓库，而把 `.venv/` 留在本地？** 下一步我们编写聊天记录 CRUD 和非法输入测试。

> .venv 不是指示性文件且不好维护且与机器相关, 留在本地, requirements.txt 是环境的说明, 需要提交

<details><summary>3 previous messages</summary>

> 你的理解正确。`.venv` 包含已安装的包、解释器路径和与操作系统相关的文件，不适合跨机器直接复用；`requirements.txt` 记录依赖，让本地、云端和 runner 都能重新安装环境。目前清单没有锁定版本，因此不同时间安装可能得到不同版本。
>
> 接下来进入自动测试阶段：用 Flask `test_client()` 在进程内发送请求，无需启动服务；用 mock 将模型调用替换为固定回复，避免依赖真实 Key、网络和模型回复；用 fixture 在每个测试前准备独立数据。我们会检查一条记录的创建、查询、修改、删除，以及空消息被拒绝且没有新增记录。
>
> 结合你的应用，测试会访问 `/api/messages`，修改使用 `PATCH /api/messages/<id>`，删除使用 `DELETE`；模拟位置是 `app.ask_deepseek`，隔离对象是内存列表 `app.messages`。例如删除后再次查询，应得到空列表。我先核对实验仓库状态和目录指引，再添加测试。
>
> <details><summary>Ran 4 commands</summary>
>
> - Ran `cat /home/jxq/playground/isse-lab5-chat-ci/app.py && cat /home/jxq/playground/isse-lab5-chat-ci/requirements.txt && test ! -f /home/jxq/playground/AGENTS.md`
>
> - Ran `git branch --show-current && git remote -v && git status --short && rg --files --hidden -g AGENTS.md -g '!\.git' -g '!\.venv' && true`
>
> - Ran `python3 - <<'PY'
> from pathlib import Path
> root = Path('/home/jxq/playground/isse-lab5-chat-ci')
> (root / 'tests').mkdir(exist_ok=True)
> (root / 'requirements-dev.txt').write_text('pytest\npytest-cov\n', encoding='utf-8')
> (root / 'tests/conftest.py').write_text('''from unittest.mock import Mock, patch
>
> import pytest
>
> # 导入应用时不加载本机 .env；测试不需要真实配置。
> with patch("dotenv.load_dotenv", return_value=False):
>     import app as chat_app
>
>
> @pytest.fixture()
> def client_and_model(monkeypatch):
>     # 每个测试获得新的列表，避免测试之间共享聊天记录。
>     monkeypatch.setattr(chat_app, "messages", [])
>     monkeypatch.setitem(chat_app.app.config, "TESTING", True)
>     model = Mock(return_value="这是固定的测试回复")
>     monkeypatch.setattr(chat_app, "ask_deepseek", model)
>     with chat_app.app.test_client() as client:
>         yield client, model
> ''', encoding='utf-8')
> (root / 'tests/test_chat_api.py').write_text('''def test_message_crud(client_and_model):
>     client, model = client_and_model
>     assert client.get("/api/messages").get_json() == []
>
>     # 创建：检查状态码、实际内容以及模型收到的输入。
>     response = client.post("/api/messages", json={"message": "你好"})
>     assert response.status_code == 201
>     record = response.get_json()
>     message_id = record["id"]
>     assert isinstance(message_id, int)
>     assert record == {
>         "id": message_id,
>         "message": "你好",
>         "reply": "这是固定的测试回复",
>     }
>     model.assert_called_once_with("你好")
>
>     # 查询：响应中确实存在刚创建的记录。
>     response = client.get("/api/messages")
>     assert response.status_code == 200
>     assert response.get_json() == [record]
>
>     # 修改：再次查询，确认修改已保存；当前接口只修改用户消息。
>     response = client.patch(
>         f"/api/messages/{message_id}", json={"message": "修改后的消息"}
>     )
>     assert response.status_code == 200
>     updated = {**record, "message": "修改后的消息"}
>     assert response.get_json() == updated
>     assert client.get("/api/messages").get_json() == [updated]
>
>     # 删除：返回成功之后，记录也应当真正消失。
>     response = client.delete(f"/api/messages/{message_id}")
>     assert response.status_code == 200
>     assert response.get_json() == updated
>     assert client.get("/api/messages").get_json() == []
>     model.assert_called_once_with("你好")
>
>
> def test_empty_message_is_rejected(client_and_model):
>     client, model = client_and_model
>     response = client.post("/api/messages", json={"message": "   "})
>
>     assert response.status_code == 400
>     assert "非空字符串" in response.get_json()["error"]
>     assert client.get("/api/messages").get_json() == []
>     model.assert_not_called()
> ''', encoding='utf-8')
> print('Added requirements-dev.txt and two isolated API tests; application code unchanged.')
> PY
> /home/jxq/.local/bin/uv pip install --python .venv/bin/python -r requirements.txt -r requirements-dev.txt && .venv/bin/python -m pytest -q`
>
> - Ran `git diff --stat && git status --short`
>
> Tool call
>
> Tool: open_in_codex
> Status: completed
>
> </details>
>
> 两个重点测试已写好，应用代码无需修改。CRUD 测试从创建响应中取得 ID，并在修改、删除后重新查询，核对实际数据；空消息测试检查 `400`、错误提示、记录仍为空，以及模型没有被调用。
>
> 测试依赖正在下载。导入应用时也已屏蔽 `.env` 加载，因此这组测试不会读取本机的真实配置。
</details>

你的理解正确：`.venv` 包含与机器和路径相关的安装结果，留在本地；`requirements.txt` 描述依赖，应提交以便其他环境重新安装。

两个重点测试已完成，实际运行结果为：

```text
2 passed in 0.03s
```

自动测试把手动请求和判断写成可重复执行的程序，`assert` 表示必须满足的预期。Flask `test_client()` 在测试进程内处理请求，因此无需先启动监听端口的服务。

本次添加了：

- [test_chat_api.py](~/playground/isse-lab5-chat-ci/tests/test_chat_api.py)：创建记录并查询核对，修改后再次查询，删除后确认记录消失；另外检查空消息返回 `400` 和错误提示，且没有新增记录。
- [conftest.py](~/playground/isse-lab5-chat-ci/tests/conftest.py)：fixture 为每个测试准备独立的内存列表和客户端；mock 将 `ask_deepseek()` 替换为固定回复，避免网络、费用和回复变化影响结果。导入应用时也屏蔽了 `.env` 加载。
- [requirements-dev.txt](~/playground/isse-lab5-chat-ci/requirements-dev.txt)：添加 `pytest` 和 `pytest-cov`。

例如删除后的断言：

```python
assert client.get("/api/messages").get_json() == []
```

它检查记录确实消失。应用代码未修改，目前尚未测量覆盖率。

命令已由我代运行：

```bash
.venv/bin/python -m pytest -q
```

请结合测试解释：**如果删除接口返回 `200`，但实际上没有删除记录，为什么这组测试仍会失败？**

> 200仅仅代表“服务器成功接收并处理了该请求”，**并不意味业务逻辑一定正确执行**
> 当触发assert时，该测试用例会被标记为失败

<details><summary>4 previous messages</summary>

> 对，判断关键在于响应之后的数据是否符合约定。更准确地说，`200` 是接口声明请求成功的 HTTP 状态；即使返回了它，删除后的列表仍可能包含记录。这里是断言条件不成立时，pytest 才会把测试标记为失败，正常成立的 `assert` 不会导致失败。
>
> 下一步查看覆盖率：它统计测试执行过的后端可执行语句比例，帮助定位尚未经过的代码；功能是否正确仍由断言判断。报告中 `Cover` 是覆盖比例，`Missing` 是未执行的行号。我们会用 `--cov=app` 统计你的整个后端，显示未覆盖行，并用 `--cov-fail-under=70` 设置门槛；即使两条测试都通过，覆盖率不足也会使命令失败。我先运行一次，再根据真实报告补充必要测试。
>
> <details><summary>Ran a command</summary>
>
> - Ran `git branch --show-current && git remote -v && git status --short && .venv/bin/python -m pytest -q --cov=app --cov-report=term-missing --cov-fail-under=70`
>
> </details>
>
> 第一次结果是：两条测试通过，但后端覆盖率只有 **65.93%**，因此命令以失败状态结束。报告统计了 `app.py` 的 91 条可执行语句，其中 31 条未执行。
>
> 未覆盖的主要部分是模型请求函数 `ask_deepseek()`：前面用 mock 替换了整个函数，所以 CRUD 测试没有执行函数内部的请求和解析代码。我会补一条小测试，让该函数实际运行，但将 `requests.post` 替换为固定 JSON 响应，同时设置测试占位 Key。这样可以检查请求参数和回复解析，仍然不访问真实模型；覆盖率统计范围保持为整个 `app.py`。
>
> <details><summary>Ran a command</summary>
>
> - Ran `python3 - <<'PY'
> from pathlib import Path
> path = Path('/home/jxq/playground/isse-lab5-chat-ci/tests/test_model_client.py')
> path.write_text('''from unittest.mock import Mock
>
> import app as chat_app
>
>
> def test_model_request_and_reply(monkeypatch):
>     # 只使用占位 Key，并在 HTTP 边界模拟固定模型响应。
>     monkeypatch.setenv("DEEPSEEK_API_KEY", "lab5-test-placeholder")
>     response = Mock(status_code=200)
>     response.json.return_value = {
>         "choices": [{"message": {"content": "这是固定的模型回复"}}]
>     }
>     post = Mock(return_value=response)
>     monkeypatch.setattr(chat_app.requests, "post", post)
>
>     assert chat_app.ask_deepseek("你好") == "这是固定的模型回复"
>     post.assert_called_once_with(
>         chat_app.DEEPSEEK_API_URL,
>         headers={
>             "Authorization": "Bearer [REDACTED_SECRET]",
>             "Content-Type": "application/json",
>         },
>         json={
>             "model": chat_app.DEEPSEEK_MODEL,
>             "messages": [{"role": "user", "content": "你好"}],
>             "stream": False,
>         },
>         timeout=chat_app.DEEPSEEK_TIMEOUT,
>     )
> ''', encoding='utf-8')
> print('Added one model-client success test with mocked HTTP.')
> PY
> .venv/bin/python -m pytest -q --cov=app --cov-report=term-missing --cov-fail-under=70`
>
> </details>
</details>

对。补充一点：只有 `assert` 的条件不成立时，测试才会失败；执行到断言本身是正常过程。

覆盖率检查现已通过：

```text
app.py：91 条可执行语句，22 条未覆盖
Total coverage: 75.82%
3 passed in 0.05s
```

行覆盖率表示测试执行过的可执行语句比例。报告中 `Cover` 是覆盖比例，`Missing` 列出未执行的行号；它帮助发现遗漏路径，业务结果是否正确仍要靠断言。

最初两条测试全部通过，但覆盖率只有 **65.93%**，低于门槛，因此命令返回失败。主要原因是 CRUD 测试替换了整个 `ask_deepseek()`，没有执行函数内部代码。

根据报告，我补充了[模型客户端测试](~/playground/isse-lab5-chat-ci/tests/test_model_client.py)：实际运行 `ask_deepseek()`，在 HTTP 请求处模拟固定响应，检查请求参数和回复解析，使用占位 Key，不访问真实模型。应用代码和统计范围均未改变。

本次执行命令：

```bash
.venv/bin/python -m pytest -q \
  --cov=app \
  --cov-report=term-missing \
  --cov-fail-under=70
```

三个参数分别指定被测后端模块、显示未覆盖行、设置 70% 门槛。现在已达标，无需继续扩展测试。

请结合这次结果解释：**为什么最初显示 `2 passed`，整个命令仍然失败？75.82% 是否代表业务结果有 75.82% 的概率正确？** 随后进入云端 CI 配置。

> 最初命令失败是因为强制要求覆盖率达标。75.82% 仅代表代码行被执行的比例，不代表业务正确概率，业务结果是否正确完全取决于断言。

<details><summary>4 previous messages</summary>

> 你对覆盖率的解释准确。关于正确性再补一句：断言检查预期结果，但也可能遗漏需求或写错，所以测试通过仍不能证明所有业务行为都正确。
>
> 现在进入云端 CI：GitHub Actions 会在推送或 PR 时自动运行检查。工作流保存在 `.github/workflows/ci.yml`；事件决定何时触发，job 交给 runner 执行，step 按顺序检出代码、准备 Python、安装依赖、运行测试。`on` 配置事件，`runs-on` 选择机器，`uses` 调用 Action，`run` 执行命令。
>
> 结合当前仓库，我会配置推送到 `main`、向 `main` 提 PR 时触发，使用 `ubuntu-latest` 和与本地一致的 Python 3.13，执行刚才通过的测试与 70% 覆盖率命令。云端不会带上本地 `.venv`，因此工作流会重新安装两份依赖清单。我先核对 Action 的官方版本，再编写、提交并推送，查看本次提交对应的运行日志。
>
> <details><summary>Ran 7 commands, searched the web</summary>
>
> Searched the web for `https://github.com/actions/checkout`
>
> - Ran `gh api repos/actions/checkout/releases/latest --jq .tag_name && gh api repos/actions/setup-python/releases/latest --jq .tag_name`
>
> - Ran `git branch --show-current && git remote -v && git status --short && cat requirements-dev.txt && cat tests/conftest.py && cat tests/test_model_client.py`
>
> - Ran `python3 - <<'PY'
> from pathlib import Path
> path = Path('.github/workflows/ci.yml')
> path.parent.mkdir(parents=True, exist_ok=True)
> path.write_text('''name: Chat CI
>
> on:
>   push:
>     branches: [main]
>   pull_request:
>     branches: [main]
>
> permissions:
>   contents: read
>
> jobs:
>   test:
>     name: Tests and coverage
>     runs-on: ubuntu-latest
>     timeout-minutes: 10
>     steps:
>       - name: Check out code
>         uses: actions/checkout@v7
>
>       - name: Set up Python
>         uses: actions/setup-python@v7
>         with:
>           python-version: '3.13'
>
>       - name: Install dependencies
>         run: python -m pip install -r requirements.txt -r requirements-dev.txt
>
>       - name: Run tests and coverage
>         run: python -m pytest -q --cov=app --cov-report=term-missing --cov-fail-under=70
> ''', encoding='utf-8')
> print(path.read_text())
> PY
>  git diff --check && git add .github/workflows/ci.yml requirements-dev.txt tests && git diff --cached --stat && git commit -m 'Add API tests and cloud CI with coverage threshold' && git push origin main`
>
> - Ran `gh run list --repo Ciang-ks/isse-lab5-chat-ci --commit 1885a6e --json databaseId,status,conclusion,url,headSha,workflowName --limit 3`
>
> Tool call
>
> Tool: open_in_codex
> Status: completed
>
> - Ran `gh run list --repo Ciang-ks/isse-lab5-chat-ci --json databaseId,status,conclusion,url,headSha,workflowName --limit 3`
>
> - Ran `gh run watch 40208865937 --repo Ciang-ks/isse-lab5-chat-ci --exit-status --interval 10`
>
> Tool call
>
> Tool: open_in_codex
> Status: completed
>
> - Ran `gh run view 40208865937 --repo Ciang-ks/isse-lab5-chat-ci --json headSha,conclusion,jobs,url && gh run view 40208865937 --repo Ciang-ks/isse-lab5-chat-ci --log | rg 'app.py|TOTAL|Total coverage|passed in|Python 3|Runner Image|Image:|Current runner version'`
>
> </details>
>
> 首次云端运行已成功，对应提交 `1885a6e`。检出代码、准备 Python、安装依赖和测试步骤全部通过。我正在核对日志中的测试数量和覆盖率，确认云端结果与本地一致。
>
> <details><summary>Ran a command</summary>
>
> - Ran `XDG_CACHE_HOME=/tmp/lab5-gh-cache gh run view 40208865937 --repo Ciang-ks/isse-lab5-chat-ci --log | rg 'app.py|TOTAL|Total coverage|passed in|Python 3|Runner Image|Image:|Current runner version'`
>
> </details>
</details>

云端 CI 已成功：[查看本次运行](https://github.com/Ciang-ks/isse-lab5-chat-ci/actions/runs/40208865937)，对应提交 **`1885a6e`**。

日志确认：

```text
3 passed in 0.05s
Total coverage: 75.82%
```

GitHub Actions 将本地检查变成推送后自动执行的流程。[ci.yml](~/playground/isse-lab5-chat-ci/.github/workflows/ci.yml) 定义了：

- `on`：推送到 `main` 或向 `main` 发 PR 时触发。
- `jobs`：组织任务，本次只有 `Tests and coverage`。
- `runs-on: ubuntu-latest`：选择 GitHub 提供的云端 runner，本次实际使用 Ubuntu 24.04。
- `steps`：依次检出当前提交、准备 Python 3.13、安装依赖、运行测试。
- `uses`：调用现有 Action，采用已核对的官方 [checkout](https://github.com/actions/checkout) 和 [setup-python](https://github.com/actions/setup-python)。
- `run`：执行安装命令，以及与本地相同的测试和 70% 覆盖率检查。

云端机器不会自动拥有你的本地 `.venv`，所以必须从两份依赖清单重新安装环境。检出步骤取得的是本次提交的代码，因此查看日志时也要核对提交号。

我已请求打开运行页面。请进入 **Tests and coverage → Run tests and coverage**，找到测试数量和覆盖率，并反馈：**这次任务运行在哪里？哪条配置决定它运行的位置？** 然后进入失败与修复实验。

> 这次任务运行在 GitHub 提供的云端 runner 上 决定运行位置的是c`i.yml` 中的 `runs-on: ubuntu-latest` 配置。

<details><summary>2 previous messages</summary>

> 对，`runs-on: ubuntu-latest` 选择了 GitHub 提供的云端 runner。
>
> 接下来做一次功能回归实验：修改一处已经被测试覆盖的应用行为，保持测试预期不变，观察 CI 能否发现问题。我们会让删除接口仍返回成功，但不再移除记录；删除后重新查询的断言应该发现记录仍在。
>
> 我先核对当前删除逻辑和对应断言，给出具体改动。按课程 README 这一阶段的要求，等你确认故障方案后再修改并推送。失败后先保留日志、截图和运行链接，再修复。
>
> <details><summary>Ran a command</summary>
>
> - Ran `git branch --show-current && git remote -v && git status --short && git log -1 --oneline && nl -ba app.py | sed -n '136,152p' && nl -ba tests/test_chat_api.py | sed -n '28,41p'`
>
> </details>
</details>

正确，运行位置由 `runs-on: ubuntu-latest` 决定。

接下来验证 CI 能否发现功能回归：改坏一处应用行为，保留原测试预期。具体方案是注释掉 [app.py 第 147 行](~/playground/isse-lab5-chat-ci/app.py:147)：

```python
# messages.remove(record)
return jsonify(record)
```

这样删除接口仍返回 `200` 和记录内容，但记录实际留在列表中。[CRUD 测试第 36 行](~/playground/isse-lab5-chat-ci/tests/test_chat_api.py:36)会再次查询：

```python
assert client.get("/api/messages").get_json() == []
```

预期为空列表，实际仍有记录，因此这条断言应失败。

推送后，我们会核对失败运行对应的提交、step、测试名，以及断言的预期和实际值。非零退出码表示检查失败，具体原因需要从前面的断言日志定位。保存失败截图和运行链接后再修复，保留两次独立运行。

**是否按上述方案注释这一行并提交推送？**

这里需要确认，是因为课程 [README 的失败实验步骤](./README.md)明确要求“学生确认后再修改”；常规命令和 Git 操作仍沿用你此前的授权。

> 确认

<details><summary>2 previous messages</summary>

> 收到。我会只注释删除接口中的 `messages.remove(record)`，保持测试不变，提交并推送，让 CI 检查这次功能回归。
>
> 预期删除请求仍返回 `200`，但随后查询还能看到记录，导致 `test_message_crud` 的空列表断言失败。运行结束后，我会核对提交号、失败步骤和断言日志，保留这次失败运行；等你解释观察结果并保存截图后，再修复。
>
> <details><summary>Ran 5 commands</summary>
>
> - Ran `git branch --show-current && git remote -v && git status --short && git log -2 --oneline && sed -n '140,149p' app.py`
>
> - Ran `python3 - <<'PY'
> from pathlib import Path
> path = Path('app.py')
> source = path.read_text(encoding='utf-8')
> old = '    messages.remove(record)\n'
> assert source.count(old) == 1
> path.write_text(source.replace(old, '    # messages.remove(record)  # Lab5: intentional deletion regression\n'), encoding='utf-8')
> PY
> git diff --check && git diff -- app.py && git add app.py && git commit -m 'Demonstrate CI failure when deletion retains the record' && git push origin main && git rev-parse HEAD`
>
> - Ran `gh run list --repo Ciang-ks/isse-lab5-chat-ci --commit 861b2376950735678f08ca3b6ba1e4009ff84ac1 --json databaseId,status,conclusion,url,headSha --limit 1`
>
> - Ran `gh run watch 40209192177 --repo Ciang-ks/isse-lab5-chat-ci --exit-status --interval 10`
>
> Tool call
>
> Tool: open_in_codex
> Status: completed
>
> - Ran `XDG_CACHE_HOME=/tmp/lab5-gh-cache gh run view 40209192177 --repo Ciang-ks/isse-lab5-chat-ci --log-failed`
>
> </details>
</details>

失败实验已完成，符合预期：[查看失败运行](https://github.com/Ciang-ks/isse-lab5-chat-ci/actions/runs/40209192177)，对应提交 **`861b237`**。

本次仅注释了删除记录的操作，测试保持不变。CI 检查到了这次功能回归：

- 失败步骤：`Run tests and coverage`
- 失败测试：`test_message_crud`
- 失败位置：`tests/test_chat_api.py:36`
- 预期：删除后查询得到 `[]`
- 实际：仍包含 `id=1` 的记录
- 结果：`1 failed, 2 passed`，退出码为 `1`

覆盖率仍有 **75.56%**，达到门槛；此次失败来自业务断言。这说明代码执行到了，并不代表执行结果正确。定位时，应将失败断言、实际数据与本次提交的改动对应起来，不能只看最后的退出码。

请打开运行中的 **Tests and coverage → Run tests and coverage**，截图保留失败测试名、断言及预期/实际差异，发到当前对话，我会整理到个人目录。

同时请用自己的话说明：**为什么返回 `200` 的检查通过了，而删除后的查询断言失败了？应该恢复哪一行代码？** 保存失败证据后再修复，保留前后两次独立运行。

> 测试在调用删除接口后，会再次查询数据库来确认记录是否真的消失。
> 应该恢复 messages.remove(record)
>
> User context
>
> Images:
> - `C:/Users/jjj/AppData/Local/Temp/codex-clipboard-9ac1a0e5-1151-40dc-b51f-b562fb6f9efc.png`
> - `C:/Users/jjj/AppData/Local/Temp/codex-clipboard-f0447911-02b3-48ff-ae15-e0419398eac3.png`

<details><summary>3 previous messages</summary>

> 你的定位正确，应该恢复 `messages.remove(record)`。这里再查询的是 `/api/messages` 接口，底层数据在内存列表中；当前应用没有使用数据库。
>
> 我先通过 Windows 路径对应的 `/mnt/c/...` 查看并保存两张截图，再恢复删除逻辑、提交推送。修复会让同一条断言重新通过；必须查看新提交触发的新运行，重跑旧记录仍会检查旧代码。之后我会核对测试结果和覆盖率，保留失败与修复两次运行链接。
>
> Viewed 2 images
>
> <details><summary>Ran 6 commands</summary>
>
> - Ran `git branch --show-current && git remote -v && git status --short && git log -1 --oneline && sed -n '141,149p' app.py`
>
> - Ran `python3 - <<'PY'
> from pathlib import Path
> import shutil
> out = Path('/home/jxq/playground/isse-labs/lab5/2400017727-蒋徐祺/screenshots')
> out.mkdir(parents=True, exist_ok=True)
> files = {
> 'failed.png': 'codex-clipboard-f0447911-02b3-48ff-ae15-e0419398eac3.png',
> 'failed-2.png': 'codex-clipboard-9ac1a0e5-1151-40dc-b51f-b562fb6f9efc.png',
> }
> for name, source in files.items():
>     dest = out / name
>     assert not dest.exists(), f'File already exists: {dest}'
>     shutil.copy2(Path('/mnt/c/Users/jjj/AppData/Local/Temp') / source, dest)
>     print(dest)
> PY`
>
> - Ran `python3 - <<'PY'
> from pathlib import Path
> path = Path('app.py')
> source = path.read_text(encoding='utf-8')
> old = '    # messages.remove(record)  # Lab5: intentional deletion regression\n'
> assert source.count(old) == 1
> path.write_text(source.replace(old, '    messages.remove(record)\n'), encoding='utf-8')
> PY
> .venv/bin/python -m pytest -q --cov=app --cov-report=term-missing --cov-fail-under=70 && git diff --check && git diff -- app.py && git add app.py && git commit -m 'Restore actual removal of deleted chat records' && git push origin main && git rev-parse HEAD`
>
> - Ran `gh run list --repo Ciang-ks/isse-lab5-chat-ci --commit d335a22c9c64f917829529813f8b32032845cce0 --json databaseId,status,conclusion,url,headSha --limit 1`
>
> - Ran `gh run watch 40209442602 --repo Ciang-ks/isse-lab5-chat-ci --exit-status --interval 10`
>
> Tool call
>
> Tool: open_in_codex
> Status: completed
>
> - Ran `XDG_CACHE_HOME=/tmp/lab5-gh-cache gh run view 40209442602 --repo Ciang-ks/isse-lab5-chat-ci --log | rg 'Total coverage|passed in|app.py +[0-9]|TOTAL +[0-9]'`
>
> </details>
</details>

定位正确。这里再次查询的是 API，底层数据保存在内存列表中，当前应用没有数据库。

两张原图已读取并保存：

- [failed.png](./2400017727-蒋徐祺/screenshots/failed.png)：失败断言及实际残留记录。
- [failed-2.png](./2400017727-蒋徐祺/screenshots/failed-2.png)：失败运行概览。

已恢复 `messages.remove(record)`，测试保持不变。修复恢复了实际删除行为，因此删除后查询得到空列表，同一条断言重新通过。

| 运行 | 提交 | 实际结果 |
|---|---|---|
| [故障版本](https://github.com/Ciang-ks/isse-lab5-chat-ci/actions/runs/40209192177) | `861b237` | 1 failed，2 passed |
| [修复版本](https://github.com/Ciang-ks/isse-lab5-chat-ci/actions/runs/40209442602) | `d335a22` | 3 passed，覆盖率 75.82% |

修复已提交推送，云端成功。此次查看的是新提交触发的新运行；重新运行旧记录仍会检查旧提交，无法验证新修复。前后两次独立运行均已保留。

请打开修复运行，确认原先失败的测试恢复通过，并反馈观察结果。随后进入冒烟检查，验证应用能否真正启动并提供 HTTP 响应。

> 确认恢复通过

<details><summary>2 previous messages</summary>

> 修复运行已确认通过。接下来做冒烟检查：前面的 Flask `test_client()` 测试检查请求处理逻辑；这一步会真正启动临时 Flask 进程，再通过 HTTP 访问首页和连通性接口，以发现启动入口、依赖或路径问题。它只检查基本服务能力，不验证浏览器里的所有交互。
>
> 课程骨架已负责启动、等待就绪、HTTP 请求和退出清理，我们只适配配置区。你的应用入口是 `app:app`，首页为 `/`，连通性接口是 `/api/hello`，预期 JSON 为 `{"message": "你好"}`。聊天记录只存在内存中，无需接入持久化目录。我先阅读骨架并核对这些配置，再复制到实验仓库运行。
>
> <details><summary>Explored a file, ran 2 commands</summary>
>
> <details><summary>Explored a file</summary>
>
> - Read `./templates/smoke_test.py`
>
> </details>
>
> - Ran `git branch --show-current && git remote -v && git status --short && cat .github/workflows/ci.yml && sed -n '89,105p' app.py`
>
> - Ran `python3 - <<'PY'
> from pathlib import Path
> source = Path('/home/jxq/playground/isse-labs/lab5/templates/smoke_test.py')
> target = Path('scripts/smoke_test.py')
> assert not target.exists(), 'Smoke script already exists; inspect before replacing'
> target.parent.mkdir(parents=True, exist_ok=True)
> text = source.read_text(encoding='utf-8')
> text = text.replace('# TODO：根据自己的应用确认这四项配置。', '# 已核对 Lab2 应用：入口 app:app，首页 /，连通性接口 /api/hello。')
> target.write_text(text, encoding='utf-8')
> print('Copied course skeleton; confirmed all four configuration values.')
> PY
> .venv/bin/python scripts/smoke_test.py`
>
> </details>
</details>

本地冒烟检查已通过，临时服务已停止：

```text
服务已就绪
PASS /
PASS /api/hello
服务已停止
冒烟检查通过
```

前面的 `test_client()` 在进程内检查 Flask 的请求处理逻辑；冒烟检查真正启动临时 Flask 进程，再通过 HTTP 请求验证服务，能发现入口、启动依赖和路径方面的问题。首页与接口通过，并不代表浏览器里的所有交互都已验证。

已复用课程骨架生成 [scripts/smoke_test.py](~/playground/isse-lab5-chat-ci/scripts/smoke_test.py)，配置为：

| 配置 | 值 |
|---|---|
| Flask 入口 | `app:app` |
| 首页 | `/`，检查 HTML 响应 |
| 连通性接口 | `/api/hello` |
| 预期 JSON | `{"message": "你好"}` |

骨架负责选择临时端口、启动服务、等待就绪、发送请求和退出清理；失败时会输出启动日志并以非零状态结束。你的应用使用内存存储，无需适配持久化目录。

本次实际执行：

```bash
.venv/bin/python scripts/smoke_test.py
```

请结合输出说明：**冒烟检查比 `test_client()` 多验证了哪一层？** 随后将同一条脚本命令加入现有 CI 工作流。

> 冒烟检查多验证了包含真实进程启动、端口监听等网络服务

<details><summary>2 previous messages</summary>

> 对，冒烟检查多验证了真实进程启动、端口监听和 HTTP 响应这一层。
>
> 现在把它加入云端 CI：在现有测试与覆盖率步骤之后增加 `Run smoke test`，执行 `python scripts/smoke_test.py`。前面的检查通过后，工作流会继续验证应用能否启动；冒烟脚本失败时，这一步也会失败。我会修改同一份 `ci.yml`，提交推送，并核对新运行中的测试、覆盖率和冒烟日志。
>
> <details><summary>Ran 5 commands</summary>
>
> - Ran `git branch --show-current && git remote -v && git status --short && cat .github/workflows/ci.yml && sed -n '1,30p' scripts/smoke_test.py`
>
> - Ran `python3 - <<'PY'
> from pathlib import Path
> path = Path('.github/workflows/ci.yml')
> source = path.read_text(encoding='utf-8')
> assert 'name: Run smoke test' not in source
> source += '\n      - name: Run smoke test\n        run: python scripts/smoke_test.py\n'
> path.write_text(source, encoding='utf-8')
> PY
> git diff --check && git diff -- .github/workflows/ci.yml && git add .github/workflows/ci.yml scripts/smoke_test.py && git commit -m 'Run course smoke checks after tests in cloud CI' && git push origin main && git rev-parse HEAD`
>
> - Ran `gh run list --repo Ciang-ks/isse-lab5-chat-ci --commit 846dec4bf3ca1e0ec9957aaf571a5e65d098939b --json databaseId,status,conclusion,url,headSha --limit 1`
>
> - Ran `gh run watch 40209687034 --repo Ciang-ks/isse-lab5-chat-ci --exit-status --interval 10`
>
> Tool call
>
> Tool: open_in_codex
> Status: completed
>
> - Ran `XDG_CACHE_HOME=/tmp/lab5-gh-cache gh run view 40209687034 --repo Ciang-ks/isse-lab5-chat-ci --log | rg 'Total coverage|passed in|服务已就绪|PASS /|服务已停止|冒烟检查通过'`
>
> </details>
</details>

理解正确。云端现在也已完成冒烟检查：[查看完整成功运行](https://github.com/Ciang-ks/isse-lab5-chat-ci/actions/runs/40209687034)，对应提交 **`846dec4`**。

已在同一份 [ci.yml](~/playground/isse-lab5-chat-ci/.github/workflows/ci.yml) 的测试与覆盖率步骤后增加：

```yaml
- name: Run smoke test
  run: python scripts/smoke_test.py
```

这样每次推送后，先检查接口逻辑与覆盖率，再检查应用在云端能否真正启动。脚本返回失败时，整个工作流也会失败。

本次实际日志确认：

```text
3 passed in 0.08s
Total coverage: 75.82%

服务已就绪
PASS /
PASS /api/hello
服务已停止
冒烟检查通过
```

请在这次运行中分别展开 **Run tests and coverage** 和 **Run smoke test**，将显示覆盖率与冒烟结果的截图发来，可以分两张。我会保存为 `cloud-passed.png`、`cloud-passed-2.png`。

这份运行链接将作为云端成功证据。截图整理后，进入必做的本机 runner 阶段。

> User context
>
> Images:
> - `C:/Users/jjj/AppData/Local/Temp/codex-clipboard-4a8ba02c-aa13-4245-b6a1-9fc4c0b1d0af.png`
> - `C:/Users/jjj/AppData/Local/Temp/codex-clipboard-74f145dc-caa9-4580-97b1-e7f02406acea.png`

<details><summary>3 previous messages</summary>

> 我会先查看并保存两张云端截图。随后进入本机 runner：runner 是实际执行 job 的程序；self-hosted runner 安装在你自己的机器上，通过下载、注册、启动三个动作准备好，之后再由工作流选择它来执行同样的检查。
>
> 我会先确认当前系统和 CPU 架构，再给出对应的安装位置与步骤。注册 token 按课程要求由你在本机终端使用，不需要发到对话中。
>
> Viewed 2 images
>
> <details><summary>Ran 2 commands, searched the web</summary>
>
> - Ran `uname -srm && cat /etc/os-release && git branch --show-current && git remote -v`
>
> - Ran `python3 - <<'PY'
> from pathlib import Path
> import shutil
> out = Path('/home/jxq/playground/isse-labs/lab5/2400017727-蒋徐祺/screenshots')
> for name, source in {
>     'cloud-passed.png': 'codex-clipboard-74f145dc-caa9-4580-97b1-e7f02406acea.png',
>     'cloud-passed-2.png': 'codex-clipboard-4a8ba02c-aa13-4245-b6a1-9fc4c0b1d0af.png',
> }.items():
>     target = out / name
>     assert not target.exists(), f'File already exists: {target}'
>     shutil.copy2(Path('/mnt/c/Users/jjj/AppData/Local/Temp') / source, target)
>     print(target)
> PY`
>
> Searched the web for `https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/add-runners`
>
> Tool call
>
> Tool: open_in_codex
> Status: completed
>
> Tool call
>
> Tool: open_in_codex
> Status: completed
>
> </details>
</details>

两张截图已保存，包含提交 `846dec4` 的成功结果、75.82% 覆盖率和完整冒烟日志：

- [cloud-passed.png](./2400017727-蒋徐祺/screenshots/cloud-passed.png)
- [cloud-passed-2.png](./2400017727-蒋徐祺/screenshots/cloud-passed-2.png)

接下来准备本机 runner。runner 是执行 job 的程序；self-hosted runner 运行在你的电脑上。下载取得程序，注册将它关联到实验仓库，启动后它连接 GitHub 等待任务。目前系统是 **WSL2、Ubuntu 24.04、x86_64**，请选择 **Linux / x64**。

我已请求打开[注册页面](https://github.com/Ciang-ks/isse-lab5-chat-ci/settings/actions/runners/new?arch=x64&os=linux)和内置终端。请在 WSL 终端操作：

1. 在两个代码仓库之外准备目录：

   ```bash
   mkdir -p /home/jxq/actions-runner-lab5
   cd /home/jxq/actions-runner-lab5
   ```

2. 按网页 **Download** 区执行下载、校验和解压命令，使用页面当前提供的版本。已创建目录，无需重复执行网页的 `mkdir actions-runner && cd actions-runner`。
3. 执行网页 **Configure** 区的 `./config.sh ...` 注册命令。名称可填 `lab5-jxq-wsl`；保留默认标签 `self-hosted, Linux, X64`，额外标签留空，工作目录使用默认 `_work`。
4. 前台启动并保持终端打开：

   ```bash
   ./run.sh
   ```

成功时终端应显示 `Connected to GitHub`、`Listening for Jobs`，网页 runner 列表应显示在线空闲。这说明它已经准备好接任务；下一步还需要修改工作流的 `runs-on`。[GitHub 官方说明](https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/add-runners)

注册 token 按课程要求只在你本机使用，无需发给我。完成后，请反馈 **runner 名称、网页状态，以及终端是否出现 `Listening for Jobs`**。

> 你来进行命令

<details><summary>8 previous messages</summary>

> 我来完成下载、校验、解压和环境检查，runner 放在 `/home/jxq/actions-runner-lab5`，与代码仓库分开。
>
> 注册 token 按课程 `AGENTS.md` 第 12 条由你本地管理，Agent 不读取或输出，因此含 token 的注册命令仍需你在终端执行。我会先把其余准备工作完成，再给你留下这一条命令；注册后继续协助启动和验证。
>
> <details><summary>Ran 4 commands</summary>
>
> - Ran `test ! -e /home/jxq/actions-runner-lab5 || ls -d /home/jxq/actions-runner-lab5 /home/jxq/actions-runner-lab5/config.sh /home/jxq/actions-runner-lab5/run.sh 2>/dev/null; uname -srm; command -v curl; command -v tar; command -v sha256sum`
> - Ran `gh api repos/actions/runner/releases/latest --jq '{tag_name, assets: [.assets[] | select(.name | test("linux-x64.*tar.gz$")) | {name,browser_download_url,digest,size}]}'`
> - Ran `mkdir -p /home/jxq/actions-runner-lab5 && curl --fail --location --retry 3 --output /home/jxq/actions-runner-lab5/actions-runner-linux-x64-2.338.1.tar.gz https://github.com/actions/runner/releases/download/v2.338.1/actions-runner-linux-x64-2.338.1.tar.gz && python3 - <<'PY'
> from pathlib import Path
> import hashlib
> path = Path('/home/jxq/actions-runner-lab5/actions-runner-linux-x64-2.338.1.tar.gz')
> digest = hashlib.file_digest(path.open('rb'), 'sha256').hexdigest()
> assert digest == '08e9ccb3604d2462c24b5e33604dc30810296ca15cc65f23cffd4317eb144c37', 'SHA256 mismatch'
> print('SHA256 verified:', digest)
> PY
> tar -xzf /home/jxq/actions-runner-lab5/actions-runner-linux-x64-2.338.1.tar.gz -C /home/jxq/actions-runner-lab5 && /home/jxq/actions-runner-lab5/bin/Runner.Listener --version`
> - Ran `command -v aria2c; command -v wget; ls -lh /home/jxq/actions-runner-lab5/actions-runner-linux-x64-2.338.1.tar.gz`
>
> </details>
>
> 已确认官方 Linux x64 runner 当前版本为 `2.338.1`，下载包约 217 MiB。当前单连接下载较慢，我会改用分段下载，并在解压前核对官方 SHA256；注册步骤仍留在你的终端完成。
>
> <details><summary>Ran 3 commands</summary>
>
> - Ran `pkill -f '^curl --fail --location --retry 3 --output /home/jxq/actions-runner-lab5/actions-runner-linux-x64-2.338.1.tar.gz'`
> - Ran `python3 -u - <<'PY'
> from concurrent.futures import ThreadPoolExecutor, as_completed
> from pathlib import Path
> import hashlib
> import shutil
> import subprocess
> root = Path('/home/jxq/actions-runner-lab5')
> url = 'https://github.com/actions/runner/releases/download/v2.338.1/actions-runner-linux-x64-2.338.1.tar.gz'
> size = 227944224
> parts = 8
> chunk = (size + parts - 1) // parts
>
> def download(i):
>     start, end = i * chunk, min((i + 1) * chunk, size) - 1
>     path = root / f'runner-download.part{i}'
>     subprocess.run(['curl', '--fail', '--silent', '--show-error', '--location', '--retry', '3', '--connect-timeout', '30', '--max-time', '600', '--range', f'{start}-{end}', '--output', str(path), url], check=True)
>     assert path.stat().st_size == end - start + 1, f'Range size mismatch for part {i}'
>     return i
>
> with ThreadPoolExecutor(max_workers=parts) as pool:
>     for future in as_completed([pool.submit(download, i) for i in range(parts)]):
>         print(f'Downloaded part {future.result() + 1}/{parts}', flush=True)
> archive = root / 'actions-runner-linux-x64-2.338.1.tar.gz'
> with archive.open('wb') as out:
>     for i in range(parts):
>         with (root / f'runner-download.part{i}').open('rb') as source:
>             shutil.copyfileobj(source, out)
> with archive.open('rb') as source:
>     digest = hashlib.file_digest(source, 'sha256').hexdigest()
> assert digest == '08e9ccb3604d2462c24b5e33604dc30810296ca15cc65f23cffd4317eb144c37', 'SHA256 mismatch'
> print('Official SHA256 verified', flush=True)
> subprocess.run(['tar', '-xzf', str(archive), '-C', str(root)], check=True)
> for i in range(parts):
>     (root / f'runner-download.part{i}').unlink()
> subprocess.run([str(root / 'bin/Runner.Listener'), '--version'], check=True, cwd=root)
> print('Runner extracted and executable', flush=True)
> PY`
> - Ran `ls -lh /home/jxq/actions-runner-lab5/runner-download.part*`
>
> </details>
>
> 分段下载已有一半完成。下载完成后会统一校验并检查 runner 能否执行；这一步准备程序，还没有将它注册到 GitHub，也没有切换现有工作流。
>
> <details><summary>Explored a list</summary>
>
> - Listed files in `runner-download.part6`
>
> </details>
>
> 已有 7 个分段下载完成，剩最后一个。注册完成后，runner 会在自己的 `_work` 目录检出应用代码；日常开发目录里的虚拟环境不会自动用于任务。下一步配置本机工作流时，会在 runner 工作区单独准备依赖。
>
> <details><summary>Ran a command</summary>
>
> - Ran `./config.sh --help`
>
> Tool call
>
> Tool: open_in_codex
> Status: completed
>
> </details>
</details>

命令准备已完成：

- 安装目录：`/home/jxq/actions-runner-lab5`
- 官方 runner：**2.338.1，Linux x64**
- 官方 SHA256 校验通过
- 版本检查和配置程序启动正常

下载只是准备程序；注册将它关联到实验仓库，启动后才会连接 GitHub 等待任务。现在请在内置 WSL 终端执行：

```bash
cd /home/jxq/actions-runner-lab5
./config.sh \
  --url https://github.com/Ciang-ks/isse-lab5-chat-ci \
  --name lab5-jxq-wsl \
  --work _work
```

提示输入注册 token 时，从[注册页面](https://github.com/Ciang-ks/isse-lab5-chat-ci/settings/actions/runners/new?arch=x64&os=linux)复制到终端。其余选项保留默认值，额外标签留空。注册完成后执行：

```bash
./run.sh
```

保持终端打开。预期看到 `Connected to GitHub` 和 `Listening for Jobs`，网页显示 runner 在线空闲。请反馈这两个状态，随后我修改工作流并触发本机检查。

含 token 的注册步骤留给你，是因为课程 [AGENTS.md](./AGENTS.md) 第 12 条明确要求：“runner 注册 token 由学生本地管理，Agent 不读取或输出。”

> 继续

<details><summary>14 previous messages</summary>

> Stream error
>
> Reconnecting 3/5
> stream disconnected before completion: tls handshake eof
>
> 我先用 `gh` 查询 runner 是否已注册并在线。下一步会把同一份工作流的 `runs-on` 改成 `self-hosted`，让任务交给本机执行。
>
> 本机 runner 会在自己的 `_work` 工作区检出代码，开发终端里的虚拟环境不会自动生效，因此还需要在工作流中明确准备 Python 和依赖。我会根据实际环境调整配置，保留相同的测试、70% 覆盖率和冒烟命令；确认 runner 在线后再推送触发任务。
>
> <details><summary>Ran 2 commands</summary>
>
> - Ran `gh api repos/Ciang-ks/isse-lab5-chat-ci/actions/runners --jq '{total_count, runners: [.runners[] | {name, os, status, busy, labels: [.labels[].name]}]}'`
> - Ran `git branch --show-current && git remote -v && git status --short && cat .github/workflows/ci.yml && /home/jxq/.local/bin/uv --version && /home/jxq/playground/isse-lab5-chat-ci/.venv/bin/python --version`
>
> </details>
>
> runner `lab5-jxq-wsl` 已注册，标签为 `self-hosted / Linux / X64`，目前是离线状态。我会启动它，再切换工作流。
>
> 本机已有 `uv` 和 Python 3.13。工作流会用 `uv` 在 runner 工作区创建带 pip 的 `.venv`，将它加入后续步骤的 PATH，然后执行原来的依赖安装、测试和冒烟命令。这样检查使用的是任务自己的环境。
>
> <details><summary>Ran 5 commands</summary>
>
> - Ran `./run.sh 2>&1 | tee /tmp/lab5-runner-terminal.log`
>
> - Ran `gh api repos/Ciang-ks/isse-lab5-chat-ci/actions/runners --jq '.runners[] | {name,status,busy}'`
>
> - Ran `python3 - <<'PY'
> from pathlib import Path
> path = Path('.github/workflows/ci.yml')
> source = path.read_text(encoding='utf-8')
> assert source.count('runs-on: ubuntu-latest') == 1
> source = source.replace('runs-on: ubuntu-latest', 'runs-on: self-hosted')
> old = '''      - name: Set up Python
>         uses: actions/setup-python@v7
>         with:
>           python-version: '3.13'
> '''
> new = '''      - name: Prepare local Python environment
>         run: |
>           /home/jxq/.local/bin/uv venv --clear --seed --python 3.13 .venv
>           echo "$GITHUB_WORKSPACE/.venv/bin" >> "$GITHUB_PATH"
>           .venv/bin/python --version
> '''
> assert old in source
> path.write_text(source.replace(old,new), encoding='utf-8')
> PY
> git diff --check && git diff -- .github/workflows/ci.yml && git add .github/workflows/ci.yml && git commit -m 'Run the same CI checks on the local self-hosted runner' && git push origin main && git rev-parse HEAD`
>
> - Ran `gh run list --repo Ciang-ks/isse-lab5-chat-ci --commit c348c85d56aa0b2226b0cb067e5e8c427ef9988a --json databaseId,status,conclusion,url,headSha --limit 1`
>
> - Ran `gh run watch 40210628889 --repo Ciang-ks/isse-lab5-chat-ci --exit-status --interval 10`
>
> Tool call
>
> Tool: open_in_codex
> Status: completed
>
> </details>
>
> 本机 runner 已上线，并已接到 `Tests and coverage` 任务。此次提交是 `c348c85`，终端已显示 `Running job`；现在等待依赖安装和完整检查结束，再核对网页与终端是否对应同一次任务。
>
> <details><summary>Ran a command</summary>
>
> - Ran `ps -eo pid,etime,args | rg '[/]home/jxq/.local/bin/uv venv|[p]ython -m pip install'`
>
> </details>
>
> 代码检出已完成，目前网页仍显示在准备 Python 环境。首次运行需要创建虚拟环境并下载依赖，我会继续核对各步骤结果；仅接到任务还不能算本机检查成功。
>
> Python 环境准备已通过，现在正在安装依赖，尚未进入测试步骤。本次仍使用和云端相同的两份依赖清单及检查命令；我会等完整结果出来，再确认本机实验是否通过。
>
> <details><summary>Ran a command</summary>
>
> - Ran `ps -eo pid,etime,comm | rg 'python|pip|uv|Runner'`
>
> </details>
>
> 依赖安装比云端慢，目前进程仍在运行，还没有测试结果。我会检查是否有下载进展，避免只因任务已启动就提前结束验证。
>
> <details><summary>Ran a command</summary>
>
> - Ran `du -sh /tmp/pip-unpack-* /tmp/pip-metadata-* 2>/dev/null; ps -eo pid,etime,comm | rg 'python|Runner'`
>
> </details>
>
> 本机检查已全部通过，runner 终端也显示 `completed with result: Succeeded`。我会再核对日志中的 runner 名称、工作区、Python 版本、覆盖率和冒烟结果，随后停止 runner，并保留终端日志供你截图。
>
> <details><summary>Ran 4 commands</summary>
>
> - Ran `XDG_CACHE_HOME=/tmp/lab5-gh-cache gh run view 40210628889 --repo Ciang-ks/isse-lab5-chat-ci --log | rg 'Runner name:|Runner group name:|Machine name:|Python 3|Total coverage|passed in|服务已就绪|PASS /|服务已停止|冒烟检查通过|/actions-runner-lab5/_work/'`
>
> - Ran `gh api repos/Ciang-ks/isse-lab5-chat-ci/actions/runs/40210628889/jobs --jq '.jobs[] | {name,conclusion,head_sha,runner_name,runner_group_name,labels,html_url}'`
>
> - Ran `gh api repos/Ciang-ks/isse-lab5-chat-ci/actions/runners --jq '.runners[] | {name,status,busy}' && cat /tmp/lab5-runner-terminal.log`
>
> Tool call
>
> Tool: open_in_codex
> Status: completed
>
> - Ran `ps -eo pid,etime,args | rg '[/]home/jxq/actions-runner-lab5/bin/Runner.Listener|[.]\/bin/Runner.Listener|[.]\/run-helper.sh|[.]\/run.sh'`
>
> </details>
</details>

本机 CI 已全部通过：[查看运行](https://github.com/Ciang-ks/isse-lab5-chat-ci/actions/runs/40210628889)，对应提交 **`c348c85`**。

实际结果：

- runner：`lab5-jxq-wsl`，运行在你的 WSL Ubuntu 上。
- Python：3.13.11。
- 测试：**3 passed**，覆盖率 **75.82%**。
- 冒烟：首页和 `/api/hello` 均通过，临时服务正常停止。

本次修改了同一份 [ci.yml](~/playground/isse-lab5-chat-ci/.github/workflows/ci.yml)：`runs-on: self-hosted` 将任务交给本机；`uv` 在 runner 的 `_work` 工作区创建独立 `.venv`，加入后续步骤的 PATH，再安装依赖。测试、覆盖率和冒烟命令与云端保持一致，之前的云端运行仍保留。

终端已确认收到任务并完成：

```text
Running job: Tests and coverage
Job Tests and coverage completed with result: Succeeded
```

runner 已停止，并核对无残留进程。终端日志保存在 `/tmp/lab5-runner-terminal.log`。

请补充两项截图：

1. **本机 Actions**：显示 runner 名称及完整检查结果。
2. **本机终端**：显示接收任务和 `Succeeded`。可在内置终端用 `cat /tmp/lab5-runner-terminal.log` 展示已保存日志后截图。

同时请解释：**为什么任务需要在 `_work` 中重新准备环境，而不能直接依赖开发终端已激活的 `.venv`？** 收到后整理截图，再复制最终应用并准备课程提交材料。

> 因为开发终端的 .venv 包含个人未提交的修改且不可复现，必须重新构建纯净的 _work，才能确保 CI 一致
> 我要在哪里找到本机action 截图之类的

方向对，修正一点：`.venv` 保存解释器和依赖，未提交的应用修改通常在源代码目录。runner 在 `_work` 检出指定提交，而且不会继承开发终端激活环境时设置的 PATH，所以工作流要明确准备自己的 Python 和依赖。

截图取这两处：

1. **本机 Actions 截图**
   打开[本机成功运行](https://github.com/Ciang-ks/isse-lab5-chat-ci/actions/runs/40210628889)，点击 **Tests and coverage**：
   - 展开 **Set up job**，截到 `Runner name: 'lab5-jxq-wsl'`。
   - 展开 **Run tests and coverage** 和 **Run smoke test**，截到 `3 passed`、`75.82%` 和冒烟通过。

   可以分成两三张截图。

2. **本机终端截图**
   在 Codex 内置终端或 WSL 终端执行：

   ```bash
   cat /tmp/lab5-runner-terminal.log
   ```

   截到 `Connected to GitHub`、`Running job` 和 `completed with result: Succeeded`。runner 已停止，不需要重新启动。

把截图直接发到这里，我会按内容保存到你的课程目录，命名为 `self-hosted-actions.png`、`self-hosted-actions-2.png` 和 `self-hosted-terminal.png`。

> User context
>
> Images:
> - `C:/Users/jjj/AppData/Local/Temp/codex-clipboard-19589d99-a2f2-4055-9a2e-05ad2f8206ff.png`
> - `C:/Users/jjj/AppData/Local/Temp/codex-clipboard-1655a39a-0b43-494a-9136-a53787837c12.png`

<details><summary>5 previous messages</summary>

> 我先查看这两张截图并按内容保存。接下来整理课程提交材料：实验仓库保留 Actions 历史，课程个人目录保存最终应用、截图和真实对话轨迹。
>
> 我会核对课程分支与本机成功提交，再将已通过本机检查的应用文件复制到个人目录的 `app/`，保留工作流、测试、依赖和配置示例。最后核对截图是否齐全；真实对话轨迹需要你导出或提供分享链接。
>
> Viewed 2 images
>
> <details><summary>Ran 2 commands</summary>
>
> - Ran `git branch --show-current && git remote -v && git status --short && rg --files --hidden '2400017727-蒋徐祺'`
> - Ran `git branch --show-current && git remote -v && git status --short && git log -1 --oneline && git ls-files && gh api repos/Ciang-ks/isse-lab5-chat-ci/actions/runners --jq '.runners[] | {name,status,busy}'`
>
> </details>
>
> 两张截图分别包含本机终端接收并完成任务，以及 Actions 中的测试、覆盖率和冒烟结果，可以作为本机阶段证据。GitHub 也已确认 runner 为离线状态。
>
> 我会按原 PNG 格式保存截图，并复制提交 `c348c85` 中已跟踪的应用文件，确保课程副本与本机成功版本一致。整理后剩下的必要材料是你导出的真实对话轨迹。
>
> <details><summary>Ran a command</summary>
>
> - Ran `python3 - <<'PY'
> from pathlib import Path
> import hashlib
> import shutil
> import subprocess
>
> personal = Path('/home/jxq/playground/isse-labs/lab5/2400017727-蒋徐祺')
> shots = personal / 'screenshots'
> for name, source in {
>     'self-hosted-terminal.png': 'codex-clipboard-19589d99-a2f2-4055-9a2e-05ad2f8206ff.png',
>     'self-hosted-actions.png': 'codex-clipboard-1655a39a-0b43-494a-9136-a53787837c12.png',
> }.items():
>     target = shots / name
>     assert not target.exists(), f'Already exists: {target}'
>     shutil.copy2(Path('/mnt/c/Users/jjj/AppData/Local/Temp') / source, target)
>     print('Saved:', target)
>
> repo = Path('/home/jxq/playground/isse-lab5-chat-ci')
> commit = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
> assert commit == 'c348c85d56aa0b2226b0cb067e5e8c427ef9988a'
> assert not subprocess.check_output(['git', '-C', str(repo), 'status', '--porcelain'])
> app = personal / 'app'
> assert not app.exists(), 'Inspect existing app directory before copying'
> files = subprocess.check_output(['git', '-C', str(repo), 'ls-tree', '-r', '--name-only', '-z', commit]).decode().split('\0')
> count = 0
> for name in filter(None, files):
>     assert not Path(name).is_absolute() and '..' not in Path(name).parts
>     assert '.env' not in Path(name).parts and '.venv' not in Path(name).parts
>     content = subprocess.check_output(['git', '-C', str(repo), 'show', f'{commit}:{name}'])
>     target = app / name
>     target.parent.mkdir(parents=True, exist_ok=True)
>     target.write_bytes(content)
>     assert hashlib.sha256(target.read_bytes()).digest() == hashlib.sha256(content).digest()
>     count += 1
> print(f'Copied and verified {count} tracked files from {commit[:7]}')
> print('Screenshot files:')
> for path in sorted(shots.iterdir()):
>     print(path.name, path.stat().st_size, 'bytes')
> print('Real conversation trace present:', (personal / 'AGENT_TRACE.md').exists())
> PY
> git diff --check && git status --short`
>
> Tool call
>
> Tool: open_in_codex
> Status: completed
>
> </details>
</details>

两张截图已保存：

- [本机 Actions](./2400017727-蒋徐祺/screenshots/self-hosted-actions.png)
- [本机终端](./2400017727-蒋徐祺/screenshots/self-hosted-terminal.png)

课程材料已整理到 `/home/jxq/playground/isse-labs/lab5/2400017727-蒋徐祺/`：

- `app/`：从本机成功提交 **`c348c85`** 复制的 14 个文件，逐一核对一致，包含隐藏的工作流、测试和配置示例。
- `screenshots/`：共 6 张原图，四类证据齐全。
- runner 已停止，GitHub 状态为 **offline**。

实验仓库保留运行历史，课程个人目录保存最终交付副本。云端与本机成功记录可以对应不同提交，前面的运行链接均已保留在对话中。

**目前只缺真实对话轨迹。** 请导出本次完整对话，保存为：

```text
/home/jxq/playground/isse-labs/lab5/2400017727-蒋徐祺/AGENT_TRACE.md
```

也可以提供可访问的对话分享链接。轨迹应包含真实讲解、你的回答和实际运行结果，不能用总结代替。

保存后告诉我，我会检查材料，再按你此前授权完成课程提交和 PR，标题为：

```text
[Lab5] 2400017727-蒋徐祺 GitHub Actions持续集成
```
