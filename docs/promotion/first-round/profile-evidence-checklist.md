# LoveTypes Profile Evidence Checklist

- Generated: `2026-06-14`
- Platforms: `3`
- Evidence rows: `18`
- Pending rows: `18`
- Issues: `0`

## Rule

- Do not write profile `set/live` until all six checks for that platform have real evidence.
- Keep the generated `proof-<platform>.txt` file as the structured writeback input.
- Evidence value can be a screenshot filename, clicked public URL, screen recording filename, or platform-visible note.

## YouTube Shorts (`youtube_shorts`)

- Proof file: `docs/promotion/first-round/proof-youtube_shorts.txt`
- Check: `python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts.txt`
- Write: `python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts.txt --proof-note "screenshot profile-youtube_shorts-2026-06-14.png verified"`

- [ ] `platform_account_visible`：The correct platform account/profile page is visible before editing.
- [ ] `profile_link_visible_or_clickable`：The platform profile, website field, description, or pinned comment visibly contains the tracked /start/ link.
- [ ] `start_url_resolves`：Clicking or copying the platform link reaches https://lovetypes.tw/start/ without 404.
- [ ] `utm_parameters_preserved`：utm_source, utm_medium, utm_campaign, and utm_content are still present after platform handling.
- [ ] `quiz_only_copy`：Bio/comment copy only promotes the 15-question guardian quiz; no Luna, affiliate, paid, diagnosis, or treatment promise.
- [ ] `proof_note_present`：A traceable proof note exists, such as screenshot filename, public clicked URL, or screen recording filename.

## TikTok (`tiktok`)

- Proof file: `docs/promotion/first-round/proof-tiktok.txt`
- Check: `python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-tiktok.txt`
- Write: `python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-tiktok.txt --proof-note "screenshot profile-tiktok-2026-06-14.png verified"`

- [ ] `platform_account_visible`：The correct platform account/profile page is visible before editing.
- [ ] `profile_link_visible_or_clickable`：The platform profile, website field, description, or pinned comment visibly contains the tracked /start/ link.
- [ ] `start_url_resolves`：Clicking or copying the platform link reaches https://lovetypes.tw/start/ without 404.
- [ ] `utm_parameters_preserved`：utm_source, utm_medium, utm_campaign, and utm_content are still present after platform handling.
- [ ] `quiz_only_copy`：Bio/comment copy only promotes the 15-question guardian quiz; no Luna, affiliate, paid, diagnosis, or treatment promise.
- [ ] `proof_note_present`：A traceable proof note exists, such as screenshot filename, public clicked URL, or screen recording filename.

## Instagram Reels (`instagram_reels`)

- Proof file: `docs/promotion/first-round/proof-instagram_reels.txt`
- Check: `python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-instagram_reels.txt`
- Write: `python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-instagram_reels.txt --proof-note "screenshot profile-instagram_reels-2026-06-14.png verified"`

- [ ] `platform_account_visible`：The correct platform account/profile page is visible before editing.
- [ ] `profile_link_visible_or_clickable`：The platform profile, website field, description, or pinned comment visibly contains the tracked /start/ link.
- [ ] `start_url_resolves`：Clicking or copying the platform link reaches https://lovetypes.tw/start/ without 404.
- [ ] `utm_parameters_preserved`：utm_source, utm_medium, utm_campaign, and utm_content are still present after platform handling.
- [ ] `quiz_only_copy`：Bio/comment copy only promotes the 15-question guardian quiz; no Luna, affiliate, paid, diagnosis, or treatment promise.
- [ ] `proof_note_present`：A traceable proof note exists, such as screenshot filename, public clicked URL, or screen recording filename.
