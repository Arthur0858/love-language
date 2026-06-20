# LoveTypes Launch Quickstart

- 產生日期：2026-06-21
- current stage：`first_batch_publish`
- stage current blockers：1
- profile configured：1
- first batch published：0
- minimum KPI rows：0
- real leads / ready offers：0 / 0
- command ready / blocked decisions：3 / 3
- clipboard ready / blocked：1 / 0
- issues：0

## Rules

- Current allowed work is profile setup only unless the master gate advances.
- Run check commands before write commands, then refresh daily ops after real writeback.
- Profile proof must be real external evidence: screenshot, clicked public link, or timestamped platform proof.
- Publishing opens only after active profile rows are configured; KPI, Luna, affiliate, and paid offer experiments remain blocked until public post evidence exists.
- Do not use empty KPI or lead data to choose winning guardians or commercial direction.

## Now: Profile Setup Only

### YouTube Shorts (`youtube_shorts`)

- status：`complete`
- profile link：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
- proof file：`docs/promotion/first-round/proof-youtube_shorts.txt`
- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts.txt`
- write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`
- stop：Stop if account/profile is not visibly LoveTypes, edit permission is missing, /start/ UTM is changed, or Bio copy adds paid/diagnosis claims.

## Next: Still Blocked

- `publish` / `blocked_until_profile_links`：First YouTube Shorts post；current：1 ready / 0 blocked；check：`python3 tools/promotion_first_batch_publish_quickstart.py --check`；stop：Do not publish until all active profile links are set/live and proof is written back.
- `kpi` / `blocked_until_public_post_url`：First-batch minimum KPI backfill；current：0 ready / 1 blocked；check：`python3 tools/promotion_first_batch_kpi_quickstart.py --check`；stop：Do not write KPI values until public post URLs and analytics source proof exist.
- `lead_offer` / `blocked_until_real_leads`：Lead, asset, Luna, and offer decisions；current：0 real leads / 0 ready offers；check：`python3 tools/promotion_lead_offer_quickstart.py --check`；stop：Do not create paid or priority offer experiments without repeated traceable demand.
