# LoveTypes First Batch Publish Quickstart

- 產生日期：2026-06-27
- rows：1
- ready to publish：1
- ready / blocked rows：0 / 1
- profile handoff ready：1
- action ready：0
- readiness blocked：0
- issues：0

## Rules

- Use this packet only after profile-publish handoff opens.
- Do not publish while any row remains blocked_until_profile_links or blocked_until_profile_gate.
- Replace the post URL placeholder with the real public HTTPS URL before writeback.
- Keep the CTA focused on the 15-question guardian quiz.
- Do not add paid, affiliate, diagnosis, treatment, or guaranteed-repair claims.

## youtube_shorts · `publish-lt-s01-iris-silence`

- readiness：`published`
- action status：`complete`
- ready to publish：`0`
- blocked by：published
- script：`lt-s01-iris-silence`
- guardian：`iris`
- title：他沉默時，你最想聽見哪一句話？
- scheduled：2026-06-15 20:30 Asia/Taipei
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence
- proof file：``

Caption:

```text
你不是想聽甜言蜜語，你只是想確認自己有沒有被看見。

Take the 15-question quiz to find your emotional guardian: https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence

留言 A/B/C，或寫下一句你最想被說出口的話。
#LoveLanguages #RelationshipQuiz #EmotionalGuardian #HeartLanguage #LoveTypes
```

Proof text to save after the post is public:

```text
LoveTypes platform post writeback
platform: youtube_shorts
task_id: publish-lt-s01-iris-silence
status: published
published_date: 2026-06-27
post_url: <REAL_YOUTUBE_SHORTS_URL>
views: 0
site_clicks: 0
quiz_starts: 0
quiz_completions: 0
proof_note: <REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified
```

- check：``
- write：`python3 tools/promotion_post_text_import.py add --input  --proof-note "<REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified"`
- stop：Stop if profile gate is not ready, post URL is still placeholder, caption changes CTA, or platform preview adds commercial claims.
