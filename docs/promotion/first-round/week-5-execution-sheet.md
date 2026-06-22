# LoveTypes Week 5 推廣執行單

- 產生日期：2026-06-23
- 平台首頁 gate：0 待設定 / 1
- 平台發布任務：3
- 腳本數：3
- 主 CTA：完成 15 題測驗，找到你的情感守護者

## 執行順序

1. 完成 YouTube channel profile link 設定。
2. 依本週三支腳本完成影片輸出或剪輯手卡交付。
3. 依任務時間發布到 YouTube Shorts。
4. 先回填 posting-queue.csv，再回填 platform-kpi-tracker.csv 的最小 KPI；有結果後互動時補齊守護者、補給、Luna、收藏、名單與聯盟欄位。
5. 週回顧時才彙總 kpi-tracker.csv，平台首頁成效另回填 platform-profile-tracker.csv。
6. 跑 promotion_publishing_status.py；未達週決策門檻前不調整商品或付費 CTA。

## 發布前平台首頁 Gate

### YouTube Shorts（`youtube_shorts`）

- 狀態：已設定 / `set`
- 連結位置：Channel description / video description
- Profile link：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
- Bio：

```text
LoveTypes Heart-Language Garden | Take the 15-question quiz to find your emotional guardian.
```

- 置頂留言 / 首則留言：

```text
Take the 15-question quiz to find your emotional guardian: https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
Comment A/B/C and we will point you to a guardian route.
```

- 回填：`status=set/live`, `profile_link_set_date`, `profile_clicks`, `site_clicks`, `quiz_starts`, `quiz_completions`

## 本週三支腳本與平台發布

### 你不是太黏，你只是用身體最先感覺到距離

- 任務：`publish-lt-s13-dora-distance`
- 腳本：`lt-s13-dora-distance`
- 守護者：朵拉（`dora`）
- 內容角度：情感錯頻情境
- UTM content：`dora_distance`

#### YouTube Shorts · 2026-07-13 20:30 Asia/Taipei

- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=dora_distance
- Caption：

```text
有些不安不是想太多，是身體先發現對方退後了。

Take the 15-question quiz to find your emotional guardian: https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=dora_distance

留言 A/B/C，哪一種靠近最能讓你安心？
#LoveLanguages #RelationshipQuiz #EmotionalGuardian #HeartLanguage #LoveTypes
```

- 回填：`posting-queue.csv: status=published`, `posting-queue.csv: published_date`, `posting-queue.csv: post_url`, `platform-kpi-tracker.csv: post_url`, `platform-kpi-tracker.csv: site_clicks`, `platform-kpi-tracker.csv: quiz_starts`, `platform-kpi-tracker.csv: quiz_completions`, `platform-kpi-tracker.csv: guardian_result_clicks`, `platform-kpi-tracker.csv: resources_clicks`, `platform-kpi-tracker.csv: repair_plan_clicks`, `platform-kpi-tracker.csv: luna_clicks`, `platform-kpi-tracker.csv: keepsake_clicks`, `platform-kpi-tracker.csv: free_keepsake_downloads`, `platform-kpi-tracker.csv: supply_lead_requests`, `platform-kpi-tracker.csv: luna_pack_clicks`, `platform-kpi-tracker.csv: affiliate_book_clicks`, `platform-kpi-tracker.csv: contact_requests`
- 最小 KPI：`platform-kpi-tracker.csv: post_url`、`platform-kpi-tracker.csv: site_clicks`、`platform-kpi-tracker.csv: quiz_starts`、`platform-kpi-tracker.csv: quiz_completions`
- 結果後互動：`platform-kpi-tracker.csv: guardian_result_clicks`、`platform-kpi-tracker.csv: resources_clicks`、`platform-kpi-tracker.csv: repair_plan_clicks`、`platform-kpi-tracker.csv: luna_clicks`、`platform-kpi-tracker.csv: keepsake_clicks`、`platform-kpi-tracker.csv: free_keepsake_downloads`、`platform-kpi-tracker.csv: supply_lead_requests`、`platform-kpi-tracker.csv: luna_pack_clicks`、`platform-kpi-tracker.csv: affiliate_book_clicks`、`platform-kpi-tracker.csv: contact_requests`

### 真正溫柔的靠近，會先問你願不願意

- 任務：`publish-lt-s14-dora-consent`
- 腳本：`lt-s14-dora-consent`
- 守護者：朵拉（`dora`）
- 內容角度：守護者人格認同
- UTM content：`dora_consent`

#### YouTube Shorts · 2026-07-15 20:30 Asia/Taipei

- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=dora_consent
- Caption：

```text
身體接觸的愛，不是要求對方配合，而是讓彼此都安心。

Take the 15-question quiz to find your emotional guardian: https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=dora_consent

留言 A/B/C，你最想聽見哪一句安全靠近？
#LoveLanguages #RelationshipQuiz #EmotionalGuardian #HeartLanguage #LoveTypes
```

