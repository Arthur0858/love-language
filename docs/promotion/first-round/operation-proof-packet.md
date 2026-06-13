# LoveTypes Operation Proof Packet

- Generated: `2026-06-14`
- Profile pending: `3`
- First batch pending: `3`
- Ready to publish: `0`
- Empty data mode: `1`
- Issues: `0`

## Proof Rules

- Run the check command before any write command.
- Do not write back placeholder post URLs.
- A zero metric is valid only after the platform or analytics source was checked.
- Keep the first launch CTA focused on the 15-question quiz; do not turn launch posts into paid offers.

## Proof Rows

### profile_setup: youtube_shorts

- Status: `needs_evidence`
- Check: `python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts.txt`
- Write: `python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts.txt --proof-note "screenshot profile-youtube_shorts-2026-06-14.png verified"`
- Required evidence:
  - `platform_account_visible`
  - `profile_link_visible_or_clickable`
  - `start_url_resolves`
  - `utm_parameters_preserved`
  - `quiz_only_copy`
  - `proof_note_present`
- Template:

```text
LoveTypes profile setup writeback
platform: youtube_shorts
status: set
set_date: 2026-06-14
profile_link: https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
proof_note: screenshot profile-platform-YYYY-MM-DD.png saved
```

### profile_setup: tiktok

- Status: `needs_evidence`
- Check: `python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-tiktok.txt`
- Write: `python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-tiktok.txt --proof-note "screenshot profile-tiktok-2026-06-14.png verified"`
- Required evidence:
  - `platform_account_visible`
  - `profile_link_visible_or_clickable`
  - `start_url_resolves`
  - `utm_parameters_preserved`
  - `quiz_only_copy`
  - `proof_note_present`
- Template:

```text
LoveTypes profile setup writeback
platform: tiktok
status: set
set_date: 2026-06-14
profile_link: https://lovetypes.tw/start/?utm_source=tiktok&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=tiktok_bio
proof_note: screenshot profile-platform-YYYY-MM-DD.png saved
```

### profile_setup: instagram_reels

- Status: `needs_evidence`
- Check: `python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-instagram_reels.txt`
- Write: `python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-instagram_reels.txt --proof-note "screenshot profile-instagram_reels-2026-06-14.png verified"`
- Required evidence:
  - `platform_account_visible`
  - `profile_link_visible_or_clickable`
  - `start_url_resolves`
  - `utm_parameters_preserved`
  - `quiz_only_copy`
  - `proof_note_present`
- Template:

```text
LoveTypes profile setup writeback
platform: instagram_reels
status: set
set_date: 2026-06-14
profile_link: https://lovetypes.tw/start/?utm_source=instagram&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=instagram_reels_bio
proof_note: screenshot profile-platform-YYYY-MM-DD.png saved
```

### post_publish: youtube_shorts publish-lt-s01-iris-silence

- Status: `blocked_until_profile_gate`
- Check: `python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt`
- Write: `python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt --proof-note "public URL post checked 2026-06-14"`
- Blocked by: `profile links are not all set/live`
- Required evidence:
  - `profile_gate_passed`
  - `public_post_url_present`
  - `post_url_is_not_placeholder`
  - `quiz_cta_preserved`
  - `utm_content_preserved`
  - `no_paid_or_affiliate_primary_cta`
  - `proof_note_present`
- Template:

```text
LoveTypes platform post writeback
platform: youtube_shorts
task_id: publish-lt-s01-iris-silence
status: published
published_date: 2026-06-14
post_url: <REAL_YOUTUBE_SHORTS_URL>
views: 0
site_clicks: 0
quiz_starts: 0
quiz_completions: 0
proof_note: public URL post checked YYYY-MM-DD
```

### post_publish: tiktok publish-lt-s01-iris-silence

- Status: `blocked_until_profile_gate`
- Check: `python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-tiktok-publish-lt-s01-iris-silence.txt`
- Write: `python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-tiktok-publish-lt-s01-iris-silence.txt --proof-note "public URL post checked 2026-06-14"`
- Blocked by: `profile links are not all set/live`
- Required evidence:
  - `profile_gate_passed`
  - `public_post_url_present`
  - `post_url_is_not_placeholder`
  - `quiz_cta_preserved`
  - `utm_content_preserved`
  - `no_paid_or_affiliate_primary_cta`
  - `proof_note_present`
- Template:

```text
LoveTypes platform post writeback
platform: tiktok
task_id: publish-lt-s01-iris-silence
status: published
published_date: 2026-06-14
post_url: <REAL_TIKTOK_VIDEO_URL>
views: 0
site_clicks: 0
quiz_starts: 0
quiz_completions: 0
proof_note: public URL post checked YYYY-MM-DD
```

### post_publish: instagram_reels publish-lt-s01-iris-silence

- Status: `blocked_until_profile_gate`
- Check: `python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-instagram_reels-publish-lt-s01-iris-silence.txt`
- Write: `python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-instagram_reels-publish-lt-s01-iris-silence.txt --proof-note "public URL post checked 2026-06-14"`
- Blocked by: `profile links are not all set/live`
- Required evidence:
  - `profile_gate_passed`
  - `public_post_url_present`
  - `post_url_is_not_placeholder`
  - `quiz_cta_preserved`
  - `utm_content_preserved`
  - `no_paid_or_affiliate_primary_cta`
  - `proof_note_present`
- Template:

```text
LoveTypes platform post writeback
platform: instagram_reels
task_id: publish-lt-s01-iris-silence
status: published
published_date: 2026-06-14
post_url: <REAL_INSTAGRAM_REEL_URL>
views: 0
site_clicks: 0
quiz_starts: 0
quiz_completions: 0
proof_note: public URL post checked YYYY-MM-DD
```
