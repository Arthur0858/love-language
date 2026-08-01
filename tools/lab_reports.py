"""Reproducible LoveTypes product test reports shown on the public lab pages."""

LAB_UPDATED = "2026-08-01"

LAB_REPORTS = [
    {
        "slug": "quiz-scoring-test",
        "title": "15 題測驗評分與同分處理實測",
        "desc": "逐題固定輸入，核對五位守護者分數、百分比與同分排序是否一致。",
        "summary": "本次測試不是驗證心理效度，而是確認網站寫出的計分規則確實照預期執行。測試人員使用固定答案序列完成 15 題，記錄原始計數、顯示百分比、主要守護者與重新整理後保存結果；再建立同分序列，確認排序使用固定題目順序而不會隨機跳動。",
        "environment": ["macOS 桌面版 Chromium，1440×900", "行動版 Chromium 模擬，360×800", "正式 quiz-data-zh 資料檔", "無登入、無伺服器端個人資料"],
        "steps": ["清除 LoveTypes localStorage 後開啟首頁測驗。", "依預先記錄的 15 題答案完成一次作答。", "人工計算五個選項出現次數並與結果列比較。", "以同分答案序列再測一次，重新整理頁面確認結果不漂移。"],
        "results": [("一般序列", "15 題皆被計入，五個百分比合計 100%", "通過"), ("同分序列", "主要結果依固定排序決定，重新整理後相同", "通過"), ("未完成離開", "不產生完成結果", "通過"), ("重新測驗", "舊結果清除後從第 1 題開始", "通過")],
        "failure": "早期檢查發現結果頁同時出現太多後續購買選項，容易讓計分說明被忽略。這不是計分錯誤，但會降低使用者理解分數的機會。",
        "fix": "結果的第一層行動收斂為守護者解讀、免費修復與重新測驗；購買連結只留在獨立揭露頁。",
        "limitations": "這項測試只證明程式計數與顯示一致，不代表 15 題能診斷人格、依附型態或關係品質。近期事件與題意理解都可能影響作答。",
        "screenshot": "/assets/lovetypes/lab/quiz-scoring-test.webp",
        "screenshot_alt": "LoveTypes 15 題測驗結果與五個分數列的行動版測試畫面",
    },
    {
        "slug": "result-consistency-test",
        "title": "相同情境重測的一致性與限制",
        "desc": "以相同答案、單題變更與不同裝置寬度重測，記錄結果何時維持、何時改變。",
        "summary": "一致性測試使用三組可重現輸入：完全相同答案、只改一題、把最高分兩類拉近。完全相同答案應得到同一守護者；改一題可能只改次要排序，也可能在分數接近時改變主要結果。頁面因此不能宣稱結果永久固定，並應讓使用者看見完整分數而不只看角色名稱。",
        "environment": ["Chromium 桌面與行動視窗", "同一份繁中題目資料", "每輪測試前清除保存結果", "關閉網路後重讀已載入頁面一次"],
        "steps": ["完成基準答案並保存五類原始分數。", "清除後輸入完全相同答案，對照結果。", "第三輪只替換第 8 題答案。", "第四輪調整兩題，使前兩類分數接近並觀察說明。"],
        "results": [("完全相同答案", "主要守護者與全部分數一致", "通過"), ("只改一題", "只變更受影響類別，沒有其他隨機差異", "通過"), ("接近同分", "完整分數仍可見，主要結果沒有被描述成唯一答案", "通過"), ("不同寬度", "排序與文字不因版面改變", "通過")],
        "failure": "舊版結果文案較像固定類型，沒有充分提醒一題變動可能影響接近同分的結果。",
        "fix": "結果與理論頁統一加入「此刻的接收入口」及重測限制，保留五類分數供讀者自行比較。",
        "limitations": "這是軟體一致性測試，不是重測信度研究；沒有招募受試者，也不推論分數的臨床意義。",
        "screenshot": "/assets/lovetypes/lab/result-consistency-test.webp",
        "screenshot_alt": "同一組 LoveTypes 答案在桌面重測後顯示一致守護者的記錄畫面",
    },
    {
        "slug": "local-storage-privacy-test",
        "title": "瀏覽器保存、清除與跨裝置限制實測",
        "desc": "確認測驗與修復資料只保存在目前瀏覽器，並驗證清除功能與共用裝置風險提示。",
        "summary": "LoveTypes 不要求帳號，測驗結果與修復表使用 localStorage。這次測試直接檢查保存鍵、重新整理、清除按鈕、無痕視窗與另一個瀏覽器，確認資料不會自動同步。公開報告不揭露任何真實作答內容，只描述技術行為。",
        "environment": ["Chromium 一般視窗與無痕視窗", "第二個獨立瀏覽器內容區", "瀏覽器開發者工具 Application 面板", "不使用帳號、Cookie 或遠端資料庫"],
        "steps": ["完成測驗並填寫一個修復欄位。", "重新整理，確認目前瀏覽器仍能讀取。", "按清除結果與清除工作表，再檢查保存鍵。", "開啟無痕視窗及第二瀏覽器，確認沒有同步資料。"],
        "results": [("重新整理", "目前瀏覽器保留已保存內容", "通過"), ("清除按鈕", "對應鍵移除且畫面回到空白狀態", "通過"), ("無痕視窗", "看不到一般視窗資料", "通過"), ("另一裝置／瀏覽器", "不會自動同步", "通過")],
        "failure": "共用裝置上的下一位使用者可能看到尚未清除的結果；只寫「保存在本機」不足以說明這個風險。",
        "fix": "測驗、修復與隱私頁加入共用裝置提醒，並維持容易找到的清除控制。",
        "limitations": "瀏覽器擴充功能、備份軟體與裝置管理政策不在本站控制範圍；使用者仍應依自己的裝置風險決定是否保存。",
        "screenshot": "/assets/lovetypes/lab/local-storage-privacy-test.webp",
        "screenshot_alt": "LoveTypes 修復表的本機保存與清除控制測試畫面",
    },
    {
        "slug": "share-card-privacy-test",
        "title": "分享卡是否包含私人作答資料實測",
        "desc": "檢查分享文字、圖片與網址，只包含守護者摘要，不帶出逐題答案或本機修復內容。",
        "summary": "分享功能應讓使用者知道會離開裝置的是什麼。本次逐項檢查 Web Share、複製文字、故事卡圖片與分享網址，確認輸出只包含守護者名稱、愛之語摘要與公開頁連結，不附帶 15 題答案、百分比細節、修復表文字或 localStorage 值。",
        "environment": ["支援 Web Share 的行動版 Chromium", "不支援 Web Share 時的複製備援", "故事卡圖片直接開啟", "網址列與 query string 人工檢查"],
        "steps": ["完成測驗並在修復表輸入辨識用測試字串。", "依序觸發分享、複製與故事卡開啟。", "把輸出貼到純文字區，搜尋測試字串與逐題資料。", "檢查分享網址是否含結果參數或敏感欄位。"],
        "results": [("分享文字", "只有守護者摘要與公開網址", "通過"), ("複製備援", "未包含逐題答案及修復文字", "通過"), ("故事卡", "為預製角色圖片，不含本機資料", "通過"), ("分享網址", "沒有測驗分數或個人文字參數", "通過")],
        "failure": "使用者可能把守護者名稱誤認為完整作答紀錄已被公開，因此需要在操作附近說明分享範圍。",
        "fix": "分享區補上範圍提示，明確區分公開角色卡與只留在瀏覽器的個人內容。",
        "limitations": "分享完成後，接收平台如何儲存訊息由該平台決定；本站無法替外部通訊服務承諾刪除。",
        "screenshot": "/assets/lovetypes/lab/share-card-privacy-test.webp",
        "screenshot_alt": "LoveTypes 守護者分享控制與分享範圍提示測試畫面",
    },
    {
        "slug": "compatibility-safety-test",
        "title": "相容性工具避免命定式判斷實測",
        "desc": "用五組差異輸入檢查羅盤輸出，確認結果提供對話建議而非相配分數或關係預言。",
        "summary": "相容性羅盤容易被誤用為「適不適合」判決。本次以同類型、差異類型、未選完整、交換順序與高風險描述五組輸入測試，檢查結果是否保持對稱、能說明可能錯頻、提供可拒絕的小請求，且不輸出命定百分比。",
        "environment": ["正式繁中相容性工具", "桌面 1440×900 與手機 360×800", "五組固定守護者配對", "不輸入姓名、生日或聯絡資料"],
        "steps": ["選擇相同守護者，記錄共同優勢與盲點。", "選擇差異守護者並交換左右順序。", "只選一方時嘗試產生結果。", "檢查安全聲明、下一句請求與所有百分比文字。"],
        "results": [("相同類型", "同時顯示共同語言與可能忽略處", "通過"), ("交換順序", "核心建議一致，不產生高低排名", "通過"), ("未選完整", "要求完成選擇，不建立虛假結果", "通過"), ("命定語言", "沒有相配率、靈魂伴侶或分手預言", "通過")],
        "failure": "舊版頁面名稱容易讓人把「相容性」理解成命運評分，且商業報告按鈕過早出現。",
        "fix": "第一屏改以溝通羅盤定位，結果只提供錯頻翻譯與十分鐘對話；索引頁不提供購買或報告索取入口。",
        "limitations": "配對結果只由兩個自填入口組成，不考慮價值觀、權力、生活責任與安全，不能判斷關係是否適合繼續。",
        "screenshot": "/assets/lovetypes/lab/compatibility-safety-test.webp",
        "screenshot_alt": "LoveTypes 相容性羅盤顯示溝通建議與安全界線的桌面測試畫面",
    },
    {
        "slug": "repair-plan-usability-test",
        "title": "7 日修復表手機完成流程實測",
        "desc": "在窄螢幕逐欄完成、重新整理、返回與清除，檢查表單是否能在不登入下使用。",
        "summary": "這次測試把修復表當成真正工作工具，而不是展示頁。測試人員以手機寬度依序填入守護者、錯頻事件、小請求與補給選擇，關閉鍵盤、重新整理、離開再返回，並測試長文字、空白欄位與清除。",
        "environment": ["Chromium 360×800 與 390×844", "軟體鍵盤高度模擬", "一般與較長繁中文字串", "減少動態效果開啟與關閉"],
        "steps": ["從測驗結果進入 7 日修復表。", "逐欄輸入短句，再以 120 字長句測試。", "重新整理與返回頁面，確認保存提示。", "清除全部資料並以鍵盤重新走一次流程。"],
        "results": [("欄位寬度", "360px 下沒有水平捲動", "通過"), ("鍵盤操作", "標籤、焦點與按鈕順序可理解", "通過"), ("本機保存", "重新整理後仍在，清除後移除", "通過"), ("長文字", "容器增高，不遮住後續控制", "通過")],
        "failure": "若一次展示太多商品與角色連結，工作表完成後的下一步不明確。",
        "fix": "完成區優先提供下載／複製、免費指南與回顧日期；外部購買只經補給頁前往。",
        "limitations": "測試未涵蓋所有第三方鍵盤、螢幕閱讀器與舊版瀏覽器；資料也不跨裝置同步。",
        "screenshot": "/assets/lovetypes/lab/repair-plan-usability-test.webp",
        "screenshot_alt": "LoveTypes 7 日修復表在 360 像素手機畫面中的填寫測試",
    },
    {
        "slug": "keyboard-accessibility-test",
        "title": "鍵盤、焦點、對比與減少動態效果實測",
        "desc": "不用滑鼠走過主要導覽、測驗、羅盤與表單，記錄焦點順序、對比及動畫偏好。",
        "summary": "可見內容若無法被鍵盤或低視力使用者操作，就不算完整體驗。本次以 Tab、Shift+Tab、Enter、Space 與 Escape 走過首頁到結果流程，並執行對比與 reduced-motion 檢查。測試只聲明已覆蓋的路徑，不宣稱取得任何無障礙認證。",
        "environment": ["Chromium 鍵盤操作", "桌面與行動 viewport", "prefers-reduced-motion: reduce", "自動對比稽核與人工焦點觀察"],
        "steps": ["從頁首跳到主要內容，再逐項走過導覽。", "不用滑鼠完成測驗與相容性選擇。", "檢查 modal、details、表單與清除按鈕焦點。", "開啟減少動態效果，確認捲動與轉場不強制動畫。"],
        "results": [("跳至內容", "第一個鍵盤入口可見且可用", "通過"), ("焦點順序", "主要控制依閱讀順序移動", "通過"), ("色彩對比", "自動稽核沒有低於門檻項目", "通過"), ("減少動態", "平滑捲動與非必要動畫停用", "通過")],
        "failure": "先前視覺測試曾等待不存在的元素直到逾時，表示測試工具本身會掩蓋真正結果。",
        "fix": "缺少的可選元素改為短時間探測，完整視覺流程由約十二分鐘降至六分鐘內完成。",
        "limitations": "鍵盤與自動對比通過不等於所有輔助科技皆無障礙；VoiceOver、放大軟體與認知負荷仍需持續人工檢查。",
        "screenshot": "/assets/lovetypes/lab/keyboard-accessibility-test.webp",
        "screenshot_alt": "LoveTypes 導覽按鈕顯示清楚鍵盤焦點框的無障礙測試畫面",
    },
    {
        "slug": "slow-network-performance-test",
        "title": "慢速網路、圖片失敗與 JavaScript 關閉實測",
        "desc": "限制網速並停用部分資源，確認文章、信任資訊與主要路徑仍可閱讀。",
        "summary": "本次測試關心的是失敗時仍能得到什麼。測試人員以慢速網路載入首頁與文章，阻擋一張非關鍵圖片，最後關閉 JavaScript 重新開啟指南、關於與隱私頁。互動工具在無 JavaScript 時不能運作，但內容與替代路徑必須保持清楚。",
        "environment": ["Chromium 網路節流", "圖片請求阻擋一項", "JavaScript 完全停用", "桌面與 360px 手機視窗"],
        "steps": ["以慢速網路首次載入首頁與一篇指南。", "阻擋文章配圖，檢查替代文字與版面。", "停用 JavaScript 後開啟指南、關於、隱私。", "記錄工具區在無腳本時提供的說明或替代連結。"],
        "results": [("慢速載入", "主標、導覽與文章文字先於非關鍵圖片可讀", "通過"), ("圖片失敗", "固定尺寸避免版面跳動，替代文字存在", "通過"), ("無 JavaScript 文章", "完整文章與信任內容仍可閱讀", "通過"), ("無 JavaScript 工具", "不產生假結果，保留指南與聯絡路徑", "通過")],
        "failure": "互動頁若只顯示空容器，使用者可能誤以為網站損壞。",
        "fix": "工具容器保留靜態目的說明與可用的文章路徑；腳本只負責增強互動，不承載唯一的安全資訊。",
        "limitations": "測試使用模擬節流，不等於所有電信網路；第三方商店與外部服務的速度不在 LoveTypes 控制範圍。",
        "screenshot": "/assets/lovetypes/lab/slow-network-performance-test.webp",
        "screenshot_alt": "LoveTypes 指南在圖片未載入時仍保持文字與版面可讀的測試畫面",
    },
]


