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

## ACR 映像檔建置資訊 (待任務 2 填入)
- **地域**：華北 2 (北京)
- **命名空間**：`AvinHsu`
- **倉庫名稱**：`isse-labs`
- **建置分支**：`lab3/2601930020-hsushuoheng`
- **建置上下文路徑**：`/lab3/2601930020-hsushuoheng/`
- **Dockerfile 路徑**：`Dockerfile`
- **映像檔標籤**：待定

---

## ECI 部署與驗證資訊 (待任務 3 填入)
- **地域**：華北 2 (北京)
- **容器規格**：經濟型 (0.25 vCPU, 0.5 GiB / 1 GiB)
- **公網 IP**：待部署後取得
- **訪問測試結果**：待測試
- **安全說明**：公網 HTTP 短時展示，API 無鑑權，測試完畢後立即刪除釋放實例以避免額外扣費。
