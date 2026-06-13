#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
PROFILE_TRACKER = PROMOTION_DIR / "platform-profile-tracker.csv"
FIRST_BATCH_PACKET = PROMOTION_DIR / "first-batch-publication-packet.json"
OUTPUT_MD = PROMOTION_DIR / "profile-post-alignment-checklist.md"
OUTPUT_JSON = PROMOTION_DIR / "profile-post-alignment-checklist.json"
OUTPUT_CSV = PROMOTION_DIR / "profile-post-alignment-checklist.csv"

CHECKS = [
    {
        "check_id": "profile_link_points_to_start",
        "phase": "profile_setup",
        "label": "Profile link points to /start/",
        "expected": "Bio/profile link uses https://lovetypes.tw/start/ with first-round profile UTM.",
    },
    {
        "check_id": "profile_utm_is_platform_specific",
        "phase": "profile_setup",
        "label": "Profile UTM is platform-specific",
        "expected": "Profile link uses utm_source for the platform and utm_medium=social_profile.",
    },
    {
        "check_id": "profile_status_configured",
        "phase": "profile_setup",
        "label": "Profile status is set/live",
        "expected": "Operator has set the live platform profile link before publishing.",
    },
    {
        "check_id": "post_link_points_to_start",
        "phase": "pre_publish",
        "label": "Post tracked URL points to /start/",
        "expected": "First-batch caption/tracked URL sends people to the quiz start route.",
    },
    {
        "check_id": "post_utm_content_preserved",
        "phase": "pre_publish",
        "label": "Post UTM content is preserved",
        "expected": "All three platform posts for this first-batch script keep the planned utm_content.",
    },
    {
        "check_id": "primary_cta_is_quiz",
        "phase": "pre_publish",
        "label": "Primary CTA stays quiz-first",
        "expected": "Primary CTA asks users to complete the 15-question quiz and find their guardian.",
    },
    {
        "check_id": "no_commerce_first_cta",
        "phase": "pre_publish",
        "label": "No commerce first CTA",
        "expected": "Caption does not make Luna, affiliate books, or paid products the first action.",
    },
    {
        "check_id": "guardian_consistent",
        "phase": "pre_publish",
        "label": "Guardian route is consistent",
        "expected": "First-batch post keeps the same guardian/script identity across platforms.",
    },
]

COMMERCE_TERMS = ("gumroad", "amazon", "博客來", "聯盟", "buy", "purchase", "購買", "下單")
QUIZ_CTA_TERMS = ("15 題測驗", "情感守護者")


def today() -> str:
    return date.today().isoformat()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def query(url: str) -> dict[str, list[str]]:
    return parse_qs(urlparse(url).query)