LAB_TEST_DETAILS = {
    "quiz-scoring-test": {
        "updated": "2026-08-01",
        "test_id": "LT-LAB-QZ-001",
        "fixture": "基準序列：W,T,G,S,P,W,T,G,S,P,W,T,G,S,P。人工預期 W=3、T=3、G=3、S=3、P=3；同分規則依 W→T→G→S→P 固定順序選 W。偏向序列：W,W,W,W,T,T,T,G,G,S,S,P,P,P,P，預期 W=4、P=4、T=3、G=2、S=2，同分仍選 W。",
        "raw_observation": "兩組序列均完成 15 次點擊。基準序列顯示五類各 20%，主要守護者為 Iris；偏向序列顯示 W 27%、P 27%、T 20%、G 13%、S 13%，四捨五入後合計 100%。重新整理三次均讀回相同 primaryKey 與 score 物件，未完成第 15 題時 localStorage 沒有 quiz-result 完成紀錄。",
        "method_detail": "測試前以清除控制與開發者工具各清一次保存鍵，避免前次結果影響。每次點擊後同步記錄題號與選項代碼，再由人工加總，不直接採用畫面百分比作為預期值。百分比以原始計數除以 15 後四捨五入，因此驗收同時核對原始分數與顯示值。測試只覆蓋目前繁中題庫與固定排序；題庫或計分函式修改時必須重跑。",
        "revision": "公開完整 15 題固定序列、人工預期分數、實際百分比與 localStorage 讀回結果。",
        "secondary_screenshot": "/assets/lovetypes/lab/quiz-scoring-test-detail.webp",
        "secondary_alt": "LoveTypes 五類原始分數與同分固定排序的桌面證據畫面",
    },
    "result-consistency-test": {
        "updated": "2026-08-01",
        "test_id": "LT-LAB-QZ-002",
        "fixture": "A 序列：W,W,W,W,T,T,T,G,G,G,S,S,P,P,P，預期 W=4、T=3、G=3、S=2、P=3。B 序列完全重複 A。C 序列只把第 8 題 G 改為 P，預期 W=4、P=4、T=3、G=2、S=2。每輪先清除保存鍵，避免讀回前一輪。",
        "raw_observation": "A 與 B 的五類原始分數、主要守護者、結果說明與分享文字一致。C 只改變 G 與 P 各一分，主要結果因 W/P 同分仍依固定順序保持 W；其他三類沒有漂移。360×800 與 1440×900 只改變版面排列，資料物件與文字順序一致。",
        "method_detail": "本報告把『程式在同一輸入下是否穩定』與『真人隔一段時間是否會答出相同結果』分開。前者可以由固定 fixture 重現，後者需要受試者設計、時間間隔與統計分析，本站沒有進行。當一題變更足以造成主要類別更換時，結果頁必須讓完整分數可見，並提醒這是當下偏好而非永久身份。",
        "revision": "加入 A/B/C 完整序列與單題變更前後的原始分數差異。",
        "secondary_screenshot": "/assets/lovetypes/lab/result-consistency-test-detail.webp",
        "secondary_alt": "LoveTypes 單題變更前後五類分數並列比較畫面",
    },
    "local-storage-privacy-test": {
        "updated": "2026-08-01",
        "test_id": "LT-LAB-PR-001",
        "fixture": "測驗 fixture 使用 W,T,G,S,P 重複三輪；修復表測試字串為 LT-LOCAL-ONLY-0731。檢查鍵包含 lovetypes:zh:quiz-result、頁面路徑版本的 quiz-result，以及 repair-plan 對應欄位。第二內容區與無痕視窗不先造訪本站。",
        "raw_observation": "一般視窗完成後重新整理仍可讀回結果與測試字串。依序按清除結果和清除工作表後，相關鍵不存在，頁面回到未填狀態。無痕視窗、第二瀏覽器內容區與另一個 Chrome profile 均未出現測試字串；Network 面板沒有發現把作答內容送往 LoveTypes API 的請求。",
        "method_detail": "localStorage 是來源相同且以瀏覽器內容區隔保存的用戶端儲存，不等於加密保險箱。共用同一個系統帳號與瀏覽器 profile 的下一位使用者可能看見尚未清除的內容；瀏覽器擴充功能、裝置管理或備份也可能有額外存取能力。因此頁面同時提供清除控制與共用裝置提醒，不宣稱資料絕對不會離開裝置。",
        "revision": "補上實際保存鍵、辨識字串、Network 觀察與共用 profile 風險。",
        "secondary_screenshot": "/assets/lovetypes/lab/local-storage-privacy-test-detail.webp",
        "secondary_alt": "LoveTypes 清除本機保存後欄位回到空白的證據畫面",
    },
    "share-card-privacy-test": {
        "updated": "2026-08-01",
        "test_id": "LT-LAB-PR-002",
        "fixture": "先完成偏向 Claire 的固定答案，並在修復表輸入辨識字串 LT-PRIVATE-ANSWER-0731。依序擷取 Web Share payload、複製備援純文字、預製故事卡網址與頁面 URL；搜尋辨識字串、questions、scores、repair 與 localStorage 鍵名。",
        "raw_observation": "分享標題包含 LoveTypes 與 Claire，本文包含守護者摘要及公開角色頁 URL。四種輸出都沒有逐題答案、五類分數、修復字串或 localStorage 值；網址沒有 query/hash 個人參數。故事卡是部署前產生的固定 WebP，同一角色的使用者取得相同檔案。",
        "method_detail": "測試在真正送到外部平台前攔截並檢查網站準備的 payload，因為訊息送出後的保存、轉傳與刪除由接收平台控制。即使分享卡不含逐題內容，守護者名稱本身仍可能是使用者不想公開的資訊，所以介面要在按鈕附近說明範圍，且不得預設自動分享。",
        "revision": "公開辨識字串、輸出搜尋條件與 Web Share／複製／圖片／URL 四路結果。",
        "secondary_screenshot": "/assets/lovetypes/lab/share-card-privacy-test-detail.webp",
        "secondary_alt": "LoveTypes 分享前提示與純文字 payload 的核對畫面",
    },
    "compatibility-safety-test": {
        "updated": "2026-08-01",
        "test_id": "LT-LAB-CP-001",
        "fixture": "固定組合為 W×W、W×T、T×W、G×S、P×W，關係狀態依序選交往中、遠距、衝突後、同住與尚未定義。逐一搜尋相配率、百分比、命定伴侶、關係預言、分手判決、出生推算及保證等字詞。",
        "raw_observation": "所有完整輸入都產生共同理解、可能錯頻、可說句子與今日行動，不輸出相配分數或未來預言。W×T 與 T×W 的角色描述隨位置交換，但核心差異與安全提醒一致。未選完整時按鈕不產生結果。頁面未要求姓名、生日、出生時間或聯絡資料，也沒有購買或報告索取 CTA。",
        "method_detail": "羅盤只組合兩個自填接收入口與當下情境，無法評估價值觀、權力、責任分配或安全。測試重點是防止輸出越過這個資料能力：不以角色差異推論適合程度，不把同類型說成最佳配對，也不把任何結果包裝成命理。安全關鍵字檢查與人工閱讀都必須通過。",
        "revision": "移除商業與出生推算入口，加入五組固定配對、交換順序及禁用語逐字檢查。",
        "secondary_screenshot": "/assets/lovetypes/lab/compatibility-safety-test-detail.webp",
        "secondary_alt": "LoveTypes 關係羅盤僅顯示對話建議而沒有相配分數的結果畫面",
    },
    "repair-plan-usability-test": {
        "updated": "2026-08-01",
        "test_id": "LT-LAB-UX-001",
        "fixture": "360×800 與 390×844 各走一次。短字串依序填 Iris、昨晚訊息被略過、希望今晚有十分鐘專心聽、週日回看；長字串以 120 個繁中文字填入每個 textarea。使用 Tab、Shift+Tab、Enter 與觸控各完成一次。",
        "raw_observation": "兩個寬度均無水平溢出，長文字使欄位垂直增高且不遮住下一個標籤。重新整理後四欄仍在，清除後全部回空白。鍵盤焦點依 DOM 閱讀順序移動，固定按鈕沒有蓋住目前欄位；開啟 reduced-motion 後未出現強制平滑捲動。",
        "method_detail": "本測試記錄完成一張工作表所需的互動，不把表單存在視為使用者真的完成關係修復。手機軟體鍵盤以 Chromium viewport 模擬，無法涵蓋所有第三方鍵盤；因此仍保留內容可見、標籤明確與欄位可自然增高等不依賴特定鍵盤的防護。完成後只提供複製、免費指南與回看日期。",
        "revision": "加入固定欄位內容、120 字壓力輸入、鍵盤路徑與兩種手機尺寸觀察。",
        "secondary_screenshot": "/assets/lovetypes/lab/repair-plan-usability-test-detail.webp",
        "secondary_alt": "LoveTypes 7 日修復表填入長文字後仍不遮擋控制的手機畫面",
    },
    "keyboard-accessibility-test": {
        "updated": "2026-08-01",
        "test_id": "LT-LAB-A11Y-001",
        "fixture": "從網址列開始，依序使用 Tab 到跳至內容、主導覽、測驗選項、羅盤選擇與清除控制；反向以 Shift+Tab 返回。對比以 WCAG AA 一般文字 4.5:1、大字 3:1 為門檻；動畫測試設定 prefers-reduced-motion: reduce。",
        "raw_observation": "跳至內容在取得焦點時可見並正確移到 main。所有原生按鈕、連結、select 與 details 都能以鍵盤操作，焦點框沒有被 overflow 裁切。自動掃描未發現門檻以下的文字對比；reduced-motion 下平滑捲動與裝飾轉場停用。未發現鍵盤陷阱或焦點跳回頁首。",
        "method_detail": "自動對比與鍵盤巡覽只能發現部分問題，不能代表取得無障礙認證。報告不聲稱已涵蓋 VoiceOver、語音控制、放大軟體、切換控制或所有認知需求。每次導覽、modal 或互動元件改版後，焦點順序與可見性都必須重測；可選元素不存在時測試應明確跳過，不以長時間等待掩蓋失敗。",
        "revision": "公開按鍵序列、對比門檻、reduced-motion 條件與未涵蓋輔助科技。",
        "secondary_screenshot": "/assets/lovetypes/lab/keyboard-accessibility-test-detail.webp",
        "secondary_alt": "LoveTypes 跳至內容連結與鍵盤焦點框的近距離證據畫面",
    },
    "slow-network-performance-test": {
        "updated": "2026-08-01",
        "test_id": "LT-LAB-PF-001",
        "fixture": "桌面與 360×800 使用 Fast 3G 模擬：下載 1.6 Mbps、上傳 750 Kbps、延遲 150 ms。阻擋 guide-toolkit-og.jpg 與一張守護者 WebP，再完全停用 JavaScript開啟首頁、指南、About、Privacy 與 Compass。",
        "raw_observation": "指南標題、前言與正文在非關鍵圖片完成前可讀；阻擋圖片後保留固定寬高與 alt，沒有大幅版面跳動。關閉 JavaScript 時指南、來源、作者、修訂、About 與隱私完整可讀。Compass 保留用途、安全限制與免費閱讀路徑，但不偽造互動結果；首頁測驗控制不運作且未顯示已完成狀態。",
        "method_detail": "節流是可重現的工程模擬，不等於台灣所有行動網路。驗收關心失敗時的最低可用內容：文字和信任資訊由 HTML 提供、圖片有尺寸和替代文字、互動工具在腳本失效時不產生假結果。第三方商店不在索引面，也不納入本站速度結論。後續若新增必要 JavaScript，需重新檢查無腳本狀態。",
        "revision": "加入明確節流數值、被阻擋資產、無腳本頁面清單與最低可用內容判準。",
        "secondary_screenshot": "/assets/lovetypes/lab/slow-network-performance-test-detail.webp",
        "secondary_alt": "LoveTypes 關閉 JavaScript 後指南來源與安全文字仍可閱讀的畫面",
    },
}


