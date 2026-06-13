# LoveTypes Launch Day Run Sheet

- 產生日期：2026-06-14
- rows：11
- profile rows：3
- publish rows：3
- post ops rows：3
- ready rows：3
- blocked rows：8
- issues：0

## Rule

- Execute rows in order; later rows do not override earlier blocked gates.
- Check commands are safe to run; write commands require real external proof.
- Profile setup must reach 3/3 before first-batch publishing.
- Post URL and KPI evidence must complete before weekly review or commerce decisions.

## Run Order

### 1. profile_setup · youtube_shorts · `profile-youtube_shorts`

- status：`ready_to_configure`
- action：Set the platform profile link, then verify the structured proof text before writeback.
- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts.txt`
- write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts.txt --proof-note "screenshot profile-youtube_shorts-2026-06-14.png verified"`
- success：profile proof import validates and platform tracker row can be set/live with real proof.
- stop：A real platform screenshot/click proof must exist before running the write command.

### 2. profile_setup · tiktok · `profile-tiktok`

- status：`ready_to_configure`
- action：Set the platform profile link, then verify the structured proof text before writeback.
- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-tiktok.txt`
- write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-tiktok.txt --proof-note "screenshot profile-tiktok-2026-06-14.png verified"`
- success：profile proof import validates and platform tracker row can be set/live with real proof.
- stop：A real platform screenshot/click proof must exist before running the write command.

### 3. profile_setup · instagram_reels · `profile-instagram_reels`

- status：`ready_to_configure`
- action：Set the platform profile link, then verify the structured proof text before writeback.
- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-instagram_reels.txt`
- write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-instagram_reels.txt --proof-note "screenshot profile-instagram_reels-2026-06-14.png verified"`
- success：profile proof import validates and platform tracker row can be set/live with real proof.
- stop：A real platform screenshot/click proof must exist before running the write command.

### 4. readiness_gate · all · `launch-readiness`

- status：`blocked`
- action：Refresh profile completion, launch readiness and dashboard before publishing.
- check：`python3 tools/promotion_profile_completion_gate.py --check && python3 tools/promotion_launch_readiness_gate.py --check && python3 tools/promotion_launch_ops_dashboard.py --check`
- write：
- success：promotion_launch_readiness_ready_to_publish=1 and profile_configured=3.
- stop：Stop before publishing while profile_configured is less than 3.

### 5. publish_first_batch · youtube_shorts · `publish-lt-s01-iris-silence`

- status：`blocked_until_profile_gate`
- action：Publish the first Iris post only after profile gate is ready; keep quiz CTA unchanged.
- check：`python3 tools/promotion_first_batch_publish_readiness_pack.py --check`
- write：
- success：A real public post URL exists and replaces the placeholder in the post proof file.
- stop：Stop if profile gate is not ready, post URL is still placeholder, caption changes CTA, or platform preview adds commercial claims.

### 6. publish_first_batch · tiktok · `publish-lt-s01-iris-silence`

- status：`blocked_until_profile_gate`
- action：Publish the first Iris post only after profile gate is ready; keep quiz CTA unchanged.
- check：`python3 tools/promotion_first_batch_publish_readiness_pack.py --check`
- write：
- success：A real public post URL exists and replaces the placeholder in the post proof file.
- stop：Stop if profile gate is not ready, post URL is still placeholder, caption changes CTA, or platform preview adds commercial claims.

### 7. publish_first_batch · instagram_reels · `publish-lt-s01-iris-silence`

- status：`blocked_until_profile_gate`
- action：Publish the first Iris post only after profile gate is ready; keep quiz CTA unchanged.
- check：`python3 tools/promotion_first_batch_publish_readiness_pack.py --check`
- write：
- success：A real public post URL exists and replaces the placeholder in the post proof file.
- stop：Stop if profile gate is not ready, post URL is still placeholder, caption changes CTA, or platform preview adds commercial claims.

### 8. post_url_and_kpi · youtube_shorts · `publish-lt-s01-iris-silence`

- status：`blocked_until_post_url`
- action：Publish the post and replace the placeholder URL with a real public post URL.
- check：`python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt`
- write：`python3 tools/promotion_post_writeback.py update --platform youtube_shorts --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-14 --post-url <REAL_YOUTUBE_SHORTS_URL> --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "platform analytics checked 2026-06-14"`
- success：post URL, site_clicks, quiz_starts and quiz_completions are backed by checked evidence.
- stop：Do not run writeback with placeholder URLs or guessed KPI values.

### 9. post_url_and_kpi · tiktok · `publish-lt-s01-iris-silence`

- status：`blocked_until_post_url`
- action：Publish the post and replace the placeholder URL with a real public post URL.
- check：`python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-tiktok-publish-lt-s01-iris-silence.txt`
- write：`python3 tools/promotion_post_writeback.py update --platform tiktok --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-14 --post-url <REAL_TIKTOK_VIDEO_URL> --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "platform analytics checked 2026-06-14"`
- success：post URL, site_clicks, quiz_starts and quiz_completions are backed by checked evidence.
- stop：Do not run writeback with placeholder URLs or guessed KPI values.

### 10. post_url_and_kpi · instagram_reels · `publish-lt-s01-iris-silence`

- status：`blocked_until_post_url`
- action：Publish the post and replace the placeholder URL with a real public post URL.
- check：`python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-instagram_reels-publish-lt-s01-iris-silence.txt`
- write：`python3 tools/promotion_post_writeback.py update --platform instagram_reels --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-14 --post-url <REAL_INSTAGRAM_REEL_URL> --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "platform analytics checked 2026-06-14"`
- success：post URL, site_clicks, quiz_starts and quiz_completions are backed by checked evidence.
- stop：Do not run writeback with placeholder URLs or guessed KPI values.

### 11. weekly_review · all · `weekly-review`

- status：`blocked_until_minimum_kpi`
- action：Run weekly review only after all first-batch post URL and KPI evidence passes.
- check：`python3 tools/promotion_weekly_review_packet.py --check && python3 tools/promotion_weekly_decision_evidence_checklist.py --check`
- write：
- success：weekly_review_ready=1 and empty_data=0 before changing content or commerce paths.
- stop：Stop all offer/Luna/affiliate prioritization while empty_data=1.
