# LoveTypes Week 1 平台發布簡報

- 產生日期：2026-06-21
- 平台任務：3
- 腳本數：3
- 主 CTA：完成 15 題測驗，找到你的情感守護者

## 發布前規則

- 每支內容只放一個主 CTA，不在影片或說明欄直接導購。
- 優先使用追蹤連結；若平台限制連結，至少保留 `https://lovetypes.tw/start/`。
- 不使用診斷、療效、保證修復或必須購買的說法。

## 平台任務

### 2026-06-15 20:30 Asia/Taipei · YouTube Shorts

- 任務：`publish-lt-s01-iris-silence`
- 腳本：`lt-s01-iris-silence`
- 守護者：艾莉絲（`iris`）
- 內容角度：情感錯頻情境
- 標題：他沉默時，你最想聽見哪一句話？
- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence
- UTM content：`iris_silence`

```text
你不是想聽甜言蜜語，你只是想確認自己有沒有被看見。

Take the 15-question quiz to find your emotional guardian: https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence

留言 A/B/C，或寫下一句你最想被說出口的話。
#LoveLanguages #RelationshipQuiz #EmotionalGuardian #HeartLanguage #LoveTypes
```

回填欄位：`posting-queue.csv` 的 `status`、`published_date`、`post_url`；`platform-kpi-tracker.csv` 先填 `post_url`、`site_clicks`、`quiz_starts`、`quiz_completions`，有結果後互動時再填 `guardian_result_clicks`、`resources_clicks`、`repair_plan_clicks`、`luna_clicks`、`keepsake_clicks`、`free_keepsake_downloads`、`supply_lead_requests`、`luna_pack_clicks`、`affiliate_book_clicks`、`contact_requests`。

### 2026-06-17 20:30 Asia/Taipei · YouTube Shorts

- 任務：`publish-lt-s02-iris-affirmation`
- 腳本：`lt-s02-iris-affirmation`
- 守護者：艾莉絲（`iris`）
- 內容角度：守護者人格認同
- 標題：哪一句肯定，會讓你瞬間安心？
- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_affirmation
- UTM content：`iris_affirmation`

```text
真正的肯定，不是把你說得完美，而是讓你知道自己被看見。

Take the 15-question quiz to find your emotional guardian: https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_affirmation

留言你選的句子，艾莉絲會把它收進晨曦玻璃花園。
#LoveLanguages #RelationshipQuiz #EmotionalGuardian #HeartLanguage #LoveTypes
```

回填欄位：`posting-queue.csv` 的 `status`、`published_date`、`post_url`；`platform-kpi-tracker.csv` 先填 `post_url`、`site_clicks`、`quiz_starts`、`quiz_completions`，有結果後互動時再填 `guardian_result_clicks`、`resources_clicks`、`repair_plan_clicks`、`luna_clicks`、`keepsake_clicks`、`free_keepsake_downloads`、`supply_lead_requests`、`luna_pack_clicks`、`affiliate_book_clicks`、`contact_requests`。

### 2026-06-19 20:30 Asia/Taipei · YouTube Shorts

- 任務：`publish-lt-s03-iris-too-sensitive`
- 腳本：`lt-s03-iris-too-sensitive`
- 守護者：艾莉絲（`iris`）
- 內容角度：測驗入口
- 標題：你真的太敏感嗎？還是你只是等一句清楚的話？
- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_too_sensitive
- UTM content：`iris_too_sensitive`

```text
有時候你不是太敏感，你只是一直在替沉默找理由。

Take the 15-question quiz to find your emotional guardian: https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_too_sensitive

留言「我想被清楚回應」，或選 A：等話、B：等行動、C：等陪伴。
#LoveLanguages #RelationshipQuiz #EmotionalGuardian #HeartLanguage #LoveTypes
```

回填欄位：`posting-queue.csv` 的 `status`、`published_date`、`post_url`；`platform-kpi-tracker.csv` 先填 `post_url`、`site_clicks`、`quiz_starts`、`quiz_completions`，有結果後互動時再填 `guardian_result_clicks`、`resources_clicks`、`repair_plan_clicks`、`luna_clicks`、`keepsake_clicks`、`free_keepsake_downloads`、`supply_lead_requests`、`luna_pack_clicks`、`affiliate_book_clicks`、`contact_requests`。

## 發布後回填

- 發布後先在 posting-queue.csv 回填 status、published_date、post_url。
- 同一天或隔天先回填 platform-kpi-tracker.csv 的平台列最小 KPI：post_url, site_clicks, quiz_starts, quiz_completions。
- 一旦測驗結果頁、守護者路線、Luna、收藏物、補給或聯盟書卷有互動，接著回填下游欄位：guardian_result_clicks, resources_clicks, repair_plan_clicks, luna_clicks, keepsake_clicks, free_keepsake_downloads, supply_lead_requests, luna_pack_clicks, affiliate_book_clicks, contact_requests。
- 週回顧時再把 YouTube Shorts 成效彙總到 kpi-tracker.csv。
- 只有在 publishing-status.md 顯示可做週決策後，才放大守護者或商品承接方向。
