#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
FIRST_BATCH_PACKET = PROMOTION_DIR / "first-batch-publication-packet.json"
OUTPUT_MD = PROMOTION_DIR / "public-post-url-checklist.md"
OUTPUT_JSON = PROMOTION_DIR / "public-post-url-checklist.json"
OUTPUT_CSV = PROMOTION_DIR / "public-post-url-checklist.csv"

PLATFORM_DOMAINS = {
    "youtube_shorts": ("youtube.com", "youtu.be"),
    "tiktok": ("tiktok.com",),
    "instagram_reels": ("instagram.com",),
}
CHECKS = [
    ("post_url_present", "公開貼文 URL 已取得", "post_url is a real https URL, not a placeholder."),
    ("platform_domain_matches", "平台網域正確", "post_url domain matches the intended publishing platform."),
    ("public_view_checked", "一般訪客可驗證", "Open the post URL logged out or from a public browser and confirm it resolves to the post."),
    ("caption_cta_checked", "Caption CTA 仍是測驗", "Published caption keeps the 15-question quiz as the first action."),
    ("tracked_url_visible", "追蹤連結或 bio 指引存在", "Published post or platform profile still leads to the planned /start/ tracked URL."),
    ("utm_content_recorded", "UTM content 已記錄", "utm_content in the tracked URL still matches the planned first-batch script."),
    ("proof_note_traceable", "Proof note 可追溯", "notes include a verified proof note with public URL, screenshot, or platform timestamp."),
    ("starter_kpi_source_checked", "初始 KPI 來源已檢查", "site_clicks, quiz_starts, and quiz_completions are from a checked source; zero is allowed only after checking."),
]


def today() -> str:
    return date.today().isoformat()


def load_packet() -> dict:
    return json.loads(FIRST_BATCH_PACKET.read_text(encoding="utf-8"))


def is_placeholder(value: str) -> bool:
    text = value.lower()
    return not value or "<real_" in text or "example.com" in text or "placeholder" in text


