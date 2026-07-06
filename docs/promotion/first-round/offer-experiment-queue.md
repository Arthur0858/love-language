# LoveTypes 商品實驗執行佇列

- 產生日期：2026-07-06
- ready rows：0
- waiting rows：0
- blocked rows：80
- 規則：只有 offer experiment plan 無 blocker 且實驗列為 READY 時，queue row 才可進入 ready；其餘維持 waiting 或 blocked。
- 步驟：brief, asset, qa, measure

## 阻擋條件

- 已回填 KPI，但目前所有關鍵訊號皆為 0；維持 collect_signal，不調整商品、守護者優先序或內容放大。

## 執行佇列

### iris-identity_save-brief

- 狀態：blocked_by_gate
- 守護者：艾莉絲（iris）
- 實驗：identity_save
- 步驟：brief / owner: content
- 交付物：Write a one-page asset brief with guardian, scene, promise boundary, and CTA.
- 驗收：Brief keeps the Shorts CTA as quiz and places offer only after result route.
- 回填：Update offer-experiment-plan after KPI review.
- 資產：`iris-free_story_card_upgrade` -> https://lovetypes.tw/keepsakes/#keepsake-iris

### iris-identity_save-asset

- 狀態：blocked_by_gate
- 守護者：艾莉絲（iris）
- 實驗：identity_save
- 步驟：asset / owner: creative
- 交付物：Produce the smallest useful asset or route copy for the experiment.
- 驗收：Asset links to the existing target URL and does not claim diagnosis or therapeutic outcome.
- 回填：Record fulfillment asset in lead-intake-tracker.csv when a real request exists.
- 資產：`iris-free_story_card_upgrade` -> https://lovetypes.tw/keepsakes/#keepsake-iris

### iris-identity_save-qa

- 狀態：blocked_by_gate
- 守護者：艾莉絲（iris）
- 實驗：identity_save
- 步驟：qa / owner: ops
- 交付物：Check safety copy, route, tracking event, and mobile presentation before publish.
- 驗收：Public smoke remains clean and no paid CTA is added before the experiment is READY.
- 回填：Run predeploy_check.py before deploy.
- 資產：`iris-free_story_card_upgrade` -> https://lovetypes.tw/keepsakes/#keepsake-iris

### iris-identity_save-measure

- 狀態：blocked_by_gate
- 守護者：艾莉絲（iris）
- 實驗：identity_save
- 步驟：measure / owner: ops
- 交付物：After the test window, backfill KPI fields and decide continue, revise, or stop.
- 驗收：KPI row includes primary and secondary metric fields for the experiment.
- 回填：Update kpi-tracker.csv, weekly-summary, decision gate, offer board, and experiment plan.
- 資產：`iris-free_story_card_upgrade` -> https://lovetypes.tw/keepsakes/#keepsake-iris

### iris-owned_lead-brief

- 狀態：blocked_by_gate
- 守護者：艾莉絲（iris）
- 實驗：owned_lead
- 步驟：brief / owner: content
- 交付物：Write a one-page asset brief with guardian, scene, promise boundary, and CTA.
- 驗收：Brief keeps the Shorts CTA as quiz and places offer only after result route.
- 回填：Update offer-experiment-plan after KPI review.
- 資產：`iris-email_lead_template` -> https://lovetypes.tw/contact/#luna-supply-request

### iris-owned_lead-asset

- 狀態：blocked_by_gate
- 守護者：艾莉絲（iris）
- 實驗：owned_lead
- 步驟：asset / owner: creative
- 交付物：Produce the smallest useful asset or route copy for the experiment.
- 驗收：Asset links to the existing target URL and does not claim diagnosis or therapeutic outcome.
- 回填：Record fulfillment asset in lead-intake-tracker.csv when a real request exists.
- 資產：`iris-email_lead_template` -> https://lovetypes.tw/contact/#luna-supply-request

### iris-owned_lead-qa

- 狀態：blocked_by_gate
- 守護者：艾莉絲（iris）
- 實驗：owned_lead
- 步驟：qa / owner: ops
- 交付物：Check safety copy, route, tracking event, and mobile presentation before publish.
- 驗收：Public smoke remains clean and no paid CTA is added before the experiment is READY.
- 回填：Run predeploy_check.py before deploy.
- 資產：`iris-email_lead_template` -> https://lovetypes.tw/contact/#luna-supply-request

### iris-owned_lead-measure

- 狀態：blocked_by_gate
- 守護者：艾莉絲（iris）
- 實驗：owned_lead
- 步驟：measure / owner: ops
- 交付物：After the test window, backfill KPI fields and decide continue, revise, or stop.
- 驗收：KPI row includes primary and secondary metric fields for the experiment.
- 回填：Update kpi-tracker.csv, weekly-summary, decision gate, offer board, and experiment plan.
- 資產：`iris-email_lead_template` -> https://lovetypes.tw/contact/#luna-supply-request

### iris-luna_soft_offer-brief

- 狀態：blocked_by_gate
- 守護者：艾莉絲（iris）
- 實驗：luna_soft_offer
- 步驟：brief / owner: content
- 交付物：Write a one-page asset brief with guardian, scene, promise boundary, and CTA.
- 驗收：Brief keeps the Shorts CTA as quiz and places offer only after result route.
- 回填：Update offer-experiment-plan after KPI review.
- 資產：`iris-luna_scene_cta` -> https://lovetypes.tw/luna-yoga-music/#luna-iris

### iris-luna_soft_offer-asset

