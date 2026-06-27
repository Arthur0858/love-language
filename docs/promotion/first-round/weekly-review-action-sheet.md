# LoveTypes Weekly Review Action Sheet

- 產生日期：2026-06-27
- rows：7
- ready rows：2
- blocked rows：3
- hold rows：2
- weekly ready：0
- empty data：0
- evidence pending：4
- issues：0

## Rule

- Weekly review is not a commerce decision until public URLs, minimum KPIs and evidence rows are complete.
- Empty data mode fails closed: keep setup, publishing and KPI backfill only.
- Do not pick a winning guardian, change offer order or increase paid CTA from zero or missing data.
- Lead and offer experiments require repeated guardian demand, not a single click or template row.

## Actions

### profile-before-review

- phase：`precondition`
- status：`ready`
- action：Confirm all platform profile links are set/live before using first-batch posts for weekly review.
- command：`python3 tools/promotion_profile_completion_gate.py --check && python3 tools/promotion_profile_link_readiness_packet.py --check`
- evidence：profile_configured=3 and profile gate ready before publish/review.
- boundary：Without profile links, do not treat missing clicks as content failure.

### first-batch-public-url

- phase：`publish`
- status：`blocked`
- action：Publish or verify the first YouTube Shorts post and record the real public post URL.
- command：`python3 tools/promotion_first_batch_publish_action_sheet.py --check`
- evidence：Three real platform post_url values, not placeholders.
- boundary：No public URL means no weekly decision.

### minimum-kpi-backfill

- phase：`kpi`
- status：`ready_to_backfill`
- action：Backfill site_clicks, quiz_starts and quiz_completions for each published first-batch post.
- command：`python3 tools/promotion_first_batch_kpi_action_sheet.py --check`
- evidence：Each 0 value has a checked platform or site source, not an assumption.
- boundary：Zero without source is still unknown.

### weekly-evidence-check

- phase：`review`
- status：`blocked`
- action：Run the weekly decision evidence checklist and require all evidence rows to complete before ranking content.
- command：`python3 tools/promotion_weekly_decision_evidence_checklist.py --check`
- evidence：complete=4, pending=4.
- boundary：Pending evidence keeps all commerce and winner decisions on HOLD.

### weekly-review-packet

- phase：`review`
- status：`hold`
- action：Regenerate weekly summary, decision gate and review packet before changing the next content batch.
- command：`python3 tools/promotion_weekly_summary.py && python3 tools/promotion_week_decision_gate.py && python3 tools/promotion_weekly_review_packet.py`
- evidence：weekly_ready=0, empty_data=0.
- boundary：Empty data mode allows only setup, publish, and KPI backfill actions.

### lead-and-offer-safety

- phase：`commerce`
- status：`blocked`
- action：Check lead demand before building owned assets, Luna packs or paid offer experiments.
- command：`python3 tools/promotion_lead_ops_action_sheet.py --check && python3 tools/promotion_lead_demand_gate.py --check`
- evidence：lead_ready_routes=0, repeated_routes=0.
- boundary：No repeated lead demand means no paid or priority offer build.

### allowed-decision-scope

- phase：`decision`
- status：`hold`
- action：Use week-decision-gate as the only source of truth for allowed next decisions.
- command：`python3 tools/promotion_week_decision_gate.py --check`
- evidence：weeklyDecision=0, testSoftOffer=0.
- boundary：Do not alter offer order, guardian priority, Luna emphasis, or affiliate weighting unless gate allows it.
