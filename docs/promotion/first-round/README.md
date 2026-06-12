# LoveTypes 第一輪推廣啟動包

## 目標

第一輪推廣只追一個主目標：提高「完成 15 題測驗，找到你的情感守護者」的完成量。短影片、SEO/GEO 文案與社群貼文都先導向首頁測驗，不直接導購。

## 檔案

- `shorts-scripts.zh-TW.json`: 15 支 Shorts 腳本，每位守護者 3 支，欄位符合 shorts-factory 腳本自動化契約。
- `publishing-calendar.csv`: 5 週發布節奏，每週 3 支 Shorts，依 Iris、Noah、Vivian、Claire、Dora 排列。
- `kpi-tracker.csv`: 發布後追蹤表，已預填 15 支 Shorts 的任務、守護者、UTM 與追蹤連結；發布後只需補平台、貼文 URL 與成效欄位。
- `posting-queue.csv`: 三平台發布佇列，將 15 支 Shorts 展開為 YouTube Shorts、TikTok、Instagram Reels 共 45 個發布任務，預設排在台北時間每週一/三/五晚間。
- `publishing-status.md`: 發布狀態對帳報告，檢查 45 筆發文任務是否已回填貼文 URL、發布日期，並確認 KPI 表是否足以做週決策。
- `publishing-status.json`: 同一份發布狀態的機器可讀版本，可交給表格、儀表板或自動化使用。
- `platform-launch-brief-index.md`: 5 週平台發布簡報索引，確認 45 筆平台任務、15 支腳本與每週守護者分布。
- `platform-launch-brief-index.json`: 同一份平台發布索引的機器可讀版本。
- `week-1-platform-launch-brief.md` 到 `week-5-platform-launch-brief.md`: 每週 9 筆平台發布任務的操作簡報，含排程時間、平台文案、追蹤連結與回填欄位。
- `week-1-platform-launch-brief.json` 到 `week-5-platform-launch-brief.json`: 每週平台發布簡報的機器可讀版本。
- `revenue-decision-matrix.md`: 五守護者獲利決策矩陣，把回填數據轉成免費收藏物、自有名單、Luna、聯盟書卷或內容放大的下一步。
- `revenue-decision-matrix.json`: 同一份決策矩陣的機器可讀版本。
- `asset-build-backlog.md`: 五守護者可製作資產 backlog，列出故事卡、PDF、桌布、Email、短儀式、Luna、聯盟書卷與短片變體。
- `asset-build-backlog.json`: 同一份資產 backlog 的機器可讀版本。
- `platform-profile-setup.md`: 三平台首頁設定檢查包，整理 YouTube Shorts、TikTok、Instagram Reels 的 Bio、個人頁連結、置頂留言、KPI 回填欄位與商業邊界。
- `platform-profile-setup.json`: 同一份平台首頁設定的機器可讀版本，可交給發布排程、表格或手動檢查使用。
- `platform-profile-tracker.csv`: 三平台 Bio/Profile link 的 KPI 追蹤表，專門回填個人頁連結帶來的點擊、測驗開始、測驗完成與收益意圖。
- `platform-profile-tracker.md/json`: 同一份平台首頁 KPI 追蹤表的人讀版與機器可讀版本。
- `execution-sheet-index.md`: 5 週推廣執行單索引，把平台首頁 gate、平台發布任務、回填順序與安全邊界集中管理。
- `execution-sheet-index.json`: 同一份執行單索引的機器可讀版本。
- `week-1-execution-sheet.md` 到 `week-5-execution-sheet.md`: 每週推廣執行單，整合三平台 Bio/Profile gate、9 筆平台發布任務、caption、追蹤連結與回填欄位。
- `week-1-execution-sheet.json` 到 `week-5-execution-sheet.json`: 每週推廣執行單的機器可讀版本。
- `now-asset-production-pack.md`: 目前 `priority=now` 的製作包，將五位守護者短影片痛點變體整理成可直接製作的腳本。
- `now-asset-production-pack.json`: 同一份 now 製作包的機器可讀版本，欄位符合 LoveTypes guardian script library。
- `now-asset-production-queue.csv`: 5 支 now 短片的製作追蹤表，拆成腳本審核、素材、剪輯、字幕、安全 QA、排程與 KPI 回填。
- `now-asset-production-queue.md/json`: 同一份製作佇列的人讀版與機器可讀版。
- `now-asset-production-briefs.md`: 5 支 now 短片的剪輯與發布手卡，包含 9:16 場景卡、字幕分段、平台 caption、hashtag、CTA 與安全檢查。
- `now-asset-production-briefs.json`: 同一份製作手卡的機器可讀版本，可交給剪輯、自動化或發布排程使用。
- `lovetypes-first-round-kpi-workbook.xlsx`: 可匯入 Google Sheets 的 KPI 工作簿，包含 Dashboard、KPI Tracker、Platform Profiles、Week 1 Execution、Next Actions 與 Data Dictionary。
- `publish-pack-index.md`: 使用 `python3 tools/promotion_publish_pack.py --all` 產生的第一輪發布包索引。
- `week-1-publish-pack.md` 到 `week-5-publish-pack.md`: 每週 3 支 Shorts 的發布包，包含說明欄文案、追蹤連結、字幕節奏、視覺提示與 KPI 回填起點。
- `weekly-summary.md`: 使用 `python3 tools/promotion_weekly_summary.py` 產生的週檢查摘要，會指出應放大的守護者、內容角度與下一個獲利承接動作。
- `weekly-summary.json`: 同一份週摘要的機器可讀版本，可交給自動化、表格或儀表板使用。
- `week-decision-gate.md`: 每週 go/no-go 決策 gate，集中判斷是否可做週決策、內容放大、免費收藏深化、自有名單資產或 Luna/聯盟柔性測試。
- `week-decision-gate.json`: 同一份週決策 gate 的機器可讀版本，空資料時會 fail-closed。
- `lead-intake-playbook.md`: 名單承接與履約 playbook，說明 Contact、收藏室等待清單、補給願望與 Luna 需求如何回填、排序與安全回覆。
- `lead-intake-playbook.json`: 同一份名單承接 playbook 的機器可讀版本。
- `lead-intake-tracker.csv`: 真實需求發生後使用的回填模板；預設列都是 `template`，不代表已有使用者名單。
- `offer-hypothesis-board.md`: 五守護者商品假設板，把免費收藏物、自有名單、Luna 與聯盟書卷拆成 PASS/HOLD 的測試假設。
- `offer-hypothesis-board.json/csv`: 同一份商品假設板的機器可讀與表格版本，可匯入 KPI 工作簿。
- `offer-experiment-plan.md`: 商品實驗計畫，為免費收藏、自有名單、Luna 與聯盟書卷設定可進入 READY 的 KPI 門檻。
- `offer-experiment-plan.json/csv`: 同一份商品實驗計畫的機器可讀與表格版本。
- `offer-experiment-queue.md`: 商品實驗執行佇列，把 READY 實驗拆成 brief、asset、QA、measure 四個步驟；未達門檻時維持 blocked。
- `offer-experiment-queue.json/csv`: 同一份商品實驗佇列的機器可讀與表格版本。
- `next-actions.md`: 使用 `python3 tools/promotion_next_actions.py` 產生的下一批發布與獲利承接建議。
- `next-actions.json`: 同一份下一步建議的機器可讀版本。

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
- 發布第一支影片前，先依 `platform-profile-setup.md` 完成三平台 Bio、個人頁連結與置頂留言設定。
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

