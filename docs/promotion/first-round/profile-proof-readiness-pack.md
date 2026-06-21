# LoveTypes Profile Proof Readiness Pack

- 產生日期：2026-06-22
- rows：1
- proof files：1
- importable templates：1
- placeholder proof rows：1
- real proof ready rows：0
- public ready：1
- configured：1
- ready to configure：0
- safe writeback rows：1
- profile gate ready：1
- issues：0

## Rule

- Importable proof text is not proof of setup; it only means the writeback format is valid.
- Run the write command only after the platform profile link is actually set and verified.
- Keep status planned until there is a real screenshot, public click, or platform-time proof note.
- After all active profile rows are set/live, rerun launch readiness before publishing first batch.

## Platform Proof Blocks

### YouTube Shorts（`youtube_shorts`）

- operator status：`complete`
- proof file：`docs/promotion/first-round/proof-youtube_shorts.txt`
- proof file exists：1
- template importable：1
- placeholder proof：1
- real proof ready：0
- public profile link ready：1
- profile configured：1
- evidence required：A real platform screenshot/click proof must exist before running the write command.
- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts.txt`
- write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`

Structured proof text:

```text
LoveTypes profile setup writeback
platform: youtube_shorts
status: set
set_date: 2026-06-22
profile_link: https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
proof_note: <REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified
```
