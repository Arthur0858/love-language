# LoveTypes Launch Exception Runbook

- 產生日期：2026-07-02
- exception rows：10
- hard stops：6
- holds：3
- escalations：1
- profile configured：1
- real profile proof ready：0 / 1
- placeholder proof rows：1
- external profile proof blockers：1
- ready to publish：1
- first batch published：1
- empty data mode：0
- issues：0

## Rule

- 異常先停手，再回填；不要用修正後的意圖覆蓋原始證據缺口。
- 錯帳號、錯 URL、錯 CTA、未驗證 KPI 都不能進週回顧。
- 危機、診斷、諮商替代或敏感個資需求不當成推廣 lead。
- 空資料時不改商品排序、付費 CTA、Luna / 聯盟優先序或勝出守護者。

## Exceptions

### `wrong_platform_account`

- phase：`profile_setup`
- severity：`stop`
- trigger：Visible account, channel, public profile, or edit permission does not match the intended LoveTypes platform identity.
- stop：Do not set profile link, do not publish, and do not write back profile status.
- recovery：Switch to the correct account, rerun platform account identity checklist, then capture a traceable proof note.
- source：`platform-account-identity-checklist.json`

### `profile_link_wrong_or_missing`

- phase：`profile_setup`
- severity：`stop`
- trigger：Profile link is not the planned /start/ UTM URL, is missing, or cannot be clicked from the public profile.
- stop：Do not mark profile set/live and do not publish first-batch posts.
- recovery：Fix the profile link, verify it opens lovetypes.tw/start/ with UTM preserved, then run profile text import check/add.
- source：`profile-proof-readiness-pack.json`

### `publish_before_profile_gate`

- phase：`publish_first_batch`
- severity：`stop`
- trigger：A first-batch post is about to publish while ready_to_publish is false.
- stop：Cancel or leave draft/scheduled; do not publish manually around the gate.
- recovery：Complete all active profile rows, refresh launch readiness, then use the first-batch publish action sheet.
- source：`first-batch-publication-packet.json`

### `post_not_public`

- phase：`post_url_writeback`
- severity：`hold`
- trigger：Post URL exists but is private, draft-only, login-only, or not reachable from a public browser.
- stop：Do not write back post_url as published and do not count KPI.
- recovery：Make the post public or replace with the correct public URL, then rerun public-post-url checks.
- source：`first-batch-evidence-matrix.json`

### `wrong_post_url_or_platform`

- phase：`post_url_writeback`
- severity：`stop`
- trigger：Post URL domain does not match the active platform row, or URL points to the wrong post.
- stop：Do not write back; do not reuse the URL in weekly review.
- recovery：Find the correct public post URL for the platform row and rerun post text import check.
- source：`first-batch-evidence-matrix.json`

### `paid_cta_or_affiliate_first_touch`

- phase：`publish_first_batch`
- severity：`stop`
- trigger：Caption/profile first action emphasizes Luna, affiliate books, paid products, or purchase before the quiz.
- stop：Do not publish, or edit immediately before public verification/writeback.
- recovery：Restore the single primary CTA: complete the 15-question quiz and find the emotional guardian.
- source：`first-batch-publication-packet.json`

### `zero_kpi_without_source`

- phase：`kpi_backfill`
- severity：`hold`
- trigger：site_clicks, quiz_starts, or quiz_completions is entered as 0 without a checked analytics/platform source.
- stop：Do not run weekly review and do not change commerce or content priority.
- recovery：Check analytics source, add proof note, then rerun zero KPI evidence checklist.
- source：`post-ops-readiness-pack.json`

### `duplicate_or_wrong_slot_post`

- phase：`publish_first_batch`
- severity：`hold`
- trigger：Same platform receives a duplicate first-batch post, wrong script, wrong slot, or wrong guardian.
- stop：Do not write back as the planned task until operator decides keep/delete/repost.
- recovery：If keeping, document exact task mapping; if deleting/reposting, only write back the final public post URL.
- source：`first-batch-publication-packet.json`

### `unsafe_or_crisis_comment`

- phase：`comment_or_lead_triage`
- severity：`escalate`
- trigger：Comment/email asks for crisis support, diagnosis, therapy replacement, or sensitive personal data handling.
- stop：Do not treat as promotion KPI or product lead.
- recovery：Use safety-bounded reply; direct to appropriate emergency/local professional support where relevant.
- source：`weekly-review-packet.json`

### `empty_data_commerce_change`

- phase：`weekly_review`
- severity：`stop`
- trigger：Offer order, paid CTA, Luna emphasis, affiliate emphasis, or winning guardian is changed while empty-data mode is true.
- stop：Revert the commerce/content-priority change and keep collect_signal focus.
- recovery：Wait until first-batch evidence, KPI rows, weekly review and decision gates are ready.
- source：`weekly-review-packet.json`
