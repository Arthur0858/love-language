# LoveTypes Week 4 推廣執行單

- 產生日期：2026-06-14
- 平台首頁 gate：3 待設定 / 3
- 平台發布任務：9
- 腳本數：3
- 主 CTA：完成 15 題測驗，找到你的情感守護者

## 執行順序

1. 完成三平台 Bio/Profile link 設定。
2. 依本週三支腳本完成影片輸出或剪輯手卡交付。
3. 依平台任務時間發布到 YouTube Shorts、TikTok、Instagram Reels。
4. 先回填 posting-queue.csv，再回填 platform-kpi-tracker.csv 的最小 KPI；有結果後互動時補齊守護者、補給、Luna、收藏、名單與聯盟欄位。
5. 週回顧時才彙總 kpi-tracker.csv，平台首頁成效另回填 platform-profile-tracker.csv。
6. 跑 promotion_publishing_status.py；未達週決策門檻前不調整商品或付費 CTA。

## 發布前平台首頁 Gate

### YouTube Shorts（`youtube_shorts`）

- 狀態：待設定 / `planned`
- 連結位置：Channel description / video description
- Profile link：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
- Bio：

```text
LoveTypes 心語庭園｜完成 15 題測驗，找到你的情感守護者。
```

- 置頂留言 / 首則留言：

```text
完成 15 題測驗，找到你的情感守護者：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
留言 A/B/C，我們會用守護者路線回覆你。
```

- 回填：`status=set/live`, `profile_link_set_date`, `profile_clicks`, `site_clicks`, `quiz_starts`, `quiz_completions`

### TikTok（`tiktok`）

- 狀態：待設定 / `planned`
- 連結位置：Profile website link
- Profile link：https://lovetypes.tw/start/?utm_source=tiktok&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=tiktok_bio
- Bio：

```text
五種愛之語測驗｜進入心語庭園，找到你的情感守護者。
```

- 置頂留言 / 首則留言：

```text
完成 15 題測驗，找到你的情感守護者。入口在個人頁連結。
留言 A/B/C，選出最像你的心語。
```

- 回填：`status=set/live`, `profile_link_set_date`, `profile_clicks`, `site_clicks`, `quiz_starts`, `quiz_completions`

### Instagram Reels（`instagram_reels`）

- 狀態：待設定 / `planned`
- 連結位置：Profile link in bio
- Profile link：https://lovetypes.tw/start/?utm_source=instagram&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=instagram_reels_bio
- Bio：

```text
LoveTypes 心語庭園｜15 題找到你的情感守護者。
```

- 置頂留言 / 首則留言：

```text
完成 15 題測驗，找到你的情感守護者。入口在個人檔案連結。
留言你的 A/B/C，讓守護者把心語接住。
```

- 回填：`status=set/live`, `profile_link_set_date`, `profile_clicks`, `site_clicks`, `quiz_starts`, `quiz_completions`

## 本週三支腳本與平台發布

### 你不是愛計較，你只是太久沒人主動幫你

- 任務：`publish-lt-s10-claire-tired`
- 腳本：`lt-s10-claire-tired`
- 守護者：克萊兒（`claire`）
- 內容角度：情感錯頻情境
- UTM content：`claire_tired`

#### YouTube Shorts · 2026-07-06 20:30 Asia/Taipei

- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=claire_tired
- Caption：

```text
如果每一次都是你收拾，那不是成熟，是失衡。

完成 15 題測驗，找到你的情感守護者：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=claire_tired

留言 A/B/C，你最希望有人替你分擔哪一件事？
#五種愛之語測驗 #情感守護者 #心語庭園 #錯頻修復 #LoveTypes
```

