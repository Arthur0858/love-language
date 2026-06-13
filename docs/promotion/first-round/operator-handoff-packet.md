# LoveTypes Operator Handoff Packet

- 產生日期：2026-06-14
- profile configured / pending：0 / 3
- ready to publish：0
- first batch published / pending：0 / 3
- weekly review ready：0
- empty data mode：1
- ready steps：3
- blocked steps：4
- issues：0

## Do Not Do

- Do not mark profiles set/live without platform evidence.
- Do not mark posts published without a verified https post URL.
- Do not fill KPI with guesses; use 0 only when the platform/source was checked and truly has 0.
- Do not change offer order, paid CTA, Luna emphasis, affiliate emphasis, or winning guardian in empty-data mode.

## Structured Import Templates

### Profile setup proof import

- check：`python3 tools/promotion_profile_text_import.py check --input /path/to/profile.txt`
- write：`python3 tools/promotion_profile_text_import.py add --input /path/to/profile.txt --proof-note "manual profile link verified"`

```text
LoveTypes profile setup writeback
platform: youtube_shorts
status: set
set_date: 2026-06-14
profile_link: https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
proof_note: manual profile link verified
```

### Published post URL and starter KPI import

- check：`python3 tools/promotion_post_text_import.py check --input /path/to/post.txt`
- write：`python3 tools/promotion_post_text_import.py add --input /path/to/post.txt --proof-note "manual post URL verified"`

```text
LoveTypes platform post writeback
platform: youtube_shorts
task_id: publish-lt-s01-iris-silence
status: published
published_date: 2026-06-14
post_url: https://www.youtube.com/shorts/lovetypes-proof-url-123
views: 0
site_clicks: 0
quiz_starts: 0
quiz_completions: 0
```

### Structured lead request import

- check：`python3 tools/promotion_lead_text_import.py check --input /path/to/request.txt`
- write：`python3 tools/promotion_lead_text_import.py add --input /path/to/request.txt --proof-note "email request verified"`

```text
LoveTypes 結構化需求
來源: 收藏室免費素材需求
我的守護者: 艾莉絲 · 肯定的言詞
需求類型: owned_asset_request
素材偏好: PDF 練習卡
可回覆 email: name@example.com
Campaign content / 推廣內容: iris_silence
使用情境或備註: 睡前整理，想要可列印版本
consent_status: explicit_reply_ok
page: https://lovetypes.tw/keepsakes/
```


## Steps

### 1. Set YouTube Shorts profile link

- phase：`profile_setup`
- status：`ready`
- priority：`high`
- platform：youtube_shorts
- url：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
- writeback：`python3 tools/promotion_profile_writeback.py update --platform youtube_shorts --status set --set-date 2026-06-14 --proof-note "manual profile link verified"`

Evidence:
- profile link 已實際貼到平台個人頁或說明欄。
- 從平台畫面點擊或複製連結後，仍可抵達 https://lovetypes.tw/start/。
- UTM source / medium / campaign / content 沒有被平台移除或改寫。
- Bio 與置頂留言只導向 15 題測驗，沒有導購、療效或診斷承諾。
- 留下可追溯 proof note，例如平台、設定時間、截圖檔名或手動驗證紀錄。

### 2. Set TikTok profile link

- phase：`profile_setup`
- status：`ready`
- priority：`high`
- platform：tiktok
- url：https://lovetypes.tw/start/?utm_source=tiktok&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=tiktok_bio
- writeback：`python3 tools/promotion_profile_writeback.py update --platform tiktok --status set --set-date 2026-06-14 --proof-note "manual profile link verified"`

Evidence:
- profile link 已實際貼到平台個人頁或說明欄。
- 從平台畫面點擊或複製連結後，仍可抵達 https://lovetypes.tw/start/。
- UTM source / medium / campaign / content 沒有被平台移除或改寫。
- Bio 與置頂留言只導向 15 題測驗，沒有導購、療效或診斷承諾。
- 留下可追溯 proof note，例如平台、設定時間、截圖檔名或手動驗證紀錄。

### 3. Set Instagram Reels profile link

