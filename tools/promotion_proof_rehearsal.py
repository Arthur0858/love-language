#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
PROOF_FILES = sorted(PROMOTION_DIR.glob("proof-*.txt"))
OUTPUT_MD = PROMOTION_DIR / "proof-rehearsal.md"
OUTPUT_JSON = PROMOTION_DIR / "proof-rehearsal.json"

SAMPLE_POST_URLS = {
    "youtube_shorts": "https://www.youtube.com/shorts/lovetypes-rehearsal-check",
    "tiktok": "https://www.tiktok.com/@lovetypes/video/1234567890123456789",
    "instagram_reels": "https://www.instagram.com/reel/lovetypesrehearsal/",
}


def run_check(tool: str, path: Path) -> tuple[int, str]:
    result = subprocess.run(
        [sys.executable, f"tools/{tool}", "check", "--input", str(path)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return result.returncode, result.stdout


def proof_kind(path: Path) -> str:
    name = path.name
    return "post" if "-publish-" in name else "profile"


def platform_from_text(text: str) -> str:
    for line in text.splitlines():
        if line.lower().startswith("platform:"):
            return line.split(":", 1)[1].strip()
    return ""


def replace_post_url(text: str, platform: str) -> str:
    replacement = SAMPLE_POST_URLS.get(platform, "https://lovetypes.tw/rehearsal-post")
    lines = []
    for line in text.splitlines():
        if line.lower().startswith("post_url:"):
            lines.append(f"post_url: {replacement}")
        elif line.lower().startswith("proof_note:"):
            lines.append(f"proof_note: rehearsal public URL checked {date.today().isoformat()}")
        else:
            lines.append(line)
    return "\n".join(lines).rstrip() + "\n"


def temp_check(tool: str, text: str) -> tuple[int, str]:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as handle:
        handle.write(text)
        temp_path = Path(handle.name)
    try:
        return run_check(tool, temp_path)
    finally:
        temp_path.unlink(missing_ok=True)


def build_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in PROOF_FILES:
        text = path.read_text(encoding="utf-8")
        platform = platform_from_text(text)
        kind = proof_kind(path)
        if kind == "profile":
            code, output = run_check("promotion_profile_text_import.py", path)
            rows.append({
                "path": str(path.relative_to(ROOT)),
                "kind": kind,
                "platform": platform,
                "scenario": "profile_template_current",
                "expected": "pass",
                "passed": code == 0 and "promotion_profile_text_import_issues=0" in output,
                "output": output.strip(),
            })
        else:
            placeholder_code, placeholder_output = run_check("promotion_post_text_import.py", path)
            rows.append({
                "path": str(path.relative_to(ROOT)),
                "kind": kind,
                "platform": platform,
                "scenario": "post_placeholder_current",
                "expected": "reject",
                "passed": placeholder_code != 0 and "published status requires non-placeholder https post_url" in placeholder_output,
                "output": placeholder_output.strip(),
            })
            sample_code, sample_output = temp_check("promotion_post_text_import.py", replace_post_url(text, platform))
            rows.append({
                "path": str(path.relative_to(ROOT)),
                "kind": kind,
                "platform": platform,
                "scenario": "post_rehearsal_real_url",
                "expected": "pass",
                "passed": sample_code == 0 and "promotion_post_text_import_issues=0" in sample_output,
                "output": sample_output.strip(),
            })
    return rows


def build_rehearsal() -> dict:
    rows = build_rows()
    issues = validate_rows(rows)
    return {
        "generatedAt": date.today().isoformat(),
        "sources": [str(path.relative_to(ROOT)) for path in PROOF_FILES],
        "metrics": {
            "proofFiles": len(PROOF_FILES),
            "rows": len(rows),
            "profilePass": sum(1 for row in rows if row["kind"] == "profile" and row["passed"]),
            "postPlaceholderRejected": sum(1 for row in rows if row["scenario"] == "post_placeholder_current" and row["passed"]),
            "postRehearsalPass": sum(1 for row in rows if row["scenario"] == "post_rehearsal_real_url" and row["passed"]),
            "issues": len(issues),
        },
        "policy": {
            "noWriteback": True,
            "checksOnly": True,
            "postPlaceholdersMustFail": True,
            "sampleRealUrlsMustPass": True,
        },
        "rows": rows,
        "issues": issues,
    }


def validate_rows(rows: list[dict[str, object]]) -> list[str]:
    issues: list[str] = []
    profile_rows = [row for row in rows if row["kind"] == "profile"]
    post_placeholder = [row for row in rows if row["scenario"] == "post_placeholder_current"]
    post_rehearsal = [row for row in rows if row["scenario"] == "post_rehearsal_real_url"]
    if len(profile_rows) != 3:
        issues.append(f"expected 3 profile proof rehearsals, got {len(profile_rows)}")
    if len(post_placeholder) != 3:
        issues.append(f"expected 3 post placeholder rehearsals, got {len(post_placeholder)}")
    if len(post_rehearsal) != 3:
        issues.append(f"expected 3 post real URL rehearsals, got {len(post_rehearsal)}")
    for row in rows:
        if not row.get("passed"):
            issues.append(f"{row.get('path')} {row.get('scenario')} did not meet expected {row.get('expected')}")
    return issues


def render_markdown(rehearsal: dict) -> str:
    metrics = rehearsal["metrics"]
    lines = [
        "# LoveTypes Proof Rehearsal",
        "",
        f"- 產生日期：{rehearsal['generatedAt']}",
        f"- proof files：{metrics['proofFiles']}",
        f"- rows：{metrics['rows']}",
        f"- profile pass：{metrics['profilePass']} / 3",
        f"- post placeholder rejected：{metrics['postPlaceholderRejected']} / 3",
        f"- post rehearsal real URL pass：{metrics['postRehearsalPass']} / 3",
        f"- issues：{metrics['issues']}",
        "",
        "## Rule",
        "",
        "- This rehearsal runs check commands only; it never writes to trackers.",
        "- Profile templates must pass because they are ready to use after external proof exists.",
        "- Post placeholder templates must fail until a real public URL replaces the placeholder.",
        "- Temporary post samples with platform-shaped URLs must pass import validation.",
        "",
        "## Rows",
        "",
    ]
    for row in rehearsal["rows"]:
        lines.extend([
            f"### `{row['scenario']}` · {row['platform']}",
            "",
            f"- file：`{row['path']}`",
            f"- expected：`{row['expected']}`",
            f"- passed：`{int(bool(row['passed']))}`",
            "",
        ])
    if rehearsal["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in rehearsal["issues"])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run non-mutating proof import rehearsal for LoveTypes launch proof files.")
    parser.add_argument("--check", action="store_true", help="Validate only; do not write outputs.")
    parser.add_argument("--output", default=str(OUTPUT_MD))
    parser.add_argument("--json-output", default=str(OUTPUT_JSON))
    args = parser.parse_args()

    rehearsal = build_rehearsal()
    metrics = rehearsal["metrics"]
    print(f"promotion_proof_rehearsal_files={metrics['proofFiles']}")
    print(f"promotion_proof_rehearsal_rows={metrics['rows']}")
    print(f"promotion_proof_rehearsal_profile_pass={metrics['profilePass']}")
    print(f"promotion_proof_rehearsal_post_placeholder_rejected={metrics['postPlaceholderRejected']}")
    print(f"promotion_proof_rehearsal_post_real_url_pass={metrics['postRehearsalPass']}")
    print(f"promotion_proof_rehearsal_issues={metrics['issues']}")
    for issue in rehearsal["issues"]:
        print(issue)
    if rehearsal["issues"]:
        return 1
    if not args.check:
        output = Path(args.output)
        json_output = Path(args.json_output)
        output.write_text(render_markdown(rehearsal), encoding="utf-8")
        json_output.write_text(json.dumps(rehearsal, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"promotion_proof_rehearsal={output.relative_to(ROOT)}")
        print(f"promotion_proof_rehearsal_json={json_output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
