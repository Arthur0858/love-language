# LoveTypes Publish to KPI Handoff

- 產生日期：2026-06-14
- rows：7
- complete rows：1
- current blockers：1
- blocked upstream rows：5
- published rows：0 / 3
- minimum KPI rows：0 / 3
- ready for weekly review：0
- issues：0

## Rule

- Profile handoff must open before first-batch publishing.
- Public post URLs and traceable proof must exist before KPI writeback.
- Zero KPI values are valid only after source checks.
- Weekly review must open before changing commerce, Luna, affiliate, or paid CTA priority.

## Handoff Steps

### `profile_publish_handoff_open`

- phase：`profile_to_publish`
- status：`current_blocker`
- value：0 / 1
- action：Only continue after the profile handoff says first-batch publishing is open.
- evidence：profile-publish-handoff readyToPublish is true after profile proof writeback and refresh.
- command：`python3 tools/promotion_profile_publish_handoff.py --check`
- stop：Do not publish first-batch posts while profile_writeback_complete is still blocked.

### `first_batch_publish_sheet_ready`

- phase：`publish`
- status：`blocked_upstream`
- value：0 / 3
- action：Confirm three first-batch rows are ready before opening platform publishing.
- evidence：first-batch publish action sheet has three ready rows and zero issues.
- command：`python3 tools/promotion_first_batch_publish_action_sheet.py --check`
- stop：Do not publish if any row remains blocked_until_profile_links.

### `post_url_writeback_complete`

- phase：`post_writeback`
- status：`blocked_upstream`
- value：0 / 3
- action：After each platform post is public, write back real HTTPS post_url with proof.
- evidence：posting-queue.csv and platform-kpi-tracker.csv have published status, date, post_url, and proof note.
- command：`python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt`
- stop：Do not mark published with placeholder URLs, private URLs, or unverified scheduled drafts.

### `post_evidence_traceable`

- phase：`post_writeback`
- status：`blocked_upstream`
- value：0 / 3
- action：Confirm every first-batch post has traceable public URL evidence.
- evidence：first-batch completion gate traceablePostEvidence matches all three published rows.
- command：`python3 tools/promotion_first_batch_completion_gate.py --check`
- stop：Stop if proof is generic, missing, or not tied to platform/date/post URL.

### `minimum_kpi_source_check`

- phase：`kpi_writeback`
- status：`blocked_upstream`
- value：0 / 3
- action：Keep KPI rows blocked until real post URLs are written back.
- evidence：first-batch KPI action sheet has three ready rows before source checks, then minimumKpiRows reaches three.
- command：`python3 tools/promotion_first_batch_kpi_action_sheet.py --check`
- stop：Do not treat 0 as data unless the platform or site analytics source was checked.

### `weekly_review_open`

- phase：`weekly_review`
- status：`blocked_upstream`
- value：0 / 1
- action：Open weekly review only after post URLs, proof, and minimum KPI are complete.
- evidence：first-batch-completion-gate readyForWeeklyReview is true.
- command：`python3 tools/promotion_weekly_review_packet.py --check && python3 tools/promotion_week_decision_gate.py --check`
- stop：Do not rank guardians, offers, Luna, or affiliate routes while empty data mode is true.

### `empty_data_safety_locked`

- phase：`decision_safety`
- status：`complete`
- value：1 / 1
- action：Keep commercial decisions locked until weekly review opens with real data.
- evidence：weekly-review remains empty-data mode and stage matrix exposes exactly one current blocker.
- command：`python3 tools/promotion_weekly_review_packet.py --check && python3 tools/promotion_stage_transition_matrix.py --check`
- stop：Stop if commercial or paid CTA decisions become allowed before KPI proof.
