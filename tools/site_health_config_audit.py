#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import py_compile
import re
import shutil
import subprocess
from collections import Counter
from pathlib import Path
from typing import NamedTuple


ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = ROOT / "tools" / "site_health_summary.py"
PREDEPLOY_PATH = ROOT / "tools" / "predeploy_check.py"
SITE_HEALTH_PATH = ROOT / "site-health.json"
RELEASE_PATH = ROOT / "release.json"
PUBLIC_DEPLOY_PATH = ROOT / "tools" / "public_deploy_smoke.py"
ISSUE_KEY_RE = re.compile(r"([A-Za-z0-9_:-]*(?:_issues|issues))=")
NODE_FALLBACK_PATH = Path("/Users/mac/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node")
SITE_HEALTH_LOCAL_AUDIT_TOOLS = {
    "site_quality": "tools/site_quality_audit.py",
    "content_uniqueness": "tools/content_uniqueness_audit.py",
    "multilingual_routes": "tools/multilingual_route_audit.py",
    "guardian_conversion": "tools/guardian_conversion_audit.py",
    "affiliate_locale": "tools/affiliate_locale_audit.py",
    "promotion_writeback_flow": "tools/promotion_writeback_flow_audit.py",
    "platform_kpi_tracker": "tools/promotion_platform_kpi_tracker.py",
    "publishing_status": "tools/promotion_publishing_status.py",
    "launch_readiness": "tools/promotion_launch_readiness_gate.py",
    "launch_command_center": "tools/promotion_launch_command_center.py",
    "accessibility": "tools/accessibility_audit.py",
    "image_assets": "tools/image_asset_audit.py",
    "performance_budget": "tools/performance_budget_audit.py",
}


class HealthCheck(NamedTuple):
    name: str
    command: str
    script_paths: list[str]
    timeout: int | None
    is_public: bool | None


def literal_strings(node: ast.AST) -> list[str]:
    if not isinstance(node, (ast.List, ast.Set)):
        return []
    return [item.value for item in node.elts if isinstance(item, ast.Constant) and isinstance(item.value, str)]


def literal_dict_keys(node: ast.AST) -> list[str]:
    if not isinstance(node, ast.Dict):
        return []
    return [key.value for key in node.keys if isinstance(key, ast.Constant) and isinstance(key.value, str)]


def parse_summary() -> tuple[list[str], list[str], list[str], list[str], list[str], list[HealthCheck]]:
    tree = ast.parse(SUMMARY_PATH.read_text(encoding="utf-8"))
    check_names: list[str] = []
    check_commands: list[str] = []
    check_script_paths: list[str] = []
    important_keys: list[str] = []
    retry_names: list[str] = []
    health_checks: list[HealthCheck] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "CHECKS" and isinstance(node.value, ast.List):
                for item in node.value.elts:
                    if not isinstance(item, ast.Tuple) or len(item.elts) < 2:
                        continue
                    name_node, command_node = item.elts[0], item.elts[1]
                    timeout_node = item.elts[2] if len(item.elts) > 2 else None
                    is_public_node = item.elts[3] if len(item.elts) > 3 else None
                    name = name_node.value if isinstance(name_node, ast.Constant) and isinstance(name_node.value, str) else ""
                    timeout = (
                        timeout_node.value
                        if isinstance(timeout_node, ast.Constant) and isinstance(timeout_node.value, int)
                        else None
                    )
                    is_public = (
                        is_public_node.value
                        if isinstance(is_public_node, ast.Constant) and isinstance(is_public_node.value, bool)
                        else None
                    )
                    if name:
                        check_names.append(name)
                    if isinstance(command_node, ast.List):
                        parts = [
                            part.value
                            for part in command_node.elts
                            if isinstance(part, ast.Constant) and isinstance(part.value, str)
                        ]
                        if parts:
                            check_commands.append(" ".join(parts))
                        check_script_paths.extend(part for part in parts if part.startswith("tools/"))
                        if name:
                            health_checks.append(
                                HealthCheck(
                                    name=name,
                                    command=" ".join(parts),
                                    script_paths=[part for part in parts if part.startswith("tools/")],
                                    timeout=timeout,
                                    is_public=is_public,
                                )
                            )
            if isinstance(target, ast.Name) and target.id == "important_keys":
                important_keys.extend(literal_strings(node.value))
            if isinstance(target, ast.Name) and target.id == "RETRY_ON_FAILURE":
                retry_names.extend(literal_strings(node.value))
    return check_names, check_commands, check_script_paths, important_keys, retry_names, health_checks


