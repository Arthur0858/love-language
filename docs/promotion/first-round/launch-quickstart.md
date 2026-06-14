# LoveTypes Launch Quickstart

- 產生日期：2026-06-14
- current stage：`profile_setup`
- stage current blockers：1
- profile configured：0
- first batch published：0
- minimum KPI rows：0
- real leads / ready offers：0 / 0
- command ready / blocked decisions：6 / 18
- clipboard ready / blocked：3 / 3
- issues：0

## Rules

- Current allowed work is profile setup only unless the master gate advances.
- Run check commands before write commands, then refresh daily ops after real writeback.
- Profile proof must be real external evidence: screenshot, clicked public link, or timestamped platform proof.
- Publishing, KPI, Luna, affiliate, and paid offer experiments remain blocked while profileConfigured is 0.
- Do not use empty KPI or lead data to choose winning guardians or commercial direction.

## Now: Profile Setup Only

### YouTube Shorts (`youtube_shorts`)

- status：`ready_to_configure`
- profile link：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
- proof file：`docs/promotion/first-round/proof-youtube_shorts.txt`
- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts.txt`
- write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`
- stop：Stop if account/profile is not visibly LoveTypes, edit permission is missing, /start/ UTM is changed, or Bio copy adds paid/diagnosis claims.

### TikTok (`tiktok`)

- status：`ready_to_configure`
- profile link：https://lovetypes.tw/start/?utm_source=tiktok&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=tiktok_bio
- proof file：`docs/promotion/first-round/proof-tiktok.txt`
- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-tiktok.txt`
- write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-tiktok.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`
- stop：Stop if account/profile is not visibly LoveTypes, edit permission is missing, /start/ UTM is changed, or Bio copy adds paid/diagnosis claims.

### Instagram Reels (`instagram_reels`)

- status：`ready_to_configure`
- profile link：https://lovetypes.tw/start/?utm_source=instagram&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=instagram_reels_bio
- proof file：`docs/promotion/first-round/proof-instagram_reels.txt`
- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-instagram_reels.txt`
- write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-instagram_reels.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`
- stop：Stop if account/profile is not visibly LoveTypes, edit permission is missing, /start/ UTM is changed, or Bio copy adds paid/diagnosis claims.

## Next: Still Blocked

- `publish` / `blocked_until_profile_links`：First three platform posts；current：0 ready / 3 blocked；check：`python3 tools/promotion_first_batch_publish_quickstart.py --check`；stop：Do not publish until all three profile links are set/live and proof is written back.
- `kpi` / `blocked_until_public_post_url`：First-batch minimum KPI backfill；current：0 ready / 3 blocked；check：`python3 tools/promotion_first_batch_kpi_quickstart.py --check`；stop：Do not write KPI values until public post URLs and analytics source proof exist.
- `lead_offer` / `blocked_until_real_leads`：Lead, asset, Luna, and offer decisions；current：0 real leads / 0 ready offers；check：`python3 tools/promotion_lead_offer_quickstart.py --check`；stop：Do not create paid or priority offer experiments without repeated traceable demand.
