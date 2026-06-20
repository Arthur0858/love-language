# LoveTypes First Batch KPI Checklist

- Generated: `2026-06-21`
- Tasks: `1`
- KPI rows: `7`
- Zero-source-check rows: `3`
- Pending rows: `7`
- Issues: `0`

## Rule

- Do not run weekly review until every first-batch post has post_url, site_clicks, quiz_starts, and quiz_completions.
- A zero value is acceptable only after the named source was checked.
- Keep product, Luna, affiliate, and guardian-priority decisions blocked while these rows are empty.

## youtube_shorts · `publish-lt-s01-iris-silence`

- Script: `lt-s01-iris-silence`
- Guardian: `iris`
- Proof file: `docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt`
- Check: `python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt`
- Write: `python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt --proof-note "<REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified"`

- [ ] `post_url`：Real public HTTPS post URL from the platform. Source: Published platform post page.
- [ ] `published_date`：YYYY-MM-DD date when the platform post became public. Source: Platform post timestamp or publishing dashboard.
- [ ] `proof_note`：Traceable analytics proof such as screenshot filename, platform analytics URL, report export, platform timestamp, or checked source note. Source: Public URL check, screenshot, or platform dashboard.
- [ ] `site_clicks`：Number of visits/clicks from this platform post or verified 0. Source: Cloudflare/Web analytics, platform link analytics, or tracked UTM report. Zero requires source check.
- [ ] `quiz_starts`：Number of quiz starts attributed to this post or verified 0. Source: Funnel event catalog/report, analytics event export, or manual verified source. Zero requires source check.
- [ ] `quiz_completions`：Number of quiz completions attributed to this post or verified 0. Source: Funnel event catalog/report, analytics event export, or manual verified source. Zero requires source check.
- [ ] `source_checked`：Name/date of the source checked before accepting metrics, especially zeros. Source: Operator note from the platform or analytics source check.
