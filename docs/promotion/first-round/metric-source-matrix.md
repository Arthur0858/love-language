# LoveTypes Metric Source Matrix

- 產生日期：2026-06-22
- rows：18
- platform fields：5
- site conversion fields：3
- route interest fields：7
- lead / revenue-intent fields：3
- issues：0

## Operating Rules

- Blank is unknown; 0 is valid only after the matching source window is checked.
- Weekly and product decisions require site / quiz data, not platform engagement alone.
- Lead-intent fields require explicit consent and traceable evidence before they influence product work.
- Do not store raw sensitive email content in trackers.

## Metrics

### `views`

- category：`platform_engagement`
- primary source：Platform analytics screen for the published post or profile link.
- trackers：kpi-tracker.csv, platform-kpi-tracker.csv
- required proof：public post/profile URL plus analytics screenshot or checked proof note.
- zero policy：`yes_after_public_source_check`；0 is valid only after the public URL exists and the platform analytics screen has been checked for the same date window.
- decision use：Useful for creative learning, but cannot choose a winning guardian or product path without site and quiz data.
- writeback：`promotion_post_writeback.py or promotion_profile_writeback.py`

### `likes`

- category：`platform_engagement`
- primary source：Platform analytics screen for the published post or profile link.
- trackers：kpi-tracker.csv, platform-kpi-tracker.csv
- required proof：public post/profile URL plus analytics screenshot or checked proof note.
- zero policy：`yes_after_public_source_check`；0 is valid only after the public URL exists and the platform analytics screen has been checked for the same date window.
- decision use：Useful for creative learning, but cannot choose a winning guardian or product path without site and quiz data.
- writeback：`promotion_post_writeback.py or promotion_profile_writeback.py`

### `comments`

- category：`platform_engagement`
- primary source：Platform analytics screen for the published post or profile link.
- trackers：kpi-tracker.csv, platform-kpi-tracker.csv
- required proof：public post/profile URL plus analytics screenshot or checked proof note.
- zero policy：`yes_after_public_source_check`；0 is valid only after the public URL exists and the platform analytics screen has been checked for the same date window.
- decision use：Useful for creative learning, but cannot choose a winning guardian or product path without site and quiz data.
- writeback：`promotion_post_writeback.py or promotion_profile_writeback.py`

### `shares`

- category：`platform_engagement`
- primary source：Platform analytics screen for the published post or profile link.
- trackers：kpi-tracker.csv, platform-kpi-tracker.csv
- required proof：public post/profile URL plus analytics screenshot or checked proof note.
- zero policy：`yes_after_public_source_check`；0 is valid only after the public URL exists and the platform analytics screen has been checked for the same date window.
- decision use：Useful for creative learning, but cannot choose a winning guardian or product path without site and quiz data.
- writeback：`promotion_post_writeback.py or promotion_profile_writeback.py`

### `profile_clicks`

- category：`platform_engagement`
- primary source：Platform analytics screen for the published post or profile link.
- trackers：kpi-tracker.csv, platform-kpi-tracker.csv, platform-profile-tracker.csv
- required proof：public post/profile URL plus analytics screenshot or checked proof note.
- zero policy：`yes_after_public_source_check`；0 is valid only after the public URL exists and the platform analytics screen has been checked for the same date window.
- decision use：Useful for creative learning, but cannot choose a winning guardian or product path without site and quiz data.
- writeback：`promotion_post_writeback.py or promotion_profile_writeback.py`

### `site_clicks`

- category：`site_conversion`
- primary source：Website analytics or event log filtered by tracked_url / utm_content.
- trackers：kpi-tracker.csv, platform-kpi-tracker.csv, platform-profile-tracker.csv
- required proof：post/profile URL, tracked UTM, analytics date window, and proof note.
- zero policy：`yes_after_site_source_check`；0 is valid only after the site analytics source was checked; blank is not the same as 0.
- decision use：Minimum required for weekly review; quiz_completions is the main first-round success signal.
- writeback：`promotion_post_writeback.py or promotion_profile_writeback.py`

### `quiz_starts`

