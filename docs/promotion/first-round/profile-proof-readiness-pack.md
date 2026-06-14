# LoveTypes Profile Proof Readiness Pack

- 產生日期：2026-06-14
- rows：3
- proof files：3
- importable templates：3
- placeholder proof rows：3
- real proof ready rows：0
- public ready：3
- configured：0
- ready to configure：3
- safe writeback rows：0
- profile gate ready：0
- issues：0

## Rule

- Importable proof text is not proof of setup; it only means the writeback format is valid.
- Run the write command only after the platform profile link is actually set and verified.
- Keep status planned until there is a real screenshot, public click, or platform-time proof note.
- After all three profile rows are set/live, rerun launch readiness before publishing first batch.

## Platform Proof Blocks

### YouTube Shorts（`youtube_shorts`）

- operator status：`ready_to_configure`
- proof file：`docs/promotion/first-round/proof-youtube_shorts.txt`
- proof file exists：1
- template importable：1
- placeholder proof：1
- real proof ready：0
- public profile link ready：1
- profile configured：0
- evidence required：A real platform screenshot/click proof must exist before running the write command.
- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts.txt`
- write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`

Structured proof text:

```text
LoveTypes profile setup writeback
platform: youtube_shorts
status: set
set_date: 2026-06-14
profile_link: https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
proof_note: <REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified
```

### TikTok（`tiktok`）

- operator status：`ready_to_configure`
- proof file：`docs/promotion/first-round/proof-tiktok.txt`
- proof file exists：1
- template importable：1
- placeholder proof：1
- real proof ready：0
- public profile link ready：1
- profile configured：0
- evidence required：A real platform screenshot/click proof must exist before running the write command.
- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-tiktok.txt`
- write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-tiktok.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`

Structured proof text:

```text
LoveTypes profile setup writeback
platform: tiktok
status: set
set_date: 2026-06-14
profile_link: https://lovetypes.tw/start/?utm_source=tiktok&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=tiktok_bio
proof_note: <REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified
```

### Instagram Reels（`instagram_reels`）

- operator status：`ready_to_configure`
- proof file：`docs/promotion/first-round/proof-instagram_reels.txt`
- proof file exists：1
- template importable：1
- placeholder proof：1
- real proof ready：0
- public profile link ready：1
- profile configured：0
- evidence required：A real platform screenshot/click proof must exist before running the write command.
- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-instagram_reels.txt`
- write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-instagram_reels.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`

Structured proof text:

```text
LoveTypes profile setup writeback
platform: instagram_reels
status: set
set_date: 2026-06-14
profile_link: https://lovetypes.tw/start/?utm_source=instagram&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=instagram_reels_bio
proof_note: <REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified
```
