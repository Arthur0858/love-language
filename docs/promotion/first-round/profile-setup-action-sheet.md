# LoveTypes Profile Setup Action Sheet

- 產生日期：2026-06-14
- platforms：3
- ready to configure：3
- ready to writeback：0
- configured：0
- identity checks：21
- evidence checks：18
- profile gate ready：0
- issues：0

## Rule

- 先確認帳號與公開頁是 LoveTypes，再貼 profile link。
- 每個平台都要完成 7 個帳號身份檢查與 6 個 profile 證據檢查。
- 沒有截圖、公開點擊或可追溯 proof note 時，不回填 `set/live`。

## YouTube Shorts（`youtube_shorts`）

- action status：`ready_to_configure`
- current tracker status：`planned`
- link location：Channel description / video description
- profile link：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
- identity / evidence checks：7 / 6

Bio:

```text
LoveTypes 心語庭園｜完成 15 題測驗，找到你的情感守護者。
```

Pinned / first comment:

```text
完成 15 題測驗，找到你的情感守護者：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
留言 A/B/C，我們會用守護者路線回覆你。
```

- proof file：`docs/promotion/first-round/proof-youtube_shorts.txt`
- proof note：`screenshot profile-youtube_shorts-2026-06-14.png verified`
- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts.txt`
- write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts.txt --proof-note "screenshot profile-youtube_shorts-2026-06-14.png verified"`
- stop：Stop if account/profile is not visibly LoveTypes, edit permission is missing, /start/ UTM is changed, or Bio copy adds paid/diagnosis claims.

## TikTok（`tiktok`）

- action status：`ready_to_configure`
- current tracker status：`planned`
- link location：Profile website link
- profile link：https://lovetypes.tw/start/?utm_source=tiktok&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=tiktok_bio
- identity / evidence checks：7 / 6

Bio:

```text
五種愛之語測驗｜進入心語庭園，找到你的情感守護者。
```

Pinned / first comment:

```text
完成 15 題測驗，找到你的情感守護者。入口在個人頁連結。
留言 A/B/C，選出最像你的心語。
```

- proof file：`docs/promotion/first-round/proof-tiktok.txt`
- proof note：`screenshot profile-tiktok-2026-06-14.png verified`
- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-tiktok.txt`
- write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-tiktok.txt --proof-note "screenshot profile-tiktok-2026-06-14.png verified"`
- stop：Stop if account/profile is not visibly LoveTypes, edit permission is missing, /start/ UTM is changed, or Bio copy adds paid/diagnosis claims.

## Instagram Reels（`instagram_reels`）

- action status：`ready_to_configure`
- current tracker status：`planned`
- link location：Profile link in bio
- profile link：https://lovetypes.tw/start/?utm_source=instagram&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=instagram_reels_bio
- identity / evidence checks：7 / 6

Bio:

```text
LoveTypes 心語庭園｜15 題找到你的情感守護者。
```

Pinned / first comment:

```text
完成 15 題測驗，找到你的情感守護者。入口在個人檔案連結。
留言你的 A/B/C，讓守護者把心語接住。
```

- proof file：`docs/promotion/first-round/proof-instagram_reels.txt`
- proof note：`screenshot profile-instagram_reels-2026-06-14.png verified`
- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-instagram_reels.txt`
- write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-instagram_reels.txt --proof-note "screenshot profile-instagram_reels-2026-06-14.png verified"`
- stop：Stop if account/profile is not visibly LoveTypes, edit permission is missing, /start/ UTM is changed, or Bio copy adds paid/diagnosis claims.
