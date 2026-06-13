# LoveTypes Launch Command Center

- 產生日期：2026-06-13
- 週次：Week 1
- 指揮列數：24
- 可立即執行：6
- 等待前置條件：18
- 週決策：尚不可
- 指揮板規則：Run profile_setup and asset_ready_check first; keep publish_post blocked until both are done; keep kpi_backfill blocked until post_url exists.
- 空資料安全：Before KPI backfill, do not change offers, paid CTA, product order, Luna emphasis, affiliate emphasis, or winning guardian.

## 今日決策

- 先完成 profile_setup 與 asset_ready_check，再發布 Week 1 三支 Shorts；未回填 KPI 前不調整商品或付費 CTA。

## 執行順序

### 1. 設定 YouTube Shorts 個人頁入口

- phase：`profile_setup`
- status：`ready`
- priority：`high`
- platform：`youtube_shorts`
- task：`profile-youtube_shorts`
- tracked URL：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
- action：把 Bio/Profile link 設為 Channel description / video description，並放上置頂留言。
- writeback：status=set/live, profile_link_set_date, profile_clicks, site_clicks, quiz_starts, quiz_completions
- safety：入口只導向 15 題測驗，不導購、不承諾療效。

### 2. 設定 TikTok 個人頁入口

- phase：`profile_setup`
- status：`ready`
- priority：`high`
- platform：`tiktok`
- task：`profile-tiktok`
- tracked URL：https://lovetypes.tw/start/?utm_source=tiktok&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=tiktok_bio
- action：把 Bio/Profile link 設為 Profile website link，並放上置頂留言。
- writeback：status=set/live, profile_link_set_date, profile_clicks, site_clicks, quiz_starts, quiz_completions
- safety：入口只導向 15 題測驗，不導購、不承諾療效。

### 3. 設定 Instagram Reels 個人頁入口

- phase：`profile_setup`
- status：`ready`
- priority：`high`
- platform：`instagram_reels`
- task：`profile-instagram_reels`
- tracked URL：https://lovetypes.tw/start/?utm_source=instagram&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=instagram_reels_bio
- action：把 Bio/Profile link 設為 Profile link in bio，並放上置頂留言。
- writeback：status=set/live, profile_link_set_date, profile_clicks, site_clicks, quiz_starts, quiz_completions
- safety：入口只導向 15 題測驗，不導購、不承諾療效。

### 4. 他沉默時，你最想聽見哪一句話？

- phase：`asset_ready_check`
- status：`ready`
- priority：`high`
- platform：`all`
- task：`publish-lt-s01-iris-silence`
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence
- action：確認直式影片、字幕、封面或首幀、caption、留言 CTA 與安全邊界都可發布。
- writeback：mark asset ready before platform posting
- safety：短片 CTA 維持測驗入口，不把素材改成直接購買。

### 5. 哪一句肯定，會讓你瞬間安心？

- phase：`asset_ready_check`
- status：`ready`
- priority：`high`
- platform：`all`
- task：`publish-lt-s02-iris-affirmation`
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_affirmation
- action：確認直式影片、字幕、封面或首幀、caption、留言 CTA 與安全邊界都可發布。
- writeback：mark asset ready before platform posting
- safety：短片 CTA 維持測驗入口，不把素材改成直接購買。

### 6. 你真的太敏感嗎？還是你只是等一句清楚的話？

- phase：`asset_ready_check`
- status：`ready`
- priority：`high`
- platform：`all`
- task：`publish-lt-s03-iris-too-sensitive`
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_too_sensitive
- action：確認直式影片、字幕、封面或首幀、caption、留言 CTA 與安全邊界都可發布。
- writeback：mark asset ready before platform posting
- safety：短片 CTA 維持測驗入口，不把素材改成直接購買。

### 7. 他沉默時，你最想聽見哪一句話？

- phase：`publish_post`
- status：`blocked_until_ready`
- priority：`high`
- platform：`youtube_shorts`
- task：`publish-lt-s01-iris-silence`
- schedule：2026-06-15 20:30 Asia/Taipei
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence
- action：依 YouTube Shorts caption 發布，確認連結與 UTM 未被改寫。
- writeback：posting-queue.csv: status=published, published_date, post_url
- blocked by：profile_setup, asset_ready_check
- safety：只使用單一 CTA：完成 15 題測驗，找到你的情感守護者。

### 8. 他沉默時，你最想聽見哪一句話？

- phase：`publish_post`
- status：`blocked_until_ready`
- priority：`high`
- platform：`tiktok`
- task：`publish-lt-s01-iris-silence`
- schedule：2026-06-15 21:00 Asia/Taipei
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence
- action：依 TikTok caption 發布，確認連結與 UTM 未被改寫。
- writeback：posting-queue.csv: status=published, published_date, post_url
- blocked by：profile_setup, asset_ready_check
- safety：只使用單一 CTA：完成 15 題測驗，找到你的情感守護者。

