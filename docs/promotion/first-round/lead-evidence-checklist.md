# LoveTypes Lead Evidence Checklist

- 產生日期：2026-07-02
- lead rows：15
- real rows：0
- checklist rows：135
- missing rows：0
- 用途：真實需求寫回 KPI 或素材履約前，逐項確認來源、同意、守護者路線與安全邊界。
- 隱私：不把原始 email 寫進 CSV，只保留可追蹤 request_id 與 proof note。

## Required Evidence

- `source_traceable`：來源可追蹤，source is contact, keepsake_waitlist, resources_wishlist, luna_page, or manual_reply.
- `guardian_route_present`：守護者與路線存在，guardian_id, guardian_name, and related_route are present.
- `intake_type_present`：需求類型明確，intake_type maps to owned asset, Luna scene, or repair/contact request.
- `asset_preference_present`：素材偏好明確，requested_asset describes the requested PDF, wallpaper, ritual, Luna scene, or repair prompt.
- `reply_email_available`：可回覆信箱已取得，reply email exists in the source email or structured request, but raw email is not stored in CSV.
- `explicit_consent`：明確同意可回覆，consent_status is explicit_reply_ok before any KPI or fulfillment writeback.
- `attribution_or_manual_rule`：歸因規則已判定，utm_content is matched for KPI writeback, or left as manual lead only.
- `safe_scope_verified`：安全範圍已確認，request is not emergency support, diagnosis, therapy replacement, or sensitive personal-data collection.
- `proof_note_traceable`：證據註記可追溯，notes include a verified proof note or the operator has a traceable external proof note.

## Operator Rule

- `pending_real_request`：模板列，不能當作真實需求。
- `complete`：欄位證據已存在。
- `operator_verify`：需在信件或外部證據中人工確認，但不可把原始 email 寫入 CSV。
- `manual_only`：可以當質性線索，不可回填為 Shorts / profile 勝出依據。
- `missing`：不可寫回 KPI，不可履約。
