# Lab 4：監控自己的應用——Prometheus 與 Grafana

本項目為北京大學《智能化軟體開發》實驗四（Lab 4）成果，延續 Lab 2/3 完成的 Flask 聊天應用，為後端服務埋設 Prometheus 業務指標，使用本機 Prometheus 定期採集，並透過 Grafana 儀表盤進行可視化觀測。最後由自動化流量模擬腳本模擬基準、突發流量、慢請求與錯誤注入場景，驗證監控系統的觀測能力。

* **學號**：2601930020
* **姓名**：徐碩亨

---

## 1. 運行模式說明（Mock vs Real）

為保證實驗的可重現性並避免產生外部模型調用成本，本項目在後端實現了嚴格區分的雙模式：

* **Mock 模式（實驗預設）**：
  * 通過環境變數 `APP_MODE=mock` 控制（預設值），無需 `DEEPSEEK_API_KEY`，後端不初始化、不調用外部 DeepSeek API，絕不產生模型調用費用。
  * 提供專用狀態檢驗接口 `GET /api/status`，返回 `{"mode": "mock", "external_model_calls": false}`，供調度腳本自動核驗。
  * 支援在 mock 模式下接收實驗參數：
    * `delay_seconds`：在後端處理邏輯中產生真實延遲（`time.sleep`），模擬大模型耗時生成。
    * `force_error`：若為 `true`，後端直接返回 HTTP 503 錯誤，模擬上游服務故障。
* **Real 模式**：
  * 設定 `APP_MODE=real` 並配置有效 `DEEPSEEK_API_KEY` 時，系統回退至原本調用 DeepSeek API 的生產模式。此模式下狀態接口如實報告 `{"mode": "real", "external_model_calls": true}`。

---

## 2. 指標定義與埋點

