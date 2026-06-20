# LoveTypes Asset Fulfillment Gate

- 產生日期：2026-06-21
- rows：40
- ready to prepare：5
- public free ready：5
- blocked until real request：20
- blocked until offer ready：10
- real leads：0
- issues：0

## Rule

- 空資料時只能準備內容變體與既有免費收藏物，不交付自有 PDF/桌布/Luna pack，也不加重付費 CTA。
- 自有素材履約必須有真實需求，且只能解鎖使用者明確要求的素材類型。
- Luna / 聯盟 / 商業資產必須等 offer experiment queue READY。
- 所有履約都必須保留安全邊界：不診斷、不承諾療效、不替代諮商。

## Rows

### 艾莉絲 · `free_story_card_upgrade`

- asset：`iris-free_story_card_upgrade`
- status：`public_free_ready`
- priority：`later`
- target：https://lovetypes.tw/keepsakes/#keepsake-iris
- evidence：Existing keepsake story card and practice-card route are present across all languages.
- stop：Do not treat saves/downloads as demand until tracked externally.

### 艾莉絲 · `pdf_practice_card`

- asset：`iris-pdf_practice_card`
- status：`blocked_until_real_request`
- priority：`later`
- target：https://lovetypes.tw/keepsakes/#keepsake-iris
- evidence：Owned assets require at least one traceable request for this specific asset type.
- stop：Wait for lead-intake-tracker.csv evidence before building or sending.

### 艾莉絲 · `phone_wallpaper`

- asset：`iris-phone_wallpaper`
- status：`blocked_until_real_request`
- priority：`later`
- target：https://lovetypes.tw/keepsakes/#keepsake-iris
- evidence：Owned assets require at least one traceable request for this specific asset type.
- stop：Wait for lead-intake-tracker.csv evidence before building or sending.

### 艾莉絲 · `email_lead_template`

- asset：`iris-email_lead_template`
- status：`blocked_until_real_request`
- priority：`later`
- target：https://lovetypes.tw/contact/#luna-supply-request
- evidence：Owned assets require at least one traceable request for this specific asset type.
- stop：Wait for lead-intake-tracker.csv evidence before building or sending.

### 艾莉絲 · `short_ritual`

- asset：`iris-short_ritual`
- status：`blocked_until_real_request`
- priority：`later`
- target：https://lovetypes.tw/repair-plan/#plan-iris
- evidence：Owned assets require at least one traceable request for this specific asset type.
- stop：Wait for lead-intake-tracker.csv evidence before building or sending.

### 艾莉絲 · `luna_scene_cta`

- asset：`iris-luna_scene_cta`
- status：`blocked_until_offer_ready`
- priority：`later`
- target：https://lovetypes.tw/luna-yoga-music/#luna-iris
- evidence：Commercial or Luna assets require a READY offer experiment.
- stop：Keep Luna/affiliate as secondary routes until KPI evidence is non-empty.

### 艾莉絲 · `affiliate_book_bundle`

- asset：`iris-affiliate_book_bundle`
- status：`blocked_until_offer_ready`
- priority：`later`
- target：https://lovetypes.tw/resources/#supply-iris
- evidence：Commercial or Luna assets require a READY offer experiment.
- stop：Keep Luna/affiliate as secondary routes until KPI evidence is non-empty.

### 艾莉絲 · `content_variant`

- asset：`iris-content_variant`
- status：`ready_to_prepare`
- priority：`now`
- target：https://lovetypes.tw/start/
- evidence：Content variants can be prepared in empty-data mode as long as the Shorts CTA stays focused on the quiz.
- stop：Do not publish as a winning variant until KPI rows exist.

### 諾雅 · `free_story_card_upgrade`

- asset：`noah-free_story_card_upgrade`
- status：`public_free_ready`
- priority：`later`
- target：https://lovetypes.tw/keepsakes/#keepsake-noah
- evidence：Existing keepsake story card and practice-card route are present across all languages.
- stop：Do not treat saves/downloads as demand until tracked externally.

### 諾雅 · `pdf_practice_card`

- asset：`noah-pdf_practice_card`
- status：`blocked_until_real_request`
- priority：`later`
- target：https://lovetypes.tw/keepsakes/#keepsake-noah
- evidence：Owned assets require at least one traceable request for this specific asset type.
- stop：Wait for lead-intake-tracker.csv evidence before building or sending.

### 諾雅 · `phone_wallpaper`

- asset：`noah-phone_wallpaper`
- status：`blocked_until_real_request`
- priority：`later`
- target：https://lovetypes.tw/keepsakes/#keepsake-noah
- evidence：Owned assets require at least one traceable request for this specific asset type.
- stop：Wait for lead-intake-tracker.csv evidence before building or sending.

### 諾雅 · `email_lead_template`

- asset：`noah-email_lead_template`
- status：`blocked_until_real_request`
- priority：`later`
- target：https://lovetypes.tw/contact/#luna-supply-request
- evidence：Owned assets require at least one traceable request for this specific asset type.
- stop：Wait for lead-intake-tracker.csv evidence before building or sending.

### 諾雅 · `short_ritual`

