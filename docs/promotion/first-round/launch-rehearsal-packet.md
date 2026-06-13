# LoveTypes Launch Rehearsal Packet

- Generated: `2026-06-14`
- Profile configured: `0/3`
- Ready to publish: `0`
- Published rows: `0/3`
- Filled KPI rows: `0/3`
- Empty data mode: `1`
- Issues: `0`

## Stage Order

1. `profile_evidence`
2. `profile_writeback`
3. `readiness_gate`
4. `publish_post`
5. `minimum_kpi_backfill`
6. `weekly_review`

## Rehearsal Stages

### profile_evidence: youtube_shorts profile-youtube_shorts

- Status: `ready`
- Blocked by: ``
- Success signal: `profile proof text validates before writeback`
- Check: `python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts.txt`

### profile_evidence: tiktok profile-tiktok

- Status: `ready`
- Blocked by: ``
- Success signal: `profile proof text validates before writeback`
- Check: `python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-tiktok.txt`

### profile_evidence: instagram_reels profile-instagram_reels

- Status: `ready`
- Blocked by: ``
- Success signal: `profile proof text validates before writeback`
- Check: `python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-instagram_reels.txt`

### profile_writeback: youtube_shorts profile-youtube_shorts

- Status: `ready`
- Blocked by: ``
- Success signal: `platform profile tracker row becomes set/live with proof_note`
- Write: `python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts.txt --proof-note "profile link manually verified"`

### profile_writeback: tiktok profile-tiktok

- Status: `ready`
- Blocked by: ``
- Success signal: `platform profile tracker row becomes set/live with proof_note`
- Write: `python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-tiktok.txt --proof-note "profile link manually verified"`

### profile_writeback: instagram_reels profile-instagram_reels

- Status: `ready`
- Blocked by: ``
- Success signal: `platform profile tracker row becomes set/live with proof_note`
- Write: `python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-instagram_reels.txt --proof-note "profile link manually verified"`

### readiness_gate: all launch-readiness

- Status: `blocked_until_profiles_configured`
- Blocked by: `profile_writeback`
- Success signal: `promotion_launch_readiness_ready_to_publish=1`
- Check: `python3 tools/promotion_launch_readiness_gate.py`

### publish_post: youtube_shorts publish-lt-s01-iris-silence

- Status: `blocked_until_readiness_gate`
- Blocked by: `readiness_gate`
- Success signal: `post_url and starter metrics validate before writeback`
- Check: `python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt`
- Write: `python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt --proof-note "post URL and starter metrics manually verified"`

### publish_post: tiktok publish-lt-s01-iris-silence

- Status: `blocked_until_readiness_gate`
- Blocked by: `readiness_gate`
- Success signal: `post_url and starter metrics validate before writeback`
- Check: `python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-tiktok-publish-lt-s01-iris-silence.txt`
- Write: `python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-tiktok-publish-lt-s01-iris-silence.txt --proof-note "post URL and starter metrics manually verified"`

### publish_post: instagram_reels publish-lt-s01-iris-silence

- Status: `blocked_until_readiness_gate`
- Blocked by: `readiness_gate`
- Success signal: `post_url and starter metrics validate before writeback`
- Check: `python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-instagram_reels-publish-lt-s01-iris-silence.txt`
- Write: `python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-instagram_reels-publish-lt-s01-iris-silence.txt --proof-note "post URL and starter metrics manually verified"`

### minimum_kpi_backfill: youtube_shorts publish-lt-s01-iris-silence

- Status: `blocked_until_post_url`
- Blocked by: `publish_post`
- Success signal: `platform row has post_url, site_clicks, quiz_starts, quiz_completions`
- Writeback: `python3 tools/promotion_post_writeback.py update --platform youtube_shorts --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-14 --post-url https://www.youtube.com/shorts/replace-with-real-post-url --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "post URL and first metrics verified"`

### minimum_kpi_backfill: tiktok publish-lt-s01-iris-silence

- Status: `blocked_until_post_url`
- Blocked by: `publish_post`
- Success signal: `platform row has post_url, site_clicks, quiz_starts, quiz_completions`
- Writeback: `python3 tools/promotion_post_writeback.py update --platform tiktok --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-14 --post-url https://www.youtube.com/shorts/replace-with-real-post-url --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "post URL and first metrics verified"`

### minimum_kpi_backfill: instagram_reels publish-lt-s01-iris-silence

- Status: `blocked_until_post_url`
- Blocked by: `publish_post`
- Success signal: `platform row has post_url, site_clicks, quiz_starts, quiz_completions`
- Writeback: `python3 tools/promotion_post_writeback.py update --platform instagram_reels --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-14 --post-url https://www.youtube.com/shorts/replace-with-real-post-url --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "post URL and first metrics verified"`

### weekly_review: all weekly-review

- Status: `blocked_until_minimum_kpi`
- Blocked by: `minimum_kpi_backfill`
- Success signal: `weeklyReviewReady becomes true before offer or revenue decisions`
- Check: `python3 tools/promotion_weekly_review_packet.py --check`