### 9. 他沉默時，你最想聽見哪一句話？

- phase：`publish_post`
- status：`blocked_until_ready`
- priority：`high`
- platform：`instagram_reels`
- task：`publish-lt-s01-iris-silence`
- schedule：2026-06-15 21:30 Asia/Taipei
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence
- action：依 Instagram Reels caption 發布，確認連結與 UTM 未被改寫。
- writeback：posting-queue.csv: status=published, published_date, post_url
- blocked by：profile_setup, asset_ready_check
- safety：只使用單一 CTA：完成 15 題測驗，找到你的情感守護者。

### 10. 哪一句肯定，會讓你瞬間安心？

- phase：`publish_post`
- status：`blocked_until_ready`
- priority：`high`
- platform：`youtube_shorts`
- task：`publish-lt-s02-iris-affirmation`
- schedule：2026-06-17 20:30 Asia/Taipei
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_affirmation
- action：依 YouTube Shorts caption 發布，確認連結與 UTM 未被改寫。
- writeback：posting-queue.csv: status=published, published_date, post_url
- blocked by：profile_setup, asset_ready_check
- safety：只使用單一 CTA：完成 15 題測驗，找到你的情感守護者。

### 11. 哪一句肯定，會讓你瞬間安心？

- phase：`publish_post`
- status：`blocked_until_ready`
- priority：`high`
- platform：`tiktok`
- task：`publish-lt-s02-iris-affirmation`
- schedule：2026-06-17 21:00 Asia/Taipei
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_affirmation
- action：依 TikTok caption 發布，確認連結與 UTM 未被改寫。
- writeback：posting-queue.csv: status=published, published_date, post_url
- blocked by：profile_setup, asset_ready_check
- safety：只使用單一 CTA：完成 15 題測驗，找到你的情感守護者。

### 12. 哪一句肯定，會讓你瞬間安心？

- phase：`publish_post`
- status：`blocked_until_ready`
- priority：`high`
- platform：`instagram_reels`
- task：`publish-lt-s02-iris-affirmation`
- schedule：2026-06-17 21:30 Asia/Taipei
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_affirmation
- action：依 Instagram Reels caption 發布，確認連結與 UTM 未被改寫。
- writeback：posting-queue.csv: status=published, published_date, post_url
- blocked by：profile_setup, asset_ready_check
- safety：只使用單一 CTA：完成 15 題測驗，找到你的情感守護者。

### 13. 你真的太敏感嗎？還是你只是等一句清楚的話？

- phase：`publish_post`
- status：`blocked_until_ready`
- priority：`high`
- platform：`youtube_shorts`
- task：`publish-lt-s03-iris-too-sensitive`
- schedule：2026-06-19 20:30 Asia/Taipei
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_too_sensitive
- action：依 YouTube Shorts caption 發布，確認連結與 UTM 未被改寫。
- writeback：posting-queue.csv: status=published, published_date, post_url
- blocked by：profile_setup, asset_ready_check
- safety：只使用單一 CTA：完成 15 題測驗，找到你的情感守護者。

### 14. 你真的太敏感嗎？還是你只是等一句清楚的話？

- phase：`publish_post`
- status：`blocked_until_ready`
- priority：`high`
- platform：`tiktok`
- task：`publish-lt-s03-iris-too-sensitive`
- schedule：2026-06-19 21:00 Asia/Taipei
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_too_sensitive
- action：依 TikTok caption 發布，確認連結與 UTM 未被改寫。
- writeback：posting-queue.csv: status=published, published_date, post_url
- blocked by：profile_setup, asset_ready_check
- safety：只使用單一 CTA：完成 15 題測驗，找到你的情感守護者。

### 15. 你真的太敏感嗎？還是你只是等一句清楚的話？

- phase：`publish_post`
- status：`blocked_until_ready`
- priority：`high`
- platform：`instagram_reels`
- task：`publish-lt-s03-iris-too-sensitive`
- schedule：2026-06-19 21:30 Asia/Taipei
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_too_sensitive
- action：依 Instagram Reels caption 發布，確認連結與 UTM 未被改寫。
- writeback：posting-queue.csv: status=published, published_date, post_url
- blocked by：profile_setup, asset_ready_check
- safety：只使用單一 CTA：完成 15 題測驗，找到你的情感守護者。

### 16. 他沉默時，你最想聽見哪一句話？

