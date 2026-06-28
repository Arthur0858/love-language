# LoveTypes Weekly Review Quickstart

- 產生日期：2026-06-29
- action rows：7
- ready / blocked / hold rows：2 / 3 / 2
- evidence complete / pending：4 / 4
- weekly ready：0
- decision ready：0
- empty data mode：0
- issues：0

## Rules

- Weekly review starts only after profile links, public post URLs, and minimum KPI source checks are complete.
- If empty data mode is active, keep all commerce and prioritization decisions on HOLD.
- Do not rank guardians, change offer order, increase paid CTA, or prioritize Luna/affiliate from zero or missing data.
- Use weekly summary, week decision gate, and decision readiness checklist as the decision source of truth.
- Lead and offer work requires repeated route or lead demand, not template rows or one-off clicks.

## Actions

### `profile-before-review`

- phase：`precondition`
- status：`ready`
- action：Confirm all platform profile links are set/live before using first-batch posts for weekly review.
- command：`python3 tools/promotion_profile_completion_gate.py --check && python3 tools/promotion_profile_link_readiness_packet.py --check`
- evidence：profile_configured=3 and profile gate ready before publish/review.
- boundary：Without profile links, do not treat missing clicks as content failure.

### `first-batch-public-url`

- phase：`publish`
- status：`blocked`
- action：Publish or verify the first YouTube Shorts post and record the real public post URL.
- command：`python3 tools/promotion_first_batch_publish_action_sheet.py --check`
- evidence：Three real platform post_url values, not placeholders.
- boundary：No public URL means no weekly decision.

### `minimum-kpi-backfill`

- phase：`kpi`
- status：`ready_to_backfill`
- action：Backfill site_clicks, quiz_starts and quiz_completions for each published first-batch post.
- command：`python3 tools/promotion_first_batch_kpi_action_sheet.py --check`
- evidence：Each 0 value has a checked platform or site source, not an assumption.
- boundary：Zero without source is still unknown.

### `weekly-evidence-check`

- phase：`review`
- status：`blocked`
- action：Run the weekly decision evidence checklist and require all evidence rows to complete before ranking content.
- command：`python3 tools/promotion_weekly_decision_evidence_checklist.py --check`
- evidence：complete=4, pending=4.
- boundary：Pending evidence keeps all commerce and winner decisions on HOLD.

### `weekly-review-packet`

- phase：`review`
- status：`hold`
- action：Regenerate weekly summary, decision gate and review packet before changing the next content batch.
- command：`python3 tools/promotion_weekly_summary.py && python3 tools/promotion_week_decision_gate.py && python3 tools/promotion_weekly_review_packet.py`
- evidence：weekly_ready=0, empty_data=0.
- boundary：Empty data mode allows only setup, publish, and KPI backfill actions.

### `lead-and-offer-safety`

- phase：`commerce`
- status：`blocked`
- action：Check lead demand before building owned assets, Luna packs or paid offer experiments.
- command：`python3 tools/promotion_lead_ops_action_sheet.py --check && python3 tools/promotion_lead_demand_gate.py --check`
- evidence：lead_ready_routes=0, repeated_routes=0.
- boundary：No repeated lead demand means no paid or priority offer build.

### `allowed-decision-scope`

- phase：`decision`
- status：`hold`
- action：Use week-decision-gate as the only source of truth for allowed next decisions.
- command：`python3 tools/promotion_week_decision_gate.py --check`
- evidence：weeklyDecision=0, testSoftOffer=0.
- boundary：Do not alter offer order, guardian priority, Luna emphasis, or affiliate weighting unless gate allows it.

## Evidence Checklist

- [ ] `profiles_configured`：All active platform profile links are set/live with traceable evidence.（pending；啟用平台 profile 尚未全部 set/live。）
- [x] `first_batch_published`：First-batch posts are published on all active platforms.（complete；證據已滿足。）
- [x] `public_post_urls_verified`：Every public post URL has platform domain, public view, CTA, UTM, and proof evidence checked.（complete；證據已滿足。）
- [ ] `zero_kpis_have_source`：Zero values for site_clicks, quiz_starts, and quiz_completions have checked-source proof.（pending；核心 KPI 仍未發布、未回填，或 0 值缺來源證據。）
- [ ] `weekly_review_ready`：Weekly review packet reports readyForWeeklyDecision=1.（pending；weekly review 尚未達可決策狀態。）
- [x] `not_empty_data_mode`：Empty data mode is false before commerce or prioritization decisions.（complete；證據已滿足。）
- [ ] `decision_gate_ready`：Week decision gate allows at least weeklyDecision before changing content or commerce paths.（pending；week decision gate 仍是 HOLD。）
- [x] `commerce_changes_still_blocked`：Paid CTA, Luna emphasis, affiliate emphasis, and offer order remain blocked until intent exists.（complete；證據已滿足。）

## Blocked Decisions

- `change_offer_order`
- `pick_winning_guardian`
- `increase_paid_cta`
- `prioritize_luna_or_affiliate`
- `build_paid_product_from_empty_data`
