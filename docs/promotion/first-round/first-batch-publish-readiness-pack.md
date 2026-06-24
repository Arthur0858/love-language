# LoveTypes First Batch Publish Readiness Pack

- 產生日期：2026-06-25
- rows：1
- profile gate ready：1
- asset QA prepared：1
- ready to publish：0
- blocked：0
- published：1
- proof templates safely rejected：1
- proof placeholder rows：1
- proof real ready rows：0
- issues：0

## Rule

- Asset QA prepared does not authorize publishing until profile gate is ready.
- Post proof templates must remain safely rejected while post_url is a placeholder.
- Only real public post URLs may move a row from blocked/ready to published.
- After publish, backfill minimum KPI with checked-source zeros or real values.

## Rows

### youtube_shorts · `publish-lt-s01-iris-silence`

- status：`published`
- script：`lt-s01-iris-silence`
- guardian：`iris`
- title：他沉默時，你最想聽見哪一句話？
- schedule：2026-06-15 20:30 Asia/Taipei
- profile gate ready：1
- asset QA prepared：1
- publish action status：`complete`
- post URL ready：1
- post proof file：`docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt`
- proof template safely rejected：1
- proof：placeholder=1 / real_ready=0
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence
- stop：Stop if profile gate is not ready, post URL is still placeholder, caption changes CTA, or platform preview adds commercial claims.
