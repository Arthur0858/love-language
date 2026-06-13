#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PATH = ROOT / "tools" / "generate_multilingual_site.py"
IMPORT_TOOL = ROOT / "tools" / "promotion_lead_text_import.py"
SOURCES = {
    "contact": "source_contact",
    "keepsake_waitlist": "source_keepsake",
}
SAMPLE_BY_LANG = {
    "zh": {
        "guardian": "艾莉絲 · 肯定的言詞",
        "asset": "PDF 練習卡",
        "context": "睡前整理，想要可列印版本",
    },
    "en": {
        "guardian": "Iris · Words of Affirmation",
        "asset": "PDF practice card",
        "context": "Bedtime reflection and printable practice.",
    },
    "ja": {
        "guardian": "Iris · 肯定の言葉",
        "asset": "PDF ワークカード",
        "context": "寝る前の整理に使いたいです。",
    },
    "ko": {
        "guardian": "Iris · 인정의 말",
        "asset": "PDF 연습 카드",
        "context": "잠들기 전 정리에 쓰고 싶어요.",
    },
    "es": {
        "guardian": "Iris · Palabras de afirmación",
        "asset": "Tarjeta PDF de práctica",
        "context": "Reflexión antes de dormir y versión imprimible.",
    },
}


def load_generator():
    spec = importlib.util.spec_from_file_location("lovetypes_generator_for_lead_import_audit", GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {GENERATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_structured_text(labels: dict, source_label: str, sample: dict, lang: str, source: str) -> str:
    page = "https://lovetypes.tw/contact/" if source == "contact" else "https://lovetypes.tw/keepsakes/"
    if lang != "zh":
        page = f"https://lovetypes.tw/{lang}/" + ("contact/" if source == "contact" else "keepsakes/")
    return "\n".join([
        str(labels["body_header"]),
        f"{labels['source_label']}: {source_label}",
        f"{labels['guardian']}: {sample['guardian']}",
        f"{labels['request_type']}: owned_asset_request",
        f"{labels['asset']}: {sample['asset']}",
        f"{labels['email']}: sample@example.com",
        f"{labels['campaign']}: iris_silence",
        f"{labels['context']}: {sample['context']}",
        "consent_status: explicit_reply_ok",
        f"page: {page}",
    ])


def run_import_check(text: str) -> tuple[bool, str]:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as handle:
        handle.write(text)
        temp_path = Path(handle.name)
    try:
        result = subprocess.run(
            [sys.executable, str(IMPORT_TOOL), "check", "--input", str(temp_path)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    finally:
        temp_path.unlink(missing_ok=True)
    output = result.stdout.strip()
    required = (
        "promotion_lead_text_import_source=",
        "promotion_lead_text_import_guardian=iris",
        "promotion_lead_text_import_intake_type=owned_asset_request",
        "promotion_lead_text_import_has_reply_email=1",
        "promotion_lead_text_import_has_utm_content=1",
        "promotion_lead_text_import_issues=0",
    )
    if result.returncode != 0:
        return False, output
    missing = [item for item in required if item not in output]
    if missing:
        return False, f"missing expected output {', '.join(missing)}\n{output}"
    return True, output


def validate() -> tuple[dict[str, int], list[str]]:
    generator = load_generator()
    issues: list[str] = []
    checked = 0
    valid = 0
    languages = list(generator.LANGS.keys())
    for lang in languages:
        labels = generator.LEAD_INTAKE_FORM.get(lang, {})
        sample = SAMPLE_BY_LANG.get(lang, SAMPLE_BY_LANG["en"])
        if not labels:
            issues.append(f"{lang}: missing lead intake labels")
            continue
        for source, source_key in SOURCES.items():
            source_label = str(labels.get(source_key, ""))
            if not source_label:
                issues.append(f"{lang}/{source}: missing source label {source_key}")
                continue
            text = build_structured_text(labels, source_label, sample, lang, source)
            checked += 1
            ok, detail = run_import_check(text)
            if ok:
                valid += 1
            else:
                issues.append(f"{lang}/{source}: generated lead text is not importable\n{detail}")
    return {
        "languages": len(languages),
        "sources": len(SOURCES),
        "checkedTexts": checked,
        "validTexts": valid,
    }, issues


def main() -> int:
    metrics, issues = validate()
    print(f"promotion_lead_form_import_languages={metrics['languages']}")
    print(f"promotion_lead_form_import_sources={metrics['sources']}")
    print(f"promotion_lead_form_import_checked_texts={metrics['checkedTexts']}")
    print(f"promotion_lead_form_import_valid_texts={metrics['validTexts']}")
    print(f"promotion_lead_form_import_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
