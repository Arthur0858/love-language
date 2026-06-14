# LoveTypes Stage Transition Matrix

- 產生日期：2026-06-14
- current stage：`profile_setup`
- rows：6
- complete rows：0
- current blockers：1
- blocked upstream rows：5
- command rows ready / blocked：3 / 18
- empty data mode：1
- issues：0

## Policy

- Do not skip stages.
- Profile setup must complete before publishing.
- Public post URLs and minimum KPI proof must complete before weekly decisions.
- Lead evidence must be repeated, consented, and traceable before offer experiments.

## Transitions

### `profile_setup` -> `first_batch_publish`

- status：`current_blocker`
- gate：`profile_completion`
- value：0 / 3 `profileConfigured`
- release：All three platform profile rows are set/live with profile_link_set_date and traceable proof.
- next command：`python3 tools/promotion_profile_completion_gate.py --check && python3 tools/promotion_launch_readiness_gate.py --check`
- fallback：Use profile proof import templates; do not publish first batch yet.
- blocker：profile_link_youtube_shorts, profile_link_tiktok, profile_link_instagram_reels

### `first_batch_publish` -> `first_batch_kpi`

- status：`blocked_upstream`
- gate：`first_batch_publication`
- value：0 / 3 `firstBatchPublished`
- release：First batch has three verified HTTPS post URLs written back.
- next command：`python3 tools/promotion_first_batch_completion_gate.py --check`
- fallback：Publish only after profile gate opens; reject placeholder URLs.
- blocker：first batch post URLs are not all verified

### `first_batch_kpi` -> `weekly_review`

- status：`blocked_upstream`
- gate：`minimum_kpi`
- value：0 / 3 `firstBatchMinimumKpiRows`
- release：Each first-batch post has site_clicks, quiz_starts, quiz_completions or checked-zero proof.
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
- blocker：empty data mode is still active

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
