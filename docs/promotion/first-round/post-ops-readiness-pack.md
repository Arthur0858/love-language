# LoveTypes Post Ops Readiness Pack

- 產生日期：2026-07-02
- rows：1
- published：1
- blocked：0
- needs public verification：0
- needs KPI source proof：1
- ready for weekly review：0
- public pending rows：0
- zero KPI pending rows：0
- issues：0

## Rule

- Post URL writeback comes before KPI interpretation.
- A placeholder URL must never pass public URL verification.
- Zero KPI values are valid only with checked-source proof.
- Weekly review stays closed until all active first-batch rows pass URL and KPI evidence checks.

## Rows

### youtube_shorts · `publish-lt-s01-iris-silence`

- status：`needs_kpi_source_proof`
- script：`lt-s01-iris-silence`
- title：他沉默時，你最想聽見哪一句話？
- published：1
- post URL：https://www.youtube.com/watch?v=uj9ZwYIKDrE
- public complete / pending / verify：6 / 0 / 2
- zero complete / pending / needs source：0 / 0 / 3
- next：Attach checked-source proof for site_clicks, quiz_starts and quiz_completions.
- KPI command：`python3 tools/promotion_post_writeback.py update --platform youtube_shorts --task-id publish-lt-s01-iris-silence --status published --published-date 2026-07-02 --post-url https://www.youtube.com/watch?v=uj9ZwYIKDrE --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "<REAL_ANALYTICS_SOURCE_PROOF_NOTE> verified"`
