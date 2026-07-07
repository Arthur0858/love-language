# LoveTypes Decision Input Matrix

- 產生日期：2026-07-07
- decisions：5
- ready decisions：0
- active decisions：1
- blocked decisions：4
- input rows：288
- filled input rows：0
- blocked input rows：252
- lead ready routes：0
- empty data mode：0
- issues：0

## Rules

- A decision needs both an open week gate and enough filled input rows.
- Empty-data mode blocks commerce, offer order changes, Luna emphasis, affiliate emphasis, and winning-guardian decisions.
- Platform engagement alone cannot open commerce decisions.
- Lead decisions require explicit consent and traceable evidence.

## Decisions

### `collect_signal`

- status：`active`
- gate：`weeklyDecision` open=0
- readiness checklist：`active`
- required metrics：`profile_clicks, site_clicks, quiz_starts, quiz_completions`
- inputs：64 rows; filled 0; ready 8; blocked 56
- minimum filled：0
- blocker：none
- allowed：Set profiles, publish first batch, and backfill public URLs plus minimum KPI evidence.
- blocked：Change offer order, pick a winning guardian, or increase paid CTA.

### `scale_content`

- status：`blocked_waiting_for_source`
- gate：`scaleContent` open=0
- readiness checklist：`blocked`
- required metrics：`site_clicks, quiz_starts, quiz_completions`
- inputs：48 rows; filled 0; ready 6; blocked 42
- minimum filled：3
- blocker：required source rows are still blocked by profile/post/KPI setup
- allowed：Publish more variants for the strongest guardian or pain point while keeping quiz CTA.
- blocked：Treat views, likes, or comments as proof of purchase intent.

### `deepen_identity_asset`

- status：`blocked_waiting_for_source`
- gate：`deepenIdentityAsset` open=0
- readiness checklist：`blocked`
- required metrics：`guardian_result_clicks, resources_clicks, repair_plan_clicks, luna_clicks, keepsake_clicks, free_keepsake_downloads`
- inputs：96 rows; filled 0; ready 12; blocked 84
- minimum filled：1
- blocker：required source rows are still blocked by profile/post/KPI setup
- allowed：Improve free keepsakes, story cards, share images, and result-route assets.
- blocked：Move the primary CTA directly to paid products.

### `build_owned_lead_asset`

- status：`blocked_waiting_for_source`
- gate：`buildOwnedLeadAsset` open=0
- readiness checklist：`blocked`
- required metrics：`supply_lead_requests, contact_requests`
- inputs：32 rows; filled 0; ready 4; blocked 28
- minimum filled：1
- blocker：required source rows are still blocked by profile/post/KPI setup
- allowed：Build one low-risk email/download asset for the signaled guardian or route.
- blocked：Build a paid product before repeated lead evidence and explicit consent exist.

### `test_soft_offer`

- status：`blocked_waiting_for_source`
- gate：`testSoftOffer` open=0
- readiness checklist：`blocked`
- required metrics：`luna_pack_clicks, affiliate_book_clicks, quiz_completions`
- inputs：48 rows; filled 0; ready 6; blocked 42
- minimum filled：2
- blocker：required source rows are still blocked by profile/post/KPI setup
- allowed：Test a soft result-route Luna or affiliate offer after the quiz/result context.
- blocked：Use direct sales language in first-touch Shorts or profile bio.
