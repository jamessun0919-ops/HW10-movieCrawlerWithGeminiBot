# HW9 - 電影資訊爬蟲與 Chatbot

[![Demo](https://img.shields.io/badge/Demo-%F0%9F%8E%AC-%231a1a2e?style=for-the-badge)](https://htmlpreview.github.io/?https://github.com/jamessun0919-ops/HW9-MovieCrawler-Csv-localweb/blob/main/movies.html)

## 專案內容

- **crawler.py** — 爬取 [ssr1.scrape.center](https://ssr1.scrape.center) 共 100 部電影資料
- **movies.csv** — 電影資料表（編號、片名、評分、分類、地區、片長、上映日期、導演、演員）
- **movies.html** — 電影資訊網頁，含搜尋、篩選、排序、海報展示，以及 Gemini AI Chatbot
- **server.py** — 本地開發伺服器（含前端靜態檔案與 `/api/chat` 端點）
- **api/index.py** — Render 後端 API（Flask）
- **vercel.json** — Vercel 前端部署設定
- **render.yaml** — Render 後端部署設定

## 部署架構

```
┌──────────┐     POST /api/chat     ┌──────────┐     Gemini API
│  Vercel   │ ──────────────────→   │  Render   │ ──────────────→
│ (靜態前端) │ ←────────────────── │ (Flask API)│ ←──────────────
└──────────┘     JSON response      └──────────┘
```

- **前端**: Vercel — 靜態部署 `movies.html`（電影資料內嵌於 HTML）
- **後端**: Render — Python Flask 服務，接收前端請求、呼叫 Gemini API、回傳回應

## 本地開發

```bash
# 1. 安裝依賴
pip install requests beautifulsoup4 openpyxl pillow flask flask-cors gunicorn

# 2. 執行爬蟲
python crawler.py

# 3. 設定 API Key
#    編輯 .env 檔案：GEMINI_API_KEY=你的金鑰

# 4. 啟動本地伺服器（同時提供前端與 /api/chat 端點）
python server.py

# 5. 開啟瀏覽器
#    http://localhost:8000
```

## 部署步驟

### 前端 → Vercel

1. 將專案推送到 GitHub
2. 在 [Vercel](https://vercel.com) 匯入此 GitHub 專案
3. Vercel 會自動偵測 `vercel.json`，以靜態網站部署
4. 部署後取得前端網址（如 `https://hw9-movie-crawler.vercel.app`）

### 後端 → Render

1. 在 [Render](https://render.com) 建立新的 **Web Service**
2. 連結同一 GitHub 專案
3. 設定：
   - **Runtime**: Python
   - **Build Command**: `pip install -r api/requirements.txt`
   - **Start Command**: `gunicorn api.index:app --bind 0.0.0.0:$PORT`
4. 新增環境變數 `GEMINI_API_KEY`
5. 部署後取得後端網址（如 `https://hw9-movie-crawler-api.onrender.com`）

### 更新前端 API 位址

將 `movies.html` 中的 `API_BASE` 變數改為 Render 後端網址：

```js
const API_BASE = 'https://hw9-movie-crawler-api.onrender.com';
```

## Demo

點擊上方按鈕可檢視電影資訊表格（靜態頁面，Chatbot 需搭配後端才能運作）。
