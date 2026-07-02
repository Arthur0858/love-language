# LoveTypes Launch Rehearsal Packet

- Generated: `2026-07-02`
- Profile configured: `1/0`
- Ready to publish: `1`
- Profile setup ready stages: `0`
- Publish ready stages: `0`
- KPI ready stages: `1`
- Published rows: `1/0`
- Filled KPI rows: `0/0`
- Empty data mode: `0`
- Issues: `0`

## Stage Order

1. `profile_evidence`
2. `profile_writeback`
3. `readiness_gate`
4. `publish_post`
5. `minimum_kpi_backfill`
6. `weekly_review`

## Rehearsal Stages

### readiness_gate: all launch-readiness

- Status: `blocked_until_profiles_configured`
- Blocked by: `profile_writeback`
- Success signal: `promotion_launch_readiness_ready_to_publish=1`
- Check: `python3 tools/promotion_launch_readiness_gate.py`

### minimum_kpi_backfill: youtube_shorts publish-lt-s01-iris-silence

- Status: `ready`
- Blocked by: ``
- Success signal: `platform row has post_url, site_clicks, quiz_starts, quiz_completions`
- Writeback: `python3 tools/promotion_post_writeback.py update --platform youtube_shorts --task-id publish-lt-s01-iris-silence --status published --published-date 2026-07-02 --post-url <REAL_YOUTUBE_SHORTS_URL> --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "<REAL_ANALYTICS_SOURCE_PROOF_NOTE> verified"`

### weekly_review: all weekly-review

- Status: `blocked_until_minimum_kpi`
- Blocked by: `minimum_kpi_backfill`
- Success signal: `weeklyReviewReady becomes true before offer or revenue decisions`
- Check: `python3 tools/promotion_weekly_review_packet.py --check`
