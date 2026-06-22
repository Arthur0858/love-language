# LoveTypes Data Collection Sheet

- 產生日期：2026-06-23
- source rows：16
- collection rows：284
- profile collection rows：14
- Shorts collection rows：270
- minimum KPI rows：48
- lead-intent rows：48
- blocked rows：252
- ready rows：6
- filled rows：0
- issues：0

## Rules

- Profile rows stay blocked until the profile link is confirmed set/live.
- Shorts rows stay blocked until a real public post URL is written back.
- Minimum KPI rows are `site_clicks`, `quiz_starts`, and `quiz_completions`.
- Lead-intent rows require real user request, explicit consent, and traceable evidence.
- Do not change product order, paid CTA, Luna emphasis, affiliate emphasis, or winning guardian from blank data.

## Source Summary

- `profile` / `youtube_shorts` / `profile-youtube_shorts`: 14 metrics, blocked 0, minimum 3, lead-intent 3
- `shorts` / `all` / `publish-lt-s12-claire-ask-help`: 18 metrics, blocked 18, minimum 3, lead-intent 3
- `shorts` / `all` / `publish-lt-s11-claire-promises`: 18 metrics, blocked 18, minimum 3, lead-intent 3
- `shorts` / `all` / `publish-lt-s10-claire-tired`: 18 metrics, blocked 18, minimum 3, lead-intent 3
- `shorts` / `all` / `publish-lt-s15-dora-after-conflict`: 18 metrics, blocked 18, minimum 3, lead-intent 3
- `shorts` / `all` / `publish-lt-s14-dora-consent`: 18 metrics, blocked 18, minimum 3, lead-intent 3
- `shorts` / `all` / `publish-lt-s13-dora-distance`: 18 metrics, blocked 18, minimum 3, lead-intent 3
- `shorts` / `all` / `publish-lt-s02-iris-affirmation`: 18 metrics, blocked 18, minimum 3, lead-intent 3
- `shorts` / `all` / `publish-lt-s01-iris-silence`: 18 metrics, blocked 0, minimum 3, lead-intent 3
- `shorts` / `all` / `publish-lt-s03-iris-too-sensitive`: 18 metrics, blocked 18, minimum 3, lead-intent 3
- `shorts` / `all` / `publish-lt-s05-noah-cancel`: 18 metrics, blocked 18, minimum 3, lead-intent 3
- `shorts` / `all` / `publish-lt-s04-noah-phone`: 18 metrics, blocked 18, minimum 3, lead-intent 3
- `shorts` / `all` / `publish-lt-s06-noah-quiet-time`: 18 metrics, blocked 18, minimum 3, lead-intent 3
- `shorts` / `all` / `publish-lt-s08-vivian-forgotten-date`: 18 metrics, blocked 18, minimum 3, lead-intent 3
- `shorts` / `all` / `publish-lt-s07-vivian-remembered`: 18 metrics, blocked 18, minimum 3, lead-intent 3
- `shorts` / `all` / `publish-lt-s09-vivian-ritual`: 18 metrics, blocked 18, minimum 3, lead-intent 3

## First 30 Collection Rows

### profile · youtube_shorts · `profile_clicks`

- task：`profile-youtube_shorts`
- status：`optional_after_minimum_kpi`
- gate：`route_learning`
- source：Platform analytics screen for the published post or profile link.
- proof：public post/profile URL plus analytics screenshot or checked proof note.
- writeback：`platform-profile-tracker.csv`

### profile · youtube_shorts · `site_clicks`

- task：`profile-youtube_shorts`
- status：`ready_for_source_check`
- gate：`weekly_review_minimum_kpi`
- source：Website analytics or event log filtered by tracked_url / utm_content.
- proof：post/profile URL, tracked UTM, analytics date window, and proof note.
- writeback：`platform-profile-tracker.csv`

### profile · youtube_shorts · `quiz_starts`

- task：`profile-youtube_shorts`
- status：`ready_for_source_check`
- gate：`weekly_review_minimum_kpi`
- source：Website analytics or event log filtered by tracked_url / utm_content.
- proof：post/profile URL, tracked UTM, analytics date window, and proof note.
- writeback：`platform-profile-tracker.csv`

