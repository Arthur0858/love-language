# LoveTypes Profile Setup Handoff Pack

- 產生日期：2026-06-21
- platforms：1
- ready to configure：0
- ready to writeback：0
- configured：1
- public ready：1
- pending evidence checks：6
- proof template ready rows：1
- proof placeholder rows：1
- proof real ready rows：0
- issues：0

## Rules

- Use this handoff pack as the single operator view for platform profile setup.
- Public-ready means the LoveTypes /start/ URL works; it does not prove the external platform profile is set.
- Run checkCommand before writeCommand, and only after replacing proof placeholders with real screenshot/click proof.
- Do not publish first-batch Shorts until all active tracker statuses are set or live.
- Keep all profile copy quiz-only; do not add Luna, affiliate, paid, diagnosis, or treatment claims.

## YouTube Shorts（`youtube_shorts`）

- tracker status：`set`
- action status：`complete`
- proof status：`complete`
- proof placeholder：`1`
- proof real ready：`0`
- public ready：`1`
- link location：Channel description / video description
- profile link：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
- identity / evidence checks：7 / 6
- pending evidence checks：6

### Bio

```text
LoveTypes Heart-Language Garden | Take the 15-question quiz to find your emotional guardian.
```

### Pinned / First Comment

```text
Take the 15-question quiz to find your emotional guardian: https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
Comment A/B/C and we will point you to a guardian route.
```

### Proof Text

Save to `docs/promotion/first-round/proof-youtube_shorts.txt` after real platform verification:

```text
LoveTypes profile setup writeback
platform: youtube_shorts
status: set
set_date: 2026-06-21
profile_link: https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
proof_note: <REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified
```

- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts.txt`
- write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`
- stop：Stop if account/profile is not visibly LoveTypes, edit permission is missing, /start/ UTM is changed, or Bio copy adds paid/diagnosis claims.