- 回填：`posting-queue.csv: status=published`, `posting-queue.csv: published_date`, `posting-queue.csv: post_url`, `platform-kpi-tracker.csv: post_url`, `platform-kpi-tracker.csv: site_clicks`, `platform-kpi-tracker.csv: quiz_starts`, `platform-kpi-tracker.csv: quiz_completions`, `platform-kpi-tracker.csv: guardian_result_clicks`, `platform-kpi-tracker.csv: resources_clicks`, `platform-kpi-tracker.csv: repair_plan_clicks`, `platform-kpi-tracker.csv: luna_clicks`, `platform-kpi-tracker.csv: keepsake_clicks`, `platform-kpi-tracker.csv: free_keepsake_downloads`, `platform-kpi-tracker.csv: supply_lead_requests`, `platform-kpi-tracker.csv: luna_pack_clicks`, `platform-kpi-tracker.csv: affiliate_book_clicks`, `platform-kpi-tracker.csv: contact_requests`
- 最小 KPI：`platform-kpi-tracker.csv: post_url`、`platform-kpi-tracker.csv: site_clicks`、`platform-kpi-tracker.csv: quiz_starts`、`platform-kpi-tracker.csv: quiz_completions`
- 結果後互動：`platform-kpi-tracker.csv: guardian_result_clicks`、`platform-kpi-tracker.csv: resources_clicks`、`platform-kpi-tracker.csv: repair_plan_clicks`、`platform-kpi-tracker.csv: luna_clicks`、`platform-kpi-tracker.csv: keepsake_clicks`、`platform-kpi-tracker.csv: free_keepsake_downloads`、`platform-kpi-tracker.csv: supply_lead_requests`、`platform-kpi-tracker.csv: luna_pack_clicks`、`platform-kpi-tracker.csv: affiliate_book_clicks`、`platform-kpi-tracker.csv: contact_requests`

#### TikTok · 2026-07-06 21:00 Asia/Taipei

- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=claire_tired
- Caption：

```text
如果每一次都是你收拾，那不是成熟，是失衡。

首頁連結完成 15 題測驗：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=claire_tired

留言 A/B/C，你最希望有人替你分擔哪一件事？
#五種愛之語測驗 #情感守護者 #心語庭園 #錯頻修復 #LoveTypes
```

- 回填：`posting-queue.csv: status=published`, `posting-queue.csv: published_date`, `posting-queue.csv: post_url`, `platform-kpi-tracker.csv: post_url`, `platform-kpi-tracker.csv: site_clicks`, `platform-kpi-tracker.csv: quiz_starts`, `platform-kpi-tracker.csv: quiz_completions`, `platform-kpi-tracker.csv: guardian_result_clicks`, `platform-kpi-tracker.csv: resources_clicks`, `platform-kpi-tracker.csv: repair_plan_clicks`, `platform-kpi-tracker.csv: luna_clicks`, `platform-kpi-tracker.csv: keepsake_clicks`, `platform-kpi-tracker.csv: free_keepsake_downloads`, `platform-kpi-tracker.csv: supply_lead_requests`, `platform-kpi-tracker.csv: luna_pack_clicks`, `platform-kpi-tracker.csv: affiliate_book_clicks`, `platform-kpi-tracker.csv: contact_requests`
- 最小 KPI：`platform-kpi-tracker.csv: post_url`、`platform-kpi-tracker.csv: site_clicks`、`platform-kpi-tracker.csv: quiz_starts`、`platform-kpi-tracker.csv: quiz_completions`
- 結果後互動：`platform-kpi-tracker.csv: guardian_result_clicks`、`platform-kpi-tracker.csv: resources_clicks`、`platform-kpi-tracker.csv: repair_plan_clicks`、`platform-kpi-tracker.csv: luna_clicks`、`platform-kpi-tracker.csv: keepsake_clicks`、`platform-kpi-tracker.csv: free_keepsake_downloads`、`platform-kpi-tracker.csv: supply_lead_requests`、`platform-kpi-tracker.csv: luna_pack_clicks`、`platform-kpi-tracker.csv: affiliate_book_clicks`、`platform-kpi-tracker.csv: contact_requests`

#### Instagram Reels · 2026-07-06 21:30 Asia/Taipei

- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=claire_tired
- Caption：

```text
如果每一次都是你收拾，那不是成熟，是失衡。

個人檔案連結完成 15 題測驗：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=claire_tired

留言 A/B/C，你最希望有人替你分擔哪一件事？
#五種愛之語測驗 #情感守護者 #心語庭園 #錯頻修復 #LoveTypes
```

