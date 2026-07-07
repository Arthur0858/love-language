# LoveTypes First Batch KPI Action Sheet

- 產生日期：2026-07-07
- rows：1
- ready：1
- blocked：0
- published：1
- zero source rows：3
- publish action ready：0
- issues：0

## Rule

- 沒有真實公開 post URL 前，不回填 KPI，也不把 0 視為有效數據。
- `site_clicks`、`quiz_starts`、`quiz_completions` 即使是 0，也必須有平台或網站來源確認。
- 啟用平台的最小 KPI 未回填前，不做週決策、商品化、Luna 或聯盟權重調整。

## youtube_shorts · `publish-lt-s01-iris-silence`

- action status：`ready_for_kpi_source_check`
- published：`1`
- post URL：https://www.youtube.com/watch?v=uj9ZwYIKDrE
- minimum KPI：`site_clicks,quiz_starts,quiz_completions`
- zero-source rows：3
- proof note：`<REAL_ANALYTICS_SOURCE_PROOF_NOTE> verified`
- KPI writeback：`python3 tools/promotion_post_writeback.py update --platform youtube_shorts --task-id publish-lt-s01-iris-silence --status published --published-date 2026-07-07 --post-url https://www.youtube.com/watch?v=uj9ZwYIKDrE --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "<REAL_ANALYTICS_SOURCE_PROOF_NOTE> verified"`
