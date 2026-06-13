#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date
from pathlib import Path

from promotion_proof_note_policy import proof_note_issue


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
LEAD_TRACKER = PROMOTION_DIR / "lead-intake-tracker.csv"
ATTRIBUTION_PATH = PROMOTION_DIR / "attribution-reconciliation.csv"
KPI_TRACKER = PROMOTION_DIR / "kpi-tracker.csv"
PROFILE_TRACKER = PROMOTION_DIR / "platform-profile-tracker.csv"
PLAYBOOK_MD = PROMOTION_DIR / "lead-writeback-playbook.md"
PLAYBOOK_JSON = PROMOTION_DIR / "lead-writeback-playbook.json"
GUARDIANS = {
    "iris": "艾莉絲",
    "noah": "諾雅",
    "vivian": "薇薇安",
    "claire": "克萊兒",
    "dora": "朵拉",
}
SOURCE_OPTIONS = {
    "contact",
    "keepsake_waitlist",
    "resources_wishlist",
    "luna_page",
    "manual_reply",
}
INTAKE_TO_KPI = {
    "owned_asset_request": "supply_lead_requests",
    "luna_scene_request": "luna_pack_clicks",
    "repair_or_contact_request": "contact_requests",
}
INTAKE_DEFAULT_ASSET = {
    "owned_asset_request": "guardian PDF / wallpaper / short ritual",
    "luna_scene_request": "Luna bedtime / conflict cooldown / quiz aftercare pack",
    "repair_or_contact_request": "relationship repair prompt / supply route guidance",
}
CONSENT_STATUSES = {"explicit_reply_ok", "do_not_contact"}
REAL_STATUSES = {"new", "triaged", "queued", "fulfilled", "closed"}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_int(value: str | None) -> int:
    text = (value or "").strip().replace(",", "")
    if not text:
        return 0
    return int(float(text))


def today() -> str:
    return date.today().isoformat()


def validate_date(value: str) -> bool:
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return False
    return parsed <= date.today()


def next_request_id(rows: list[dict[str, str]], request_date: str, guardian: str, intake_type: str) -> str:
    prefix = f"{request_date}-{guardian}-{intake_type}"
    count = sum(1 for row in rows if (row.get("request_id") or "").startswith(prefix))
    return f"{prefix}-{count + 1:03d}"


def load_attribution() -> dict[str, dict[str, str]]:
    _, rows = read_csv(ATTRIBUTION_PATH)
    return {
        (row.get("utm_content") or "").strip(): row
        for row in rows
        if (row.get("utm_content") or "").strip()
    }


def increment_field(path: Path, key_field: str, key_value: str, field: str) -> bool:
    fieldnames, rows = read_csv(path)
    changed = False
    if field not in fieldnames:
        return False
    for row in rows:
        if (row.get(key_field) or "").strip() == key_value:
            row[field] = str(parse_int(row.get(field)) + 1)
            changed = True
            break
    if changed:
        write_csv(path, fieldnames, rows)
    return changed


def related_route(guardian: str, intake_type: str) -> str:
    if intake_type == "owned_asset_request":
        return f"https://lovetypes.tw/keepsakes/#keepsake-{guardian}"
    if intake_type == "luna_scene_request":
        return f"https://lovetypes.tw/luna-yoga-music/#luna-{guardian}"
    return "https://lovetypes.tw/contact/#luna-supply-request"


def validate_tracker(fieldnames: list[str], rows: list[dict[str, str]]) -> list[str]:
    issues: list[str] = []
    required = {
        "request_id",
        "date",
        "source",
        "utm_content",
        "guardian_id",
        "guardian_name",
        "intake_type",
        "requested_asset",
        "related_route",
        "kpi_writeback_field",
        "email_status",
        "consent_status",
        "priority",
        "status",
        "notes",
    }
    missing = sorted(required - set(fieldnames))
    if missing:
        issues.append("lead tracker missing fields: " + ", ".join(missing))
    seen: set[str] = set()
    real_rows = 0
    for row in rows:
        request_id = (row.get("request_id") or "").strip()
        if not request_id:
            issues.append("lead row missing request_id")
            continue
        if request_id in seen:
            issues.append(f"{request_id}: duplicate request_id")
        seen.add(request_id)
        status = row.get("status", "")
        source = row.get("source", "")
        intake = row.get("intake_type", "")
        guardian = row.get("guardian_id", "")
        if status == "template":
            if source != "template":
                issues.append(f"{request_id}: template row source must be template")
            if row.get("email_status") != "not_received":
                issues.append(f"{request_id}: template row must not imply received email")
            continue
        real_rows += 1
        if source not in SOURCE_OPTIONS:
            issues.append(f"{request_id}: invalid real source {source}")
        if guardian not in GUARDIANS:
            issues.append(f"{request_id}: invalid guardian {guardian}")
        if intake not in INTAKE_TO_KPI:
            issues.append(f"{request_id}: invalid intake_type {intake}")
        elif row.get("kpi_writeback_field") != INTAKE_TO_KPI[intake]:
            issues.append(f"{request_id}: kpi_writeback_field should be {INTAKE_TO_KPI[intake]}")
        if not row.get("date"):
            issues.append(f"{request_id}: real lead requires date")
        elif not validate_date(row.get("date", "")):
            issues.append(f"{request_id}: real lead date must be YYYY-MM-DD and not in the future")
        if row.get("consent_status") not in CONSENT_STATUSES:
            issues.append(f"{request_id}: real lead requires explicit consent or do_not_contact")
        if row.get("email_status") not in {"received", "replied", "fulfilled", "closed"}:
            issues.append(f"{request_id}: real lead requires received/replied/fulfilled/closed email_status")
        if status not in REAL_STATUSES:
            issues.append(f"{request_id}: invalid real status {status}")
        if "verified:" not in (row.get("notes") or ""):
            issues.append(f"{request_id}: real lead requires verified proof note")
    if real_rows == 0 and any(row.get("source") != "template" for row in rows):
        issues.append("non-template lead rows were expected to count as real rows")
    return issues


