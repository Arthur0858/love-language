# AdSense submission gate

Run `python3 tools/adsense_submission_gate.py` before opening the AdSense review action.

The command is intentionally read-only. It never signs in, clicks the review button, or changes the evidence file. A manual gate is accepted only when `confirmed` is `true`, `checkedAt` is an ISO timestamp, and `evidence` points to a saved screenshot, export, or audit receipt. The impressions gate additionally requires `value >= minimum`.

`lastMaterialChange` must be moved forward after any material content, navigation, indexing, commercial, schema, or deployment-surface change. The 14-day stable period starts again from that date.

Do not submit unless the command returns `adsense_submission_ready=true`. After submission, set `reviewSubmitted` to `true` and retain the AdSense status screenshot separately.
