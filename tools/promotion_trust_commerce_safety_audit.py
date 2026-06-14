#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
SAFETY_INDEX = ROOT / "safety-index.json"
COMMERCE_CATALOG = ROOT / "commerce-catalog.json"
OUTPUT_MD = ROOT / "docs" / "promotion" / "first-round" / "trust-commerce-safety-audit.md"
OUTPUT_JSON = ROOT / "docs" / "promotion" / "first-round" / "trust-commerce-safety-audit.json"
MAIN_COMMERCIAL_PAGES = (
    "resources/index.html",
    "luna-yoga-music/index.html",
    "contact/index.html",
    "keepsakes/index.html",
)
REQUIRED_BOUNDARY_IDS = {
    "reflection_not_diagnosis",
    "urgent_risk_first",
    "do_not_buy_to_fix",
    "email_minimum_context",
    "external_store_boundary",
}
BOUNDARY_SNIPPETS = {
    "reflection_not_diagnosis": {
        "diagnosis": ("診斷", "diagnosis"),
        "counseling": ("諮商", "counseling", "therapy"),
    },
    "urgent_risk_first": {
        "emergency": ("緊急", "urgent", "emergency", "risk", "危急"),
    },
    "do_not_buy_to_fix": {
        "purchase": ("購買", "buy", "purchase", "商品"),
        "outcome": ("不承諾", "guaranteed", "promise", "替代", "取代", "replace"),
    },
    "email_minimum_context": {
        "sensitive": ("sensitive", "敏感", "minimum", "最少"),
    },
    "external_store_boundary": {
        "external": ("external", "外部", "Gumroad", "affiliate", "聯盟"),
    },
}
PAGE_REQUIRED_SNIPPETS = {
    "resources/index.html": ("不適合購買", "不承諾療效", "不取代諮商", "sponsored"),
    "luna-yoga-music/index.html": ("Gumroad", "不承諾療效", "不取代諮商", "sponsored"),
    "contact/index.html": ("緊急", "診斷", "諮商", "contact@lovetypes.tw"),
    "keepsakes/index.html": ("不承諾療效", "不取代諮商", "data-safety-boundary-bridge"),
}
EXTERNAL_COMMERCIAL_HOSTS = ("books.com.tw", "amazon.com", "gumroad.com")


def today() -> str:
    return date.today().isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def local_path_for(url: str) -> Path | None:
    parsed = urlparse(url)
    if parsed.netloc != "lovetypes.tw":
        return None
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if not parts:
        return ROOT / "index.html"
    return ROOT.joinpath(*parts, "index.html")


