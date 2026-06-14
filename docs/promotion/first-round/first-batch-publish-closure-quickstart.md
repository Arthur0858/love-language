# LoveTypes First Batch Publish Closure Quickstart

- 產生日期：2026-06-14
- rows：3
- profile handoff ready：0
- ready / blocked rows：0 / 3
- published / pending rows：0 / 3
- public pending rows：24
- minimum KPI rows：0
- completion ready：0
- issues：0

## Rules

- First-batch publishing stays blocked until profile handoff is open.
- Publish only the first Iris script across YouTube Shorts, TikTok, and Instagram Reels.
- Do not write post_url with placeholders, private drafts, scheduled previews, or login-only links.
- After each post URL writeback, refresh daily ops before trusting KPI or weekly review packets.
- KPI interpretation remains blocked until public URL checks and checked-source KPI proof are complete.

## Closure Steps

- `profile_publish_handoff_open` / `current_blocker`：`python3 tools/promotion_profile_publish_handoff.py --check`
  Stop: Do not publish while profile_writeback_complete remains blocked.
- `publish_first_batch_posts` / `blocked_until_profile_gate`：`python3 tools/promotion_first_batch_publish_quickstart.py --check`
  Stop: Publish only rows with readyToPublish=1 and unchanged quiz CTA.
- `writeback_public_post_urls` / `blocked_until_public_url`：`python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-<platform>-publish-lt-s01-iris-silence.txt --proof-note "public URL and analytics source checked YYYY-MM-DD"`
  Stop: Replace <REAL_...> with a real public HTTPS post URL before writeback.
- `verify_public_post_urls` / `blocked_until_post_url`：`python3 tools/promotion_public_post_url_checklist.py --check && python3 tools/promotion_post_ops_readiness_pack.py --check`
  Stop: Stop if platform domain, public view, caption CTA, UTM, or proof note is not traceable.
- `open_kpi_backfill` / `blocked_until_public_url`：`python3 tools/promotion_first_batch_kpi_quickstart.py --check`
  Stop: Do not interpret zero KPI values until the analytics source was actually checked.

## Platform Publish Rows

### youtube_shorts · `publish-lt-s01-iris-silence`

- status：`blocked_until_profile_links`
- ready to publish：0
- blocked by：profile links are not all set/live
- schedule：2026-06-15 20:30 Asia/Taipei
- post URL：(pending)
- placeholder：`<REAL_YOUTUBE_SHORTS_URL>`
- public complete / pending / verify：0 / 8 / 0
- proof file：`docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt`
- check：`python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt`
- write：`python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt --proof-note "public URL and analytics source checked YYYY-MM-DD"`
- URL writeback：`python3 tools/promotion_post_writeback.py update --platform youtube_shorts --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-14 --post-url <REAL_YOUTUBE_SHORTS_URL> --proof-note "public URL and analytics source checked 2026-06-14"`
- KPI example：`python3 tools/promotion_post_writeback.py update --platform youtube_shorts --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-14 --post-url <REAL_YOUTUBE_SHORTS_URL> --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "platform analytics checked 2026-06-14"`
- stop：Stop if profile gate is not ready, post URL is still placeholder, caption changes CTA, or platform preview adds commercial claims.

### tiktok · `publish-lt-s01-iris-silence`

- status：`blocked_until_profile_links`
- ready to publish：0
- blocked by：profile links are not all set/live
- schedule：2026-06-15 21:00 Asia/Taipei
- post URL：(pending)
- placeholder：`<REAL_TIKTOK_VIDEO_URL>`
- public complete / pending / verify：0 / 8 / 0
- proof file：`docs/promotion/first-round/proof-tiktok-publish-lt-s01-iris-silence.txt`
- check：`python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-tiktok-publish-lt-s01-iris-silence.txt`
- write：`python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-tiktok-publish-lt-s01-iris-silence.txt --proof-note "public URL and analytics source checked YYYY-MM-DD"`
- URL writeback：`python3 tools/promotion_post_writeback.py update --platform tiktok --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-14 --post-url <REAL_TIKTOK_VIDEO_URL> --proof-note "public URL and analytics source checked 2026-06-14"`
- KPI example：`python3 tools/promotion_post_writeback.py update --platform tiktok --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-14 --post-url <REAL_TIKTOK_VIDEO_URL> --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "platform analytics checked 2026-06-14"`
- stop：Stop if profile gate is not ready, post URL is still placeholder, caption changes CTA, or platform preview adds commercial claims.

### instagram_reels · `publish-lt-s01-iris-silence`

- status：`blocked_until_profile_links`
- ready to publish：0
- blocked by：profile links are not all set/live
- schedule：2026-06-15 21:30 Asia/Taipei
- post URL：(pending)
- placeholder：`<REAL_INSTAGRAM_REEL_URL>`
- public complete / pending / verify：0 / 8 / 0
- proof file：`docs/promotion/first-round/proof-instagram_reels-publish-lt-s01-iris-silence.txt`
- check：`python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-instagram_reels-publish-lt-s01-iris-silence.txt`
- write：`python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-instagram_reels-publish-lt-s01-iris-silence.txt --proof-note "public URL and analytics source checked YYYY-MM-DD"`
- URL writeback：`python3 tools/promotion_post_writeback.py update --platform instagram_reels --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-14 --post-url <REAL_INSTAGRAM_REEL_URL> --proof-note "public URL and analytics source checked 2026-06-14"`
- KPI example：`python3 tools/promotion_post_writeback.py update --platform instagram_reels --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-14 --post-url <REAL_INSTAGRAM_REEL_URL> --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "platform analytics checked 2026-06-14"`
- stop：Stop if profile gate is not ready, post URL is still placeholder, caption changes CTA, or platform preview adds commercial claims.
