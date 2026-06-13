# LoveTypes Attribution Reconciliation

- 產生日期：2026-06-13
- Attribution rows：18
- Profile rows：3
- Shorts rows：15
- 已有 KPI row：15
- 已完整回填 KPI row：0
- 歸因規則：Profile rows 回填 platform-profile-tracker.csv；Shorts rows 回填 kpi-tracker.csv；空資料時維持 collect_signal，不加重付費或聯盟 CTA。
- KPI 完整回填定義：A KPI row is filled only after post_url exists and at least one required metric is non-zero.

## 使用方式

- 發布或收到 Contact 信後，先找信件中的 `推廣內容 / Campaign content`，對回本表 `utm_content`。
- 若是 Shorts row，把 `post_url` 與平台數據回填到 `kpi-tracker.csv` 的同一個 `utm_content`。
- 若是 Profile row，把平台首頁數據回填到 `platform-profile-tracker.csv`，不要混進單支影片 KPI。
- 沒有 KPI 前只維持 `collect_signal`，不判定優勝守護者、不加重付費 CTA。
- 必填 KPI 欄位：`site_clicks, quiz_starts, quiz_completions, guardian_result_clicks, resources_clicks, repair_plan_clicks, luna_clicks, keepsake_clicks, free_keepsake_downloads, supply_lead_requests, luna_pack_clicks, affiliate_book_clicks, contact_requests`。

## Decision Stages

- `collect_signal`: 先發布或回填資料。
- `scale_quiz_completion`: 有測驗完成，先放大相近 hook。
- `deepen_identity_asset`: 有路線或收藏興趣，先強化免費守護者資產。
- `build_owned_asset`: 有補給或 Contact 意圖，優先做 Email/免費素材承接。
- `test_soft_offer`: 有 Luna 或聯盟點擊，再測柔性商品承接。

## Rows

### instagram_reels_bio

- type：`profile`
- platform：`instagram_reels`
- guardian：`` 
- angle：
- KPI status：`profile_link_only`
- decision：`collect_signal`
- Contact 對照：`Campaign content / 推廣內容 = instagram_reels_bio`
- 下一步：Publish or backfill KPI first; do not pick a winning guardian from empty data.
- URL：https://lovetypes.tw/start/?utm_source=instagram&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=instagram_reels_bio

### tiktok_bio

- type：`profile`
- platform：`tiktok`
- guardian：`` 
- angle：
- KPI status：`profile_link_only`
- decision：`collect_signal`
- Contact 對照：`Campaign content / 推廣內容 = tiktok_bio`
- 下一步：Publish or backfill KPI first; do not pick a winning guardian from empty data.
- URL：https://lovetypes.tw/start/?utm_source=tiktok&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=tiktok_bio

### youtube_shorts_bio

- type：`profile`
- platform：`youtube_shorts`
- guardian：`` 
- angle：
- KPI status：`profile_link_only`
- decision：`collect_signal`
- Contact 對照：`Campaign content / 推廣內容 = youtube_shorts_bio`
- 下一步：Publish or backfill KPI first; do not pick a winning guardian from empty data.
- URL：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio

### claire_ask_help

- type：`shorts`
- platform：`all`
- guardian：`claire` 克萊兒
- angle：測驗入口
- KPI status：`ready_for_backfill`
- decision：`collect_signal`
- Contact 對照：`Campaign content / 推廣內容 = claire_ask_help`
- 下一步：Publish or backfill KPI first; do not pick a winning guardian from empty data.
- URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=claire_ask_help

### claire_promises

- type：`shorts`
- platform：`all`
- guardian：`claire` 克萊兒
- angle：守護者人格認同
- KPI status：`ready_for_backfill`
- decision：`collect_signal`
- Contact 對照：`Campaign content / 推廣內容 = claire_promises`
- 下一步：Publish or backfill KPI first; do not pick a winning guardian from empty data.
- URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=claire_promises

### claire_tired

- type：`shorts`
- platform：`all`
- guardian：`claire` 克萊兒
- angle：情感錯頻情境
- KPI status：`ready_for_backfill`
- decision：`collect_signal`
- Contact 對照：`Campaign content / 推廣內容 = claire_tired`
- 下一步：Publish or backfill KPI first; do not pick a winning guardian from empty data.
- URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=claire_tired

### dora_after_conflict

- type：`shorts`
- platform：`all`
- guardian：`dora` 朵拉
- angle：測驗入口
- KPI status：`ready_for_backfill`
- decision：`collect_signal`
- Contact 對照：`Campaign content / 推廣內容 = dora_after_conflict`
- 下一步：Publish or backfill KPI first; do not pick a winning guardian from empty data.
- URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=dora_after_conflict

