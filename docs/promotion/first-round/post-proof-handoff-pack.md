# LoveTypes Post Proof Handoff Pack

- 產生日期：2026-07-02
- rows：1
- proof files：1
- ready to import：0
- templates safely rejected：1
- placeholder proof rows：1
- real proof ready rows：0
- blocked until post URL：0
- writeback commands：1
- issues：0

## Rule

- Proof text is the handoff surface between external publishing and local KPI writeback.
- Placeholder proof files must fail the import check until a real public post URL is pasted in.
- Run the check command before the write command for every platform.
- Do not write zero KPI values unless the proof note names the checked analytics source.

## Rows

### youtube_shorts · `publish-lt-s01-iris-silence`

- status：`template_safely_rejected`
- proof：placeholder=1 / real_ready=0
- post ops：`needs_kpi_source_proof`
- proof：`docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt`
- title：他沉默時，你最想聽見哪一句話？
- check：`python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt`
- write：`python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt`
- fallback：`python3 tools/promotion_post_writeback.py update --platform youtube_shorts --task-id publish-lt-s01-iris-silence --status published --published-date 2026-07-02 --post-url https://www.youtube.com/watch?v=uj9ZwYIKDrE --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "<REAL_ANALYTICS_SOURCE_PROOF_NOTE> verified"`
- next：Replace the placeholder post_url and proof_note date, then rerun the check command.
- stop：Stop if the URL is still a placeholder, the platform domain does not match, or zero metrics lack checked-source proof.
