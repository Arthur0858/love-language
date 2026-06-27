# LoveTypes Lead Intake Closure Quickstart

- 產生日期：2026-06-27
- template rows：15
- real leads：0
- lead evidence rows：135
- pending template evidence rows：135
- evidence missing rows：0
- proof templates：15
- proof placeholder / real ready：15 / 0
- lead ops ready / blocked：1 / 2
- repeated routes / ready routes：0 / 0
- public free assets：5
- offer queue ready：0
- master stage：`first_batch_kpi`
- master lead ready routes：0
- issues：0

## Rules

- Template rows are readiness scaffolds, not real leads.
- A real lead requires explicit_reply_ok consent, a traceable proof note, and safe non-emergency scope.
- Raw email addresses or message bodies must not be stored in tracker CSV files.
- Matched UTM can increment KPI; unmatched UTM remains qualitative manual lead only.
- Owned assets, Luna packs, or offer experiments open only after repeated same-guardian demand.

## Closure Steps

### `capture_structured_request`

- status：`ready_to_receive`
- command：`python3 tools/promotion_lead_form_audit.py && python3 tools/promotion_lead_form_importability_audit.py`
- release：Contact / keepsake / Luna request text is structured and importable.
- stop：Do not store raw email content in CSV; copy only the structured request fields and proof note.

### `verify_consent_and_scope`

- status：`blocked_until_real_request`
- command：`python3 tools/promotion_lead_evidence_checklist.py --check`
- release：The request has explicit_reply_ok consent, reply email verified outside CSV, and safe non-emergency scope.
- stop：Do not use emergency, diagnostic, therapy-replacement, or sensitive-detail requests for marketing decisions.

### `writeback_real_lead`

- status：`blocked_until_verified_request`
- command：`python3 tools/promotion_lead_text_import.py add --input <REAL_STRUCTURED_REQUEST.txt> --proof-note "email thread checked YYYY-MM-DD"`
- release：A real non-template lead row exists with traceable proof and no raw email stored.
- stop：Do not create fake leads, inferred consent, or placeholder request rows.

### `refresh_lead_demand`

- status：`blocked_until_real_lead`
- command：`python3 tools/promotion_daily_ops_refresh.py`
- release：Lead summary, evidence checklist, demand gate, handoff, and offer quickstart reflect the real request.
- stop：Do not make lead or offer decisions from stale generated files.

### `open_asset_or_offer_route`

- status：`blocked_until_repeated_demand`
- command：`python3 tools/promotion_lead_demand_gate.py --check && python3 tools/promotion_lead_offer_quickstart.py --check`
- release：Same guardian / intake has repeated demand and a matching ready route.
- stop：Do not build paid, Luna, or affiliate experiments from one request or empty data.

## Guardian Intake Rows

### 艾莉絲 · `iris`

- template rows：3
- intake types：`owned_asset_request, luna_scene_request, repair_or_contact_request`
- routes：https://lovetypes.tw/contact/#luna-supply-request, https://lovetypes.tw/keepsakes/#keepsake-iris, https://lovetypes.tw/luna-yoga-music/#luna-iris

Writeback commands after a real verified request:

```text
python3 tools/promotion_lead_writeback.py add --source contact --guardian iris --intake-type owned_asset_request --consent-status explicit_reply_ok --proof-note "email thread iris-owned request checked 2026-06-27"
python3 tools/promotion_lead_writeback.py add --source luna_page --guardian iris --intake-type luna_scene_request --consent-status explicit_reply_ok --proof-note "email thread iris-luna request checked 2026-06-27"
```

Evidence checks per template:

- `template-iris-owned_asset_request`：9 checks
- `template-iris-luna_scene_request`：9 checks
- `template-iris-repair_or_contact_request`：9 checks

### 諾雅 · `noah`

- template rows：3
- intake types：`owned_asset_request, luna_scene_request, repair_or_contact_request`
- routes：https://lovetypes.tw/contact/#luna-supply-request, https://lovetypes.tw/keepsakes/#keepsake-noah, https://lovetypes.tw/luna-yoga-music/#luna-noah

Writeback commands after a real verified request:

```text
python3 tools/promotion_lead_writeback.py add --source contact --guardian noah --intake-type owned_asset_request --consent-status explicit_reply_ok --proof-note "email thread noah-owned request checked 2026-06-27"
python3 tools/promotion_lead_writeback.py add --source luna_page --guardian noah --intake-type luna_scene_request --consent-status explicit_reply_ok --proof-note "email thread noah-luna request checked 2026-06-27"
```

Evidence checks per template:

- `template-noah-owned_asset_request`：9 checks
- `template-noah-luna_scene_request`：9 checks
- `template-noah-repair_or_contact_request`：9 checks

### 薇薇安 · `vivian`

- template rows：3
- intake types：`owned_asset_request, luna_scene_request, repair_or_contact_request`
- routes：https://lovetypes.tw/contact/#luna-supply-request, https://lovetypes.tw/keepsakes/#keepsake-vivian, https://lovetypes.tw/luna-yoga-music/#luna-vivian

Writeback commands after a real verified request:

```text
python3 tools/promotion_lead_writeback.py add --source contact --guardian vivian --intake-type owned_asset_request --consent-status explicit_reply_ok --proof-note "email thread vivian-owned request checked 2026-06-27"
python3 tools/promotion_lead_writeback.py add --source luna_page --guardian vivian --intake-type luna_scene_request --consent-status explicit_reply_ok --proof-note "email thread vivian-luna request checked 2026-06-27"
```

Evidence checks per template:

- `template-vivian-owned_asset_request`：9 checks
- `template-vivian-luna_scene_request`：9 checks
- `template-vivian-repair_or_contact_request`：9 checks

### 克萊兒 · `claire`

- template rows：3
- intake types：`owned_asset_request, luna_scene_request, repair_or_contact_request`
- routes：https://lovetypes.tw/contact/#luna-supply-request, https://lovetypes.tw/keepsakes/#keepsake-claire, https://lovetypes.tw/luna-yoga-music/#luna-claire

Writeback commands after a real verified request:

```text
python3 tools/promotion_lead_writeback.py add --source contact --guardian claire --intake-type owned_asset_request --consent-status explicit_reply_ok --proof-note "email thread claire-owned request checked 2026-06-27"
python3 tools/promotion_lead_writeback.py add --source luna_page --guardian claire --intake-type luna_scene_request --consent-status explicit_reply_ok --proof-note "email thread claire-luna request checked 2026-06-27"
```

Evidence checks per template:

- `template-claire-owned_asset_request`：9 checks
- `template-claire-luna_scene_request`：9 checks
- `template-claire-repair_or_contact_request`：9 checks

### 朵拉 · `dora`

- template rows：3
- intake types：`owned_asset_request, luna_scene_request, repair_or_contact_request`
- routes：https://lovetypes.tw/contact/#luna-supply-request, https://lovetypes.tw/keepsakes/#keepsake-dora, https://lovetypes.tw/luna-yoga-music/#luna-dora

Writeback commands after a real verified request:

```text
python3 tools/promotion_lead_writeback.py add --source contact --guardian dora --intake-type owned_asset_request --consent-status explicit_reply_ok --proof-note "email thread dora-owned request checked 2026-06-27"
python3 tools/promotion_lead_writeback.py add --source luna_page --guardian dora --intake-type luna_scene_request --consent-status explicit_reply_ok --proof-note "email thread dora-luna request checked 2026-06-27"
```

Evidence checks per template:

- `template-dora-owned_asset_request`：9 checks
- `template-dora-luna_scene_request`：9 checks
- `template-dora-repair_or_contact_request`：9 checks
