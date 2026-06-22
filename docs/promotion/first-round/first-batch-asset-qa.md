# LoveTypes First Batch Asset QA

- 產生日期：2026-06-22
- QA rows：1
- required QA items：8
- issues：0

## Rule

- 這份文件只做發布前 QA；`prepared` 代表素材可預檢，不代表 profile、post URL 或 KPI 已完成。
- 發布前逐項留下 proof note；發布後再用 post text import 回填 URL 與初始 KPI。

## youtube_shorts · `publish-lt-s01-iris-silence`

- script：`lt-s01-iris-silence`
- guardian：艾莉絲（`iris`）
- title：他沉默時，你最想聽見哪一句話？
- asset ready status：`published`
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence

### QA Checklist

- `vertical_video` 直式影片檔：確認 9:16 直式影片可播放，長度符合 YouTube Shorts 節奏。
  - evidence：實際影片檔路徑、平台預覽截圖或剪輯輸出紀錄。
- `subtitle_readability` 字幕可讀性：字幕短句、無錯字、手機尺寸不遮擋主體，保留 A/B/C 互動。
  - evidence：手機預覽截圖或字幕 QA 記錄。
- `cover_or_first_frame` 封面或首幀：首幀能在 1 秒內看懂情緒鉤子與守護者氛圍。
  - evidence：封面圖、首幀截圖或平台草稿預覽。
- `guardian_universe_match` 守護者宇宙一致：使用 艾莉絲 / iris 的色彩、象徵物與情緒設定，不混用其他守護者。
  - evidence：畫面截圖或素材清單。
- `caption_quiz_cta` Caption 單一 CTA：Caption 主 CTA 維持 15-question quiz，不加入商品、Luna 或聯盟導購作為第一動作。
  - evidence：平台 caption 草稿。
- `tracked_url_utm` 追蹤連結：連結保留 utm_content=iris_silence，且指向 /start/。
  - evidence：平台草稿中的連結或點擊後網址。
- `safety_boundary` 安全邊界：無診斷、療效、保證修復、必須購買或危機支援承諾。
  - evidence：最終字幕與 caption 檢查紀錄。
- `writeback_ready` 回填準備：發布後可取得 https post URL、發布日期、proof note，並使用 post text import 回填。
  - evidence：post text import 模板已準備。

### Post Import Template

```text
LoveTypes platform post writeback
platform: youtube_shorts
task_id: publish-lt-s01-iris-silence
status: published
published_date: 2026-06-22
post_url: <REAL_YOUTUBE_SHORTS_URL>
views: 0
site_clicks: 0
quiz_starts: 0
quiz_completions: 0
```
