# LoveTypes Launch Blocker Digest

- 產生日期：2026-06-14
- current stage：`profile_setup`
- first blocker：`set_platform_profile_links`
- profile configured：0 / 3
- real profile proof ready：0 / 3
- external profile proof blockers：3
- current true blockers：1
- first batch published：0 / 3
- filled KPI rows：0
- active blockers：14
- ready now：3
- empty data mode：1
- issues：0

## Next Action

- action：Set the three external platform profile links, capture real proof, then import profile proof text.
- command：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-<platform>.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`
- release：promotion_launch_readiness_profile_configured=3 and ready_to_publish=1

## First Blocker

- phase：`profile_setup`
- severity：`launch_blocker`
- message：3 個平台個人頁仍未全部標記為 set/live；發布前先把 Bio/Profile link 設為平台專屬 /start/ 追蹤連結。

## Allowed Now

- Set or verify external platform profile links.
- Replace placeholder profile proof with real screenshot/click evidence, then import only source-checked profile proof.
- Refresh daily ops packets after any writeback.

## Do Not Do

- Do not publish first-batch posts before all profile rows are set/live.
- Do not mark posts published without real public post URLs.
- Do not fill KPI values from guesses or placeholders.
- Do not change Luna, affiliate, paid offer, or guardian winner decisions while empty_data_mode=1.

## Evidence Snapshot

- command ready / prepared / blocked：3 / 3 / 18
- profile completion blockers：1
- profile placeholder proof rows：3
- weekly ready：0
- KPI posting / platform / script rows：45 / 45 / 15
- attribution rows：18