- phase：`kpi_backfill`
- status：`blocked_until_published`
- priority：`high`
- platform：`youtube_shorts`
- task：`publish-lt-s01-iris-silence`
- schedule：2026-06-15 20:30 Asia/Taipei
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence
- action：發布後先回填平台貼文 URL 與最小 KPI；有結果後互動時補齊守護者、補給、修復計畫、Luna、收藏、名單、聯盟與 Contact 欄位；週回顧再彙總到腳本級 KPI。
- writeback：platform-kpi-tracker.csv: platform row post_url, site_clicks, quiz_starts, quiz_completions, guardian_result_clicks, resources_clicks, repair_plan_clicks, luna_clicks, keepsake_clicks, free_keepsake_downloads, supply_lead_requests, luna_pack_clicks, affiliate_book_clicks, contact_requests; kpi-tracker.csv: script-level weekly rollup
- blocked by：post_url
- safety：只使用單一 CTA：完成 15 題測驗，找到你的情感守護者。

### 17. 他沉默時，你最想聽見哪一句話？

- phase：`kpi_backfill`
- status：`blocked_until_published`
- priority：`high`
- platform：`tiktok`
- task：`publish-lt-s01-iris-silence`
- schedule：2026-06-15 21:00 Asia/Taipei
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence
- action：發布後先回填平台貼文 URL 與最小 KPI；有結果後互動時補齊守護者、補給、修復計畫、Luna、收藏、名單、聯盟與 Contact 欄位；週回顧再彙總到腳本級 KPI。
- writeback：platform-kpi-tracker.csv: platform row post_url, site_clicks, quiz_starts, quiz_completions, guardian_result_clicks, resources_clicks, repair_plan_clicks, luna_clicks, keepsake_clicks, free_keepsake_downloads, supply_lead_requests, luna_pack_clicks, affiliate_book_clicks, contact_requests; kpi-tracker.csv: script-level weekly rollup
- blocked by：post_url
- safety：只使用單一 CTA：完成 15 題測驗，找到你的情感守護者。

### 18. 他沉默時，你最想聽見哪一句話？

- phase：`kpi_backfill`
- status：`blocked_until_published`
- priority：`high`
- platform：`instagram_reels`
- task：`publish-lt-s01-iris-silence`
- schedule：2026-06-15 21:30 Asia/Taipei
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence
- action：發布後先回填平台貼文 URL 與最小 KPI；有結果後互動時補齊守護者、補給、修復計畫、Luna、收藏、名單、聯盟與 Contact 欄位；週回顧再彙總到腳本級 KPI。
- writeback：platform-kpi-tracker.csv: platform row post_url, site_clicks, quiz_starts, quiz_completions, guardian_result_clicks, resources_clicks, repair_plan_clicks, luna_clicks, keepsake_clicks, free_keepsake_downloads, supply_lead_requests, luna_pack_clicks, affiliate_book_clicks, contact_requests; kpi-tracker.csv: script-level weekly rollup
- blocked by：post_url
- safety：只使用單一 CTA：完成 15 題測驗，找到你的情感守護者。

### 19. 哪一句肯定，會讓你瞬間安心？

- phase：`kpi_backfill`
- status：`blocked_until_published`
- priority：`high`
- platform：`youtube_shorts`
- task：`publish-lt-s02-iris-affirmation`
- schedule：2026-06-17 20:30 Asia/Taipei
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_affirmation
- action：發布後先回填平台貼文 URL 與最小 KPI；有結果後互動時補齊守護者、補給、修復計畫、Luna、收藏、名單、聯盟與 Contact 欄位；週回顧再彙總到腳本級 KPI。
- writeback：platform-kpi-tracker.csv: platform row post_url, site_clicks, quiz_starts, quiz_completions, guardian_result_clicks, resources_clicks, repair_plan_clicks, luna_clicks, keepsake_clicks, free_keepsake_downloads, supply_lead_requests, luna_pack_clicks, affiliate_book_clicks, contact_requests; kpi-tracker.csv: script-level weekly rollup
- blocked by：post_url
- safety：只使用單一 CTA：完成 15 題測驗，找到你的情感守護者。

### 20. 哪一句肯定，會讓你瞬間安心？

- phase：`kpi_backfill`
- status：`blocked_until_published`
- priority：`high`
- platform：`tiktok`
- task：`publish-lt-s02-iris-affirmation`
- schedule：2026-06-17 21:00 Asia/Taipei
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_affirmation
- action：發布後先回填平台貼文 URL 與最小 KPI；有結果後互動時補齊守護者、補給、修復計畫、Luna、收藏、名單、聯盟與 Contact 欄位；週回顧再彙總到腳本級 KPI。
- writeback：platform-kpi-tracker.csv: platform row post_url, site_clicks, quiz_starts, quiz_completions, guardian_result_clicks, resources_clicks, repair_plan_clicks, luna_clicks, keepsake_clicks, free_keepsake_downloads, supply_lead_requests, luna_pack_clicks, affiliate_book_clicks, contact_requests; kpi-tracker.csv: script-level weekly rollup
- blocked by：post_url
- safety：只使用單一 CTA：完成 15 題測驗，找到你的情感守護者。

