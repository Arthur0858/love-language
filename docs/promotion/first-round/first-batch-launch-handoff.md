# LoveTypes First Batch Launch Handoff

- 產生日期：2026-06-14
- rows：3
- profile gate ready：0
- asset ready：3
- publish ready：0
- post batch ready：0
- post proof blocked：3
- issues：0

## Commands
- `python3 tools/promotion_profile_batch_import.py --check`
- `python3 tools/promotion_profile_batch_import.py --add`
- `python3 tools/promotion_post_batch_import.py --check`
- `python3 tools/promotion_post_batch_import.py --add`
- `python3 tools/promotion_daily_ops_refresh.py && python3 tools/promotion_launch_sequence_dry_run.py`

## Rows

### youtube_shorts · `publish-lt-s01-iris-silence`
- status：`blocked_until_profile_gate`
- guardian：`iris`
- schedule：2026-06-15 20:30 Asia/Taipei
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence
- proof：`docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt`
- check：`python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt`
- write：`python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt --proof-note "<REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified"`
- caption source：`docs/promotion/first-round/first-batch-publish-action-sheet.md`
- stop：Stop if profile gate is not ready, post URL is still placeholder, caption changes CTA, or platform preview adds commercial claims.

### tiktok · `publish-lt-s01-iris-silence`
- status：`blocked_until_profile_gate`
- guardian：`iris`
- schedule：2026-06-15 21:00 Asia/Taipei
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence
- proof：`docs/promotion/first-round/proof-tiktok-publish-lt-s01-iris-silence.txt`
- check：`python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-tiktok-publish-lt-s01-iris-silence.txt`
- write：`python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-tiktok-publish-lt-s01-iris-silence.txt --proof-note "<REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified"`
- caption source：`docs/promotion/first-round/first-batch-publish-action-sheet.md`
- stop：Stop if profile gate is not ready, post URL is still placeholder, caption changes CTA, or platform preview adds commercial claims.

### instagram_reels · `publish-lt-s01-iris-silence`
- status：`blocked_until_profile_gate`
- guardian：`iris`
- schedule：2026-06-15 21:30 Asia/Taipei
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence
- proof：`docs/promotion/first-round/proof-instagram_reels-publish-lt-s01-iris-silence.txt`
- check：`python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-instagram_reels-publish-lt-s01-iris-silence.txt`
- write：`python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-instagram_reels-publish-lt-s01-iris-silence.txt --proof-note "<REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified"`
- caption source：`docs/promotion/first-round/first-batch-publish-action-sheet.md`
- stop：Stop if profile gate is not ready, post URL is still placeholder, caption changes CTA, or platform preview adds commercial claims.
