# LoveTypes Stage Transition Matrix

- 產生日期：2026-06-23
- current stage：`first_batch_kpi`
- rows：6
- complete rows：2
- current blockers：1
- blocked upstream rows：3
- command rows ready / blocked：2 / 2
- real profile proof ready：0 / 1
- external profile proof blockers：1
- current true blockers：0
- empty data mode：0
- issues：0

## Policy

- Do not skip stages.
- Profile setup must complete before publishing.
- Public post URLs and minimum KPI proof must complete before weekly decisions.
- Lead evidence must be repeated, consented, and traceable before offer experiments.

## Transitions

### `profile_setup` -> `first_batch_publish`

- status：`complete`
- gate：`profile_completion`
- value：1 / 1 `profileConfigured`
- release：All active platform profile rows are set/live with profile_link_set_date and traceable proof.
- next command：`python3 tools/promotion_profile_completion_gate.py --check && python3 tools/promotion_launch_readiness_gate.py --check`
- fallback：Use profile proof import templates; do not publish first batch yet.
- blocker：none

### `first_batch_publish` -> `first_batch_kpi`

- status：`complete`
- gate：`first_batch_publication`
- value：1 / 1 `firstBatchPublished`
- release：First batch has verified HTTPS post URLs written back for all active platforms.
- next command：`python3 tools/promotion_first_batch_completion_gate.py --check`
- fallback：Publish only after profile gate opens; reject placeholder URLs.
- blocker：none

### `first_batch_kpi` -> `weekly_review`

- status：`current_blocker`
- gate：`minimum_kpi`
- value：0 / 1 `firstBatchMinimumKpiRows`
- release：Each active first-batch post has site_clicks, quiz_starts, quiz_completions or checked-zero proof.
- next command：`python3 tools/promotion_weekly_review_packet.py --check && python3 tools/promotion_week_decision_gate.py --check`
- fallback：Keep KPI rows blank until the source was checked; 0 requires proof.
- blocker：minimum KPI rows need checked source proof

### `weekly_review` -> `lead_collection`

- status：`blocked_upstream`
- gate：`weekly_review`
- value：0 / 1 `weeklyReady`
- release：Weekly review is ready and empty-data mode is false before changing route or commerce emphasis.
- next command：`python3 tools/promotion_decision_input_matrix.py --check && python3 tools/promotion_weekly_decision_evidence_checklist.py --check`
- fallback：Keep collect_signal active; do not choose winner, paid CTA, Luna, or affiliate emphasis.
- blocker：weekly review gate is not ready

### `lead_collection` -> `offer_experiment`

- status：`blocked_upstream`
- gate：`lead_demand`
- value：0 / 1 `leadReadyRoutes`
- release：At least one guardian/intake route has repeated real demand, explicit consent, and traceable evidence.
- next command：`python3 tools/promotion_lead_demand_gate.py --check && python3 tools/promotion_offer_experiment_plan.py --check`
- fallback：Keep collecting real requests; do not build paid or priority offers from weak demand.
- blocker：no repeated consented real lead demand route

### `offer_experiment` -> `scale`

- status：`blocked_upstream`
- gate：`offer_experiment`
- value：0 / 1 `readyOfferExperiments`
- release：Offer experiment plan has at least one READY row with matching evidence and safety boundaries.
- next command：`python3 tools/promotion_offer_experiment_queue.py --check && python3 tools/promotion_asset_fulfillment_gate.py --check`
- fallback：Keep offer rows on HOLD; do not add paid CTA to first-touch Shorts.
- blocker：no READY offer experiment
