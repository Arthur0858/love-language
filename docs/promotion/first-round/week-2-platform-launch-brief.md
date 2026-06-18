# LoveTypes Week 2 平台發布簡報

- 產生日期：2026-06-18
- 平台任務：3
- 腳本數：3
- 主 CTA：完成 15 題測驗，找到你的情感守護者

## 發布前規則

- 每支內容只放一個主 CTA，不在影片或說明欄直接導購。
- 優先使用追蹤連結；若平台限制連結，至少保留 `https://lovetypes.tw/start/`。
- 不使用診斷、療效、保證修復或必須購買的說法。

## 平台任務

### 2026-06-22 20:30 Asia/Taipei · YouTube Shorts

- 任務：`publish-lt-s04-noah-phone`
- 腳本：`lt-s04-noah-phone`
- 守護者：諾雅（`noah`）
- 內容角度：情感錯頻情境
- 標題：約會時他一直看手機，你真正難過的是什麼？
- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=noah_phone
- UTM content：`noah_phone`

```text
你不是要他每分每秒陪你，你只是希望他在的時候真的在。

Take the 15-question quiz to find your emotional guardian: https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=noah_phone

留言 A/B/C，你最不能接受哪一種不在場？
#LoveLanguages #RelationshipQuiz #EmotionalGuardian #HeartLanguage #LoveTypes
```

回填欄位：`posting-queue.csv` 的 `status`、`published_date`、`post_url`；`platform-kpi-tracker.csv` 先填 `post_url`、`site_clicks`、`quiz_starts`、`quiz_completions`，有結果後互動時再填 `guardian_result_clicks`、`resources_clicks`、`repair_plan_clicks`、`luna_clicks`、`keepsake_clicks`、`free_keepsake_downloads`、`supply_lead_requests`、`luna_pack_clicks`、`affiliate_book_clicks`、`contact_requests`。

### 2026-06-24 20:30 Asia/Taipei · YouTube Shorts

- 任務：`publish-lt-s05-noah-cancel`
- 腳本：`lt-s05-noah-cancel`
- 守護者：諾雅（`noah`）
- 內容角度：守護者人格認同
- 標題：約定一再被取消，你會怎麼保護自己？
- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=noah_cancel
- UTM content：`noah_cancel`

```text
每一次被延後，都像星海裡少了一盞燈。

Take the 15-question quiz to find your emotional guardian: https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=noah_cancel

留言 A/B/C，諾雅會替你留下一盞還沒熄掉的燈。
#LoveLanguages #RelationshipQuiz #EmotionalGuardian #HeartLanguage #LoveTypes
```

回填欄位：`posting-queue.csv` 的 `status`、`published_date`、`post_url`；`platform-kpi-tracker.csv` 先填 `post_url`、`site_clicks`、`quiz_starts`、`quiz_completions`，有結果後互動時再填 `guardian_result_clicks`、`resources_clicks`、`repair_plan_clicks`、`luna_clicks`、`keepsake_clicks`、`free_keepsake_downloads`、`supply_lead_requests`、`luna_pack_clicks`、`affiliate_book_clicks`、`contact_requests`。

### 2026-06-26 20:30 Asia/Taipei · YouTube Shorts

- 任務：`publish-lt-s06-noah-quiet-time`
- 腳本：`lt-s06-noah-quiet-time`
- 守護者：諾雅（`noah`）
- 內容角度：測驗入口
- 標題：你最想被怎樣陪伴？
- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=noah_quiet_time
- UTM content：`noah_quiet_time`

```text
有些人要的不是熱鬧，而是一段不被打斷的在場。

Take the 15-question quiz to find your emotional guardian: https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=noah_quiet_time

留言你的選項，或寫下你最想被陪伴的 15 分鐘。
#LoveLanguages #RelationshipQuiz #EmotionalGuardian #HeartLanguage #LoveTypes
```

回填欄位：`posting-queue.csv` 的 `status`、`published_date`、`post_url`；`platform-kpi-tracker.csv` 先填 `post_url`、`site_clicks`、`quiz_starts`、`quiz_completions`，有結果後互動時再填 `guardian_result_clicks`、`resources_clicks`、`repair_plan_clicks`、`luna_clicks`、`keepsake_clicks`、`free_keepsake_downloads`、`supply_lead_requests`、`luna_pack_clicks`、`affiliate_book_clicks`、`contact_requests`。

## 發布後回填

- 發布後先在 posting-queue.csv 回填 status、published_date、post_url。
- 同一天或隔天先回填 platform-kpi-tracker.csv 的平台列最小 KPI：post_url, site_clicks, quiz_starts, quiz_completions。
- 一旦測驗結果頁、守護者路線、Luna、收藏物、補給或聯盟書卷有互動，接著回填下游欄位：guardian_result_clicks, resources_clicks, repair_plan_clicks, luna_clicks, keepsake_clicks, free_keepsake_downloads, supply_lead_requests, luna_pack_clicks, affiliate_book_clicks, contact_requests。
- 週回顧時再把 YouTube Shorts 成效彙總到 kpi-tracker.csv。
- 只有在 publishing-status.md 顯示可做週決策後，才放大守護者或商品承接方向。
