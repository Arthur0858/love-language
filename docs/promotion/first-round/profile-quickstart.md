# LoveTypes Profile Quickstart

- 產生日期：2026-06-14
- platforms：3
- ready to configure：3
- ready to writeback：0
- configured：0
- pending evidence checks：18
- issues：0

## Rules

- Only complete profile setup when the external platform profile visibly contains the tracked /start/ link.
- Use the profile proof text after replacing the proof placeholder with real evidence.
- Run the check command before the write command.
- Do not publish first-batch posts until all three profile links are set or live.
- Keep profile copy focused on the 15-question quiz; do not add paid, affiliate, diagnosis, or treatment claims.

## YouTube Shorts（`youtube_shorts`）

- current status：`planned`
- action status：`ready_to_configure`
- link location：Channel description / video description
- profile link：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
- identity / evidence checks：7 / 6
- pending evidence checks：6
- proof file：`docs/promotion/first-round/proof-youtube_shorts.txt`

Bio:

```text
LoveTypes 心語庭園｜完成 15 題測驗，找到你的情感守護者。
```

Pinned / first comment:

```text
完成 15 題測驗，找到你的情感守護者：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
留言 A/B/C，我們會用守護者路線回覆你。
```

Proof text to save after real platform verification:

```text
LoveTypes profile setup writeback
platform: youtube_shorts
status: set
set_date: 2026-06-14
profile_link: https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
proof_note: <REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified
```

- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts.txt`
- write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`
- stop：Stop if account/profile is not visibly LoveTypes, edit permission is missing, /start/ UTM is changed, or Bio copy adds paid/diagnosis claims.

## TikTok（`tiktok`）

- current status：`planned`
- action status：`ready_to_configure`
- link location：Profile website link
- profile link：https://lovetypes.tw/start/?utm_source=tiktok&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=tiktok_bio
- identity / evidence checks：7 / 6
- pending evidence checks：6
- proof file：`docs/promotion/first-round/proof-tiktok.txt`

Bio:

```text
五種愛之語測驗｜進入心語庭園，找到你的情感守護者。
```

Pinned / first comment:

```text
完成 15 題測驗，找到你的情感守護者。入口在個人頁連結。
留言 A/B/C，選出最像你的心語。
```

Proof text to save after real platform verification:

```text
LoveTypes profile setup writeback
platform: tiktok
status: set
set_date: 2026-06-14
profile_link: https://lovetypes.tw/start/?utm_source=tiktok&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=tiktok_bio
proof_note: <REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified
```

- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-tiktok.txt`
- write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-tiktok.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`
- stop：Stop if account/profile is not visibly LoveTypes, edit permission is missing, /start/ UTM is changed, or Bio copy adds paid/diagnosis claims.

## Instagram Reels（`instagram_reels`）

- current status：`planned`
- action status：`ready_to_configure`
- link location：Profile link in bio
- profile link：https://lovetypes.tw/start/?utm_source=instagram&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=instagram_reels_bio
- identity / evidence checks：7 / 6
- pending evidence checks：6
- proof file：`docs/promotion/first-round/proof-instagram_reels.txt`

Bio:

```text
LoveTypes 心語庭園｜15 題找到你的情感守護者。
```

Pinned / first comment:

```text
完成 15 題測驗，找到你的情感守護者。入口在個人檔案連結。
留言你的 A/B/C，讓守護者把心語接住。
```

Proof text to save after real platform verification:

```text
LoveTypes profile setup writeback
platform: instagram_reels
status: set
set_date: 2026-06-14
profile_link: https://lovetypes.tw/start/?utm_source=instagram&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=instagram_reels_bio
proof_note: <REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified
```

- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-instagram_reels.txt`
- write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-instagram_reels.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`
- stop：Stop if account/profile is not visibly LoveTypes, edit permission is missing, /start/ UTM is changed, or Bio copy adds paid/diagnosis claims.
