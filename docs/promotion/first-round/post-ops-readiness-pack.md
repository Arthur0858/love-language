# LoveTypes Post Ops Readiness Pack

- 產生日期：2026-06-14
- rows：3
- published：0
- blocked：3
- needs public verification：0
- needs KPI source proof：0
- ready for weekly review：0
- public pending rows：24
- zero KPI pending rows：9
- issues：0

## Rule

- Post URL writeback comes before KPI interpretation.
- A placeholder URL must never pass public URL verification.
- Zero KPI values are valid only with checked-source proof.
- Weekly review stays closed until all three first-batch rows pass URL and KPI evidence checks.

## Rows

### youtube_shorts · `publish-lt-s01-iris-silence`

- status：`blocked_until_post_url`
- script：`lt-s01-iris-silence`
- title：他沉默時，你最想聽見哪一句話？
- published：0
- post URL：(pending)
- public complete / pending / verify：0 / 8 / 0
- zero complete / pending / needs source：0 / 3 / 0
- next：Publish the post and replace the placeholder URL with a real public post URL.
- KPI command：`python3 tools/promotion_post_writeback.py update --platform youtube_shorts --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-14 --post-url <REAL_YOUTUBE_SHORTS_URL> --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "<REAL_ANALYTICS_SOURCE_PROOF_NOTE> verified"`

### tiktok · `publish-lt-s01-iris-silence`

- status：`blocked_until_post_url`
- script：`lt-s01-iris-silence`
- title：他沉默時，你最想聽見哪一句話？
- published：0
- post URL：(pending)
- public complete / pending / verify：0 / 8 / 0
- zero complete / pending / needs source：0 / 3 / 0
- next：Publish the post and replace the placeholder URL with a real public post URL.
- KPI command：`python3 tools/promotion_post_writeback.py update --platform tiktok --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-14 --post-url <REAL_TIKTOK_VIDEO_URL> --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "<REAL_ANALYTICS_SOURCE_PROOF_NOTE> verified"`

### instagram_reels · `publish-lt-s01-iris-silence`

- status：`blocked_until_post_url`
- script：`lt-s01-iris-silence`
- title：他沉默時，你最想聽見哪一句話？
- published：0
- post URL：(pending)
- public complete / pending / verify：0 / 8 / 0
- zero complete / pending / needs source：0 / 3 / 0
- next：Publish the post and replace the placeholder URL with a real public post URL.
- KPI command：`python3 tools/promotion_post_writeback.py update --platform instagram_reels --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-14 --post-url <REAL_INSTAGRAM_REEL_URL> --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "<REAL_ANALYTICS_SOURCE_PROOF_NOTE> verified"`
