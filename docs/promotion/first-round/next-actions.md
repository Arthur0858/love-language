# LoveTypes 下一批推廣動作建議

- 產生日期：2026-06-14
- 影片追蹤列數：0
- 平台首頁待設定列數：3 / 3
- 空資料安全模式：是
- 行動選擇規則：Select the first three planned tasks by week and slot, then keep Shorts CTA focused on the 15-question quiz.
- 商品調整 gate：Do not change products, guardian priority, paid CTA, Luna emphasis, or affiliate emphasis until filled KPI rows create quiz, route, lead, Luna, or affiliate intent.

## 優先動作

- [high] 發布 Week 1 前 3 支 Shorts，先取得測驗完成樣本。
- [high] 發布後先回填 post_url、site_clicks、quiz_starts、quiz_completions；有結果後互動時補齊 guardian_result_clicks、resources_clicks、repair_plan_clicks、luna_clicks、keepsake_clicks、free_keepsake_downloads、supply_lead_requests、luna_pack_clicks、affiliate_book_clicks、contact_requests。
- [high] 發布前同步完成 YouTube、TikTok、Instagram 的 Bio/Profile link，使用平台專屬 UTM。
- [high] 平台首頁設定後回填 platform-profile-tracker.csv 的 status、profile_link_set_date、profile_clicks、site_clicks、quiz_starts、quiz_completions。
- [medium] 目前沒有回填數據，不調整商品、守護者優先序或付費 CTA。

## 平台首頁設定

### YouTube Shorts（`youtube_shorts`）

- 連結位置：Channel description / video description
- Profile link：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
- 狀態：`planned`
- Bio：

```text
LoveTypes 心語庭園｜完成 15 題測驗，找到你的情感守護者。
```

- 置頂留言 / 首則留言：

```text
完成 15 題測驗，找到你的情感守護者：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
留言 A/B/C，我們會用守護者路線回覆你。
```

- 設定後回填值：

  - `status`：set
  - `profile_link_set_date`：YYYY-MM-DD
  - `profile_link`：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
  - `notes`：YouTube 說明欄可放完整追蹤連結；置頂留言也放同一條。

- 設定後驗證：

  - 在無痕視窗開啟 profile link，確認會到 /start/ 且沒有 404。
  - 確認 URL 保留 utm_source=youtube、utm_medium=social_profile、utm_campaign=first_round_quiz_completion。
  - 確認 Bio 或置頂留言只出現測驗 CTA，沒有 Luna、聯盟書卷或療效承諾。
  - 設定後先截圖或記錄平台時間，再回填 platform-profile-tracker.csv。

- 未完成前不要發布：

  - platform-profile-tracker.csv 的 status 已改為 set 或 live。
  - profile_link_set_date 已填入設定日期。
  - profile link 已手動開啟並確認 UTM 沒被平台截斷。

- 優先回填欄位：`status`, `profile_link_set_date`, `profile_clicks`, `site_clicks`, `quiz_starts`, `quiz_completions`

### TikTok（`tiktok`）

- 連結位置：Profile website link
- Profile link：https://lovetypes.tw/start/?utm_source=tiktok&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=tiktok_bio
- 狀態：`planned`
- Bio：

```text
五種愛之語測驗｜進入心語庭園，找到你的情感守護者。
```

- 置頂留言 / 首則留言：

```text
完成 15 題測驗，找到你的情感守護者。入口在個人頁連結。
留言 A/B/C，選出最像你的心語。
```

- 設定後回填值：

  - `status`：set
  - `profile_link_set_date`：YYYY-MM-DD
  - `profile_link`：https://lovetypes.tw/start/?utm_source=tiktok&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=tiktok_bio
  - `notes`：若 caption 不能放可點連結，Bio/個人頁連結必須使用平台專屬追蹤連結。

- 設定後驗證：

  - 在無痕視窗開啟 profile link，確認會到 /start/ 且沒有 404。
  - 確認 URL 保留 utm_source=tiktok、utm_medium=social_profile、utm_campaign=first_round_quiz_completion。
  - 確認 Bio 或置頂留言只出現測驗 CTA，沒有 Luna、聯盟書卷或療效承諾。
  - 設定後先截圖或記錄平台時間，再回填 platform-profile-tracker.csv。

