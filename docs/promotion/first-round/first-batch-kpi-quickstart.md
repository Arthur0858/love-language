# LoveTypes First Batch KPI Quickstart

- 產生日期：2026-06-20
- rows：1
- ready for KPI：0
- blocked rows：1
- published rows：0
- zero-source rows：3
- weekly ready：0
- empty data mode：0
- issues：0

## Rules

- Do not run KPI writeback until the platform post has a real public HTTPS post URL.
- A zero KPI value is valid only after checking the named analytics source.
- Minimum KPI fields are site_clicks, quiz_starts, and quiz_completions.
- Weekly review and commerce decisions remain locked until all first-batch minimum KPIs are written back.
- Do not use guesses, private drafts, scheduled URLs, or placeholder post URLs.

## youtube_shorts · `publish-lt-s01-iris-silence`

- action status：`blocked_until_public_post_url`
- ready for KPI：`0`
- published：`0`
- post URL：(not published)
- blocked by：first-batch post is not published
- minimum KPIs：`site_clicks, quiz_starts, quiz_completions`
- zero-source rows：3

Zero-source checks:

- `site_clicks`：status `pending_publish`；source：Cloudflare/Web analytics, platform link analytics, or tracked UTM report.
- `quiz_starts`：status `pending_publish`；source：Funnel event catalog/report, analytics event export, or manual verified source.
- `quiz_completions`：status `pending_publish`；source：Funnel event catalog/report, analytics event export, or manual verified source.

Proof text after analytics source is checked:

```text
LoveTypes platform post writeback
platform: youtube_shorts
task_id: publish-lt-s01-iris-silence
status: published
published_date: 2026-06-20
post_url: <REAL_YOUTUBE_SHORTS_URL>
site_clicks: <CHECKED_SITE_CLICKS>
quiz_starts: <CHECKED_QUIZ_STARTS>
quiz_completions: <CHECKED_QUIZ_COMPLETIONS>
proof_note: analytics source checked 2026-06-20 for youtube_shorts/publish-lt-s01-iris-silence
```

- write：`python3 tools/promotion_post_writeback.py update --platform youtube_shorts --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-20 --post-url <REAL_YOUTUBE_SHORTS_URL> --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "<REAL_ANALYTICS_SOURCE_PROOF_NOTE> verified"`
- stop：Stop if the post URL is not public HTTPS, analytics source was not checked, or a zero value lacks source proof.
