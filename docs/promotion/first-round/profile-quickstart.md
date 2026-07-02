# LoveTypes Profile Quickstart

- 產生日期：2026-07-02
- platforms：1
- ready to configure：0
- ready to writeback：0
- configured：1
- pending evidence checks：6
- issues：0

## Rules

- Only complete profile setup when the external platform profile visibly contains the tracked /start/ link.
- Use the profile proof text after replacing the proof placeholder with real evidence.
- Run the check command before the write command.
- Do not publish first-batch posts until all active profile links are set or live.
- First-round promotion currently uses YouTube Shorts as the only active publishing channel.
- Keep profile copy focused on the 15-question quiz; do not add paid, affiliate, diagnosis, or treatment claims.

## YouTube Shorts（`youtube_shorts`）

- current status：`set`
- action status：`complete`
- link location：Channel description / video description
- profile link：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
- identity / evidence checks：7 / 6
- pending evidence checks：6
- proof file：`docs/promotion/first-round/proof-youtube_shorts.txt`

Bio:

```text
LoveTypes Heart-Language Garden | Take the 15-question quiz to find your emotional guardian.
```

Pinned / first comment:

```text
Take the 15-question quiz to find your emotional guardian: https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
Comment A/B/C and we will point you to a guardian route.
```

Proof text to save after real platform verification:

```text
LoveTypes profile setup writeback
platform: youtube_shorts
status: set
set_date: 2026-07-02
profile_link: https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
proof_note: <REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified
```

- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts.txt`
- write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`
- stop：Stop if account/profile is not visibly LoveTypes, edit permission is missing, /start/ UTM is changed, or Bio copy adds paid/diagnosis claims.
