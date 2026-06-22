# LoveTypes First Batch KPI Closure Quickstart

- 產生日期：2026-06-22
- rows：1
- ready for KPI：1
- blocked rows：0
- published rows：1
- zero pending rows：0
- zero source proof needs / complete / missing：3 / 0 / 0
- minimum KPI rows：0
- weekly ready：0
- empty data：1
- master stage：`first_batch_kpi`
- master profile configured：1
- issues：0

## Rules

- Public post URL writeback is the first gate; KPI source checks are not valid before it.
- Zero values are acceptable only as checked zeroes with source proof.
- The minimum KPI set is site_clicks, quiz_starts, and quiz_completions.
- Weekly review remains closed while emptyData is true.
- Keep commerce and product decisions locked until first-batch KPI rows exist.

## Closure Steps

### `post_url_writeback_complete`

- status：`complete`
- command：`python3 tools/promotion_first_batch_publish_closure_quickstart.py --check && python3 tools/promotion_post_ops_readiness_pack.py --check`
- release：All active first-batch posts have real public HTTPS post_url values.
- stop：Do not continue with KPI proof while post_url fields are blank, scheduled-only, private, or placeholders.

### `verify_zero_kpi_sources`

- status：`complete`
- command：`python3 tools/promotion_zero_kpi_evidence_checklist.py --check`
- release：Each platform row has checked-source proof for site_clicks, quiz_starts, and quiz_completions.
- stop：Do not treat zero as data until a named analytics source has actually been checked.

### `writeback_minimum_kpis`

- status：`blocked_until_source_proof`
- command：`python3 tools/promotion_post_writeback.py update ... --site-clicks <REAL_OR_CHECKED_ZERO> --quiz-starts <REAL_OR_CHECKED_ZERO> --quiz-completions <REAL_OR_CHECKED_ZERO>`
- release：All first-batch rows include checked minimum KPI values.
- stop：Do not write estimates, drafts, or unverified copied counts.

### `refresh_ops_docs`

- status：`blocked_until_kpi_writeback`
- command：`python3 tools/promotion_daily_ops_refresh.py`
- release：Generated launch, KPI, weekly, and handoff docs reflect the written KPI rows.
- stop：Do not run a decision from stale generated docs.

### `open_weekly_review`

- status：`blocked_until_minimum_kpi`
- command：`python3 tools/promotion_first_batch_completion_gate.py --check && python3 tools/promotion_weekly_review_packet.py --check`
- release：Weekly review is open only after publication, URL proof, and minimum KPI proof all pass.
- stop：Do not make product or channel decisions while emptyDataMode is still true.

## Platform Rows

### youtube_shorts · `publish-lt-s01-iris-silence`

- status：`needs_kpi_source_proof`
- published：1
- ready for KPI：1
- post URL：https://www.youtube.com/watch?v=uj9ZwYIKDrE
- blocked by：needs_kpi_source_proof
- minimum KPIs：`site_clicks, quiz_starts, quiz_completions`

Zero checks:

- `site_clicks`：status `needs_source_proof`；source：Cloudflare/Web analytics, platform link analytics, or tracked UTM report.
- `quiz_starts`：status `needs_source_proof`；source：Funnel event catalog/report, analytics event export, or manual verified source.
- `quiz_completions`：status `needs_source_proof`；source：Funnel event catalog/report, analytics event export, or manual verified source.

Writeback command after source proof:

```text
python3 tools/promotion_post_writeback.py update --platform youtube_shorts --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-22 --post-url https://www.youtube.com/watch?v=uj9ZwYIKDrE --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "<REAL_ANALYTICS_SOURCE_PROOF_NOTE> verified"
```

Proof template:

```text
LoveTypes platform post writeback
platform: youtube_shorts
task_id: publish-lt-s01-iris-silence
status: published
published_date: 2026-06-22
post_url: <REAL_YOUTUBE_SHORTS_URL>
site_clicks: <CHECKED_SITE_CLICKS>
quiz_starts: <CHECKED_QUIZ_STARTS>
quiz_completions: <CHECKED_QUIZ_COMPLETIONS>
proof_note: analytics source checked 2026-06-22 for youtube_shorts/publish-lt-s01-iris-silence
```

- next：Attach checked-source proof for site_clicks, quiz_starts and quiz_completions.
