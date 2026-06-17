#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SHORTS_FACTORY = ROOT.parent
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
FIRST_BATCH_PACKET = PROMOTION_DIR / "first-batch-publication-packet.json"
PROMOTION_KIT = ROOT / "promotion-kit.json"
SCHEDULES = SHORTS_FACTORY.parent / "automation" / "local-scheduler" / "schedules.toml"
DEFAULT_OUTPUT_DIR = PROMOTION_DIR / "render-bridge"
DATA_CENTER_ROOT = Path(os.environ.get("PROJECT_DATA_CENTER_ROOT", "/Users/mac/Mounts/ProjectDataCenter"))
OUTPUTS_ROOT = DATA_CENTER_ROOT / "outputs"
JOBS_ROOT = DATA_CENTER_ROOT / "jobs"
LOOP_LIBRARY_ROOT = DATA_CENTER_ROOT / "assets" / "pika-loop-library"
CLAIM_GUARDRAILS = [
    "Do not claim official status.",
    "Do not claim original status.",
    "Do not claim science-backed validation.",
    "Do not imply the quiz diagnoses attachment style.",
    "Keep claims framed as self-reflection, not clinical advice.",
]
VOICE_ROLE_BY_GUARDIAN = {
    "iris": "heroine_warm",
    "noah": "mysterious_strong",
    "vivian": "bright_girl",
    "claire": "calm_analyst",
    "dora": "mature_narrator",
}
SCENE_IDS = ("hook", "mirror", "choices", "insight", "cta")
SCENE_DURATIONS = (2.5, 3.5, 7.0, 4.0, 6.0)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_tasks() -> dict[str, dict]:
    data = read_json(PROMOTION_KIT)
    return {str(task.get("taskId", "")): task for task in data.get("publishingTasks", [])}


def schedule_status() -> str:
    if not SCHEDULES.exists():
        return "unknown"
    text = SCHEDULES.read_text(encoding="utf-8")
    marker = 'id = "lovetypes-nightly-shorts-render"'
    if marker not in text:
        return "missing"
    tail = text.split(marker, 1)[1].split("[[schedules]]", 1)[0]
    for line in tail.splitlines():
        if line.strip().startswith("status"):
            return line.split("=", 1)[1].strip().strip('"')
    return "unknown"


def first_ready_rows(packet: dict) -> list[dict]:
    if not packet.get("readyToPublish"):
        return []
    return [
        row
        for row in packet.get("rows", [])
        if row.get("platform") == "youtube_shorts" and not row.get("published")
    ]


def output_exists(job_id: str) -> bool:
    if (OUTPUTS_ROOT / job_id).exists():
        return True
    return bool(list((SHORTS_FACTORY / "output").glob(f"**/{job_id}*")))


def job_queue_location(job_id: str) -> str:
    for state in ("pending", "in-progress", "done", "failed"):
        if (JOBS_ROOT / state / job_id).exists():
            return state
    return ""


def job_exists(job_id: str) -> bool:
    return output_exists(job_id) or bool(job_queue_location(job_id))


def choose_job_id(row: dict) -> tuple[str, int]:
    guardian = str(row.get("guardianId", "iris") or "iris")
    scheduled = str(row.get("scheduledDate") or date.today().isoformat())
    for week in range(51, 100):
        job_id = f"guardian-en-us-{scheduled}-{guardian}-w{week:02d}"
        if not job_exists(job_id):
            return job_id, week
    raise SystemExit(f"no unused promo job id available for {guardian} on {scheduled}")


def compress_subtitles(lines: list[str]) -> list[str]:
    cleaned = [line.strip() for line in lines if str(line).strip()]
    if len(cleaned) >= 5:
        return [
            cleaned[0],
            " ".join(cleaned[1:3]),
            " ".join(cleaned[3:6]),
            " ".join(cleaned[6:8]) if len(cleaned) > 7 else cleaned[-2],
            cleaned[-1],
        ]
    while len(cleaned) < 5:
        cleaned.append(cleaned[-1] if cleaned else "Take the quiz.")
    return cleaned[:5]


def visual_prompt(task: dict) -> str:
    guardian = str(task.get("guardianName") or task.get("guardianId") or "LoveTypes guardian")
    suggestions = task.get("visualSuggestions", [])
    base = str(suggestions[0]) if suggestions else f"{guardian} LoveTypes guardian, vertical relationship quiz card."
    return f"{base} Premium 9:16 YouTube Shorts composition, readable subtitle area, emotional fantasy garden style."


