# LoveTypes Week 1 Publication Runbook

- 產生日期：2026-06-21
- tasks：3
- scripts：3
- platforms：1
- ready_to_publish：1
- issues：0

## Rules

- 先完成 YouTube profile gate，再發布 Week 任務。
- 每則貼文只導向 15 題測驗，不把 caption 變成導購。
- `<REAL_...>` 必須替換成公開平台上的真實 https post URL；沒有真實 URL 時，匯入檢查應拒絕。
- 0 KPI 只能在平台或網站來源檢查後回填，不用空資料做商品判斷。

## KPI Fields

Minimum:
- `post_url`
- `site_clicks`
- `quiz_starts`
- `quiz_completions`

Follow-up:
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

## Slot 1 · youtube_shorts · `publish-lt-s01-iris-silence`

- status：`planned`
- blocked by：`none`
- scheduled：2026-06-15 20:30 Asia/Taipei
- script：`lt-s01-iris-silence`
- guardian：艾莉絲（`iris`）
- title：他沉默時，你最想聽見哪一句話？
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence
- post URL placeholder：`<REAL_YOUTUBE_SHORTS_URL>`

### Caption

```text
你不是想聽甜言蜜語，你只是想確認自己有沒有被看見。

Take the 15-question quiz to find your emotional guardian: https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence

留言 A/B/C，或寫下一句你最想被說出口的話。
#LoveLanguages #RelationshipQuiz #EmotionalGuardian #HeartLanguage #LoveTypes
```

### Pre-publish Checks

- launch readiness ready_to_publish=1。
- profile link 已完成 set/live，且平台個人頁只導向測驗。
- 影片素材已完成 9:16、字幕、封面或首幀 QA。
- Caption 保留單一 CTA：take the 15-question quiz。
- Tracked URL 指向 /start/ 且 UTM content 與任務一致。
- 不加入 Luna、聯盟書卷或付費商品作為第一 CTA。

### Post-publish Checks

- 公開 post URL 是真實 https URL，不是 <REAL_...>、example.com 或文字型假網址。
- 用 post text import check 先驗證，再 add 寫入。
- 有平台或網站來源檢查後，才回填 site_clicks、quiz_starts、quiz_completions；0 必須是確認後的 0。
- 週回顧前重新跑 publishing status、weekly summary、week decision gate。

### Writeback

Published URL:

```bash
python3 tools/promotion_post_writeback.py update --platform youtube_shorts --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-21 --post-url <REAL_YOUTUBE_SHORTS_URL> --proof-note "<REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified"
```

Minimum KPI after source check:

```bash
python3 tools/promotion_post_writeback.py update --platform youtube_shorts --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-21 --post-url <REAL_YOUTUBE_SHORTS_URL> --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "<REAL_ANALYTICS_SOURCE_PROOF_NOTE> verified"
```

Structured import template:

```text
LoveTypes platform post writeback
platform: youtube_shorts
task_id: publish-lt-s01-iris-silence
status: published
published_date: 2026-06-21
post_url: <REAL_YOUTUBE_SHORTS_URL>
views: 0
site_clicks: 0
quiz_starts: 0
quiz_completions: 0
proof_note: <REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified
```

## Slot 2 · youtube_shorts · `publish-lt-s02-iris-affirmation`

- status：`planned`
- blocked by：`none`
- scheduled：2026-06-17 20:30 Asia/Taipei
- script：`lt-s02-iris-affirmation`
- guardian：艾莉絲（`iris`）
- title：哪一句肯定，會讓你瞬間安心？
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_affirmation
- post URL placeholder：`<REAL_YOUTUBE_SHORTS_URL>`

### Caption

```text
真正的肯定，不是把你說得完美，而是讓你知道自己被看見。

Take the 15-question quiz to find your emotional guardian: https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_affirmation

留言你選的句子，艾莉絲會把它收進晨曦玻璃花園。
#LoveLanguages #RelationshipQuiz #EmotionalGuardian #HeartLanguage #LoveTypes
```

### Pre-publish Checks

- launch readiness ready_to_publish=1。
- profile link 已完成 set/live，且平台個人頁只導向測驗。
- 影片素材已完成 9:16、字幕、封面或首幀 QA。
- Caption 保留單一 CTA：take the 15-question quiz。
- Tracked URL 指向 /start/ 且 UTM content 與任務一致。
- 不加入 Luna、聯盟書卷或付費商品作為第一 CTA。

