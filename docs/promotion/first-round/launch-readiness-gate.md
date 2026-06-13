# LoveTypes Launch Readiness Gate

- 產生日期：2026-06-13
- 結構就緒：`1`
- 可開始設定平台入口：`1`
- 可發布首批貼文：`0`
- 可做 KPI/商品判斷：`0`
- 空資料模式：`1`

## 目前數字

- 平台個人頁：0 / 3 已標記 set/live
- 平台追蹤連結：3 / 3 有效
- 首批排程：3 / 3 有效
- 首週排程：9 / 9 有效
- 素材就緒檢查：3
- 已發布平台列：0
- 已回填 KPI 列：0

## 下一個決策

- 先設定三個平台個人頁連結；完成 set/live 後發布首批三平台貼文。

## 阻擋項

- `set_platform_profile_links`：三個平台個人頁仍未標記為 set/live；發布前先把 Bio/Profile link 設為平台專屬 /start/ 追蹤連結。
- `publish_first_batch`：首批三平台貼文尚未標記 published；沒有 post_url 前不能開始 KPI 判讀。
- `backfill_first_batch_kpis`：KPI 尚未回填到前三筆；保持測驗 CTA，不調整商品、Luna 或聯盟權重。

## 安全界線

- 空資料模式下不改商品排序、不加重 Luna 或聯盟 CTA。
- Shorts 與個人頁入口維持單一 CTA：完成 15 題測驗，找到你的情感守護者。
- KPI 未回填前，不判定優勝守護者，不承諾療效，不寫診斷式文案。
