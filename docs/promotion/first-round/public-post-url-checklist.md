# LoveTypes Public Post URL Checklist

- 產生日期：2026-06-22
- first-batch posts：1
- published posts：1
- checklist rows：8
- pending publish rows：0
- missing rows：0
- 用途：第一批貼文發布後，確認公開 URL、平台網域、CTA、UTM、proof note 與初始 KPI 來源。

## Rule

- 沒有真實公開 post_url 時，所有檢查保持 pending_publish。
- post_url 必須是對應平台的公開 https URL，不能用 placeholder 或登入後才看得到的草稿頁。
- site_clicks / quiz_starts / quiz_completions 可以是 0，但必須先確認數據來源真的被檢查過。

## youtube_shorts · `publish-lt-s01-iris-silence`

- script：`lt-s01-iris-silence`
- guardian：`iris`
- post URL：https://www.youtube.com/watch?v=uj9ZwYIKDrE
- tracked URL：https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence

- [x] `post_url_present`：公開貼文 URL 已取得（complete）
- [x] `platform_domain_matches`：平台網域正確（complete）
- [ ] `public_view_checked`：一般訪客可驗證（operator_verify）
- [x] `caption_cta_checked`：Caption CTA 仍是測驗（complete）
- [x] `tracked_url_visible`：追蹤連結或 bio 指引存在（complete）
- [x] `utm_content_recorded`：UTM content 已記錄（complete）
- [x] `proof_note_traceable`：Proof note 可追溯（complete）
- [ ] `starter_kpi_source_checked`：初始 KPI 來源已檢查（operator_verify）
