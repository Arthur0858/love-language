#!/usr/bin/env python3
from __future__ import annotations

import ast
import py_compile
import re
import shutil
import subprocess
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = ROOT / "tools" / "site_health_summary.py"
PREDEPLOY_PATH = ROOT / "tools" / "predeploy_check.py"
ISSUE_KEY_RE = re.compile(r"([A-Za-z0-9_:-]*(?:_issues|issues))=")
NODE_FALLBACK_PATH = Path("/Users/mac/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node")


def literal_strings(node: ast.AST) -> list[str]:
    if not isinstance(node, (ast.List, ast.Set)):
        return []
    return [item.value for item in node.elts if isinstance(item, ast.Constant) and isinstance(item.value, str)]


def parse_summary() -> tuple[list[str], list[str], list[str], list[str], list[str]]:
    tree = ast.parse(SUMMARY_PATH.read_text(encoding="utf-8"))
    check_names: list[str] = []
    check_commands: list[str] = []
    check_script_paths: list[str] = []
    important_keys: list[str] = []
    retry_names: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "CHECKS" and isinstance(node.value, ast.List):
                for item in node.value.elts:
                    if not isinstance(item, ast.Tuple) or len(item.elts) < 2:
                        continue
                    name_node, command_node = item.elts[0], item.elts[1]
                    if isinstance(name_node, ast.Constant) and isinstance(name_node.value, str):
                        check_names.append(name_node.value)
                    if isinstance(command_node, ast.List):
                        parts = [
                            part.value
                            for part in command_node.elts
                            if isinstance(part, ast.Constant) and isinstance(part.value, str)
                        ]
                        if parts:
                            check_commands.append(" ".join(parts))
                        check_script_paths.extend(part for part in parts if part.startswith("tools/"))
            if isinstance(target, ast.Name) and target.id == "important_keys":
                important_keys.extend(literal_strings(node.value))
            if isinstance(target, ast.Name) and target.id == "RETRY_ON_FAILURE":
                retry_names.extend(literal_strings(node.value))
    return check_names, check_commands, check_script_paths, important_keys, retry_names


def parse_predeploy_script_paths() -> list[str]:
    tree = ast.parse(PREDEPLOY_PATH.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if any(isinstance(target, ast.Name) and target.id == "PYTHON_TOOLS" for target in node.targets):
            return [path for path in literal_strings(node.value) if path.startswith("tools/")]
    return []


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


def main() -> int:
    issues: list[str] = []
    check_names, check_commands, check_script_paths, important_keys, retry_names = parse_summary()
    predeploy_script_paths = parse_predeploy_script_paths()
    issue_keys = emitted_issue_keys(check_script_paths + predeploy_script_paths)
    duplicate_check_names = duplicates(check_names)
    duplicate_check_commands = duplicates(check_commands)
    duplicate_script_paths = duplicates(check_script_paths)
    duplicate_important_keys = duplicates(important_keys)
    unknown_retry_names = sorted(set(retry_names).difference(check_names))
    missing_issue_important_keys = sorted(set(issue_keys).difference(important_keys))
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
    print(f"site_health_config_issue_metric_keys={len(issue_keys)}")
    print(f"site_health_config_duplicate_check_names={len(duplicate_check_names)}")
    print(f"site_health_config_duplicate_check_commands={len(duplicate_check_commands)}")
    print(f"site_health_config_duplicate_script_paths={len(duplicate_script_paths)}")
    print(f"site_health_config_missing_scripts={len(missing_scripts)}")
    print(f"site_health_config_duplicate_important_keys={len(duplicate_important_keys)}")
    print(f"site_health_config_unknown_retry_names={len(unknown_retry_names)}")
    print(f"site_health_config_missing_issue_important_keys={len(missing_issue_important_keys)}")
    print(f"site_health_config_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