- 回填：`posting-queue.csv: status=published`, `posting-queue.csv: published_date`, `posting-queue.csv: post_url`, `platform-kpi-tracker.csv: post_url`, `platform-kpi-tracker.csv: site_clicks`, `platform-kpi-tracker.csv: quiz_starts`, `platform-kpi-tracker.csv: quiz_completions`, `platform-kpi-tracker.csv: guardian_result_clicks`, `platform-kpi-tracker.csv: resources_clicks`, `platform-kpi-tracker.csv: repair_plan_clicks`, `platform-kpi-tracker.csv: luna_clicks`, `platform-kpi-tracker.csv: keepsake_clicks`, `platform-kpi-tracker.csv: free_keepsake_downloads`, `platform-kpi-tracker.csv: supply_lead_requests`, `platform-kpi-tracker.csv: luna_pack_clicks`, `platform-kpi-tracker.csv: affiliate_book_clicks`, `platform-kpi-tracker.csv: contact_requests`
- 最小 KPI：`platform-kpi-tracker.csv: post_url`、`platform-kpi-tracker.csv: site_clicks`、`platform-kpi-tracker.csv: quiz_starts`、`platform-kpi-tracker.csv: quiz_completions`
- 結果後互動：`platform-kpi-tracker.csv: guardian_result_clicks`、`platform-kpi-tracker.csv: resources_clicks`、`platform-kpi-tracker.csv: repair_plan_clicks`、`platform-kpi-tracker.csv: luna_clicks`、`platform-kpi-tracker.csv: keepsake_clicks`、`platform-kpi-tracker.csv: free_keepsake_downloads`、`platform-kpi-tracker.csv: supply_lead_requests`、`platform-kpi-tracker.csv: luna_pack_clicks`、`platform-kpi-tracker.csv: affiliate_book_clicks`、`platform-kpi-tracker.csv: contact_requests`

### 他說會改，卻一直沒有行動

- 任務：`publish-lt-s11-claire-promises`
- 腳本：`lt-s11-claire-promises`
- 守護者：克萊兒（`claire`）
- 內容角度：守護者人格認同
- UTM content：`claire_promises`

#### YouTube Shorts · 2026-07-08 20:30 Asia/Taipei

- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=claire_promises
- Caption：

```text
對克萊兒來說，真正的承諾會變成你不用一個人完成的事。

完成 15 題測驗，找到你的情感守護者：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=claire_promises

留言 A/B/C，哪一種只說不做最讓你累？
#五種愛之語測驗 #情感守護者 #心語庭園 #錯頻修復 #LoveTypes
```

- 回填：`posting-queue.csv: status=published`, `posting-queue.csv: published_date`, `posting-queue.csv: post_url`, `platform-kpi-tracker.csv: post_url`, `platform-kpi-tracker.csv: site_clicks`, `platform-kpi-tracker.csv: quiz_starts`, `platform-kpi-tracker.csv: quiz_completions`, `platform-kpi-tracker.csv: guardian_result_clicks`, `platform-kpi-tracker.csv: resources_clicks`, `platform-kpi-tracker.csv: repair_plan_clicks`, `platform-kpi-tracker.csv: luna_clicks`, `platform-kpi-tracker.csv: keepsake_clicks`, `platform-kpi-tracker.csv: free_keepsake_downloads`, `platform-kpi-tracker.csv: supply_lead_requests`, `platform-kpi-tracker.csv: luna_pack_clicks`, `platform-kpi-tracker.csv: affiliate_book_clicks`, `platform-kpi-tracker.csv: contact_requests`
- 最小 KPI：`platform-kpi-tracker.csv: post_url`、`platform-kpi-tracker.csv: site_clicks`、`platform-kpi-tracker.csv: quiz_starts`、`platform-kpi-tracker.csv: quiz_completions`
- 結果後互動：`platform-kpi-tracker.csv: guardian_result_clicks`、`platform-kpi-tracker.csv: resources_clicks`、`platform-kpi-tracker.csv: repair_plan_clicks`、`platform-kpi-tracker.csv: luna_clicks`、`platform-kpi-tracker.csv: keepsake_clicks`、`platform-kpi-tracker.csv: free_keepsake_downloads`、`platform-kpi-tracker.csv: supply_lead_requests`、`platform-kpi-tracker.csv: luna_pack_clicks`、`platform-kpi-tracker.csv: affiliate_book_clicks`、`platform-kpi-tracker.csv: contact_requests`

