# LoveTypes Weekly Review Packet

- 產生日期：2026-06-14
- weekly decision ready：0
- empty data mode：1
- first batch published：0 / 3
- first batch minimum KPI rows：0
- tracker rows：0
- profile tracker rows：0
- issues：0

## Hold Reasons

- 首批三平台尚無公開 post URL。
- 首批尚無 site_clicks / quiz_starts / quiz_completions 回填列。
- publishing-status 尚未達週決策條件。
- 目前仍是空資料模式，不能調整商品、付費 CTA、Luna 或聯盟優先序。

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
- status：`planned`
- post URL：(pending)
- writeback：`python3 tools/promotion_post_writeback.py update --platform youtube_shorts --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-14 --post-url https://www.youtube.com/shorts/replace-with-real-post-url --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "post URL and first metrics verified"`

### tiktok · `publish-lt-s01-iris-silence`

- script：`lt-s01-iris-silence`
- status：`planned`
- post URL：(pending)
- writeback：`python3 tools/promotion_post_writeback.py update --platform tiktok --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-14 --post-url https://www.youtube.com/shorts/replace-with-real-post-url --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "post URL and first metrics verified"`

### instagram_reels · `publish-lt-s01-iris-silence`

- script：`lt-s01-iris-silence`
- status：`planned`
- post URL：(pending)
- writeback：`python3 tools/promotion_post_writeback.py update --platform instagram_reels --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-14 --post-url https://www.youtube.com/shorts/replace-with-real-post-url --site-clicks 0 --quiz-starts 0 --quiz-completions 0 --proof-note "post URL and first metrics verified"`

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
