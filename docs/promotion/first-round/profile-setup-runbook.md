# LoveTypes Profile Setup Runbook

- 產生日期：2026-06-14
- platforms：3
- configured：0
- pending：3
- clipboard blocks：3
- current stage：`profile_setup`
- ready_to_publish：0
- issues：0

## Operating Rules

- 三個 profile link 都完成 set/live 並通過 gate 後，才發布第一批 Shorts/Reels。
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

- current status：`planned`
- configured：0
- link location：Channel description / video description
- profile link：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
- platform note：YouTube 說明欄可放完整追蹤連結；置頂留言也放同一條。

### Copy Into Profile

Bio:

```text
LoveTypes 心語庭園｜完成 15 題測驗，找到你的情感守護者。
```

Pinned / first comment:

```text
完成 15 題測驗，找到你的情感守護者：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
留言 A/B/C，我們會用守護者路線回覆你。
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
python3 tools/promotion_profile_writeback.py update --platform youtube_shorts --status set --set-date 2026-06-14 --proof-note "screenshot profile-youtube_shorts-2026-06-14.png verified"
```

公開可點後：

```bash
python3 tools/promotion_profile_writeback.py update --platform youtube_shorts --status live --set-date 2026-06-14 --proof-note "public URL profile link clicked 2026-06-14"
```

Structured import template:

```text
LoveTypes profile setup writeback
platform: youtube_shorts
status: set
set_date: 2026-06-14
profile_link: https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
proof_note: screenshot profile-youtube_shorts-2026-06-14.png verified
```

Traceable proof note examples:

- `screenshot profile-youtube_shorts-2026-06-14.png verified`
- `public URL profile link clicked 2026-06-14`
- `screen recording profile-youtube_shorts-2026-06-14.mov verified`

## TikTok（`tiktok`）

- current status：`planned`
- configured：0
- link location：Profile website link
- profile link：https://lovetypes.tw/start/?utm_source=tiktok&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=tiktok_bio
- platform note：若 caption 不能放可點連結，Bio/個人頁連結必須使用平台專屬追蹤連結。

### Copy Into Profile

Bio:

```text
五種愛之語測驗｜進入心語庭園，找到你的情感守護者。
```

Pinned / first comment:

```text
完成 15 題測驗，找到你的情感守護者。入口在個人頁連結。
留言 A/B/C，選出最像你的心語。
```

### Verification

- 貼上 profile link 後，從平台畫面點擊或複製連結。
- 確認瀏覽器抵達 https://lovetypes.tw/start/，且沒有 404。
- 確認 UTM 保留 utm_source=tiktok、utm_medium=social_profile、utm_campaign=first_round_quiz_completion、utm_content=tiktok_bio。
- 確認 Bio / 置頂留言只有測驗 CTA，沒有 Luna、聯盟書卷、診斷或療效承諾。
- 保存截圖或公開點擊紀錄，proof note 必須含 screenshot / public URL / clicked / verified 等可追溯詞。

### Writeback

設定完成後：

```bash
python3 tools/promotion_profile_writeback.py update --platform tiktok --status set --set-date 2026-06-14 --proof-note "screenshot profile-tiktok-2026-06-14.png verified"
```

公開可點後：

```bash
python3 tools/promotion_profile_writeback.py update --platform tiktok --status live --set-date 2026-06-14 --proof-note "public URL profile link clicked 2026-06-14"
```

Structured import template:

```text
LoveTypes profile setup writeback
platform: tiktok
status: set
set_date: 2026-06-14
profile_link: https://lovetypes.tw/start/?utm_source=tiktok&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=tiktok_bio
proof_note: screenshot profile-tiktok-2026-06-14.png verified
```

Traceable proof note examples:

- `screenshot profile-tiktok-2026-06-14.png verified`
- `public URL profile link clicked 2026-06-14`
- `screen recording profile-tiktok-2026-06-14.mov verified`

## Instagram Reels（`instagram_reels`）

- current status：`planned`
- configured：0
- link location：Profile link in bio
- profile link：https://lovetypes.tw/start/?utm_source=instagram&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=instagram_reels_bio
- platform note：IG Reels caption 以個人檔案連結承接；Bio 連結需先於發布前更新。

### Copy Into Profile

Bio:

```text
LoveTypes 心語庭園｜15 題找到你的情感守護者。
```

Pinned / first comment:

```text
完成 15 題測驗，找到你的情感守護者。入口在個人檔案連結。
留言你的 A/B/C，讓守護者把心語接住。
```

### Verification

- 貼上 profile link 後，從平台畫面點擊或複製連結。
- 確認瀏覽器抵達 https://lovetypes.tw/start/，且沒有 404。
- 確認 UTM 保留 utm_source=instagram、utm_medium=social_profile、utm_campaign=first_round_quiz_completion、utm_content=instagram_reels_bio。
- 確認 Bio / 置頂留言只有測驗 CTA，沒有 Luna、聯盟書卷、診斷或療效承諾。
- 保存截圖或公開點擊紀錄，proof note 必須含 screenshot / public URL / clicked / verified 等可追溯詞。

### Writeback

設定完成後：

```bash
python3 tools/promotion_profile_writeback.py update --platform instagram_reels --status set --set-date 2026-06-14 --proof-note "screenshot profile-instagram_reels-2026-06-14.png verified"
```

公開可點後：

```bash
python3 tools/promotion_profile_writeback.py update --platform instagram_reels --status live --set-date 2026-06-14 --proof-note "public URL profile link clicked 2026-06-14"
```

Structured import template:

```text
LoveTypes profile setup writeback
platform: instagram_reels
status: set
set_date: 2026-06-14
profile_link: https://lovetypes.tw/start/?utm_source=instagram&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=instagram_reels_bio
proof_note: screenshot profile-instagram_reels-2026-06-14.png verified
```

Traceable proof note examples:

- `screenshot profile-instagram_reels-2026-06-14.png verified`
- `public URL profile link clicked 2026-06-14`
- `screen recording profile-instagram_reels-2026-06-14.mov verified`
