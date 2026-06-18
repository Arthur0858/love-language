# LoveTypes Lead Writeback Playbook

- 產生日期：2026-06-18
- real leads：0
- template rows：15
- issues：0
- 原則：只有收到真實 Contact / 收藏室 / Luna / 補給願望來信後，才能新增 real lead。
- 隱私：不把原始 email 寫入 CSV；只記 request_id、守護者、需求類型、來源與 proof note。

## 回填命令範例

### 艾莉絲（`iris`）

- 自有素材需求：`python3 tools/promotion_lead_writeback.py add --source contact --guardian iris --intake-type owned_asset_request --consent-status explicit_reply_ok --proof-note "email thread iris-owned request checked 2026-06-18"`
- Luna 場景需求：`python3 tools/promotion_lead_writeback.py add --source luna_page --guardian iris --intake-type luna_scene_request --consent-status explicit_reply_ok --proof-note "email thread iris-luna request checked 2026-06-18"`

### 諾雅（`noah`）

- 自有素材需求：`python3 tools/promotion_lead_writeback.py add --source contact --guardian noah --intake-type owned_asset_request --consent-status explicit_reply_ok --proof-note "email thread noah-owned request checked 2026-06-18"`
- Luna 場景需求：`python3 tools/promotion_lead_writeback.py add --source luna_page --guardian noah --intake-type luna_scene_request --consent-status explicit_reply_ok --proof-note "email thread noah-luna request checked 2026-06-18"`

### 薇薇安（`vivian`）

- 自有素材需求：`python3 tools/promotion_lead_writeback.py add --source contact --guardian vivian --intake-type owned_asset_request --consent-status explicit_reply_ok --proof-note "email thread vivian-owned request checked 2026-06-18"`
- Luna 場景需求：`python3 tools/promotion_lead_writeback.py add --source luna_page --guardian vivian --intake-type luna_scene_request --consent-status explicit_reply_ok --proof-note "email thread vivian-luna request checked 2026-06-18"`

### 克萊兒（`claire`）

- 自有素材需求：`python3 tools/promotion_lead_writeback.py add --source contact --guardian claire --intake-type owned_asset_request --consent-status explicit_reply_ok --proof-note "email thread claire-owned request checked 2026-06-18"`
- Luna 場景需求：`python3 tools/promotion_lead_writeback.py add --source luna_page --guardian claire --intake-type luna_scene_request --consent-status explicit_reply_ok --proof-note "email thread claire-luna request checked 2026-06-18"`

### 朵拉（`dora`）

- 自有素材需求：`python3 tools/promotion_lead_writeback.py add --source contact --guardian dora --intake-type owned_asset_request --consent-status explicit_reply_ok --proof-note "email thread dora-owned request checked 2026-06-18"`
- Luna 場景需求：`python3 tools/promotion_lead_writeback.py add --source luna_page --guardian dora --intake-type luna_scene_request --consent-status explicit_reply_ok --proof-note "email thread dora-luna request checked 2026-06-18"`

## 結構化文字匯入

- Contact 與收藏室的結構化表單會產生 `LoveTypes 結構化需求` 文字。
- 收到來信後，先把該段文字存成暫存 `.txt`，再用匯入工具解析欄位；工具不會把 email 原文寫進 tracker。
- 檢查：`python3 tools/promotion_lead_text_import.py check --input /path/to/request.txt`
- 寫入：`python3 tools/promotion_lead_text_import.py add --input /path/to/request.txt --proof-note "email thread Gmail request checked YYYY-MM-DD"`

## 安全規則

- 不用本工具偽造名單、來信、同意或 KPI。
- `--utm-content` 能對上 attribution 時才會回填 KPI；對不上時只記 manual lead。
- 同守護者同需求重複出現後，才提高自有素材或 Luna 商品化優先級。
