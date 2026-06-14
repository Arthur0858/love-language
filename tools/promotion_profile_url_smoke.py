#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
PROFILE_SETUP_PATH = PROMOTION_DIR / "platform-profile-setup.json"
DEFAULT_OUTPUT_PATH = PROMOTION_DIR / "profile-url-smoke.md"
DEFAULT_JSON_OUTPUT_PATH = PROMOTION_DIR / "profile-url-smoke.json"
DEFAULT_CSV_OUTPUT_PATH = PROMOTION_DIR / "profile-url-smoke.csv"
EXPECTED_CAMPAIGN = "first_round_quiz_completion"
EXPECTED_MEDIUM = "social_profile"
EXPECTED_PLATFORM_SOURCES = {
    "youtube_shorts": "youtube",
    "tiktok": "tiktok",
    "instagram_reels": "instagram",
}
FIELDNAMES = [
    "platform",
    "label",
    "url",
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_content",
    "structural_status",
    "public_status",
    "final_url",
    "landing_quiz_entry",
    "landing_hero_actions",
    "landing_safety_nav",
    "notes",
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def url_parts(value: str) -> dict[str, str]:
    parsed = urlparse(value)
    query = parse_qs(parsed.query)
    return {
        "scheme": parsed.scheme,
        "netloc": parsed.netloc,
        "path": parsed.path,
        "utm_source": query.get("utm_source", [""])[0],
        "utm_medium": query.get("utm_medium", [""])[0],
        "utm_campaign": query.get("utm_campaign", [""])[0],
        "utm_content": query.get("utm_content", [""])[0],
    }


def fetch_public(url: str, timeout: int) -> tuple[str, str, str]:
    request = Request(url, headers={"User-Agent": "LoveTypes profile URL smoke/1.0", "Accept": "text/html"})
    with urlopen(request, timeout=timeout) as response:
        html = response.read().decode("utf-8", errors="replace")
        return str(response.status), response.geturl(), html


def landing_checks(html: str) -> tuple[dict[str, bool], list[str]]:
    checks = {
        "quiz_entry": all(marker in html for marker in ('id="quiz-section"', "data-quiz-root", "data-quiz-start")),
        "hero_actions": all(
            marker in html
            for marker in (
                'data-funnel-event="start_hero_quiz"',
                'data-funnel-event="start_hero_guardians"',
                'data-funnel-event="start_hero_resources"',
            )
        ),
        "safety_nav": all(marker in html for marker in ('href="/privacy/"', 'href="/terms/"', 'href="/contact/"')),
    }
    issues = []
    if not checks["quiz_entry"] or not ("15 題" in html and ("心語儀式" in html or "情感守護者" in html)):
        issues.append("public page missing quiz start signals")
    if not checks["hero_actions"]:
        issues.append("public page missing start hero action tracking")
    if not checks["safety_nav"]:
        issues.append("public page missing trust/safety footer links")
    return checks, issues


def build_rows(profile_setup: dict, public: bool, timeout: int) -> tuple[list[dict[str, str]], list[str]]:
    rows: list[dict[str, str]] = []
    issues: list[str] = []
    platforms = profile_setup.get("platforms", [])
    if len(platforms) != 3:
        issues.append(f"expected 3 profile platforms, got {len(platforms)}")

    for item in platforms:
        platform = str(item.get("platformId", "")).strip()
        label = str(item.get("label", "")).strip()
        url = str(item.get("profileLink", "")).strip()
        parts = url_parts(url)
        structural_issues: list[str] = []
        public_issues: list[str] = []
        expected_source = EXPECTED_PLATFORM_SOURCES.get(platform, "")
        if platform not in EXPECTED_PLATFORM_SOURCES:
            structural_issues.append("unknown platform")
        if parts["scheme"] != "https" or parts["netloc"] != "lovetypes.tw" or parts["path"] != "/start/":
            structural_issues.append("profile URL should point to https://lovetypes.tw/start/")
        if parts["utm_source"] != expected_source:
            structural_issues.append(f"utm_source should be {expected_source}")
        if parts["utm_medium"] != EXPECTED_MEDIUM:
            structural_issues.append(f"utm_medium should be {EXPECTED_MEDIUM}")
        if parts["utm_campaign"] != EXPECTED_CAMPAIGN:
            structural_issues.append(f"utm_campaign should be {EXPECTED_CAMPAIGN}")
        if parts["utm_content"] != f"{platform}_bio":
            structural_issues.append(f"utm_content should be {platform}_bio")

        public_status = "not_checked"
        final_url = ""
        landing_quiz_entry = ""
        landing_hero_actions = ""
        landing_safety_nav = ""
        if public and not structural_issues:
            try:
                status, final_url, html = fetch_public(url, timeout)
                final_parts = url_parts(final_url)
                if status != "200":
                    public_issues.append(f"public status should be 200, got {status}")
                if final_parts["path"] != "/start/":
                    public_issues.append(f"final path should be /start/, got {final_parts['path']}")
                for key in ("utm_source", "utm_medium", "utm_campaign", "utm_content"):
                    if final_parts[key] != parts[key]:
                        public_issues.append(f"final URL changed {key}")
                checks, landing_issues = landing_checks(html)
                landing_quiz_entry = "1" if checks["quiz_entry"] else "0"
                landing_hero_actions = "1" if checks["hero_actions"] else "0"
                landing_safety_nav = "1" if checks["safety_nav"] else "0"
                public_issues.extend(landing_issues)
                public_status = "pass" if not public_issues else "fail"
            except Exception as exc:  # noqa: BLE001
                public_issues.append(f"public request failed: {exc}")
                public_status = "fail"

        structural_status = "pass" if not structural_issues else "fail"
        row_issues = structural_issues + public_issues
        if row_issues:
            issues.extend(f"{platform}: {issue}" for issue in row_issues)

        rows.append({
            "platform": platform,
            "label": label,
            "url": url,
            "utm_source": parts["utm_source"],
            "utm_medium": parts["utm_medium"],
            "utm_campaign": parts["utm_campaign"],
            "utm_content": parts["utm_content"],
            "structural_status": structural_status,
            "public_status": public_status,
            "final_url": final_url,
            "landing_quiz_entry": landing_quiz_entry,
            "landing_hero_actions": landing_hero_actions,
            "landing_safety_nav": landing_safety_nav,
            "notes": "Destination URL smoke only. This does not prove the profile link is configured on the platform.",
        })
    return rows, issues


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def render_markdown(payload: dict) -> str:
    lines = [
        "# LoveTypes Profile URL Smoke",
        "",
        f"- 產生日期：{payload['generatedAt']}",
        f"- Profile URLs：{payload['rowCount']}",
        f"- Structural pass：{payload['structuralPass']}",
        f"- Public checked：{payload['publicChecked']}",
        f"- Public pass：{payload['publicPass']}",
        "",
        "## 邊界",
        "",
        "- 這份檢查只驗證三個平台 Bio/Profile 目標網址與 UTM 規格。",
        "- 它不代表 YouTube、TikTok、Instagram 已經完成設定；完成設定仍以 profile proof 與 tracker 回填為準。",
        "- 預設不打公開站；需要公開可達性時執行 `python3 tools/promotion_profile_url_smoke.py --public --check`。",
        "",
        "## URLs",
        "",
    ]
    for row in payload["rows"]:
        lines.extend([
            f"### {row['label'] or row['platform']}",
            "",
            f"- platform：`{row['platform']}`",
            f"- URL：{row['url']}",
            f"- utm：`{row['utm_source']}` / `{row['utm_medium']}` / `{row['utm_campaign']}` / `{row['utm_content']}`",
            f"- structural：`{row['structural_status']}`",
            f"- public：`{row['public_status']}`",
            f"- notes：{row['notes']}",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(payload: dict, output: Path, json_output: Path, csv_output: Path) -> None:
    output.write_text(render_markdown(payload), encoding="utf-8")
    json_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(payload["rows"], csv_output)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate LoveTypes profile Bio/Profile destination URLs.")
    parser.add_argument("--profile-setup", default=str(PROFILE_SETUP_PATH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--csv-output", default=str(DEFAULT_CSV_OUTPUT_PATH))
    parser.add_argument("--public", action="store_true", help="Also fetch the public landing page for each profile URL.")
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rows, issues = build_rows(read_json(Path(args.profile_setup)), public=args.public, timeout=args.timeout)
    structural_pass = sum(1 for row in rows if row["structural_status"] == "pass")
    public_checked = sum(1 for row in rows if row["public_status"] != "not_checked")
    public_pass = sum(1 for row in rows if row["public_status"] == "pass")
    landing_quiz_entries = sum(1 for row in rows if row["landing_quiz_entry"] == "1")
    landing_hero_actions = sum(1 for row in rows if row["landing_hero_actions"] == "1")
    landing_safety_navs = sum(1 for row in rows if row["landing_safety_nav"] == "1")
    payload = {
        "generatedAt": date.today().isoformat(),
        "rowCount": len(rows),
        "structuralPass": structural_pass,
        "publicChecked": public_checked,
        "publicPass": public_pass,
        "landingQuizEntries": landing_quiz_entries,
        "landingHeroActions": landing_hero_actions,
        "landingSafetyNavs": landing_safety_navs,
        "rows": rows,
        "issues": issues,
    }
    if not args.check:
        write_outputs(payload, Path(args.output), Path(args.json_output), Path(args.csv_output))

    print(f"promotion_profile_url_rows={len(rows)}")
    print(f"promotion_profile_url_structural_pass={structural_pass}")
    print(f"promotion_profile_url_public_checked={public_checked}")
    print(f"promotion_profile_url_public_pass={public_pass}")
    print(f"promotion_profile_url_landing_quiz_entries={landing_quiz_entries}")
    print(f"promotion_profile_url_landing_hero_actions={landing_hero_actions}")
    print(f"promotion_profile_url_landing_safety_navs={landing_safety_navs}")
    print(f"promotion_profile_url_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
