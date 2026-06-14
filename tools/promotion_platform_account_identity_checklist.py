#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
PROFILE_TRACKER = PROMOTION_DIR / "platform-profile-tracker.csv"
OUTPUT_MD = PROMOTION_DIR / "platform-account-identity-checklist.md"
OUTPUT_JSON = PROMOTION_DIR / "platform-account-identity-checklist.json"
OUTPUT_CSV = PROMOTION_DIR / "platform-account-identity-checklist.csv"

CHECKS = [
    ("account_identity", "visible_account_matches_lovetypes", "可見帳號是 LoveTypes 發布帳號", "平台右上角、個人頁或頻道名稱能證明正在操作 LoveTypes 相關帳號。"),
    ("account_identity", "public_profile_page_opened", "公開個人頁已開啟", "從平台公開頁確認目前帳號/頻道是即將貼 profile link 的公開頁。"),
    ("account_permission", "profile_edit_permission_visible", "可編輯 profile/bio", "畫面顯示可編輯 bio、website、description 或 channel profile。"),
    ("account_permission", "profile_link_field_located", "已找到 profile link 欄位", "操作者知道連結要貼到哪個欄位，不把追蹤連結貼到錯誤位置。"),
    ("profile_link", "planned_profile_url_ready", "平台專屬 profile URL 已備妥", "使用 platform-profile-tracker.csv 的平台專屬 /start/ UTM 連結。"),
    ("proof", "proof_capture_ready", "截圖或證據命名已準備", "設定前先準備 proof note，寫入前必須把 <REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> 換成真截圖、公開點擊或平台 URL 證據。"),
    ("publish_gate", "do_not_publish_wrong_account", "錯帳號時停止發布", "若帳號名稱、頻道、權限或公開頁不一致，不設定 profile link，也不發布貼文。"),
]


def today() -> str:
    return date.today().isoformat()


def read_profiles() -> list[dict[str, str]]:
    with PROFILE_TRACKER.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def proof_note(platform: str) -> str:
    return "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"


def build_payload() -> dict:
    profiles = read_profiles()
    rows: list[dict[str, str]] = []
    for profile in profiles:
        platform = profile.get("platform", "")
        for phase, check_id, label, expected in CHECKS:
            rows.append({
                "platform": platform,
                "label": profile.get("label", ""),
                "phase": phase,
                "check_id": check_id,
                "check_label": label,
                "expected_value": expected,
                "profile_link": profile.get("profile_link", ""),
                "profile_status": profile.get("status", ""),
                "proof_note_template": proof_note(platform),
                "operator_status": "pending",
                "evidence_value": "",
                "notes": "完成後再回填 profile-writeback；不要用本清單假設帳號已驗證。",
            })
    return {
        "generatedAt": today(),
        "source": str(PROFILE_TRACKER.relative_to(ROOT)),
        "metrics": {
            "platforms": len(profiles),
            "checksPerPlatform": len(CHECKS),
            "rows": len(rows),
            "pendingRows": sum(1 for row in rows if row["operator_status"] == "pending"),
            "configuredProfiles": sum(1 for profile in profiles if profile.get("status") in {"set", "live", "configured"}),
        },
        "policy": {
            "doNotAssumeLogin": True,
            "doNotWritebackWithoutProof": True,
            "stopOnWrongAccount": True,
            "requiredBeforePublish": True,
        },
        "items": rows,
    }


def validate(payload: dict) -> list[str]:
    issues: list[str] = []
    metrics = payload["metrics"]
    if metrics["platforms"] != 3:
        issues.append(f"expected 3 platform profiles, got {metrics['platforms']}")
    if metrics["rows"] != metrics["platforms"] * metrics["checksPerPlatform"]:
        issues.append("account identity checklist row count mismatch")
    if metrics["pendingRows"] != metrics["rows"]:
        issues.append("generated account identity checks must start pending")
    for row in payload["items"]:
        if not row["platform"] or not row["check_id"] or not row["profile_link"]:
            issues.append("identity row missing platform, check_id, or profile_link")
        if row["operator_status"] != "pending":
            issues.append(f"{row['platform']}/{row['check_id']}: generated status must be pending")
        proof_template = row["proof_note_template"]
        if "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE>" not in proof_template or "verified" not in proof_template:
            issues.append(f"{row['platform']}/{row['check_id']}: proof note template must force real proof replacement")
        if "screenshot profile-" in proof_template:
            issues.append(f"{row['platform']}/{row['check_id']}: proof note template must not look like completed scaffold proof")
    if not payload["policy"].get("stopOnWrongAccount"):
        issues.append("policy must stop publishing on wrong account")
    if not payload["policy"].get("doNotWritebackWithoutProof"):
        issues.append("policy must require proof before writeback")
    return issues


def render_markdown(payload: dict, issues: list[str]) -> str:
    metrics = payload["metrics"]
    lines = [
        "# LoveTypes Platform Account Identity Checklist",
        "",
        f"- 產生日期：{payload['generatedAt']}",
        f"- platforms：{metrics['platforms']}",
        f"- checklist rows：{metrics['rows']}",
        f"- pending rows：{metrics['pendingRows']}",
        f"- configured profiles：{metrics['configuredProfiles']}",
        "- 用途：設定 profile link 或發布第一批貼文前，先確認正在操作正確平台帳號/頻道。",
        "",
        "## Rule",
        "",
        "- 不因為瀏覽器已登入就假設帳號正確。",
        "- 看不到 LoveTypes 對應公開頁、可編輯權限或 profile link 欄位時，停止設定與發布。",
        "- 設定後要保留可追溯 proof note，再執行 profile writeback。",
        "",
    ]
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in payload["items"]:
        grouped.setdefault(row["platform"], []).append(row)
    for platform, rows in grouped.items():
        lines.extend([
            f"## {rows[0]['label']}（`{platform}`）",
            "",
            f"- planned profile link：{rows[0]['profile_link']}",
            f"- current tracker status：`{rows[0]['profile_status']}`",
            f"- proof note template：`{rows[0]['proof_note_template']}`",
            "",
        ])
        for row in rows:
            lines.append(f"- [ ] `{row['check_id']}`：{row['check_label']}，{row['expected_value']}")
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
        "label",
        "phase",
        "check_id",
        "check_label",
        "expected_value",
        "profile_link",
        "profile_status",
        "proof_note_template",
        "operator_status",
        "evidence_value",
        "notes",
    ]
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(payload["items"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an operator checklist to verify platform account identity before profile setup.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    payload = build_payload()
    issues = validate(payload)
    if not args.check:
        write_outputs(payload, issues)
        print(f"promotion_platform_account_identity_csv={OUTPUT_CSV}")
        print(f"promotion_platform_account_identity_json={OUTPUT_JSON}")
        print(f"promotion_platform_account_identity_md={OUTPUT_MD}")
    metrics = payload["metrics"]
    print(f"promotion_platform_account_identity_platforms={metrics['platforms']}")
    print(f"promotion_platform_account_identity_checks_per_platform={metrics['checksPerPlatform']}")
    print(f"promotion_platform_account_identity_rows={metrics['rows']}")
    print(f"promotion_platform_account_identity_pending={metrics['pendingRows']}")
    print(f"promotion_platform_account_identity_configured={metrics['configuredProfiles']}")
    print(f"promotion_platform_account_identity_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
