# LoveTypes Weekly Decision Evidence Checklist

- 產生日期：2026-06-24
- checklist rows：8
- complete rows：4
- pending rows：4
- weekly ready：0
- decision ready：0
- empty data mode：0
- 用途：週回顧前確認 profile、公開貼文、KPI、0 值來源與空資料安全邊界都已滿足。

## Rule

- 不能用單一指標或空資料調整商品、Luna、聯盟或守護者優先序。
- 週決策必須同時具備公開 URL、KPI 來源、週摘要與 gate 通過。
- 只要仍是 empty data mode，就保持收集訊號，不做商品化判斷。

- [ ] `profiles_configured`：All active platform profile links are set/live with traceable evidence.（pending；啟用平台 profile 尚未全部 set/live。）
- [x] `first_batch_published`：First-batch posts are published on all active platforms.（complete；證據已滿足。）
- [x] `public_post_urls_verified`：Every public post URL has platform domain, public view, CTA, UTM, and proof evidence checked.（complete；證據已滿足。）
- [ ] `zero_kpis_have_source`：Zero values for site_clicks, quiz_starts, and quiz_completions have checked-source proof.（pending；核心 KPI 仍未發布、未回填，或 0 值缺來源證據。）
- [ ] `weekly_review_ready`：Weekly review packet reports readyForWeeklyDecision=1.（pending；weekly review 尚未達可決策狀態。）
- [x] `not_empty_data_mode`：Empty data mode is false before commerce or prioritization decisions.（complete；證據已滿足。）
- [ ] `decision_gate_ready`：Week decision gate allows at least weeklyDecision before changing content or commerce paths.（pending；week decision gate 仍是 HOLD。）
- [x] `commerce_changes_still_blocked`：Paid CTA, Luna emphasis, affiliate emphasis, and offer order remain blocked until intent exists.（complete；證據已滿足。）
