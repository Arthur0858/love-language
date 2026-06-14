# LoveTypes Empty Data Safety Audit

- 產生日期：2026-06-14
- empty data mode：`1`
- fail-closed checks：14
- blocked offer rows：5
- blocked experiment rows：20
- blocked queue rows：80
- issues：0

## Rule

- No KPI and no lead evidence means collect_signal remains the only decision focus.
- Offer, Luna, affiliate, owned product, and winning-guardian decisions must fail closed.
- HOLD or blocked_by_gate rows are expected in empty data mode.
- A non-empty data signal must arrive before changing commerce emphasis.