def build_row(args: argparse.Namespace, existing_rows: list[dict[str, str]]) -> dict[str, str]:
    request_date = args.request_date or today()
    if not validate_date(request_date):
        raise SystemExit("real lead writeback requires --request-date YYYY-MM-DD and not in the future")
    request_id = args.request_id or next_request_id(existing_rows, request_date, args.guardian, args.intake_type)
    kpi_field = INTAKE_TO_KPI[args.intake_type]
    proof = args.proof_note.strip()
    if not proof:
        raise SystemExit("real lead writeback requires --proof-note")
    issue = proof_note_issue(proof)
    if issue:
        raise SystemExit(issue)
    if args.consent_status != "explicit_reply_ok":
        raise SystemExit("lead writeback requires explicit_reply_ok consent; use manual notes only for do_not_contact")
    return {
        "request_id": request_id,
        "date": request_date,
        "source": args.source,
        "utm_content": args.utm_content,
        "contact_campaign_content": args.utm_content,
        "guardian_id": args.guardian,
        "guardian_name": GUARDIANS[args.guardian],
        "intake_type": args.intake_type,
        "requested_asset": args.requested_asset or INTAKE_DEFAULT_ASSET[args.intake_type],
        "related_route": related_route(args.guardian, args.intake_type),
        "kpi_writeback_field": kpi_field,
        "kpi_writeback_rule": "If utm_content matches attribution-reconciliation.csv, increment this field; otherwise manual lead only.",
        "email_status": "received",
        "consent_status": args.consent_status,
        "priority": "high" if args.intake_type == "repair_or_contact_request" else "medium",
        "status": "new",
        "first_response": "Use the safety-bounded first response from lead-intake-playbook.md.",
        "next_action": "Triage request; only build owned asset after repeated guardian demand.",
        "follow_up_deadline": "",
        "fulfillment_asset": "",
        "notes": f"verified:{request_date} {proof}",
    }


def writeback_kpi(row: dict[str, str]) -> str:
    utm = (row.get("utm_content") or "").strip()
    if not utm:
        return "manual_lead_no_utm"
    attribution = load_attribution().get(utm)
    if not attribution:
        return "manual_lead_unmatched_utm"
    field = row["kpi_writeback_field"]
    source_type = attribution.get("source_type")
    if source_type == "shorts":
        changed = increment_field(KPI_TRACKER, "script_id", attribution.get("script_id", ""), field)
        return "kpi_tracker_incremented" if changed else "kpi_tracker_missing_script"
    if source_type == "profile":
        changed = increment_field(PROFILE_TRACKER, "platform", attribution.get("platform", ""), field)
        return "profile_tracker_incremented" if changed else "profile_tracker_missing_platform"
    return "manual_lead_unsupported_attribution"


def playbook(fieldnames: list[str], rows: list[dict[str, str]], issues: list[str]) -> dict:
    real_rows = [row for row in rows if row.get("status") != "template"]
    commands = []
    for guardian in GUARDIANS:
        commands.append({
            "guardian": guardian,
            "guardianName": GUARDIANS[guardian],
            "ownedAssetCommand": (
                f"python3 tools/promotion_lead_writeback.py add --source contact --guardian {guardian} "
                f"--intake-type owned_asset_request --consent-status explicit_reply_ok --proof-note \"email thread {guardian}-owned request checked {today()}\""
            ),
            "lunaCommand": (
                f"python3 tools/promotion_lead_writeback.py add --source luna_page --guardian {guardian} "
                f"--intake-type luna_scene_request --consent-status explicit_reply_ok --proof-note \"email thread {guardian}-luna request checked {today()}\""
            ),
        })
    return {
        "generatedAt": today(),
        "sources": {
            "leadTracker": str(LEAD_TRACKER.relative_to(ROOT)),
            "attribution": str(ATTRIBUTION_PATH.relative_to(ROOT)),
            "kpiTracker": str(KPI_TRACKER.relative_to(ROOT)),
            "profileTracker": str(PROFILE_TRACKER.relative_to(ROOT)),
        },
        "metrics": {
            "rows": len(rows),
            "templateRows": len(rows) - len(real_rows),
            "realRows": len(real_rows),
            "issues": len(issues),
        },
        "commands": commands,
        "policy": {
            "doNotFake": True,
            "storeRawEmail": False,
            "realLeadRequires": ["proof note", "explicit_reply_ok consent", "guardian", "intake type"],
            "utmRule": "Matched shorts/profile utm_content increments KPI/profile tracker by one; missing or unmatched utm stays manual only.",
        },
        "issues": issues,
    }


