# LoveTypes Profile Verification Packet

- 產生日期：2026-07-06
- platforms：1
- configured：1
- pending：0
- ready_to_publish：1
- issues：0

## Gate

- Do not publish first batch until all active profile links are set/live and readiness ready_to_publish is true.
- Profile copy keeps the CTA on the 15-question guardian quiz and does not promote Luna, books, or paid products first.
- 不用本文件偽造 profile 設定、post URL 或 KPI；只在外部平台完成後回填。

## YouTube Shorts（`youtube_shorts`）

- current status：`set`
- configured：1
- profile link：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
- link location：Channel description / video description

### Bio

```text
LoveTypes Heart-Language Garden | Take the 15-question quiz to find your emotional guardian.
```

### Pinned / First Comment

```text
Take the 15-question quiz to find your emotional guardian: https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
Comment A/B/C and we will point you to a guardian route.
```

### Evidence Required

- profile link 已實際貼到平台個人頁或說明欄。
- 從平台畫面點擊或複製連結後，仍可抵達 https://lovetypes.tw/start/。
- UTM source / medium / campaign / content 沒有被平台移除或改寫。
- Bio 與置頂留言只導向 15 題測驗，沒有導購、療效或診斷承諾。
- 留下可追溯 proof note，例如平台、設定時間、截圖檔名或手動驗證紀錄。

### Writeback

- 設定完成：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`
- 公開可點：`python3 tools/promotion_profile_writeback.py update --platform youtube_shorts --status live --set-date 2026-07-06 --proof-note "<REAL_PROFILE_CLICK_NOTE> verified"`

### After Writeback

- 重新跑 promotion_launch_readiness_gate.py。
- 確認 promotion_launch_readiness_profile_configured 變成 1。
- 只有 promotion_launch_readiness_ready_to_publish=1 時才發布第一批。