- category：`site_conversion`
- primary source：Website analytics or event log filtered by tracked_url / utm_content.
- trackers：kpi-tracker.csv, platform-kpi-tracker.csv, platform-profile-tracker.csv
- required proof：post/profile URL, tracked UTM, analytics date window, and proof note.
- zero policy：`yes_after_site_source_check`；0 is valid only after the site analytics source was checked; blank is not the same as 0.
- decision use：Minimum required for weekly review; quiz_completions is the main first-round success signal.
- writeback：`promotion_post_writeback.py or promotion_profile_writeback.py`

### `quiz_completions`

- category：`site_conversion`
- primary source：Website analytics or event log filtered by tracked_url / utm_content.
- trackers：kpi-tracker.csv, platform-kpi-tracker.csv, platform-profile-tracker.csv
- required proof：post/profile URL, tracked UTM, analytics date window, and proof note.
- zero policy：`yes_after_site_source_check`；0 is valid only after the site analytics source was checked; blank is not the same as 0.
- decision use：Minimum required for weekly review; quiz_completions is the main first-round success signal.
- writeback：`promotion_post_writeback.py or promotion_profile_writeback.py`

### `guardian_result_clicks`

- category：`route_interest`
- primary source：Website event catalog: guardian_resume_primary, guardian_resume_profile, home_resume_guardian, guide_resume_guardian, guardian_map_card
- trackers：kpi-tracker.csv, platform-kpi-tracker.csv, platform-profile-tracker.csv
- required proof：site event count or checked-zero proof note tied to the same UTM row.
- zero policy：`yes_after_site_source_check`；0 can inform route ordering only after minimum decision fields are also checked.
- decision use：Supports route sequencing after quiz completion exists; does not justify paid-product production by itself.
- writeback：`promotion_post_writeback.py, promotion_profile_writeback.py, or weekly review rollup`

### `resources_clicks`

- category：`route_interest`
- primary source：Website event catalog: quiz_result_supply_route, home_resume_supply_route, guardian_hero_supply_route, supply_quick_route, supply_entry_routes, home_saved_pack_link, supply_pack_link
- trackers：kpi-tracker.csv, platform-kpi-tracker.csv, platform-profile-tracker.csv
- required proof：site event count or checked-zero proof note tied to the same UTM row.
- zero policy：`yes_after_site_source_check`；0 can inform route ordering only after minimum decision fields are also checked.
- decision use：Supports route sequencing after quiz completion exists; does not justify paid-product production by itself.
- writeback：`promotion_post_writeback.py, promotion_profile_writeback.py, or weekly review rollup`

### `repair_plan_clicks`

- category：`route_interest`
- primary source：Website event catalog: quiz_result_repair_plan, home_resume_repair_plan, repair_resume_plan, practice_card_repair_plan
- trackers：kpi-tracker.csv, platform-kpi-tracker.csv, platform-profile-tracker.csv
- required proof：site event count or checked-zero proof note tied to the same UTM row.
- zero policy：`yes_after_site_source_check`；0 can inform route ordering only after minimum decision fields are also checked.
- decision use：Supports route sequencing after quiz completion exists; does not justify paid-product production by itself.
- writeback：`promotion_post_writeback.py, promotion_profile_writeback.py, or weekly review rollup`

### `luna_clicks`

- category：`route_interest`
- primary source：Website event catalog: quiz_result_luna, home_resume_luna, guardian_resume_luna, luna_offer_resources, luna_use_case_action, home_saved_pack_luna, supply_pack_luna
- trackers：kpi-tracker.csv, platform-kpi-tracker.csv, platform-profile-tracker.csv
- required proof：site event count or checked-zero proof note tied to the same UTM row.
- zero policy：`yes_after_site_source_check`；0 can inform route ordering only after minimum decision fields are also checked.
- decision use：Supports route sequencing after quiz completion exists; does not justify paid-product production by itself.
- writeback：`promotion_post_writeback.py, promotion_profile_writeback.py, or weekly review rollup`

### `keepsake_clicks`

