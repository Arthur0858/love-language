# LoveTypes 第一輪推廣啟動包

## 目標

第一輪推廣只追一個主目標：提高「完成 15 題測驗，找到你的情感守護者」的完成量。短影片、SEO/GEO 文案與社群貼文都先導向首頁測驗，不直接導購。

## 檔案

- `shorts-scripts.zh-TW.json`: 15 支 Shorts 腳本，每位守護者 3 支，欄位符合 shorts-factory 腳本自動化契約。
- `publishing-calendar.csv`: 5 週發布節奏，每週 3 支 Shorts，依 Iris、Noah、Vivian、Claire、Dora 排列。
- `kpi-tracker.csv`: 發布後追蹤表，記錄觀看、互動、網站點擊、測驗開始與完成，並回填收藏物、補給名單、Luna、聯盟書卷與 Contact 需求。

## 推廣語彙

固定使用這些詞，避免文案分散：

- 五種愛之語測驗
- 情感守護者
- 心語庭園
- 錯頻修復
- 旅人補給
- 完成 15 題測驗，找到你的情感守護者

## 發布規則

- 每支 Shorts 只保留一個 CTA：完成 15 題測驗，找到你的情感守護者。
- 不把測驗結果寫成診斷，不承諾療效，不用恐嚇式情緒操控。
- 第一輪不主推聯盟書卷或 Luna 購買；測驗完成後再由網站承接旅人補給、修復計畫、Luna、收藏室。
- Shorts 說明欄建議連結：優先使用 `publishing-calendar.csv` 的 `tracked_url`。
- 若平台不允許長連結，退回 `https://lovetypes.tw/start/`，並在平台後台用 `utm_campaign=first_round_quiz_completion`、`utm_content` 對應 `publishing-calendar.csv`。

## 每週檢查

- 首頁測驗入口可正常開啟。
- 完成測驗後可看到守護者結果。
- `https://lovetypes.tw/ai-discovery.json`、`https://lovetypes.tw/llms.txt`、`https://lovetypes.tw/sitemap.xml` 可公開存取。
- Shorts 連結導向 `/start/` 測驗入口，不導向過多分散頁面。

## 成功門檻

第一輪結束後先看方向，不急著判斷營收：

- 哪位守護者的觀看與留言最高。
- 哪種角度最能帶來測驗開始：錯頻情境、守護者認同、測驗入口。
- 哪些 Shorts 帶來最多測驗完成。
- 測驗結果後，使用者是否自然點向守護者頁、旅人補給、修復計畫、Luna 或收藏室。
- 哪些守護者開始出現可變現意圖：免費收藏物下載、補給名單需求、Luna 商品點擊、聯盟書卷點擊或 Contact 需求。

## 獲利意圖欄位

- `free_keepsake_downloads`: 免費守護者收藏物下載或列印，代表角色認同與保存意願。
- `supply_lead_requests`: 補給願望清單、補給資產或 Email 需求，代表可建立自有名單。
- `luna_pack_clicks`: Luna Gumroad 商品包點擊，代表夜間補給付費意圖。
- `affiliate_book_clicks`: 聯盟書卷點擊，代表延伸閱讀購買意圖。
- `contact_requests`: 使用 Contact 或帶有路徑摘要的 mailto，代表高意圖需求。

每週檢查時先看 `quiz_completions`，再看上述五個欄位。若某位守護者連續兩週有補給名單或 Luna 商品點擊，下一週優先補該守護者的收藏物、短儀式或 Luna 入口內容。
