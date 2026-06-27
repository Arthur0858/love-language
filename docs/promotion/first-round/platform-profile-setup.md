# LoveTypes 平台首頁設定檢查包

- 產生日期：2026-06-27
- 平台數：1
- 主入口：https://lovetypes.tw/start/
- UTM campaign：`first_round_quiz_completion`

## 使用規則

- 發布第一支 YouTube Shorts 前，先完成 YouTube 頻道首頁設定。
- 首頁 Bio 和置頂留言只導向測驗，不直接導購。
- YouTube 是第一輪英文主渠道；其他平台不列入本輪必備 gate。
- 發布後把 profile_clicks 與 site_clicks 一起回填，才能判斷個人頁承接是否有效。

## YouTube Shorts

- 連結位置：Channel description / video description
- Profile link：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
- 限制備註：YouTube is the first-round English channel; the channel bio, descriptions, and pinned comments can use the full tracking link.

### Bio

```text
LoveTypes Heart-Language Garden | Take the 15-question quiz to find your emotional guardian.
```

### 置頂留言 / 首則留言

```text
Take the 15-question quiz to find your emotional guardian: https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
Comment A/B/C and we will point you to a guardian route.
```

### 發布前檢查

- 發布第一支 Shorts/Reels 前，先確認 profile link 使用平台專屬追蹤連結。
- Bio 不直接導購，只保留測驗與情感守護者入口。
- 置頂留言或首則留言維持單一 CTA：完成 15 題測驗。
- 發布後回填 profile_clicks、site_clicks、quiz_starts、quiz_completions。

### 設定後回填值

- `status`：set
- `profile_link_set_date`：YYYY-MM-DD
- `profile_link`：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
- `notes`：YouTube is the first-round English channel; the channel bio, descriptions, and pinned comments can use the full tracking link.

### 設定後驗證

- 在無痕視窗開啟 profile link，確認會到 /start/ 且沒有 404。
- 確認 URL 保留 utm_source=youtube、utm_medium=social_profile、utm_campaign=first_round_quiz_completion。
- 確認 Bio 或置頂留言只出現測驗 CTA，沒有 Luna、聯盟書卷或療效承諾。
- 設定後先截圖或記錄平台時間，再回填 platform-profile-tracker.csv。

### 未完成前不要發布

- platform-profile-tracker.csv 的 status 已改為 set 或 live。
- profile_link_set_date 已填入設定日期。
- profile link 已手動開啟並確認 UTM 沒被平台截斷。

### KPI 回填欄位

- `profile_clicks`
- `site_clicks`
- `quiz_starts`
- `quiz_completions`
- `guardian_result_clicks`
- `resources_clicks`
- `luna_clicks`

## 商業邊界

- 平台首頁先承接測驗完成量，不直接推 Luna、聯盟書卷或付費商品。
- 不使用：診斷, 療效, 保證修復, 必須購買