#### TikTok · 2026-07-08 21:00 Asia/Taipei

- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=claire_promises
- Caption：

```text
對克萊兒來說，真正的承諾會變成你不用一個人完成的事。

首頁連結完成 15 題測驗：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=claire_promises

留言 A/B/C，哪一種只說不做最讓你累？
#五種愛之語測驗 #情感守護者 #心語庭園 #錯頻修復 #LoveTypes
```

- 回填：`posting-queue.csv: status=published`, `posting-queue.csv: published_date`, `posting-queue.csv: post_url`, `platform-kpi-tracker.csv: post_url`, `platform-kpi-tracker.csv: site_clicks`, `platform-kpi-tracker.csv: quiz_starts`, `platform-kpi-tracker.csv: quiz_completions`, `platform-kpi-tracker.csv: guardian_result_clicks`, `platform-kpi-tracker.csv: resources_clicks`, `platform-kpi-tracker.csv: repair_plan_clicks`, `platform-kpi-tracker.csv: luna_clicks`, `platform-kpi-tracker.csv: keepsake_clicks`, `platform-kpi-tracker.csv: free_keepsake_downloads`, `platform-kpi-tracker.csv: supply_lead_requests`, `platform-kpi-tracker.csv: luna_pack_clicks`, `platform-kpi-tracker.csv: affiliate_book_clicks`, `platform-kpi-tracker.csv: contact_requests`
- 最小 KPI：`platform-kpi-tracker.csv: post_url`、`platform-kpi-tracker.csv: site_clicks`、`platform-kpi-tracker.csv: quiz_starts`、`platform-kpi-tracker.csv: quiz_completions`
- 結果後互動：`platform-kpi-tracker.csv: guardian_result_clicks`、`platform-kpi-tracker.csv: resources_clicks`、`platform-kpi-tracker.csv: repair_plan_clicks`、`platform-kpi-tracker.csv: luna_clicks`、`platform-kpi-tracker.csv: keepsake_clicks`、`platform-kpi-tracker.csv: free_keepsake_downloads`、`platform-kpi-tracker.csv: supply_lead_requests`、`platform-kpi-tracker.csv: luna_pack_clicks`、`platform-kpi-tracker.csv: affiliate_book_clicks`、`platform-kpi-tracker.csv: contact_requests`

#### Instagram Reels · 2026-07-08 21:30 Asia/Taipei

- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=claire_promises
- Caption：

```text
對克萊兒來說，真正的承諾會變成你不用一個人完成的事。

個人檔案連結完成 15 題測驗：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=claire_promises

留言 A/B/C，哪一種只說不做最讓你累？
#五種愛之語測驗 #情感守護者 #心語庭園 #錯頻修復 #LoveTypes
```

- 回填：`posting-queue.csv: status=published`, `posting-queue.csv: published_date`, `posting-queue.csv: post_url`, `platform-kpi-tracker.csv: post_url`, `platform-kpi-tracker.csv: site_clicks`, `platform-kpi-tracker.csv: quiz_starts`, `platform-kpi-tracker.csv: quiz_completions`, `platform-kpi-tracker.csv: guardian_result_clicks`, `platform-kpi-tracker.csv: resources_clicks`, `platform-kpi-tracker.csv: repair_plan_clicks`, `platform-kpi-tracker.csv: luna_clicks`, `platform-kpi-tracker.csv: keepsake_clicks`, `platform-kpi-tracker.csv: free_keepsake_downloads`, `platform-kpi-tracker.csv: supply_lead_requests`, `platform-kpi-tracker.csv: luna_pack_clicks`, `platform-kpi-tracker.csv: affiliate_book_clicks`, `platform-kpi-tracker.csv: contact_requests`
- 最小 KPI：`platform-kpi-tracker.csv: post_url`、`platform-kpi-tracker.csv: site_clicks`、`platform-kpi-tracker.csv: quiz_starts`、`platform-kpi-tracker.csv: quiz_completions`
- 結果後互動：`platform-kpi-tracker.csv: guardian_result_clicks`、`platform-kpi-tracker.csv: resources_clicks`、`platform-kpi-tracker.csv: repair_plan_clicks`、`platform-kpi-tracker.csv: luna_clicks`、`platform-kpi-tracker.csv: keepsake_clicks`、`platform-kpi-tracker.csv: free_keepsake_downloads`、`platform-kpi-tracker.csv: supply_lead_requests`、`platform-kpi-tracker.csv: luna_pack_clicks`、`platform-kpi-tracker.csv: affiliate_book_clicks`、`platform-kpi-tracker.csv: contact_requests`

