# LoveTypes Launch Blocker Digest

- 產生日期：2026-06-28
- current stage：`kpi_backfill`
- first blocker：`backfill_first_batch_kpis`
- profile configured：1 / 1
- real profile proof ready：0 / 1
- external profile proof blockers：0
- current true blockers：0
- first batch published：1 / 1
- filled KPI rows：0
- active blockers：7
- ready now：1
- empty data mode：1
- issues：0

## Next Action

- action：Backfill source-checked site_clicks, quiz_starts, and quiz_completions for the first batch.
- command：`python3 tools/promotion_post_text_import.py add --input <post-proof.txt> --proof-note "public URL and KPI source checked YYYY-MM-DD"`
- release：filled KPI rows cover the first batch or source-checked zeros are recorded

## First Blocker

- phase：`measurement`
- severity：`decision_blocker`
- message：KPI 尚未回填到前 1 筆；保持測驗 CTA，不調整商品、Luna 或聯盟權重。

## Allowed Now

- Backfill source-checked site_clicks, quiz_starts, and quiz_completions for the first batch.
- Refresh daily ops packets after any writeback.

## Do Not Do

- Do not publish first-batch posts before all profile rows are set/live.
- Do not mark posts published without real public post URLs.
- Do not fill KPI values from guesses or placeholders.
- Do not change Luna, affiliate, paid offer, or guardian winner decisions while empty_data_mode=1.

## Evidence Snapshot

- command ready / prepared / blocked：2 / 2 / 2
- profile completion blockers：0
- profile placeholder proof rows：1
- weekly ready：0
- KPI posting / platform / script rows：15 / 15 / 15
- attribution rows：16
