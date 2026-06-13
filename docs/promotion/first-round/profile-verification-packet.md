# LoveTypes Profile Verification Packet

- 產生日期：2026-06-13
- platforms：3
- configured：0
- pending：3
- ready_to_publish：0
- issues：0

## Gate

- Do not publish first batch until all three profile links are set/live and readiness ready_to_publish is true.
- Profile copy keeps the CTA on the 15-question guardian quiz and does not promote Luna, books, or paid products first.
- 不用本文件偽造 profile 設定、post URL 或 KPI；只在外部平台完成後回填。

## YouTube Shorts（`youtube_shorts`）

- current status：`planned`
- configured：0
- profile link：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
- link location：Channel description / video description

### Bio

```text
LoveTypes 心語庭園｜完成 15 題測驗，找到你的情感守護者。
```

### Pinned / First Comment

```text
完成 15 題測驗，找到你的情感守護者：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
留言 A/B/C，我們會用守護者路線回覆你。
```

### Evidence Required

- profile link 已實際貼到平台個人頁或說明欄。
- 從平台畫面點擊或複製連結後，仍可抵達 https://lovetypes.tw/start/。
- UTM source / medium / campaign / content 沒有被平台移除或改寫。
- Bio 與置頂留言只導向 15 題測驗，沒有導購、療效或診斷承諾。
- 留下可追溯 proof note，例如平台、設定時間、截圖檔名或手動驗證紀錄。

### Writeback

- 設定完成：`python3 tools/promotion_profile_writeback.py update --platform youtube_shorts --status set --set-date 2026-06-13 --proof-note "manual profile link verified"`
- 公開可點：`python3 tools/promotion_profile_writeback.py update --platform youtube_shorts --status live --set-date 2026-06-13 --proof-note "live profile link verified"`

### After Writeback

- 重新跑 promotion_launch_readiness_gate.py。
- 確認 promotion_launch_readiness_profile_configured 變成 3。
- 只有 promotion_launch_readiness_ready_to_publish=1 時才發布第一批。

## TikTok（`tiktok`）

- current status：`planned`
- configured：0
- profile link：https://lovetypes.tw/start/?utm_source=tiktok&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=tiktok_bio
- link location：Profile website link

### Bio

```text
五種愛之語測驗｜進入心語庭園，找到你的情感守護者。
```

### Pinned / First Comment

```text
完成 15 題測驗，找到你的情感守護者。入口在個人頁連結。
留言 A/B/C，選出最像你的心語。
```

### Evidence Required

- profile link 已實際貼到平台個人頁或說明欄。
- 從平台畫面點擊或複製連結後，仍可抵達 https://lovetypes.tw/start/。
- UTM source / medium / campaign / content 沒有被平台移除或改寫。
- Bio 與置頂留言只導向 15 題測驗，沒有導購、療效或診斷承諾。
- 留下可追溯 proof note，例如平台、設定時間、截圖檔名或手動驗證紀錄。

### Writeback

- 設定完成：`python3 tools/promotion_profile_writeback.py update --platform tiktok --status set --set-date 2026-06-13 --proof-note "manual profile link verified"`
- 公開可點：`python3 tools/promotion_profile_writeback.py update --platform tiktok --status live --set-date 2026-06-13 --proof-note "live profile link verified"`

### After Writeback

- 重新跑 promotion_launch_readiness_gate.py。
- 確認 promotion_launch_readiness_profile_configured 變成 3。
- 只有 promotion_launch_readiness_ready_to_publish=1 時才發布第一批。

## Instagram Reels（`instagram_reels`）

- current status：`planned`
- configured：0
- profile link：https://lovetypes.tw/start/?utm_source=instagram&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=instagram_reels_bio
- link location：Profile link in bio

### Bio

```text
LoveTypes 心語庭園｜15 題找到你的情感守護者。
```

### Pinned / First Comment

```text
完成 15 題測驗，找到你的情感守護者。入口在個人檔案連結。
留言你的 A/B/C，讓守護者把心語接住。
```

### Evidence Required

- profile link 已實際貼到平台個人頁或說明欄。
- 從平台畫面點擊或複製連結後，仍可抵達 https://lovetypes.tw/start/。
- UTM source / medium / campaign / content 沒有被平台移除或改寫。
- Bio 與置頂留言只導向 15 題測驗，沒有導購、療效或診斷承諾。
- 留下可追溯 proof note，例如平台、設定時間、截圖檔名或手動驗證紀錄。

### Writeback

- 設定完成：`python3 tools/promotion_profile_writeback.py update --platform instagram_reels --status set --set-date 2026-06-13 --proof-note "manual profile link verified"`
- 公開可點：`python3 tools/promotion_profile_writeback.py update --platform instagram_reels --status live --set-date 2026-06-13 --proof-note "live profile link verified"`

### After Writeback

- 重新跑 promotion_launch_readiness_gate.py。
- 確認 promotion_launch_readiness_profile_configured 變成 3。
- 只有 promotion_launch_readiness_ready_to_publish=1 時才發布第一批。