### 你是不是很不習慣開口求助？

- 任務：`publish-lt-s12-claire-ask-help`
- 腳本：`lt-s12-claire-ask-help`
- 守護者：克萊兒（`claire`）
- 內容角度：測驗入口
- UTM content：`claire_ask_help`

#### YouTube Shorts · 2026-07-10 20:30 Asia/Taipei

- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=claire_ask_help
- Caption：

```text
你不是不需要被照顧，你只是太習慣先照顧別人。

完成 15 題測驗，找到你的情感守護者：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=claire_ask_help

留言 A/B/C，或寫下一件你其實很想被幫忙的事。
#五種愛之語測驗 #情感守護者 #心語庭園 #錯頻修復 #LoveTypes
```

- 回填：`posting-queue.csv: status=published`, `posting-queue.csv: published_date`, `posting-queue.csv: post_url`, `platform-kpi-tracker.csv: post_url`, `platform-kpi-tracker.csv: site_clicks`, `platform-kpi-tracker.csv: quiz_starts`, `platform-kpi-tracker.csv: quiz_completions`, `platform-kpi-tracker.csv: guardian_result_clicks`, `platform-kpi-tracker.csv: resources_clicks`, `platform-kpi-tracker.csv: repair_plan_clicks`, `platform-kpi-tracker.csv: luna_clicks`, `platform-kpi-tracker.csv: keepsake_clicks`, `platform-kpi-tracker.csv: free_keepsake_downloads`, `platform-kpi-tracker.csv: supply_lead_requests`, `platform-kpi-tracker.csv: luna_pack_clicks`, `platform-kpi-tracker.csv: affiliate_book_clicks`, `platform-kpi-tracker.csv: contact_requests`
- 最小 KPI：`platform-kpi-tracker.csv: post_url`、`platform-kpi-tracker.csv: site_clicks`、`platform-kpi-tracker.csv: quiz_starts`、`platform-kpi-tracker.csv: quiz_completions`
- 結果後互動：`platform-kpi-tracker.csv: guardian_result_clicks`、`platform-kpi-tracker.csv: resources_clicks`、`platform-kpi-tracker.csv: repair_plan_clicks`、`platform-kpi-tracker.csv: luna_clicks`、`platform-kpi-tracker.csv: keepsake_clicks`、`platform-kpi-tracker.csv: free_keepsake_downloads`、`platform-kpi-tracker.csv: supply_lead_requests`、`platform-kpi-tracker.csv: luna_pack_clicks`、`platform-kpi-tracker.csv: affiliate_book_clicks`、`platform-kpi-tracker.csv: contact_requests`

#### TikTok · 2026-07-10 21:00 Asia/Taipei

- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=claire_ask_help
- Caption：

```text
你不是不需要被照顧，你只是太習慣先照顧別人。

首頁連結完成 15 題測驗：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=claire_ask_help

留言 A/B/C，或寫下一件你其實很想被幫忙的事。
#五種愛之語測驗 #情感守護者 #心語庭園 #錯頻修復 #LoveTypes
```

