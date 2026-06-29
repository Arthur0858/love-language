# LoveTypes Decision Readiness Checklist

- Generated: `2026-06-30`
- Decisions: `5`
- Active signal rows: `1`
- Ready rows: `0`
- Blocked rows: `4`
- Issues: `0`

## Rule

- Empty or minimum-only data can only support launch execution and KPI backfill.
- Commercial changes require matching route, lead, Luna, affiliate, or contact signals.
- Shorts and profile CTAs remain focused on the quiz until result-route evidence exists.

## `collect_signal`

- Status: `active`
- Required signal: profile links and first-batch publication not complete
- Current value: `blocked`
- Required value: Allowed while launch is incomplete; do not make commercial decisions.
- Allowed: Set profile links, publish first batch, backfill post URL and minimum KPI.
- Blocked: Change offer order, paid CTA, Luna emphasis, affiliate emphasis, or winning guardian.
- Evidence: `docs/promotion/first-round/week-decision-gate.json; docs/promotion/first-round/revenue-decision-matrix.json; docs/promotion/first-round/weekly-summary.json`

## `scale_content`

- Status: `blocked`
- Required signal: quiz_completions
- Current value: `0`
- Required value: At least the configured scale-content quiz completion threshold and acceptable completion rate. Current threshold: 10 quiz completions.
- Allowed: Publish more variants for the strongest guardian or pain point while keeping quiz CTA.
- Blocked: Treat content interest as proof of purchase intent.
- Evidence: `docs/promotion/first-round/week-decision-gate.json; docs/promotion/first-round/revenue-decision-matrix.json; docs/promotion/first-round/weekly-summary.json`

## `deepen_identity_asset`

- Status: `blocked`
- Required signal: identityRouteInterest
- Current value: `0`
- Required value: Any guardian result, route, keepsake, or resource interest after weekly gate is ready.
- Allowed: Improve free keepsakes, story cards, share images, and result-route assets.
- Blocked: Move the primary CTA directly to paid products.
- Evidence: `docs/promotion/first-round/week-decision-gate.json; docs/promotion/first-round/revenue-decision-matrix.json; docs/promotion/first-round/weekly-summary.json`

## `build_owned_lead_asset`

- Status: `blocked`
- Required signal: leadIntent
- Current value: `0`
- Required value: Any supply lead, contact request, or explicit downloadable asset request.
- Allowed: Build one low-risk email/download asset for the signaled guardian or route.
- Blocked: Build a paid product before repeated lead evidence exists.
- Evidence: `docs/promotion/first-round/week-decision-gate.json; docs/promotion/first-round/revenue-decision-matrix.json; docs/promotion/first-round/weekly-summary.json`

## `test_soft_offer`

- Status: `blocked`
- Required signal: paidRevenueIntent
- Current value: `0`
- Required value: Any Luna pack, affiliate book, or other revenue-route click after result-route context.
- Allowed: Test a soft result-route offer; keep Shorts and profile CTAs focused on the quiz.
- Blocked: Use direct sales language in first-touch Shorts or profile bio.
- Evidence: `docs/promotion/first-round/week-decision-gate.json; docs/promotion/first-round/revenue-decision-matrix.json; docs/promotion/first-round/weekly-summary.json`
