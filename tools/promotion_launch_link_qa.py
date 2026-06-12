#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
POSTING_QUEUE_PATH = PROMOTION_DIR / "posting-queue.csv"
PROFILE_SETUP_PATH = PROMOTION_DIR / "platform-profile-setup.json"
DEFAULT_OUTPUT_PATH = PROMOTION_DIR / "launch-link-qa.md"
DEFAULT_JSON_OUTPUT_PATH = PROMOTION_DIR / "launch-link-qa.json"
DEFAULT_CSV_OUTPUT_PATH = PROMOTION_DIR / "launch-link-qa.csv"
EXPECTED_CAMPAIGN = "first_round_quiz_completion"
FIELDNAMES = [
    "link_id",
    "source_type",
    "platform",
    "task_id",
    "script_id",
    "guardian_id",
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_content",
    "url",
    "expected_path",
    "status",
    "notes",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


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


def row_for_url(source_type: str, platform: str, task_id: str, script_id: str, guardian_id: str, url: str, notes: str) -> dict[str, str]:
    parts = url_parts(url)
    return {
        "link_id": f"{source_type}:{platform}:{parts['utm_content'] or task_id or script_id}",
        "source_type": source_type,
        "platform": platform,
        "task_id": task_id,
        "script_id": script_id,
        "guardian_id": guardian_id,
        "utm_source": parts["utm_source"],
        "utm_medium": parts["utm_medium"],
        "utm_campaign": parts["utm_campaign"],
        "utm_content": parts["utm_content"],
        "url": url,
        "expected_path": "/start/",
        "status": "ready_to_test",
        "notes": notes,
    }


def build_rows(posting_rows: list[dict[str, str]], profile_setup: dict) -> list[dict[str, str]]:
    seen_urls: set[str] = set()
    rows: list[dict[str, str]] = []
    for item in profile_setup.get("platforms", []):
        url = str(item.get("profileLink", ""))
        if url in seen_urls:
            continue
        seen_urls.add(url)
        rows.append(row_for_url(
            "profile",
            str(item.get("platformId", "")),
            f"profile-{item.get('platformId', '')}",
            "",
            "",
            url,
            "Bio/Profile link before first post.",
        ))
    for item in posting_rows:
        url = str(item.get("tracked_url", ""))
        if url in seen_urls:
            continue
        seen_urls.add(url)
        rows.append(row_for_url(
            "shorts",
            "all",
            str(item.get("task_id", "")),
            str(item.get("script_id", "")),
            str(item.get("guardian_id", "")),
            url,
            "Unique Shorts campaign link shared across platforms for this script.",
        ))
    rows.sort(key=lambda row: (row["source_type"], row["guardian_id"], row["utm_content"], row["platform"]))
    return rows


def validate_rows(rows: list[dict[str, str]]) -> list[str]:
    issues: list[str] = []
    if len(rows) != 18:
        issues.append(f"expected 18 unique launch links, got {len(rows)}")
    counts = Counter(row["source_type"] for row in rows)
    if counts.get("profile") != 3:
        issues.append(f"expected 3 profile links, got {counts.get('profile', 0)}")
    if counts.get("shorts") != 15:
        issues.append(f"expected 15 shorts links, got {counts.get('shorts', 0)}")
    seen_ids: set[str] = set()
    for row in rows:
        label = row.get("link_id", "<link>")
        if label in seen_ids:
            issues.append(f"{label}: duplicate link_id")
        seen_ids.add(label)
        parsed = urlparse(row.get("url", ""))
        if parsed.scheme != "https" or parsed.netloc != "lovetypes.tw" or parsed.path != "/start/":
            issues.append(f"{label}: URL should point to https://lovetypes.tw/start/")
        if row.get("utm_campaign") != EXPECTED_CAMPAIGN:
            issues.append(f"{label}: utm_campaign should be {EXPECTED_CAMPAIGN}")
        if row["source_type"] == "profile" and row.get("utm_medium") != "social_profile":
            issues.append(f"{label}: profile links should use utm_medium=social_profile")
        if row["source_type"] == "shorts" and row.get("utm_medium") != "social":
            issues.append(f"{label}: shorts links should use utm_medium=social")
        if not row.get("utm_source") or not row.get("utm_content"):
            issues.append(f"{label}: missing utm_source or utm_content")
    return issues


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def render_markdown(payload: dict) -> str:
    lines = [
        "# LoveTypes Launch Link QA",
        "",
        f"- 產生日期：{payload['generatedAt']}",
        f"- 唯一追蹤連結：{payload['rowCount']}",
        f"- Profile links：{payload['profileLinks']}",
        f"- Shorts links：{payload['shortsLinks']}",
        "",
        "## 使用方式",
        "",
        "- 發布前先確認這些連結都保留 UTM，且都導向 `/start/` 測驗入口。",
        "- Shorts 三平台共用同一支腳本的 `utm_content`；平台來源由貼文平台與回填表判讀。",
        "- Bio/Profile links 使用平台專屬 `utm_source` 與 `utm_medium=social_profile`。",
        "",
        "## Links",
        "",
    ]
    for row in payload["rows"]:
        lines.extend([
            f"### {row['link_id']}",
            "",
            f"- type：`{row['source_type']}`",
            f"- platform：`{row['platform']}`",
            f"- guardian：`{row['guardian_id']}`",
            f"- utm：`{row['utm_source']}` / `{row['utm_medium']}` / `{row['utm_campaign']}` / `{row['utm_content']}`",
            f"- URL：{row['url']}",
            f"- status：`{row['status']}`",
            f"- notes：{row['notes']}",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(payload: dict, output: Path, json_output: Path, csv_output: Path) -> None:
    output.write_text(render_markdown(payload), encoding="utf-8")
    json_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(payload["rows"], csv_output)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build LoveTypes launch link QA list for first-round promotion.")
    parser.add_argument("--posting-queue", default=str(POSTING_QUEUE_PATH))
    parser.add_argument("--profile-setup", default=str(PROFILE_SETUP_PATH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--csv-output", default=str(DEFAULT_CSV_OUTPUT_PATH))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rows = build_rows(read_csv(Path(args.posting_queue)), read_json(Path(args.profile_setup)))
    issues = validate_rows(rows)
    payload = {
        "generatedAt": date.today().isoformat(),
        "source": {
            "postingQueue": str(POSTING_QUEUE_PATH.relative_to(ROOT)),
            "profileSetup": str(PROFILE_SETUP_PATH.relative_to(ROOT)),
        },
        "rowCount": len(rows),
        "profileLinks": sum(1 for row in rows if row["source_type"] == "profile"),
        "shortsLinks": sum(1 for row in rows if row["source_type"] == "shorts"),
        "rows": rows,
        "issues": issues,
    }
    if not args.check:
        write_outputs(payload, Path(args.output), Path(args.json_output), Path(args.csv_output))
        print(f"promotion_launch_link_qa={args.output}")
        print(f"promotion_launch_link_qa_json={args.json_output}")
        print(f"promotion_launch_link_qa_csv={args.csv_output}")
    print(f"promotion_launch_link_rows={payload['rowCount']}")
    print(f"promotion_launch_link_profile={payload['profileLinks']}")
    print(f"promotion_launch_link_shorts={payload['shortsLinks']}")
    print(f"promotion_launch_link_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