- 狀態：blocked_by_gate
- 守護者：艾莉絲（iris）
- 實驗：luna_soft_offer
- 步驟：asset / owner: creative
- 交付物：Produce the smallest useful asset or route copy for the experiment.
- 驗收：Asset links to the existing target URL and does not claim diagnosis or therapeutic outcome.
- 回填：Record fulfillment asset in lead-intake-tracker.csv when a real request exists.
- 資產：`iris-luna_scene_cta` -> https://lovetypes.tw/luna-yoga-music/#luna-iris

### iris-luna_soft_offer-qa

- 狀態：blocked_by_gate
- 守護者：艾莉絲（iris）
- 實驗：luna_soft_offer
- 步驟：qa / owner: ops
- 交付物：Check safety copy, route, tracking event, and mobile presentation before publish.
- 驗收：Public smoke remains clean and no paid CTA is added before the experiment is READY.
- 回填：Run predeploy_check.py before deploy.
- 資產：`iris-luna_scene_cta` -> https://lovetypes.tw/luna-yoga-music/#luna-iris

### iris-luna_soft_offer-measure

- 狀態：blocked_by_gate
- 守護者：艾莉絲（iris）
- 實驗：luna_soft_offer
- 步驟：measure / owner: ops
- 交付物：After the test window, backfill KPI fields and decide continue, revise, or stop.
- 驗收：KPI row includes primary and secondary metric fields for the experiment.
- 回填：Update kpi-tracker.csv, weekly-summary, decision gate, offer board, and experiment plan.
- 資產：`iris-luna_scene_cta` -> https://lovetypes.tw/luna-yoga-music/#luna-iris

### iris-affiliate_book-brief

- 狀態：blocked_by_gate
- 守護者：艾莉絲（iris）
- 實驗：affiliate_book
- 步驟：brief / owner: content
- 交付物：Write a one-page asset brief with guardian, scene, promise boundary, and CTA.
- 驗收：Brief keeps the Shorts CTA as quiz and places offer only after result route.
- 回填：Update offer-experiment-plan after KPI review.
- 資產：`iris-affiliate_book_bundle` -> https://lovetypes.tw/resources/#supply-iris

### iris-affiliate_book-asset

- 狀態：blocked_by_gate
- 守護者：艾莉絲（iris）
- 實驗：affiliate_book
- 步驟：asset / owner: creative
- 交付物：Produce the smallest useful asset or route copy for the experiment.
- 驗收：Asset links to the existing target URL and does not claim diagnosis or therapeutic outcome.
- 回填：Record fulfillment asset in lead-intake-tracker.csv when a real request exists.
- 資產：`iris-affiliate_book_bundle` -> https://lovetypes.tw/resources/#supply-iris

### iris-affiliate_book-qa

- 狀態：blocked_by_gate
- 守護者：艾莉絲（iris）
- 實驗：affiliate_book
- 步驟：qa / owner: ops
- 交付物：Check safety copy, route, tracking event, and mobile presentation before publish.
- 驗收：Public smoke remains clean and no paid CTA is added before the experiment is READY.
- 回填：Run predeploy_check.py before deploy.
- 資產：`iris-affiliate_book_bundle` -> https://lovetypes.tw/resources/#supply-iris

### iris-affiliate_book-measure

- 狀態：blocked_by_gate
- 守護者：艾莉絲（iris）
- 實驗：affiliate_book
- 步驟：measure / owner: ops
- 交付物：After the test window, backfill KPI fields and decide continue, revise, or stop.
- 驗收：KPI row includes primary and secondary metric fields for the experiment.
- 回填：Update kpi-tracker.csv, weekly-summary, decision gate, offer board, and experiment plan.
- 資產：`iris-affiliate_book_bundle` -> https://lovetypes.tw/resources/#supply-iris

### noah-identity_save-brief

- 狀態：blocked_by_gate
- 守護者：諾雅（noah）
- 實驗：identity_save
- 步驟：brief / owner: content
- 交付物：Write a one-page asset brief with guardian, scene, promise boundary, and CTA.
- 驗收：Brief keeps the Shorts CTA as quiz and places offer only after result route.
- 回填：Update offer-experiment-plan after KPI review.
- 資產：`noah-free_story_card_upgrade` -> https://lovetypes.tw/keepsakes/#keepsake-noah

### noah-identity_save-asset

- 狀態：blocked_by_gate
- 守護者：諾雅（noah）
- 實驗：identity_save
- 步驟：asset / owner: creative
- 交付物：Produce the smallest useful asset or route copy for the experiment.
- 驗收：Asset links to the existing target URL and does not claim diagnosis or therapeutic outcome.
- 回填：Record fulfillment asset in lead-intake-tracker.csv when a real request exists.
- 資產：`noah-free_story_card_upgrade` -> https://lovetypes.tw/keepsakes/#keepsake-noah

### noah-identity_save-qa

- 狀態：blocked_by_gate
- 守護者：諾雅（noah）
- 實驗：identity_save
- 步驟：qa / owner: ops
- 交付物：Check safety copy, route, tracking event, and mobile presentation before publish.
- 驗收：Public smoke remains clean and no paid CTA is added before the experiment is READY.
- 回填：Run predeploy_check.py before deploy.
- 資產：`noah-free_story_card_upgrade` -> https://lovetypes.tw/keepsakes/#keepsake-noah

### noah-identity_save-measure

