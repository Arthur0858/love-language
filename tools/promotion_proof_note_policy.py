#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "proof-note-policy.md"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "proof-note-policy.json"


TRACEABLE_PROOF_TOKENS = (
    "screenshot",
    "截圖",
    "螢幕截圖",
    "screen recording",
    "recording",
    "錄影",
    "public url",
    "public link",
    "公開",
    "live url",
    "profile url",
    "post url",
    "platform url",
    "channel url",
    "video url",
    "email thread",
    "gmail thread",
    "message id",
    "mail id",
    "inbox",
    "email",
    "信件",
    "來信",
    "thread",
    "url:",
    "http://",
    "https://",
)
GENERIC_ONLY_PHRASES = {
    "manual profile link verified",
    "live profile link verified",
    "profile link manually verified",
    "manual post url verified",
    "post url and first metrics verified",
    "post url and starter metrics manually verified",
    "email request verified",
    "manual link verified",
    "verified",
}
DATE_RE = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")
PLACEHOLDER_TOKENS = (
    "<real_",
    "<replace",
    "replace-with-real",
    "yyyy-mm-dd",
    "example.com",
)


def normalize_note(value: str) -> str:
    return " ".join(value.strip().lower().split())


def has_traceable_evidence(value: str) -> bool:
    normalized = normalize_note(value)
    if not normalized:
        return False
    if normalized in GENERIC_ONLY_PHRASES:
        return False
    return any(token in normalized for token in TRACEABLE_PROOF_TOKENS) or bool(DATE_RE.search(normalized))


def proof_note_issue(value: str, label: str = "proof_note") -> str:
    normalized = normalize_note(value)
    if any(token in normalized for token in PLACEHOLDER_TOKENS):
        return f"{label} must replace placeholder proof text with real evidence"
    if has_traceable_evidence(value):
        return ""
    return (
        f"{label} must include traceable evidence such as a screenshot filename, "
        "public URL, platform URL, email thread, message id, or checked date"
    )


def build_policy() -> dict:
    accepted_examples = [
        "screenshot profile-youtube_shorts-2026-06-14.png verified",
        "public URL https://www.youtube.com/@lovetypes clicked 2026-06-14",
        "screen recording profile-instagram_reels-2026-06-14.mov verified",
        "email thread Gmail abc123 checked 2026-06-14",
    ]
    rejected_examples = sorted(GENERIC_ONLY_PHRASES | {"<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified"})
    rows = [
        {
            "ruleId": "replace_placeholder",
            "status": "required",
            "description": "Placeholder proof text must be replaced before writeback.",
            "rejects": ", ".join(PLACEHOLDER_TOKENS),
        },
        {
            "ruleId": "traceable_evidence",
            "status": "required",
            "description": "Proof notes must include traceable evidence, not only a claim that work was done.",
            "accepts": ", ".join(TRACEABLE_PROOF_TOKENS),
        },
        {
            "ruleId": "generic_note_rejection",
            "status": "required",
            "description": "Generic notes like verified are rejected unless paired with a traceable artifact, URL, thread, or date.",
            "rejects": ", ".join(sorted(GENERIC_ONLY_PHRASES)),
        },
        {
            "ruleId": "date_support",
            "status": "allowed",
            "description": "A checked date is accepted as supporting evidence when the note is otherwise specific.",
            "accepts": DATE_RE.pattern,
        },
    ]
    issues: list[str] = []
    for example in accepted_examples:
        if proof_note_issue(example):
            issues.append(f"accepted example should pass: {example}")
    for example in rejected_examples:
        if not proof_note_issue(example):
            issues.append(f"rejected example should fail: {example}")
    return {
        "generatedAt": date.today().isoformat(),
        "metrics": {
            "rules": len(rows),
            "traceableTokens": len(TRACEABLE_PROOF_TOKENS),
            "genericRejectedPhrases": len(GENERIC_ONLY_PHRASES),
            "placeholderTokens": len(PLACEHOLDER_TOKENS),
            "acceptedExamples": len(accepted_examples),
            "rejectedExamples": len(rejected_examples),
            "issues": len(issues),
        },
        "rows": rows,
        "traceableProofTokens": list(TRACEABLE_PROOF_TOKENS),
        "placeholderTokens": list(PLACEHOLDER_TOKENS),
        "genericOnlyPhrases": sorted(GENERIC_ONLY_PHRASES),
        "acceptedExamples": accepted_examples,
        "rejectedExamples": rejected_examples,
        "issues": issues,
    }


def render_markdown(policy: dict) -> str:
    metrics = policy["metrics"]
    lines = [
        "# LoveTypes Proof Note Policy",
        "",
        f"- 產生日期：{policy['generatedAt']}",
        f"- rules：{metrics['rules']}",
        f"- traceable tokens：{metrics['traceableTokens']}",
        f"- generic rejected phrases：{metrics['genericRejectedPhrases']}",
        f"- placeholder tokens：{metrics['placeholderTokens']}",
        f"- accepted examples：{metrics['acceptedExamples']}",
        f"- rejected examples：{metrics['rejectedExamples']}",
        f"- issues：{metrics['issues']}",
        "",
        "## Rules",
        "",
    ]
    for row in policy["rows"]:
        lines.extend([
            f"### `{row['ruleId']}`",
            "",
            f"- status：`{row['status']}`",
            f"- description：{row['description']}",
        ])
        if row.get("accepts"):
            lines.append(f"- accepts：{row['accepts']}")
        if row.get("rejects"):
            lines.append(f"- rejects：{row['rejects']}")
        lines.append("")
    lines.extend(["## Accepted Examples", ""])
    lines.extend(f"- `{example}`" for example in policy["acceptedExamples"])
    lines.extend(["", "## Rejected Examples", ""])
    lines.extend(f"- `{example}`" for example in policy["rejectedExamples"])
    if policy["issues"]:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in policy["issues"])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(policy: dict, md_output: Path, json_output: Path) -> None:
    md_output.write_text(render_markdown(policy), encoding="utf-8")
    json_output.write_text(json.dumps(policy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate and validate the LoveTypes proof-note policy.")
    parser.add_argument("--check", action="store_true", help="Validate without writing outputs.")
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    args = parser.parse_args()
    policy = build_policy()
    metrics = policy["metrics"]
    if not args.check:
        write_outputs(policy, Path(args.output), Path(args.json_output))
        print(f"promotion_proof_note_policy={args.output}")
        print(f"promotion_proof_note_policy_json={args.json_output}")
    print(f"promotion_proof_note_policy_rules={metrics['rules']}")
    print(f"promotion_proof_note_policy_traceable_tokens={metrics['traceableTokens']}")
    print(f"promotion_proof_note_policy_generic_rejected_phrases={metrics['genericRejectedPhrases']}")
    print(f"promotion_proof_note_policy_placeholder_tokens={metrics['placeholderTokens']}")
    print(f"promotion_proof_note_policy_accepted_examples={metrics['acceptedExamples']}")
    print(f"promotion_proof_note_policy_rejected_examples={metrics['rejectedExamples']}")
    print(f"promotion_proof_note_policy_issues={metrics['issues']}")
    for issue in policy["issues"]:
        print(issue)
    return 1 if policy["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