- phase：`profile_setup`
- status：`ready`
- priority：`high`
- platform：instagram_reels
- url：https://lovetypes.tw/start/?utm_source=instagram&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=instagram_reels_bio
- writeback：`python3 tools/promotion_profile_writeback.py update --platform instagram_reels --status set --set-date 2026-06-14 --proof-note "manual profile link verified"`

Evidence:
- profile link 已實際貼到平台個人頁或說明欄。
- 從平台畫面點擊或複製連結後，仍可抵達 https://lovetypes.tw/start/。
- UTM source / medium / campaign / content 沒有被平台移除或改寫。
- Bio 與置頂留言只導向 15 題測驗，沒有導購、療效或診斷承諾。
- 留下可追溯 proof note，例如平台、設定時間、截圖檔名或手動驗證紀錄。

### 4. 他沉默時，你最想聽見哪一句話？

- phase：`publish_first_batch`
- status：`blocked_until_profile_links`
- priority：`high`
- platform：youtube_shorts
- taskId：publish-lt-s01-iris-silence
- scriptId：lt-s01-iris-silence
- scheduled：2026-06-15 20:30 Asia/Taipei
- trackedUrl：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence
- blocked by：profile links are not all set/live
- writeback：`python3 tools/promotion_post_writeback.py update --platform youtube_shorts --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-14 --post-url https://www.youtube.com/shorts/replace-with-real-post-url --proof-note "manual post URL verified"`

Caption:

```text
你不是想聽甜言蜜語，你只是想確認自己有沒有被看見。

完成 15 題測驗，找到你的情感守護者：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence

留言 A/B/C，或寫下一句你最想被說出口的話。
#五種愛之語測驗 #情感守護者 #心語庭園 #錯頻修復 #LoveTypes
```

### 5. 他沉默時，你最想聽見哪一句話？

- phase：`publish_first_batch`
- status：`blocked_until_profile_links`
- priority：`high`
- platform：tiktok
- taskId：publish-lt-s01-iris-silence
- scriptId：lt-s01-iris-silence
- scheduled：2026-06-15 21:00 Asia/Taipei
- trackedUrl：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence
- blocked by：profile links are not all set/live
- writeback：`python3 tools/promotion_post_writeback.py update --platform tiktok --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-14 --post-url https://www.youtube.com/shorts/replace-with-real-post-url --proof-note "manual post URL verified"`

Caption:

```text
你不是想聽甜言蜜語，你只是想確認自己有沒有被看見。

首頁連結完成 15 題測驗：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence

留言 A/B/C，或寫下一句你最想被說出口的話。
#五種愛之語測驗 #情感守護者 #心語庭園 #錯頻修復 #LoveTypes
```

### 6. 他沉默時，你最想聽見哪一句話？

- phase：`publish_first_batch`
- status：`blocked_until_profile_links`
- priority：`high`
- platform：instagram_reels
- taskId：publish-lt-s01-iris-silence
- scriptId：lt-s01-iris-silence
- scheduled：2026-06-15 21:30 Asia/Taipei
- trackedUrl：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence
- blocked by：profile links are not all set/live
- writeback：`python3 tools/promotion_post_writeback.py update --platform instagram_reels --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-14 --post-url https://www.youtube.com/shorts/replace-with-real-post-url --proof-note "manual post URL verified"`

Caption:

```text
你不是想聽甜言蜜語，你只是想確認自己有沒有被看見。

個人檔案連結完成 15 題測驗：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence

留言 A/B/C，或寫下一句你最想被說出口的話。
#五種愛之語測驗 #情感守護者 #心語庭園 #錯頻修復 #LoveTypes
```

### 7. Run weekly review and decision gates

- phase：`weekly_review`
- status：`blocked_until_kpi_backfill`
- priority：`medium`
- blocked by：首批三平台尚無公開 post URL。; 首批尚無 site_clicks / quiz_starts / quiz_completions 回填列。; publishing-status 尚未達週決策條件。; 目前仍是空資料模式，不能調整商品、付費 CTA、Luna 或聯盟優先序。

## Completion Criteria

- profileConfigured reaches 3
- readyToPublish becomes true
- firstBatchPublished reaches 3
- minimum KPI rows are backfilled or explicitly verified as 0
- weeklyReviewReady becomes true before any revenue decision
