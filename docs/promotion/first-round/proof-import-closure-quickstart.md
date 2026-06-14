# LoveTypes Proof Import Closure Quickstart

- 產生日期：2026-06-14
- profile templates：3
- post templates：3
- profile valid：3
- post safely rejected：3
- rehearsal rows：9
- rehearsal profile pass：3
- rehearsal post placeholder rejected：3
- rehearsal post real URL pass：3
- profile evidence rows：18
- profile evidence pending：18
- structured imports：3 / 3
- launch ready to publish：0
- empty data mode：1
- issues：0

## Rules

- Check commands must pass before any add/writeback command is allowed.
- Profile proof templates may pass structurally, but still require real external evidence before writeback.
- Post proof templates must fail while placeholder URLs remain in place.
- A zero KPI is valid only after a real analytics source check.
- Rehearsal data, sample URLs, and templates are never production evidence.

## Closure Steps

### `validate_profile_proof_templates`

- status：`ready_to_use`
- command：`python3 tools/promotion_operation_proof_templates.py --check && python3 tools/promotion_profile_evidence_checklist.py --check`
- release：Three profile proof templates validate and each platform has six evidence checks.
- stop：Do not write profile status unless all six evidence checks are backed by real platform proof.

### `reject_post_placeholders`

- status：`guard_active`
- command：`python3 tools/promotion_operation_proof_templates.py --check`
- release：Three post proof templates are safely rejected while their post URLs are placeholders.
- stop：Do not weaken this guard; placeholder post URLs must never write to trackers.

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

### profile_setup · youtube_shorts

- file：`docs/promotion/first-round/proof-youtube_shorts.txt`
- status：`written`
- evidence count：6
- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts.txt`
- write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`

### profile_setup · tiktok

- file：`docs/promotion/first-round/proof-tiktok.txt`
- status：`written`
- evidence count：6
- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-tiktok.txt`
- write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-tiktok.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`

### profile_setup · instagram_reels

- file：`docs/promotion/first-round/proof-instagram_reels.txt`
- status：`written`
- evidence count：6
- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-instagram_reels.txt`
- write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-instagram_reels.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`

### post_publish · youtube_shorts publish-lt-s01-iris-silence

- file：`docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt`
- status：`written`
- evidence count：7
- check：`python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt`
- write：`python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt --proof-note "public URL and analytics source checked 2026-06-14"`

### post_publish · tiktok publish-lt-s01-iris-silence

- file：`docs/promotion/first-round/proof-tiktok-publish-lt-s01-iris-silence.txt`
- status：`written`
- evidence count：7
- check：`python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-tiktok-publish-lt-s01-iris-silence.txt`
- write：`python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-tiktok-publish-lt-s01-iris-silence.txt --proof-note "public URL and analytics source checked 2026-06-14"`

### post_publish · instagram_reels publish-lt-s01-iris-silence

- file：`docs/promotion/first-round/proof-instagram_reels-publish-lt-s01-iris-silence.txt`
- status：`written`
- evidence count：7
- check：`python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-instagram_reels-publish-lt-s01-iris-silence.txt`
- write：`python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-instagram_reels-publish-lt-s01-iris-silence.txt --proof-note "public URL and analytics source checked 2026-06-14"`

## Structured Imports

- `lead_request_import`
- `post_publish_import`
- `profile_setup_import`
