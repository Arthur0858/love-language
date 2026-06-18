# LoveTypes Launch Execution Closure Quickstart

- 產生日期：2026-06-18
- master stage：`first_batch_publish`
- profile configured：1 / 1
- first batch published：0 / 1
- minimum KPI rows：0 / 1
- profile clipboard ready：0
- post clipboard blocked：0
- launch day ready / blocked：2 / 2
- exception stop / hold：6 / 3
- proof profile template valid / post rejected：0 / 1
- proof profile placeholder / real ready：1 / 0
- proof rehearsal profile pass / post placeholder rejected：1 / 1
- profile publish ready：1
- publish KPI weekly ready：0
- issues：0

## Rules

- Use master-gate stage as the source of truth; do not skip profile_setup.
- Profile setup may proceed now, but publish, KPI, weekly review, lead, and offer decisions remain blocked.
- Every external action needs visible account identity, safe copy, public URL verification, and proof note.
- Placeholder post URLs must be rejected until real public post URLs exist.
- Exception runbook stop conditions override all quickstarts.

## Closure Steps

### `prepare_profile_clipboard`

- status：`blocked`
- command：`python3 tools/promotion_launch_clipboard.py --check && python3 tools/promotion_operation_proof_templates.py --check`
- release：Three profile setup copy blocks and profile proof templates are ready.
- stop：Stop if the visible platform account is not LoveTypes or the profile copy adds paid, diagnosis, therapy, or guarantee claims.

### `capture_profile_proof`

- status：`complete`
- command：`python3 tools/promotion_proof_rehearsal.py --check && python3 tools/promotion_profile_writeback.py check`
- release：All profile links are set/live with traceable proof notes.
- stop：Do not write back profile status from memory, draft screens, private previews, or missing screenshots.

### `open_first_batch_publish`

- status：`ready_to_publish`
- command：`python3 tools/promotion_profile_publish_handoff.py --check && python3 tools/promotion_first_batch_publish_closure_quickstart.py --check`
- release：Profile handoff opens first-batch publishing.
- stop：Do not publish first-batch posts while profile setup remains incomplete.

### `close_first_batch_and_kpi`

- status：`blocked_until_public_posts`
- command：`python3 tools/promotion_publish_kpi_handoff.py --check && python3 tools/promotion_first_batch_kpi_closure_quickstart.py --check`
- release：First batch posts have public URLs and checked minimum KPI rows.
- stop：Do not open weekly review from placeholder URLs, private posts, or unchecked zero KPI values.

### `keep_exception_runbook_armed`

- status：`armed`
- command：`python3 tools/promotion_launch_exception_runbook.py --check`
- release：Stop/hold/escalate conditions are visible before every external platform action.
- stop：Stop immediately on wrong account, missing permission, URL rewrite, unsafe copy, or emergency/support request.

## Profile Actions

### youtube_shorts

- status：`complete`
- action：Set the platform profile link, then verify the structured proof text before writeback.
- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts.txt`
- write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`
- stop：A real platform screenshot/click proof must exist before running the write command.

## Armed Stop Conditions

- `wrong_platform_account`：Visible account, channel, public profile, or edit permission does not match the intended LoveTypes platform identity. Stop：Do not set profile link, do not publish, and do not write back profile status.
- `profile_link_wrong_or_missing`：Profile link is not the planned /start/ UTM URL, is missing, or cannot be clicked from the public profile. Stop：Do not mark profile set/live and do not publish first-batch posts.
- `publish_before_profile_gate`：A first-batch post is about to publish while ready_to_publish is false. Stop：Cancel or leave draft/scheduled; do not publish manually around the gate.
- `wrong_post_url_or_platform`：Post URL domain does not match the active platform row, or URL points to the wrong post. Stop：Do not write back; do not reuse the URL in weekly review.
- `paid_cta_or_affiliate_first_touch`：Caption/profile first action emphasizes Luna, affiliate books, paid products, or purchase before the quiz. Stop：Do not publish, or edit immediately before public verification/writeback.
- `empty_data_commerce_change`：Offer order, paid CTA, Luna emphasis, affiliate emphasis, or winning guardian is changed while empty-data mode is true. Stop：Revert the commerce/content-priority change and keep collect_signal focus.
