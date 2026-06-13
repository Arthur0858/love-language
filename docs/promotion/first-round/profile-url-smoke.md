# LoveTypes Profile URL Smoke

- 產生日期：2026-06-14
- Profile URLs：3
- Structural pass：3
- Public checked：0
- Public pass：0

## 邊界

- 這份檢查只驗證三個平台 Bio/Profile 目標網址與 UTM 規格。
- 它不代表 YouTube、TikTok、Instagram 已經完成設定；完成設定仍以 profile proof 與 tracker 回填為準。
- 預設不打公開站；需要公開可達性時執行 `python3 tools/promotion_profile_url_smoke.py --public --check`。

## URLs

### YouTube Shorts

- platform：`youtube_shorts`
- URL：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
- utm：`youtube` / `social_profile` / `first_round_quiz_completion` / `youtube_shorts_bio`
- structural：`pass`
- public：`not_checked`
- notes：Destination URL smoke only. This does not prove the profile link is configured on the platform.

### TikTok

- platform：`tiktok`
- URL：https://lovetypes.tw/start/?utm_source=tiktok&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=tiktok_bio
- utm：`tiktok` / `social_profile` / `first_round_quiz_completion` / `tiktok_bio`
- structural：`pass`
- public：`not_checked`
- notes：Destination URL smoke only. This does not prove the profile link is configured on the platform.

### Instagram Reels

- platform：`instagram_reels`
- URL：https://lovetypes.tw/start/?utm_source=instagram&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=instagram_reels_bio
- utm：`instagram` / `social_profile` / `first_round_quiz_completion` / `instagram_reels_bio`
- structural：`pass`
- public：`not_checked`
- notes：Destination URL smoke only. This does not prove the profile link is configured on the platform.
