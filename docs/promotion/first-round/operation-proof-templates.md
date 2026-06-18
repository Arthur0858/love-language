# LoveTypes Operation Proof Templates

- Generated: `2026-06-18`
- Template files: `1`
- Profile templates valid: `0`
- Post templates safely rejected until real URL: `1`
- Issues: `0`

## How To Use

- Fill profile templates only after the platform profile link is visibly set and clicked.
- Fill post templates only after the public post exists and the placeholder URL is replaced with the real HTTPS post URL.
- Run the check command before the write command.
- Keep zero metrics only when the platform or analytics source was actually checked.

## Files

### post_publish: youtube_shorts publish-lt-s01-iris-silence

- File: `docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt`
- Check: `python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt`
- Write: `python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt --proof-note "<REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified"`
- Required evidence:
  - `profile_gate_passed`
  - `public_post_url_present`
  - `post_url_is_not_placeholder`
  - `quiz_cta_preserved`
  - `utm_content_preserved`
  - `no_paid_or_affiliate_primary_cta`
  - `proof_note_present`