- 未完成前不要發布：

  - platform-profile-tracker.csv 的 status 已改為 set 或 live。
  - profile_link_set_date 已填入設定日期。
  - profile link 已手動開啟並確認 UTM 沒被平台截斷。

- 優先回填欄位：`status`, `profile_link_set_date`, `profile_clicks`, `site_clicks`, `quiz_starts`, `quiz_completions`

### Instagram Reels（`instagram_reels`）

- 連結位置：Profile link in bio
- Profile link：https://lovetypes.tw/start/?utm_source=instagram&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=instagram_reels_bio
- 狀態：`planned`
- Bio：

```text
LoveTypes 心語庭園｜15 題找到你的情感守護者。
```

- 置頂留言 / 首則留言：

```text
完成 15 題測驗，找到你的情感守護者。入口在個人檔案連結。
留言你的 A/B/C，讓守護者把心語接住。
```

- 設定後回填值：

  - `status`：set
  - `profile_link_set_date`：YYYY-MM-DD
  - `profile_link`：https://lovetypes.tw/start/?utm_source=instagram&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=instagram_reels_bio
  - `notes`：IG Reels caption 以個人檔案連結承接；Bio 連結需先於發布前更新。

- 設定後驗證：

  - 在無痕視窗開啟 profile link，確認會到 /start/ 且沒有 404。
  - 確認 URL 保留 utm_source=instagram、utm_medium=social_profile、utm_campaign=first_round_quiz_completion。
  - 確認 Bio 或置頂留言只出現測驗 CTA，沒有 Luna、聯盟書卷或療效承諾。
  - 設定後先截圖或記錄平台時間，再回填 platform-profile-tracker.csv。

- 未完成前不要發布：

  - platform-profile-tracker.csv 的 status 已改為 set 或 live。
  - profile_link_set_date 已填入設定日期。
  - profile link 已手動開啟並確認 UTM 沒被平台截斷。

- 優先回填欄位：`status`, `profile_link_set_date`, `profile_clicks`, `site_clicks`, `quiz_starts`, `quiz_completions`

## 建議發布任務

### publish-lt-s01-iris-silence

- Week/Slot：1 / 1
- 守護者：艾莉絲（iris）
- 內容角度：情感錯頻情境
- 標題：他沉默時，你最想聽見哪一句話？
- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence
- 免費資產：free-keepsake-iris
- 名單承接：supply-wishlist-iris
- 補給路線：https://lovetypes.tw/resources/#supply-iris
- Luna：https://lovetypes.tw/luna-yoga-music/#luna-iris
- 收藏物：https://lovetypes.tw/keepsakes/#keepsake-iris

### publish-lt-s02-iris-affirmation

- Week/Slot：1 / 2
- 守護者：艾莉絲（iris）
- 內容角度：守護者人格認同
- 標題：哪一句肯定，會讓你瞬間安心？
- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_affirmation
- 免費資產：free-keepsake-iris
- 名單承接：supply-wishlist-iris
- 補給路線：https://lovetypes.tw/resources/#supply-iris
- Luna：https://lovetypes.tw/luna-yoga-music/#luna-iris
- 收藏物：https://lovetypes.tw/keepsakes/#keepsake-iris

### publish-lt-s03-iris-too-sensitive

- Week/Slot：1 / 3
- 守護者：艾莉絲（iris）
- 內容角度：測驗入口
- 標題：你真的太敏感嗎？還是你只是等一句清楚的話？
- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_too_sensitive
- 免費資產：free-keepsake-iris
- 名單承接：supply-wishlist-iris
- 補給路線：https://lovetypes.tw/resources/#supply-iris
- Luna：https://lovetypes.tw/luna-yoga-music/#luna-iris
- 收藏物：https://lovetypes.tw/keepsakes/#keepsake-iris

## 安全邊界

- Shorts CTA 維持測驗，不直接導購。
- 平台首頁 Bio/Profile link 也維持測驗，不直接導購。
- 不把守護者結果描述成診斷、療效或保證修復。
- 空資料時不調整商品、守護者優先序或付費 CTA。
