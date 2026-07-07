# LoveTypes Asset Fulfillment Dry Run

- 產生日期：2026-07-07
- dry-run mode：`1`
- synthetic real leads：1
- current real leads：0
- simulated real leads：1
- requested asset types：1
- ready after real request：1
- PDF ready：`1`
- wallpaper blocked：`1`
- short ritual blocked：`1`
- email template blocked：`1`
- commercial ready：0
- current files mutated：`0`
- issues：0

## Rule

- This dry run appends one synthetic PDF request inside a temporary directory only.
- `syntheticRealLeads` is not production demand and must not unlock the official launch or offer gates.
- One real owned-asset request may open the matching free PDF practice card.
- Wallpaper, short ritual, email template, paid assets, Luna packs, and commercial offers must remain blocked without stronger evidence.
- Current lead, asset, demand, and offer files must not mutate.

## Asset Status

- `pdf`：`ready_after_real_request`
- `wallpaper`：`blocked_until_real_request`
- `short_ritual`：`blocked_until_real_request`
- `email_template`：`blocked_until_real_request`
