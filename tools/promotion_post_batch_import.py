#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import promotion_post_text_import as text_import
import promotion_post_writeback as writeback
from promotion_proof_note_policy import proof_note_issue


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
TASK_ID = "publish-lt-s01-iris-silence"
PROOF_FILES = {
    "youtube_shorts": PROMOTION_DIR / f"proof-youtube_shorts-{TASK_ID}.txt",
    "tiktok": PROMOTION_DIR / f"proof-tiktok-{TASK_ID}.txt",
    "instagram_reels": PROMOTION_DIR / f"proof-instagram_reels-{TASK_ID}.txt",
}
OUTPUT_MD = PROMOTION_DIR / "post-batch-import-quickstart.md"
OUTPUT_JSON = PROMOTION_DIR / "post-batch-import-quickstart.json"
OUTPUT_TXT = PROMOTION_DIR / "post-batch-import-quickstart.txt"


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def is_placeholder(value: str) -> bool:
    text = value.strip().lower()
    return not text or "<real_" in text or "placeholder" in text or "example.com" in text


def classify_proof(path: Path) -> dict[str, object]:
    if not path.exists():
        return {
            "platform": "",
            "taskId": TASK_ID,
            "proofFile": str(path.relative_to(ROOT)),
            "status": "missing_file",
            "ready": 0,
            "issues": [f"missing proof file {path.relative_to(ROOT)}"],
        }
    data, parse_issues = text_import.parse_text(path.read_text(encoding="utf-8"))
    platform = data.get("platform", "")
    issues = [str(issue) for issue in parse_issues]
    status = "ready"
    if platform not in PROOF_FILES:
        status = "invalid"
        issues.append(f"unexpected platform {platform!r}")
    elif path != PROOF_FILES[platform]:
        status = "invalid"
        issues.append(f"{platform}: proof file path does not match platform")
    if data.get("task_id") != TASK_ID:
        status = "invalid"
        issues.append(f"unexpected task_id {data.get('task_id')!r}")
    proof = data.get("proof_note", "")
    if is_placeholder(data.get("post_url", "")) or proof_note_issue(proof):
        status = "blocked_until_real_public_post"
    return {
        "platform": platform,
        "taskId": data.get("task_id", TASK_ID),
        "proofFile": str(path.relative_to(ROOT)),
        "status": status,
        "ready": 1 if status == "ready" and not issues else 0,
        "data": data,
        "issues": issues,
    }


def build_packet() -> dict:
    rows = [classify_proof(path) for path in PROOF_FILES.values()]
    ready_rows = sum(int(row["ready"]) for row in rows)
    blocked_rows = sum(1 for row in rows if row["status"] == "blocked_until_real_public_post")
    invalid_rows = sum(1 for row in rows if row["status"] not in {"ready", "blocked_until_real_public_post"})
    platforms = [str(row.get("platform", "")) for row in rows if row.get("platform")]
    issues: list[str] = []
    if len(set(platforms)) != len(PROOF_FILES):
        issues.append("post proof files must cover exactly youtube_shorts, tiktok, and instagram_reels")
    if invalid_rows:
        issues.append(f"invalid post proof rows: {invalid_rows}")
    return {
        "generatedAt": text_import.TODAY,
        "taskId": TASK_ID,
        "metrics": {
            "proofFiles": len(rows),
            "readyRows": ready_rows,
            "blockedRows": blocked_rows,
            "invalidRows": invalid_rows,
            "issues": len(issues),
        },
        "rows": rows,
        "commands": {
            "check": "python3 tools/promotion_post_batch_import.py --check",
            "writeDocs": "python3 tools/promotion_post_batch_import.py",
            "addAll": "python3 tools/promotion_post_batch_import.py --add",
        },
        "issues": issues,
    }