def render_markdown(data: dict) -> str:
    lines = [
        "# LoveTypes Lead Writeback Playbook",
        "",
        f"- 產生日期：{data['generatedAt']}",
        f"- real leads：{data['metrics']['realRows']}",
        f"- template rows：{data['metrics']['templateRows']}",
        f"- issues：{data['metrics']['issues']}",
        "- 原則：只有收到真實 Contact / 收藏室 / Luna / 補給願望來信後，才能新增 real lead。",
        "- 隱私：不把原始 email 寫入 CSV；只記 request_id、守護者、需求類型、來源與 proof note。",
        "",
        "## 回填命令範例",
        "",
    ]
    for item in data["commands"]:
        lines.extend([
            f"### {item['guardianName']}（`{item['guardian']}`）",
            "",
            f"- 自有素材需求：`{item['ownedAssetCommand']}`",
            f"- Luna 場景需求：`{item['lunaCommand']}`",
            "",
        ])
    lines.extend([
        "## 結構化文字匯入",
        "",
        "- Contact 與收藏室的結構化表單會產生 `LoveTypes 結構化需求` 文字。",
        "- 收到來信後，先把該段文字存成暫存 `.txt`，再用匯入工具解析欄位；工具不會把 email 原文寫進 tracker。",
        "- 檢查：`python3 tools/promotion_lead_text_import.py check --input /path/to/request.txt`",
        "- 寫入：`python3 tools/promotion_lead_text_import.py add --input /path/to/request.txt --proof-note \"email thread Gmail request checked YYYY-MM-DD\"`",
        "",
        "## 安全規則",
        "",
        "- 不用本工具偽造名單、來信、同意或 KPI。",
        "- `--utm-content` 能對上 attribution 時才會回填 KPI；對不上時只記 manual lead。",
        "- 同守護者同需求重複出現後，才提高自有素材或 Luna 商品化優先級。",
    ])
    if data["issues"]:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in data["issues"])
    return "\n".join(lines).rstrip() + "\n"


def write_playbook(data: dict) -> None:
    PLAYBOOK_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    PLAYBOOK_MD.write_text(render_markdown(data), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Safely append real LoveTypes lead intake requests and write back matched KPI signals.")
    subparsers = parser.add_subparsers(dest="command")
    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("--write-playbook", action="store_true")
    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("--source", choices=sorted(SOURCE_OPTIONS), required=True)
    add_parser.add_argument("--guardian", choices=sorted(GUARDIANS), required=True)
    add_parser.add_argument("--intake-type", choices=sorted(INTAKE_TO_KPI), required=True)
    add_parser.add_argument("--consent-status", choices=sorted(CONSENT_STATUSES), required=True)
    add_parser.add_argument("--proof-note", required=True)
    add_parser.add_argument("--request-date", default="")
    add_parser.add_argument("--request-id", default="")
    add_parser.add_argument("--utm-content", default="")
    add_parser.add_argument("--requested-asset", default="")

    args = parser.parse_args()
    if not args.command:
        args.command = "check"
        args.write_playbook = False

    fieldnames, rows = read_csv(LEAD_TRACKER)
    if args.command == "add":
        new_row = build_row(args, rows)
        candidate = [*rows, {field: new_row.get(field, "") for field in fieldnames}]
        issues = validate_tracker(fieldnames, candidate)
        if issues:
            for issue in issues:
                print(issue)
            return 1
        write_csv(LEAD_TRACKER, fieldnames, candidate)
        kpi_status = writeback_kpi(new_row)
        fieldnames, rows = read_csv(LEAD_TRACKER)
        print(f"promotion_lead_writeback_kpi_status={kpi_status}")

    issues = validate_tracker(fieldnames, rows)
    data = playbook(fieldnames, rows, issues)
    if args.command == "add" or getattr(args, "write_playbook", False):
        write_playbook(data)
        print(f"promotion_lead_writeback_playbook={PLAYBOOK_MD}")
        print(f"promotion_lead_writeback_json={PLAYBOOK_JSON}")
    print(f"promotion_lead_writeback_rows={data['metrics']['rows']}")
    print(f"promotion_lead_writeback_template_rows={data['metrics']['templateRows']}")
    print(f"promotion_lead_writeback_real_rows={data['metrics']['realRows']}")
    print(f"promotion_lead_writeback_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