- 狀態：blocked_by_gate
- 守護者：諾雅（noah）
- 實驗：identity_save
- 步驟：measure / owner: ops
- 交付物：After the test window, backfill KPI fields and decide continue, revise, or stop.
- 驗收：KPI row includes primary and secondary metric fields for the experiment.
- 回填：Update kpi-tracker.csv, weekly-summary, decision gate, offer board, and experiment plan.
- 資產：`noah-free_story_card_upgrade` -> https://lovetypes.tw/keepsakes/#keepsake-noah

### noah-owned_lead-brief

- 狀態：blocked_by_gate
- 守護者：諾雅（noah）
- 實驗：owned_lead
- 步驟：brief / owner: content
- 交付物：Write a one-page asset brief with guardian, scene, promise boundary, and CTA.
- 驗收：Brief keeps the Shorts CTA as quiz and places offer only after result route.
- 回填：Update offer-experiment-plan after KPI review.
- 資產：`noah-email_lead_template` -> https://lovetypes.tw/contact/#luna-supply-request

### noah-owned_lead-asset

- 狀態：blocked_by_gate
- 守護者：諾雅（noah）
- 實驗：owned_lead
- 步驟：asset / owner: creative
- 交付物：Produce the smallest useful asset or route copy for the experiment.
- 驗收：Asset links to the existing target URL and does not claim diagnosis or therapeutic outcome.
- 回填：Record fulfillment asset in lead-intake-tracker.csv when a real request exists.
- 資產：`noah-email_lead_template` -> https://lovetypes.tw/contact/#luna-supply-request

### noah-owned_lead-qa

- 狀態：blocked_by_gate
- 守護者：諾雅（noah）
- 實驗：owned_lead
- 步驟：qa / owner: ops
- 交付物：Check safety copy, route, tracking event, and mobile presentation before publish.
- 驗收：Public smoke remains clean and no paid CTA is added before the experiment is READY.
- 回填：Run predeploy_check.py before deploy.
- 資產：`noah-email_lead_template` -> https://lovetypes.tw/contact/#luna-supply-request

### noah-owned_lead-measure

- 狀態：blocked_by_gate
- 守護者：諾雅（noah）
- 實驗：owned_lead
- 步驟：measure / owner: ops
- 交付物：After the test window, backfill KPI fields and decide continue, revise, or stop.
- 驗收：KPI row includes primary and secondary metric fields for the experiment.
- 回填：Update kpi-tracker.csv, weekly-summary, decision gate, offer board, and experiment plan.
- 資產：`noah-email_lead_template` -> https://lovetypes.tw/contact/#luna-supply-request

### noah-luna_soft_offer-brief

- 狀態：blocked_by_gate
- 守護者：諾雅（noah）
- 實驗：luna_soft_offer
- 步驟：brief / owner: content
- 交付物：Write a one-page asset brief with guardian, scene, promise boundary, and CTA.
- 驗收：Brief keeps the Shorts CTA as quiz and places offer only after result route.
- 回填：Update offer-experiment-plan after KPI review.
- 資產：`noah-luna_scene_cta` -> https://lovetypes.tw/luna-yoga-music/#luna-noah

### noah-luna_soft_offer-asset

- 狀態：blocked_by_gate
- 守護者：諾雅（noah）
- 實驗：luna_soft_offer
- 步驟：asset / owner: creative
- 交付物：Produce the smallest useful asset or route copy for the experiment.
- 驗收：Asset links to the existing target URL and does not claim diagnosis or therapeutic outcome.
- 回填：Record fulfillment asset in lead-intake-tracker.csv when a real request exists.
- 資產：`noah-luna_scene_cta` -> https://lovetypes.tw/luna-yoga-music/#luna-noah

### noah-luna_soft_offer-qa

- 狀態：blocked_by_gate
- 守護者：諾雅（noah）
- 實驗：luna_soft_offer
- 步驟：qa / owner: ops
- 交付物：Check safety copy, route, tracking event, and mobile presentation before publish.
- 驗收：Public smoke remains clean and no paid CTA is added before the experiment is READY.
- 回填：Run predeploy_check.py before deploy.
- 資產：`noah-luna_scene_cta` -> https://lovetypes.tw/luna-yoga-music/#luna-noah

### noah-luna_soft_offer-measure

- 狀態：blocked_by_gate
- 守護者：諾雅（noah）
- 實驗：luna_soft_offer
- 步驟：measure / owner: ops
- 交付物：After the test window, backfill KPI fields and decide continue, revise, or stop.
- 驗收：KPI row includes primary and secondary metric fields for the experiment.
- 回填：Update kpi-tracker.csv, weekly-summary, decision gate, offer board, and experiment plan.
- 資產：`noah-luna_scene_cta` -> https://lovetypes.tw/luna-yoga-music/#luna-noah

### noah-affiliate_book-brief

- 狀態：blocked_by_gate
- 守護者：諾雅（noah）
- 實驗：affiliate_book
- 步驟：brief / owner: content
- 交付物：Write a one-page asset brief with guardian, scene, promise boundary, and CTA.
- 驗收：Brief keeps the Shorts CTA as quiz and places offer only after result route.
- 回填：Update offer-experiment-plan after KPI review.
- 資產：`noah-affiliate_book_bundle` -> https://lovetypes.tw/resources/#supply-noah

### noah-affiliate_book-asset

