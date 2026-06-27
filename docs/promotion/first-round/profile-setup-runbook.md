# LoveTypes Profile Setup Runbook

- 產生日期：2026-06-28
- platforms：1
- configured：1
- pending：0
- clipboard blocks：1
- current stage：`first_batch_kpi`
- ready_to_publish：0
- issues：0

## Operating Rules

- 目前活動平台的 profile link 都完成 set/live 並通過 gate 後，才發布第一批 Shorts。
- 平台個人頁先只承接 15 題測驗，不直接導購。
- 沒有外部平台截圖、公開點擊或可追溯紀錄時，不回填 set/live。
- 禁用詞：診斷、療效、保證修復、必須購買

## After Every Profile Update

```bash
python3 tools/promotion_daily_ops_refresh.py
python3 tools/promotion_profile_completion_gate.py --check
python3 tools/promotion_master_gate.py --check
```

## YouTube Shorts（`youtube_shorts`）

- current status：`set`
- configured：1
- link location：Channel description / video description
- profile link：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
- platform note：YouTube is the first-round English channel; the channel bio, descriptions, and pinned comments can use the full tracking link.

### Copy Into Profile

Bio:

```text
LoveTypes Heart-Language Garden | Take the 15-question quiz to find your emotional guardian.
```

Pinned / first comment:

```text
Take the 15-question quiz to find your emotional guardian: https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
Comment A/B/C and we will point you to a guardian route.
```

### Verification

- 貼上 profile link 後，從平台畫面點擊或複製連結。
- 確認瀏覽器抵達 https://lovetypes.tw/start/，且沒有 404。
- 確認 UTM 保留 utm_source=youtube、utm_medium=social_profile、utm_campaign=first_round_quiz_completion、utm_content=youtube_shorts_bio。
- 確認 Bio / 置頂留言只有測驗 CTA，沒有 Luna、聯盟書卷、診斷或療效承諾。
- 保存截圖或公開點擊紀錄，proof note 必須含 screenshot / public URL / clicked / verified 等可追溯詞。

### Writeback

設定完成後：

```bash
python3 tools/promotion_profile_writeback.py update --platform youtube_shorts --status set --set-date 2026-06-28 --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"
```

公開可點後：

```bash
python3 tools/promotion_profile_writeback.py update --platform youtube_shorts --status live --set-date 2026-06-28 --proof-note "<REAL_PROFILE_CLICK_NOTE> verified"
```

Structured import template:

```text
LoveTypes profile setup writeback
platform: youtube_shorts
status: set
set_date: 2026-06-28
profile_link: https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
proof_note: <REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified
```

Traceable proof note examples:

- `<REAL_SCREENSHOT_FILENAME> verified`
- `<REAL_PUBLIC_PROFILE_CLICK_URL_OR_TIMESTAMP> verified`
- `<REAL_SCREEN_RECORDING_FILENAME> verified`
