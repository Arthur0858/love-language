# LoveTypes Launch Ops Dashboard

- 產生日期：2026-06-22
- rows：11
- ready areas：4
- actionable areas：0
- blocked areas：6
- hold areas：0
- profile configured：1 / 3
- real profile proof ready：0 / 1
- external profile proof blockers：1
- current true blockers：0
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

- status：`first_batch_publish`
- ready / blocked：3 / 3
- next：Publish the first-batch YouTube Short and write back the real public post URL.
- evidence：profile=1/1, first_batch=0, kpi_rows=0
- safety：Use master gate as final stage source; do not skip profile_setup.

### profile_setup

- status：`ready`
- ready / blocked：0 / 0
- next：Set active platform profile links and write back proof.
- evidence：public_ready=1, configured=1, real_proof=0/1, ready_to_writeback=0
- safety：Do not mark set/live without real screenshot or click proof from the platform.

### first_batch_publish

- status：`ready`
- ready / blocked：1 / 0
- next：Publish first-batch posts only after profile gate is ready.
- evidence：complete=0, profile_gate=1
- safety：No placeholder post URLs; keep CTA focused on quiz.

### minimum_kpi

- status：`blocked`
- ready / blocked：0 / 1
- next：Backfill post_url, site_clicks, quiz_starts and quiz_completions after publish.
- evidence：published=0, zero_source_rows=3
- safety：A zero needs a checked source; unknown is not zero.

### lead_ops

- status：`blocked`
- ready / blocked：1 / 3
- next：Use structured request import when real Contact or keepsake emails arrive.
- evidence：real_leads=0, ready_routes=0, story_assets=25
- safety：No raw email in CSV; no offer build without repeated demand.

### weekly_review

- status：`blocked`
- ready / blocked：2 / 5
- next：Keep weekly review on hold until public URLs, KPIs and evidence rows are complete.
- evidence：weekly_ready=0, empty_data=0, evidence_pending=6
- safety：No winning guardian, offer order change, Luna emphasis or affiliate weighting in empty data mode.

### operator_handoff

- status：`blocked`
- ready / blocked：1 / 1
- next：Follow the handoff packet for structured proof imports and do-not-do rules.
- evidence：profile_pending=0, first_batch_pending=1, weekly_ready=0
- safety：Keep external operations evidence-backed.

### profile_publish_handoff

- status：`ready`
- ready / blocked：10 / 0
- next：Use this gate to hand off completed profile proof into first-batch publishing.
- evidence：ready_to_publish=1, current_blockers=0, blocked_upstream=0
- safety：No first-batch publishing until profile proof and refreshed packets are complete.

### publish_kpi_handoff

- status：`blocked`
- ready / blocked：2 / 5
- next：Use this gate to hand off public post URLs and minimum KPI into weekly review.
- evidence：published=0, minimum_kpi=0, weekly=0
- safety：No weekly review or commerce decision until post URL, proof, and KPI checks are complete.

### weekly_lead_offer_handoff

- status：`blocked`
- ready / blocked：2 / 6
- next：Use this gate to move weekly signals into lead, asset, Luna, or offer work only when evidence exists.
- evidence：real_leads=0, ready_routes=0, ready_offers=0
- safety：Public free assets are safe lead magnets, not proof of product demand.

### next_actions

- status：`ready`
- ready / blocked：3 / 3
- next：Only profile setup is currently actionable; publishing remains blocked until profile proof is written back.
- evidence：selected_tasks=3, command_rows=10
- safety：A next-actions packet can include blocked downstream work; follow status and master gate before acting.