- 狀態：blocked_by_gate
- 守護者：諾雅（noah）
- 實驗：affiliate_book
- 步驟：asset / owner: creative
- 交付物：Produce the smallest useful asset or route copy for the experiment.
- 驗收：Asset links to the existing target URL and does not claim diagnosis or therapeutic outcome.
- 回填：Record fulfillment asset in lead-intake-tracker.csv when a real request exists.
- 資產：`noah-affiliate_book_bundle` -> https://lovetypes.tw/resources/#supply-noah

### noah-affiliate_book-qa

- 狀態：blocked_by_gate
- 守護者：諾雅（noah）
- 實驗：affiliate_book
- 步驟：qa / owner: ops
- 交付物：Check safety copy, route, tracking event, and mobile presentation before publish.
- 驗收：Public smoke remains clean and no paid CTA is added before the experiment is READY.
- 回填：Run predeploy_check.py before deploy.
- 資產：`noah-affiliate_book_bundle` -> https://lovetypes.tw/resources/#supply-noah

### noah-affiliate_book-measure

- 狀態：blocked_by_gate
- 守護者：諾雅（noah）
- 實驗：affiliate_book
- 步驟：measure / owner: ops
- 交付物：After the test window, backfill KPI fields and decide continue, revise, or stop.
- 驗收：KPI row includes primary and secondary metric fields for the experiment.
- 回填：Update kpi-tracker.csv, weekly-summary, decision gate, offer board, and experiment plan.
- 資產：`noah-affiliate_book_bundle` -> https://lovetypes.tw/resources/#supply-noah

### vivian-identity_save-brief

- 狀態：blocked_by_gate
- 守護者：薇薇安（vivian）
- 實驗：identity_save
- 步驟：brief / owner: content
- 交付物：Write a one-page asset brief with guardian, scene, promise boundary, and CTA.
- 驗收：Brief keeps the Shorts CTA as quiz and places offer only after result route.
- 回填：Update offer-experiment-plan after KPI review.
- 資產：`vivian-free_story_card_upgrade` -> https://lovetypes.tw/keepsakes/#keepsake-vivian

### vivian-identity_save-asset

- 狀態：blocked_by_gate
- 守護者：薇薇安（vivian）
- 實驗：identity_save
- 步驟：asset / owner: creative
- 交付物：Produce the smallest useful asset or route copy for the experiment.
- 驗收：Asset links to the existing target URL and does not claim diagnosis or therapeutic outcome.
- 回填：Record fulfillment asset in lead-intake-tracker.csv when a real request exists.
- 資產：`vivian-free_story_card_upgrade` -> https://lovetypes.tw/keepsakes/#keepsake-vivian

### vivian-identity_save-qa

- 狀態：blocked_by_gate
- 守護者：薇薇安（vivian）
- 實驗：identity_save
- 步驟：qa / owner: ops
- 交付物：Check safety copy, route, tracking event, and mobile presentation before publish.
- 驗收：Public smoke remains clean and no paid CTA is added before the experiment is READY.
- 回填：Run predeploy_check.py before deploy.
- 資產：`vivian-free_story_card_upgrade` -> https://lovetypes.tw/keepsakes/#keepsake-vivian

### vivian-identity_save-measure

- 狀態：blocked_by_gate
- 守護者：薇薇安（vivian）
- 實驗：identity_save
- 步驟：measure / owner: ops
- 交付物：After the test window, backfill KPI fields and decide continue, revise, or stop.
- 驗收：KPI row includes primary and secondary metric fields for the experiment.
- 回填：Update kpi-tracker.csv, weekly-summary, decision gate, offer board, and experiment plan.
- 資產：`vivian-free_story_card_upgrade` -> https://lovetypes.tw/keepsakes/#keepsake-vivian

### vivian-owned_lead-brief

- 狀態：blocked_by_gate
- 守護者：薇薇安（vivian）
- 實驗：owned_lead
- 步驟：brief / owner: content
- 交付物：Write a one-page asset brief with guardian, scene, promise boundary, and CTA.
- 驗收：Brief keeps the Shorts CTA as quiz and places offer only after result route.
- 回填：Update offer-experiment-plan after KPI review.
- 資產：`vivian-email_lead_template` -> https://lovetypes.tw/contact/#luna-supply-request

### vivian-owned_lead-asset

- 狀態：blocked_by_gate
- 守護者：薇薇安（vivian）
- 實驗：owned_lead
- 步驟：asset / owner: creative
- 交付物：Produce the smallest useful asset or route copy for the experiment.
- 驗收：Asset links to the existing target URL and does not claim diagnosis or therapeutic outcome.
- 回填：Record fulfillment asset in lead-intake-tracker.csv when a real request exists.
- 資產：`vivian-email_lead_template` -> https://lovetypes.tw/contact/#luna-supply-request

### vivian-owned_lead-qa

- 狀態：blocked_by_gate
- 守護者：薇薇安（vivian）
- 實驗：owned_lead
- 步驟：qa / owner: ops
- 交付物：Check safety copy, route, tracking event, and mobile presentation before publish.
- 驗收：Public smoke remains clean and no paid CTA is added before the experiment is READY.
- 回填：Run predeploy_check.py before deploy.
- 資產：`vivian-email_lead_template` -> https://lovetypes.tw/contact/#luna-supply-request

### vivian-owned_lead-measure

- 狀態：blocked_by_gate
- 守護者：薇薇安（vivian）
- 實驗：owned_lead
- 步驟：measure / owner: ops
- 交付物：After the test window, backfill KPI fields and decide continue, revise, or stop.
- 驗收：KPI row includes primary and secondary metric fields for the experiment.
- 回填：Update kpi-tracker.csv, weekly-summary, decision gate, offer board, and experiment plan.
- 資產：`vivian-email_lead_template` -> https://lovetypes.tw/contact/#luna-supply-request

