# LoveTypes First Batch Publish Action Sheet

- 產生日期：2026-06-18
- rows：1
- ready：1
- blocked：0
- complete：0
- profile links public ready：1
- profile gate ready：1
- issues：0

## Rule

- 啟用平台 profile link 都 set/live 且 gate ready 前，不發布首批貼文。
- 發布後必須先用 proof text import `check` 驗證，再用 `add` 回填真實 post URL。
- KPI 只能填平台或網站來源確認後的值；0 也必須是確認後的 0。

## youtube_shorts · `publish-lt-s01-iris-silence`

- action status：`ready_to_publish`
- scheduled：2026-06-15 20:30 Asia/Taipei
- title：他沉默時，你最想聽見哪一句話？
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence
- proof file：`docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt`
- check：`python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt`
- write：`python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt --proof-note "<REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified"`

Caption:

```text
你不是想聽甜言蜜語，你只是想確認自己有沒有被看見。

Take the 15-question quiz to find your emotional guardian: https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence

留言 A/B/C，或寫下一句你最想被說出口的話。
#LoveLanguages #RelationshipQuiz #EmotionalGuardian #HeartLanguage #LoveTypes
```