def build_script(row: dict, task: dict, job_id: str) -> dict:
    guardian = str(row.get("guardianId") or task.get("guardianId") or "iris")
    guardian_name = str(task.get("guardianName") or row.get("guardianName") or guardian.title())
    scheduled = str(row.get("scheduledDate") or date.today().isoformat())
    publish_at = f"{scheduled}T20:30:00+08:00"
    subtitles = compress_subtitles([str(item) for item in task.get("subtitleLines", [])])
    prompt = visual_prompt(task)
    narration = "\n".join(subtitles)
    scenes = []
    for scene_id, duration, subtitle in zip(SCENE_IDS, SCENE_DURATIONS, subtitles):
        scenes.append({
            "scene_id": scene_id,
            "duration": duration,
            "narration": subtitle,
            "image_prompt": prompt,
            "motion_prompt": "Use approved Pika guardian loop library motion plate. Keep the guardian stable and readable behind subtitles.",
            "subtitle": subtitle,
        })
    return {
        "id": job_id,
        "guardian_id": guardian,
        "guardian_name": guardian_name,
        "language": "zh-TW",
        "locale": "zh-TW",
        "market": "Taiwan",
        "scheduled_publish_time": publish_at,
        "publish_timezone": "Asia/Taipei",
        "target_platform": "youtube_shorts",
        "destination_url": str(row.get("trackedUrl") or task.get("trackedUrl") or "https://lovetypes.tw/start/"),
        "voice_role_id": VOICE_ROLE_BY_GUARDIAN.get(guardian, "heroine_warm"),
        "title": str(row.get("title") or task.get("title") or job_id),
        "hook": str(task.get("hook") or row.get("title") or ""),
        "narration": narration,
        "subtitle_text": subtitles,
        "scene_list": scenes,
        "visual_prompts": [prompt for _ in scenes],
        "description": str(row.get("caption") or task.get("caption") or ""),
        "hashtags": [tag for tag in str(row.get("caption") or "").split() if tag.startswith("#")] or [
            "#LoveTypes",
            "#EmotionalGuardian",
            "#RelationshipQuiz",
            "#LoveLanguage",
        ],
        "comment_cta": str(task.get("commentCta") or "Comment A, B, or C. Then take the quiz."),
        "claim_guardrails": CLAIM_GUARDRAILS,
        "source_promotion": {
            "task_id": row.get("taskId"),
            "script_id": row.get("scriptId"),
            "utm_content": row.get("utmContent"),
            "tracked_url": row.get("trackedUrl"),
            "caption": row.get("caption"),
            "primary_cta": row.get("primaryCta"),
        },
    }


