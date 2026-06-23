# LoveTypes Platform Account Identity Checklist

- 產生日期：2026-06-24
- platforms：1
- checklist rows：7
- pending rows：7
- configured profiles：1
- 用途：設定 profile link 或發布第一批貼文前，先確認正在操作正確平台帳號/頻道。

## Rule

- 不因為瀏覽器已登入就假設帳號正確。
- 看不到 LoveTypes 對應公開頁、可編輯權限或 profile link 欄位時，停止設定與發布。
- 設定後要保留可追溯 proof note，再執行 profile writeback。

## YouTube Shorts（`youtube_shorts`）

- planned profile link：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
- current tracker status：`set`
- proof note template：`<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified`

- [ ] `visible_account_matches_lovetypes`：可見帳號是 LoveTypes 發布帳號，平台右上角、個人頁或頻道名稱能證明正在操作 LoveTypes 相關帳號。
- [ ] `public_profile_page_opened`：公開個人頁已開啟，從平台公開頁確認目前帳號/頻道是即將貼 profile link 的公開頁。
- [ ] `profile_edit_permission_visible`：可編輯 profile/bio，畫面顯示可編輯 bio、website、description 或 channel profile。
- [ ] `profile_link_field_located`：已找到 profile link 欄位，操作者知道連結要貼到哪個欄位，不把追蹤連結貼到錯誤位置。
- [ ] `planned_profile_url_ready`：平台專屬 profile URL 已備妥，使用 platform-profile-tracker.csv 的平台專屬 /start/ UTM 連結。
- [ ] `proof_capture_ready`：截圖或證據命名已準備，設定前先準備 proof note，寫入前必須把 <REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> 換成真截圖、公開點擊或平台 URL 證據。
- [ ] `do_not_publish_wrong_account`：錯帳號時停止發布，若帳號名稱、頻道、權限或公開頁不一致，不設定 profile link，也不發布貼文。