### profile · youtube_shorts · `quiz_completions`

- task：`profile-youtube_shorts`
- status：`ready_for_source_check`
- gate：`weekly_review_minimum_kpi`
- source：Website analytics or event log filtered by tracked_url / utm_content.
- proof：post/profile URL, tracked UTM, analytics date window, and proof note.
- writeback：`platform-profile-tracker.csv`

### profile · youtube_shorts · `guardian_result_clicks`

- task：`profile-youtube_shorts`
- status：`optional_after_minimum_kpi`
- gate：`route_learning`
- source：Website event catalog: guardian_resume_primary, guardian_resume_profile, home_resume_guardian, guide_resume_guardian, guardian_map_card
- proof：site event count or checked-zero proof note tied to the same UTM row.
- writeback：`platform-profile-tracker.csv`

### profile · youtube_shorts · `resources_clicks`

- task：`profile-youtube_shorts`
- status：`optional_after_minimum_kpi`
- gate：`route_learning`
- source：Website event catalog: quiz_result_supply_route, home_resume_supply_route, guardian_hero_supply_route, supply_quick_route, supply_entry_routes, home_saved_pack_link, supply_pack_link
- proof：site event count or checked-zero proof note tied to the same UTM row.
- writeback：`platform-profile-tracker.csv`

### profile · youtube_shorts · `repair_plan_clicks`

- task：`profile-youtube_shorts`
- status：`optional_after_minimum_kpi`
- gate：`route_learning`
- source：Website event catalog: quiz_result_repair_plan, home_resume_repair_plan, repair_resume_plan, practice_card_repair_plan
- proof：site event count or checked-zero proof note tied to the same UTM row.
- writeback：`platform-profile-tracker.csv`

### profile · youtube_shorts · `luna_clicks`

- task：`profile-youtube_shorts`
- status：`optional_after_minimum_kpi`
- gate：`route_learning`
- source：Website event catalog: quiz_result_luna, home_resume_luna, guardian_resume_luna, luna_offer_resources, luna_use_case_action, home_saved_pack_luna, supply_pack_luna
- proof：site event count or checked-zero proof note tied to the same UTM row.
- writeback：`platform-profile-tracker.csv`

### profile · youtube_shorts · `keepsake_clicks`

- task：`profile-youtube_shorts`
- status：`optional_after_minimum_kpi`
- gate：`route_learning`
- source：Website event catalog: quiz_result_keepsake, home_resume_keepsake, keepsake_resume_story_open, practice_card_supply_route
- proof：site event count or checked-zero proof note tied to the same UTM row.
- writeback：`platform-profile-tracker.csv`

### profile · youtube_shorts · `free_keepsake_downloads`

- task：`profile-youtube_shorts`
- status：`optional_after_minimum_kpi`
- gate：`route_learning`
- source：Website event catalog: free_keepsake_download, collector_story_download, keepsake_resume_story_download, practice_card_print, home_saved_pack_free_keepsake, supply_pack_free_keepsake
- proof：site event count or checked-zero proof note tied to the same UTM row.
- writeback：`platform-profile-tracker.csv`

### profile · youtube_shorts · `supply_lead_requests`

- task：`profile-youtube_shorts`
- status：`waiting_for_real_lead_or_review`
- gate：`lead_demand_or_offer_gate`
- source：lead-intake-tracker.csv plus traceable consent/evidence; optional matching UTM attribution.
- proof：real user request, explicit_reply_ok consent, traceable email/thread/proof note, and safe notes without raw sensitive content.
- writeback：`platform-profile-tracker.csv`

### profile · youtube_shorts · `luna_pack_clicks`

- task：`profile-youtube_shorts`
- status：`waiting_for_real_lead_or_review`
- gate：`lead_demand_or_offer_gate`
- source：lead-intake-tracker.csv plus traceable consent/evidence; optional matching UTM attribution.
- proof：real user request, explicit_reply_ok consent, traceable email/thread/proof note, and safe notes without raw sensitive content.
- writeback：`platform-profile-tracker.csv`

