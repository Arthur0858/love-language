# LoveTypes Operator Next Action Closure Quickstart

- 產生日期：2026-06-14
- stage：`profile_setup`
- profile configured：0 / 3
- ready actions：3 / 3
- first batch published：0 / 3
- minimum KPI rows：0 / 3
- proof profile valid：3
- proof post rejected：3
- profile publish ready：0
- publish KPI weekly ready：0
- active blockers：14
- issues：0

## Rules

- The only allowed external actions now are the three profile setup actions.
- Run the check command before any writeback command.
- Do not publish first-batch posts until profile publish handoff is ready.
- Do not write KPI, weekly review, lead route, Luna, affiliate, or offer decisions while empty data mode is active.
- Stop immediately if account identity, permission, URL preservation, or safety copy is uncertain.

## Allowed Actions Now

### Set YouTube Shorts profile link · `youtube_shorts`

- status：`ready_to_configure`
- profile URL：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
- release：platform-profile-tracker.csv row is set/live with profile_link_set_date and traceable proof note.
- stop：A real platform screenshot/click proof must exist before running the write command.

Copy block:

```text
Profile link location: Channel description / video description
Profile link: https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio

Bio:
LoveTypes 心語庭園｜完成 15 題測驗，找到你的情感守護者。

Pinned / first comment:
完成 15 題測驗，找到你的情感守護者：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
留言 A/B/C，我們會用守護者路線回覆你。
```

Proof template:

```text
LoveTypes profile setup writeback
platform: youtube_shorts
status: set
set_date: 2026-06-14
profile_link: https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
proof_note: <REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified
```

- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts.txt`
- write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`

### Set TikTok profile link · `tiktok`

- status：`ready_to_configure`
- profile URL：https://lovetypes.tw/start/?utm_source=tiktok&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=tiktok_bio
- release：platform-profile-tracker.csv row is set/live with profile_link_set_date and traceable proof note.
- stop：A real platform screenshot/click proof must exist before running the write command.

Copy block:

```text
Profile link location: Profile website link
Profile link: https://lovetypes.tw/start/?utm_source=tiktok&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=tiktok_bio

Bio:
五種愛之語測驗｜進入心語庭園，找到你的情感守護者。

Pinned / first comment:
完成 15 題測驗，找到你的情感守護者。入口在個人頁連結。
留言 A/B/C，選出最像你的心語。
```

Proof template:

```text
LoveTypes profile setup writeback
platform: tiktok
status: set
set_date: 2026-06-14
profile_link: https://lovetypes.tw/start/?utm_source=tiktok&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=tiktok_bio
proof_note: <REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified
```

- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-tiktok.txt`
- write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-tiktok.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`

### Set Instagram Reels profile link · `instagram_reels`

- status：`ready_to_configure`
- profile URL：https://lovetypes.tw/start/?utm_source=instagram&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=instagram_reels_bio
- release：platform-profile-tracker.csv row is set/live with profile_link_set_date and traceable proof note.
- stop：A real platform screenshot/click proof must exist before running the write command.

Copy block:

```text
Profile link location: Profile link in bio
Profile link: https://lovetypes.tw/start/?utm_source=instagram&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=instagram_reels_bio

Bio:
LoveTypes 心語庭園｜15 題找到你的情感守護者。

Pinned / first comment:
完成 15 題測驗，找到你的情感守護者。入口在個人檔案連結。
留言你的 A/B/C，讓守護者把心語接住。
```

Proof template:

```text
LoveTypes profile setup writeback
platform: instagram_reels
status: set
set_date: 2026-06-14
profile_link: https://lovetypes.tw/start/?utm_source=instagram&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=instagram_reels_bio
proof_note: <REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified
```

- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-instagram_reels.txt`
- write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-instagram_reels.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`

## After External Proof

- `refresh_after_profile_writeback`：`python3 tools/promotion_daily_ops_refresh.py`；expected：profileConfigured moves toward 3 only after real proof writeback.
- `check_profile_to_publish_gate`：`python3 tools/promotion_profile_completion_gate.py --check && python3 tools/promotion_profile_publish_handoff.py --check`；expected：readyToPublish remains 0 until all three profiles are set/live.
- `keep_publish_locked_until_gate`：`python3 tools/promotion_first_batch_publish_closure_quickstart.py --check`；expected：first-batch publishing remains blocked before profile gate completion.