def apply_batch(packet: dict) -> None:
    metrics = packet["metrics"]
    if metrics["readyRows"] != len(PROOF_FILES) or metrics["issues"]:
        details = []
        for row in packet["rows"]:
            if row["issues"] or not row["ready"]:
                details.append(f"{row.get('platform') or row.get('proofFile')}: {row['status']}")
        raise SystemExit("post batch import requires all three public post proof files ready\n" + "\n".join(details))
    profile_issue = writeback.profile_gate_issue()
    if profile_issue:
        raise SystemExit(profile_issue)

    queue_fields, queue_rows = read_rows(writeback.QUEUE_PATH)
    platform_fields, platform_rows = read_rows(writeback.PLATFORM_TRACKER_PATH)
    script_fields, script_rows = read_rows(writeback.SCRIPT_TRACKER_PATH)
    touched_scripts: set[str] = set()
    for row in packet["rows"]:
        data = row["data"]
        proof = data.get("proof_note", "")
        metrics_data = {field: data.get(field, "") for field in writeback.METRIC_FIELDS}
        queue_row = writeback.update_platform_rows(
            queue_rows,
            data["platform"],
            data["task_id"],
            data["status"],
            data["published_date"],
            data["post_url"],
            proof,
            metrics_data,
        )
        writeback.update_platform_rows(
            platform_rows,
            data["platform"],
            data["task_id"],
            data["status"],
            data["published_date"],
            data["post_url"],
            proof,
            metrics_data,
        )
        touched_scripts.add(queue_row["script_id"])
    for script_id in touched_scripts:
        writeback.rollup_script_tracker(script_rows, platform_rows, script_id)
    issues = writeback.validate_rows(queue_fields, queue_rows, platform_fields, platform_rows, script_fields, script_rows)
    if issues:
        raise SystemExit("\n".join(issues))
    write_rows(writeback.QUEUE_PATH, queue_fields, queue_rows)
    write_rows(writeback.PLATFORM_TRACKER_PATH, platform_fields, platform_rows)
    write_rows(writeback.SCRIPT_TRACKER_PATH, script_fields, script_rows)
    writeback.regenerate_dependent_docs()


def render_markdown(packet: dict) -> str:
    metrics = packet["metrics"]
    lines = [
        "# LoveTypes Post Batch Import Quickstart",
        "",
        f"- 產生日期：{packet['generatedAt']}",
        f"- task：`{packet['taskId']}`",
        f"- 狀態：ready={metrics['readyRows']} / blocked={metrics['blockedRows']} / invalid={metrics['invalidRows']} / issues={metrics['issues']}",
        f"- check：`{packet['commands']['check']}`",
        f"- add all：`{packet['commands']['addAll']}`",
        "",
        "## Proof Files",
        "",
    ]
    for row in packet["rows"]:
        lines.append(
            f"- `{row['proofFile']}`：`{row.get('platform') or 'unknown'}` / `{row['status']}` / ready={row['ready']} / issues={len(row['issues'])}"
        )
    return "\n".join(lines).rstrip() + "\n"


def render_text(packet: dict) -> str:
    metrics = packet["metrics"]
    return "\n".join([
        f"generated: {packet['generatedAt']}",
        f"task: {packet['taskId']}",
        f"ready={metrics['readyRows']} blocked={metrics['blockedRows']} invalid={metrics['invalidRows']} issues={metrics['issues']}",
        f"check: {packet['commands']['check']}",
        f"add: {packet['commands']['addAll']}",
    ]) + "\n"


def write_outputs(packet: dict) -> None:
    public_packet = {
        "generatedAt": packet["generatedAt"],
        "taskId": packet["taskId"],
        "metrics": packet["metrics"],
        "rows": [
            {
                "p": row.get("platform", ""),
                "file": row["proofFile"],
                "status": row["status"],
                "ready": row["ready"],
                "issues": len(row["issues"]),
            }
            for row in packet["rows"]
        ],
        "issues": packet["issues"],
    }
    OUTPUT_JSON.write_text(json.dumps(public_packet, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(packet), encoding="utf-8")
    OUTPUT_TXT.write_text(render_text(packet), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check or import all first-batch public post proof files as one guarded batch.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--add", action="store_true")
    args = parser.parse_args()

    packet = build_packet()
    if args.add:
        apply_batch(packet)
        packet = build_packet()
    if not args.check:
        write_outputs(packet)
        print(f"promotion_post_batch_import_md={OUTPUT_MD.relative_to(ROOT)}")
        print(f"promotion_post_batch_import_json={OUTPUT_JSON.relative_to(ROOT)}")
        print(f"promotion_post_batch_import_txt={OUTPUT_TXT.relative_to(ROOT)}")
    metrics = packet["metrics"]
    print(f"promotion_post_batch_import_proof_files={metrics['proofFiles']}")
    print(f"promotion_post_batch_import_ready_rows={metrics['readyRows']}")
    print(f"promotion_post_batch_import_blocked_rows={metrics['blockedRows']}")
    print(f"promotion_post_batch_import_invalid_rows={metrics['invalidRows']}")
    print(f"promotion_post_batch_import_issues={metrics['issues']}")
    for issue in packet["issues"]:
        print(issue)
    return 1 if packet["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
