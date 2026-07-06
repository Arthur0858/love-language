# LoveTypes Post Writeback Playbook

- 產生日期：2026-07-06
- 已發布列：1 / 15
- issues：0
- 原則：只有平台貼文已公開且 post URL 可驗證時，才能標記 published/live/posted。

## 首批回填命令

### youtube_shorts · `publish-lt-s01-iris-silence`

- script：`lt-s01-iris-silence`
- 標題：他沉默時，你最想聽見哪一句話？
- 目前狀態：`published`
- 回填：`python3 tools/promotion_post_writeback.py update --platform youtube_shorts --task-id publish-lt-s01-iris-silence --status published --published-date 2026-07-06 --post-url <REAL_YOUTUBE_SHORTS_URL> --proof-note "<REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified"`

## 平台文字匯入

- 發布後可把平台、task_id、post_url、發布日期與初始 KPI 貼成一段文字，再用匯入工具檢查。
- 檢查：`python3 tools/promotion_post_text_import.py check --input /path/to/post.txt`
- 寫入：`python3 tools/promotion_post_text_import.py add --input /path/to/post.txt --proof-note "<REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified"`
- 寫入時仍會同步 posting queue、platform KPI tracker、script KPI tracker 與後續摘要文件。

## 安全規則

- 不用本工具偽造 post URL、發布日期或 KPI。
- `published/live/posted` 必須有 `--published-date`、`--post-url`、`--proof-note`。
- 發布後先回填 `site_clicks`、`quiz_starts`、`quiz_completions`；填 0 前必須在 proof note 寫明 analytics/source 已檢查。
