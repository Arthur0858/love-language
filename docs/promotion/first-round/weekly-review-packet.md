# LoveTypes Weekly Review Packet

- 產生日期：2026-06-24
- weekly decision ready：0
- empty data mode：0
- first batch published：1 / 1
- first batch minimum KPI rows：0
- tracker rows：0
- profile tracker rows：1
- issues：0

## Hold Reasons

- 首批尚無 site_clicks / quiz_starts / quiz_completions 回填列。

## Required Review Fields

### Minimum
- `post_url`
- `site_clicks`
- `quiz_starts`
- `quiz_completions`

### Route
- `guardian_result_clicks`
- `resources_clicks`
- `repair_plan_clicks`
- `luna_clicks`
- `keepsake_clicks`

### Revenue
- `free_keepsake_downloads`
- `supply_lead_requests`
- `luna_pack_clicks`
- `affiliate_book_clicks`
- `contact_requests`

## Rows To Update

### youtube_shorts · `publish-lt-s01-iris-silence`

- script：`lt-s01-iris-silence`
- status：`published`
- post URL：https://www.youtube.com/watch?v=uj9ZwYIKDrE
- writeback：`python3 tools/promotion_post_writeback.py update --platform youtube_shorts --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-24 --post-url <REAL_YOUTUBE_SHORTS_URL> --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "<REAL_ANALYTICS_SOURCE_PROOF_NOTE> verified"`

## Allowed Decisions Now

- `publish_or_verify_first_batch`
- `set_profile_links`
- `backfill_minimum_kpis`

## Blocked Decisions

- `change_offer_order`
- `pick_winning_guardian`
- `increase_paid_cta`
- `prioritize_luna_or_affiliate`
- `build_paid_product_from_empty_data`

## Policy

- 至少一個已發布 post_url
- 對應平台列已回填 published_date 與 proof note
- 至少填入 site_clicks、quiz_starts、quiz_completions 或確認為 0
- weekly summary 與 week decision gate 重新產生
- 週回顧只判斷內容與漏斗，不把測驗寫成診斷，不承諾修復結果。
