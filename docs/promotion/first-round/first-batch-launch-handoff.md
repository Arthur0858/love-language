# LoveTypes First Batch Launch Handoff

- 產生日期：2026-06-28
- rows：1
- profile gate ready：1
- asset ready：1
- publish ready：0
- post batch ready：0
- post proof blocked：1
- issues：0

## Commands
- `python3 tools/promotion_profile_batch_import.py --check`
- `python3 tools/promotion_profile_batch_import.py --add`
- `python3 tools/promotion_post_batch_import.py --check`
- `python3 tools/promotion_post_batch_import.py --add`
- `python3 tools/promotion_daily_ops_refresh.py && python3 tools/promotion_launch_sequence_dry_run.py`

## Rows

### youtube_shorts · `publish-lt-s01-iris-silence`
- status：`published`
- guardian：`iris`
- schedule：2026-06-15 20:30 Asia/Taipei
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence
- proof：`docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt`
- check：``
- write：``
- caption source：`docs/promotion/first-round/first-batch-publish-action-sheet.md`
- stop：Stop if profile gate is not ready, post URL is still placeholder, caption changes CTA, or platform preview adds commercial claims.
