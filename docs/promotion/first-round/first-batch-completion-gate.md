# LoveTypes First Batch Completion Gate

- 產生日期：2026-06-20
- first batch published：0 / 1
- minimum KPI rows：0 / 1
- traceable post evidence：0 / 0
- generic / missing evidence：0 / 0
- ready for weekly review：0
- blockers：2
- issues：0

## Required Minimum KPI

- `site_clicks`
- `quiz_starts`
- `quiz_completions`

## State

- firstBatchPublished：`0`
- evidenceComplete：`1`
- minimumKpiComplete：`0`
- publishingStatusReady：`0`
- emptyDataMode：`1`

## Next Action

- Publish first-batch posts, write back real post URLs, then fill or verified-zero minimum KPI.

## Blockers

- `first_batch_not_published`：published rows 0/1; publish each platform post and write back post_url. 解除條件：All first-batch rows are marked published/live/posted with real post_url values.
- `minimum_kpi_not_backfilled`：minimum KPI rows 0/1; fill or verified-zero site_clicks, quiz_starts, quiz_completions. 解除條件：Every first-batch platform row has checked minimum KPI values.
