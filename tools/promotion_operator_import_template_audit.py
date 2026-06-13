#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HANDOFF_PATH = ROOT / "docs" / "promotion" / "first-round" / "operator-handoff-packet.json"
EXPECTED_IMPORTS = {
    "profile_setup_import": {
        "tool": "tools/promotion_profile_text_import.py",
        "required_outputs": (
            "promotion_profile_text_import_has_profile_link=1",
            "promotion_profile_text_import_issues=0",
        ),
    },
    "post_publish_import": {
        "tool": "tools/promotion_post_text_import.py",
        "required_outputs": (
            "promotion_post_text_import_has_post_url=1",
            "promotion_post_text_import_issues=1",
            "published status requires non-placeholder https post_url",
        ),
        "expect_rejected": True,
    },
    "lead_request_import": {
        "tool": "tools/promotion_lead_text_import.py",
        "required_outputs": (
            "promotion_lead_text_import_has_reply_email=1",
            "promotion_lead_text_import_has_utm_content=1",
            "promotion_lead_text_import_issues=1",
            "reply_email must be a real requester address",
        ),
        "expect_rejected": True,
    },
}


def load_handoff(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def run_template_check(import_id: str, template: str) -> tuple[bool, str]:
    config = EXPECTED_IMPORTS[import_id]
    tool_path = ROOT / str(config["tool"])
    if not tool_path.exists():
        return False, f"{import_id}: missing tool {config['tool']}"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as handle:
        handle.write(template)
        temp_path = Path(handle.name)
    try:
        result = subprocess.run(
            [sys.executable, str(tool_path), "check", "--input", str(temp_path)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    finally:
        temp_path.unlink(missing_ok=True)
    output = result.stdout.strip()
    expect_rejected = bool(config.get("expect_rejected"))
    if result.returncode != 0 and not expect_rejected:
        return False, f"{import_id}: check command failed\n{output}"
    if result.returncode == 0 and expect_rejected:
        return False, f"{import_id}: placeholder template should be rejected until a real post URL is supplied\n{output}"
    missing_outputs = [item for item in config["required_outputs"] if item not in output]
    if missing_outputs:
        return False, f"{import_id}: missing expected check output {', '.join(missing_outputs)}\n{output}"
    return True, output


def validate() -> tuple[dict[str, int], list[str]]:
    issues: list[str] = []
    handoff = load_handoff(HANDOFF_PATH)
    imports = handoff.get("structuredImports", [])
    if not isinstance(imports, list):
        imports = []
        issues.append("operator handoff structuredImports should be a list")
    by_id = {str(item.get("id", "")): item for item in imports if isinstance(item, dict)}
    missing = [import_id for import_id in EXPECTED_IMPORTS if import_id not in by_id]
    for import_id in missing:
        issues.append(f"missing structured import template: {import_id}")

    checked = 0
    valid = 0
    safely_rejected = 0
    for import_id in EXPECTED_IMPORTS:
        item = by_id.get(import_id)
        if not item:
            continue
        template = str(item.get("template", "")).strip()
        check_command = str(item.get("checkCommand", ""))
        expected_tool = EXPECTED_IMPORTS[import_id]["tool"]
        if expected_tool not in check_command:
            issues.append(f"{import_id}: checkCommand should reference {expected_tool}")
        if not template:
            issues.append(f"{import_id}: template is empty")
            continue
        checked += 1
        ok, detail = run_template_check(import_id, template)
        if ok:
            if EXPECTED_IMPORTS[import_id].get("expect_rejected"):
                safely_rejected += 1
            else:
                valid += 1
        else:
            issues.append(detail)

    return {
        "templates": len(imports),
        "expectedTemplates": len(EXPECTED_IMPORTS),
        "checkedTemplates": checked,
        "validTemplates": valid,
        "safelyRejectedTemplates": safely_rejected,
    }, issues


def main() -> int:
    metrics, issues = validate()
    print(f"promotion_operator_import_templates={metrics['templates']}")
    print(f"promotion_operator_import_expected_templates={metrics['expectedTemplates']}")
    print(f"promotion_operator_import_checked_templates={metrics['checkedTemplates']}")
    print(f"promotion_operator_import_valid_templates={metrics['validTemplates']}")
    print(f"promotion_operator_import_safely_rejected_templates={metrics['safelyRejectedTemplates']}")
    print(f"promotion_operator_import_template_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
