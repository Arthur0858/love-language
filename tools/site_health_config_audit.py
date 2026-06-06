#!/usr/bin/env python3
from __future__ import annotations

import ast
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = ROOT / "tools" / "site_health_summary.py"


def literal_strings(node: ast.AST) -> list[str]:
    if not isinstance(node, ast.List):
        return []
    return [item.value for item in node.elts if isinstance(item, ast.Constant) and isinstance(item.value, str)]


def parse_summary() -> tuple[list[str], list[str], list[str]]:
    tree = ast.parse(SUMMARY_PATH.read_text(encoding="utf-8"))
    check_names: list[str] = []
    check_commands: list[str] = []
    important_keys: list[str] = []
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
            if isinstance(target, ast.Name) and target.id == "important_keys":
                important_keys.extend(literal_strings(node.value))
    return check_names, check_commands, important_keys


def duplicates(values: list[str]) -> list[str]:
    counts = Counter(values)
    return sorted(value for value, count in counts.items() if count > 1)


def main() -> int:
    issues: list[str] = []
    check_names, check_commands, important_keys = parse_summary()
    duplicate_check_names = duplicates(check_names)
    duplicate_check_commands = duplicates(check_commands)
    duplicate_important_keys = duplicates(important_keys)
    if duplicate_check_names:
        issues.append(f"duplicate CHECKS names: {', '.join(duplicate_check_names)}")
    if duplicate_check_commands:
        issues.append(f"duplicate CHECKS commands: {', '.join(duplicate_check_commands)}")
    if duplicate_important_keys:
        issues.append(f"duplicate important_keys: {', '.join(duplicate_important_keys)}")
    if not check_names:
        issues.append("CHECKS list not found")
    if not important_keys:
        issues.append("important_keys list not found")

    print(f"site_health_config_checks={len(check_names)}")
    print(f"site_health_config_commands={len(check_commands)}")
    print(f"site_health_config_important_keys={len(important_keys)}")
    print(f"site_health_config_duplicate_check_names={len(duplicate_check_names)}")
    print(f"site_health_config_duplicate_check_commands={len(duplicate_check_commands)}")
    print(f"site_health_config_duplicate_important_keys={len(duplicate_important_keys)}")
    print(f"site_health_config_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