- category：`route_interest`
- primary source：Website event catalog: quiz_result_keepsake, home_resume_keepsake, keepsake_resume_story_open, practice_card_supply_route
- trackers：kpi-tracker.csv, platform-kpi-tracker.csv, platform-profile-tracker.csv
- required proof：site event count or checked-zero proof note tied to the same UTM row.
- zero policy：`yes_after_site_source_check`；0 can inform route ordering only after minimum decision fields are also checked.
- decision use：Supports route sequencing after quiz completion exists; does not justify paid-product production by itself.
- writeback：`promotion_post_writeback.py, promotion_profile_writeback.py, or weekly review rollup`

### `free_keepsake_downloads`

- category：`route_interest`
- primary source：Website event catalog: free_keepsake_download, collector_story_download, keepsake_resume_story_download, practice_card_print, home_saved_pack_free_keepsake, supply_pack_free_keepsake
- trackers：kpi-tracker.csv, platform-kpi-tracker.csv, platform-profile-tracker.csv
- required proof：site event count or checked-zero proof note tied to the same UTM row.
- zero policy：`yes_after_site_source_check`；0 can inform route ordering only after minimum decision fields are also checked.
- decision use：Supports route sequencing after quiz completion exists; does not justify paid-product production by itself.
- writeback：`promotion_post_writeback.py, promotion_profile_writeback.py, or weekly review rollup`

### `supply_lead_requests`

- category：`lead_or_revenue_intent`
- primary source：lead-intake-tracker.csv plus traceable consent/evidence; optional matching UTM attribution.
- trackers：kpi-tracker.csv, platform-kpi-tracker.csv, platform-profile-tracker.csv, lead-intake-tracker.csv
- required proof：real user request, explicit_reply_ok consent, traceable email/thread/proof note, and safe notes without raw sensitive content.
- zero policy：`no_without_review`；Do not write fake 0 demand from silence; keep blank until the lead window is reviewed, then document checked-zero separately.
- decision use：Can open owned asset or Luna experiments only after repeated same-guardian demand and matching gates.
- writeback：`promotion_lead_writeback.py`

### `luna_pack_clicks`

- category：`lead_or_revenue_intent`
- primary source：lead-intake-tracker.csv plus traceable consent/evidence; optional matching UTM attribution.
- trackers：kpi-tracker.csv, platform-kpi-tracker.csv, platform-profile-tracker.csv, lead-intake-tracker.csv
- required proof：real user request, explicit_reply_ok consent, traceable email/thread/proof note, and safe notes without raw sensitive content.
- zero policy：`no_without_review`；Do not write fake 0 demand from silence; keep blank until the lead window is reviewed, then document checked-zero separately.
- decision use：Can open owned asset or Luna experiments only after repeated same-guardian demand and matching gates.
- writeback：`promotion_lead_writeback.py`

### `affiliate_book_clicks`

- category：`route_interest`
- primary source：Website event catalog: supply_route_affiliate_book, quiz_result_affiliate_book, repair_guardian_affiliate_book, repair_resume_affiliate_book
- trackers：kpi-tracker.csv, platform-kpi-tracker.csv, platform-profile-tracker.csv
- required proof：site event count or checked-zero proof note tied to the same UTM row.
- zero policy：`yes_after_site_source_check`；0 can inform route ordering only after minimum decision fields are also checked.
- decision use：Supports route sequencing after quiz completion exists; does not justify paid-product production by itself.
- writeback：`promotion_post_writeback.py, promotion_profile_writeback.py, or weekly review rollup`

### `contact_requests`

- category：`lead_or_revenue_intent`
- primary source：lead-intake-tracker.csv plus traceable consent/evidence; optional matching UTM attribution.
- trackers：kpi-tracker.csv, platform-kpi-tracker.csv, platform-profile-tracker.csv, lead-intake-tracker.csv
- required proof：real user request, explicit_reply_ok consent, traceable email/thread/proof note, and safe notes without raw sensitive content.
- zero policy：`no_without_review`；Do not write fake 0 demand from silence; keep blank until the lead window is reviewed, then document checked-zero separately.
- decision use：Can open owned asset or Luna experiments only after repeated same-guardian demand and matching gates.
- writeback：`promotion_lead_writeback.py`
