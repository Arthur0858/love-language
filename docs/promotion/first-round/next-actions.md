# LoveTypes 下一批推廣動作建議

- 產生日期：2026-07-18
- 影片追蹤列數：1
- 平台首頁待設定列數：0 / 1
- Profile proof ready / blocked：1 / 0
- Post proof ready / blocked：1 / 0
- 空資料安全模式：否
- 行動選擇規則：When profile links are pending, finish platform profile setup first; then select the first three planned tasks by week and slot and keep Shorts CTA focused on the 15-question quiz.
- 商品調整 gate：Do not change products, guardian priority, paid CTA, Luna emphasis, or affiliate emphasis until filled KPI rows create quiz, route, lead, Luna, or affiliate intent.

## 優先動作

- [medium] 目前數據不足以調整策略，先補足回填並維持原排程。

## Proof Control

### `prepare_profile_proofs`

- status：`complete`
- command：`python3 tools/promotion_profile_batch_import.py --check`
- release：profile batch readyRows is 1.

### `write_profile_batch`

- status：`complete`
- command：`python3 tools/promotion_profile_batch_import.py --add`
- release：master gate moves from profile_setup to first_batch_publish.

### `prepare_post_proofs`

- status：`complete`
- command：`python3 tools/promotion_post_batch_import.py --check`
- release：post batch readyRows is 1.

### `write_post_batch`

- status：`complete`
- command：`python3 tools/promotion_post_batch_import.py --add`
- release：first batch has 1 published rows and minimum KPI rows.

### `refresh_and_review`

- status：`blocked_until_post_writeback`
- command：`python3 tools/promotion_daily_ops_refresh.py && python3 tools/promotion_launch_sequence_dry_run.py`
- release：dry run stays green and weekly evidence gate can open.

Proof rows:

- `profile` / `youtube_shorts`：`ready` ready=1 file=`docs/promotion/first-round/proof-youtube_shorts.txt`
- `post` / `youtube_shorts`：`ready` ready=1 file=`docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt`


## 平台首頁設定

- 平台首頁追蹤列已設定，下一步看 profile_clicks、site_clicks、quiz_starts、quiz_completions。

## 建議發布任務

### publish-lt-s01-iris-silence

- Week/Slot：1 / 1
- 守護者：艾莉絲（iris）
- 內容角度：情感錯頻情境
- 標題：他沉默時，你最想聽見哪一句話？
- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence
- 免費資產：free-keepsake-iris
- 名單承接：supply-wishlist-iris
- 補給路線：https://lovetypes.tw/resources/#supply-iris
- Luna：https://lovetypes.tw/luna-yoga-music/#luna-iris
- 收藏物：https://lovetypes.tw/keepsakes/#keepsake-iris

### publish-lt-s02-iris-affirmation

- Week/Slot：1 / 2
- 守護者：艾莉絲（iris）
- 內容角度：守護者人格認同
- 標題：哪一句肯定，會讓你瞬間安心？
- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_affirmation
- 免費資產：free-keepsake-iris
- 名單承接：supply-wishlist-iris
- 補給路線：https://lovetypes.tw/resources/#supply-iris
- Luna：https://lovetypes.tw/luna-yoga-music/#luna-iris
- 收藏物：https://lovetypes.tw/keepsakes/#keepsake-iris

### publish-lt-s03-iris-too-sensitive

- Week/Slot：1 / 3
- 守護者：艾莉絲（iris）
- 內容角度：測驗入口
- 標題：你真的太敏感嗎？還是你只是等一句清楚的話？
- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_too_sensitive
- 免費資產：free-keepsake-iris
- 名單承接：supply-wishlist-iris
- 補給路線：https://lovetypes.tw/resources/#supply-iris
- Luna：https://lovetypes.tw/luna-yoga-music/#luna-iris
- 收藏物：https://lovetypes.tw/keepsakes/#keepsake-iris

## 安全邊界

- Shorts CTA 維持測驗，不直接導購。
- 平台首頁 Bio/Profile link 也維持測驗，不直接導購。
- 不把守護者結果描述成診斷、療效或保證修復。
- 空資料時不調整商品、守護者優先序或付費 CTA。
