# LoveTypes Profile to Publish Handoff

- 產生日期：2026-06-23
- rows：10
- complete rows：10
- current blockers：0
- blocked upstream rows：0
- ready to publish：1
- issues：0

## Rule

- Profile proof must be written back before first-batch publishing.
- Run the daily ops refresh after profile writeback before using publish sheets.
- Keep KPI and product decisions in empty-data mode until real post URLs and metric proof exist.

## Handoff Steps

### `profile_action_sheet_ready`

- phase：`profile_setup`
- status：`complete`
- value：1 / 1
- action：Use the platform-specific Bio/Profile link copy from the action sheet.
- evidence：Action sheet has active platforms, valid /start/ UTM links, and no issues.
- command：`python3 tools/promotion_profile_setup_action_sheet.py --check`
- stop：Stop if any Bio adds paid, diagnosis, therapy, or guarantee claims.

### `profile_setup_handoff_ready`

- phase：`profile_setup`
- status：`complete`
- value：1 / 1
- action：Use the consolidated profile setup handoff pack before touching platform profiles.
- evidence：profile-setup-handoff-pack has active ready_to_configure rows, or profile setup is already configured with traceable proof.
- command：`python3 tools/promotion_profile_setup_handoff_pack.py --check`
- stop：Stop if any platform lacks a public-ready profile link, proof template, or identity check.

### `profile_writeback_complete`

- phase：`profile_writeback`
- status：`complete`
- value：1 / 1
- action：After setting each public profile link, write back status set/live with a proof note.
- evidence：platform-profile-tracker.csv has status set/live, set date, and traceable proof for all platforms.
- command：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts.txt`
- stop：Do not write set/live without screenshot, clicked public link, or platform timestamp evidence.

### `profile_evidence_complete`

- phase：`profile_writeback`
- status：`complete`
- value：2 / 2
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
- status：`complete`
- value：1 / 1
- action：Confirm launch readiness opens first-batch publishing.
- evidence：launch-readiness-gate.json readiness.readyToPublishPosts is true.
- command：`python3 tools/promotion_launch_readiness_gate.py --check`
- stop：Stop if profile links are incomplete, campaign UTM is invalid, or assets are not ready.

### `first_batch_action_sheet_ready`

- phase：`publish`
- status：`complete`
- value：1 / 1
- action：Publish only the first batch rows that become ready after the profile gate opens.
- evidence：First-batch publish action sheet has active ready rows, or the first-batch publication packet proves the row is already published.
- command：`python3 tools/promotion_first_batch_publish_action_sheet.py --check`
- stop：Do not publish if any row remains blocked_until_profile_links.

### `publish_readiness_guarded`

- phase：`publish`
- status：`complete`
- value：2 / 2
- action：Confirm first-batch assets are ready and placeholder proof templates are still safely rejected.
- evidence：first-batch-publish-readiness-pack has active asset-ready rows and safely rejected proof templates.
- command：`python3 tools/promotion_first_batch_publish_readiness_pack.py --check`
- stop：Do not publish if proof templates become importable before real public post URLs exist.

### `post_proof_handoff_guarded`

- phase：`post_proof`
- status：`complete`
- value：2 / 2
- action：Keep post proof handoff files ready for real URLs while rejecting placeholders.
- evidence：post-proof-handoff-pack has active proof files and safely rejected templates.
- command：`python3 tools/promotion_post_proof_handoff_pack.py --check`
- stop：Do not run writeback until the proof check becomes ready_to_import with real platform URLs.

### `single_current_blocker_visible`

- phase：`stage_control`
- status：`complete`
- value：1 / 1
- action：Keep the stage matrix exposing exactly one current blocker before advancing.
- evidence：stage-transition-matrix has one current_blocker and no issues.
- command：`python3 tools/promotion_stage_transition_matrix.py --check`
- stop：Stop if multiple current blockers appear or if later stages become next before profile handoff.