def path_is_start(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "https" and parsed.netloc == "lovetypes.tw" and parsed.path == "/start/"


def first_value(params: dict[str, list[str]], key: str) -> str:
    values = params.get(key) or []
    return values[0] if values else ""


def load_first_batch() -> dict:
    return json.loads(FIRST_BATCH_PACKET.read_text(encoding="utf-8"))


def row_status(profile: dict[str, str], post: dict, check_id: str, script_utm: str, script_guardian: str) -> tuple[str, str]:
    profile_url = profile.get("profile_link", "")
    post_url = str(post.get("trackedUrl", ""))
    profile_params = query(profile_url)
    post_params = query(post_url)
    platform = str(post.get("platform", ""))
    caption = str(post.get("caption", ""))
    primary_cta = str(post.get("primaryCta", ""))

    if check_id == "profile_link_points_to_start":
        ok = path_is_start(profile_url)
        return ("complete" if ok else "missing", profile_url or "missing profile link")
    if check_id == "profile_utm_is_platform_specific":
        ok = (
            first_value(profile_params, "utm_source") == profile.get("utm_source")
            and first_value(profile_params, "utm_medium") == "social_profile"
            and first_value(profile_params, "utm_content") == profile.get("utm_content")
        )
        return ("complete" if ok else "missing", profile_url or "missing profile UTM")
    if check_id == "profile_status_configured":
        ok = profile.get("status") in {"set", "live", "configured"}
        return ("complete" if ok else "pending_operator", f"{platform} status={profile.get('status', '') or 'missing'}")
    if check_id == "post_link_points_to_start":
        ok = path_is_start(post_url)
        return ("complete" if ok else "missing", post_url or "missing tracked URL")
    if check_id == "post_utm_content_preserved":
        ok = first_value(post_params, "utm_content") == script_utm == str(post.get("utmContent", ""))
        return ("complete" if ok else "missing", str(post.get("utmContent", "")) or "missing post utm_content")
    if check_id == "primary_cta_is_quiz":
        ok = all(term in primary_cta or term in caption for term in QUIZ_CTA_TERMS)
        return ("complete" if ok else "missing", primary_cta or "missing primary CTA")
    if check_id == "no_commerce_first_cta":
        first_block = "\n".join(caption.splitlines()[:4]).lower()
        ok = not any(term.lower() in first_block for term in COMMERCE_TERMS)
        return ("complete" if ok else "missing", "first caption block checked")
    if check_id == "guardian_consistent":
        ok = str(post.get("guardianId", "")) == script_guardian and str(post.get("scriptId", ""))
        return ("complete" if ok else "missing", f"{post.get('guardianId', '')}/{post.get('scriptId', '')}")
    return "missing", "unknown check"


def build_payload() -> dict:
    profiles = {row.get("platform", ""): row for row in read_csv(PROFILE_TRACKER)}
    packet = load_first_batch()
    posts = packet.get("rows", [])
    script_utms = {str(post.get("utmContent", "")) for post in posts}
    script_guardians = {str(post.get("guardianId", "")) for post in posts}
    script_utm = next(iter(script_utms), "")
    script_guardian = next(iter(script_guardians), "")
    rows: list[dict[str, str]] = []
    for post in posts:
        platform = str(post.get("platform", ""))
        profile = profiles.get(platform, {})
        for check in CHECKS:
            status, evidence = row_status(profile, post, check["check_id"], script_utm, script_guardian)
            rows.append({
                "platform": platform,
                "task_id": str(post.get("taskId", "")),
                "script_id": str(post.get("scriptId", "")),
                "guardian_id": str(post.get("guardianId", "")),
                "phase": check["phase"],
                "check_id": check["check_id"],
                "check_label": check["label"],
                "expected_value": check["expected"],
                "profile_link": profile.get("profile_link", ""),
                "tracked_url": str(post.get("trackedUrl", "")),
                "utm_content": str(post.get("utmContent", "")),
                "operator_status": status,
                "evidence_note": evidence,
            })
    return {
        "generatedAt": today(),
        "sources": {
            "profileTracker": str(PROFILE_TRACKER.relative_to(ROOT)),
            "firstBatchPacket": str(FIRST_BATCH_PACKET.relative_to(ROOT)),
        },
        "metrics": {
            "platforms": len({row["platform"] for row in rows}),
            "posts": len(posts),
            "checksPerPost": len(CHECKS),
            "rows": len(rows),
            "completeRows": sum(1 for row in rows if row["operator_status"] == "complete"),
            "pendingRows": sum(1 for row in rows if row["operator_status"] == "pending_operator"),
            "missingRows": sum(1 for row in rows if row["operator_status"] == "missing"),
            "uniquePostUtmContents": len(script_utms),
            "uniqueGuardians": len(script_guardians),
        },
        "policy": {
            "profileMustBeLiveBeforePublish": True,
            "firstBatchCta": "完成 15 題測驗，找到你的情感守護者",
            "doNotUseCommerceFirstCta": True,
        },
        "items": rows,
    }


def validate(payload: dict) -> list[str]:
    issues: list[str] = []
    metrics = payload["metrics"]
    if metrics["posts"] != 3:
        issues.append(f"expected 3 first-batch posts, got {metrics['posts']}")
    if metrics["platforms"] != 3:
        issues.append(f"expected 3 platforms, got {metrics['platforms']}")
    if metrics["rows"] != metrics["posts"] * metrics["checksPerPost"]:
        issues.append("alignment checklist row count mismatch")
    if metrics["uniquePostUtmContents"] != 1:
        issues.append("first batch posts must share one planned utm_content")
    if metrics["uniqueGuardians"] != 1:
        issues.append("first batch posts must share one guardian")
    if metrics["missingRows"] != 0:
        issues.append(f"static alignment missing rows: {metrics['missingRows']}")
    for row in payload["items"]:
        if not row["platform"] or not row["task_id"] or not row["check_id"]:
            issues.append("alignment row missing platform, task_id, or check_id")
        if row["operator_status"] not in {"complete", "pending_operator", "missing"}:
            issues.append(f"{row['platform']}/{row['check_id']}: invalid operator_status")
    if not payload["policy"].get("profileMustBeLiveBeforePublish"):
        issues.append("policy must require live profile before publishing")
    return issues


def render_markdown(payload: dict, issues: list[str]) -> str:
    metrics = payload["metrics"]
    lines = [
        "# LoveTypes Profile-to-Post Alignment Checklist",
        "",
        f"- 產生日期：{payload['generatedAt']}",
        f"- platforms：{metrics['platforms']}",
        f"- first-batch posts：{metrics['posts']}",
        f"- checklist rows：{metrics['rows']}",
        f"- complete rows：{metrics['completeRows']}",
        f"- pending operator rows：{metrics['pendingRows']}",
        f"- missing rows：{metrics['missingRows']}",
        "- 用途：發布第一批 Shorts/Reels/TikTok 前，確認平台 profile link 與貼文 CTA/UTM 對齊。",
        "",
        "## Rule",
        "",
        "- 三個平台 profile link 都必須先設為 live/configured，才進入發布。",
        "- 第一批貼文只推測驗，不把 Luna、聯盟書卷或付費商品放成第一 CTA。",
        "- `utm_content` 必須保留，否則後續 KPI 與守護者路線無法回填。",
        "",
    ]
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in payload["items"]:
        grouped.setdefault(row["platform"], []).append(row)
    for platform, rows in grouped.items():
        lines.extend([
            f"## {platform}",
            "",
            f"- task：`{rows[0]['task_id']}`",
            f"- guardian：`{rows[0]['guardian_id']}`",
            f"- profile link：{rows[0]['profile_link']}",
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
        "phase",
        "check_id",
        "check_label",
        "expected_value",
        "profile_link",
        "tracked_url",
        "utm_content",
        "operator_status",
        "evidence_note",
    ]
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(payload["items"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Check profile-link and first-batch post CTA/UTM alignment.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    payload = build_payload()
    issues = validate(payload)
    if not args.check:
        write_outputs(payload, issues)
        print(f"promotion_profile_post_alignment_csv={OUTPUT_CSV}")
        print(f"promotion_profile_post_alignment_json={OUTPUT_JSON}")
        print(f"promotion_profile_post_alignment_md={OUTPUT_MD}")
    metrics = payload["metrics"]
    print(f"promotion_profile_post_alignment_platforms={metrics['platforms']}")
    print(f"promotion_profile_post_alignment_posts={metrics['posts']}")
    print(f"promotion_profile_post_alignment_rows={metrics['rows']}")
    print(f"promotion_profile_post_alignment_complete={metrics['completeRows']}")
    print(f"promotion_profile_post_alignment_pending={metrics['pendingRows']}")
    print(f"promotion_profile_post_alignment_missing={metrics['missingRows']}")
    print(f"promotion_profile_post_alignment_unique_utm={metrics['uniquePostUtmContents']}")
    print(f"promotion_profile_post_alignment_unique_guardians={metrics['uniqueGuardians']}")
    print(f"promotion_profile_post_alignment_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