### profile · youtube_shorts · `affiliate_book_clicks`

- task：`profile-youtube_shorts`
- status：`optional_after_minimum_kpi`
- gate：`route_learning`
- source：Website event catalog: supply_route_affiliate_book, quiz_result_affiliate_book, repair_guardian_affiliate_book, repair_resume_affiliate_book
- proof：site event count or checked-zero proof note tied to the same UTM row.
- writeback：`platform-profile-tracker.csv`

### profile · youtube_shorts · `contact_requests`

- task：`profile-youtube_shorts`
- status：`waiting_for_real_lead_or_review`
- gate：`lead_demand_or_offer_gate`
- source：lead-intake-tracker.csv plus traceable consent/evidence; optional matching UTM attribution.
- proof：real user request, explicit_reply_ok consent, traceable email/thread/proof note, and safe notes without raw sensitive content.
- writeback：`platform-profile-tracker.csv`

### shorts · all · `views`

- task：`publish-lt-s12-claire-ask-help`
- status：`blocked_until_public_post_url`
- gate：`route_learning`
- source：Platform analytics screen for the published post or profile link.
- proof：public post/profile URL plus analytics screenshot or checked proof note.
- writeback：`platform-kpi-tracker.csv first; kpi-tracker.csv weekly rollup`

### shorts · all · `likes`

- task：`publish-lt-s12-claire-ask-help`
- status：`blocked_until_public_post_url`
- gate：`route_learning`
- source：Platform analytics screen for the published post or profile link.
- proof：public post/profile URL plus analytics screenshot or checked proof note.
- writeback：`platform-kpi-tracker.csv first; kpi-tracker.csv weekly rollup`

### shorts · all · `comments`

- task：`publish-lt-s12-claire-ask-help`
- status：`blocked_until_public_post_url`
- gate：`route_learning`
- source：Platform analytics screen for the published post or profile link.
- proof：public post/profile URL plus analytics screenshot or checked proof note.
- writeback：`platform-kpi-tracker.csv first; kpi-tracker.csv weekly rollup`

### shorts · all · `shares`

- task：`publish-lt-s12-claire-ask-help`
- status：`blocked_until_public_post_url`
- gate：`route_learning`
- source：Platform analytics screen for the published post or profile link.
- proof：public post/profile URL plus analytics screenshot or checked proof note.
- writeback：`platform-kpi-tracker.csv first; kpi-tracker.csv weekly rollup`

### shorts · all · `profile_clicks`

- task：`publish-lt-s12-claire-ask-help`
- status：`blocked_until_public_post_url`
- gate：`route_learning`
- source：Platform analytics screen for the published post or profile link.
- proof：public post/profile URL plus analytics screenshot or checked proof note.
- writeback：`platform-kpi-tracker.csv first; kpi-tracker.csv weekly rollup`

### shorts · all · `site_clicks`

- task：`publish-lt-s12-claire-ask-help`
- status：`blocked_until_public_post_url`
- gate：`weekly_review_minimum_kpi`
- source：Website analytics or event log filtered by tracked_url / utm_content.
- proof：post/profile URL, tracked UTM, analytics date window, and proof note.
- writeback：`platform-kpi-tracker.csv first; kpi-tracker.csv weekly rollup`

### shorts · all · `quiz_starts`

- task：`publish-lt-s12-claire-ask-help`
- status：`blocked_until_public_post_url`
- gate：`weekly_review_minimum_kpi`
- source：Website analytics or event log filtered by tracked_url / utm_content.
- proof：post/profile URL, tracked UTM, analytics date window, and proof note.
- writeback：`platform-kpi-tracker.csv first; kpi-tracker.csv weekly rollup`

### shorts · all · `quiz_completions`

- task：`publish-lt-s12-claire-ask-help`
- status：`blocked_until_public_post_url`
- gate：`weekly_review_minimum_kpi`
- source：Website analytics or event log filtered by tracked_url / utm_content.
- proof：post/profile URL, tracked UTM, analytics date window, and proof note.
- writeback：`platform-kpi-tracker.csv first; kpi-tracker.csv weekly rollup`

