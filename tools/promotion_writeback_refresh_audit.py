#!/usr/bin/env python3
from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
WRITEBACK_TOOLS = (
    "promotion_profile_writeback.py",
    "promotion_post_writeback.py",
    "promotion_lead_writeback.py",
)
TEXT_IMPORT_TOOLS = (
    "promotion_profile_text_import.py",
    "promotion_post_text_import.py",
    "promotion_lead_text_import.py",
)


def read_source(name: str) -> str:
    return (TOOLS / name).read_text(encoding="utf-8")


def has_function_call(source: str, function_name: str, attr_name: str = "") -> bool:
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id == function_name:
            return True
        if attr_name and isinstance(func, ast.Attribute) and func.attr == attr_name:
            return True
    return False


def validate() -> tuple[dict[str, int], list[str]]:
    issues: list[str] = []
    writeback_refresh = 0
    text_import_refresh = 0

    helper = read_source("promotion_refresh.py")
    if "promotion_daily_ops_refresh.py" not in helper:
        issues.append("promotion_refresh.py must call promotion_daily_ops_refresh.py")
    if "LOVETYPES_PROMOTION_DAILY_REFRESH_RUNNING" not in helper:
        issues.append("promotion_refresh.py must guard against nested refresh")

    for name in WRITEBACK_TOOLS:
        source = read_source(name)
        if "import promotion_refresh" not in source:
            issues.append(f"{name}: missing promotion_refresh import")
        if "def regenerate_dependent_docs" not in source:
            issues.append(f"{name}: missing regenerate_dependent_docs")
            continue
        if "promotion_refresh.run_daily_ops_refresh()" not in source:
            issues.append(f"{name}: regenerate_dependent_docs must run full daily ops refresh")
        else:
            writeback_refresh += 1

    for name in TEXT_IMPORT_TOOLS:
        source = read_source(name)
        if "regenerate_dependent_docs()" not in source:
            issues.append(f"{name}: add path must trigger writeback.regenerate_dependent_docs")
        else:
            text_import_refresh += 1

    metrics = {
        "writebackTools": len(WRITEBACK_TOOLS),
        "writebackFullRefresh": writeback_refresh,
        "textImportTools": len(TEXT_IMPORT_TOOLS),
        "textImportRefresh": text_import_refresh,
    }
    return metrics, issues


def main() -> int:
    metrics, issues = validate()
    print(f"promotion_writeback_refresh_writeback_tools={metrics['writebackTools']}")
    print(f"promotion_writeback_refresh_writeback_full_refresh={metrics['writebackFullRefresh']}")
    print(f"promotion_writeback_refresh_text_import_tools={metrics['textImportTools']}")
    print(f"promotion_writeback_refresh_text_import_refresh={metrics['textImportRefresh']}")
    print(f"promotion_writeback_refresh_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())

