# LoveTypes Launch Clipboard

- 產生日期：2026-06-14
- blocks：6
- profile blocks：3
- post blocks：3
- ready / blocked blocks：3 / 3
- dashboard blocked areas：8
- handoff blocked steps：4
- issues：0

## Rules

- Copy profile blocks first; publish blocks remain blocked until profile gate opens.
- Run check commands before write commands.
- Write commands require real external proof; placeholders must be replaced before use.
- Do not change the quiz CTA, add paid claims, or use guessed KPI values.

## profile · YouTube Shorts · `youtube_shorts`

- status：`ready_to_configure`

### Copy

```text
Profile link location: Channel description / video description
Profile link: https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio

Bio:
LoveTypes 心語庭園｜完成 15 題測驗，找到你的情感守護者。

Pinned / first comment:
完成 15 題測驗，找到你的情感守護者：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
留言 A/B/C，我們會用守護者路線回覆你。
```

### Proof Template

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
- stop：Stop if account/profile is not visibly LoveTypes, edit permission is missing, /start/ UTM is changed, or Bio copy adds paid/diagnosis claims.

## profile · TikTok · `tiktok`

- status：`ready_to_configure`

### Copy

```text
Profile link location: Profile website link
Profile link: https://lovetypes.tw/start/?utm_source=tiktok&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=tiktok_bio

Bio:
五種愛之語測驗｜進入心語庭園，找到你的情感守護者。

Pinned / first comment:
完成 15 題測驗，找到你的情感守護者。入口在個人頁連結。
留言 A/B/C，選出最像你的心語。
```

### Proof Template

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
- stop：Stop if account/profile is not visibly LoveTypes, edit permission is missing, /start/ UTM is changed, or Bio copy adds paid/diagnosis claims.

## profile · Instagram Reels · `instagram_reels`

- status：`ready_to_configure`

### Copy

```text
Profile link location: Profile link in bio
Profile link: https://lovetypes.tw/start/?utm_source=instagram&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=instagram_reels_bio

Bio:
LoveTypes 心語庭園｜15 題找到你的情感守護者。

Pinned / first comment:
完成 15 題測驗，找到你的情感守護者。入口在個人檔案連結。
留言你的 A/B/C，讓守護者把心語接住。
```

### Proof Template

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
- stop：Stop if account/profile is not visibly LoveTypes, edit permission is missing, /start/ UTM is changed, or Bio copy adds paid/diagnosis claims.

## post · youtube_shorts · `youtube_shorts`

- status：`blocked_until_profile_links`

### Copy

```text
你不是想聽甜言蜜語，你只是想確認自己有沒有被看見。

完成 15 題測驗，找到你的情感守護者：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence

留言 A/B/C，或寫下一句你最想被說出口的話。
#五種愛之語測驗 #情感守護者 #心語庭園 #錯頻修復 #LoveTypes
```

### Proof Template

```text
LoveTypes platform post writeback
platform: youtube_shorts
task_id: publish-lt-s01-iris-silence
status: published
published_date: 2026-06-14
post_url: <REAL_YOUTUBE_SHORTS_URL>
views: 0
site_clicks: 0
quiz_starts: 0
quiz_completions: 0
proof_note: <REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified
```

- check：`python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt`
- write：`python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt --proof-note "<REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified"`
- stop：Stop while profile links are not all set/live; replace placeholder URL with real public post URL before writeback.

## post · tiktok · `tiktok`

- status：`blocked_until_profile_links`

### Copy

```text
你不是想聽甜言蜜語，你只是想確認自己有沒有被看見。

首頁連結完成 15 題測驗：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence

留言 A/B/C，或寫下一句你最想被說出口的話。
#五種愛之語測驗 #情感守護者 #心語庭園 #錯頻修復 #LoveTypes
```

### Proof Template

```text
LoveTypes platform post writeback
platform: tiktok
task_id: publish-lt-s01-iris-silence
status: published
published_date: 2026-06-14
post_url: <REAL_TIKTOK_VIDEO_URL>
views: 0
site_clicks: 0
quiz_starts: 0
quiz_completions: 0
proof_note: <REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified
```

- check：`python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-tiktok-publish-lt-s01-iris-silence.txt`
- write：`python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-tiktok-publish-lt-s01-iris-silence.txt --proof-note "<REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified"`
- stop：Stop while profile links are not all set/live; replace placeholder URL with real public post URL before writeback.

## post · instagram_reels · `instagram_reels`

- status：`blocked_until_profile_links`

### Copy

```text
你不是想聽甜言蜜語，你只是想確認自己有沒有被看見。

個人檔案連結完成 15 題測驗：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence

留言 A/B/C，或寫下一句你最想被說出口的話。
#五種愛之語測驗 #情感守護者 #心語庭園 #錯頻修復 #LoveTypes
```

### Proof Template

```text
LoveTypes platform post writeback
platform: instagram_reels
task_id: publish-lt-s01-iris-silence
status: published
published_date: 2026-06-14
post_url: <REAL_INSTAGRAM_REEL_URL>
views: 0
site_clicks: 0
quiz_starts: 0
quiz_completions: 0
proof_note: <REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified
```

- check：`python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-instagram_reels-publish-lt-s01-iris-silence.txt`
- write：`python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-instagram_reels-publish-lt-s01-iris-silence.txt --proof-note "<REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified"`
- stop：Stop while profile links are not all set/live; replace placeholder URL with real public post URL before writeback.
