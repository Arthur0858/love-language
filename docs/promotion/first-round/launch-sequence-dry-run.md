# LoveTypes Launch Sequence Dry Run

- 產生日期：2026-07-18
- initial ready to publish：`1`
- initial stage：`kpi_backfill`
- profile imports：1
- profile batch ready：1
- profile configured：1
- profile ready to publish：`1`
- profile stage：`kpi_backfill`
- profile gate ready：`1`
- post imports：1
- post batch ready：1
- first batch published：1
- minimum KPI rows：1
- post stage：`weekly_evidence`
- traceable / required evidence：2 / 2
- publishing ready：`1`
- weekly ready：`1`
- current files mutated：`0`
- issues：0

## Rule

- This is a temporary-directory dry run; current promotion CSV files must not mutate.
- Profile proof batch import must open the profile gate before first-batch post imports.
- Post proof batch import must produce active-platform published rows, minimum KPI rows, and traceable evidence.
- Blocker stage must not regress; after a real public post it may hold at kpi_backfill until source-checked KPI data exists.
- Weekly decision can open only after the simulated post URL and KPI evidence path is complete.