### Post-publish Checks

- 公開 post URL 是真實 https URL，不是 <REAL_...>、example.com 或文字型假網址。
- 用 post text import check 先驗證，再 add 寫入。
- 有平台或網站來源檢查後，才回填 site_clicks、quiz_starts、quiz_completions；0 必須是確認後的 0。
- 週回顧前重新跑 publishing status、weekly summary、week decision gate。

### Writeback

Published URL:

```bash
python3 tools/promotion_post_writeback.py update --platform youtube_shorts --task-id publish-lt-s02-iris-affirmation --status published --published-date 2026-06-21 --post-url <REAL_YOUTUBE_SHORTS_URL> --proof-note "<REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified"
```

Minimum KPI after source check:

```bash
python3 tools/promotion_post_writeback.py update --platform youtube_shorts --task-id publish-lt-s02-iris-affirmation --status published --published-date 2026-06-21 --post-url <REAL_YOUTUBE_SHORTS_URL> --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "<REAL_ANALYTICS_SOURCE_PROOF_NOTE> verified"
```

Structured import template:

```text
LoveTypes platform post writeback
platform: youtube_shorts
task_id: publish-lt-s02-iris-affirmation
status: published
published_date: 2026-06-21
post_url: <REAL_YOUTUBE_SHORTS_URL>
views: 0
site_clicks: 0
quiz_starts: 0
quiz_completions: 0
proof_note: <REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified
```

## Slot 3 · youtube_shorts · `publish-lt-s03-iris-too-sensitive`

- status：`planned`
- blocked by：`none`
- scheduled：2026-06-19 20:30 Asia/Taipei
- script：`lt-s03-iris-too-sensitive`
- guardian：艾莉絲（`iris`）
- title：你真的太敏感嗎？還是你只是等一句清楚的話？
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_too_sensitive
- post URL placeholder：`<REAL_YOUTUBE_SHORTS_URL>`

### Caption

```text
有時候你不是太敏感，你只是一直在替沉默找理由。

Take the 15-question quiz to find your emotional guardian: https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_too_sensitive

留言「我想被清楚回應」，或選 A：等話、B：等行動、C：等陪伴。
#LoveLanguages #RelationshipQuiz #EmotionalGuardian #HeartLanguage #LoveTypes
```

### Pre-publish Checks

- launch readiness ready_to_publish=1。
- profile link 已完成 set/live，且平台個人頁只導向測驗。
- 影片素材已完成 9:16、字幕、封面或首幀 QA。
- Caption 保留單一 CTA：take the 15-question quiz。
- Tracked URL 指向 /start/ 且 UTM content 與任務一致。
- 不加入 Luna、聯盟書卷或付費商品作為第一 CTA。

### Post-publish Checks

- 公開 post URL 是真實 https URL，不是 <REAL_...>、example.com 或文字型假網址。
- 用 post text import check 先驗證，再 add 寫入。
- 有平台或網站來源檢查後，才回填 site_clicks、quiz_starts、quiz_completions；0 必須是確認後的 0。
- 週回顧前重新跑 publishing status、weekly summary、week decision gate。

### Writeback

Published URL:

```bash
python3 tools/promotion_post_writeback.py update --platform youtube_shorts --task-id publish-lt-s03-iris-too-sensitive --status published --published-date 2026-06-21 --post-url <REAL_YOUTUBE_SHORTS_URL> --proof-note "<REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified"
```

Minimum KPI after source check:

```bash
python3 tools/promotion_post_writeback.py update --platform youtube_shorts --task-id publish-lt-s03-iris-too-sensitive --status published --published-date 2026-06-21 --post-url <REAL_YOUTUBE_SHORTS_URL> --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "<REAL_ANALYTICS_SOURCE_PROOF_NOTE> verified"
```

Structured import template:

```text
LoveTypes platform post writeback
platform: youtube_shorts
task_id: publish-lt-s03-iris-too-sensitive
status: published
published_date: 2026-06-21
post_url: <REAL_YOUTUBE_SHORTS_URL>
views: 0
site_clicks: 0
quiz_starts: 0
quiz_completions: 0
proof_note: <REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified
```
