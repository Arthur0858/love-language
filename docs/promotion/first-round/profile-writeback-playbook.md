# LoveTypes Profile Writeback Playbook

- 產生日期：2026-06-14
- configured：0 / 3
- issues：0
- 原則：只有實際設定並確認平台 profile link 後，才能用 `set` 或 `live`。

## 回填命令

### YouTube Shorts（`youtube_shorts`）

- 目前狀態：`planned`
- Profile link：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
- 設定完成後：
  - `python3 tools/promotion_profile_writeback.py update --platform youtube_shorts --status set --set-date 2026-06-14 --proof-note "screenshot profile-youtube_shorts-2026-06-14.png verified"`
- 已確認公開可點後：
  - `python3 tools/promotion_profile_writeback.py update --platform youtube_shorts --status live --set-date 2026-06-14 --proof-note "public URL profile link clicked 2026-06-14"`

### TikTok（`tiktok`）

- 目前狀態：`planned`
- Profile link：https://lovetypes.tw/start/?utm_source=tiktok&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=tiktok_bio
- 設定完成後：
  - `python3 tools/promotion_profile_writeback.py update --platform tiktok --status set --set-date 2026-06-14 --proof-note "screenshot profile-tiktok-2026-06-14.png verified"`
- 已確認公開可點後：
  - `python3 tools/promotion_profile_writeback.py update --platform tiktok --status live --set-date 2026-06-14 --proof-note "public URL profile link clicked 2026-06-14"`

### Instagram Reels（`instagram_reels`）

- 目前狀態：`planned`
- Profile link：https://lovetypes.tw/start/?utm_source=instagram&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=instagram_reels_bio
- 設定完成後：
  - `python3 tools/promotion_profile_writeback.py update --platform instagram_reels --status set --set-date 2026-06-14 --proof-note "screenshot profile-instagram_reels-2026-06-14.png verified"`
- 已確認公開可點後：
  - `python3 tools/promotion_profile_writeback.py update --platform instagram_reels --status live --set-date 2026-06-14 --proof-note "public URL profile link clicked 2026-06-14"`

## Profile 設定文字匯入

- 設定平台 profile link 後，可把平台、狀態、日期、profile link 與 proof note 貼成一段文字，再用匯入工具檢查。
- 檢查：`python3 tools/promotion_profile_text_import.py check --input /path/to/profile.txt`
- 寫入：`python3 tools/promotion_profile_text_import.py add --input /path/to/profile.txt --proof-note "screenshot profile-youtube_shorts-YYYY-MM-DD.png verified"`
- 寫入時仍會驗證平台專屬 `/start/` UTM、同步 readiness 與 next actions。

## 安全規則

- 不用本工具偽造 profile link 設定、post URL 或 KPI。
- `set/live` 必須有 `--set-date` 與 `--proof-note`。
- 更新後要重新跑 launch readiness；只有 `ready_to_publish=1` 才發布首批。
