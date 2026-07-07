# LoveTypes Lead Ops Action Sheet

- 產生日期：2026-07-07
- rows：6
- real leads：0
- template rows：15
- blocked rows：2
- ready rows：1
- ready routes：0
- issues：0

## Rule

- Only real emails or copied structured requests may become real lead rows.
- Do not store raw reply email in lead-intake-tracker.csv.
- A zero, empty or missing KPI signal is not a commercial decision.
- Repeated same-guardian demand must appear before building paid or priority assets.
- Emergency, diagnosis, counseling replacement or sensitive personal-data requests stay outside the promotion tracker.

## Actions

### lead-form-health

- phase：`capture`
- status：`ready_to_check`
- action：Run lead form and importability audits before treating Contact or keepsake requests as structured leads.
- command：`python3 tools/promotion_lead_form_audit.py && python3 tools/promotion_lead_form_importability_audit.py`
- evidence：configured/rendered forms and importable sample texts must report issues=0.
- next gate：`structured_request_can_be_copied`

### incoming-request-triage

- phase：`triage`
- status：`waiting_for_real_email`
- action：For each real Contact or keepsake email, copy only the LoveTypes structured request block into a temporary text file.
- command：`python3 tools/promotion_lead_text_import.py check --input /path/to/request.txt`
- evidence：source, guardian, intake_type, reply email presence, consent and utm_content parsing all visible in check output.
- next gate：`safe_to_writeback`

### lead-writeback

- phase：`writeback`
- status：`blocked_until_real_request`
- action：Write back only real requests with explicit reply consent and a traceable proof note; never store raw email in the CSV.
- command：`python3 tools/promotion_lead_text_import.py add --input /path/to/request.txt --proof-note "email thread Gmail request checked 2026-07-07"`
- evidence：lead-intake-tracker.csv gains one real row, and matched utm_content increments the mapped KPI field.
- next gate：`lead_evidence_checklist`

### evidence-and-demand

- phase：`gate`
- status：`blocked_until_traceable_leads`
- action：Refresh evidence and demand gates before deciding whether to build a free asset, Luna pack, or offer experiment.
- command：`python3 tools/promotion_evidence_ledger.py && python3 tools/promotion_lead_evidence_checklist.py && python3 tools/promotion_lead_demand_gate.py`
- evidence：real leads have traceable evidence and explicit consent; repeated guardian demand reaches the threshold before any offer build.
- next gate：`offer_or_asset_queue`

### manual-command-fallback

- phase：`fallback`
- status：`available`
- action：If structured text parsing fails, use guardian-specific command examples from lead-writeback-playbook.md after manual validation.
- command：`python3 tools/promotion_lead_writeback.py add --source contact --guardian <guardian> --intake-type <type> --consent-status explicit_reply_ok --proof-note "email thread checked YYYY-MM-DD"`
- evidence：manual command still requires explicit consent, safe scope and proof note policy.
- next gate：`lead_evidence_checklist`

### current-demand-state

- phase：`state`
- status：`hold`
- action：Use the demand gate state as the only source for asset or offer priority.
- command：`python3 tools/promotion_lead_demand_gate.py --check`
- evidence：real_leads=0, ready_routes=0, blockers=no_real_leads,no_repeated_guardian_demand
- next gate：`master_gate_lead_ready_routes`