- 回填：`posting-queue.csv: status=published`, `posting-queue.csv: published_date`, `posting-queue.csv: post_url`, `platform-kpi-tracker.csv: post_url`, `platform-kpi-tracker.csv: site_clicks`, `platform-kpi-tracker.csv: quiz_starts`, `platform-kpi-tracker.csv: quiz_completions`, `platform-kpi-tracker.csv: guardian_result_clicks`, `platform-kpi-tracker.csv: resources_clicks`, `platform-kpi-tracker.csv: repair_plan_clicks`, `platform-kpi-tracker.csv: luna_clicks`, `platform-kpi-tracker.csv: keepsake_clicks`, `platform-kpi-tracker.csv: free_keepsake_downloads`, `platform-kpi-tracker.csv: supply_lead_requests`, `platform-kpi-tracker.csv: luna_pack_clicks`, `platform-kpi-tracker.csv: affiliate_book_clicks`, `platform-kpi-tracker.csv: contact_requests`
- 最小 KPI：`platform-kpi-tracker.csv: post_url`、`platform-kpi-tracker.csv: site_clicks`、`platform-kpi-tracker.csv: quiz_starts`、`platform-kpi-tracker.csv: quiz_completions`
- 結果後互動：`platform-kpi-tracker.csv: guardian_result_clicks`、`platform-kpi-tracker.csv: resources_clicks`、`platform-kpi-tracker.csv: repair_plan_clicks`、`platform-kpi-tracker.csv: luna_clicks`、`platform-kpi-tracker.csv: keepsake_clicks`、`platform-kpi-tracker.csv: free_keepsake_downloads`、`platform-kpi-tracker.csv: supply_lead_requests`、`platform-kpi-tracker.csv: luna_pack_clicks`、`platform-kpi-tracker.csv: affiliate_book_clicks`、`platform-kpi-tracker.csv: contact_requests`

#### Instagram Reels · 2026-07-10 21:30 Asia/Taipei

- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=claire_ask_help
- Caption：

```text
你不是不需要被照顧，你只是太習慣先照顧別人。

個人檔案連結完成 15 題測驗：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=claire_ask_help

留言 A/B/C，或寫下一件你其實很想被幫忙的事。
#五種愛之語測驗 #情感守護者 #心語庭園 #錯頻修復 #LoveTypes
```

- 回填：`posting-queue.csv: status=published`, `posting-queue.csv: published_date`, `posting-queue.csv: post_url`, `platform-kpi-tracker.csv: post_url`, `platform-kpi-tracker.csv: site_clicks`, `platform-kpi-tracker.csv: quiz_starts`, `platform-kpi-tracker.csv: quiz_completions`, `platform-kpi-tracker.csv: guardian_result_clicks`, `platform-kpi-tracker.csv: resources_clicks`, `platform-kpi-tracker.csv: repair_plan_clicks`, `platform-kpi-tracker.csv: luna_clicks`, `platform-kpi-tracker.csv: keepsake_clicks`, `platform-kpi-tracker.csv: free_keepsake_downloads`, `platform-kpi-tracker.csv: supply_lead_requests`, `platform-kpi-tracker.csv: luna_pack_clicks`, `platform-kpi-tracker.csv: affiliate_book_clicks`, `platform-kpi-tracker.csv: contact_requests`
- 最小 KPI：`platform-kpi-tracker.csv: post_url`、`platform-kpi-tracker.csv: site_clicks`、`platform-kpi-tracker.csv: quiz_starts`、`platform-kpi-tracker.csv: quiz_completions`
- 結果後互動：`platform-kpi-tracker.csv: guardian_result_clicks`、`platform-kpi-tracker.csv: resources_clicks`、`platform-kpi-tracker.csv: repair_plan_clicks`、`platform-kpi-tracker.csv: luna_clicks`、`platform-kpi-tracker.csv: keepsake_clicks`、`platform-kpi-tracker.csv: free_keepsake_downloads`、`platform-kpi-tracker.csv: supply_lead_requests`、`platform-kpi-tracker.csv: luna_pack_clicks`、`platform-kpi-tracker.csv: affiliate_book_clicks`、`platform-kpi-tracker.csv: contact_requests`

## 安全邊界

- Shorts 與平台首頁都只導向測驗，不直接導購。
- 不使用診斷、療效、保證修復或必須購買說法。
- 沒有足夠回填前，不調整守護者優先序、商品承接或付費 CTA。