使用 `prometheus_client` 庫在 [metrics.py](file:///Users/apple/Desktop/北大/智能化軟件/isse-labs-hw/lab4/2601930020-hsushuoheng/metrics.py) 中定義三個核心指標，並在聊天發送接口（`/api/conversations/<id>/messages`）中進行埋點：

| 指標名稱 | 類型 | 標籤 / 桶配置 | 埋點與統計意義 |
| --- | --- | --- | --- |
| `chat_requests_total` | Counter | `outcome="success"`<br>`outcome="error"` | 聊天處理完成後累計次數。成功加一，模擬出錯或異常時以 error 累加。初始化兩標籤均為 0。 |
| `chat_inprogress_requests` | Gauge | 無 | 進入聊天處理時 `inc()`，在 `finally` 區塊中 `dec()`，精準反映當前並發執行中的請求數，異常路徑必定回落。 |
| `chat_request_duration_seconds` | Histogram | `(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 3.5, 5.0, 10.0)` | 記錄服務端處理單次聊天請求的真實耗時（秒），成功與失敗均記錄。 |

* **接口暴露**：應用暴露 `/metrics` 端點，以標準 Prometheus 格式輸出指標。監控採集、狀態核驗及前端靜態資源訪問均不計入聊天業務指標。

---

## 3. 本地工具版本、目錄與啟動命令

所有監控工具與運行數據均嚴格限制在個人目錄下，不寫入倉庫根目錄或上層目錄：

* **作業系統與架構**：macOS (Darwin arm64)
* **Prometheus**：版本 `v3.15.0`
  * 程式路徑：`.tools/prometheus/prometheus`
  * 數據路徑：`.runtime/prometheus/`
  * 啟動命令：
    ```bash
    ./.tools/prometheus/prometheus \
      --config.file=prometheus.yml \
      --storage.tsdb.path=.runtime/prometheus \
      --web.listen-address=127.0.0.1:9090
    ```
* **Grafana**：版本 `v11.5.2`
  * 程式路徑：`.tools/grafana/bin/grafana`
  * 數據與日誌：`.runtime/grafana/`
  * 啟動命令：
    ```bash
    ./.tools/grafana/bin/grafana server \
      --homepath=./.tools/grafana \
      --configOverrides="cfg:default.paths.data=$(pwd)/.runtime/grafana/data cfg:default.paths.logs=$(pwd)/.runtime/grafana/logs cfg:default.paths.plugins=$(pwd)/.runtime/grafana/plugins cfg:default.server.http_addr=127.0.0.1 cfg:default.server.http_port=3000 cfg:default.security.admin_user=admin cfg:default.security.admin_password=admin cfg:default.auth.anonymous.enabled=true cfg:default.auth.anonymous.org_role=Admin"
    ```
* **監聽端口總結**：
  * Flask 聊天應用：`http://127.0.0.1:5001`
  * Prometheus：`http://127.0.0.1:9090`
  * Grafana：`http://127.0.0.1:3000`

---

## 4. Grafana 儀表盤設計與 PromQL 查詢解析

儀表盤包含三個時間序列 Panel（導出於 [grafana-dashboard.json](file:///Users/apple/Desktop/北大/智能化軟件/isse-labs-hw/lab4/2601930020-hsushuoheng/grafana-dashboard.json)）：

1. **Panel 1：成功/失敗請求變化 (Req/s)**
   * **PromQL**：`sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))`
   * **含義**：在 30 秒滑動窗口內計算平均每秒完成的請求數（QPS 速率），分別繪製 `success`（成功）與 `error`（錯誤）兩條曲線。
2. **Panel 2：正在處理的請求數 (In-progress)**
   * **PromQL**：`sum(chat_inprogress_requests{job="chat-app"})`
   * **含義**：反映當前系統內部處於處理狀態的請求總數，體現瞬時並發負載。
3. **Panel 3：平均處理耗時 (Average Duration)**
   * **PromQL**：`sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s])) / sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))`
   * **含義**：利用 Histogram 總耗時速率與總請求數速率之比，計算最近窗口內服務端平均單次請求耗時（秒）。

---

## 5. 項目適配（project_adapter.py）

在 [project_adapter.py](file:///Users/apple/Desktop/北大/智能化軟件/isse-labs-hw/lab4/2601930020-hsushuoheng/project_adapter.py) 中補齊三個適配函數，將課程調度腳本與本項目對接：
* `confirm_mock_mode(base_url, timeout)`：向 `GET /api/status` 發起請求，確認 `mode == "mock"` 且 `external_model_calls == false`。
* `build_chat_request(base_url, message, delay_seconds, force_error)`：構造指向 `POST /api/conversations/1/messages` 的 HTTP Request，攜帶 JSON 正文與模擬控制參數。
* `response_is_success(status_code, body)`：檢查狀態碼為 HTTP 201 且包含合法的會話與回覆 JSON。

---

## 6. 流量模擬實驗與對比分析

### 6.1 首次完整模擬運行（first-run.json）
* **執行參數**：`--scenario all --phase-seconds 30 --concurrency 6 --base-url http://127.0.0.1:5001`
* **各階段真實數據**：
  * **`baseline`（14:45:17 ~ 14:45:47）**：排程 30 次，發送 30 次，成功 30 次，錯誤 0 次，跳過 0 次。平均客戶端耗時 0.11 秒。
  * **`burst`（14:45:47 ~ 14:46:17）**：排程 120 次，發送 120 次，成功 120 次，錯誤 0 次，跳過 0 次。Panel 1 成功請求速率顯著激增至約 4 req/s。
  * **`slow`（14:46:17 ~ 14:46:50）**：排程 60 次，發送 52 次，成功 52 次，因並發上限 6 導致**跳過 8 次**。平均耗時拉長至 3 秒以上，Panel 2 在途請求數達到 5～6 階梯頂峰。
  * **`errors`（14:46:50 ~ 14:47:20）**：排程 30 次，發送 30 次，成功 20 次，業務錯誤 10 次（每 3 次失敗 1 次），Panel 1 錯誤曲線升高。
  * **`recovery`（14:47:20 ~ 14:47:50）**：排程 30 次，發送 30 次，全數成功，系統各項指標回落至基準線。

### 6.2 第二次調整參數對比運行（changed-run.json）
* **調整策略**：學生選擇調整選項 C，將最大並發上限 `--concurrency` 從 6 提高至 **10**，場景為 `--scenario slow --phase-seconds 35`。
* **對比結果**：
  * 排程 70 次，發送 70 次，成功 70 次，錯誤 0 次，**跳過 0 次（第一次跳過 8 次）**。
  * 客戶端平均耗時為 3.06 秒。
* **結論分析**：將並發容量提升至 10 後，調度器線程池能容納更多並發在途請求，消除線程耗盡導致的跳過現象，後端多線程服務能夠穩定承載更高並發的慢請求。

---

## 7. 乾淨環境復現步驟

在未運行過監控工具的新環境中，可按以下步驟復現：

1. **安裝依賴與啟動應用**：
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python app.py
   ```
2. **啟動 Prometheus**：
   使用第 3 節中的命令啟動 Prometheus，打開 `http://127.0.0.1:9090/targets` 確認 `chat-app` 為 `UP`。
3. **啟動 Grafana 並導入儀表盤**：
   使用第 3 節中的命令啟動 Grafana，登入後進入 Dashboards -> New -> Import，上傳 [grafana-dashboard.json](file:///Users/apple/Desktop/北大/智能化軟件/isse-labs-hw/lab4/2601930020-hsushuoheng/grafana-dashboard.json)，數據源選擇本地 Prometheus。
4. **執行流量模擬**：
   ```bash
   python simulate_traffic.py --base-url http://127.0.0.1:5001 --output results/first-run.json
   ```
   觀察 Grafana 儀表盤各 Panel 的波動與回落。
