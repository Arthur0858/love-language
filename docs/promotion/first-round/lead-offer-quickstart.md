# LoveTypes Lead and Offer Quickstart

- 產生日期：2026-06-29
- handoff rows：8
- current blockers / blocked upstream：1 / 5
- real leads：0
- ready lead routes：0
- public free assets：5
- ready to prepare assets：5
- offer queue ready / blocked：0 / 80
- offer board ready / hold：0 / 5
- issues：0

## Rules

- Do not build paid, Luna, affiliate, or priority offer experiments until weekly review and lead demand gates are open.
- Real lead demand requires explicit reply consent, traceable proof, and repeated same-guardian demand.
- Public free keepsakes and content variants can remain available, but they are not proof of purchase intent.
- Owned PDFs, wallpapers, email templates, and short rituals remain blocked until a real matching request exists.
- Offer queue rows must remain blocked while empty data mode or weekly review blockers are active.

## Handoff

### `weekly_review_open`

- phase：`weekly_review`
- status：`current_blocker`
- value：0 / 1
- action：Start lead and offer evaluation only after publish/KPI handoff opens weekly review.
- command：`python3 tools/promotion_publish_kpi_handoff.py --check`
- stop：Do not evaluate lead or offer routes while post URLs or minimum KPI proof are incomplete.

### `weekly_decision_ready`

- phase：`weekly_review`
- status：`blocked_upstream`
- value：1 / 3
- action：Confirm weekly review, week decision gate, and non-empty data mode before route decisions.
- command：`python3 tools/promotion_weekly_review_packet.py --check && python3 tools/promotion_week_decision_gate.py --check`
- stop：Do not pick winners or change commerce order while empty data mode is true.

### `weekly_evidence_complete`

- phase：`weekly_review`
- status：`blocked_upstream`
- value：4 / 8
- action：Complete weekly evidence checks before choosing content, asset, Luna, or affiliate direction.
- command：`python3 tools/promotion_weekly_decision_evidence_checklist.py --check`
- stop：Stop if any weekly decision evidence row remains pending.

### `lead_capture_ready`

- phase：`lead_collection`
- status：`complete`
- value：1 / 1
- action：Keep Contact, keepsake, and Luna requests importable before using them as lead signals.
- command：`python3 tools/promotion_lead_ops_action_sheet.py --check`
- stop：Do not collect raw sensitive content or use requests without explicit reply consent.

### `lead_demand_ready`

- phase：`lead_collection`
- status：`blocked_upstream`
- value：0 / 1
- action：Advance to owned assets or Luna only after repeated same-guardian demand creates a ready route.
- command：`python3 tools/promotion_lead_demand_gate.py --check`
- stop：Do not create paid or priority assets from a single request, weak signal, or no consent.

### `asset_fulfillment_ready`

- phase：`asset_fulfillment`
- status：`blocked_upstream`
- value：0 / 1
- action：Prepare only the smallest matching free asset or Luna aftercare item for proven demand.
- command：`python3 tools/promotion_asset_fulfillment_gate.py --check`
- stop：Keep public free assets available, but do not build custom products before demand proof.

### `offer_experiment_ready`

- phase：`offer_experiment`
- status：`blocked_upstream`
- value：0 / 1
- action：Only run low-risk offer experiments when both plan and queue have READY rows.
- command：`python3 tools/promotion_offer_experiment_plan.py --check && python3 tools/promotion_offer_experiment_queue.py --check`
- stop：Do not add paid CTA to Shorts or claim diagnosis, therapy, guarantee, or required purchase.

### `public_free_assets_remain_safe`

- phase：`safety`
- status：`complete`
- value：1 / 1
- action：Keep five public free assets as safe lead magnets while real demand is absent.
- command：`python3 tools/promotion_asset_fulfillment_gate.py --check && python3 tools/promotion_lead_demand_gate.py --check`
- stop：Stop if public free assets are treated as proof of product demand without tracked requests.

## Lead Actions

- `lead-form-health` / `ready_to_check`：Run lead form and importability audits before treating Contact or keepsake requests as structured leads.
- `incoming-request-triage` / `waiting_for_real_email`：For each real Contact or keepsake email, copy only the LoveTypes structured request block into a temporary text file.
- `lead-writeback` / `blocked_until_real_request`：Write back only real requests with explicit reply consent and a traceable proof note; never store raw email in the CSV.
- `evidence-and-demand` / `blocked_until_traceable_leads`：Refresh evidence and demand gates before deciding whether to build a free asset, Luna pack, or offer experiment.
- `manual-command-fallback` / `available`：If structured text parsing fails, use guardian-specific command examples from lead-writeback-playbook.md after manual validation.
- `current-demand-state` / `hold`：Use the demand gate state as the only source for asset or offer priority.

## Safe Assets Now

- `iris-free_story_card_upgrade` / `public_free_ready`：https://lovetypes.tw/keepsakes/#keepsake-iris
- `iris-content_variant` / `ready_to_prepare`：https://lovetypes.tw/start/
- `noah-free_story_card_upgrade` / `public_free_ready`：https://lovetypes.tw/keepsakes/#keepsake-noah
- `noah-content_variant` / `ready_to_prepare`：https://lovetypes.tw/start/
- `vivian-free_story_card_upgrade` / `public_free_ready`：https://lovetypes.tw/keepsakes/#keepsake-vivian
- `vivian-content_variant` / `ready_to_prepare`：https://lovetypes.tw/start/
- `claire-free_story_card_upgrade` / `public_free_ready`：https://lovetypes.tw/keepsakes/#keepsake-claire
- `claire-content_variant` / `ready_to_prepare`：https://lovetypes.tw/start/
- `dora-free_story_card_upgrade` / `public_free_ready`：https://lovetypes.tw/keepsakes/#keepsake-dora
- `dora-content_variant` / `ready_to_prepare`：https://lovetypes.tw/start/

## Blocked Asset Examples

- `iris-pdf_practice_card` / `blocked_until_real_request`：Wait for lead-intake-tracker.csv evidence before building or sending.
- `iris-phone_wallpaper` / `blocked_until_real_request`：Wait for lead-intake-tracker.csv evidence before building or sending.
- `iris-email_lead_template` / `blocked_until_real_request`：Wait for lead-intake-tracker.csv evidence before building or sending.
- `iris-short_ritual` / `blocked_until_real_request`：Wait for lead-intake-tracker.csv evidence before building or sending.
- `iris-luna_scene_cta` / `blocked_until_offer_ready`：Keep Luna/affiliate as secondary routes until KPI evidence is non-empty.
- `iris-affiliate_book_bundle` / `blocked_until_offer_ready`：Keep Luna/affiliate as secondary routes until KPI evidence is non-empty.
- `noah-pdf_practice_card` / `blocked_until_real_request`：Wait for lead-intake-tracker.csv evidence before building or sending.
- `noah-phone_wallpaper` / `blocked_until_real_request`：Wait for lead-intake-tracker.csv evidence before building or sending.
- `noah-email_lead_template` / `blocked_until_real_request`：Wait for lead-intake-tracker.csv evidence before building or sending.
- `noah-short_ritual` / `blocked_until_real_request`：Wait for lead-intake-tracker.csv evidence before building or sending.