### 21. 哪一句肯定，會讓你瞬間安心？

- phase：`kpi_backfill`
- status：`blocked_until_published`
- priority：`high`
- platform：`instagram_reels`
- task：`publish-lt-s02-iris-affirmation`
- schedule：2026-06-17 21:30 Asia/Taipei
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_affirmation
- action：發布後先回填平台貼文 URL 與最小 KPI；有結果後互動時補齊守護者、補給、修復計畫、Luna、收藏、名單、聯盟與 Contact 欄位；週回顧再彙總到腳本級 KPI。
- writeback：platform-kpi-tracker.csv: platform row post_url, site_clicks, quiz_starts, quiz_completions, guardian_result_clicks, resources_clicks, repair_plan_clicks, luna_clicks, keepsake_clicks, free_keepsake_downloads, supply_lead_requests, luna_pack_clicks, affiliate_book_clicks, contact_requests; kpi-tracker.csv: script-level weekly rollup
- blocked by：post_url
- safety：只使用單一 CTA：完成 15 題測驗，找到你的情感守護者。

### 22. 你真的太敏感嗎？還是你只是等一句清楚的話？

- phase：`kpi_backfill`
- status：`blocked_until_published`
- priority：`high`
- platform：`youtube_shorts`
- task：`publish-lt-s03-iris-too-sensitive`
- schedule：2026-06-19 20:30 Asia/Taipei
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_too_sensitive
- action：發布後先回填平台貼文 URL 與最小 KPI；有結果後互動時補齊守護者、補給、修復計畫、Luna、收藏、名單、聯盟與 Contact 欄位；週回顧再彙總到腳本級 KPI。
- writeback：platform-kpi-tracker.csv: platform row post_url, site_clicks, quiz_starts, quiz_completions, guardian_result_clicks, resources_clicks, repair_plan_clicks, luna_clicks, keepsake_clicks, free_keepsake_downloads, supply_lead_requests, luna_pack_clicks, affiliate_book_clicks, contact_requests; kpi-tracker.csv: script-level weekly rollup
- blocked by：post_url
- safety：只使用單一 CTA：完成 15 題測驗，找到你的情感守護者。

### 23. 你真的太敏感嗎？還是你只是等一句清楚的話？

- phase：`kpi_backfill`
- status：`blocked_until_published`
- priority：`high`
- platform：`tiktok`
- task：`publish-lt-s03-iris-too-sensitive`
- schedule：2026-06-19 21:00 Asia/Taipei
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_too_sensitive
- action：發布後先回填平台貼文 URL 與最小 KPI；有結果後互動時補齊守護者、補給、修復計畫、Luna、收藏、名單、聯盟與 Contact 欄位；週回顧再彙總到腳本級 KPI。
- writeback：platform-kpi-tracker.csv: platform row post_url, site_clicks, quiz_starts, quiz_completions, guardian_result_clicks, resources_clicks, repair_plan_clicks, luna_clicks, keepsake_clicks, free_keepsake_downloads, supply_lead_requests, luna_pack_clicks, affiliate_book_clicks, contact_requests; kpi-tracker.csv: script-level weekly rollup
- blocked by：post_url
- safety：只使用單一 CTA：完成 15 題測驗，找到你的情感守護者。

### 24. 你真的太敏感嗎？還是你只是等一句清楚的話？

- phase：`kpi_backfill`
- status：`blocked_until_published`
- priority：`high`
- platform：`instagram_reels`
- task：`publish-lt-s03-iris-too-sensitive`
- schedule：2026-06-19 21:30 Asia/Taipei
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_too_sensitive
- action：發布後先回填平台貼文 URL 與最小 KPI；有結果後互動時補齊守護者、補給、修復計畫、Luna、收藏、名單、聯盟與 Contact 欄位；週回顧再彙總到腳本級 KPI。
- writeback：platform-kpi-tracker.csv: platform row post_url, site_clicks, quiz_starts, quiz_completions, guardian_result_clicks, resources_clicks, repair_plan_clicks, luna_clicks, keepsake_clicks, free_keepsake_downloads, supply_lead_requests, luna_pack_clicks, affiliate_book_clicks, contact_requests; kpi-tracker.csv: script-level weekly rollup
- blocked by：post_url
- safety：只使用單一 CTA：完成 15 題測驗，找到你的情感守護者。

## 不做事項

- 未有發布與 KPI 回填前，不改商品排序、不加重付費 CTA、不判定優勝守護者。
- 不把測驗結果寫成診斷，不承諾療效，不用恐嚇式文案。
- 若平台不允許長連結，使用 `/start/`，但 KPI 回填仍要保留對應 `utm_content`。
