# LoveTypes Profile to Publish Handoff

- 產生日期：2026-06-14
- rows：7
- complete rows：3
- current blockers：1
- blocked upstream rows：3
- ready to publish：0
- issues：0

## Rule

- Profile proof must be written back before first-batch publishing.
- Run the daily ops refresh after profile writeback before using publish sheets.
- Keep KPI and product decisions in empty-data mode until real post URLs and metric proof exist.

## Handoff Steps

### `profile_action_sheet_ready`

- phase：`profile_setup`
- status：`complete`
- value：3 / 3
- action：Use the platform-specific Bio/Profile link copy from the action sheet.
- evidence：Action sheet has three platforms, valid /start/ UTM links, and no issues.
- command：`python3 tools/promotion_profile_setup_action_sheet.py --check`
- stop：Stop if any Bio adds paid, diagnosis, therapy, or guarantee claims.

### `profile_writeback_complete`

- phase：`profile_writeback`
- status：`current_blocker`
- value：0 / 3
- action：After setting each public profile link, write back status set/live with a proof note.
- evidence：platform-profile-tracker.csv has status set/live, set date, and traceable proof for all platforms.
- command：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts.txt`
- stop：Do not write set/live without screenshot, clicked public link, or platform timestamp evidence.

### `profile_evidence_complete`

- phase：`profile_writeback`
- status：`blocked_upstream`
- value：0 / 3
- action：Confirm every completed profile row has proof in the evidence ledger.
- evidence：Evidence ledger traceable count equals required count and evidence issues are zero.
- command：`python3 tools/promotion_evidence_ledger.py --check`
- stop：Stop if proof note is vague, missing, or not tied to a platform/date.

### `ops_refresh_after_profile`

- phase：`handoff`
- status：`complete`
- value：1 / 1
- action：Refresh promotion docs after profile writeback before opening publication.
- evidence：Profile completion gate packetsInSync is true.
- command：`python3 tools/promotion_daily_ops_refresh.py`
- stop：Do not publish from stale action sheets after tracker writeback.

### `launch_readiness_open`

- phase：`handoff`
- status：`blocked_upstream`
- value：0 / 1
- action：Confirm launch readiness opens first-batch publishing.
- evidence：launch-readiness-gate.json readiness.readyToPublishPosts is true.
- command：`python3 tools/promotion_launch_readiness_gate.py --check`
- stop：Stop if profile links are incomplete, campaign UTM is invalid, or assets are not ready.

### `first_batch_action_sheet_ready`

- phase：`publish`
- status：`blocked_upstream`
- value：0 / 3
- action：Publish only the first batch rows that become ready after the profile gate opens.
- evidence：First-batch publish action sheet has three ready rows and zero issues.
- command：`python3 tools/promotion_first_batch_publish_action_sheet.py --check`
- stop：Do not publish if any row remains blocked_until_profile_links.

### `single_current_blocker_visible`

- phase：`stage_control`
- status：`complete`
- value：1 / 1
- action：Keep the stage matrix exposing exactly one current blocker before advancing.
- evidence：stage-transition-matrix has one current_blocker and no issues.
- command：`python3 tools/promotion_stage_transition_matrix.py --check`
- stop：Stop if multiple current blockers appear or if later stages become next before profile handoff.