def domain_matches(platform: str, url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        return False
    host = parsed.netloc.lower().removeprefix("www.")
    return any(host == domain or host.endswith("." + domain) for domain in PLATFORM_DOMAINS.get(platform, ()))


def status_for(row: dict, check_id: str) -> tuple[str, str]:
    platform = str(row.get("platform", ""))
    post_url = str(row.get("postUrl", ""))
    notes = str(row.get("notes", ""))
    published = bool(row.get("published"))
    if not published:
        return "pending_publish", "等待真實公開 post_url 回填後再驗證。"
    if check_id == "post_url_present":
        ok = not is_placeholder(post_url) and urlparse(post_url).scheme == "https"
        return ("complete" if ok else "missing", post_url or "missing post_url")
    if check_id == "platform_domain_matches":
        ok = domain_matches(platform, post_url)
        return ("complete" if ok else "operator_verify", post_url or "missing post_url")
    if check_id == "public_view_checked":
        return "operator_verify", "需用公開瀏覽狀態確認貼文可見。"
    if check_id == "caption_cta_checked":
        caption = str(row.get("caption", ""))
        ok = "15 題測驗" in caption and "情感守護者" in caption
        return ("complete" if ok else "missing", "caption checked")
    if check_id == "tracked_url_visible":
        tracked = str(row.get("trackedUrl", ""))
        ok = "https://lovetypes.tw/start/" in tracked
        return ("complete" if ok else "missing", tracked or "missing tracked URL")
    if check_id == "utm_content_recorded":
        ok = bool(row.get("utmContent")) and str(row.get("utmContent")) in str(row.get("trackedUrl", ""))
        return ("complete" if ok else "missing", str(row.get("utmContent", "")) or "missing utm_content")
    if check_id == "proof_note_traceable":
        ok = "verified:" in notes
        return ("complete" if ok else "missing", notes or "missing verified proof note")
    if check_id == "starter_kpi_source_checked":
        return "operator_verify", "確認平台或網站數據來源後才回填 0 或正數。"
    return "missing", "unknown check"


def build_payload() -> dict:
    packet = load_packet()
    rows: list[dict[str, str]] = []
    for item in packet.get("rows", []):
        for check_id, label, expected in CHECKS:
            status, evidence = status_for(item, check_id)
            rows.append({
                "platform": str(item.get("platform", "")),
                "task_id": str(item.get("taskId", "")),
                "script_id": str(item.get("scriptId", "")),
                "guardian_id": str(item.get("guardianId", "")),
                "check_id": check_id,
                "check_label": label,
                "expected_value": expected,
                "post_url": str(item.get("postUrl", "")),
                "tracked_url": str(item.get("trackedUrl", "")),
                "utm_content": str(item.get("utmContent", "")),
                "published_status": "published" if item.get("published") else "pending",
                "operator_status": status,
                "evidence_note": evidence,
            })
    return {
        "generatedAt": today(),
        "source": str(FIRST_BATCH_PACKET.relative_to(ROOT)),
        "metrics": {
            "posts": len(packet.get("rows", [])),
            "checksPerPost": len(CHECKS),
            "rows": len(rows),
            "publishedPosts": sum(1 for row in packet.get("rows", []) if row.get("published")),
            "pendingPublishRows": sum(1 for row in rows if row["operator_status"] == "pending_publish"),
            "completeRows": sum(1 for row in rows if row["operator_status"] == "complete"),
            "operatorVerifyRows": sum(1 for row in rows if row["operator_status"] == "operator_verify"),
            "missingRows": sum(1 for row in rows if row["operator_status"] == "missing"),
        },
        "policy": {
            "publicUrlRequiredForWeeklyReview": True,
            "wrongPlatformUrlRequiresManualStop": True,
            "zeroKpiRequiresCheckedSource": True,
        },
        "items": rows,
    }


def validate(payload: dict) -> list[str]:
    issues: list[str] = []
    metrics = payload["metrics"]
    if metrics["posts"] != 3:
        issues.append(f"expected 3 first-batch posts, got {metrics['posts']}")
    if metrics["rows"] != metrics["posts"] * metrics["checksPerPost"]:
        issues.append("public post URL checklist row count mismatch")
    if metrics["missingRows"]:
        issues.append(f"published public post URL checks missing evidence: {metrics['missingRows']}")
    for row in payload["items"]:
        if not row["platform"] or not row["task_id"] or not row["check_id"]:
            issues.append("public post URL row missing platform, task_id, or check_id")
        if row["operator_status"] not in {"pending_publish", "complete", "operator_verify", "missing"}:
            issues.append(f"{row['platform']}/{row['task_id']}/{row['check_id']}: invalid operator_status")
    if not payload["policy"].get("publicUrlRequiredForWeeklyReview"):
        issues.append("policy must require public URLs before weekly review")
    if not payload["policy"].get("zeroKpiRequiresCheckedSource"):
        issues.append("policy must require checked source for zero KPI")
    return issues


def render_markdown(payload: dict, issues: list[str]) -> str:
    metrics = payload["metrics"]
    lines = [
        "# LoveTypes Public Post URL Checklist",
        "",
        f"- 產生日期：{payload['generatedAt']}",
        f"- first-batch posts：{metrics['posts']}",
        f"- published posts：{metrics['publishedPosts']}",
        f"- checklist rows：{metrics['rows']}",
        f"- pending publish rows：{metrics['pendingPublishRows']}",
        f"- missing rows：{metrics['missingRows']}",
        "- 用途：第一批貼文發布後，確認公開 URL、平台網域、CTA、UTM、proof note 與初始 KPI 來源。",
        "",
        "## Rule",
        "",
        "- 沒有真實公開 post_url 時，所有檢查保持 pending_publish。",
        "- post_url 必須是對應平台的公開 https URL，不能用 placeholder 或登入後才看得到的草稿頁。",
        "- site_clicks / quiz_starts / quiz_completions 可以是 0，但必須先確認數據來源真的被檢查過。",
        "",
    ]
    grouped: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in payload["items"]:
        grouped.setdefault((row["platform"], row["task_id"]), []).append(row)
    for (platform, task_id), rows in grouped.items():
        lines.extend([
            f"## {platform} · `{task_id}`",
            "",
            f"- script：`{rows[0]['script_id']}`",
            f"- guardian：`{rows[0]['guardian_id']}`",
            f"- post URL：{rows[0]['post_url'] or '(pending)'}",
            f"- tracked URL：{rows[0]['tracked_url']}",
            "",
        ])
        for row in rows:
            marker = "x" if row["operator_status"] == "complete" else " "
            lines.append(f"- [{marker}] `{row['check_id']}`：{row['check_label']}（{row['operator_status']}）")
        lines.append("")
    if issues:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in issues)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(payload: dict, issues: list[str]) -> None:
    OUTPUT_JSON.write_text(json.dumps({**payload, "issues": issues}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(payload, issues), encoding="utf-8")
    fieldnames = [
        "platform",
        "task_id",
        "script_id",
        "guardian_id",
        "check_id",
        "check_label",
        "expected_value",
        "post_url",
        "tracked_url",
        "utm_content",
        "published_status",
        "operator_status",
        "evidence_note",
    ]
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(payload["items"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a public URL verification checklist for first-batch platform posts.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    payload = build_payload()
    issues = validate(payload)
    if not args.check:
        write_outputs(payload, issues)
        print(f"promotion_public_post_url_csv={OUTPUT_CSV}")
        print(f"promotion_public_post_url_json={OUTPUT_JSON}")
        print(f"promotion_public_post_url_md={OUTPUT_MD}")
    metrics = payload["metrics"]
    print(f"promotion_public_post_url_posts={metrics['posts']}")
    print(f"promotion_public_post_url_published={metrics['publishedPosts']}")
    print(f"promotion_public_post_url_rows={metrics['rows']}")
    print(f"promotion_public_post_url_pending_publish={metrics['pendingPublishRows']}")
    print(f"promotion_public_post_url_complete={metrics['completeRows']}")
    print(f"promotion_public_post_url_operator_verify={metrics['operatorVerifyRows']}")
    print(f"promotion_public_post_url_missing={metrics['missingRows']}")
    print(f"promotion_public_post_url_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
