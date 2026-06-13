# LoveTypes 平台首頁 KPI 追蹤表

- 產生日期：2026-06-14
- 平台數：3
- 用途：追蹤 Bio/Profile link 帶來的測驗與收益承接，不和單支 Shorts 成效混在一起。
- 狀態規則：`planned`, `set`, `live`, `paused`, `blocked`；`set/live` 必須填 `profile_link_set_date`。
- 每週最小回填欄位：`profile_clicks`, `site_clicks`, `quiz_starts`, `quiz_completions`。

## 使用方式

- 完成平台首頁設定後，把 `status` 改成 `set` 或 `live`，並填入 `profile_link_set_date`。
- 每週回填 `profile_clicks`、`site_clicks`、`quiz_starts`、`quiz_completions`。
- 若 Bio/Profile link 也帶來收藏、補給、Luna、聯盟或 Contact 意圖，回填對應欄位。
- 單支影片成效仍回填 `kpi-tracker.csv`；本表只看平台首頁承接。

## 平台

### YouTube Shorts（`youtube_shorts`）

- 狀態：`planned`
- Profile link：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
- UTM：`youtube / social_profile / first_round_quiz_completion / youtube_shorts_bio`
- 設定日期：尚未回填
- 備註：YouTube 說明欄可放完整追蹤連結；置頂留言也放同一條。

### TikTok（`tiktok`）

- 狀態：`planned`
- Profile link：https://lovetypes.tw/start/?utm_source=tiktok&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=tiktok_bio
- UTM：`tiktok / social_profile / first_round_quiz_completion / tiktok_bio`
- 設定日期：尚未回填
- 備註：若 caption 不能放可點連結，Bio/個人頁連結必須使用平台專屬追蹤連結。

### Instagram Reels（`instagram_reels`）

- 狀態：`planned`
- Profile link：https://lovetypes.tw/start/?utm_source=instagram&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=instagram_reels_bio
- UTM：`instagram / social_profile / first_round_quiz_completion / instagram_reels_bio`
- 設定日期：尚未回填
- 備註：IG Reels caption 以個人檔案連結承接；Bio 連結需先於發布前更新。