## 產生週摘要

發布前先產生完整第一輪 5 週發布包：

```bash
python3 tools/promotion_sync_kpi_tracker.py
python3 tools/promotion_sync_posting_queue.py
python3 tools/promotion_publishing_status.py
python3 tools/promotion_launch_brief.py --all
python3 tools/promotion_revenue_decision_matrix.py
python3 tools/promotion_asset_backlog.py
python3 tools/promotion_platform_profile_setup.py
python3 tools/promotion_platform_profile_tracker.py
python3 tools/promotion_week_execution_sheet.py --all
python3 tools/promotion_now_asset_pack.py
python3 tools/promotion_now_asset_queue.py
python3 tools/promotion_now_asset_briefs.py
python3 tools/promotion_publish_pack.py --all
node tools/build_promotion_spreadsheet.mjs
```

若要指定第一週週一日期，可使用：

```bash
python3 tools/promotion_sync_posting_queue.py --start-date 2026-06-15
```

發布後先在 `posting-queue.csv` 回填各平台 `post_url`、`published_date`、`status`，再回填 `kpi-tracker.csv` 的 `date`、`platform`、`post_url` 與成效欄位。每週做判讀前先執行：

```bash
python3 tools/promotion_publishing_status.py
```

若 `publishing-status.md` 顯示「是否可做週決策：尚不可」，先補貼文 URL、發布日期或 KPI 回填，不要急著判斷優勝守護者或商品方向。資料足夠後再執行：

```bash
python3 tools/promotion_revenue_decision_matrix.py
python3 tools/promotion_asset_backlog.py
python3 tools/promotion_platform_profile_setup.py
python3 tools/promotion_platform_profile_tracker.py
python3 tools/promotion_week_execution_sheet.py --all
python3 tools/promotion_now_asset_pack.py
python3 tools/promotion_now_asset_queue.py
python3 tools/promotion_now_asset_briefs.py
python3 tools/promotion_weekly_summary.py
python3 tools/promotion_week_decision_gate.py
python3 tools/promotion_lead_intake_playbook.py
python3 tools/promotion_offer_hypothesis_board.py
python3 tools/promotion_offer_experiment_plan.py
python3 tools/promotion_offer_experiment_queue.py
node tools/build_promotion_spreadsheet.mjs
```

