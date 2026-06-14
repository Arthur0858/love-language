# LoveTypes Launch Sequence Dry Run

- 產生日期：2026-06-14
- initial ready to publish：`0`
- initial stage：`profile_setup`
- profile imports：3
- profile configured：3
- profile ready to publish：`1`
- profile stage：`first_batch_publish`
- profile gate ready：`1`
- post imports：3
- first batch published：3
- minimum KPI rows：3
- post stage：`weekly_evidence`
- traceable / required evidence：6 / 6
- publishing ready：`1`
- weekly ready：`1`
- current files mutated：`0`
- issues：0

## Rule

- This is a temporary-directory dry run; current promotion CSV files must not mutate.
- Profile proof imports must open the profile gate before first-batch post imports.
- Post proof imports must produce three published rows, three minimum KPI rows, and traceable evidence.
- Blocker stage must move from profile_setup to first_batch_publish, then hold at weekly_evidence until real weekly review data exists.
- Weekly decision can open only after the simulated post URL and KPI evidence path is complete.
