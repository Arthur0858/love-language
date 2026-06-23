# LoveTypes Empty Data Safety Audit

- 產生日期：2026-06-24
- empty data mode：`0`
- fail-closed checks：0
- blocked offer rows：0
- blocked experiment rows：0
- blocked queue rows：0
- issues：0

## Rule

- No KPI and no lead evidence means collect_signal remains the only decision focus.
- Offer, Luna, affiliate, owned product, and winning-guardian decisions must fail closed.
- HOLD or blocked_by_gate rows are expected in empty data mode.
- A non-empty data signal must arrive before changing commerce emphasis.