### vivian-luna_soft_offer-brief

- 狀態：blocked_by_gate
- 守護者：薇薇安（vivian）
- 實驗：luna_soft_offer
- 步驟：brief / owner: content
- 交付物：Write a one-page asset brief with guardian, scene, promise boundary, and CTA.
- 驗收：Brief keeps the Shorts CTA as quiz and places offer only after result route.
- 回填：Update offer-experiment-plan after KPI review.
- 資產：`vivian-luna_scene_cta` -> https://lovetypes.tw/luna-yoga-music/#luna-vivian

### vivian-luna_soft_offer-asset

- 狀態：blocked_by_gate
- 守護者：薇薇安（vivian）
- 實驗：luna_soft_offer
- 步驟：asset / owner: creative
- 交付物：Produce the smallest useful asset or route copy for the experiment.
- 驗收：Asset links to the existing target URL and does not claim diagnosis or therapeutic outcome.
- 回填：Record fulfillment asset in lead-intake-tracker.csv when a real request exists.
- 資產：`vivian-luna_scene_cta` -> https://lovetypes.tw/luna-yoga-music/#luna-vivian

### vivian-luna_soft_offer-qa

- 狀態：blocked_by_gate
- 守護者：薇薇安（vivian）
- 實驗：luna_soft_offer
- 步驟：qa / owner: ops
- 交付物：Check safety copy, route, tracking event, and mobile presentation before publish.
- 驗收：Public smoke remains clean and no paid CTA is added before the experiment is READY.
- 回填：Run predeploy_check.py before deploy.
- 資產：`vivian-luna_scene_cta` -> https://lovetypes.tw/luna-yoga-music/#luna-vivian

### vivian-luna_soft_offer-measure

- 狀態：blocked_by_gate
- 守護者：薇薇安（vivian）
- 實驗：luna_soft_offer
- 步驟：measure / owner: ops
- 交付物：After the test window, backfill KPI fields and decide continue, revise, or stop.
- 驗收：KPI row includes primary and secondary metric fields for the experiment.
- 回填：Update kpi-tracker.csv, weekly-summary, decision gate, offer board, and experiment plan.
- 資產：`vivian-luna_scene_cta` -> https://lovetypes.tw/luna-yoga-music/#luna-vivian

### vivian-affiliate_book-brief

- 狀態：blocked_by_gate
- 守護者：薇薇安（vivian）
- 實驗：affiliate_book
- 步驟：brief / owner: content
- 交付物：Write a one-page asset brief with guardian, scene, promise boundary, and CTA.
- 驗收：Brief keeps the Shorts CTA as quiz and places offer only after result route.
- 回填：Update offer-experiment-plan after KPI review.
- 資產：`vivian-affiliate_book_bundle` -> https://lovetypes.tw/resources/#supply-vivian

### vivian-affiliate_book-asset

- 狀態：blocked_by_gate
- 守護者：薇薇安（vivian）
- 實驗：affiliate_book
- 步驟：asset / owner: creative
- 交付物：Produce the smallest useful asset or route copy for the experiment.
- 驗收：Asset links to the existing target URL and does not claim diagnosis or therapeutic outcome.
- 回填：Record fulfillment asset in lead-intake-tracker.csv when a real request exists.
- 資產：`vivian-affiliate_book_bundle` -> https://lovetypes.tw/resources/#supply-vivian

### vivian-affiliate_book-qa

- 狀態：blocked_by_gate
- 守護者：薇薇安（vivian）
- 實驗：affiliate_book
- 步驟：qa / owner: ops
- 交付物：Check safety copy, route, tracking event, and mobile presentation before publish.
- 驗收：Public smoke remains clean and no paid CTA is added before the experiment is READY.
- 回填：Run predeploy_check.py before deploy.
- 資產：`vivian-affiliate_book_bundle` -> https://lovetypes.tw/resources/#supply-vivian

### vivian-affiliate_book-measure

- 狀態：blocked_by_gate
- 守護者：薇薇安（vivian）
- 實驗：affiliate_book
- 步驟：measure / owner: ops
- 交付物：After the test window, backfill KPI fields and decide continue, revise, or stop.
- 驗收：KPI row includes primary and secondary metric fields for the experiment.
- 回填：Update kpi-tracker.csv, weekly-summary, decision gate, offer board, and experiment plan.
- 資產：`vivian-affiliate_book_bundle` -> https://lovetypes.tw/resources/#supply-vivian

### claire-identity_save-brief

- 狀態：blocked_by_gate
- 守護者：克萊兒（claire）
- 實驗：identity_save
- 步驟：brief / owner: content
- 交付物：Write a one-page asset brief with guardian, scene, promise boundary, and CTA.
- 驗收：Brief keeps the Shorts CTA as quiz and places offer only after result route.
- 回填：Update offer-experiment-plan after KPI review.
- 資產：`claire-free_story_card_upgrade` -> https://lovetypes.tw/keepsakes/#keepsake-claire

### claire-identity_save-asset

- 狀態：blocked_by_gate
- 守護者：克萊兒（claire）
- 實驗：identity_save
- 步驟：asset / owner: creative
- 交付物：Produce the smallest useful asset or route copy for the experiment.
- 驗收：Asset links to the existing target URL and does not claim diagnosis or therapeutic outcome.
- 回填：Record fulfillment asset in lead-intake-tracker.csv when a real request exists.
- 資產：`claire-free_story_card_upgrade` -> https://lovetypes.tw/keepsakes/#keepsake-claire

