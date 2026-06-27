# LoveTypes Launch Proof Control Sheet

- 產生日期：2026-06-28
- stage：`first_batch_kpi`
- profile ready / blocked：0 / 1
- profile placeholder / real proof ready：1 / 0
- post ready / blocked：0 / 1
- proof rows：2
- clipboard blocks：2
- issues：0

## Rules

- Profile proofs must be completed before post proofs are imported.
- Batch add commands are allowed only when all active rows in that batch are ready.
- Post proof requires a real public post URL and checked analytics/source note.
- No product, Luna, or affiliate decision is allowed while minimum KPI rows are empty.

## Ordered Steps

### `prepare_profile_proofs`

- status：`current_action`
- command：`python3 tools/promotion_profile_batch_import.py --check`
- release：profile batch readyRows is 1.

### `write_profile_batch`

- status：`complete`
- command：`python3 tools/promotion_profile_batch_import.py --add`
- release：master gate moves from profile_setup to first_batch_publish.

### `prepare_post_proofs`

- status：`blocked_until_profile_gate`
- command：`python3 tools/promotion_post_batch_import.py --check`
- release：post batch readyRows is 1.

### `write_post_batch`

- status：`complete`
- command：`python3 tools/promotion_post_batch_import.py --add`
- release：first batch has 1 published rows and minimum KPI rows.

### `refresh_and_review`

- status：`blocked_until_post_writeback`
- command：`python3 tools/promotion_daily_ops_refresh.py && python3 tools/promotion_launch_sequence_dry_run.py`
- release：dry run stays green and weekly evidence gate can open.

## Proof Rows

- `profile` / `youtube_shorts`：`blocked_until_real_proof` ready=0 issues=1 file=`docs/promotion/first-round/proof-youtube_shorts.txt`
- `post` / `youtube_shorts`：`blocked_until_real_public_post` ready=0 issues=2 file=`docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt`
