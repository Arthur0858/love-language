# LoveTypes Launch Proof Control Sheet

- 產生日期：2026-06-14
- stage：`profile_setup`
- profile ready / blocked：0 / 3
- profile placeholder / real proof ready：3 / 0
- post ready / blocked：0 / 3
- proof rows：6
- clipboard blocks：6
- issues：0

## Rules

- Profile proofs must be completed before post proofs are imported.
- Batch add commands are allowed only when all three rows in that batch are ready.
- Post proof requires a real public post URL and checked analytics/source note.
- No product, Luna, or affiliate decision is allowed while minimum KPI rows are empty.

## Ordered Steps

### `prepare_profile_proofs`

- status：`current_action`
- command：`python3 tools/promotion_profile_batch_import.py --check`
- release：profile batch readyRows is 3.

### `write_profile_batch`

- status：`blocked_until_profile_ready`
- command：`python3 tools/promotion_profile_batch_import.py --add`
- release：master gate moves from profile_setup to first_batch_publish.

### `prepare_post_proofs`

- status：`blocked_until_profile_gate`
- command：`python3 tools/promotion_post_batch_import.py --check`
- release：post batch readyRows is 3.

### `write_post_batch`

- status：`blocked_until_post_ready`
- command：`python3 tools/promotion_post_batch_import.py --add`
- release：first batch has 3 published rows and minimum KPI rows.

### `refresh_and_review`

- status：`blocked_until_post_writeback`
- command：`python3 tools/promotion_daily_ops_refresh.py && python3 tools/promotion_launch_sequence_dry_run.py`
- release：dry run stays green and weekly evidence gate can open.

## Proof Rows

- `profile` / `youtube_shorts`：`blocked_until_real_proof` ready=0 issues=1 file=`docs/promotion/first-round/proof-youtube_shorts.txt`
- `profile` / `tiktok`：`blocked_until_real_proof` ready=0 issues=1 file=`docs/promotion/first-round/proof-tiktok.txt`
- `profile` / `instagram_reels`：`blocked_until_real_proof` ready=0 issues=1 file=`docs/promotion/first-round/proof-instagram_reels.txt`
- `post` / `youtube_shorts`：`blocked_until_real_public_post` ready=0 issues=2 file=`docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt`
- `post` / `tiktok`：`blocked_until_real_public_post` ready=0 issues=2 file=`docs/promotion/first-round/proof-tiktok-publish-lt-s01-iris-silence.txt`
- `post` / `instagram_reels`：`blocked_until_real_public_post` ready=0 issues=2 file=`docs/promotion/first-round/proof-instagram_reels-publish-lt-s01-iris-silence.txt`