### claire-identity_save-qa

- 狀態：blocked_by_gate
- 守護者：克萊兒（claire）
- 實驗：identity_save
- 步驟：qa / owner: ops
- 交付物：Check safety copy, route, tracking event, and mobile presentation before publish.
- 驗收：Public smoke remains clean and no paid CTA is added before the experiment is READY.
- 回填：Run predeploy_check.py before deploy.
- 資產：`claire-free_story_card_upgrade` -> https://lovetypes.tw/keepsakes/#keepsake-claire

### claire-identity_save-measure

- 狀態：blocked_by_gate
- 守護者：克萊兒（claire）
- 實驗：identity_save
- 步驟：measure / owner: ops
- 交付物：After the test window, backfill KPI fields and decide continue, revise, or stop.
- 驗收：KPI row includes primary and secondary metric fields for the experiment.
- 回填：Update kpi-tracker.csv, weekly-summary, decision gate, offer board, and experiment plan.
- 資產：`claire-free_story_card_upgrade` -> https://lovetypes.tw/keepsakes/#keepsake-claire

### claire-owned_lead-brief

- 狀態：blocked_by_gate
- 守護者：克萊兒（claire）
- 實驗：owned_lead
- 步驟：brief / owner: content
- 交付物：Write a one-page asset brief with guardian, scene, promise boundary, and CTA.
- 驗收：Brief keeps the Shorts CTA as quiz and places offer only after result route.
- 回填：Update offer-experiment-plan after KPI review.
- 資產：`claire-email_lead_template` -> https://lovetypes.tw/contact/#luna-supply-request

### claire-owned_lead-asset

- 狀態：blocked_by_gate
- 守護者：克萊兒（claire）
- 實驗：owned_lead
- 步驟：asset / owner: creative
- 交付物：Produce the smallest useful asset or route copy for the experiment.
- 驗收：Asset links to the existing target URL and does not claim diagnosis or therapeutic outcome.
- 回填：Record fulfillment asset in lead-intake-tracker.csv when a real request exists.
- 資產：`claire-email_lead_template` -> https://lovetypes.tw/contact/#luna-supply-request

### claire-owned_lead-qa

- 狀態：blocked_by_gate
- 守護者：克萊兒（claire）
- 實驗：owned_lead
- 步驟：qa / owner: ops
- 交付物：Check safety copy, route, tracking event, and mobile presentation before publish.
- 驗收：Public smoke remains clean and no paid CTA is added before the experiment is READY.
- 回填：Run predeploy_check.py before deploy.
- 資產：`claire-email_lead_template` -> https://lovetypes.tw/contact/#luna-supply-request

### claire-owned_lead-measure

- 狀態：blocked_by_gate
- 守護者：克萊兒（claire）
- 實驗：owned_lead
- 步驟：measure / owner: ops
- 交付物：After the test window, backfill KPI fields and decide continue, revise, or stop.
- 驗收：KPI row includes primary and secondary metric fields for the experiment.
- 回填：Update kpi-tracker.csv, weekly-summary, decision gate, offer board, and experiment plan.
- 資產：`claire-email_lead_template` -> https://lovetypes.tw/contact/#luna-supply-request

### claire-luna_soft_offer-brief

- 狀態：blocked_by_gate
- 守護者：克萊兒（claire）
- 實驗：luna_soft_offer
- 步驟：brief / owner: content
- 交付物：Write a one-page asset brief with guardian, scene, promise boundary, and CTA.
- 驗收：Brief keeps the Shorts CTA as quiz and places offer only after result route.
- 回填：Update offer-experiment-plan after KPI review.
- 資產：`claire-luna_scene_cta` -> https://lovetypes.tw/luna-yoga-music/#luna-claire

### claire-luna_soft_offer-asset

- 狀態：blocked_by_gate
- 守護者：克萊兒（claire）
- 實驗：luna_soft_offer
- 步驟：asset / owner: creative
- 交付物：Produce the smallest useful asset or route copy for the experiment.
- 驗收：Asset links to the existing target URL and does not claim diagnosis or therapeutic outcome.
- 回填：Record fulfillment asset in lead-intake-tracker.csv when a real request exists.
- 資產：`claire-luna_scene_cta` -> https://lovetypes.tw/luna-yoga-music/#luna-claire

### claire-luna_soft_offer-qa

- 狀態：blocked_by_gate
- 守護者：克萊兒（claire）
- 實驗：luna_soft_offer
- 步驟：qa / owner: ops
- 交付物：Check safety copy, route, tracking event, and mobile presentation before publish.
- 驗收：Public smoke remains clean and no paid CTA is added before the experiment is READY.
- 回填：Run predeploy_check.py before deploy.
- 資產：`claire-luna_scene_cta` -> https://lovetypes.tw/luna-yoga-music/#luna-claire

### claire-luna_soft_offer-measure

- 狀態：blocked_by_gate
- 守護者：克萊兒（claire）
- 實驗：luna_soft_offer
- 步驟：measure / owner: ops
- 交付物：After the test window, backfill KPI fields and decide continue, revise, or stop.
- 驗收：KPI row includes primary and secondary metric fields for the experiment.
- 回填：Update kpi-tracker.csv, weekly-summary, decision gate, offer board, and experiment plan.
- 資產：`claire-luna_scene_cta` -> https://lovetypes.tw/luna-yoga-music/#luna-claire

