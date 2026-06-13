#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
TEMPLATE_DIR = PROMOTION_DIR / "lead-request-proof-templates"
OUTPUT_MD = PROMOTION_DIR / "lead-request-proof-packet.md"
OUTPUT_JSON = PROMOTION_DIR / "lead-request-proof-packet.json"
OUTPUT_CSV = PROMOTION_DIR / "lead-request-proof-packet.csv"
LEAD_PLAYBOOK = PROMOTION_DIR / "lead-intake-playbook.json"
LEAD_WRITEBACK = PROMOTION_DIR / "lead-writeback-playbook.json"
LEAD_TRACKER = PROMOTION_DIR / "lead-intake-tracker.csv"

GUARDIANS = {
    "iris": "艾莉絲",
    "noah": "諾雅",
    "vivian": "薇薇安",
    "claire": "克萊兒",
    "dora": "朵拉",
}
INTAKE_ROWS = {
    "owned_asset_request": {
        "source": "keepsake_waitlist",
        "sourceLabel": "收藏室免費素材需求",
        "asset": "PDF 練習卡 / 手機桌布 / 短儀式",
        "page": "https://lovetypes.tw/keepsakes/",
        "context": "想收到這位守護者的免費收藏物，並同意收到回覆。",
    },
    "luna_scene_request": {
        "source": "luna_page",
        "sourceLabel": "Luna page",
        "asset": "Luna bedtime / conflict cooldown / quiz aftercare pack",
        "page": "https://lovetypes.tw/luna-yoga-music/",
        "context": "想知道這位守護者適合哪一種 Luna 夜間補給場景。",
    },
    "repair_or_contact_request": {
        "source": "contact",
        "sourceLabel": "Contact 結構化需求",
        "asset": "relationship repair prompt / supply route guidance",
        "page": "https://lovetypes.tw/contact/",
        "context": "想詢問守護者路線、修復計畫或補給方向；非緊急危機需求。",
    },
}


def today() -> str:
    return date.today().isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def template_text(guardian_id: str, intake_type: str, config: dict[str, str]) -> str:
    guardian_name = GUARDIANS[guardian_id]
    return "\n".join([
        "LoveTypes 結構化需求",
        f"來源: {config['sourceLabel']}",
        f"我的守護者: {guardian_name}",
        f"需求類型: {intake_type}",
        f"素材偏好: {config['asset']}",
        "可回覆 email: <REAL_REPLY_EMAIL>",
        f"Campaign content / 推廣內容: {guardian_id}_{intake_type}",
        f"使用情境或備註: {config['context']}",
        "consent_status: explicit_reply_ok",
        f"page: {config['page']}",
    ]) + "\n"


def build_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for guardian_id in GUARDIANS:
        for intake_type, config in INTAKE_ROWS.items():
            filename = f"lead-{guardian_id}-{intake_type}.txt"
            rel_path = TEMPLATE_DIR.relative_to(ROOT) / filename
            rows.append({
                "guardian": guardian_id,
                "guardianName": GUARDIANS[guardian_id],
                "intakeType": intake_type,
                "source": config["source"],
                "templatePath": str(rel_path),
                "checkCommand": f"python3 tools/promotion_lead_text_import.py check --input {rel_path}",
                "writeCommand": f"python3 tools/promotion_lead_text_import.py add --input {rel_path} --proof-note \"email thread {guardian_id}-{intake_type} request checked {today()}\"",
                "requiredEvidence": "real reply email, explicit_reply_ok consent, safe non-emergency scope, proof note, no raw email stored in tracker",
                "template": template_text(guardian_id, intake_type, config),
            })
    return rows


def write_templates(rows: list[dict[str, str]]) -> None:
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    for row in rows:
        path = ROOT / row["templatePath"]
        path.write_text(row["template"], encoding="utf-8")


def run_check(row: dict[str, str]) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, "tools/promotion_lead_text_import.py", "check", "--input", row["templatePath"]],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def validate(rows: list[dict[str, str]], playbook: dict, writeback: dict, lead_rows: list[dict[str, str]]) -> tuple[list[str], dict[str, int]]:
    issues: list[str] = []
    safe_rejected = 0
    files = 0
    source_options = set(playbook.get("sourceOptions", []))
    intake_types = {item.get("type") for item in playbook.get("intakeTypes", []) if isinstance(item, dict)}
    tracker_fields = set(lead_rows[0].keys()) if lead_rows else set()

    if len(rows) != len(GUARDIANS) * len(INTAKE_ROWS):
        issues.append(f"expected {len(GUARDIANS) * len(INTAKE_ROWS)} lead proof templates, got {len(rows)}")
    if source_options and not {item["source"] for item in INTAKE_ROWS.values()}.issubset(source_options):
        issues.append("lead request template sources must exist in lead intake playbook")
    if intake_types and set(INTAKE_ROWS) != intake_types:
        issues.append("lead request template intake types must match lead intake playbook")
    if not writeback.get("policy", {}).get("doNotFake"):
        issues.append("lead writeback policy must keep doNotFake enabled")
    if "notes" not in tracker_fields or "consent_status" not in tracker_fields:
        issues.append("lead tracker must include notes and consent_status fields")

    seen_paths: set[str] = set()
    for row in rows:
        label = f"{row['guardian']}/{row['intakeType']}"
        path = ROOT / row["templatePath"]
        if row["templatePath"] in seen_paths:
            issues.append(f"{label}: duplicate template path")
        seen_paths.add(row["templatePath"])
        if not path.exists():
            issues.append(f"{label}: missing template file")
            continue
        files += 1
        text = path.read_text(encoding="utf-8")
        if "sample@example.com" in text or "s755102" in text:
            issues.append(f"{label}: template must not contain a real-looking personal email")
        if "<REAL_REPLY_EMAIL>" not in text:
            issues.append(f"{label}: template must keep the real email placeholder")
        if "consent_status: explicit_reply_ok" not in text:
            issues.append(f"{label}: template must include explicit consent field")
        if "非緊急" not in text and row["intakeType"] == "repair_or_contact_request":
            issues.append(f"{label}: contact template must include non-emergency scope wording")
        code, output = run_check(row)
        safe_email_rejected = (
            "reply_email should look like an email address" in output
            or "reply_email must be a real requester address" in output
            or "reply_email must not use a reserved test/example domain" in output
        )
        if code != 0 and "promotion_lead_text_import_issues=1" in output and safe_email_rejected:
            safe_rejected += 1
        else:
            issues.append(f"{label}: blank template should be safely rejected until a real reply email is inserted")

    metrics = {
        "rows": len(rows),
        "files": files,
        "guardians": len(GUARDIANS),
        "intakeTypes": len(INTAKE_ROWS),
        "safeRejected": safe_rejected,
        "realLeadRows": sum(1 for row in lead_rows if row.get("status") != "template"),
    }
    return issues, metrics


