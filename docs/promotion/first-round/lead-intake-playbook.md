# LoveTypes 名單承接 Playbook

- 產生日期：2026-06-20
- 模板列數：15
- 用途：把 Contact、補給願望、收藏物等待清單與 Luna 需求轉成可回填、可排序、可履約的素材線索。
- Attribution：用 Contact 信中的 `Campaign content / 推廣內容` 對回 `attribution-reconciliation.csv`。

## 使用規則

- 收到 Contact、收藏室等待清單或旅人補給願望後，先填 lead-intake-tracker.csv。
- 把 Contact 信中的 Campaign content / 推廣內容 複製到 utm_content，並用 attribution-reconciliation.csv 找到對應腳本。
- 依 intake_type 回填 kpi_writeback_field；找不到 utm_content 時，只記錄 manual lead，不判定優勝腳本。
- 同一守護者同一需求類型重複出現兩次以上，才排進自有素材製作。
- Luna 或聯盟需求只在測驗結果後路線測試，不把 Shorts CTA 改成購買。
- 回覆時保持安全邊界：不診斷、不承諾療效、不要求敏感個資。

## 五守護者承接路線

### 艾莉絲（iris）

- 名單資產 ID：supply-wishlist-iris
- 安全策略：只記錄守護者、需求類型、素材偏好與可回覆信箱；不要求測驗分數、敏感個資或關係細節。
- 可對照 utm_content：iris_affirmation, iris_silence, iris_too_sensitive
- `owned_asset_request`：guardian PDF / wallpaper / short ritual -> `supply_lead_requests` -> https://lovetypes.tw/keepsakes/#keepsake-iris
- `luna_scene_request`：Luna bedtime / conflict cooldown / quiz aftercare pack -> `luna_pack_clicks` -> https://lovetypes.tw/luna-yoga-music/#luna-iris
- `repair_or_contact_request`：relationship repair prompt / supply route guidance -> `contact_requests` -> https://lovetypes.tw/contact/#luna-supply-request

### 諾雅（noah）

- 名單資產 ID：supply-wishlist-noah
- 安全策略：只記錄守護者、需求類型、素材偏好與可回覆信箱；不要求測驗分數、敏感個資或關係細節。
- 可對照 utm_content：noah_cancel, noah_phone, noah_quiet_time
- `owned_asset_request`：guardian PDF / wallpaper / short ritual -> `supply_lead_requests` -> https://lovetypes.tw/keepsakes/#keepsake-noah
- `luna_scene_request`：Luna bedtime / conflict cooldown / quiz aftercare pack -> `luna_pack_clicks` -> https://lovetypes.tw/luna-yoga-music/#luna-noah
- `repair_or_contact_request`：relationship repair prompt / supply route guidance -> `contact_requests` -> https://lovetypes.tw/contact/#luna-supply-request

### 薇薇安（vivian）

- 名單資產 ID：supply-wishlist-vivian
- 安全策略：只記錄守護者、需求類型、素材偏好與可回覆信箱；不要求測驗分數、敏感個資或關係細節。
- 可對照 utm_content：vivian_forgotten_date, vivian_remembered, vivian_ritual
- `owned_asset_request`：guardian PDF / wallpaper / short ritual -> `supply_lead_requests` -> https://lovetypes.tw/keepsakes/#keepsake-vivian
- `luna_scene_request`：Luna bedtime / conflict cooldown / quiz aftercare pack -> `luna_pack_clicks` -> https://lovetypes.tw/luna-yoga-music/#luna-vivian
- `repair_or_contact_request`：relationship repair prompt / supply route guidance -> `contact_requests` -> https://lovetypes.tw/contact/#luna-supply-request

### 克萊兒（claire）

- 名單資產 ID：supply-wishlist-claire
- 安全策略：只記錄守護者、需求類型、素材偏好與可回覆信箱；不要求測驗分數、敏感個資或關係細節。
- 可對照 utm_content：claire_ask_help, claire_promises, claire_tired
- `owned_asset_request`：guardian PDF / wallpaper / short ritual -> `supply_lead_requests` -> https://lovetypes.tw/keepsakes/#keepsake-claire
- `luna_scene_request`：Luna bedtime / conflict cooldown / quiz aftercare pack -> `luna_pack_clicks` -> https://lovetypes.tw/luna-yoga-music/#luna-claire
- `repair_or_contact_request`：relationship repair prompt / supply route guidance -> `contact_requests` -> https://lovetypes.tw/contact/#luna-supply-request

### 朵拉（dora）

- 名單資產 ID：supply-wishlist-dora
- 安全策略：只記錄守護者、需求類型、素材偏好與可回覆信箱；不要求測驗分數、敏感個資或關係細節。
- 可對照 utm_content：dora_after_conflict, dora_consent, dora_distance
- `owned_asset_request`：guardian PDF / wallpaper / short ritual -> `supply_lead_requests` -> https://lovetypes.tw/keepsakes/#keepsake-dora
- `luna_scene_request`：Luna bedtime / conflict cooldown / quiz aftercare pack -> `luna_pack_clicks` -> https://lovetypes.tw/luna-yoga-music/#luna-dora
- `repair_or_contact_request`：relationship repair prompt / supply route guidance -> `contact_requests` -> https://lovetypes.tw/contact/#luna-supply-request

## 回填欄位

- `request_id`: 真實需求發生後改成可追蹤 ID，例如 `2026-06-15-iris-owned-001`。
- `source`: 模板列維持 template；真實需求發生後改成 contact、keepsake_waitlist、resources_wishlist、luna_page 或 manual_reply。
- `utm_content`: 從 Contact 信中的 `Campaign content / 推廣內容` 複製；若沒有，保留空白並只當質性線索。
- `kpi_writeback_field`: 依需求類型回填到 `kpi-tracker.csv` 的對應欄位。
- `email_status`: not_received、received、replied、fulfilled、closed。
- `consent_status`: not_applicable_until_user_contacts、explicit_reply_ok、do_not_contact。
- `status`: template、new、triaged、queued、fulfilled、closed。

## 安全邊界

- 模板列不代表真實名單或需求，不可當成成效數據。
- 沒有對上的 `utm_content` 不可用來判定哪支 Shorts 獲勝。
- 不要求測驗分數、敏感個資、緊急求助內容或諮商替代承諾。
- 同守護者同需求至少重複兩次，才提高自有素材或 Luna 商品承接優先級。
