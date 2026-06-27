# LoveTypes Blocker Resolution Checklist

- 產生日期：2026-06-27
- current stage：`first_batch_kpi`
- rows：10
- active blockers：7
- ready now：1
- empty data mode：0
- issues：0

## Rule

- 只解除有外部證據的 blocker；不可用預設模板當成已完成。
- 啟用平台 Profile 完成前，不發布第一批貼文。
- 公開 URL 與 KPI 來源確認前，不做週決策、商品化或 Luna / 聯盟權重調整。

## Checklist

- [x] `profile_link_youtube_shorts`（profile_setup / complete）
  - scope：`youtube_shorts`
  - action：Set the platform profile/Bio link to the listed /start/ URL, then verify the copied platform link still keeps UTM.
  - release：platform-profile-tracker.csv row is set/live with profile_link_set_date and traceable proof note.
  - evidence：`https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio`
  - writeback：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`
- [ ] `publish_youtube_shorts_publish-lt-s01-iris-silence`（publish_first_batch / ready_to_act）
  - scope：`youtube_shorts:publish-lt-s01-iris-silence`
  - action：Publish or schedule the first-batch Shorts post with quiz-only CTA, then copy the real public post URL.
  - release：posting-queue.csv and platform-kpi-tracker.csv have status=published, published_date, and a verified HTTPS post_url.
  - evidence：`https://lovetypes.tw/start/?utm_source=shorts&utm_medium=social&utm_campaign=first_round_quiz_completion&utm_content=iris_silence`
  - writeback：`python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt --proof-note "<REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified"`
- [x] `public_post_urls_verified`（publish_first_batch / complete）
  - scope：`first_round`
  - action：Every public post URL has platform domain, public view, CTA, UTM, and proof evidence checked.
  - release：證據已滿足。
  - evidence：`docs/promotion/first-round/weekly-decision-evidence-checklist.json`
  - writeback：`python3 tools/promotion_daily_ops_refresh.py`
- [ ] `zero_kpis_have_source`（kpi_backfill / blocked_until_evidence）
  - scope：`first_round`
  - action：Zero values for site_clicks, quiz_starts, and quiz_completions have checked-source proof.
  - release：核心 KPI 仍未發布、未回填，或 0 值缺來源證據。
  - evidence：`docs/promotion/first-round/weekly-decision-evidence-checklist.json`
  - writeback：`python3 tools/promotion_daily_ops_refresh.py`
- [ ] `weekly_review_ready`（weekly_review / blocked_until_evidence）
  - scope：`first_round`
  - action：Weekly review packet reports readyForWeeklyDecision=1.
  - release：weekly review 尚未達可決策狀態。
  - evidence：`docs/promotion/first-round/weekly-decision-evidence-checklist.json`
  - writeback：`python3 tools/promotion_daily_ops_refresh.py`
- [x] `not_empty_data_mode`（weekly_review / complete）
  - scope：`first_round`
  - action：Empty data mode is false before commerce or prioritization decisions.
  - release：證據已滿足。
  - evidence：`docs/promotion/first-round/weekly-decision-evidence-checklist.json`
  - writeback：`python3 tools/promotion_daily_ops_refresh.py`
- [ ] `decision_gate_ready`（weekly_decision / blocked_until_evidence）
  - scope：`first_round`
  - action：Week decision gate allows at least weeklyDecision before changing content or commerce paths.
  - release：week decision gate 仍是 HOLD。
  - evidence：`docs/promotion/first-round/weekly-decision-evidence-checklist.json`
  - writeback：`python3 tools/promotion_daily_ops_refresh.py`
- [ ] `first_batch_minimum_kpi_rows`（kpi_backfill / blocked_until_post_urls）
  - scope：`first_batch`
  - action：After public URLs exist, check platform analytics and site analytics before entering site_clicks, quiz_starts, and quiz_completions.
  - release：At least first-batch rows have real source-checked KPI values or source-checked zeros.
  - evidence：`docs/promotion/first-round/platform-kpi-tracker.csv`
  - writeback：`python3 tools/promotion_post_text_import.py add --input <post-proof.txt> --proof-note "<REAL_PUBLIC_POST_URL_AND_ANALYTICS_SOURCE_PROOF>"`
- [ ] `no_real_leads`（lead_collection / blocked_until_real_request）
  - scope：`lead_intake`
  - action：Collect a real Contact/Keepsakes/Luna request with guardian, request type, reply email, consent, and source.
  - release：lead-intake-tracker.csv has at least one non-template row with explicit consent and traceable source.
  - evidence：`docs/promotion/first-round/lead-intake-tracker.csv`
  - writeback：`python3 tools/promotion_lead_text_import.py add --input <lead-request.txt> --proof-note "<REAL_EMAIL_THREAD_OR_FORM_REQUEST_PROOF>"`
- [ ] `no_ready_offer_experiment`（offer_experiment / blocked_until_repeated_intent）
  - scope：`commerce`
  - action：Wait for repeated route, lead, Luna, or affiliate intent before creating a paid pack or changing offer order.
  - release：offer-experiment-plan.json has a ready experiment selected from non-empty demand evidence.
  - evidence：`docs/promotion/first-round/offer-experiment-plan.json`
  - writeback：`python3 tools/promotion_offer_experiment_plan.py`
