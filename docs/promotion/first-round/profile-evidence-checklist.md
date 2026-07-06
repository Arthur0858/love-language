# LoveTypes Profile Evidence Checklist

- Generated: `2026-07-06`
- Platforms: `1`
- Evidence rows: `6`
- Pending rows: `6`
- Issues: `0`

## Rule

- Do not write profile `set/live` until all six checks for that platform have real evidence.
- Keep the generated `proof-<platform>.txt` file as the structured writeback input.
- Evidence value can be a screenshot filename, clicked public URL, screen recording filename, or platform-visible note.

## YouTube Shorts (`youtube_shorts`)

- Proof file: `docs/promotion/first-round/proof-youtube_shorts.txt`
- Check: `python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts.txt`
- Write: `python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts.txt --proof-note "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"`

- [ ] `platform_account_visible`：The correct platform account/profile page is visible before editing.
- [ ] `start_url_resolves`：Clicking or copying the platform link reaches https://lovetypes.tw/start/ without 404.
- [ ] `utm_parameters_preserved`：utm_source, utm_medium, utm_campaign, and utm_content are still present after platform handling.
- [ ] `profile_link_visible_or_clickable`：The platform profile, website field, description, or pinned comment visibly contains the tracked /start/ link.
- [ ] `proof_note_present`：A traceable proof note exists, such as screenshot filename, public clicked URL, or screen recording filename.
- [ ] `quiz_only_copy`：Bio/comment copy only promotes the 15-question guardian quiz; no Luna, affiliate, paid, diagnosis, or treatment promise.
