# LoveTypes First Batch Evidence Matrix

- 產生日期：2026-06-24
- rows：1
- published：1
- blocked until publish：0
- needs public URL evidence：0
- needs KPI source evidence：1
- ready for weekly review：0
- completion ready：0
- issues：0

## Rule

- 先取得真實公開 post URL，再回填 KPI。
- 0 可以是有效 KPI，但必須先檢查來源並留下 proof note。
- 啟用平台都完成公開 URL、proof note、starter KPI 後，才進週回顧與商品判斷。

## Matrix

### youtube_shorts · `publish-lt-s01-iris-silence`

- status：`needs_kpi_source_evidence`
- scheduled：2026-06-15 20:30 Asia/Taipei
- published：1
- post URL：https://www.youtube.com/watch?v=uj9ZwYIKDrE
- public complete / pending / verify：6 / 0 / 2
- KPI complete / pending / needs source：0 / 0 / 3
- proof：`traceable`
- check：`python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt`
- write：`python3 tools/promotion_post_writeback.py update --platform youtube_shorts --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-24 --post-url https://www.youtube.com/watch?v=uj9ZwYIKDrE --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "<REAL_ANALYTICS_SOURCE_PROOF_NOTE> verified"`
- next：Check analytics source before writing zero or positive starter KPI values.
