# LoveTypes First Batch KPI Quickstart

- 產生日期：2026-06-25
- rows：1
- ready for KPI：1
- blocked rows：0
- published rows：1
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

- action status：`ready_for_kpi_source_check`
- ready for KPI：`1`
- published：`1`
- post URL：https://www.youtube.com/watch?v=uj9ZwYIKDrE
- blocked by：(none)
- minimum KPIs：`site_clicks, quiz_starts, quiz_completions`
- zero-source rows：3

Zero-source checks:

- `site_clicks`：status `needs_source_proof`；source：Cloudflare/Web analytics, platform link analytics, or tracked UTM report.
- `quiz_starts`：status `needs_source_proof`；source：Funnel event catalog/report, analytics event export, or manual verified source.
- `quiz_completions`：status `needs_source_proof`；source：Funnel event catalog/report, analytics event export, or manual verified source.

Proof text after analytics source is checked:

```text
LoveTypes platform post writeback
platform: youtube_shorts
task_id: publish-lt-s01-iris-silence
status: published
published_date: 2026-06-25
post_url: <REAL_YOUTUBE_SHORTS_URL>
site_clicks: <CHECKED_SITE_CLICKS>
quiz_starts: <CHECKED_QUIZ_STARTS>
quiz_completions: <CHECKED_QUIZ_COMPLETIONS>
proof_note: analytics source checked 2026-06-25 for youtube_shorts/publish-lt-s01-iris-silence
```

- write：`python3 tools/promotion_post_writeback.py update --platform youtube_shorts --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-25 --post-url https://www.youtube.com/watch?v=uj9ZwYIKDrE --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "<REAL_ANALYTICS_SOURCE_PROOF_NOTE> verified"`
- stop：Stop if the post URL is not public HTTPS, analytics source was not checked, or a zero value lacks source proof.
