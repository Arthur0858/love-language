# LoveTypes Profile-to-Post Alignment Checklist

- 產生日期：2026-07-17
- platforms：1
- first-batch posts：1
- checklist rows：8
- complete rows：8
- pending operator rows：0
- missing rows：0
- 用途：發布第一批 YouTube Shorts 前，確認平台 profile link 與貼文 CTA/UTM 對齊。

## Rule

- 啟用平台 profile link 必須先設為 live/configured，才進入發布。
- 第一批貼文只推測驗，不把 Luna、聯盟書卷或付費商品放成第一 CTA。
- `utm_content` 必須保留，否則後續 KPI 與守護者路線無法回填。

## youtube_shorts

- task：`publish-lt-s01-iris-silence`
- guardian：`iris`
- profile link：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence

- [x] `profile_link_points_to_start`：Profile link points to /start/（complete）
- [x] `profile_utm_is_platform_specific`：Profile UTM is platform-specific（complete）
- [x] `profile_status_configured`：Profile status is set/live（complete）
- [x] `post_link_points_to_start`：Post tracked URL points to /start/（complete）
- [x] `post_utm_content_preserved`：Post UTM content is preserved（complete）
- [x] `primary_cta_is_quiz`：Primary CTA stays quiz-first（complete）
- [x] `no_commerce_first_cta`：No commerce first CTA（complete）
- [x] `guardian_consistent`：Guardian route is consistent（complete）
