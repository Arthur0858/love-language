#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import promotion_lead_writeback as writeback


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_TEXT = """LoveTypes 結構化需求
來源: 收藏室免費素材需求
我的守護者: 艾莉絲 · 肯定的言詞
需求類型: owned_asset_request
素材偏好: PDF 練習卡
可回覆 email: requester@customer-mail.com
Campaign content / 推廣內容: iris_silence
使用情境或備註: 睡前整理，想要可列印版本
consent_status: explicit_reply_ok
page: https://lovetypes.tw/keepsakes/
"""

SOURCE_ALIASES = {
    "contact": "contact",
    "contact 結構化需求": "contact",
    "contact structured request": "contact",
    "contact 構造化リクエスト": "contact",
    "contact 구조화 요청": "contact",
    "petición estructurada de contacto": "contact",
    "keepsake": "keepsake_waitlist",
    "keepsake free asset request": "keepsake_waitlist",
    "收藏室免費素材需求": "keepsake_waitlist",
    "コレクション室の無料素材希望": "keepsake_waitlist",
    "소장실 무료 소재 요청": "keepsake_waitlist",
    "petición de recurso gratuito": "keepsake_waitlist",
    "resources": "resources_wishlist",
    "旅人補給": "resources_wishlist",
    "補給": "resources_wishlist",
    "luna": "luna_page",
    "luna page": "luna_page",
    "manual_reply": "manual_reply",
}
GUARDIAN_ALIASES = {
    "iris": "iris",
    "艾莉絲": "iris",
    "アイリス": "iris",
    "아이리스": "iris",
    "noah": "noah",
    "諾雅": "noah",
    "ノア": "noah",
    "노아": "noah",
    "vivian": "vivian",
    "薇薇安": "vivian",
    "ヴィヴィアン": "vivian",
    "비비안": "vivian",
    "claire": "claire",
    "克萊兒": "claire",
    "クレア": "claire",
    "클레어": "claire",
    "dora": "dora",
    "朵拉": "dora",
    "ドーラ": "dora",
    "ドラ": "dora",
    "도라": "dora",
}
KEY_ALIASES = {
    "來源": "source",
    "送信元": "source",
    "source": "source",
    "출처": "source",
    "fuente": "source",
    "我的守護者": "guardian",
    "my guardian": "guardian",
    "私の守護者": "guardian",
    "나의 수호자": "guardian",
    "mi guardiana": "guardian",
    "mi guardian": "guardian",
    "guardian": "guardian",
    "需求類型": "intake_type",
    "我想處理的事情": "intake_type",
    "希望タイプ": "intake_type",
    "相談したいこと": "intake_type",
    "相談内容": "intake_type",
    "요청 유형": "intake_type",
    "도움이 필요한 내용": "intake_type",
    "tipo de petición": "intake_type",
    "¿con qué necesitas ayuda?": "intake_type",
    "con qué necesitas ayuda?": "intake_type",
    "tipo de peticion": "intake_type",
    "request type": "intake_type",
    "what would you like help with?": "intake_type",
    "request_type": "intake_type",
    "素材偏好": "requested_asset",
    "asset preference": "requested_asset",
    "素材の希望": "requested_asset",
    "소재 선호": "requested_asset",
    "preferencia de recurso": "requested_asset",
    "asset": "requested_asset",
    "可回覆 email": "reply_email",
    "reply email": "reply_email",
    "返信用 email": "reply_email",
    "답장 받을 email": "reply_email",
    "email de respuesta": "reply_email",
    "reply email": "reply_email",
    "reply_email": "reply_email",
    "campaign content / 推廣內容": "utm_content",
    "頁面來源": "utm_content",
    "page source": "utm_content",
    "ページの送信元": "utm_content",
    "経路": "utm_content",
    "페이지 출처": "utm_content",
    "origen de la página": "utm_content",
    "campaign content": "utm_content",
    "推廣內容": "utm_content",
    "utm_content": "utm_content",
    "使用情境或備註": "context",
    "context": "context",
    "consent_status": "consent_status",
    "page": "page",
}
PLACEHOLDER_EMAIL_TOKENS = (
    "<",
    ">",
    "example.",
    "sample@",
    "placeholder",
    "replace",
    "real_reply_email",
    "test@",
    "dummy",
)
RESERVED_EMAIL_DOMAINS = {
    "example.com",
    "example.net",
    "example.org",
    "test",
    "invalid",
    "localhost",
}


def normalize_key(value: str) -> str:
    return " ".join(value.strip().lower().replace("：", ":").split())


def split_line(line: str) -> tuple[str, str] | None:
    normalized = line.replace("：", ":", 1)
    if ":" not in normalized:
        return None
    key, value = normalized.split(":", 1)
    return key.strip(), value.strip()


