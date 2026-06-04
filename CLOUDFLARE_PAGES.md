# LoveTypes Cloudflare Pages Deployment

LoveTypes is deployed as a static Cloudflare Pages project.

## Current Setup

- Production domain: `https://lovetypes.tw/`
- Pages project: `lovetypes`
- Account id: `e6780ef96bb6f53eba1dbc4d6dfa7376`
- Default branch label: `main`
- Token file: `~/.config/lovetypes/cloudflare-pages.token`

Do not commit the token file. The deploy script reads it locally, or reads
`CLOUDFLARE_API_TOKEN` when that environment variable is set.

## Deploy Flow

Run quality checks first:

```bash
python3 tools/predeploy_check.py
```

Dry-run the Cloudflare manifest and remote hash check:

```bash
python3 tools/deploy_cloudflare_pages.py --dry-run
```

Deploy and verify the preview URL:

```bash
python3 tools/deploy_cloudflare_pages.py
```

Deploy and also verify the live domain:

```bash
python3 tools/deploy_cloudflare_pages.py --verify-alias https://lovetypes.tw
```

After deployment, run the public smoke test:

```bash
python3 tools/public_deploy_smoke.py
```

Then run the full sitemap public smoke test:

```bash
python3 tools/public_sitemap_smoke.py
```

Generate a local health summary:

```bash
python3 tools/site_health_summary.py
```

The summary is written to `output/site-health.md`. It is local evidence for the
current machine and is intentionally not committed or deployed.

GitHub Actions also runs the structural and browser smoke checks on pull
requests. On pushes to `main`, it additionally runs the production public smoke
and full sitemap smoke checks, then uploads those logs as workflow evidence.

## Deployment Scope

The deploy script uploads only public static site output. It excludes local
source, tooling, evidence, and repository metadata:

- `.git/`, `.github/`, `.wrangler/`, `node_modules/`, `output/`, `tools/`
- hidden files such as `.DS_Store`
- Markdown docs, Python tools, local Playwright screenshots, and source maps
- `CNAME`, `_headers`, `_redirects`, `_routes.json`, `_worker.js` from the
  normal asset manifest

`_headers` and `_redirects` are still attached separately to the Pages
deployment when present.

## Required Proof

A production deploy is not considered verified until all of these are true:

- `python3 tools/predeploy_check.py` returns `predeploy_checks=ok`.
- `python3 tools/deploy_cloudflare_pages.py --dry-run` can collect the
  manifest and query missing hashes.
- The real deploy reaches a Cloudflare deployment stage of `deploy success`.
- `python3 tools/public_deploy_smoke.py` returns `public_deploy_issues=0`.
- `python3 tools/public_sitemap_smoke.py` returns `public_sitemap_issues=0`.
- `python3 tools/site_health_summary.py` returns `site_health_status=ok`.
- The `LoveTypes predeploy check` GitHub workflow for the pushed commit shows
  `completed/success`, including the production public smoke steps on `main`.
- `git status --short --branch` shows `main...origin/main` with no local
  changes after the intended commit has been pushed.
