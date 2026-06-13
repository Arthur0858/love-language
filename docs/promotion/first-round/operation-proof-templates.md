# LoveTypes Operation Proof Templates

- Generated: `2026-06-14`
- Template files: `6`
- Profile templates valid: `3`
- Post templates safely rejected until real URL: `3`
- Issues: `0`

## How To Use

- Fill profile templates only after the platform profile link is visibly set and clicked.
- Fill post templates only after the public post exists and the placeholder URL is replaced with the real HTTPS post URL.
- Run the check command before the write command.
- Keep zero metrics only when the platform or analytics source was actually checked.

## Files

### profile_setup: youtube_shorts

- File: `docs/promotion/first-round/proof-youtube_shorts.txt`
- Check: `python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts.txt`
- Write: `python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts.txt --proof-note "screenshot profile-youtube_shorts-2026-06-14.png verified"`
- Required evidence:
  - `platform_account_visible`
  - `profile_link_visible_or_clickable`
  - `start_url_resolves`
  - `utm_parameters_preserved`
  - `quiz_only_copy`
  - `proof_note_present`

### profile_setup: tiktok

- File: `docs/promotion/first-round/proof-tiktok.txt`
- Check: `python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-tiktok.txt`
- Write: `python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-tiktok.txt --proof-note "screenshot profile-tiktok-2026-06-14.png verified"`
- Required evidence:
  - `platform_account_visible`
  - `profile_link_visible_or_clickable`
  - `start_url_resolves`
  - `utm_parameters_preserved`
  - `quiz_only_copy`
  - `proof_note_present`

### profile_setup: instagram_reels

- File: `docs/promotion/first-round/proof-instagram_reels.txt`
- Check: `python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-instagram_reels.txt`
- Write: `python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-instagram_reels.txt --proof-note "screenshot profile-instagram_reels-2026-06-14.png verified"`
- Required evidence:
  - `platform_account_visible`
  - `profile_link_visible_or_clickable`
  - `start_url_resolves`
  - `utm_parameters_preserved`
  - `quiz_only_copy`
  - `proof_note_present`

### post_publish: youtube_shorts publish-lt-s01-iris-silence

- File: `docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt`
- Check: `python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt`
- Write: `python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt --proof-note "public URL and analytics source checked 2026-06-14"`
- Required evidence:
  - `profile_gate_passed`
  - `public_post_url_present`
  - `post_url_is_not_placeholder`
  - `quiz_cta_preserved`
  - `utm_content_preserved`
  - `no_paid_or_affiliate_primary_cta`
  - `proof_note_present`

### post_publish: tiktok publish-lt-s01-iris-silence

- File: `docs/promotion/first-round/proof-tiktok-publish-lt-s01-iris-silence.txt`
- Check: `python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-tiktok-publish-lt-s01-iris-silence.txt`
- Write: `python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-tiktok-publish-lt-s01-iris-silence.txt --proof-note "public URL and analytics source checked 2026-06-14"`
- Required evidence:
  - `profile_gate_passed`
  - `public_post_url_present`
  - `post_url_is_not_placeholder`
  - `quiz_cta_preserved`
  - `utm_content_preserved`
  - `no_paid_or_affiliate_primary_cta`
  - `proof_note_present`

### post_publish: instagram_reels publish-lt-s01-iris-silence

- File: `docs/promotion/first-round/proof-instagram_reels-publish-lt-s01-iris-silence.txt`
- Check: `python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-instagram_reels-publish-lt-s01-iris-silence.txt`
- Write: `python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-instagram_reels-publish-lt-s01-iris-silence.txt --proof-note "public URL and analytics source checked 2026-06-14"`
- Required evidence:
  - `profile_gate_passed`
  - `public_post_url_present`
  - `post_url_is_not_placeholder`
  - `quiz_cta_preserved`
  - `utm_content_preserved`
  - `no_paid_or_affiliate_primary_cta`
  - `proof_note_present`
