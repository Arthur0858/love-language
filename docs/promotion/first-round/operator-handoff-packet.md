# LoveTypes Operator Handoff Packet

- 產生日期：2026-06-21
- profile configured / pending：1 / 0
- ready to publish：1
- first batch published / pending：0 / 1
- weekly review ready：0
- empty data mode：0
- ready steps：1
- blocked steps：1
- issues：0

## Do Not Do

- Do not mark profiles set/live without platform evidence.
- Do not mark posts published without a verified https post URL.
- Do not fill KPI with guesses; use 0 only when the platform/source was checked and truly has 0.
- Do not change offer order, paid CTA, Luna emphasis, affiliate emphasis, or winning guardian in empty-data mode.

## Structured Import Templates

### Profile setup proof import

- check：`python3 tools/promotion_profile_text_import.py check --input /path/to/profile.txt`
- write：`python3 tools/promotion_profile_text_import.py add --input /path/to/profile.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`

```text
LoveTypes profile setup writeback
platform: youtube_shorts
status: set
set_date: 2026-06-21
profile_link: https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
proof_note: <REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified
```

### Published post URL and starter KPI import

- check：`python3 tools/promotion_post_text_import.py check --input /path/to/post.txt`
- write：`python3 tools/promotion_post_text_import.py add --input /path/to/post.txt --proof-note "<REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified"`

```text
LoveTypes platform post writeback
platform: youtube_shorts
task_id: publish-lt-s01-iris-silence
status: published
published_date: 2026-06-21
post_url: <REAL_YOUTUBE_SHORTS_URL>
views: 0
site_clicks: 0
quiz_starts: 0
quiz_completions: 0
proof_note: <REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified
```

### Structured lead request import

- check：`python3 tools/promotion_lead_text_import.py check --input /path/to/request.txt`
- write：`python3 tools/promotion_lead_text_import.py add --input /path/to/request.txt --proof-note "<REAL_EMAIL_THREAD_OR_MESSAGE_ID> checked YYYY-MM-DD"`

```text
LoveTypes 結構化需求
來源: 收藏室免費素材需求
我的守護者: 艾莉絲 · 肯定的言詞
需求類型: owned_asset_request
素材偏好: PDF 練習卡
可回覆 email: <REAL_REPLY_EMAIL>
Campaign content / 推廣內容: iris_silence
使用情境或備註: 睡前整理，想要可列印版本
consent_status: explicit_reply_ok
page: https://lovetypes.tw/keepsakes/
```


## Steps

### 1. 他沉默時，你最想聽見哪一句話？

- phase：`publish_first_batch`
- status：`ready`
- priority：`high`
- platform：youtube_shorts
- taskId：publish-lt-s01-iris-silence
- scriptId：lt-s01-iris-silence
- scheduled：2026-06-15 20:30 Asia/Taipei
- trackedUrl：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence
- writeback：`python3 tools/promotion_post_writeback.py update --platform youtube_shorts --task-id publish-lt-s01-iris-silence --status published --published-date 2026-06-21 --post-url <REAL_YOUTUBE_SHORTS_URL> --proof-note "<REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified"`

Caption:

```text
你不是想聽甜言蜜語，你只是想確認自己有沒有被看見。

Take the 15-question quiz to find your emotional guardian: https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence

留言 A/B/C，或寫下一句你最想被說出口的話。
#LoveLanguages #RelationshipQuiz #EmotionalGuardian #HeartLanguage #LoveTypes
```

### 2. Run weekly review and decision gates

- phase：`weekly_review`
- status：`blocked_until_kpi_backfill`
- priority：`medium`
- blocked by：首批 YouTube Shorts 尚無公開 post URL。; 首批尚無 site_clicks / quiz_starts / quiz_completions 回填列。; publishing-status 尚未達週決策條件。

## Completion Criteria

- profileConfigured reaches 3
- readyToPublish becomes true
- firstBatchPublished reaches 3
- minimum KPI rows are backfilled or explicitly verified as 0
- weeklyReviewReady becomes true before any revenue decision
