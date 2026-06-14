# LoveTypes Profile Writeback Closure Quickstart

- 產生日期：2026-06-14
- platforms：3
- pending evidence rows：18
- configured：0 / 3
- completion ready：0
- handoff ready to publish：0
- launch ready to publish：0
- master stage index：0
- issues：0

## Rules

- Do not run any add/writeback command until all six evidence checks for that platform are true.
- Use profile_text_import add only with a real proof note; scaffold screenshot names must be replaced by real evidence.
- After each writeback, run daily ops refresh before trusting downstream quickstarts.
- Publish can open only when profile completion, profile handoff, launch readiness, and master gate all agree.
- If any gate stays closed after writeback, stop and inspect that gate instead of publishing manually.

## Closure Steps

- `capture_evidence` / `current`：`python3 tools/promotion_profile_proof_capture_quickstart.py --check`
  Stop: Stop if any required evidence row remains unverified for the platform you plan to write back.
- `writeback_profile_rows` / `blocked_until_evidence`：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-<platform>.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`
  Stop: Stop if the proof note is generic, scaffold-only, missing, or not tied to platform/date.
- `refresh_ops_docs` / `blocked_until_writeback`：`python3 tools/promotion_daily_ops_refresh.py`
  Stop: Do not publish from stale generated packets after tracker writeback.
- `verify_profile_gates` / `blocked_until_refresh`：`python3 tools/promotion_profile_completion_gate.py --check && python3 tools/promotion_profile_publish_handoff.py --check && python3 tools/promotion_launch_readiness_gate.py --check`
  Stop: Publish only when all profile gates agree ready_to_publish is open.
- `open_first_batch_publish` / `blocked_until_profile_gate`：`python3 tools/promotion_first_batch_publish_quickstart.py --check`
  Stop: Do not publish if any first-batch row remains blocked_until_profile_links.

## Platform Writeback Commands

### YouTube Shorts (`youtube_shorts`)

- current status：`planned`
- pending evidence：6
- profile link：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
- proof file：`docs/promotion/first-round/proof-youtube_shorts.txt`
- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts.txt`
- text import write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`
- direct set：`python3 tools/promotion_profile_writeback.py update --platform youtube_shorts --status set --set-date 2026-06-14 --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`
- direct live：`python3 tools/promotion_profile_writeback.py update --platform youtube_shorts --status live --set-date 2026-06-14 --proof-note "<REAL_PROFILE_CLICK_NOTE> verified"`
- stop：Stop if account/profile is not visibly LoveTypes, edit permission is missing, /start/ UTM is changed, or Bio copy adds paid/diagnosis claims.

### TikTok (`tiktok`)

- current status：`planned`
- pending evidence：6
- profile link：https://lovetypes.tw/start/?utm_source=tiktok&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=tiktok_bio
- proof file：`docs/promotion/first-round/proof-tiktok.txt`
- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-tiktok.txt`
- text import write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-tiktok.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`
- direct set：`python3 tools/promotion_profile_writeback.py update --platform tiktok --status set --set-date 2026-06-14 --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`
- direct live：`python3 tools/promotion_profile_writeback.py update --platform tiktok --status live --set-date 2026-06-14 --proof-note "<REAL_PROFILE_CLICK_NOTE> verified"`
- stop：Stop if account/profile is not visibly LoveTypes, edit permission is missing, /start/ UTM is changed, or Bio copy adds paid/diagnosis claims.

### Instagram Reels (`instagram_reels`)

- current status：`planned`
- pending evidence：6
- profile link：https://lovetypes.tw/start/?utm_source=instagram&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=instagram_reels_bio
- proof file：`docs/promotion/first-round/proof-instagram_reels.txt`
- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-instagram_reels.txt`
- text import write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-instagram_reels.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`
- direct set：`python3 tools/promotion_profile_writeback.py update --platform instagram_reels --status set --set-date 2026-06-14 --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`
- direct live：`python3 tools/promotion_profile_writeback.py update --platform instagram_reels --status live --set-date 2026-06-14 --proof-note "<REAL_PROFILE_CLICK_NOTE> verified"`
- stop：Stop if account/profile is not visibly LoveTypes, edit permission is missing, /start/ UTM is changed, or Bio copy adds paid/diagnosis claims.
