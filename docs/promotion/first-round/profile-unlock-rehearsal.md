# LoveTypes Profile Unlock Rehearsal

- 產生日期：2026-07-02
- proof files：1
- current ready / blocked：0 / 1
- current placeholder / real proof ready：1 / 0
- synthetic ready：1
- candidate tracker valid：1
- launch dry run green：1
- issues：0

## Rule

- This rehearsal does not write tracker rows.
- It proves that replacing placeholder proof notes with traceable profile evidence would unlock the guarded profile batch path.
- Real add still requires actual screenshot, clicked public link, recording, or platform URL proof.

## Commands After Real Proof

- `python3 tools/promotion_profile_batch_import.py --check`
- `python3 tools/promotion_profile_batch_import.py --add`
- `python3 tools/promotion_daily_ops_refresh.py && python3 tools/promotion_launch_sequence_dry_run.py`

## Rows

- `youtube_shorts`：ready=1 file=`docs/promotion/first-round/proof-youtube_shorts.txt` issues=0