- asset：`noah-short_ritual`
- status：`blocked_until_real_request`
- priority：`later`
- target：https://lovetypes.tw/repair-plan/#plan-noah
- evidence：Owned assets require at least one traceable request for this specific asset type.
- stop：Wait for lead-intake-tracker.csv evidence before building or sending.

### 諾雅 · `luna_scene_cta`

- asset：`noah-luna_scene_cta`
- status：`blocked_until_offer_ready`
- priority：`later`
- target：https://lovetypes.tw/luna-yoga-music/#luna-noah
- evidence：Commercial or Luna assets require a READY offer experiment.
- stop：Keep Luna/affiliate as secondary routes until KPI evidence is non-empty.

### 諾雅 · `affiliate_book_bundle`

- asset：`noah-affiliate_book_bundle`
- status：`blocked_until_offer_ready`
- priority：`later`
- target：https://lovetypes.tw/resources/#supply-noah
- evidence：Commercial or Luna assets require a READY offer experiment.
- stop：Keep Luna/affiliate as secondary routes until KPI evidence is non-empty.

### 諾雅 · `content_variant`

- asset：`noah-content_variant`
- status：`ready_to_prepare`
- priority：`now`
- target：https://lovetypes.tw/start/
- evidence：Content variants can be prepared in empty-data mode as long as the Shorts CTA stays focused on the quiz.
- stop：Do not publish as a winning variant until KPI rows exist.

### 薇薇安 · `free_story_card_upgrade`

- asset：`vivian-free_story_card_upgrade`
- status：`public_free_ready`
- priority：`later`
- target：https://lovetypes.tw/keepsakes/#keepsake-vivian
- evidence：Existing keepsake story card and practice-card route are present across all languages.
- stop：Do not treat saves/downloads as demand until tracked externally.

### 薇薇安 · `pdf_practice_card`

- asset：`vivian-pdf_practice_card`
- status：`blocked_until_real_request`
- priority：`later`
- target：https://lovetypes.tw/keepsakes/#keepsake-vivian
- evidence：Owned assets require at least one traceable request for this specific asset type.
- stop：Wait for lead-intake-tracker.csv evidence before building or sending.

### 薇薇安 · `phone_wallpaper`

- asset：`vivian-phone_wallpaper`
- status：`blocked_until_real_request`
- priority：`later`
- target：https://lovetypes.tw/keepsakes/#keepsake-vivian
- evidence：Owned assets require at least one traceable request for this specific asset type.
- stop：Wait for lead-intake-tracker.csv evidence before building or sending.

### 薇薇安 · `email_lead_template`

- asset：`vivian-email_lead_template`
- status：`blocked_until_real_request`
- priority：`later`
- target：https://lovetypes.tw/contact/#luna-supply-request
- evidence：Owned assets require at least one traceable request for this specific asset type.
- stop：Wait for lead-intake-tracker.csv evidence before building or sending.

### 薇薇安 · `short_ritual`

- asset：`vivian-short_ritual`
- status：`blocked_until_real_request`
- priority：`later`
- target：https://lovetypes.tw/repair-plan/#plan-vivian
- evidence：Owned assets require at least one traceable request for this specific asset type.
- stop：Wait for lead-intake-tracker.csv evidence before building or sending.

### 薇薇安 · `luna_scene_cta`

- asset：`vivian-luna_scene_cta`
- status：`blocked_until_offer_ready`
- priority：`later`
- target：https://lovetypes.tw/luna-yoga-music/#luna-vivian
- evidence：Commercial or Luna assets require a READY offer experiment.
- stop：Keep Luna/affiliate as secondary routes until KPI evidence is non-empty.

### 薇薇安 · `affiliate_book_bundle`

- asset：`vivian-affiliate_book_bundle`
- status：`blocked_until_offer_ready`
- priority：`later`
- target：https://lovetypes.tw/resources/#supply-vivian
- evidence：Commercial or Luna assets require a READY offer experiment.
- stop：Keep Luna/affiliate as secondary routes until KPI evidence is non-empty.

### 薇薇安 · `content_variant`

- asset：`vivian-content_variant`
- status：`ready_to_prepare`
- priority：`now`
- target：https://lovetypes.tw/start/
- evidence：Content variants can be prepared in empty-data mode as long as the Shorts CTA stays focused on the quiz.
- stop：Do not publish as a winning variant until KPI rows exist.

### 克萊兒 · `free_story_card_upgrade`

- asset：`claire-free_story_card_upgrade`
- status：`public_free_ready`
- priority：`later`
- target：https://lovetypes.tw/keepsakes/#keepsake-claire
- evidence：Existing keepsake story card and practice-card route are present across all languages.
- stop：Do not treat saves/downloads as demand until tracked externally.

### 克萊兒 · `pdf_practice_card`

- asset：`claire-pdf_practice_card`
- status：`blocked_until_real_request`
- priority：`later`
- target：https://lovetypes.tw/keepsakes/#keepsake-claire
- evidence：Owned assets require at least one traceable request for this specific asset type.
- stop：Wait for lead-intake-tracker.csv evidence before building or sending.

