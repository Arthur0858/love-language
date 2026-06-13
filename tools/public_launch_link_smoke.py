#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = "https://lovetypes.tw"
LINK_QA_PATH = ROOT / "docs" / "promotion" / "first-round" / "launch-link-qa.json"


def load_links() -> list[dict]:
    return json.loads(LINK_QA_PATH.read_text(encoding="utf-8")).get("rows", [])


def public_url(base_url: str, link: dict) -> str:
    parsed = urlparse(link["url"])
    base = urlparse(base_url)
    netloc = base.netloc or parsed.netloc
    scheme = base.scheme or parsed.scheme or "https"
    return parsed._replace(scheme=scheme, netloc=netloc).geturl()


def fetch(url: str) -> tuple[int, str, str]:
    request = Request(url, headers={"User-Agent": "LoveTypes launch link smoke/1.0", "Accept": "text/html"})
    with urlopen(request, timeout=20) as response:
        return response.status, response.geturl(), response.read().decode("utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test public LoveTypes promotion launch links.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument(
        "--source-type",
        choices=("all", "profile", "shorts"),
        default="all",
        help="Limit checks to profile Bio links or Shorts campaign links.",
    )
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/") or DEFAULT_BASE_URL
    issues: list[str] = []
    checked = 0
    profile_checked = 0
    shorts_checked = 0
    quiz_entries = 0
    safety_navs = 0
    utm_checks = 0
    for link in load_links():
        source_type = str(link.get("source_type", ""))
        if args.source_type != "all" and source_type != args.source_type:
            continue
        checked += 1
        if source_type == "profile":
            profile_checked += 1
        elif source_type == "shorts":
            shorts_checked += 1
        source = link.get("link_id", f"link-{checked}")
        url = public_url(base_url, link)
        try:
            status, final_url, html = fetch(url)
        except Exception as exc:  # noqa: BLE001
            issues.append(f"{source}: request failed: {exc}")
            continue
        if status != 200:
            issues.append(f"{source}: expected HTTP 200, got {status}")
        parsed = urlparse(final_url)
        query = parse_qs(parsed.query)
        if parsed.path != "/start/":
            issues.append(f"{source}: final path should be /start/, got {parsed.path}")
        for key in ("utm_source", "utm_medium", "utm_campaign", "utm_content"):
            utm_checks += 1
            if query.get(key, [""])[0] != link.get(key, ""):
                issues.append(f"{source}: final URL changed {key}")
        has_quiz_entry = all(marker in html for marker in ('id="quiz-section"', 'data-quiz-root', 'data-quiz-start'))
        has_quiz_copy = "15 題" in html and ("心語儀式" in html or "情感守護者" in html)
        if not has_quiz_entry or not has_quiz_copy:
            issues.append(f"{source}: landing page missing quiz start signals")
        else:
            quiz_entries += 1
        if all(marker in html for marker in ('href="/privacy/"', 'href="/terms/"', 'href="/contact/"')):
            safety_navs += 1
        else:
            issues.append(f"{source}: landing page missing trust/safety footer links")

    print(f"public_launch_link_checked={checked}")
    print(f"public_launch_link_profile_checked={profile_checked}")
    print(f"public_launch_link_shorts_checked={shorts_checked}")
    print(f"public_launch_link_quiz_entries={quiz_entries}")
    print(f"public_launch_link_safety_navs={safety_navs}")
    print(f"public_launch_link_utm_checks={utm_checks}")
    print(f"public_launch_link_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
