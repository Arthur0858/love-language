# LoveTypes Post Writeback Playbook

- 產生日期：2026-06-13
- 已發布列：0 / 45
- issues：0
- 原則：只有平台貼文已公開且 post URL 可驗證時，才能標記 published/live/posted。

## 首批回填命令

### youtube_shorts · `publish-lt-s01-iris-silence`

- script：`lt-s01-iris-silence`
- 標題：他沉默時，你最想聽見哪一句話？
- 目前狀態：`planned`
- 回填：`python3 tools/promotion_post_writeback.py update --platform youtube_shorts --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-13 --post-url https://example.com/post --proof-note "manual post URL verified"`

### tiktok · `publish-lt-s01-iris-silence`

- script：`lt-s01-iris-silence`
- 標題：他沉默時，你最想聽見哪一句話？
- 目前狀態：`planned`
- 回填：`python3 tools/promotion_post_writeback.py update --platform tiktok --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-13 --post-url https://example.com/post --proof-note "manual post URL verified"`

### instagram_reels · `publish-lt-s01-iris-silence`

- script：`lt-s01-iris-silence`
- 標題：他沉默時，你最想聽見哪一句話？
- 目前狀態：`planned`
- 回填：`python3 tools/promotion_post_writeback.py update --platform instagram_reels --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-13 --post-url https://example.com/post --proof-note "manual post URL verified"`

## 安全規則

- 不用本工具偽造 post URL、發布日期或 KPI。
- `published/live/posted` 必須有 `--published-date`、`--post-url`、`--proof-note`。
- 發布後先回填 `site_clicks`、`quiz_starts`、`quiz_completions`；沒有數據時保留空白，不做商品判斷。
