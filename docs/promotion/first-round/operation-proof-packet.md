# LoveTypes Operation Proof Packet

- Generated: `2026-06-20`
- Profile pending: `0`
- First batch pending: `1`
- Ready to publish: `1`
- Empty data mode: `0`
- Issues: `0`

## Proof Rules

- Run the check command before any write command.
- Do not write back placeholder post URLs.
- A zero metric is valid only after the platform or analytics source was checked.
- Keep the first launch CTA focused on the 15-question quiz; do not turn launch posts into paid offers.

## Proof Rows

### post_publish: youtube_shorts publish-lt-s01-iris-silence

- Status: `needs_evidence`
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
- Template:

```text
LoveTypes platform post writeback
platform: youtube_shorts
task_id: publish-lt-s01-iris-silence
status: published
published_date: 2026-06-20
post_url: <REAL_YOUTUBE_SHORTS_URL>
views: 0
site_clicks: 0
quiz_starts: 0
quiz_completions: 0
proof_note: <REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified
```
