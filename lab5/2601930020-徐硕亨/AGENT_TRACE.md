# Lab 5 Agent 協作對話軌跡

- **學號**：2601930020
- **姓名**：徐碩亨 (Hsu Shuo-Heng)
- **課程分支**：`lab5/2601930020-hsushuoheng`
- **獨立實驗倉庫**：[AvinHsu/isse-lab5-chat-ci](https://github.com/AvinHsu/isse-lab5-chat-ci)

---

## 實驗總覽與關鍵鏈接

1. **自動測試與覆蓋率**：
   - 後端測試涵蓋連通性、會話 CRUD、訊息 CRUD（含 Mock LLM）以及各類非法輸入。
   - 單元測試行覆蓋率達到 **88%**（課程要求 ≥ 70%）。
   - 首次雲端 CI 通過鏈接：[Run #40072658735](https://github.com/AvinHsu/isse-lab5-chat-ci/actions/runs/40072658735)
2. **失敗製造與排查定位**：
   - 故意改壞 `/api/hello` 回覆為 `{"message": "Hello"}`，導致 `test_hello_endpoint` 觸發 `AssertionError`。
   - 失敗運行鏈接：[Run #40072731459](https://github.com/AvinHsu/isse-lab5-chat-ci/actions/runs/40072731459)
   - 失敗截圖：`screenshots/failed.png`
3. **冒煙檢查與雲端修復通過**：
   - 修復接口並引入 `scripts/smoke_test.py`，驗證服務啟動、首頁 `/` 與 `/api/hello` 連通性。
   - 雲端通過鏈接：[Run #40073893047](https://github.com/AvinHsu/isse-lab5-chat-ci/actions/runs/40073893047)
   - 通過截圖：`screenshots/cloud-passed.png`
4. **本機 Self-hosted Runner**：
   - 本機 macOS ARM64 註冊並前台運行 GitHub runner。
   - 工作流切換為 `runs-on: self-hosted`，本機成功完成全套測試與冒煙檢查。
   - 本機運行鏈接：[Run #40075541683](https://github.com/AvinHsu/isse-lab5-chat-ci/actions/runs/40075541683)
   - 本機 Actions 截圖：`screenshots/self-hosted-actions.png`
   - 本機終端機接單截圖：`screenshots/self-hosted-terminal.png`

---

## 對話軌跡記錄

### User

幫我抓取遠端最新版本

### Assistant

正在為你從遠端（`origin` 與 `upstream`）抓取最新版本中，請稍候。

### Assistant

已完成遠端最新版本的抓取，並將本地的 `main` 分支快進同步至 `upstream/main`（最新 commit：`37383f7`，包含 Lab 5 內容）。

### 目前狀態
* **當前分支**：`lab4/2601930020-hsushuoheng`（乾淨，無衝突）
* **本地 `main`**：已同步至 `upstream/main`（超前個人遠端 `origin/main` 51 個 commit）

---

### 後續可執行的操作（依需求挑選）

1. **同步個人 Fork (`origin/main`)**：
   ```bash
   git push origin main
   ```

2. **切換並建立 Lab 5 工作分支**：
   ```bash
   git checkout -b lab5/2601930020-hsushuoheng main
   ```

### User

lab5工作是什麼

### User

lab5工作是什麼

### Assistant

Lab 5 的主題是 **「GitHub Actions 持續整合（CI）與 本機 Self-hosted Runner」**。

核心任務是把你在 **Lab 2 寫的聊天應用** 獨立出去做自動化測試與 CI 流水線，最後把結果整理回課程倉庫。

---

### 核心要做的事（5 個階段）

1. **獨立實驗倉庫**：在 GitHub 新建一個獨立的個人倉庫（如 `isse-lab5-chat-ci`），把 Lab 2 的聊天應用放進去。
2. **自動測試 & 雲端 CI**：
   - 撰寫 `pytest`：測試聊天紀錄的一套 CRUD 流程及一類非法輸入（LLM 模型調用使用 Mock，不用真實 API Key）。
   - 後端測試覆蓋率必須 **≥ 70%**（使用 `pytest-cov`）。
   - 編寫 `.github/workflows/ci.yml`，推送代碼後在 GitHub 雲端環境（`ubuntu-latest`）自動跑測試與覆蓋率檢查。
3. **製造失敗與修復（取證）**：
   - 故意改壞一個功能推上去讓 CI 報錯，從 Actions 日志中排查定位問題。
   - 修復後再次推送變綠燈（保留失敗截圖與修復前後記錄）。
4. **冒煙測試（Smoke Test）**：
   - 引入並適配官方提供的 `scripts/smoke_test.py`（檢查服務能否啟動、首頁與 `/api/hello` 是否正常）。
   - 整合至 `ci.yml`。
5. **切換到本機 Runner（必做）**：
   - 在自己電腦上下載、註冊 GitHub Actions 的 `self-hosted runner` 並在終端機啟動。
   - 將 `ci.yml` 的 `runs-on` 改為 `self-hosted`，驗證本機接單並跑通整套測試與冒煙流程。

---

### 最終繳交材料（回課程倉庫提交 PR）

在課程倉庫建分支 `lab5/2601930020-hsushuoheng`，目錄結構如下：
```text
lab5/2601930020-徐硕亨/
├── AGENT_TRACE.md                 # 完整對話軌跡
├── screenshots/
│   ├── failed.png                 # CI 失敗截圖
│   ├── cloud-passed.png           # 雲端跑通與覆蓋率截圖
│   ├── self-hosted-actions.png    # 本機 Runner 在 Actions 成功的截圖
│   └── self-hosted-terminal.png   # 本機終端機接單執行的截圖
└── app/                           # 包含 ci.yml、測試腳本、冒煙腳本與最終應用的代碼
```

---

如果你準備好開始，下一步是建立課程分支 `lab5/2601930020-hsushuoheng` 並去 GitHub 建立新的實驗倉庫。隨時告訴我即可開始引導。

### User

ok

### Assistant

## 準備階段：環境與倉庫建立

### 概念講解

在 Lab 2 中，你已經做出了可透過網頁互動的聊天應用。日後若修改介面、調整資料結構或擴充功能，都需要反覆驗證既有功能是否健全。**持續整合（CI, Continuous Integration）** 就是將測試與檢查寫成自動化流水線，每當程式碼推送（Push）到遠端，即自動執行驗證並即時反饋結果。

本次實驗將延續 Lab 2 的聊天應用：
1. 編寫後端自動化測試與覆蓋率檢查。
2. 透過 GitHub Actions 於雲端環境自動觸發執行。
3. 刻意改壞功能體驗 CI 抓錯與修復驗證。
4. 加入冒煙檢查（Smoke Test）確保服務能正常啟動與回應。
5. 將同一個 CI 工作流切換到你本機的 Self-hosted Runner 上執行。

---

### 人機分工與兩個倉庫的用途

* **課程倉庫（當前目錄：`isse-labs-hw`）**：
  * 用途：存放最終驗收材料（應用程式碼複本、測試日誌截圖、對話軌跡 `AGENT_TRACE.md`），最後發 PR 回主課程倉庫評分。
* **實驗倉庫（新建 GitHub 個人倉庫，如 `isse-lab5-chat-ci`）**：
  * 用途：實際配置 GitHub Actions 工作流、觸發 CI 構建、註冊並跑本機 Runner。
* **分工**：
  * **你**：建立分支與目錄、在 GitHub 網頁新建實驗倉庫、操作終端機執行推拉與啟動 Runner。
  * **我**：負責講解步驟細節、編寫測試與 CI 設定檔、協助排查錯誤及最後整理提交材料。

---

### 本步操作指引

#### 1. 建立課程分支與個人目錄
請在當前課程倉庫（`isse-labs-hw`）執行以下指令，從最新的 `main` 建立 Lab 5 分支與目錄：

```bash
# 切換並建立 lab5 分支
git checkout -b lab5/2601930020-hsushuoheng main

# 建立個人的 lab5 目錄
mkdir -p lab5/2601930020-徐硕亨
```

#### 2. 建立並複製獨立實驗倉庫
1. 前往 GitHub 新建一個全新的 **Public** 個人倉庫，名稱建議：`isse-lab5-chat-ci`（勾選初始化 README 或空倉庫皆可，預設分支設為 `main`）。
2. 在課程倉庫**外部**（例如同層的 `~/Desktop/北大/智能化軟件/`）將其 clone 下來：
   ```bash
   cd /Users/apple/Desktop/北大/智能化軟件
   git clone <你的實驗倉庫 Git 地址> isse-lab5-chat-ci
   ```

完成後，請將**實驗倉庫的 GitHub 網址**與**本地絕對路徑**回覆給我，我們立即將 Lab 2 應用移入並開始第一階段測試！

### User

從這裡可以開啟終端機嗎？

### Assistant

可以，有兩種方式：

### 1. IDE 內建終端機快捷鍵
* **快速鍵**：按下 **`Control + \``**（即鍵盤數字 1 左邊的波浪鍵 `~`）
* **選單**：點擊頂部選單的 **Terminal（終端機）** → **New Terminal（新增終端機）**
* **命令面板**：按 **`Cmd + Shift + P`**，輸入 `View: Toggle Terminal` 並按 Enter。

---

### 2. 或者直接交給我跑
你不需要手動開終端機，我可以直接在環境裡幫你執行命令。
如果你已經在 GitHub 上建好倉庫，直接把**倉庫網址**貼給我，我幫你跑建立分支、建立目錄以及 `git clone`！

### User

你幫我吧

### Assistant

我已經幫你在課程倉庫完成前置作業了：
* ✅ 已切換並建立課程分支：`lab5/2601930020-hsushuoheng`
* ✅ 已建立個人目錄：`lab5/2601930020-徐硕亨`

---

### 只剩一個需要你在瀏覽器點擊的動作（10 秒鐘）

因為在 GitHub 建立新倉庫需要你的帳號授權，請直接點開網頁：
👉 **[https://github.com/new](https://github.com/new)**

1. **Repository name**：填入 `isse-lab5-chat-ci`
2. **Visibility**：選 **Public**
3. 其餘保持預設不用勾選，直接點最底下的 **Create repository**

按完後回我一句**「建好了」**，接下來的 `git clone`、複製 Lab 2 聊天應用程式碼、配置測試與 CI 工作流，我全部幫你自動完成！

### User

建造好了

### Assistant

正在將 `isse-lab5-chat-ci` clone 至本地目錄，請稍候。

### Assistant

正在將初始應用程式碼提交並推送至 `isse-lab5-chat-ci` 的 `main` 分支，請稍候。

### Assistant

正在虛擬環境中安裝應用與測試相依套件（`Flask`, `requests`, `pytest`, `pytest-cov` 等），請稍候。

### Assistant

正在提交測試套件與 CI 設定檔並推送到 GitHub，請稍候。

### Assistant

正在將刻意改壞的程式碼提交並推送到 GitHub，以觸發 CI 失敗進行排查實驗。

### Assistant

正在等待 GitHub Actions 執行並產生失敗記錄...

### Assistant

目前進度非常順利，前兩項任務的進展如下：

### 任務 1 進度回報（測試與雲端 CI）
1. **測試與覆蓋率**：我們為聊天應用編寫了完整的測試（包含連通性檢查、會話 CRUD、訊息 CRUD 與非法輸入拒絕，模型調用使用 Mock）。本機測量後端行覆蓋率達到 **88%**（課程要求 ≥ 70%）。
2. **雲端 CI 工作流**：已建立 `.github/workflows/ci.yml`，首次推送即在 GitHub 雲端環境（`ubuntu-latest`）全數通過：
   * 第一次成功運行：[Run #40072658735](https://github.com/AvinHsu/isse-lab5-chat-ci/actions/runs/40072658735)

---

### 任務 2：故意製造失敗並排查（目前階段）

#### 概念與改動說明
CI 的核心價值不僅在於顯示綠勾，更在於程式出錯時能第一時間在日誌中精確指出失敗點。
為了完成排查實驗：
* 我在 `app.py` 中將 `/api/hello` 的回覆內容故意改壞：由原本的 `{"message": "你好"}` 改為 `{"message": "Hello"}`。
* 保持測試程式碼的預期不變，推送後 GitHub Actions 觸發執行並如期**變紅報錯**。

👉 **本次失敗運行連結**：[Run #40072731459](https://github.com/AvinHsu/isse-lab5-chat-ci/actions/runs/40072731459)

---

### 需要你配合的操作與回饋

1. 請點開上方的 **[失敗運行連結](https://github.com/AvinHsu/isse-lab5-chat-ci/actions/runs/40072731459)**，點進 `test` job，展開標紅的 **`Run tests with coverage`** 步驟。
2. 將包含**失敗測試案例名稱與 AssertionError 斷言**的畫面截圖。
   * 請將截圖命名為 **`failed.png`** 存放到課程倉庫的 `lab5/2601930020-徐硕亨/screenshots/failed.png`（或者直接發在這段對話中，由我幫你整理存檔）。
3. 在對話中簡單回答我這三個問題：
   * **哪一個測試函數（Test function）失敗了？**
   * **測試期望（Expected）的內容是什麼？**
   * **實際（Actual）得到的內容是什麼？**

收到你的回答與截圖後，我們馬上把程式碼修復恢復綠燈，並推進至任務 3（冒煙測試）！

### User

幫我把圖片存起來
1.def test_hello_endpoint(client)
2.你好
3.hello

### Assistant

已修復 `app.py` 並將冒煙檢查腳本加入 CI 工作流，正在推送到 GitHub...

### Assistant

圖片已幫你存好在課程個人目錄中：
* ✅ `lab5/2601930020-徐硕亨/screenshots/failed.png`

你的分析完全正確：
1. **失敗函數**：`test_hello_endpoint(client)`
2. **期望值**：`{"message": "你好"}`
3. **實際值**：`{"message": "Hello"}`

---

### 任務 3 完成（修復 + 冒煙檢查雲端通過）

我已經將 `app.py` 的 `"你好"` 恢復，並將課程的冒煙測試腳本（`scripts/smoke_test.py`）加入 CI 工作流推送到 GitHub。
本次雲端運行已經**全數綠燈通過**：
👉 **雲端成功運行連結**：[Run #40073893047](https://github.com/AvinHsu/isse-lab5-chat-ci/actions/runs/40073893047)

> **請幫忙截圖**：點開上方連結，展開 `Run tests with coverage`（顯示 88% 覆蓋率）和 `Run smoke test`（顯示冒煙檢查通過），截圖發給我，我幫你儲存為 `cloud-passed.png`。

---

## 任務 4：切換到本機 Self-hosted Runner（最後一個核心任務）

### 概念講解
先前的檢查都在 GitHub 的雲端虛擬機（`ubuntu-latest`）執行。**Self-hosted Runner** 是在自己電腦上安裝 GitHub 的執行代理程式，讓 GitHub 把 CI 任務派發到你的本機執行。
這能讓你在本機環境直接重現 CI 測試，也能節省雲端額度。配置分為三個動作：**下載**適合本機架構的程式、使用臨時 token **註冊**綁定到實驗倉庫、在終端機前台**啟動**監聽任務。

---

### 本步操作指引（在自己終端機執行）

1. 打開倉庫的 Runner 新增頁面：
   👉 **[新增 Self-hosted Runner](https://github.com/AvinHsu/isse-lab5-chat-ci/settings/actions/runners/new)**
2. 頁面選項請選：
   * **Runner image**：`macOS`
   * **Architecture**：`ARM64`（因為你的 Mac 是 Apple Silicon 晶片）
3. 開啟本機終端機，在倉庫**外部**的目錄（例如 `~/actions-runner`）依序貼上 GitHub 頁面給你的指令：
   ```bash
   # 1. 建立並進入目錄
   mkdir -p ~/actions-runner && cd ~/actions-runner

   # 2. 下載並解壓（依 GitHub 頁面給的最新版本 curl 與 tar 指令）
   ...

   # 3. 註冊（頁面會附帶一串 --token 臨時憑證，按 Enter 保持預設即可）
   ./config.sh --url https://github.com/AvinHsu/isse-lab5-chat-ci --token <頁面上的TOKEN>

   # 4. 前台啟動監聽
   ./run.sh
   ```
4. 終端機出現 **`Listening for Jobs`**，且 GitHub 網頁的 Runners 列表顯示 **`Idle`（綠色在線）** 即表示環境就緒！

請把 `cloud-passed.png` 截圖發給我，並在 runner 啟動完成後告訴我，我立即幫你把 `ci.yml` 切換為 `runs-on: self-hosted` 觸發本機執行！

### User

我沒找到88％的

### Assistant

請點擊畫面左側選單的 **`✔ test`**（或中間方框裡的 **`✔ test  9s`**）進入日誌詳情頁面！

進入後會看到各個執行步驟：
1. 點開 **`Run tests with coverage`**（會展開黑色終端機日誌，最底下就會看到印出 `app.py ... 88%` 的表格）
2. 點開 **`Run smoke test`**（會看到 `PASS /`、`PASS /api/hello`、`冒烟检查通过`）

截一張包含覆蓋率表格與冒煙通過的日誌圖給我，我幫你覆蓋更新 `cloud-passed.png`！

### Assistant

太棒了，這張覆蓋率表格非常完整（**88.20%**，全部 5 個測試通過），我已經把它覆蓋儲存為：
* ✅ `lab5/2601930020-徐硕亨/screenshots/cloud-passed.png`

---

### 接下來進行最後一個核心任務：本機 Self-hosted Runner

請打開瀏覽器前往你的倉庫 Runner 頁面：
👉 **[https://github.com/AvinHsu/isse-lab5-chat-ci/settings/actions/runners/new](https://github.com/AvinHsu/isse-lab5-chat-ci/settings/actions/runners/new)**

1. 點選 **macOS** 與 **ARM64**。
2. 打開終端機，在使用者家目錄建立資料夾並執行下載、註冊與啟動：
   ```bash
   mkdir -p ~/actions-runner && cd ~/actions-runner
   ```
   * 貼上頁面給的 **Download** 指令（curl 下載與 tar 解壓）
   * 貼上頁面給的 **Configure** 指令（包含 `./config.sh --url ... --token ...`，過程中所有提示直接按 **Enter** 採用預設值即可）
   * 最後執行：
     ```bash
     ./run.sh
     ```
3. 當終端機印出：
   ```text
   √ Connected to GitHub
   Current runner version: '...'
   Listening for Jobs
   ```
   就代表本機 Runner 已經在線等待接單！

請保持該終端機視窗開啟，並在就緒後跟我說一聲，我立即把 `ci.yml` 切換為本機模式推上去觸發！

### User

apple@sslvpn-026 actions-runner % curl -o actions-runner-osx-arm64-2.338.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.338.0/actions-runner-osx-arm64-2.338.0.tar.gz
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
  0     0    0     0    0     0      0      0 --:--:--  0:00:01 --:--:--     0
100  122M  100  122M    0     0  3029k      0  0:00:41  0:00:41 --:--:-- 4636k
apple@sslvpn-026 actions-runner % echo "dea7a58796ce215fc424a8b27c0fdd9b813fa5fc03d109a4a1d38131d6bfa1a3  actions-runner-osx-x64-2.338.0.tar.gz" | shasum -a 256 -c
shasum: actions-runner-osx-x64-2.338.0.tar.gz: No such file or directory
actions-runner-osx-x64-2.338.0.tar.gz: FAILED open or read
shasum: WARNING: 1 listed file could not be read
apple@sslvpn-026 actions-runner % tar xzf ./actions-runner-osx-x64-2.338.0.tar.gz
tar: ./actions-runner-osx-x64-2.338.0.tar.gz: m: No such file or directory
不知道下載到哪去了

### Assistant

檔案下載成功了，就在當前目錄！

問題出在：你下載的是 **`arm64`** 版本，但解壓指令貼成 **`x64`** 了。

請直接在終端機貼上這行解壓：
```bash
tar xzf ./actions-runner-osx-arm64-2.338.0.tar.gz
```

解壓完成後，接著執行 GitHub 網頁上的 `./config.sh` 註冊指令，所有提示按 Enter 預設即可，最後跑 `./run.sh`！

### User

Enter the name of the runner group to add this runner to: [press Enter for Default]         

Enter the name of runner: [press Enter for sslvpn-026]

### Assistant

全部直接按 **Enter** 鍵採用預設值即可！

接下來如果提示：
* `Enter any additional labels...` ➡️ 按 **Enter**
* `Enter name of work folder... [_work]` ➡️ 按 **Enter**

完成註冊後，輸入：
```bash
./run.sh
```
看到出現 `Listening for Jobs` 就完成了，請保持那個視窗不要關閉！

### User

完成了

### Assistant

註冊已經順利完成了！只差最後啟動一步：

請在剛才的終端機視窗輸入：
```bash
./run.sh
```

按下 Enter 後，終端機應該會印出：
```text
√ Connected to GitHub
Current runner version: '2.338.0'
2026-10-24 ... Listening for Jobs
```

**請保持該終端機視窗不要關閉**（等一下本機執行任務時需要截取該終端機畫面的日誌），啟動後回我一聲，我立即推送本機 CI 工作流！

### User

ok

### Assistant

已將工作流切換為 `runs-on: self-hosted`，正在推送到 GitHub 觸發本機執行...

### Assistant

任務已被本機 Runner 接收並正在執行中，請稍候...

### Assistant

本機 Runner 已經**成功執行並完成了整套 CI 檢查**！

👉 **本機成功運行連結**：[Run #40075541683](https://github.com/AvinHsu/isse-lab5-chat-ci/actions/runs/40075541683)

---

### 只剩最後兩張截圖：

1. **`self-hosted-actions.png`**：
   * 點開上方 [Run #40075541683](https://github.com/AvinHsu/isse-lab5-chat-ci/actions/runs/40075541683) 頁面，截取本機任務執行成功的畫面。
2. **`self-hosted-terminal.png`**：
   * 截取剛才執行 `./run.sh` 的本機終端機畫面（畫面中包含 `Running job: test` 以及 `Job test completed with result: Succeeded`）。

截圖完成後，可以在終端機按 **`Control + C`** 停止 runner。

---

### 我已經幫你同步好的材料：
* ✅ 最終本機成功版本的所有應用程式碼、測試、`ci.yml` 與冒煙腳本已複製到課程目錄：`lab5/2601930020-徐硕亨/app/`。
* ✅ `failed.png` 與 `cloud-passed.png` 已妥善存放於 `lab5/2601930020-徐硕亨/screenshots/`。

請把這最後兩張圖發給我，我們立即補齊截圖、建立對話軌跡並推送發起 PR！