def route_exists(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.path.endswith(".json"):
        json_path = ROOT / parsed.path.lstrip("/")
        return json_path.exists()
    path = local_path_for(url)
    if not path or not path.exists():
        return False
    if parsed.fragment:
        html = path.read_text(encoding="utf-8")
        return parsed.fragment in html
    return True


def page_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def commercial_links(html: str) -> list[tuple[str, str]]:
    links: list[tuple[str, str]] = []
    pattern = re.compile(r"<a\b(?P<attrs>[^>]*?)>", re.IGNORECASE | re.DOTALL)
    href_pattern = re.compile(r'href="(?P<href>[^"]+)"', re.IGNORECASE)
    rel_pattern = re.compile(r'rel="(?P<rel>[^"]+)"', re.IGNORECASE)
    for match in pattern.finditer(html):
        attrs = match.group("attrs")
        href_match = href_pattern.search(attrs)
        if not href_match:
            continue
        href = href_match.group("href")
        if any(host in href for host in EXTERNAL_COMMERCIAL_HOSTS):
            rel_match = rel_pattern.search(attrs)
            links.append((href, rel_match.group("rel") if rel_match else ""))
    return links


def validate_safety_index(data: dict) -> tuple[int, int, int, list[str]]:
    issues: list[str] = []
    boundaries = data.get("boundaries", [])
    if not isinstance(boundaries, list):
        return 0, 0, 0, ["safety-index boundaries should be a list"]
    seen_ids = {boundary.get("id") for boundary in boundaries if isinstance(boundary, dict)}
    missing_ids = sorted(REQUIRED_BOUNDARY_IDS - seen_ids)
    if missing_ids:
        issues.append("safety-index missing boundary ids: " + ", ".join(missing_ids))
    route_checks = 0
    snippet_checks = 0
    for boundary in boundaries:
        if not isinstance(boundary, dict):
            issues.append("safety-index boundary should be an object")
            continue
        boundary_id = str(boundary.get("id", ""))
        text = f"{boundary.get('title', '')} {boundary.get('body', '')}".lower()
        if not boundary.get("severity"):
            issues.append(f"{boundary_id}: missing severity")
        for label, snippets in BOUNDARY_SNIPPETS.get(boundary_id, {}).items():
            snippet_checks += 1
            if not any(snippet.lower() in text for snippet in snippets):
                issues.append(f"{boundary_id}: missing {label} boundary language")
        routes = boundary.get("routes", [])
        if not routes:
            issues.append(f"{boundary_id}: missing routes")
        for url in routes:
            route_checks += 1
            if not route_exists(str(url)):
                issues.append(f"{boundary_id}: route missing locally: {url}")
    return len(boundaries), route_checks, snippet_checks, issues


def validate_commerce_catalog(data: dict) -> tuple[int, int, int, int, list[str]]:
    issues: list[str] = []
    items = data.get("items", [])
    playbook = data.get("revenuePlaybook", [])
    safety = " ".join(str(item) for item in data.get("safetyBoundaries", []))
    for required in ("diagnostic", "guaranteed outcome", "Affiliate", "Gumroad", "Email"):
        if required.lower() not in safety.lower():
            issues.append(f"commerce safetyBoundaries missing {required}")
    playbook_by_id = {item.get("id"): item for item in playbook if isinstance(item, dict)}
    playbook_checks = 0
    item_checks = 0
    local_url_checks = 0
    for item in playbook:
        if not isinstance(item, dict):
            issues.append("commerce revenuePlaybook entry should be an object")
            continue
        playbook_checks += 1
        for field in ("useWhen", "nextStep", "doNotUseWhen", "primaryEvents"):
            if not item.get(field):
                issues.append(f"{item.get('id', '<playbook>')}: missing {field}")
    for item in items:
        if not isinstance(item, dict):
            issues.append("commerce item should be an object")
            continue
        item_checks += 1
        item_id = item.get("id", "<item>")
        playbook_id = item.get("playbookId")
        if playbook_id not in playbook_by_id:
            issues.append(f"{item_id}: playbookId missing from revenuePlaybook")
        for field in ("disclosure", "doNotUseWhen", "nextStep", "primaryEvents"):
            if not item.get(field):
                issues.append(f"{item_id}: missing {field}")
        item_type = item.get("type")
        disclosure = str(item.get("disclosure", "")).lower()
        do_not = str(item.get("doNotUseWhen", "")).lower()
        if item_type in {"affiliate_book", "luna_gumroad_pack"}:
            if "therapy" not in disclosure and "therapy" not in do_not and "counsel" not in do_not:
                issues.append(f"{item_id}: revenue item missing therapy/counseling boundary")
        if item_type == "owned_supply_waitlist" and "sensitive" not in do_not:
            issues.append(f"{item_id}: owned lead item should avoid sensitive details")
        url = str(item.get("url", ""))
        if "lovetypes.tw" in url:
            local_url_checks += 1
            if not route_exists(url):
                issues.append(f"{item_id}: local commerce URL missing: {url}")
    return len(items), playbook_checks, item_checks, local_url_checks, issues


def validate_pages() -> tuple[int, int, int, list[str]]:
    issues: list[str] = []
    snippet_checks = 0
    external_links_checked = 0
    pages_checked = 0
    for relative in MAIN_COMMERCIAL_PAGES:
        path = ROOT / relative
        html = page_text(path)
        if not html:
            issues.append(f"{relative}: missing page")
            continue
        pages_checked += 1
        for snippet in PAGE_REQUIRED_SNIPPETS[relative]:
            snippet_checks += 1
            if snippet not in html:
                issues.append(f"{relative}: missing visible safety/commercial snippet {snippet!r}")
        for href, rel in commercial_links(html):
            external_links_checked += 1
            if "sponsored" not in rel or "noopener" not in rel:
                issues.append(f"{relative}: commercial link missing sponsored/noopener rel: {href}")
    return pages_checked, snippet_checks, external_links_checked, issues


def validate() -> tuple[dict[str, int], list[str]]:
    safety = load_json(SAFETY_INDEX)
    commerce = load_json(COMMERCE_CATALOG)
    boundary_count, safety_routes, safety_snippets, safety_issues = validate_safety_index(safety)
    commerce_items, playbook_checks, item_checks, local_url_checks, commerce_issues = validate_commerce_catalog(commerce)
    pages_checked, page_snippets, external_links, page_issues = validate_pages()
    issues = [*safety_issues, *commerce_issues, *page_issues]
    return {
        "boundaries": boundary_count,
        "safetyRoutes": safety_routes,
        "safetySnippetChecks": safety_snippets,
        "commerceItems": commerce_items,
        "commercePlaybookChecks": playbook_checks,
        "commerceItemChecks": item_checks,
        "commerceLocalUrlChecks": local_url_checks,
        "pagesChecked": pages_checked,
        "pageSnippetChecks": page_snippets,
        "externalCommercialLinks": external_links,
    }, issues


def render_markdown(report: dict) -> str:
    metrics = report["metrics"]
    lines = [
        "# LoveTypes Trust Commerce Safety Audit",
        "",
        f"- 產生日期：{report['generatedAt']}",
        f"- safety boundaries：{metrics['boundaries']}",
        f"- safety routes checked：{metrics['safetyRoutes']}",
        f"- safety snippet checks：{metrics['safetySnippetChecks']}",
        f"- commerce items：{metrics['commerceItems']}",
        f"- commerce playbook checks：{metrics['commercePlaybookChecks']}",
        f"- commerce item checks：{metrics['commerceItemChecks']}",
        f"- local commerce URL checks：{metrics['commerceLocalUrlChecks']}",
        f"- commercial pages checked：{metrics['pagesChecked']}",
        f"- page snippet checks：{metrics['pageSnippetChecks']}",
        f"- external commercial links：{metrics['externalCommercialLinks']}",
        f"- issues：{len(report['issues'])}",
        "",
        "## Rule",
        "",
        "- Commercial paths must keep visible boundaries for diagnosis, counseling, urgent risk, external checkout, and non-guaranteed outcomes.",
        "- Affiliate, Amazon, Books.com.tw, Gumroad, and owned waitlist items must map to the commerce playbook.",
        "- External commercial links must use sponsored and noopener rel values.",
        "- Contact and owned request routes must avoid sensitive over-collection and emergency handling claims.",
        "",
        "## Checked Pages",
        "",
    ]
    lines.extend(f"- `{page}`" for page in MAIN_COMMERCIAL_PAGES)
    lines.append("")
    if report["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in report["issues"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_report(metrics: dict[str, int], issues: list[str]) -> None:
    report = {
        "generatedAt": today(),
        "sources": {
            "safetyIndex": str(SAFETY_INDEX.relative_to(ROOT)),
            "commerceCatalog": str(COMMERCE_CATALOG.relative_to(ROOT)),
            "commercialPages": list(MAIN_COMMERCIAL_PAGES),
        },
        "metrics": metrics,
        "issues": issues,
    }
    OUTPUT_MD.write_text(render_markdown(report), encoding="utf-8")
    OUTPUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit LoveTypes trust and commerce safety boundaries.")
    parser.add_argument("--write-report", action="store_true", help="Write a dated md/json trust commerce safety report.")
    args = parser.parse_args()
    metrics, issues = validate()
    if args.write_report:
        write_report(metrics, issues)
        print(f"promotion_trust_commerce_safety_report={OUTPUT_MD.relative_to(ROOT)}")
        print(f"promotion_trust_commerce_safety_report_json={OUTPUT_JSON.relative_to(ROOT)}")
    print(f"promotion_trust_safety_boundaries={metrics['boundaries']}")
    print(f"promotion_trust_safety_routes_checked={metrics['safetyRoutes']}")
    print(f"promotion_trust_safety_snippet_checks={metrics['safetySnippetChecks']}")
    print(f"promotion_trust_commerce_items={metrics['commerceItems']}")
    print(f"promotion_trust_commerce_playbook_checks={metrics['commercePlaybookChecks']}")
    print(f"promotion_trust_commerce_item_checks={metrics['commerceItemChecks']}")
    print(f"promotion_trust_commerce_local_url_checks={metrics['commerceLocalUrlChecks']}")
    print(f"promotion_trust_pages_checked={metrics['pagesChecked']}")
    print(f"promotion_trust_page_snippet_checks={metrics['pageSnippetChecks']}")
    print(f"promotion_trust_external_commercial_links={metrics['externalCommercialLinks']}")
    print(f"promotion_trust_commerce_safety_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
