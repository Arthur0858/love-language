# LoveTypes First Batch Publication Packet

- 產生日期：2026-06-22
- week / slot：1 / 1
- rows：1
- published：0
- pending：1
- rows with minimum KPI：0
- ready_to_publish：1
- weekly_decision_ready：0
- issues：0

## Gate

- Publish the first Iris script on YouTube Shorts, then measure quiz starts and quiz completions before revenue decisions.
- If first batch has no post URLs or KPI rows, keep offer order, paid CTA, Luna emphasis, and affiliate emphasis unchanged.
- 不用本文件偽造 post URL、發布日期或 KPI；只有貼文公開後才回填。

## Minimum KPI

- `site_clicks`
- `quiz_starts`
- `quiz_completions`

## Follow-up KPI

- `guardian_result_clicks`
- `resources_clicks`
- `repair_plan_clicks`
- `luna_clicks`
- `keepsake_clicks`
- `free_keepsake_downloads`
- `supply_lead_requests`
- `luna_pack_clicks`
- `affiliate_book_clicks`
- `contact_requests`

## youtube_shorts · `publish-lt-s01-iris-silence`

- script：`lt-s01-iris-silence`
- guardian：艾莉絲（`iris`）
- title：他沉默時，你最想聽見哪一句話？
- status：`planned`
- schedule：2026-06-15 20:30 Asia/Taipei
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence
- post URL：(pending)
- post URL placeholder：`<REAL_YOUTUBE_SHORTS_URL>`

### Caption

```text
你不是想聽甜言蜜語，你只是想確認自己有沒有被看見。

Take the 15-question quiz to find your emotional guardian: https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence

留言 A/B/C，或寫下一句你最想被說出口的話。
#LoveLanguages #RelationshipQuiz #EmotionalGuardian #HeartLanguage #LoveTypes
```

### Pre-publish Checks

- Profile link 已完成 set/live，且 launch readiness ready_to_publish=1。
- 影片、字幕、首幀或封面使用正確守護者宇宙，不交換角色設定。
- Caption keeps one primary CTA: take the 15-question quiz and find your emotional guardian.
- Tracked URL 指向 /start/ 且保留 utm_content。
- 不加入 Luna、聯盟書卷或付費商品作為第一 CTA。

### Post-publish Checks

- 貼文公開 URL 是 https URL，且可以在無登入狀態開啟或至少可從平台公開頁驗證。
- 回填 published_date、post_url、proof_note。
- 有平台數據後才回填 site_clicks、quiz_starts、quiz_completions。
- 週回顧前確認 platform-kpi-tracker 與 kpi-tracker 已同步。

### Writeback

- 發布 URL 回填：`python3 tools/promotion_post_writeback.py update --platform youtube_shorts --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-22 --post-url <REAL_YOUTUBE_SHORTS_URL> --proof-note "<REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified"`
- 初始 KPI 回填：`python3 tools/promotion_post_writeback.py update --platform youtube_shorts --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-22 --post-url <REAL_YOUTUBE_SHORTS_URL> --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "<REAL_ANALYTICS_SOURCE_PROOF_NOTE> verified"`
