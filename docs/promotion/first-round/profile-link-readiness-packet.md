# LoveTypes Profile Link Readiness Packet

- 產生日期：2026-06-14
- profile links：3
- public checked：3
- public ready：3
- ready to configure：3
- configured：0
- profile gate ready：0
- issues：0

## Rule

- `public ready` 只代表 LoveTypes `/start/` 追蹤連結可用，不代表平台 profile 已設定。
- 只有完成外部平台設定、保存 proof note，並回填 profile tracker 後，才能解除 `profile_setup` gate。
- 三個平台 profile 都 set/live 前，不發布第一批 Shorts/Reels。

## Rows

### youtube_shorts

- status：`planned`
- action：`ready_to_configure`
- public ready：`1`
- configured：`0`
- profile link：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
- write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`

### tiktok

- status：`planned`
- action：`ready_to_configure`
- public ready：`1`
- configured：`0`
- profile link：https://lovetypes.tw/start/?utm_source=tiktok&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=tiktok_bio
- write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-tiktok.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`

### instagram_reels

- status：`planned`
- action：`ready_to_configure`
- public ready：`1`
- configured：`0`
- profile link：https://lovetypes.tw/start/?utm_source=instagram&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=instagram_reels_bio
- write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-instagram_reels.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`
