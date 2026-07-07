# LoveTypes Proof Import Closure Quickstart

- 產生日期：2026-07-07
- profile templates：0
- post templates：0
- active platforms：1
- profile template valid：0
- profile placeholder proof rows：1
- profile real proof ready rows：0
- post safely rejected：0
- rehearsal rows：3
- rehearsal profile pass：1
- rehearsal post placeholder rejected：1
- rehearsal post real URL pass：1
- profile evidence rows：6
- profile evidence pending：6
- structured imports：3 / 3
- launch ready to publish：1
- empty data mode：0
- issues：0

## Rules

- Check commands must pass before any add/writeback command is allowed.
- Profile proof templates may pass structurally, but still require real external evidence before writeback.
- Post proof templates must fail while placeholder URLs remain in place; after public URL writeback, KPI source proof is required.
- A zero KPI is valid only after a real analytics source check.
- Rehearsal data, sample URLs, and templates are never production evidence.

## Closure Steps

### `validate_profile_proof_templates`

- status：`ready_to_use`
- command：`python3 tools/promotion_operation_proof_templates.py --check && python3 tools/promotion_profile_evidence_checklist.py --check`
- release：Active profile proof templates validate and each active platform has six evidence checks.
- stop：Do not write profile status unless all six evidence checks are backed by real platform proof.

### `reject_post_placeholders`

- status：`complete`
- command：`python3 tools/promotion_operation_proof_templates.py --check`
- release：Active post proof templates are safely rejected while their post URLs are placeholders; completed posts move to KPI source proof.
- stop：Do not weaken this guard; placeholder post URLs must never write to trackers or KPI rows.

### `rehearse_import_paths`

- status：`complete`
- command：`python3 tools/promotion_proof_rehearsal.py --check && python3 tools/promotion_operator_import_template_audit.py`
- release：Profile import passes, placeholder post import fails, sample real post URLs pass, and operator import templates enforce safe rejection.
- stop：Do not run add/writeback commands until the check path behaves as expected.

### `writeback_after_external_proof`

- status：`blocked_until_external_proof`
- command：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-<platform>.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`
- release：A real platform screenshot/click proof exists and the profile proof text passed check.
- stop：Do not write back from rehearsal data, templates, private previews, or memory.

### `open_publish_only_after_profile_gate`

- status：`blocked_until_profile_writeback`
- command：`python3 tools/promotion_launch_rehearsal_packet.py --check && python3 tools/promotion_profile_publish_handoff.py --check`
- release：Profile writeback is complete and first-batch publishing is explicitly open.
- stop：Do not publish or backfill KPI while launch rehearsal says publish is blocked.

## Proof Rows

## Structured Imports

- `lead_request_import`
- `post_publish_import`
- `profile_setup_import`
