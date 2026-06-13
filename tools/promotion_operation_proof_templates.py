#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
PACKET_PATH = PROMOTION_DIR / "operation-proof-packet.json"
DEFAULT_OUTPUT_PATH = PROMOTION_DIR / "operation-proof-templates.md"
DEFAULT_JSON_OUTPUT_PATH = PROMOTION_DIR / "operation-proof-templates.json"
INPUT_RE = re.compile(r"--input\s+([^\s]+)")
FORBIDDEN_FAKE_URL_MARKERS = (
    "replace-with-real",
    "example.com/replace",
    "lovetypes-proof-url-123",
)


def load_packet() -> dict:
    if not PACKET_PATH.exists():
        raise SystemExit(f"missing {PACKET_PATH.relative_to(ROOT)}; run promotion_operation_proof_packet.py first")
    return json.loads(PACKET_PATH.read_text(encoding="utf-8"))


def extract_input_path(command: str) -> Path | None:
    match = INPUT_RE.search(command)
    if not match:
        return None
    value = match.group(1).strip().strip('"').strip("'")
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def run_check(command: list[str]) -> tuple[int, str]:
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def write_templates(packet: dict) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for item in packet.get("proofs", []):
        input_path = extract_input_path(str(item.get("checkCommand", "")))
        if not input_path:
            rows.append({
                "kind": item.get("kind", ""),
                "platform": item.get("platform", ""),
                "taskId": item.get("taskId", ""),
                "path": "",
                "status": "missing_input_path",
            })
            continue
        input_path.parent.mkdir(parents=True, exist_ok=True)
        input_path.write_text(str(item.get("template", "")).rstrip() + "\n", encoding="utf-8")
        rows.append({
            "kind": item.get("kind", ""),
            "platform": item.get("platform", ""),
            "taskId": item.get("taskId", ""),
            "path": str(input_path.relative_to(ROOT)),
            "checkCommand": item.get("checkCommand", ""),
            "writeCommand": item.get("writeCommand", ""),
            "requiredEvidence": item.get("requiredEvidence", []),
            "status": "written",
        })
    return rows


def existing_rows(packet: dict) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for item in packet.get("proofs", []):
        input_path = extract_input_path(str(item.get("checkCommand", "")))
        rows.append({
            "kind": item.get("kind", ""),
            "platform": item.get("platform", ""),
            "taskId": item.get("taskId", ""),
            "path": str(input_path.relative_to(ROOT)) if input_path else "",
            "checkCommand": item.get("checkCommand", ""),
            "writeCommand": item.get("writeCommand", ""),
            "requiredEvidence": item.get("requiredEvidence", []),
            "status": "existing",
        })
    return rows


def validate(packet: dict, rows: list[dict[str, object]]) -> tuple[list[str], dict[str, int]]:
    issues: list[str] = []
    profile_valid = 0
    post_safely_rejected = 0
    proof_count = len(packet.get("proofs", []))
    existing_files = 0

    if len(rows) != proof_count:
        issues.append("template row count should match proof rows")

    for row in rows:
        label = f"{row.get('kind')}/{row.get('platform')}/{row.get('taskId', '')}"
        rel_path = str(row.get("path", ""))
        if not rel_path:
            issues.append(f"{label}: missing input file path")
            continue
        path = ROOT / rel_path
        if not path.exists():
            issues.append(f"{label}: missing template file {rel_path}")
            continue
        existing_files += 1
        text = path.read_text(encoding="utf-8")
        for marker in FORBIDDEN_FAKE_URL_MARKERS:
            if marker in text:
                issues.append(f"{label}: forbidden fake URL marker {marker}")
        if row.get("kind") == "profile_setup":
            code, output = run_check([sys.executable, "tools/promotion_profile_text_import.py", "check", "--input", rel_path])
            if code == 0 and "promotion_profile_text_import_issues=0" in output:
                profile_valid += 1
            else:
                issues.append(f"{label}: profile proof template should pass check")
        elif row.get("kind") == "post_publish":
            code, output = run_check([sys.executable, "tools/promotion_post_text_import.py", "check", "--input", rel_path])
            if code != 0 and "promotion_post_text_import_issues=1" in output and "non-placeholder https post_url" in output:
                post_safely_rejected += 1
            else:
                issues.append(f"{label}: post proof template should be rejected until a real post URL is inserted")

    metrics = {
        "proofRows": proof_count,
        "files": existing_files,
        "profile": sum(1 for row in rows if row.get("kind") == "profile_setup"),
        "post": sum(1 for row in rows if row.get("kind") == "post_publish"),
        "profileValid": profile_valid,
        "postSafelyRejected": post_safely_rejected,
    }
    return issues, metrics


def render_markdown(packet: dict, rows: list[dict[str, object]], issues: list[str], metrics: dict[str, int]) -> str:
    lines = [
        "# LoveTypes Operation Proof Templates",
        "",
        f"- Generated: `{packet.get('generatedAt', '')}`",
        f"- Template files: `{metrics.get('files', 0)}`",
        f"- Profile templates valid: `{metrics.get('profileValid', 0)}`",
        f"- Post templates safely rejected until real URL: `{metrics.get('postSafelyRejected', 0)}`",
        f"- Issues: `{len(issues)}`",
        "",
        "## How To Use",
        "",
        "- Fill profile templates only after the platform profile link is visibly set and clicked.",
        "- Fill post templates only after the public post exists and the placeholder URL is replaced with the real HTTPS post URL.",
        "- Run the check command before the write command.",
        "- Keep zero metrics only when the platform or analytics source was actually checked.",
        "",
        "## Files",
        "",
    ]
    for row in rows:
        lines.extend([
            f"### {row.get('kind', '')}: {row.get('platform', '')} {row.get('taskId', '')}".strip(),
            "",
            f"- File: `{row.get('path', '')}`",
            f"- Check: `{row.get('checkCommand', '')}`",
            f"- Write: `{row.get('writeCommand', '')}`",
            "- Required evidence:",
            *[f"  - `{item}`" for item in row.get("requiredEvidence", [])],
            "",
        ])
    if issues:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in issues)
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate and validate fillable LoveTypes operation proof templates.")
    parser.add_argument("--check", action="store_true", help="Validate existing template files without writing.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT_PATH))
    args = parser.parse_args()

    packet = load_packet()
    rows = existing_rows(packet) if args.check else write_templates(packet)
    issues, metrics = validate(packet, rows)
    result = {
        "generatedAt": packet.get("generatedAt", ""),
        "source": str(PACKET_PATH.relative_to(ROOT)),
        "metrics": metrics,
        "rows": rows,
        "issues": issues,
    }
    print(f"promotion_operation_proof_templates_profile={metrics.get('profile', 0)}")
    print(f"promotion_operation_proof_templates_post={metrics.get('post', 0)}")
    print(f"promotion_operation_proof_templates_files={metrics.get('files', 0)}")
    print(f"promotion_operation_proof_templates_profile_valid={metrics.get('profileValid', 0)}")
    print(f"promotion_operation_proof_templates_post_safely_rejected={metrics.get('postSafelyRejected', 0)}")
    print(f"promotion_operation_proof_templates_issues={len(issues)}")
    for issue in issues:
        print(issue)
    if issues:
        return 1
    if not args.check:
        json_output = Path(args.json_output)
        md_output = Path(args.output)
        json_output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        md_output.write_text(render_markdown(packet, rows, issues, metrics), encoding="utf-8")
        print(f"promotion_operation_proof_templates_json={json_output.relative_to(ROOT)}")
        print(f"promotion_operation_proof_templates_md={md_output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
