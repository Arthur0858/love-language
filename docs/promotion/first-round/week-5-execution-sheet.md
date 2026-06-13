# LoveTypes Week 5 推廣執行單

- 產生日期：2026-06-13
- 平台首頁 gate：3 待設定 / 3
- 平台發布任務：9
- 腳本數：3
- 主 CTA：完成 15 題測驗，找到你的情感守護者

## 執行順序

1. 完成三平台 Bio/Profile link 設定。
2. 依本週三支腳本完成影片輸出或剪輯手卡交付。
3. 依平台任務時間發布到 YouTube Shorts、TikTok、Instagram Reels。
4. 先回填 posting-queue.csv，再回填 platform-kpi-tracker.csv；週回顧時才彙總 kpi-tracker.csv，平台首頁成效另回填 platform-profile-tracker.csv。
5. 跑 promotion_publishing_status.py；未達週決策門檻前不調整商品或付費 CTA。

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

完成 15 題測驗，找到你的情感守護者：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=dora_distance

留言 A/B/C，哪一種靠近最能讓你安心？
#五種愛之語測驗 #情感守護者 #心語庭園 #錯頻修復 #LoveTypes
```

- 回填：`posting-queue.csv: status=published`, `posting-queue.csv: published_date`, `posting-queue.csv: post_url`, `platform-kpi-tracker.csv: post_url`, `platform-kpi-tracker.csv: site_clicks`, `platform-kpi-tracker.csv: quiz_starts`, `platform-kpi-tracker.csv: quiz_completions`

#### TikTok · 2026-07-13 21:00 Asia/Taipei

- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=dora_distance
- Caption：

```text
有些不安不是想太多，是身體先發現對方退後了。

首頁連結完成 15 題測驗：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=dora_distance

留言 A/B/C，哪一種靠近最能讓你安心？
#五種愛之語測驗 #情感守護者 #心語庭園 #錯頻修復 #LoveTypes
```

- 回填：`posting-queue.csv: status=published`, `posting-queue.csv: published_date`, `posting-queue.csv: post_url`, `platform-kpi-tracker.csv: post_url`, `platform-kpi-tracker.csv: site_clicks`, `platform-kpi-tracker.csv: quiz_starts`, `platform-kpi-tracker.csv: quiz_completions`

#### Instagram Reels · 2026-07-13 21:30 Asia/Taipei

- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=dora_distance
- Caption：

```text
有些不安不是想太多，是身體先發現對方退後了。

個人檔案連結完成 15 題測驗：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=dora_distance

留言 A/B/C，哪一種靠近最能讓你安心？
#五種愛之語測驗 #情感守護者 #心語庭園 #錯頻修復 #LoveTypes
```

- 回填：`posting-queue.csv: status=published`, `posting-queue.csv: published_date`, `posting-queue.csv: post_url`, `platform-kpi-tracker.csv: post_url`, `platform-kpi-tracker.csv: site_clicks`, `platform-kpi-tracker.csv: quiz_starts`, `platform-kpi-tracker.csv: quiz_completions`

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

完成 15 題測驗，找到你的情感守護者：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=dora_consent

留言 A/B/C，你最想聽見哪一句安全靠近？
#五種愛之語測驗 #情感守護者 #心語庭園 #錯頻修復 #LoveTypes
```

- 回填：`posting-queue.csv: status=published`, `posting-queue.csv: published_date`, `posting-queue.csv: post_url`, `platform-kpi-tracker.csv: post_url`, `platform-kpi-tracker.csv: site_clicks`, `platform-kpi-tracker.csv: quiz_starts`, `platform-kpi-tracker.csv: quiz_completions`

#### TikTok · 2026-07-15 21:00 Asia/Taipei

- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=dora_consent
- Caption：

```text
身體接觸的愛，不是要求對方配合，而是讓彼此都安心。

首頁連結完成 15 題測驗：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=dora_consent

留言 A/B/C，你最想聽見哪一句安全靠近？
#五種愛之語測驗 #情感守護者 #心語庭園 #錯頻修復 #LoveTypes
```

- 回填：`posting-queue.csv: status=published`, `posting-queue.csv: published_date`, `posting-queue.csv: post_url`, `platform-kpi-tracker.csv: post_url`, `platform-kpi-tracker.csv: site_clicks`, `platform-kpi-tracker.csv: quiz_starts`, `platform-kpi-tracker.csv: quiz_completions`

#### Instagram Reels · 2026-07-15 21:30 Asia/Taipei

- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=dora_consent
- Caption：

```text
身體接觸的愛，不是要求對方配合，而是讓彼此都安心。

個人檔案連結完成 15 題測驗：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=dora_consent

留言 A/B/C，你最想聽見哪一句安全靠近？
#五種愛之語測驗 #情感守護者 #心語庭園 #錯頻修復 #LoveTypes
```

- 回填：`posting-queue.csv: status=published`, `posting-queue.csv: published_date`, `posting-queue.csv: post_url`, `platform-kpi-tracker.csv: post_url`, `platform-kpi-tracker.csv: site_clicks`, `platform-kpi-tracker.csv: quiz_starts`, `platform-kpi-tracker.csv: quiz_completions`

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

完成 15 題測驗，找到你的情感守護者：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=dora_after_conflict

留言 A/B/C，吵架後你是哪一種靠近節奏？
#五種愛之語測驗 #情感守護者 #心語庭園 #錯頻修復 #LoveTypes
```

- 回填：`posting-queue.csv: status=published`, `posting-queue.csv: published_date`, `posting-queue.csv: post_url`, `platform-kpi-tracker.csv: post_url`, `platform-kpi-tracker.csv: site_clicks`, `platform-kpi-tracker.csv: quiz_starts`, `platform-kpi-tracker.csv: quiz_completions`

#### TikTok · 2026-07-17 21:00 Asia/Taipei

- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=dora_after_conflict
- Caption：

```text
有些人不是不想和好，而是身體還沒感覺安全。

首頁連結完成 15 題測驗：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=dora_after_conflict

留言 A/B/C，吵架後你是哪一種靠近節奏？
#五種愛之語測驗 #情感守護者 #心語庭園 #錯頻修復 #LoveTypes
```

- 回填：`posting-queue.csv: status=published`, `posting-queue.csv: published_date`, `posting-queue.csv: post_url`, `platform-kpi-tracker.csv: post_url`, `platform-kpi-tracker.csv: site_clicks`, `platform-kpi-tracker.csv: quiz_starts`, `platform-kpi-tracker.csv: quiz_completions`

#### Instagram Reels · 2026-07-17 21:30 Asia/Taipei

- 追蹤連結：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=dora_after_conflict
- Caption：

```text
有些人不是不想和好，而是身體還沒感覺安全。

個人檔案連結完成 15 題測驗：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=dora_after_conflict

留言 A/B/C，吵架後你是哪一種靠近節奏？
#五種愛之語測驗 #情感守護者 #心語庭園 #錯頻修復 #LoveTypes
```

- 回填：`posting-queue.csv: status=published`, `posting-queue.csv: published_date`, `posting-queue.csv: post_url`, `platform-kpi-tracker.csv: post_url`, `platform-kpi-tracker.csv: site_clicks`, `platform-kpi-tracker.csv: quiz_starts`, `platform-kpi-tracker.csv: quiz_completions`

## 安全邊界

- Shorts 與平台首頁都只導向測驗，不直接導購。
- 不使用診斷、療效、保證修復或必須購買說法。
- 沒有足夠回填前，不調整守護者優先序、商品承接或付費 CTA。