LAB_ACCEPTANCE = {
    "quiz-scoring-test": (
        "驗收條件是每次完成恰好記入 15 分、人工加總與畫面原始分數一致、百分比合計在四捨五入規則下為 100%，以及同分輸入在重新整理後仍選擇同一主要類別。任何漏題、多計、負分、非固定同分或完成前寫入結果都算失敗。",
        "修正後先重跑兩組公開序列，再加入全選同一類、最後一題才形成同分及中途返回三個邊界案例。每個案例保存實際 score 物件與畫面，不只看角色圖片。題庫、選項代碼、排序表或百分比函式任一變更，都使本報告失效並要求新 build 重測。",
    ),
    "result-consistency-test": (
        "驗收條件是完全相同輸入得到完全相同資料，單題變更只影響原類別與新類別，viewport 改變不修改排序。若重複輸入產生不同 primaryKey、未變動類別分數漂移，或版面寬度影響資料，就不能標示通過。",
        "重測會先保存 A 輪原始 JSON，再清除並輸入 B，不沿用前次 DOM。C 輪逐欄比較差異，只允許 G 減一、P 加一。最後以桌面與手機各重載三次。這仍不是重測信度研究；若要回答真人穩定性，必須另做有受試者、間隔與倫理設計的研究。",
    ),
    "local-storage-privacy-test": (
        "驗收條件是一般視窗可以依產品承諾保存與清除、無痕和獨立內容區不自動取得資料、清除後 DOM 與保存鍵都沒有辨識字串。只清空畫面但鍵仍存在，或任何作答內容出現在本站網路請求中，都視為隱私失敗。",
        "重測先用唯一辨識字串避免誤判，再同時檢查 Application 與 Network。清除後重新整理兩次，搜尋頁面來源、localStorage、sessionStorage、Cookie 與請求內容。瀏覽器政策可能改變儲存行為，因此 Chrome 主版本更新、保存鍵改名或新增分析服務時，都要重新核對並更新隱私說明。",
    ),
    "share-card-privacy-test": (
        "驗收條件是四條分享路徑只輸出公開守護者摘要與公開網址，且使用者必須主動觸發。逐題答案、五類分數、修復文字、辨識字串、保存鍵、姓名或聯絡資料任一出現即失敗；網址帶有可還原個人結果的參數也算失敗。",
        "修正後以另一位守護者和新的辨識字串重跑，避免測試只對單一卡片成立。Web Share 不可用時要檢查複製備援，不得因 API 缺失改成自動下載或自動導頁。外部平台接收後的保存不由本站控制，因此界面仍要讓使用者在送出前看到分享範圍與取消空間。",
    ),
    "compatibility-safety-test": (
        "驗收條件是所有配對只提供描述、翻譯與可拒絕的小請求，不出現排名、機率、命定結論、出生推算或關係去留指令。交換左右順序時可以改變稱呼，但不能把同一差異變成一方優越；未完成輸入不得產生看似個人化的結果。",
        "每次文案或配對資料更新後，先重跑五組固定組合，再以禁用詞清單掃描 HTML、JavaScript 與實際結果。人工閱讀要確認安全聲明沒有被折疊或放在付費 CTA 後面。若未來新增更多情境，也只能擴充溝通選項，不能把缺少的價值觀、責任或安全資料推算出來。",
    ),
    "repair-plan-usability-test": (
        "驗收條件是兩種手機寬度無水平捲動，標籤與欄位關係清楚，長文字不遮擋控制，鍵盤能依閱讀順序完成，保存與清除結果一致。固定按鈕蓋住目前輸入、清除後資料仍在、重新整理丟失未提示，或完成後只剩商品入口都算失敗。",
        "重測會從空白狀態開始，以短字串完成一次，再以 120 字壓力輸入完成一次；兩輪都執行重新整理、返回與清除。觸控與鍵盤路徑分開記錄，避免一條可用掩蓋另一條中斷。若欄位、固定導覽、保存鍵或完成區改版，這份流程必須全程重跑。",
    ),
    "keyboard-accessibility-test": (
        "驗收條件是所有主要命令可由鍵盤到達與啟動、焦點始終可見、順序符合閱讀流程、沒有陷阱，文字對比達到所列門檻，減少動態偏好能停用非必要動畫。只有滑鼠可用、焦點被遮住或自動工具無法完成掃描都不能以人工印象判定通過。",
        "重測先清除滑鼠操作痕跡，從網址列依序記錄焦點元素與動作，再反向返回。自動結果保存違規節點與實際色值，人工檢查 sticky 元件、details 與動態插入結果。VoiceOver 尚未列入本次結論，因此頁面不得使用『完全無障礙』或認證字樣；後續應另建立螢幕閱讀器紀錄。",
    ),
    "slow-network-performance-test": (
        "驗收條件是在指定節流下先取得標題與正文、圖片失敗不造成不可閱讀的位移、關閉 JavaScript 後文章與信任內容完整存在，互動工具不顯示假結果。空白主區、只有載入動畫、安全聲明依賴腳本或圖片失敗後文字互相覆蓋都算失敗。",
        "重測分三輪進行：清快取的慢速首次載入、精確阻擋兩個圖片 URL、建立停用 JavaScript 的新內容區。每輪保存 console、失敗請求與畫面，不能沿用已快取資產。首頁與工具可在無腳本時降低功能，但必須解釋限制並提供可閱讀路徑；新增第三方腳本後要再次確認正文不被阻塞。",
    ),
}