def parse_predeploy_script_paths() -> list[str]:
    tree = ast.parse(PREDEPLOY_PATH.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if any(isinstance(target, ast.Name) and target.id == "PYTHON_TOOLS" for target in node.targets):
            return [path for path in literal_strings(node.value) if path.startswith("tools/")]
    return []


def release_verification_script_paths() -> list[str]:
    try:
        data = json.loads(RELEASE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []
    commands = data.get("verificationCommands") if isinstance(data, dict) else None
    if not isinstance(commands, list):
        return []
    paths: list[str] = []
    for command in commands:
        if not isinstance(command, str):
            continue
        paths.extend(part for part in command.split() if part.startswith("tools/"))
    return paths


def release_local_audit_script_paths() -> list[str]:
    try:
        data = json.loads(RELEASE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []
    coverage = data.get("localAuditCoverage") if isinstance(data, dict) else None
    if not isinstance(coverage, dict):
        return []
    paths: list[str] = []
    for values in coverage.values():
        if not isinstance(values, list):
            continue
        paths.extend(value for value in values if isinstance(value, str) and value.startswith("tools/"))
    return paths


def site_health_local_audit_tools() -> tuple[list[str], list[str]]:
    try:
        data = json.loads(SITE_HEALTH_PATH.read_text(encoding="utf-8"))
    except Exception:
        return [], []
    coverage = data.get("localAuditCoverage") if isinstance(data, dict) else None
    if not isinstance(coverage, dict):
        return [], []
    names: list[str] = []
    unknown: list[str] = []
    for values in coverage.values():
        if not isinstance(values, list):
            continue
        for value in values:
            if not isinstance(value, str):
                continue
            names.append(value)
            if value not in SITE_HEALTH_LOCAL_AUDIT_TOOLS:
                unknown.append(value)
    tools = [SITE_HEALTH_LOCAL_AUDIT_TOOLS[name] for name in names if name in SITE_HEALTH_LOCAL_AUDIT_TOOLS]
    return tools, unknown


def emitted_issue_keys(script_paths: list[str]) -> list[str]:
    keys: set[str] = set()
    for path in sorted(set(script_paths)):
        source_path = ROOT / path
        if not source_path.exists():
            continue
        source = source_path.read_text(encoding="utf-8", errors="replace")
        keys.update(match.group(1) for match in ISSUE_KEY_RE.finditer(source))
    return sorted(keys)


def find_node() -> str:
    candidate = shutil.which("node")
    if candidate:
        return candidate
    if NODE_FALLBACK_PATH.exists():
        return str(NODE_FALLBACK_PATH)
    return ""


def duplicates(values: list[str]) -> list[str]:
    counts = Counter(values)
    return sorted(value for value, count in counts.items() if count > 1)


def mixed_return_tuple_functions(script_paths: list[str]) -> list[str]:
    mixed: list[str] = []
    for path in sorted(set(script_paths)):
        if not path.endswith(".py"):
            continue
        source_path = ROOT / path
        if not source_path.exists():
            continue
        try:
            tree = ast.parse(source_path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            tuple_return_sizes = sorted(
                {
                    len(child.value.elts)
                    for child in ast.walk(node)
                    if isinstance(child, ast.Return) and isinstance(child.value, ast.Tuple)
                }
            )
            if len(tuple_return_sizes) > 1:
                sizes = ",".join(str(size) for size in tuple_return_sizes)
                mixed.append(f"{path}:{node.name}[{sizes}]")
    return mixed


def public_smoke_tools() -> list[str]:
    return sorted(
        str(path.relative_to(ROOT))
        for path in (ROOT / "tools").glob("public_*")
        if path.suffix in {".py", ".js", ".mjs"}
    )


def site_health_support_files() -> list[str]:
    try:
        data = json.loads(SITE_HEALTH_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []
    support_files = data.get("supportFiles") if isinstance(data, dict) else None
    if not isinstance(support_files, list):
        return []
    return sorted(f"/{path}" for path in support_files if isinstance(path, str) and path)


def public_deploy_support_files() -> list[str]:
    tree = ast.parse(PUBLIC_DEPLOY_PATH.read_text(encoding="utf-8"))
    paths: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "SUPPORT_FILES":
                paths.update(literal_dict_keys(node.value))
            if isinstance(target, ast.Name) and target.id == "DEDICATED_SUPPORT_FILES":
                paths.update(literal_strings(node.value))
    return sorted(paths)


def main() -> int:
    issues: list[str] = []
    check_names, check_commands, check_script_paths, important_keys, retry_names, health_checks = parse_summary()
    predeploy_script_paths = parse_predeploy_script_paths()
    release_script_paths = release_verification_script_paths()
    release_local_audit_scripts = release_local_audit_script_paths()
    site_health_local_audit_scripts, unknown_site_health_local_audits = site_health_local_audit_tools()
    issue_keys = emitted_issue_keys(check_script_paths + predeploy_script_paths)
    duplicate_check_names = duplicates(check_names)
    duplicate_check_commands = duplicates(check_commands)
    duplicate_script_paths = duplicates(check_script_paths)
    duplicate_important_keys = duplicates(important_keys)
    unknown_retry_names = sorted(set(retry_names).difference(check_names))
    missing_issue_important_keys = sorted(set(issue_keys).difference(important_keys))
    malformed_checks = sorted(check.name for check in health_checks if check.timeout is None or check.is_public is None)
    invalid_timeouts = sorted(
        check.name for check in health_checks if check.timeout is None or check.timeout <= 0 or check.timeout > 1800
    )
    mixed_return_functions = mixed_return_tuple_functions(check_script_paths + predeploy_script_paths)
    public_tools = public_smoke_tools()
    missing_public_tools = sorted(set(public_tools).difference(check_script_paths))
    site_support_files = site_health_support_files()
    deploy_support_files = public_deploy_support_files()
    missing_deploy_support_files = sorted(set(site_support_files).difference(deploy_support_files))
    extra_deploy_support_files = sorted(set(deploy_support_files).difference(site_support_files))
    missing_release_verification_scripts = sorted(set(release_script_paths).difference(check_script_paths))
    missing_release_local_audit_scripts = sorted(set(release_local_audit_scripts).difference(predeploy_script_paths))
    missing_site_health_local_audit_scripts = sorted(set(site_health_local_audit_scripts).difference(predeploy_script_paths))
    site_health_release_local_audit_mismatches = sorted(
        set(site_health_local_audit_scripts).symmetric_difference(release_local_audit_scripts)
    )
    public_flag_mismatches: list[str] = []
    for check in health_checks:
        expected_public = (
            check.name.startswith("public_")
            or check.name
            in {
                "contrast_smoke",
                "csp_runtime_smoke",
                "keyboard_navigation_smoke",
                "runtime_performance_smoke",
                "storage_privacy_smoke",
                "tap_target_smoke",
                "user_preferences_smoke",
            }
        )
        if check.is_public is not None and check.is_public != expected_public:
            public_flag_mismatches.append(f"{check.name}: expected {expected_public}, got {check.is_public}")
    if duplicate_check_names:
        issues.append(f"duplicate CHECKS names: {', '.join(duplicate_check_names)}")
    if duplicate_check_commands:
        issues.append(f"duplicate CHECKS commands: {', '.join(duplicate_check_commands)}")
    if duplicate_script_paths:
        issues.append(f"duplicate CHECKS script paths: {', '.join(duplicate_script_paths)}")
    if duplicate_important_keys:
        issues.append(f"duplicate important_keys: {', '.join(duplicate_important_keys)}")
    if unknown_retry_names:
        issues.append(f"unknown RETRY_ON_FAILURE names: {', '.join(unknown_retry_names)}")
    if missing_issue_important_keys:
        issues.append(f"issue metrics missing from important_keys: {', '.join(missing_issue_important_keys)}")
    if malformed_checks:
        issues.append(f"malformed CHECKS tuples: {', '.join(malformed_checks)}")
    if invalid_timeouts:
        issues.append(f"invalid CHECKS timeouts: {', '.join(invalid_timeouts)}")
    if public_flag_mismatches:
        issues.append(f"CHECKS public flag mismatches: {', '.join(public_flag_mismatches)}")
    if mixed_return_functions:
        issues.append(f"mixed tuple return sizes in Python tools: {', '.join(mixed_return_functions)}")
    if missing_public_tools:
        issues.append(f"public smoke tools missing from site health CHECKS: {', '.join(missing_public_tools)}")
    if missing_deploy_support_files or extra_deploy_support_files:
        issues.append(
            "public deploy support file coverage mismatch: "
            f"missing={missing_deploy_support_files} extra={extra_deploy_support_files}"
        )
    if missing_release_verification_scripts:
        issues.append(
            "release verification scripts missing from site health CHECKS: "
            f"{', '.join(missing_release_verification_scripts)}"
        )
    if missing_release_local_audit_scripts:
        issues.append(
            "release local audit scripts missing from predeploy PYTHON_TOOLS: "
            f"{', '.join(missing_release_local_audit_scripts)}"
        )
    if unknown_site_health_local_audits:
        issues.append(f"unknown site-health local audit names: {', '.join(sorted(unknown_site_health_local_audits))}")
    if missing_site_health_local_audit_scripts:
        issues.append(
            "site-health local audit scripts missing from predeploy PYTHON_TOOLS: "
            f"{', '.join(missing_site_health_local_audit_scripts)}"
        )
    if site_health_release_local_audit_mismatches:
        issues.append(
            "site-health and release local audit coverage mismatch: "
            f"{', '.join(site_health_release_local_audit_mismatches)}"
        )
    missing_scripts = sorted(path for path in check_script_paths if not (ROOT / path).exists())
    if missing_scripts:
        issues.append(f"missing CHECKS scripts: {', '.join(missing_scripts)}")
    missing_predeploy_scripts = sorted(path for path in predeploy_script_paths if not (ROOT / path).exists())
    if missing_predeploy_scripts:
        issues.append(f"missing predeploy PYTHON_TOOLS scripts: {', '.join(missing_predeploy_scripts)}")
    compiled_python_scripts = 0
    compiled_predeploy_python_scripts = 0
    checked_node_scripts = 0
    node_bin = find_node()
    for path in sorted(set(check_script_paths)):
        if not path.endswith(".py"):
            continue
        try:
            py_compile.compile(str(ROOT / path), doraise=True)
            compiled_python_scripts += 1
        except py_compile.PyCompileError as error:
            issues.append(f"{path}: py_compile failed: {error.msg}")
    for path in sorted(set(predeploy_script_paths)):
        if not path.endswith(".py") or not (ROOT / path).exists():
            continue
        try:
            py_compile.compile(str(ROOT / path), doraise=True)
            compiled_predeploy_python_scripts += 1
        except py_compile.PyCompileError as error:
            issues.append(f"{path}: predeploy py_compile failed: {error.msg}")
    node_script_paths = sorted({path for path in check_script_paths if path.endswith((".js", ".mjs"))})
    if node_script_paths and not node_bin:
        issues.append("node executable not found for CHECKS JavaScript syntax checks")
    if node_bin:
        for path in node_script_paths:
            result = subprocess.run(
                [node_bin, "--check", str(ROOT / path)],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            if result.returncode == 0:
                checked_node_scripts += 1
            else:
                output = " ".join(result.stdout.split())
                issues.append(f"{path}: node --check failed: {output}")
    if not check_names:
        issues.append("CHECKS list not found")
    if not important_keys:
        issues.append("important_keys list not found")
    if not retry_names:
        issues.append("RETRY_ON_FAILURE set not found")

    print(f"site_health_config_checks={len(check_names)}")
    print(f"site_health_config_check_tuples_parsed={len(health_checks)}")
    print(f"site_health_config_commands={len(check_commands)}")
    print(f"site_health_config_scripts={len(check_script_paths)}")
    print(f"site_health_config_python_scripts_compiled={compiled_python_scripts}")
    print(f"site_health_config_node_scripts={len(node_script_paths)}")
    print(f"site_health_config_node_scripts_checked={checked_node_scripts}")
    print(f"site_health_config_node_missing={0 if node_bin else 1}")
    print(f"site_health_config_important_keys={len(important_keys)}")
    print(f"site_health_config_retry_names={len(retry_names)}")
    print(f"site_health_config_predeploy_scripts={len(predeploy_script_paths)}")
    print(f"site_health_config_predeploy_python_scripts_compiled={compiled_predeploy_python_scripts}")
    print(f"site_health_config_missing_predeploy_scripts={len(missing_predeploy_scripts)}")
    print(f"site_health_config_release_verification_scripts={len(release_script_paths)}")
    print(f"site_health_config_missing_release_verification_scripts={len(missing_release_verification_scripts)}")
    print(f"site_health_config_release_local_audit_scripts={len(release_local_audit_scripts)}")
    print(f"site_health_config_missing_release_local_audit_scripts={len(missing_release_local_audit_scripts)}")
    print(f"site_health_config_site_health_local_audit_scripts={len(site_health_local_audit_scripts)}")
    print(f"site_health_config_unknown_site_health_local_audits={len(unknown_site_health_local_audits)}")
    print(f"site_health_config_missing_site_health_local_audit_scripts={len(missing_site_health_local_audit_scripts)}")
    print(f"site_health_config_site_health_release_local_audit_mismatches={len(site_health_release_local_audit_mismatches)}")
    print(f"site_health_config_issue_metric_keys={len(issue_keys)}")
    print(f"site_health_config_duplicate_check_names={len(duplicate_check_names)}")
    print(f"site_health_config_duplicate_check_commands={len(duplicate_check_commands)}")
    print(f"site_health_config_duplicate_script_paths={len(duplicate_script_paths)}")
    print(f"site_health_config_missing_scripts={len(missing_scripts)}")
    print(f"site_health_config_duplicate_important_keys={len(duplicate_important_keys)}")
    print(f"site_health_config_unknown_retry_names={len(unknown_retry_names)}")
    print(f"site_health_config_missing_issue_important_keys={len(missing_issue_important_keys)}")
    print(f"site_health_config_malformed_checks={len(malformed_checks)}")
    print(f"site_health_config_invalid_timeouts={len(invalid_timeouts)}")
    print(f"site_health_config_public_flag_mismatches={len(public_flag_mismatches)}")
    print(f"site_health_config_mixed_return_tuple_functions={len(mixed_return_functions)}")
    print(f"site_health_config_public_smoke_tools={len(public_tools)}")
    print(f"site_health_config_missing_public_smoke_tools={len(missing_public_tools)}")
    print(f"site_health_config_site_support_files={len(site_support_files)}")
    print(f"site_health_config_public_deploy_support_files={len(deploy_support_files)}")
    print(f"site_health_config_public_deploy_missing_support_files={len(missing_deploy_support_files)}")
    print(f"site_health_config_public_deploy_extra_support_files={len(extra_deploy_support_files)}")
    print(f"site_health_config_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