def parse_text(text: str) -> tuple[dict[str, str], list[str]]:
    data: dict[str, str] = {}
    issues: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        split = split_line(line)
        if not split:
            continue
        key, value = split
        canonical = KEY_ALIASES.get(normalize_key(key))
        if canonical:
            data[canonical] = value

    data["source"] = resolve_source(data.get("source", ""), data.get("page", ""))
    data["guardian"] = resolve_guardian(data.get("guardian", ""))
    required = ("source", "guardian", "intake_type", "requested_asset", "reply_email", "consent_status")
    for field in required:
        if not data.get(field):
            issues.append(f"missing {field}")
    if data.get("source") not in writeback.SOURCE_OPTIONS:
        issues.append(f"invalid source {data.get('source')!r}")
    if data.get("guardian") not in writeback.GUARDIANS:
        issues.append(f"invalid guardian {data.get('guardian')!r}")
    if data.get("intake_type") not in writeback.INTAKE_TO_KPI:
        issues.append(f"invalid intake_type {data.get('intake_type')!r}")
    if data.get("consent_status") != "explicit_reply_ok":
        issues.append("consent_status must be explicit_reply_ok")
    email_issue = reply_email_issue(data.get("reply_email", ""))
    if email_issue:
        issues.append(email_issue)
    return data, issues


def reply_email_issue(value: str) -> str:
    email = " ".join((value or "").strip().split())
    lowered = email.lower()
    if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
        return "reply_email should look like an email address"
    if any(token in lowered for token in PLACEHOLDER_EMAIL_TOKENS):
        return "reply_email must be a real requester address, not a placeholder or sample address"
    domain = lowered.rsplit("@", 1)[-1]
    if domain in RESERVED_EMAIL_DOMAINS or domain.endswith(".invalid") or domain.endswith(".test"):
        return "reply_email must not use a reserved test/example domain"
    return ""


def resolve_source(value: str, page: str) -> str:
    haystack = f"{value} {page}".strip().lower()
    for token, source in SOURCE_ALIASES.items():
        if token.lower() in haystack:
            return source
    return value.strip()


def resolve_guardian(value: str) -> str:
    haystack = value.strip().lower()
    for token, guardian in GUARDIAN_ALIASES.items():
        if token.lower() in haystack:
            return guardian
    return value.strip()


def read_input(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def add_lead(data: dict[str, str], proof_note: str, request_date: str = "") -> str:
    fieldnames, rows = writeback.read_csv(writeback.LEAD_TRACKER)
    args = argparse.Namespace(
        source=data["source"],
        guardian=data["guardian"],
        intake_type=data["intake_type"],
        consent_status=data["consent_status"],
        proof_note=proof_note,
        request_date=request_date,
        request_id="",
        utm_content=data.get("utm_content", ""),
        requested_asset=data.get("requested_asset", ""),
    )
    new_row = writeback.build_row(args, rows)
    candidate = [*rows, {field: new_row.get(field, "") for field in fieldnames}]
    issues = writeback.validate_tracker(fieldnames, candidate)
    if issues:
        raise SystemExit("\n".join(issues))
    writeback.write_csv(writeback.LEAD_TRACKER, fieldnames, candidate)
    kpi_status = writeback.writeback_kpi(new_row)
    writeback.regenerate_dependent_docs()
    _, refreshed = writeback.read_csv(writeback.LEAD_TRACKER)
    playbook = writeback.playbook(fieldnames, refreshed, writeback.validate_tracker(fieldnames, refreshed))
    writeback.write_playbook(playbook)
    return kpi_status


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse copied LoveTypes structured request text into safe lead writeback fields.")
    subparsers = parser.add_subparsers(dest="command")
    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("--input", default="", help="Optional text file to validate instead of the built-in sample.")
    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("--input", required=True, help="Text file path, or - for stdin.")
    add_parser.add_argument("--proof-note", required=True, help="Traceable proof note, e.g. email thread Gmail request checked YYYY-MM-DD.")
    add_parser.add_argument("--request-date", default="")
    args = parser.parse_args()
    command = args.command or "check"
    text = read_input(args.input) if getattr(args, "input", "") else SAMPLE_TEXT
    data, issues = parse_text(text)
    print(f"promotion_lead_text_import_fields_parsed={len(data)}")
    print(f"promotion_lead_text_import_source={data.get('source', '')}")
    print(f"promotion_lead_text_import_guardian={data.get('guardian', '')}")
    print(f"promotion_lead_text_import_intake_type={data.get('intake_type', '')}")
    print(f"promotion_lead_text_import_has_reply_email={1 if data.get('reply_email') else 0}")
    print(f"promotion_lead_text_import_has_utm_content={1 if data.get('utm_content') else 0}")
    if command == "add" and not issues:
        kpi_status = add_lead(data, args.proof_note, args.request_date)
        print(f"promotion_lead_text_import_kpi_status={kpi_status}")
    print(f"promotion_lead_text_import_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