`revenue-decision-matrix.md` 會把每位守護者分成五種階段：先收集訊號、放大內容變體、深化免費收藏物、建立自有名單資產、測試柔性商品承接。空資料時它會維持安全模式，不會建議調整商品或付費 CTA。

`week-decision-gate.md` 是週判讀前的最後一道閘門。它會把發布狀態、週摘要、獲利矩陣與 next actions 合併成 PASS/HOLD，只有發布與 KPI 回填足夠時才允許放大內容、補自有名單或測試 Luna/聯盟承接。

`lead-intake-playbook.md` 是有人寄信、索取收藏物、提出補給願望或詢問 Luna 後的承接規則。它不預設已有名單；只有真實需求發生時才把 `lead-intake-tracker.csv` 的模板列複製成真實列，並回填來源、守護者、需求類型、回覆狀態與履約資產。這讓「免費收藏物 → Email 需求 → 自有素材或柔性商品」的路徑可追蹤，而不需要一開始就上付款系統。

`offer-hypothesis-board.md` 是商品化前的假設板。它把每位守護者目前可測的免費資產、自有名單資產、Luna 測試與聯盟書卷列成 PASS/HOLD；只要週 Gate 還有阻擋條件，商品假設就維持 HOLD，不改公開付費 CTA 或商品排序。

`offer-experiment-plan.md` 是把假設推進成實驗的門檻表。每位守護者有四種實驗：免費保存、自有名單、Luna 柔性商品、聯盟書卷；只有測驗完成與對應意圖指標達標，實驗才會 READY。未達 READY 前，不製作或加重付費 CTA。

`offer-experiment-queue.md` 是達標後才執行的工作佇列。每個 READY 實驗會拆成 brief、asset、QA、measure；若週 Gate 還有阻擋條件，所有佇列列都保持 `blocked_by_gate`，不製作公開商品素材。

`asset-build-backlog.md` 則把上述階段拆成具體製作任務。每位守護者都有故事卡、PDF 練習卡、手機桌布、Email 名單模板、短儀式、Luna 場景、聯盟書卷與內容變體；只有符合目前階段的項目會標成 `now`。

`platform-profile-setup.md` 是發布前的承接檢查包。三平台各自有專屬 profile link UTM、Bio、置頂留言與 KPI 欄位，避免 Shorts caption 說「個人頁連結」但平台首頁沒有一致入口。

`platform-profile-tracker.csv` 則是 Bio/Profile link 的回填表。單支影片成效仍放在 `kpi-tracker.csv`，平台首頁承接成效放在此表，避免把 caption 連結與個人頁連結混在一起判斷。

`week-N-execution-sheet.md` 是每週真正執行時打開的單一檢查表。它把平台首頁 gate、該週 9 筆平台發布任務、caption、追蹤連結、回填欄位和安全邊界放在同一份文件，避免發布時在多份文件之間人工拼接。

`now-asset-production-pack.md` 只抽出當前 `priority=now` 的任務，整理成可直接製作的短影片腳本、字幕、畫面建議與留言引導。若 tracker 尚未回填，它會先提供每位守護者一支痛點變體，不提前製作付費商品。

`now-asset-production-queue.csv` 則把這 5 支短片拆成 40 個製作步驟，方便標記 `planned`、`in_progress`、`done` 或 `blocked`，並保留建議輸出檔名與 KPI 回填提醒。

`now-asset-production-briefs.md` 把同一批 5 支短片整理成可交給剪輯者的製作手卡：每支都有 9:16 場景卡、字幕分段、畫面字、三平台 caption、hashtag、安全檢查與回填提醒。

需要只檢查不寫檔時執行：

```bash
python3 tools/promotion_weekly_summary.py --check
```

若追蹤表尚未有資料，摘要會保持保守，只提示先發布與回填，不會誤判優勝守護者或商品方向。

## 平台發布

先打開 `platform-launch-brief-index.md`，再依週次打開 `week-N-platform-launch-brief.md`。每週有 3 支腳本、9 筆平台任務，直接依簡報發布到 YouTube Shorts、TikTok、Instagram Reels。每支發布後先回填：

- `posting-queue.csv`: `status`、`published_date`、`post_url`
- `kpi-tracker.csv`: `platform`、`post_url`、`site_clicks`、`quiz_starts`、`quiz_completions`
- `platform-profile-tracker.csv`: 若流量來自 Bio/Profile link，回填 `profile_clicks`、`site_clicks`、`quiz_starts`、`quiz_completions`

若要重新產生全部週次的平台簡報：

```bash
python3 tools/promotion_launch_brief.py --all
```

若只要重建指定週次：

```bash
python3 tools/promotion_launch_brief.py --week 1
```

產生下一批內容與承接建議：

```bash
python3 tools/promotion_next_actions.py
```

若追蹤表尚未有資料，`next-actions` 會進入空資料安全模式，只建議先發布與回填，不調整商品或付費承接。