### claire-affiliate_book-brief

- 狀態：blocked_by_gate
- 守護者：克萊兒（claire）
- 實驗：affiliate_book
- 步驟：brief / owner: content
- 交付物：Write a one-page asset brief with guardian, scene, promise boundary, and CTA.
- 驗收：Brief keeps the Shorts CTA as quiz and places offer only after result route.
- 回填：Update offer-experiment-plan after KPI review.
- 資產：`claire-affiliate_book_bundle` -> https://lovetypes.tw/resources/#supply-claire

### claire-affiliate_book-asset

- 狀態：blocked_by_gate
- 守護者：克萊兒（claire）
- 實驗：affiliate_book
- 步驟：asset / owner: creative
- 交付物：Produce the smallest useful asset or route copy for the experiment.
- 驗收：Asset links to the existing target URL and does not claim diagnosis or therapeutic outcome.
- 回填：Record fulfillment asset in lead-intake-tracker.csv when a real request exists.
- 資產：`claire-affiliate_book_bundle` -> https://lovetypes.tw/resources/#supply-claire

### claire-affiliate_book-qa

- 狀態：blocked_by_gate
- 守護者：克萊兒（claire）
- 實驗：affiliate_book
- 步驟：qa / owner: ops
- 交付物：Check safety copy, route, tracking event, and mobile presentation before publish.
- 驗收：Public smoke remains clean and no paid CTA is added before the experiment is READY.
- 回填：Run predeploy_check.py before deploy.
- 資產：`claire-affiliate_book_bundle` -> https://lovetypes.tw/resources/#supply-claire

### claire-affiliate_book-measure

- 狀態：blocked_by_gate
- 守護者：克萊兒（claire）
- 實驗：affiliate_book
- 步驟：measure / owner: ops
- 交付物：After the test window, backfill KPI fields and decide continue, revise, or stop.
- 驗收：KPI row includes primary and secondary metric fields for the experiment.
- 回填：Update kpi-tracker.csv, weekly-summary, decision gate, offer board, and experiment plan.
- 資產：`claire-affiliate_book_bundle` -> https://lovetypes.tw/resources/#supply-claire

### dora-identity_save-brief

- 狀態：blocked_by_gate
- 守護者：朵拉（dora）
- 實驗：identity_save
- 步驟：brief / owner: content
- 交付物：Write a one-page asset brief with guardian, scene, promise boundary, and CTA.
- 驗收：Brief keeps the Shorts CTA as quiz and places offer only after result route.
- 回填：Update offer-experiment-plan after KPI review.
- 資產：`dora-free_story_card_upgrade` -> https://lovetypes.tw/keepsakes/#keepsake-dora

### dora-identity_save-asset

- 狀態：blocked_by_gate
- 守護者：朵拉（dora）
- 實驗：identity_save
- 步驟：asset / owner: creative
- 交付物：Produce the smallest useful asset or route copy for the experiment.
- 驗收：Asset links to the existing target URL and does not claim diagnosis or therapeutic outcome.
- 回填：Record fulfillment asset in lead-intake-tracker.csv when a real request exists.
- 資產：`dora-free_story_card_upgrade` -> https://lovetypes.tw/keepsakes/#keepsake-dora

### dora-identity_save-qa

- 狀態：blocked_by_gate
- 守護者：朵拉（dora）
- 實驗：identity_save
- 步驟：qa / owner: ops
- 交付物：Check safety copy, route, tracking event, and mobile presentation before publish.
- 驗收：Public smoke remains clean and no paid CTA is added before the experiment is READY.
- 回填：Run predeploy_check.py before deploy.
- 資產：`dora-free_story_card_upgrade` -> https://lovetypes.tw/keepsakes/#keepsake-dora

### dora-identity_save-measure

- 狀態：blocked_by_gate
- 守護者：朵拉（dora）
- 實驗：identity_save
- 步驟：measure / owner: ops
- 交付物：After the test window, backfill KPI fields and decide continue, revise, or stop.
- 驗收：KPI row includes primary and secondary metric fields for the experiment.
- 回填：Update kpi-tracker.csv, weekly-summary, decision gate, offer board, and experiment plan.
- 資產：`dora-free_story_card_upgrade` -> https://lovetypes.tw/keepsakes/#keepsake-dora

### dora-owned_lead-brief

- 狀態：blocked_by_gate
- 守護者：朵拉（dora）
- 實驗：owned_lead
- 步驟：brief / owner: content
- 交付物：Write a one-page asset brief with guardian, scene, promise boundary, and CTA.
- 驗收：Brief keeps the Shorts CTA as quiz and places offer only after result route.
- 回填：Update offer-experiment-plan after KPI review.
- 資產：`dora-email_lead_template` -> https://lovetypes.tw/contact/#luna-supply-request

### dora-owned_lead-asset

- 狀態：blocked_by_gate
- 守護者：朵拉（dora）
- 實驗：owned_lead
- 步驟：asset / owner: creative
- 交付物：Produce the smallest useful asset or route copy for the experiment.
- 驗收：Asset links to the existing target URL and does not claim diagnosis or therapeutic outcome.
- 回填：Record fulfillment asset in lead-intake-tracker.csv when a real request exists.
- 資產：`dora-email_lead_template` -> https://lovetypes.tw/contact/#luna-supply-request

### dora-owned_lead-qa