- 回填：`posting-queue.csv: status=published`, `posting-queue.csv: published_date`, `posting-queue.csv: post_url`, `platform-kpi-tracker.csv: post_url`, `platform-kpi-tracker.csv: site_clicks`, `platform-kpi-tracker.csv: quiz_starts`, `platform-kpi-tracker.csv: quiz_completions`, `platform-kpi-tracker.csv: guardian_result_clicks`, `platform-kpi-tracker.csv: resources_clicks`, `platform-kpi-tracker.csv: repair_plan_clicks`, `platform-kpi-tracker.csv: luna_clicks`, `platform-kpi-tracker.csv: keepsake_clicks`, `platform-kpi-tracker.csv: free_keepsake_downloads`, `platform-kpi-tracker.csv: supply_lead_requests`, `platform-kpi-tracker.csv: luna_pack_clicks`, `platform-kpi-tracker.csv: affiliate_book_clicks`, `platform-kpi-tracker.csv: contact_requests`
- 最小 KPI：`platform-kpi-tracker.csv: post_url`、`platform-kpi-tracker.csv: site_clicks`、`platform-kpi-tracker.csv: quiz_starts`、`platform-kpi-tracker.csv: quiz_completions`
- 結果後互動：`platform-kpi-tracker.csv: guardian_result_clicks`、`platform-kpi-tracker.csv: resources_clicks`、`platform-kpi-tracker.csv: repair_plan_clicks`、`platform-kpi-tracker.csv: luna_clicks`、`platform-kpi-tracker.csv: keepsake_clicks`、`platform-kpi-tracker.csv: free_keepsake_downloads`、`platform-kpi-tracker.csv: supply_lead_requests`、`platform-kpi-tracker.csv: luna_pack_clicks`、`platform-kpi-tracker.csv: affiliate_book_clicks`、`platform-kpi-tracker.csv: contact_requests`

### 吵架後，你需要多久才能重新靠近？

- 任務：`publish-lt-s15-dora-after-conflict`
- 腳本：`lt-s15-dora-after-conflict`
- 守護者：朵拉（`dora`）
- 內容角度：測驗入口
- UTM content：`dora_after_conflict`

#### YouTube Shorts · 2026-07-17 20:30 Asia/Taipei

- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=dora_after_conflict
- Caption：

```text
有些人不是不想和好，而是身體還沒感覺安全。

Take the 15-question quiz to find your emotional guardian: https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=dora_after_conflict

留言 A/B/C，吵架後你是哪一種靠近節奏？
#LoveLanguages #RelationshipQuiz #EmotionalGuardian #HeartLanguage #LoveTypes
```

- 回填：`posting-queue.csv: status=published`, `posting-queue.csv: published_date`, `posting-queue.csv: post_url`, `platform-kpi-tracker.csv: post_url`, `platform-kpi-tracker.csv: site_clicks`, `platform-kpi-tracker.csv: quiz_starts`, `platform-kpi-tracker.csv: quiz_completions`, `platform-kpi-tracker.csv: guardian_result_clicks`, `platform-kpi-tracker.csv: resources_clicks`, `platform-kpi-tracker.csv: repair_plan_clicks`, `platform-kpi-tracker.csv: luna_clicks`, `platform-kpi-tracker.csv: keepsake_clicks`, `platform-kpi-tracker.csv: free_keepsake_downloads`, `platform-kpi-tracker.csv: supply_lead_requests`, `platform-kpi-tracker.csv: luna_pack_clicks`, `platform-kpi-tracker.csv: affiliate_book_clicks`, `platform-kpi-tracker.csv: contact_requests`
- 最小 KPI：`platform-kpi-tracker.csv: post_url`、`platform-kpi-tracker.csv: site_clicks`、`platform-kpi-tracker.csv: quiz_starts`、`platform-kpi-tracker.csv: quiz_completions`
- 結果後互動：`platform-kpi-tracker.csv: guardian_result_clicks`、`platform-kpi-tracker.csv: resources_clicks`、`platform-kpi-tracker.csv: repair_plan_clicks`、`platform-kpi-tracker.csv: luna_clicks`、`platform-kpi-tracker.csv: keepsake_clicks`、`platform-kpi-tracker.csv: free_keepsake_downloads`、`platform-kpi-tracker.csv: supply_lead_requests`、`platform-kpi-tracker.csv: luna_pack_clicks`、`platform-kpi-tracker.csv: affiliate_book_clicks`、`platform-kpi-tracker.csv: contact_requests`

## 安全邊界

- Shorts 與平台首頁都只導向測驗，不直接導購。
- 不使用診斷、療效、保證修復或必須購買說法。
- 沒有足夠回填前，不調整守護者優先序、商品承接或付費 CTA。
