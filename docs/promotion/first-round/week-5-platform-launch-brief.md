# LoveTypes Week 5 平台發布簡報

- 產生日期：2026-06-23
- 平台任務：3
- 腳本數：3
- 主 CTA：完成 15 題測驗，找到你的情感守護者

## 發布前規則

- 每支內容只放一個主 CTA，不在影片或說明欄直接導購。
- 優先使用追蹤連結；若平台限制連結，至少保留 `https://lovetypes.tw/start/`。
- 不使用診斷、療效、保證修復或必須購買的說法。

## 平台任務

### 2026-07-13 20:30 Asia/Taipei · YouTube Shorts

- 任務：`publish-lt-s13-dora-distance`
- 腳本：`lt-s13-dora-distance`
- 守護者：朵拉（`dora`）
- 內容角度：情感錯頻情境
- 標題：你不是太黏，你只是用身體最先感覺到距離
- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=dora_distance
- UTM content：`dora_distance`

```text
有些不安不是想太多，是身體先發現對方退後了。

Take the 15-question quiz to find your emotional guardian: https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=dora_distance

留言 A/B/C，哪一種靠近最能讓你安心？
#LoveLanguages #RelationshipQuiz #EmotionalGuardian #HeartLanguage #LoveTypes
```

回填欄位：`posting-queue.csv` 的 `status`、`published_date`、`post_url`；`platform-kpi-tracker.csv` 先填 `post_url`、`site_clicks`、`quiz_starts`、`quiz_completions`，有結果後互動時再填 `guardian_result_clicks`、`resources_clicks`、`repair_plan_clicks`、`luna_clicks`、`keepsake_clicks`、`free_keepsake_downloads`、`supply_lead_requests`、`luna_pack_clicks`、`affiliate_book_clicks`、`contact_requests`。

### 2026-07-15 20:30 Asia/Taipei · YouTube Shorts

- 任務：`publish-lt-s14-dora-consent`
- 腳本：`lt-s14-dora-consent`
- 守護者：朵拉（`dora`）
- 內容角度：守護者人格認同
- 標題：真正溫柔的靠近，會先問你願不願意
- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=dora_consent
- UTM content：`dora_consent`

```text
身體接觸的愛，不是要求對方配合，而是讓彼此都安心。

Take the 15-question quiz to find your emotional guardian: https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=dora_consent

留言 A/B/C，你最想聽見哪一句安全靠近？
#LoveLanguages #RelationshipQuiz #EmotionalGuardian #HeartLanguage #LoveTypes
```

回填欄位：`posting-queue.csv` 的 `status`、`published_date`、`post_url`；`platform-kpi-tracker.csv` 先填 `post_url`、`site_clicks`、`quiz_starts`、`quiz_completions`，有結果後互動時再填 `guardian_result_clicks`、`resources_clicks`、`repair_plan_clicks`、`luna_clicks`、`keepsake_clicks`、`free_keepsake_downloads`、`supply_lead_requests`、`luna_pack_clicks`、`affiliate_book_clicks`、`contact_requests`。

### 2026-07-17 20:30 Asia/Taipei · YouTube Shorts

- 任務：`publish-lt-s15-dora-after-conflict`
- 腳本：`lt-s15-dora-after-conflict`
- 守護者：朵拉（`dora`）
- 內容角度：測驗入口
- 標題：吵架後，你需要多久才能重新靠近？
- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=dora_after_conflict
- UTM content：`dora_after_conflict`

```text
有些人不是不想和好，而是身體還沒感覺安全。

Take the 15-question quiz to find your emotional guardian: https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=dora_after_conflict

留言 A/B/C，吵架後你是哪一種靠近節奏？
#LoveLanguages #RelationshipQuiz #EmotionalGuardian #HeartLanguage #LoveTypes
```

回填欄位：`posting-queue.csv` 的 `status`、`published_date`、`post_url`；`platform-kpi-tracker.csv` 先填 `post_url`、`site_clicks`、`quiz_starts`、`quiz_completions`，有結果後互動時再填 `guardian_result_clicks`、`resources_clicks`、`repair_plan_clicks`、`luna_clicks`、`keepsake_clicks`、`free_keepsake_downloads`、`supply_lead_requests`、`luna_pack_clicks`、`affiliate_book_clicks`、`contact_requests`。

## 發布後回填

- 發布後先在 posting-queue.csv 回填 status、published_date、post_url。
- 同一天或隔天先回填 platform-kpi-tracker.csv 的平台列最小 KPI：post_url, site_clicks, quiz_starts, quiz_completions。
- 一旦測驗結果頁、守護者路線、Luna、收藏物、補給或聯盟書卷有互動，接著回填下游欄位：guardian_result_clicks, resources_clicks, repair_plan_clicks, luna_clicks, keepsake_clicks, free_keepsake_downloads, supply_lead_requests, luna_pack_clicks, affiliate_book_clicks, contact_requests。
- 週回顧時再把 YouTube Shorts 成效彙總到 kpi-tracker.csv。
- 只有在 publishing-status.md 顯示可做週決策後，才放大守護者或商品承接方向。
