# LoveTypes Launch Readiness Gate

- 產生日期：2026-07-07
- 結構就緒：`1`
- 可開始設定平台入口：`1`
- 可發布首批貼文：`1`
- 可做 KPI/商品判斷：`0`
- 空資料模式：`1`
- 規則：YouTube profile link 設定完成後才發布首批；首批發布與 KPI 回填前維持空資料安全模式。
- blocker 順序：`set_platform_profile_links`, `publish_first_batch`, `backfill_first_batch_kpis`

## 目前數字

- 平台個人頁：1 / 1 已標記 set/live
- 平台追蹤連結：1 / 1 有效
- 首批排程：1 / 1 有效
- 首週排程：3 / 3 有效
- 素材預備檢查：2
- 已發布平台列：1
- 已回填 KPI 列：0
- 必填 KPI 欄位：`site_clicks`, `quiz_starts`, `quiz_completions`

## 平台入口清單

### YouTube Shorts

- 狀態：`set` (完成)
- Profile link：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
- 連結檢查：有效
- 回填：platform-profile-tracker.csv: status=set/live, profile_link_set_date, profile_clicks, site_clicks, quiz_starts, quiz_completions

## 首批發文清單

### YouTube Shorts · 艾莉絲 · 他沉默時，你最想聽見哪一句話？

- 排程：2026-06-15 20:30 Asia/Taipei
- task：`publish-lt-s01-iris-silence`
- script：`lt-s01-iris-silence`
- CTA：完成 15 題測驗，找到你的情感守護者
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence
- 連結檢查：有效
- 回填：posting-queue.csv: status=published, published_date, post_url; platform-kpi-tracker.csv: same platform row post_url, site_clicks, quiz_starts, quiz_completions; kpi-tracker.csv: script-level weekly rollup

## 下一個決策

- 可發布首批 YouTube Shorts；發布後立即回填 post_url 與最小 KPI。

## 阻擋項

- `backfill_first_batch_kpis` (decision_blocker)：KPI 尚未回填到前 1 筆；保持測驗 CTA，不調整商品、Luna 或聯盟權重。 解除條件：At least the first-batch KPI rows have source-checked values for site_clicks, quiz_starts, and quiz_completions.

## 安全界線

- 空資料模式下不改商品排序、不加重 Luna 或聯盟 CTA。
- Shorts 與個人頁入口維持單一 CTA：完成 15 題測驗，找到你的情感守護者。
- KPI 未回填前，不判定優勝守護者，不承諾療效，不寫診斷式文案。
