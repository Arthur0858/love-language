# LoveTypes First Batch Evidence Matrix

- 產生日期：2026-06-14
- rows：3
- published：0
- blocked until publish：3
- needs public URL evidence：0
- needs KPI source evidence：0
- ready for weekly review：0
- completion ready：0
- issues：0

## Rule

- 先取得真實公開 post URL，再回填 KPI。
- 0 可以是有效 KPI，但必須先檢查來源並留下 proof note。
- 三平台都完成公開 URL、proof note、starter KPI 後，才進週回顧與商品判斷。

## Matrix

### youtube_shorts · `publish-lt-s01-iris-silence`

- status：`blocked_until_publish`
- scheduled：2026-06-15 20:30 Asia/Taipei
- published：0
- post URL：(pending)
- public complete / pending / verify：0 / 8 / 0
- KPI complete / pending / needs source：0 / 3 / 0
- proof：`not_required_yet`
- check：`python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt`
- write：`python3 tools/promotion_post_writeback.py update --platform youtube_shorts --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-14 --post-url <REAL_YOUTUBE_SHORTS_URL> --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "<REAL_ANALYTICS_SOURCE_PROOF_NOTE> verified"`
- next：Publish the platform post, then write back the real HTTPS post URL and proof note.

### tiktok · `publish-lt-s01-iris-silence`

- status：`blocked_until_publish`
- scheduled：2026-06-15 21:00 Asia/Taipei
- published：0
- post URL：(pending)
- public complete / pending / verify：0 / 8 / 0
- KPI complete / pending / needs source：0 / 3 / 0
- proof：`not_required_yet`
- check：`python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-tiktok-publish-lt-s01-iris-silence.txt`
- write：`python3 tools/promotion_post_writeback.py update --platform tiktok --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-14 --post-url <REAL_TIKTOK_VIDEO_URL> --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "<REAL_ANALYTICS_SOURCE_PROOF_NOTE> verified"`
- next：Publish the platform post, then write back the real HTTPS post URL and proof note.

### instagram_reels · `publish-lt-s01-iris-silence`

- status：`blocked_until_publish`
- scheduled：2026-06-15 21:30 Asia/Taipei
- published：0
- post URL：(pending)
- public complete / pending / verify：0 / 8 / 0
- KPI complete / pending / needs source：0 / 3 / 0
- proof：`not_required_yet`
- check：`python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-instagram_reels-publish-lt-s01-iris-silence.txt`
- write：`python3 tools/promotion_post_writeback.py update --platform instagram_reels --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-14 --post-url <REAL_INSTAGRAM_REEL_URL> --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "<REAL_ANALYTICS_SOURCE_PROOF_NOTE> verified"`
- next：Publish the platform post, then write back the real HTTPS post URL and proof note.
