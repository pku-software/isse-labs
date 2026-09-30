# Lab 3: 從程式碼到雲端——ACR 建置與 ECI 部署

- **學號**：2601930020
- **姓名**：HSUSHUOHENG (徐碩亨)
- **個人分支**：`lab3/2601930020-hsushuoheng`

---

## 專案概述與架構

本專案延續 Lab 2 的 Flask + DeepSeek 智慧對話應用，透過容器化技術（Docker）與阿里雲雲端原生服務（ACR + ECI）將其部署至公網環境。

### 系統架構
1. **前端 (Frontend)**：HTML / CSS / JavaScript 原生實現，提供簡潔現代的聊天 UI，支援 Markdown 渲染、代碼高亮、多會話切換與對話 CRUD。
2. **後端 (Backend)**：Flask 應用（`app.py`），提供靜態資源託管與 API 路由，透過 `requests` 調用 DeepSeek API。
3. **生產 WSGI 伺服器**：Gunicorn（`0.0.0.0:5001`），替代 Flask 內建開發伺服器，提供穩定可靠的 HTTP 服務。
4. **雲端建置 (ACR)**：透過阿里雲容器映像檔服務（ACR）個人版，綁定 GitHub 個人倉庫分支，直接在雲端自動建置 Docker 映像檔。
5. **彈性容器執行個體 (ECI)**：免去雲伺服器（ECS）底層維運，直接拉取 ACR 映像檔運行容器，並掛載彈性公網 IP (EIP) 提供公網存取。

---

## Dockerfile 關鍵配置

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 先複製依賴清單並安裝，利用 Docker 層級快取機制
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式程式碼及前端靜態資源
COPY . .

# 聲明容器服務預期監聽的連接埠
EXPOSE 5001

# 容器啟動時使用 Gunicorn 生產級 WSGI 伺服器
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "1", "app:app"]
```

- **安全防護**：`.dockerignore` 排除了 `.env`、`__pycache__`、`screenshots`、`data` 等敏感檔案與暫存資料，確保金鑰不被寫入 Docker 映像檔。

---

## ACR 映像檔建置資訊
- **地域**：華北 2 (北京)
- **程式碼源**：GitHub (`AvinHsu/isse-labs-hw`)
- **建置分支**：`lab3/2601930020-hsushuoheng`
- **建置上下文路徑**：`/lab3/2601930020-hsushuoheng/`
- **Dockerfile 路徑**：`Dockerfile`
- **映像檔標籤**：`lab3-f7e6edb`
- **建置狀態**：雲端建置成功 (海外機器建置)

---

## ECI 部署與驗證資訊
- **地域**：華北 2 (北京) 可用區 H
- **容器組 ID**：`eci-2ze60a1dh9hnd0j17xvp` (`container-group-1790740819631`)
- **容器組規格**：經濟型（0.25 vCPU, 512 MiB）
- **服務連接埠**：`5001`（安全組入方向放行自定義 TCP 5001）
- **環境變數名稱**：`DEEPSEEK_API_KEY`（在 ECI 控制台容器進階設定中手動注入，避免硬編碼）
- **公網 IP**：`47.93.19.198`
- **訪問測試結果**：
  - HTTP 狀態碼：`200 OK`（Gunicorn 正常回應靜態資源與 API）
  - API 端點測試：`/api/hello` 與 `/api/conversations` 均正常返回 JSON
  - 瀏覽器對話測試：成功在公網網頁發送問題並即時取得 DeepSeek 回覆（見 `screenshots/public-page.png`）

---

## 安全說明與風險防範
1. **HTTP 明文傳輸**：目前採用短時公網 HTTP 演示，未啟用 TLS 加密，不建議傳輸敏感個人機密。
2. **API 無鑑權風險**：當前後端 API 無使用者認證機制，任何存取該公網 IP 的請求皆會調用後端並消耗帳號內的 DeepSeek Token 額度。
3. **清理計畫**：實驗驗證完畢並發起 PR 後，務必於阿里雲控制台立即刪除該 ECI 容器組實例與解綁釋放 EIP，避免產生額外按量計費。
