# LoveTypes Operator Next Action Closure Quickstart

- 產生日期：2026-07-17
- stage：`first_batch_kpi`
- active platforms：1
- profile configured：1 / 1
- ready actions：0 / 1
- first batch published：1 / 1
- minimum KPI rows：0 / 1
- proof profile template valid：0
- proof profile placeholder rows：1
- proof profile real ready rows：0
- proof post rejected：0
- profile publish ready：1
- publish KPI weekly ready：0
- active blockers：7
- issues：0

## Rules

- Active platforms only are considered for first-round promotion operations.
- Run the check command before any writeback command.
- If profile setup is complete and first batch is published, the next external action is KPI source-proof collection.
- Do not write KPI, weekly review, lead route, Luna, affiliate, or offer decisions without source-checked evidence.
- Stop immediately if account identity, permission, URL preservation, or safety copy is uncertain.

## Allowed Actions Now

### YouTube Shorts · `youtube_shorts`

- status：`complete`
- profile URL：https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
- release：platform-profile-tracker.csv row is set/live with profile_link_set_date and traceable proof note.
- stop：A real platform screenshot/click proof must exist before running the write command.

Copy block:

```text
Profile link location: Channel description / video description
Profile link: https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio

Bio:
LoveTypes Heart-Language Garden | Take the 15-question quiz to find your emotional guardian.

Pinned / first comment:
Take the 15-question quiz to find your emotional guardian: https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
Comment A/B/C and we will point you to a guardian route.
```

Proof template:

```text
LoveTypes profile setup writeback
platform: youtube_shorts
status: set
set_date: 2026-07-17
profile_link: https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
proof_note: <REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified
```

- check：`python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts.txt`
- write：`python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`

## After External Proof

- `refresh_after_profile_writeback`：`python3 tools/promotion_daily_ops_refresh.py`；expected：profileConfigured reflects active platform proof writeback.
- `check_profile_to_publish_gate`：`python3 tools/promotion_profile_completion_gate.py --check && python3 tools/promotion_profile_publish_handoff.py --check`；expected：readyToPublish opens only after active profile setup is complete.
- `keep_publish_locked_until_gate`：`python3 tools/promotion_first_batch_publish_closure_quickstart.py --check`；expected：first-batch publishing stays proof-gated until a real public post URL exists.