- 狀態：blocked_by_gate
- 守護者：朵拉（dora）
- 實驗：owned_lead
- 步驟：qa / owner: ops
- 交付物：Check safety copy, route, tracking event, and mobile presentation before publish.
- 驗收：Public smoke remains clean and no paid CTA is added before the experiment is READY.
- 回填：Run predeploy_check.py before deploy.
- 資產：`dora-email_lead_template` -> https://lovetypes.tw/contact/#luna-supply-request

### dora-owned_lead-measure

- 狀態：blocked_by_gate
- 守護者：朵拉（dora）
- 實驗：owned_lead
- 步驟：measure / owner: ops
- 交付物：After the test window, backfill KPI fields and decide continue, revise, or stop.
- 驗收：KPI row includes primary and secondary metric fields for the experiment.
- 回填：Update kpi-tracker.csv, weekly-summary, decision gate, offer board, and experiment plan.
- 資產：`dora-email_lead_template` -> https://lovetypes.tw/contact/#luna-supply-request

### dora-luna_soft_offer-brief

- 狀態：blocked_by_gate
- 守護者：朵拉（dora）
- 實驗：luna_soft_offer
- 步驟：brief / owner: content
- 交付物：Write a one-page asset brief with guardian, scene, promise boundary, and CTA.
- 驗收：Brief keeps the Shorts CTA as quiz and places offer only after result route.
- 回填：Update offer-experiment-plan after KPI review.
- 資產：`dora-luna_scene_cta` -> https://lovetypes.tw/luna-yoga-music/#luna-dora

### dora-luna_soft_offer-asset

- 狀態：blocked_by_gate
- 守護者：朵拉（dora）
- 實驗：luna_soft_offer
- 步驟：asset / owner: creative
- 交付物：Produce the smallest useful asset or route copy for the experiment.
- 驗收：Asset links to the existing target URL and does not claim diagnosis or therapeutic outcome.
- 回填：Record fulfillment asset in lead-intake-tracker.csv when a real request exists.
- 資產：`dora-luna_scene_cta` -> https://lovetypes.tw/luna-yoga-music/#luna-dora

### dora-luna_soft_offer-qa

- 狀態：blocked_by_gate
- 守護者：朵拉（dora）
- 實驗：luna_soft_offer
- 步驟：qa / owner: ops
- 交付物：Check safety copy, route, tracking event, and mobile presentation before publish.
- 驗收：Public smoke remains clean and no paid CTA is added before the experiment is READY.
- 回填：Run predeploy_check.py before deploy.
- 資產：`dora-luna_scene_cta` -> https://lovetypes.tw/luna-yoga-music/#luna-dora

### dora-luna_soft_offer-measure

- 狀態：blocked_by_gate
- 守護者：朵拉（dora）
- 實驗：luna_soft_offer
- 步驟：measure / owner: ops
- 交付物：After the test window, backfill KPI fields and decide continue, revise, or stop.
- 驗收：KPI row includes primary and secondary metric fields for the experiment.
- 回填：Update kpi-tracker.csv, weekly-summary, decision gate, offer board, and experiment plan.
- 資產：`dora-luna_scene_cta` -> https://lovetypes.tw/luna-yoga-music/#luna-dora

### dora-affiliate_book-brief

- 狀態：blocked_by_gate
- 守護者：朵拉（dora）
- 實驗：affiliate_book
- 步驟：brief / owner: content
- 交付物：Write a one-page asset brief with guardian, scene, promise boundary, and CTA.
- 驗收：Brief keeps the Shorts CTA as quiz and places offer only after result route.
- 回填：Update offer-experiment-plan after KPI review.
- 資產：`dora-affiliate_book_bundle` -> https://lovetypes.tw/resources/#supply-dora

### dora-affiliate_book-asset

- 狀態：blocked_by_gate
- 守護者：朵拉（dora）
- 實驗：affiliate_book
- 步驟：asset / owner: creative
- 交付物：Produce the smallest useful asset or route copy for the experiment.
- 驗收：Asset links to the existing target URL and does not claim diagnosis or therapeutic outcome.
- 回填：Record fulfillment asset in lead-intake-tracker.csv when a real request exists.
- 資產：`dora-affiliate_book_bundle` -> https://lovetypes.tw/resources/#supply-dora

### dora-affiliate_book-qa

- 狀態：blocked_by_gate
- 守護者：朵拉（dora）
- 實驗：affiliate_book
- 步驟：qa / owner: ops
- 交付物：Check safety copy, route, tracking event, and mobile presentation before publish.
- 驗收：Public smoke remains clean and no paid CTA is added before the experiment is READY.
- 回填：Run predeploy_check.py before deploy.
- 資產：`dora-affiliate_book_bundle` -> https://lovetypes.tw/resources/#supply-dora

### dora-affiliate_book-measure

- 狀態：blocked_by_gate
- 守護者：朵拉（dora）
- 實驗：affiliate_book
- 步驟：measure / owner: ops
- 交付物：After the test window, backfill KPI fields and decide continue, revise, or stop.
- 驗收：KPI row includes primary and secondary metric fields for the experiment.
- 回填：Update kpi-tracker.csv, weekly-summary, decision gate, offer board, and experiment plan.
- 資產：`dora-affiliate_book_bundle` -> https://lovetypes.tw/resources/#supply-dora

## 安全邊界

- 未達 READY 前，不新增或加重付費 CTA。
- 每個實驗都必須保留測驗作為 Shorts 主 CTA。
- 商品或聯盟只放在結果後路線、旅人補給、Luna 或 Contact 承接。
