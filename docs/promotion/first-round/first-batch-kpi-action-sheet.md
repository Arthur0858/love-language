# LoveTypes First Batch KPI Action Sheet

- 產生日期：2026-06-14
- rows：3
- ready：0
- blocked：3
- published：0
- zero source rows：9
- publish action ready：0
- issues：0

## Rule

- 沒有真實公開 post URL 前，不回填 KPI，也不把 0 視為有效數據。
- `site_clicks`、`quiz_starts`、`quiz_completions` 即使是 0，也必須有平台或網站來源確認。
- 三平台最小 KPI 未回填前，不做週決策、商品化、Luna 或聯盟權重調整。

## youtube_shorts · `publish-lt-s01-iris-silence`

- action status：`blocked_until_public_post_url`
- published：`0`
- post URL：(not published)
- minimum KPI：`site_clicks,quiz_starts,quiz_completions`
- zero-source rows：3
- proof note：`platform analytics checked 2026-06-14 for youtube_shorts/publish-lt-s01-iris-silence`
- KPI writeback：`python3 tools/promotion_post_writeback.py update --platform youtube_shorts --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-14 --post-url <REAL_YOUTUBE_SHORTS_URL> --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "platform analytics checked 2026-06-14"`
- blocked by：first-batch post is not published

## tiktok · `publish-lt-s01-iris-silence`

- action status：`blocked_until_public_post_url`
- published：`0`
- post URL：(not published)
- minimum KPI：`site_clicks,quiz_starts,quiz_completions`
- zero-source rows：3
- proof note：`platform analytics checked 2026-06-14 for tiktok/publish-lt-s01-iris-silence`
- KPI writeback：`python3 tools/promotion_post_writeback.py update --platform tiktok --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-14 --post-url <REAL_TIKTOK_VIDEO_URL> --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "platform analytics checked 2026-06-14"`
- blocked by：first-batch post is not published

## instagram_reels · `publish-lt-s01-iris-silence`

- action status：`blocked_until_public_post_url`
- published：`0`
- post URL：(not published)
- minimum KPI：`site_clicks,quiz_starts,quiz_completions`
- zero-source rows：3
- proof note：`platform analytics checked 2026-06-14 for instagram_reels/publish-lt-s01-iris-silence`
- KPI writeback：`python3 tools/promotion_post_writeback.py update --platform instagram_reels --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-14 --post-url <REAL_INSTAGRAM_REEL_URL> --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "platform analytics checked 2026-06-14"`
- blocked by：first-batch post is not published
