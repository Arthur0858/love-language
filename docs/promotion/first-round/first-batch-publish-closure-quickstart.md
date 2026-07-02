# LoveTypes First Batch Publish Closure Quickstart

- 產生日期：2026-07-02
- rows：1
- profile handoff ready：1
- ready / blocked rows：0 / 1
- published / pending rows：1 / 0
- public pending rows：0
- minimum KPI rows：0
- completion ready：0
- issues：0

## Rules

- First-batch publishing stays blocked until profile handoff is open.
- Publish only the first Iris script on active first-round channels. Current active channel: YouTube Shorts.
- Do not write post_url with placeholders, private drafts, scheduled previews, or login-only links.
- After each post URL writeback, refresh daily ops before trusting KPI or weekly review packets.
- KPI interpretation remains blocked until public URL checks and checked-source KPI proof are complete.

## Closure Steps

- `profile_publish_handoff_open` / `complete`：`python3 tools/promotion_profile_publish_handoff.py --check`
  Stop: Do not publish while profile_writeback_complete remains blocked.
- `publish_first_batch_posts` / `blocked_until_profile_gate`：`python3 tools/promotion_first_batch_publish_quickstart.py --check`
  Stop: Publish only rows with readyToPublish=1 and unchanged quiz CTA.
- `writeback_public_post_urls` / `ready_after_publish`：`python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-<platform>-publish-lt-s01-iris-silence.txt --proof-note "<REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified"`
  Stop: Replace <REAL_...> with a real public HTTPS post URL before writeback.
- `verify_public_post_urls` / `ready`：`python3 tools/promotion_public_post_url_checklist.py --check && python3 tools/promotion_post_ops_readiness_pack.py --check`
  Stop: Stop if platform domain, public view, caption CTA, UTM, or proof note is not traceable.
- `open_kpi_backfill` / `ready_after_public_verification`：`python3 tools/promotion_first_batch_kpi_quickstart.py --check`
  Stop: Do not interpret zero KPI values until the analytics source was actually checked.

## Platform Publish Rows

### youtube_shorts · `publish-lt-s01-iris-silence`

- status：`complete`
- ready to publish：0
- blocked by：published
- schedule：2026-06-15 20:30 Asia/Taipei
- post URL：https://www.youtube.com/watch?v=uj9ZwYIKDrE
- placeholder：`<REAL_YOUTUBE_SHORTS_URL>`
- public complete / pending / verify：6 / 0 / 2
- proof file：``
- check：``
- write：`python3 tools/promotion_post_text_import.py add --input  --proof-note "<REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified"`
- URL writeback：`python3 tools/promotion_post_writeback.py update --platform youtube_shorts --task-id publish-lt-s01-iris-silence --status published --published-date 2026-07-02 --post-url <REAL_YOUTUBE_SHORTS_URL> --proof-note "<REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified"`
- KPI example：`python3 tools/promotion_post_writeback.py update --platform youtube_shorts --task-id publish-lt-s01-iris-silence --status published --published-date 2026-07-02 --post-url <REAL_YOUTUBE_SHORTS_URL> --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "<REAL_ANALYTICS_SOURCE_PROOF_NOTE> verified"`
- stop：Stop if profile gate is not ready, post URL is still placeholder, caption changes CTA, or platform preview adds commercial claims.
