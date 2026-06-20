# LoveTypes Profile Setup Action Sheet

- 產生日期：2026-06-20
- platforms：1
- ready to configure：0
- ready to writeback：0
- configured：1
- identity checks：7
- evidence checks：6
- profile gate ready：1
- issues：0

## Rule

- 先確認帳號與公開頁是 LoveTypes，再貼 profile link。
- 每個平台都要完成 7 個帳號身份檢查與 6 個 profile 證據檢查。
- 沒有截圖、公開點擊或可追溯 proof note 時，不回填 `set/live`。

## YouTube Shorts（`youtube_shorts`）

- action status：`complete`
- current tracker status：`set`
- link location：Channel description / video description
- profile link：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
- identity / evidence checks：7 / 6

Bio:

```text
LoveTypes Heart-Language Garden | Take the 15-question quiz to find your emotional guardian.
```

Pinned / first comment:

```text
Take the 15-question quiz to find your emotional guardian: https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
Comment A/B/C and we will point you to a guardian route.
```

- proof file：`docs/promotion/first-round/proof-youtube_shorts.txt`
- suggested proof note：`<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified`
- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts.txt`
- write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`
- stop：Stop if account/profile is not visibly LoveTypes, edit permission is missing, /start/ UTM is changed, or Bio copy adds paid/diagnosis claims.