### 克萊兒 · `phone_wallpaper`

- asset：`claire-phone_wallpaper`
- status：`blocked_until_real_request`
- priority：`later`
- target：https://lovetypes.tw/keepsakes/#keepsake-claire
- evidence：Owned assets require at least one traceable request for this specific asset type.
- stop：Wait for lead-intake-tracker.csv evidence before building or sending.

### 克萊兒 · `email_lead_template`

- asset：`claire-email_lead_template`
- status：`blocked_until_real_request`
- priority：`later`
- target：https://lovetypes.tw/contact/#luna-supply-request
- evidence：Owned assets require at least one traceable request for this specific asset type.
- stop：Wait for lead-intake-tracker.csv evidence before building or sending.

### 克萊兒 · `short_ritual`

- asset：`claire-short_ritual`
- status：`blocked_until_real_request`
- priority：`later`
- target：https://lovetypes.tw/repair-plan/#plan-claire
- evidence：Owned assets require at least one traceable request for this specific asset type.
- stop：Wait for lead-intake-tracker.csv evidence before building or sending.

### 克萊兒 · `luna_scene_cta`

- asset：`claire-luna_scene_cta`
- status：`blocked_until_offer_ready`
- priority：`later`
- target：https://lovetypes.tw/luna-yoga-music/#luna-claire
- evidence：Commercial or Luna assets require a READY offer experiment.
- stop：Keep Luna/affiliate as secondary routes until KPI evidence is non-empty.

### 克萊兒 · `affiliate_book_bundle`

- asset：`claire-affiliate_book_bundle`
- status：`blocked_until_offer_ready`
- priority：`later`
- target：https://lovetypes.tw/resources/#supply-claire
- evidence：Commercial or Luna assets require a READY offer experiment.
- stop：Keep Luna/affiliate as secondary routes until KPI evidence is non-empty.

### 克萊兒 · `content_variant`

- asset：`claire-content_variant`
- status：`ready_to_prepare`
- priority：`now`
- target：https://lovetypes.tw/start/
- evidence：Content variants can be prepared in empty-data mode as long as the Shorts CTA stays focused on the quiz.
- stop：Do not publish as a winning variant until KPI rows exist.

### 朵拉 · `free_story_card_upgrade`

- asset：`dora-free_story_card_upgrade`
- status：`public_free_ready`
- priority：`later`
- target：https://lovetypes.tw/keepsakes/#keepsake-dora
- evidence：Existing keepsake story card and practice-card route are present across all languages.
- stop：Do not treat saves/downloads as demand until tracked externally.

### 朵拉 · `pdf_practice_card`

- asset：`dora-pdf_practice_card`
- status：`blocked_until_real_request`
- priority：`later`
- target：https://lovetypes.tw/keepsakes/#keepsake-dora
- evidence：Owned assets require at least one traceable request for this specific asset type.
- stop：Wait for lead-intake-tracker.csv evidence before building or sending.

### 朵拉 · `phone_wallpaper`

- asset：`dora-phone_wallpaper`
- status：`blocked_until_real_request`
- priority：`later`
- target：https://lovetypes.tw/keepsakes/#keepsake-dora
- evidence：Owned assets require at least one traceable request for this specific asset type.
- stop：Wait for lead-intake-tracker.csv evidence before building or sending.

### 朵拉 · `email_lead_template`

- asset：`dora-email_lead_template`
- status：`blocked_until_real_request`
- priority：`later`
- target：https://lovetypes.tw/contact/#luna-supply-request
- evidence：Owned assets require at least one traceable request for this specific asset type.
- stop：Wait for lead-intake-tracker.csv evidence before building or sending.

### 朵拉 · `short_ritual`

- asset：`dora-short_ritual`
- status：`blocked_until_real_request`
- priority：`later`
- target：https://lovetypes.tw/repair-plan/#plan-dora
- evidence：Owned assets require at least one traceable request for this specific asset type.
- stop：Wait for lead-intake-tracker.csv evidence before building or sending.

### 朵拉 · `luna_scene_cta`

- asset：`dora-luna_scene_cta`
- status：`blocked_until_offer_ready`
- priority：`later`
- target：https://lovetypes.tw/luna-yoga-music/#luna-dora
- evidence：Commercial or Luna assets require a READY offer experiment.
- stop：Keep Luna/affiliate as secondary routes until KPI evidence is non-empty.

### 朵拉 · `affiliate_book_bundle`

- asset：`dora-affiliate_book_bundle`
- status：`blocked_until_offer_ready`
- priority：`later`
- target：https://lovetypes.tw/resources/#supply-dora
- evidence：Commercial or Luna assets require a READY offer experiment.
- stop：Keep Luna/affiliate as secondary routes until KPI evidence is non-empty.

### 朵拉 · `content_variant`

- asset：`dora-content_variant`
- status：`ready_to_prepare`
- priority：`now`
- target：https://lovetypes.tw/start/
- evidence：Content variants can be prepared in empty-data mode as long as the Shorts CTA stays focused on the quiz.
- stop：Do not publish as a winning variant until KPI rows exist.