### shorts · all · `guardian_result_clicks`

- task：`publish-lt-s12-claire-ask-help`
- status：`blocked_until_public_post_url`
- gate：`route_learning`
- source：Website event catalog: guardian_resume_primary, guardian_resume_profile, home_resume_guardian, guide_resume_guardian, guardian_map_card
- proof：site event count or checked-zero proof note tied to the same UTM row.
- writeback：`platform-kpi-tracker.csv first; kpi-tracker.csv weekly rollup`

### shorts · all · `resources_clicks`

- task：`publish-lt-s12-claire-ask-help`
- status：`blocked_until_public_post_url`
- gate：`route_learning`
- source：Website event catalog: quiz_result_supply_route, home_resume_supply_route, guardian_hero_supply_route, supply_quick_route, supply_entry_routes, home_saved_pack_link, supply_pack_link
- proof：site event count or checked-zero proof note tied to the same UTM row.
- writeback：`platform-kpi-tracker.csv first; kpi-tracker.csv weekly rollup`

### shorts · all · `repair_plan_clicks`

- task：`publish-lt-s12-claire-ask-help`
- status：`blocked_until_public_post_url`
- gate：`route_learning`
- source：Website event catalog: quiz_result_repair_plan, home_resume_repair_plan, repair_resume_plan, practice_card_repair_plan
- proof：site event count or checked-zero proof note tied to the same UTM row.
- writeback：`platform-kpi-tracker.csv first; kpi-tracker.csv weekly rollup`

### shorts · all · `luna_clicks`

- task：`publish-lt-s12-claire-ask-help`
- status：`blocked_until_public_post_url`
- gate：`route_learning`
- source：Website event catalog: quiz_result_luna, home_resume_luna, guardian_resume_luna, luna_offer_resources, luna_use_case_action, home_saved_pack_luna, supply_pack_luna
- proof：site event count or checked-zero proof note tied to the same UTM row.
- writeback：`platform-kpi-tracker.csv first; kpi-tracker.csv weekly rollup`

### shorts · all · `keepsake_clicks`

- task：`publish-lt-s12-claire-ask-help`
- status：`blocked_until_public_post_url`
- gate：`route_learning`
- source：Website event catalog: quiz_result_keepsake, home_resume_keepsake, keepsake_resume_story_open, practice_card_supply_route
- proof：site event count or checked-zero proof note tied to the same UTM row.
- writeback：`platform-kpi-tracker.csv first; kpi-tracker.csv weekly rollup`

### shorts · all · `free_keepsake_downloads`

- task：`publish-lt-s12-claire-ask-help`
- status：`blocked_until_public_post_url`
- gate：`route_learning`
- source：Website event catalog: free_keepsake_download, collector_story_download, keepsake_resume_story_download, practice_card_print, home_saved_pack_free_keepsake, supply_pack_free_keepsake
- proof：site event count or checked-zero proof note tied to the same UTM row.
- writeback：`platform-kpi-tracker.csv first; kpi-tracker.csv weekly rollup`

### shorts · all · `supply_lead_requests`

- task：`publish-lt-s12-claire-ask-help`
- status：`blocked_until_public_post_url`
- gate：`lead_demand_or_offer_gate`
- source：lead-intake-tracker.csv plus traceable consent/evidence; optional matching UTM attribution.
- proof：real user request, explicit_reply_ok consent, traceable email/thread/proof note, and safe notes without raw sensitive content.
- writeback：`platform-kpi-tracker.csv first; kpi-tracker.csv weekly rollup`

### shorts · all · `luna_pack_clicks`

- task：`publish-lt-s12-claire-ask-help`
- status：`blocked_until_public_post_url`
- gate：`lead_demand_or_offer_gate`
- source：lead-intake-tracker.csv plus traceable consent/evidence; optional matching UTM attribution.
- proof：real user request, explicit_reply_ok consent, traceable email/thread/proof note, and safe notes without raw sensitive content.
- writeback：`platform-kpi-tracker.csv first; kpi-tracker.csv weekly rollup`

_完整 284 rows 請看 CSV / JSON。_