def build_packet(check_only: bool) -> dict:
    rows = build_rows()
    if not check_only:
        write_templates(rows)
    playbook = load_json(LEAD_PLAYBOOK)
    writeback = load_json(LEAD_WRITEBACK)
    lead_rows = read_csv(LEAD_TRACKER)
    issues, metrics = validate(rows, playbook, writeback, lead_rows)
    return {
        "generatedAt": today(),
        "sources": {
            "leadIntakePlaybook": str(LEAD_PLAYBOOK.relative_to(ROOT)),
            "leadWritebackPlaybook": str(LEAD_WRITEBACK.relative_to(ROOT)),
            "leadTracker": str(LEAD_TRACKER.relative_to(ROOT)),
        },
        "policy": {
            "templatesAreNotRealLeads": True,
            "doNotStoreRawEmail": True,
            "safeRejectionRequired": "Templates must fail check until <REAL_REPLY_EMAIL> is replaced from a real request.",
            "writeCommandRequires": ["real reply email", "explicit_reply_ok consent", "traceable proof note", "safe non-emergency scope"],
        },
        "metrics": metrics,
        "rows": [{key: value for key, value in row.items() if key != "template"} for row in rows],
        "issues": issues,
    }


def render_markdown(packet: dict) -> str:
    metrics = packet["metrics"]
    lines = [
        "# LoveTypes Lead Request Proof Packet",
        "",
        f"- 產生日期：{packet['generatedAt']}",
        f"- template rows：{metrics['rows']}",
        f"- template files：{metrics['files']}",
        f"- guardians：{metrics['guardians']}",
        f"- intake types：{metrics['intakeTypes']}",
        f"- safely rejected templates：{metrics['safeRejected']}",
        f"- real leads：{metrics['realLeadRows']}",
        f"- issues：{len(packet['issues'])}",
        "",
        "## Rules",
        "",
        "- 這些模板不是名單，不可直接當作真實需求寫入。",
        "- 每份模板都必須在未填入真實可回覆 email 前被 `check` 拒收。",
        "- 收到真實 Contact / 收藏室 / Luna 來信後，只複製結構化需求區塊到對應模板或暫存檔。",
        "- 寫入前必須保留 `explicit_reply_ok`、安全非緊急範圍與可追溯 proof note。",
        "- Tracker 不保存原始 email，只保存 request_id、守護者、需求類型、來源與 proof note。",
        "",
        "## Templates",
        "",
    ]
    for row in packet["rows"]:
        lines.extend([
            f"### {row['guardianName']} · `{row['intakeType']}`",
            "",
            f"- source：`{row['source']}`",
            f"- file：`{row['templatePath']}`",
            f"- check：`{row['checkCommand']}`",
            f"- write：`{row['writeCommand']}`",
            f"- evidence：{row['requiredEvidence']}",
            "",
        ])
    if packet["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in packet["issues"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(packet: dict) -> None:
    OUTPUT_MD.write_text(render_markdown(packet), encoding="utf-8")
    OUTPUT_JSON.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fieldnames = ["guardian", "guardianName", "intakeType", "source", "templatePath", "checkCommand", "writeCommand", "requiredEvidence"]
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fieldnames} for row in packet["rows"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Build safe fillable proof templates for LoveTypes lead requests.")
    parser.add_argument("--check", action="store_true", help="Validate existing template files without writing.")
    args = parser.parse_args()
    packet = build_packet(check_only=args.check)
    metrics = packet["metrics"]
    if not args.check:
        write_outputs(packet)
        print(f"promotion_lead_request_proof_packet={OUTPUT_MD.relative_to(ROOT)}")
        print(f"promotion_lead_request_proof_packet_json={OUTPUT_JSON.relative_to(ROOT)}")
        print(f"promotion_lead_request_proof_packet_csv={OUTPUT_CSV.relative_to(ROOT)}")
    print(f"promotion_lead_request_proof_rows={metrics['rows']}")
    print(f"promotion_lead_request_proof_files={metrics['files']}")
    print(f"promotion_lead_request_proof_guardians={metrics['guardians']}")
    print(f"promotion_lead_request_proof_intake_types={metrics['intakeTypes']}")
    print(f"promotion_lead_request_proof_safe_rejected={metrics['safeRejected']}")
    print(f"promotion_lead_request_proof_real_leads={metrics['realLeadRows']}")
    print(f"promotion_lead_request_proof_issues={len(packet['issues'])}")
    for issue in packet["issues"]:
        print(issue)
    return 1 if packet["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
