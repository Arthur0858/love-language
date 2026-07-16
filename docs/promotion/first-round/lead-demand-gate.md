# LoveTypes Lead Demand Gate

- 產生日期：2026-07-17
- real leads：0
- traceable evidence：0 / 0
- explicit consent：0 / 0
- repeated demand routes：0
- ready routes：0
- blockers：2
- issues：0

## Policy

- Same guardian / intake must reach at least 2 real requests.
- Every real request needs explicit reply consent and traceable proof.
- Raw email content is not stored in the tracker.
- Lead demand can prioritize free owned assets or Luna aftercare only after repeated same-guardian demand and matching offer readiness.

## Routes

### iris / owned_asset_request

- experiment：`owned_lead`
- leads：0
- repeated demand：`0`
- offer ready：`0`
- route ready：`0`
- next：Keep collecting real requests; do not create paid or priority offer from this signal yet.

### iris / luna_scene_request

- experiment：`luna_soft_offer`
- leads：0
- repeated demand：`0`
- offer ready：`0`
- route ready：`0`
- next：Keep collecting real requests; do not create paid or priority offer from this signal yet.

### iris / repair_or_contact_request

- experiment：`identity_save`
- leads：0
- repeated demand：`0`
- offer ready：`0`
- route ready：`0`
- next：Keep collecting real requests; do not create paid or priority offer from this signal yet.

### noah / owned_asset_request

- experiment：`owned_lead`
- leads：0
- repeated demand：`0`
- offer ready：`0`
- route ready：`0`
- next：Keep collecting real requests; do not create paid or priority offer from this signal yet.

### noah / luna_scene_request

- experiment：`luna_soft_offer`
- leads：0
- repeated demand：`0`
- offer ready：`0`
- route ready：`0`
- next：Keep collecting real requests; do not create paid or priority offer from this signal yet.

### noah / repair_or_contact_request

- experiment：`identity_save`
- leads：0
- repeated demand：`0`
- offer ready：`0`
- route ready：`0`
- next：Keep collecting real requests; do not create paid or priority offer from this signal yet.

### vivian / owned_asset_request

- experiment：`owned_lead`
- leads：0
- repeated demand：`0`
- offer ready：`0`
- route ready：`0`
- next：Keep collecting real requests; do not create paid or priority offer from this signal yet.

### vivian / luna_scene_request

- experiment：`luna_soft_offer`
- leads：0
- repeated demand：`0`
- offer ready：`0`
- route ready：`0`
- next：Keep collecting real requests; do not create paid or priority offer from this signal yet.

### vivian / repair_or_contact_request

- experiment：`identity_save`
- leads：0
- repeated demand：`0`
- offer ready：`0`
- route ready：`0`
- next：Keep collecting real requests; do not create paid or priority offer from this signal yet.

### claire / owned_asset_request

- experiment：`owned_lead`
- leads：0
- repeated demand：`0`
- offer ready：`0`
- route ready：`0`
- next：Keep collecting real requests; do not create paid or priority offer from this signal yet.

### claire / luna_scene_request

- experiment：`luna_soft_offer`
- leads：0
- repeated demand：`0`
- offer ready：`0`
- route ready：`0`
- next：Keep collecting real requests; do not create paid or priority offer from this signal yet.

### claire / repair_or_contact_request

- experiment：`identity_save`
- leads：0
- repeated demand：`0`
- offer ready：`0`
- route ready：`0`
- next：Keep collecting real requests; do not create paid or priority offer from this signal yet.

### dora / owned_asset_request

- experiment：`owned_lead`
- leads：0
- repeated demand：`0`
- offer ready：`0`
- route ready：`0`
- next：Keep collecting real requests; do not create paid or priority offer from this signal yet.

### dora / luna_scene_request

- experiment：`luna_soft_offer`
- leads：0
- repeated demand：`0`
- offer ready：`0`
- route ready：`0`
- next：Keep collecting real requests; do not create paid or priority offer from this signal yet.

### dora / repair_or_contact_request

- experiment：`identity_save`
- leads：0
- repeated demand：`0`
- offer ready：`0`
- route ready：`0`
- next：Keep collecting real requests; do not create paid or priority offer from this signal yet.

## Blockers

- `no_real_leads`：No real Contact / keepsake / Luna requests have been written back yet. 解除條件：Add real lead rows only after a user request with explicit reply consent arrives.
- `no_repeated_guardian_demand`：No guardian/intake pair has reached 2 real requests. 解除條件：Wait for repeated same-guardian demand before prioritizing owned assets or Luna packs.
