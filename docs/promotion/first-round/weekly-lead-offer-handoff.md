# LoveTypes Weekly to Lead and Offer Handoff

- 產生日期：2026-06-18
- rows：8
- complete rows：2
- current blockers：1
- blocked upstream rows：5
- real leads：0
- ready lead routes：0
- public free assets ready：5
- ready offer experiments：0
- issues：0

## Rule

- Weekly review must open before lead, asset, Luna, affiliate, or offer decisions.
- Real lead demand requires explicit consent, traceable proof, and repeated same-guardian signal.
- Free public assets may stay available, but they are not proof of product demand.
- Paid or priority offer experiments require READY plan and queue rows.

## Handoff Steps

### `weekly_review_open`

- phase：`weekly_review`
- status：`current_blocker`
- value：0 / 1
- action：Start lead and offer evaluation only after publish/KPI handoff opens weekly review.
- evidence：publish-kpi-handoff readyForWeeklyReview is true.
- command：`python3 tools/promotion_publish_kpi_handoff.py --check`
- stop：Do not evaluate lead or offer routes while post URLs or minimum KPI proof are incomplete.

### `weekly_decision_ready`

- phase：`weekly_review`
- status：`blocked_upstream`
- value：1 / 3
- action：Confirm weekly review, week decision gate, and non-empty data mode before route decisions.
- evidence：weekly review ready=1, weeklyDecision gate=1, emptyDataMode=0.
- command：`python3 tools/promotion_weekly_review_packet.py --check && python3 tools/promotion_week_decision_gate.py --check`
- stop：Do not pick winners or change commerce order while empty data mode is true.

### `weekly_evidence_complete`

- phase：`weekly_review`
- status：`blocked_upstream`
- value：2 / 8
- action：Complete weekly evidence checks before choosing content, asset, Luna, or affiliate direction.
- evidence：weekly-decision-evidence-checklist completeRows equals rows.
- command：`python3 tools/promotion_weekly_decision_evidence_checklist.py --check`
- stop：Stop if any weekly decision evidence row remains pending.

### `lead_capture_ready`

- phase：`lead_collection`
- status：`complete`
- value：1 / 1
- action：Keep Contact, keepsake, and Luna requests importable before using them as lead signals.
- evidence：lead ops action sheet has ready capture checks and lead magnet inventory issues=0.
- command：`python3 tools/promotion_lead_ops_action_sheet.py --check`
- stop：Do not collect raw sensitive content or use requests without explicit reply consent.

### `lead_demand_ready`

- phase：`lead_collection`
- status：`blocked_upstream`
- value：0 / 1
- action：Advance to owned assets or Luna only after repeated same-guardian demand creates a ready route.
- evidence：lead-demand-gate readyRoutes >= 1 with traceable evidence and explicit consent.
- command：`python3 tools/promotion_lead_demand_gate.py --check`
- stop：Do not create paid or priority assets from a single request, weak signal, or no consent.

### `asset_fulfillment_ready`

- phase：`asset_fulfillment`
- status：`blocked_upstream`
- value：0 / 1
- action：Prepare only the smallest matching free asset or Luna aftercare item for proven demand.
- evidence：asset-fulfillment-gate has at least one ready demand pair or ready offer asset.
- command：`python3 tools/promotion_asset_fulfillment_gate.py --check`
- stop：Keep public free assets available, but do not build custom products before demand proof.

### `offer_experiment_ready`

- phase：`offer_experiment`
- status：`blocked_upstream`
- value：0 / 1
- action：Only run low-risk offer experiments when both plan and queue have READY rows.
- evidence：offer-experiment-plan and offer-experiment-queue both have at least one READY row.
- command：`python3 tools/promotion_offer_experiment_plan.py --check && python3 tools/promotion_offer_experiment_queue.py --check`
- stop：Do not add paid CTA to Shorts or claim diagnosis, therapy, guarantee, or required purchase.

### `public_free_assets_remain_safe`

- phase：`safety`
- status：`complete`
- value：1 / 1
- action：Keep five public free assets as safe lead magnets while real demand is absent.
- evidence：asset-fulfillment-gate publicFreeReady >= 5 and lead-demand-gate has no repeated route.
- command：`python3 tools/promotion_asset_fulfillment_gate.py --check && python3 tools/promotion_lead_demand_gate.py --check`
- stop：Stop if public free assets are treated as proof of product demand without tracked requests.