def validate_script(script_path: Path) -> dict:
    result = subprocess.run(
        [sys.executable, "scripts/validate_script_json.py"],
        cwd=str(SHORTS_FACTORY),
        text=True,
        input=script_path.read_text(encoding="utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        payload = {"valid": False, "error": result.stdout.strip()}
    payload["returncode"] = result.returncode
    return payload


def count_guardian_loops(guardian_id: str) -> int:
    candidates = [
        LOOP_LIBRARY_ROOT / "guardians" / guardian_id / "loops",
        LOOP_LIBRARY_ROOT / "loops" / guardian_id,
    ]
    seen: set[Path] = set()
    for root in candidates:
        if not root.exists():
            continue
        seen.update(path.resolve() for path in root.glob("*.mp4") if path.is_file())
    return len(seen)


def select_guardian_loop(guardian_id: str, resolution: str = "720p") -> dict:
    result = subprocess.run(
        [
            sys.executable,
            str(SHORTS_FACTORY / "scripts" / "select_pika_loop_from_library.py"),
            "--guardian-id",
            guardian_id,
            "--library-root",
            str(LOOP_LIBRARY_ROOT),
            "--resolution",
            resolution,
        ],
        cwd=str(SHORTS_FACTORY),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode != 0:
        return {
            "ok": False,
            "resolution": resolution,
            "error": result.stdout.strip(),
        }
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {
            "ok": False,
            "resolution": resolution,
            "error": result.stdout.strip(),
        }
    return {
        "ok": True,
        "resolution": payload.get("resolution") or resolution,
        "selected_video": payload.get("selected_video"),
        "selected_metadata": payload.get("selected_metadata"),
        "variant_id": payload.get("variant_id"),
    }


def arthurnb_loop_availability(guardian_id: str, resolution: str = "720p") -> dict:
    remote_root = "/mnt/project-data-center/assets/pika-loop-library"
    code = f"""
import json
from pathlib import Path
guardian = {guardian_id!r}
root = Path({remote_root!r})
loops = sorted((root / "guardians" / guardian / "loops").glob("*.mp4")) if root.exists() else []
manifest = root / "guardians" / guardian / "metadata" / "approved_assets.json"
approved_count = 0
manifest_readable = False
if manifest.exists():
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        manifest_readable = True
        if isinstance(data, dict):
            data = data.get("assets", [])
        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue
                item_resolution = str(item.get("resolution") or item.get("pika_resolution_setting") or {resolution!r}).lower()
                if item.get("guardian_id") == guardian and item.get("approved_for_random_render") is True and {resolution!r} in item_resolution:
                    approved_count += 1
    except Exception:
        pass
print(json.dumps({{
    "ok": bool(root.exists() and loops and manifest_readable and approved_count > 0),
    "root": str(root),
    "root_exists": root.exists(),
    "loop_count": len(loops),
    "manifest": str(manifest),
    "manifest_exists": manifest.exists(),
    "manifest_readable": manifest_readable,
    "approved_manifest_count": approved_count,
    "resolution": {resolution!r},
}}, ensure_ascii=False))
"""
    result = subprocess.run(
        [
            "ssh",
            "-o",
            "BatchMode=yes",
            "-o",
            "ConnectTimeout=8",
            "arthurnb-wsl",
            f"python3 -c {shlex.quote(code)}",
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=15,
    )
    if result.returncode != 0:
        return {
            "ok": False,
            "root": remote_root,
            "resolution": resolution,
            "error": result.stdout.strip(),
        }
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {
            "ok": False,
            "root": remote_root,
            "resolution": resolution,
            "error": result.stdout.strip(),
        }


def render_preflight(rows: list[dict]) -> dict:
    guardians = sorted({str(row.get("guardianId") or "iris") for row in rows})
    required_paths = {
        "projectDataCenterRoot": DATA_CENTER_ROOT.exists(),
        "outputsRoot": OUTPUTS_ROOT.exists(),
        "jobsRoot": JOBS_ROOT.exists(),
        "loopLibraryRoot": LOOP_LIBRARY_ROOT.exists(),
    }
    loop_counts = {guardian: count_guardian_loops(guardian) for guardian in guardians}
    loop_selections = {guardian: select_guardian_loop(guardian) for guardian in guardians}
    arthur_loop_availability = {guardian: arthurnb_loop_availability(guardian) for guardian in guardians}
    busy_jobs: list[dict] = []
    for state in ("pending", "in-progress"):
        state_root = JOBS_ROOT / state
        if not state_root.exists():
            continue
        for path in sorted(state_root.iterdir()):
            if not path.is_dir():
                continue
            name = path.name
            if name.startswith("guardian-en-us-") or name.startswith("00-lovetypes-quiz-new-"):
                busy_jobs.append({"state": state, "jobId": name})
    issues: list[str] = []
    for label, available in required_paths.items():
        if not available:
            issues.append(f"required render path unavailable: {label}")
    for guardian, count in loop_counts.items():
        if count <= 0:
            issues.append(f"no approved loop mp4 found for guardian: {guardian}")
    for guardian, selection in loop_selections.items():
        if not selection.get("ok"):
            issues.append(f"local selector cannot choose approved 720p loop for guardian: {guardian}: {selection.get('error')}")
    for guardian, availability in arthur_loop_availability.items():
        if not availability.get("ok"):
            issues.append(f"ArthurNB cannot see approved 720p loop library for guardian: {guardian}: {availability}")
    return {
        "checkedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "projectDataCenterRoot": str(DATA_CENTER_ROOT),
        "requiredPaths": required_paths,
        "guardianLoopCounts": loop_counts,
        "guardianLoopSelections": loop_selections,
        "arthurNBRuntimeLoopAvailability": arthur_loop_availability,
        "busyRenderJobs": busy_jobs,
        "busyRenderJobCount": len(busy_jobs),
        "ready": not issues,
        "issues": issues,
    }


def write_handoff_run(output_dir: Path, payload: dict) -> dict:
    handoff_rows = []
    for row in payload.get("rows", []):
        handoff_rows.append({
            "job_id": row["renderJobId"],
            "status": "bridge_ready",
            "ready_for_desktop_publish": False,
            "script_json": row["scriptJson"],
            "expected_output": row["projectDataCenterOutput"],
            "source_task_id": row.get("taskId"),
            "validation": row.get("validation", {}),
        })
    run_id = payload["rows"][0]["renderJobId"] if len(payload.get("rows", [])) == 1 else f"promotion-bridge-{date.today().isoformat()}"
    run_dir = output_dir / "handoff" / run_id
    summary = {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "mode": "dry_run",
        "bridge_mode": "promotion_render_bridge",
        "ready_for_upload_queue": False,
        "safety": payload.get("safety", {}),
        "jobs": handoff_rows,
        "notes": [
            "This handoff does not contain rendered MP4 outputs.",
            "Upload queue creation must wait until ready_for_desktop_publish.json and the final MP4 exist under ProjectDataCenter outputs.",
        ],
    }
    results = {
        "generated_at": summary["generated_at"],
        "mode": summary["mode"],
        "jobs": handoff_rows,
    }
    write_json(run_dir / "nightly_summary.json", summary)
    write_json(run_dir / "nightly_results.json", results)
    return {
        "runDir": str(run_dir),
        "summary": str(run_dir / "nightly_summary.json"),
        "results": str(run_dir / "nightly_results.json"),
        "jobs": len(handoff_rows),
    }


def build_bridge(output_dir: Path, write_scripts: bool, include_render_preflight: bool) -> dict:
    packet = read_json(FIRST_BATCH_PACKET)
    tasks = load_tasks()
    rows = first_ready_rows(packet)
    bridge_rows = []
    for row in rows:
        task_id = str(row.get("taskId", ""))
        task = tasks.get(task_id, {})
        job_id, week = choose_job_id(row)
        script = build_script(row, task, job_id)
        script_path = output_dir / "scripts" / f"{job_id}.json"
        validation = {"valid": False, "error": "not written"}
        if write_scripts:
            write_json(script_path, script)
            validation = validate_script(script_path)
        bridge_rows.append({
            "platform": row.get("platform"),
            "taskId": task_id,
            "scriptId": row.get("scriptId"),
            "guardianId": row.get("guardianId"),
            "title": row.get("title"),
            "scheduledDate": row.get("scheduledDate"),
            "renderJobId": job_id,
            "renderWeek": week,
            "scriptJson": str(script_path),
            "projectDataCenterOutput": str(OUTPUTS_ROOT / job_id / f"{job_id}.mp4"),
            "nightlyCompatible": True,
            "uploadQueueCompatible": False,
            "uploadQueueCompatibleAfterRender": True,
            "validation": validation,
            "existingJobQueueLocation": job_queue_location(job_id),
        })
    issues: list[str] = []
    if schedule_status() != "PAUSED":
        issues.append("lovetypes-nightly-shorts-render schedule is not PAUSED")
    if not rows:
        issues.append("no ready unpublished YouTube Shorts rows found")
    for item in bridge_rows:
        validation = item.get("validation", {})
        if write_scripts and not validation.get("valid"):
            issues.append(f"{item['renderJobId']}: script validation failed: {validation.get('error')}")
        if item.get("existingJobQueueLocation"):
            issues.append(f"{item['renderJobId']}: job already exists in {item['existingJobQueueLocation']}")
    preflight = render_preflight(rows) if include_render_preflight else None
    if preflight:
        issues.extend(preflight["issues"])
    return {
        "generatedAt": date.today().isoformat(),
        "mode": "write" if write_scripts else "check",
        "safety": {
            "doesNotModifySchedules": True,
            "doesNotSubmitRemoteRender": True,
            "doesNotCreateUploadQueueJobs": True,
            "nightlyScheduleStatus": schedule_status(),
        },
        "sources": {
            "firstBatchPublicationPacket": str(FIRST_BATCH_PACKET),
            "promotionKit": str(PROMOTION_KIT),
            "nightlyRenderer": str(SHORTS_FACTORY / "scripts/run_lovetypes_nightly_render.py"),
            "uploadQueueCreator": str(SHORTS_FACTORY / "scripts/create_lovetypes_upload_jobs_from_nightly.py"),
        },
        "metrics": {
            "readyRows": len(rows),
            "bridgeRows": len(bridge_rows),
            "validScripts": sum(1 for item in bridge_rows if item.get("validation", {}).get("valid")),
            "renderPreflightReady": preflight["ready"] if preflight else None,
            "issues": len(issues),
        },
        "rows": bridge_rows,
        "renderPreflight": preflight,
        "nextCommands": [
            "PROJECT_DATA_CENTER_ROOT=/Users/mac/Mounts/ProjectDataCenter python3 scripts/run_lovetypes_nightly_render.py --dry-run --same-day --run-label promo-check",
            "Only after manual approval: submit a single adapted render job; do not resume lovetypes-nightly-shorts-render schedule.",
        ],
        "issues": issues,
    }


def render_markdown(payload: dict) -> str:
    lines = [
        "# LoveTypes Render Bridge",
        "",
        f"- generated：{payload['generatedAt']}",
        f"- mode：`{payload['mode']}`",
        f"- nightly schedule：`{payload['safety']['nightlyScheduleStatus']}`",
        f"- ready rows：{payload['metrics']['readyRows']}",
        f"- bridge rows：{payload['metrics']['bridgeRows']}",
        f"- valid scripts：{payload['metrics']['validScripts']}",
        f"- render preflight ready：`{payload['metrics']['renderPreflightReady']}`",
        f"- issues：{payload['metrics']['issues']}",
        "",
        "## Safety",
        "",
        "- Does not modify schedules.",
        "- Does not submit remote render jobs.",
        "- Does not create YouTube upload queue jobs.",
        "",
        "## Rows",
        "",
    ]
    for row in payload["rows"]:
        lines.extend([
            f"### `{row['renderJobId']}`",
            "",
            f"- task：`{row['taskId']}`",
            f"- title：{row['title']}",
            f"- script JSON：`{row['scriptJson']}`",
            f"- expected output：`{row['projectDataCenterOutput']}`",
            f"- validation：`{row['validation'].get('valid')}`",
            f"- upload queue compatible now：`{row['uploadQueueCompatible']}`",
            f"- upload queue compatible after render：`{row['uploadQueueCompatibleAfterRender']}`",
            "",
        ])
    preflight = payload.get("renderPreflight")
    if preflight:
        lines.extend([
            "## Render Preflight",
            "",
            f"- ProjectDataCenter：`{preflight['projectDataCenterRoot']}`",
            f"- ready：`{preflight['ready']}`",
            f"- busy render jobs：{preflight['busyRenderJobCount']}",
            f"- guardian loop counts：`{preflight['guardianLoopCounts']}`",
            "",
        ])
    if payload["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in payload["issues"])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Bridge LoveTypes promotion tasks to the paused nightly Shorts render format without touching schedules.")
    parser.add_argument("--check", action="store_true", help="Validate bridge candidates without writing script JSON files.")
    parser.add_argument("--include-render-preflight", action="store_true", help="Also verify ProjectDataCenter paths, job queues, and approved guardian loop availability.")
    parser.add_argument("--write-handoff", action="store_true", help="Write a nightly-style dry-run handoff directory for later manual render approval.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    payload = build_bridge(output_dir, write_scripts=not args.check, include_render_preflight=args.include_render_preflight)
    if not args.check:
        write_json(output_dir / "render-bridge.json", payload)
        (output_dir / "render-bridge.md").write_text(render_markdown(payload), encoding="utf-8")
        if args.write_handoff:
            handoff = write_handoff_run(output_dir, payload)
            payload["handoff"] = handoff
            write_json(output_dir / "render-bridge.json", payload)
    metrics = payload["metrics"]
    print(f"promotion_render_bridge_mode={payload['mode']}")
    print(f"promotion_render_bridge_schedule_status={payload['safety']['nightlyScheduleStatus']}")
    print(f"promotion_render_bridge_ready_rows={metrics['readyRows']}")
    print(f"promotion_render_bridge_rows={metrics['bridgeRows']}")
    print(f"promotion_render_bridge_valid_scripts={metrics['validScripts']}")
    print(f"promotion_render_bridge_render_preflight_ready={metrics['renderPreflightReady']}")
    print(f"promotion_render_bridge_issues={metrics['issues']}")
    for row in payload["rows"]:
        print(f"promotion_render_bridge_job={row['renderJobId']}")
        print(f"promotion_render_bridge_script={row['scriptJson']}")
    if payload.get("handoff"):
        print(f"promotion_render_bridge_handoff_run_dir={payload['handoff']['runDir']}")
    for issue in payload["issues"]:
        print(issue)
    return 1 if payload["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