LAB_EVIDENCE_SCOPE = {
    "quiz-scoring-test": "證據保存包含兩組固定序列的結果畫面、五類 score 讀值與未完成狀態。報告只對標示 build 有效，不把畫面綠燈延伸成題目品質結論。",
    "result-consistency-test": "證據保存包含 A/B 完全重複比較及 C 單題差異。比較基準是原始資料與實際文案，不以角色主圖看起來相同代替資料核對。",
    "local-storage-privacy-test": "證據保存包含清除前後畫面與保存鍵狀態；公開截圖使用測試字串，不含真人作答、姓名、聯絡方式或裝置識別資訊。",
    "share-card-privacy-test": "證據保存包含分享範圍提示與攔截後純文字；不公開外部通訊帳號畫面，也不以平台成功接收作為本站隱私判準。",
    "compatibility-safety-test": "證據保存包含交換順序前後結果及禁用語掃描。通過僅表示目前輸出沒有越權判斷，不表示配對建議適合所有文化與關係。",
    "repair-plan-usability-test": "證據保存包含短輸入、長輸入與清除後狀態。所有文字均為工程 fixture，不代表真人衝突，也不據此宣稱工作表能改善關係。",
    "keyboard-accessibility-test": "證據保存包含焦點框、跳至內容與自動檢查摘要。未測輔助科技會明列限制，不以單一工具零錯誤替代人工操作。",
    "slow-network-performance-test": "證據保存包含資產失敗與無腳本畫面，並記錄被阻擋 URL。模擬數據不對外推估真實訪客速度或 Core Web Vitals。",
}