### dora_consent

- type：`shorts`
- platform：`all`
- guardian：`dora` 朵拉
- angle：守護者人格認同
- KPI status：`ready_for_backfill`
- decision：`collect_signal`
- Contact 對照：`Campaign content / 推廣內容 = dora_consent`
- 下一步：Publish or backfill KPI first; do not pick a winning guardian from empty data.
- URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=dora_consent

### dora_distance

- type：`shorts`
- platform：`all`
- guardian：`dora` 朵拉
- angle：情感錯頻情境
- KPI status：`ready_for_backfill`
- decision：`collect_signal`
- Contact 對照：`Campaign content / 推廣內容 = dora_distance`
- 下一步：Publish or backfill KPI first; do not pick a winning guardian from empty data.
- URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=dora_distance

### iris_affirmation

- type：`shorts`
- platform：`all`
- guardian：`iris` 艾莉絲
- angle：守護者人格認同
- KPI status：`ready_for_backfill`
- decision：`collect_signal`
- Contact 對照：`Campaign content / 推廣內容 = iris_affirmation`
- 下一步：Publish or backfill KPI first; do not pick a winning guardian from empty data.
- URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_affirmation

### iris_silence

- type：`shorts`
- platform：`all`
- guardian：`iris` 艾莉絲
- angle：情感錯頻情境
- KPI status：`ready_for_backfill`
- decision：`collect_signal`
- Contact 對照：`Campaign content / 推廣內容 = iris_silence`
- 下一步：Publish or backfill KPI first; do not pick a winning guardian from empty data.
- URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence

### iris_too_sensitive

- type：`shorts`
- platform：`all`
- guardian：`iris` 艾莉絲
- angle：測驗入口
- KPI status：`ready_for_backfill`
- decision：`collect_signal`
- Contact 對照：`Campaign content / 推廣內容 = iris_too_sensitive`
- 下一步：Publish or backfill KPI first; do not pick a winning guardian from empty data.
- URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_too_sensitive

### noah_cancel

- type：`shorts`
- platform：`all`
- guardian：`noah` 諾雅
- angle：守護者人格認同
- KPI status：`ready_for_backfill`
- decision：`collect_signal`
- Contact 對照：`Campaign content / 推廣內容 = noah_cancel`
- 下一步：Publish or backfill KPI first; do not pick a winning guardian from empty data.
- URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=noah_cancel

### noah_phone

- type：`shorts`
- platform：`all`
- guardian：`noah` 諾雅
- angle：情感錯頻情境
- KPI status：`ready_for_backfill`
- decision：`collect_signal`
- Contact 對照：`Campaign content / 推廣內容 = noah_phone`
- 下一步：Publish or backfill KPI first; do not pick a winning guardian from empty data.
- URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=noah_phone

### noah_quiet_time

- type：`shorts`
- platform：`all`
- guardian：`noah` 諾雅
- angle：測驗入口
- KPI status：`ready_for_backfill`
- decision：`collect_signal`
- Contact 對照：`Campaign content / 推廣內容 = noah_quiet_time`
- 下一步：Publish or backfill KPI first; do not pick a winning guardian from empty data.
- URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=noah_quiet_time

### vivian_forgotten_date

- type：`shorts`
- platform：`all`
- guardian：`vivian` 薇薇安
- angle：守護者人格認同
- KPI status：`ready_for_backfill`
- decision：`collect_signal`
- Contact 對照：`Campaign content / 推廣內容 = vivian_forgotten_date`
- 下一步：Publish or backfill KPI first; do not pick a winning guardian from empty data.
- URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=vivian_forgotten_date

### vivian_remembered

- type：`shorts`
- platform：`all`
- guardian：`vivian` 薇薇安
- angle：情感錯頻情境
- KPI status：`ready_for_backfill`
- decision：`collect_signal`
- Contact 對照：`Campaign content / 推廣內容 = vivian_remembered`
- 下一步：Publish or backfill KPI first; do not pick a winning guardian from empty data.
- URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=vivian_remembered

### vivian_ritual

- type：`shorts`
- platform：`all`
- guardian：`vivian` 薇薇安
- angle：測驗入口
- KPI status：`ready_for_backfill`
- decision：`collect_signal`
- Contact 對照：`Campaign content / 推廣內容 = vivian_ritual`
- 下一步：Publish or backfill KPI first; do not pick a winning guardian from empty data.
- URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=vivian_ritual
