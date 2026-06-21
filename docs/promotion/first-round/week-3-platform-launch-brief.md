# LoveTypes Week 3 平台發布簡報

- 產生日期：2026-06-22
- 平台任務：3
- 腳本數：3
- 主 CTA：完成 15 題測驗，找到你的情感守護者

## 發布前規則

- 每支內容只放一個主 CTA，不在影片或說明欄直接導購。
- 優先使用追蹤連結；若平台限制連結，至少保留 `https://lovetypes.tw/start/`。
- 不使用診斷、療效、保證修復或必須購買的說法。

## 平台任務

### 2026-06-29 20:30 Asia/Taipei · YouTube Shorts

- 任務：`publish-lt-s07-vivian-remembered`
- 腳本：`lt-s07-vivian-remembered`
- 守護者：薇薇安（`vivian`）
- 內容角度：情感錯頻情境
- 標題：你在乎的真的是禮物嗎？
- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=vivian_remembered
- UTM content：`vivian_remembered`

```text
你不是物質，你只是想知道自己有沒有被放在心上。

Take the 15-question quiz to find your emotional guardian: https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=vivian_remembered

留言 A/B/C，哪一種小心意最能打動你？
#LoveLanguages #RelationshipQuiz #EmotionalGuardian #HeartLanguage #LoveTypes
```

回填欄位：`posting-queue.csv` 的 `status`、`published_date`、`post_url`；`platform-kpi-tracker.csv` 先填 `post_url`、`site_clicks`、`quiz_starts`、`quiz_completions`，有結果後互動時再填 `guardian_result_clicks`、`resources_clicks`、`repair_plan_clicks`、`luna_clicks`、`keepsake_clicks`、`free_keepsake_downloads`、`supply_lead_requests`、`luna_pack_clicks`、`affiliate_book_clicks`、`contact_requests`。

### 2026-07-01 20:30 Asia/Taipei · YouTube Shorts

- 任務：`publish-lt-s08-vivian-forgotten-date`
- 腳本：`lt-s08-vivian-forgotten-date`
- 守護者：薇薇安（`vivian`）
- 內容角度：守護者人格認同
- 標題：重要日子被忘記，你最痛的是哪裡？
- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=vivian_forgotten_date
- UTM content：`vivian_forgotten_date`

```text
那一天不是日期而已，是你想確認自己有沒有被記得。

Take the 15-question quiz to find your emotional guardian: https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=vivian_forgotten_date

留言 A/B/C，或寫下一個你希望被記得的日子。
#LoveLanguages #RelationshipQuiz #EmotionalGuardian #HeartLanguage #LoveTypes
```

回填欄位：`posting-queue.csv` 的 `status`、`published_date`、`post_url`；`platform-kpi-tracker.csv` 先填 `post_url`、`site_clicks`、`quiz_starts`、`quiz_completions`，有結果後互動時再填 `guardian_result_clicks`、`resources_clicks`、`repair_plan_clicks`、`luna_clicks`、`keepsake_clicks`、`free_keepsake_downloads`、`supply_lead_requests`、`luna_pack_clicks`、`affiliate_book_clicks`、`contact_requests`。

### 2026-07-03 20:30 Asia/Taipei · YouTube Shorts

- 任務：`publish-lt-s09-vivian-ritual`
- 腳本：`lt-s09-vivian-ritual`
- 守護者：薇薇安（`vivian`）
- 內容角度：測驗入口
- 標題：你的戀愛儀式感是哪一種？
- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=vivian_ritual
- UTM content：`vivian_ritual`

```text
有些人把愛藏在細節裡，等你發現自己被記得。

Take the 15-question quiz to find your emotional guardian: https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=vivian_ritual

留言 A/B/C，薇薇安會替你把那份心意歸檔。
#LoveLanguages #RelationshipQuiz #EmotionalGuardian #HeartLanguage #LoveTypes
```

回填欄位：`posting-queue.csv` 的 `status`、`published_date`、`post_url`；`platform-kpi-tracker.csv` 先填 `post_url`、`site_clicks`、`quiz_starts`、`quiz_completions`，有結果後互動時再填 `guardian_result_clicks`、`resources_clicks`、`repair_plan_clicks`、`luna_clicks`、`keepsake_clicks`、`free_keepsake_downloads`、`supply_lead_requests`、`luna_pack_clicks`、`affiliate_book_clicks`、`contact_requests`。

## 發布後回填

- 發布後先在 posting-queue.csv 回填 status、published_date、post_url。
- 同一天或隔天先回填 platform-kpi-tracker.csv 的平台列最小 KPI：post_url, site_clicks, quiz_starts, quiz_completions。
- 一旦測驗結果頁、守護者路線、Luna、收藏物、補給或聯盟書卷有互動，接著回填下游欄位：guardian_result_clicks, resources_clicks, repair_plan_clicks, luna_clicks, keepsake_clicks, free_keepsake_downloads, supply_lead_requests, luna_pack_clicks, affiliate_book_clicks, contact_requests。
- 週回顧時再把 YouTube Shorts 成效彙總到 kpi-tracker.csv。
- 只有在 publishing-status.md 顯示可做週決策後，才放大守護者或商品承接方向。
