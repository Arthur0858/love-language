# LoveTypes Launch Ops Dashboard

- 產生日期：2026-06-14
- rows：8
- ready areas：1
- blocked areas：6
- hold areas：0
- profile configured：0 / 3
- first batch published：0 / 3
- minimum KPI rows：0
- lead ready routes：0
- issues：0

## Rule

- Use this dashboard for orientation only; individual gates remain authoritative.
- Do not skip profile setup, public post URL verification, or KPI proof notes.
- Empty data mode keeps commerce and winning-content decisions closed.
- Only externally verified platform/profile/post/lead evidence can move a blocked area forward.

## Areas

### master_gate

- status：`profile_setup`
- ready / blocked：6 / 18
- next：Finish three platform profile links, then run profile writeback and refresh ops docs.
- evidence：profile=0/3, first_batch=0/3, kpi_rows=0
- safety：Use master gate as final stage source; do not skip profile_setup.

### profile_setup

- status：`blocked`
- ready / blocked：3 / 3
- next：Set three platform profile links and write back proof.
- evidence：public_ready=3, configured=0, ready_to_writeback=0
- safety：Do not mark set/live without platform evidence.

### first_batch_publish

- status：`blocked`
- ready / blocked：0 / 3
- next：Publish first three posts only after profile gate is ready.
- evidence：complete=0, profile_gate=0
- safety：No placeholder post URLs; keep CTA focused on quiz.

### minimum_kpi

- status：`blocked`
- ready / blocked：0 / 3
- next：Backfill post_url, site_clicks, quiz_starts and quiz_completions after publish.
- evidence：published=0, zero_source_rows=9
- safety：A zero needs a checked source; unknown is not zero.

### lead_ops

- status：`blocked`
- ready / blocked：1 / 3
- next：Use structured request import when real Contact or keepsake emails arrive.
- evidence：real_leads=0, ready_routes=0, story_assets=25
- safety：No raw email in CSV; no offer build without repeated demand.

### weekly_review

- status：`blocked`
- ready / blocked：0 / 7
- next：Keep weekly review on hold until public URLs, KPIs and evidence rows are complete.
- evidence：weekly_ready=0, empty_data=1, evidence_pending=7
- safety：No winning guardian, offer order change, Luna emphasis or affiliate weighting in empty data mode.

### operator_handoff

- status：`blocked`
- ready / blocked：3 / 4
- next：Follow the handoff packet for structured proof imports and do-not-do rules.
- evidence：profile_pending=3, first_batch_pending=3, weekly_ready=0
- safety：Keep external operations evidence-backed.

### next_actions

- status：`ready`
- ready / blocked：6 / 18
- next：Do the current ready actions in order: profile setup, asset readiness, then publish.
- evidence：selected_tasks=3, command_rows=24
- safety：Ready actions do not authorize downstream commerce decisions.
