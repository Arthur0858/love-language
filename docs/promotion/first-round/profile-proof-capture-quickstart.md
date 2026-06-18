# LoveTypes Profile Proof Capture Quickstart

- 產生日期：2026-06-18
- platforms：1
- capture rows：6
- pending evidence rows：6
- proof files / importable templates：1 / 1
- public ready / configured：1 / 1
- artifact required rows：1
- safe writeback rows：0
- writeback blocked rows：1
- profile gate ready：1
- issues：0

## Rules

- Capture proof before writeback; importable text is only a format check.
- Each active platform keeps six optional evidence checks for operator review.
- Use screenshot, clicked public link, screen recording, or platform timestamp as proof.
- Keep the proof note tied to platform and date; do not use generic notes like done or checked.
- After all active profile writebacks, rerun daily ops refresh, profile completion gate, and launch quickstart.

## Capture Steps

### YouTube Shorts (`youtube_shorts`)

- status：`complete`
- profile link location：Channel description / video description
- profile link：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
- proof file：`docs/promotion/first-round/proof-youtube_shorts.txt`
- suggested capture：`profile-youtube_shorts-2026-06-18.png`
- capture artifact required：1
- safe writeback ready：0
- proof note：`<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified`
- required proof-note tokens：screenshot, public URL, clicked, screen recording, verified
- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts.txt`
- proof bundle check：`python3 tools/promotion_profile_batch_import.py --check`
- write after proof：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`
- post-writeback check：`python3 tools/promotion_daily_ops_refresh.py && python3 tools/promotion_profile_completion_gate.py --check && python3 tools/promotion_master_gate.py --check`
- stop：Stop if account/profile is not visibly LoveTypes, edit permission is missing, /start/ UTM is changed, or Bio copy adds paid/diagnosis claims.

Evidence checklist:

- [ ] `platform_account_visible`：The correct platform account/profile page is visible before editing. Notes: profile link 已實際貼到平台個人頁或說明欄。
- [ ] `start_url_resolves`：Clicking or copying the platform link reaches https://lovetypes.tw/start/ without 404. Notes: 從平台畫面點擊或複製連結後，仍可抵達 https://lovetypes.tw/start/。
- [ ] `utm_parameters_preserved`：utm_source, utm_medium, utm_campaign, and utm_content are still present after platform handling. Notes: UTM source / medium / campaign / content 沒有被平台移除或改寫。
- [ ] `profile_link_visible_or_clickable`：The platform profile, website field, description, or pinned comment visibly contains the tracked /start/ link. Notes: Link location: Channel description / video description; URL: https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
- [ ] `proof_note_present`：A traceable proof note exists, such as screenshot filename, public clicked URL, or screen recording filename. Notes: 留下可追溯 proof note，例如平台、設定時間、截圖檔名或手動驗證紀錄。
- [ ] `quiz_only_copy`：Bio/comment copy only promotes the 15-question guardian quiz; no Luna, affiliate, paid, diagnosis, or treatment promise. Notes: Bio 與置頂留言只導向 15 題測驗，沒有導購、療效或診斷承諾。