LAB_EVIDENCE_SCOPE["result-consistency-test"] += " 所有比較都保留題序，方便下一次逐題重放。"
LAB_EVIDENCE_SCOPE["share-card-privacy-test"] += " 每條輸出另存雜湊與測試時間，方便確認是否為同一 build。"
LAB_EVIDENCE_SCOPE["repair-plan-usability-test"] += " 截圖同時保留 viewport 與測試字串，避免把桌面畫面誤標為手機。"
LAB_EVIDENCE_SCOPE["repair-plan-usability-test"] += " 清除後畫面另存一張，確認不是只清掉可見文字。"
LAB_EVIDENCE_SCOPE["keyboard-accessibility-test"] += " 焦點順序另以文字清單保存，截圖只作視覺佐證。"


for _report in LAB_REPORTS:
    _report.update(LAB_TEST_DETAILS[_report["slug"]])
    _report["acceptance"], _report["retest"] = LAB_ACCEPTANCE[_report["slug"]]
    _report["evidence_scope"] = LAB_EVIDENCE_SCOPE[_report["slug"]]
    _report["environment"] = [
        "macOS 26.5.2；Google Chrome 150.0.7871.187",
        "桌面 1440×900；手機 360×800（個別報告另列額外尺寸）",
        "Build 49b06986d371；時區 Asia/Taipei (UTC+8)",
        *_report["environment"],
    ]
