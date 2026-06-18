# LoveTypes Launch Blocker Digest

- 產生日期：2026-06-18
- current stage：`first_batch_publish`
- first blocker：`publish_first_batch`
- profile configured：1 / 1
- real profile proof ready：0 / 1
- external profile proof blockers：0
- current true blockers：0
- first batch published：0 / 1
- filled KPI rows：0
- active blockers：8
- ready now：1
- empty data mode：1
- issues：0

## Next Action

- action：Publish the active first-batch platform post and write back the real public post URL.
- command：`python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-<platform>-<task>.txt --proof-note "<REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified"`
- release：first-batch post_url values exist for all active platforms

## First Blocker

- phase：`publish`
- severity：`measurement_blocker`
- message：首批 1 個平台貼文尚未全部標記 published；沒有 post_url 前不能開始 KPI 判讀。

## Allowed Now

- Publish the active first-batch platform post and write back the real public post URL.
- Refresh daily ops packets after any writeback.

## Do Not Do

- Do not publish first-batch posts before all profile rows are set/live.
- Do not mark posts published without real public post URLs.
- Do not fill KPI values from guesses or placeholders.
- Do not change Luna, affiliate, paid offer, or guardian winner decisions while empty_data_mode=1.

## Evidence Snapshot

- command ready / prepared / blocked：3 / 3 / 3
- profile completion blockers：0
- profile placeholder proof rows：1
- weekly ready：0
- KPI posting / platform / script rows：15 / 15 / 15
- attribution rows：16
