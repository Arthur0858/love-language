#!/usr/bin/env python3
"""Keep the public privacy policy aligned with the deployed browser behavior."""

from __future__ import annotations

import html
import importlib.util
import json
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

from generate_multilingual_site import INTERACTIONS_ASSET, PRIVACY_UPDATED


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_STORAGE_KEYS = {
    "lovetypes:campaign-attribution:v1",
    "lovetypes:funnel-events:v1",
}
REQUIRED_POLICY_PHRASES = (
    "瀏覽器 localStorage",
    "最近 40 筆",
    "不會由網站程式自動上傳",
    "測驗開始與完成計數",
    "不含帳號、答案、分數或守護者結果",
    "Cloudflare Pages",
    "Cloudflare Web Analytics",
    "beacon.min.js",
    "/cdn-cgi/rum",
    "不讀取 Cookie、localStorage",
    "email-decode.min.js",
    "IP 位址",
    "第三方廣告執行程式",
    "不設定第一方 Cookie",
    "外部書店與 Gumroad",
    "不設定自動到期日",
    "contact@lovetypes.tw",
)

REQUIRED_POLICY_LINKS = (
    "https://developers.cloudflare.com/speed/observatory/rum-beacon/",
    "https://developers.cloudflare.com/waf/tools/scrape-shield/email-address-obfuscation/",
)


def load_deploy_module():
    deploy_path = ROOT / "tools" / "deploy_cloudflare_pages.py"
    spec = importlib.util.spec_from_file_location("lovetypes_privacy_deploy", deploy_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load deploy manifest logic: {deploy_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def visible_text(raw: str) -> str:
    raw = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", raw, flags=re.I | re.S)
    raw = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(raw)).strip()


def main() -> int:
    issues: list[str] = []
    privacy_raw = (ROOT / "privacy" / "index.html").read_text(encoding="utf-8")
    privacy_text = visible_text(privacy_raw)
    interactions_path = ROOT / INTERACTIONS_ASSET.lstrip("/")
    interactions = interactions_path.read_text(encoding="utf-8")
    redirects = (ROOT / "_redirects").read_text(encoding="utf-8")
    headers = (ROOT / "_headers").read_text(encoding="utf-8")

    for phrase in REQUIRED_POLICY_PHRASES:
        if phrase not in privacy_text:
            issues.append(f"privacy policy missing runtime disclosure: {phrase}")
    for href in REQUIRED_POLICY_LINKS:
        if f'href="{href}"' not in privacy_raw:
            issues.append(f"privacy policy missing authoritative runtime source: {href}")

    if PRIVACY_UPDATED not in privacy_text:
        issues.append(f"privacy policy visible update date should be {PRIVACY_UPDATED}")
    if f'"dateModified":"{PRIVACY_UPDATED}"' not in privacy_raw:
        issues.append("privacy schema dateModified does not match the policy revision")

    sitemap = ET.parse(ROOT / "sitemap.xml").getroot()
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    privacy_lastmod = ""
    for node in sitemap.findall("s:url", ns):
        if node.findtext("s:loc", default="", namespaces=ns) == "https://lovetypes.tw/privacy/":
            privacy_lastmod = node.findtext("s:lastmod", default="", namespaces=ns)
            break
    if privacy_lastmod != PRIVACY_UPDATED:
        issues.append(f"privacy sitemap lastmod should be {PRIVACY_UPDATED}, got {privacy_lastmod!r}")

    for key in EXPECTED_STORAGE_KEYS:
        if key not in interactions:
            issues.append(f"expected browser storage key missing from runtime: {key}")
    for runtime_marker in (
        "localStorage.setItem(storageKey",
        "localStorage.setItem(sharedStorageKey",
        "localStorage.setItem(key",
    ):
        generated_sources = "\n".join(
            path.read_text(encoding="utf-8", errors="ignore")
            for path in (ROOT / "tools" / "generate_multilingual_site.py", interactions_path)
        )
        if runtime_marker not in generated_sources:
            issues.append(f"expected local-storage behavior missing: {runtime_marker}")

    for metric in ("/go/quiz-started.gif", "/go/quiz-completed.gif"):
        if metric not in interactions:
            issues.append(f"technical metric path missing from runtime: {metric}")
        if f"{metric} /favicon.ico 200" not in redirects:
            issues.append(f"technical metric path missing same-origin redirect: {metric}")
    if "window.fetch(metricPath, { credentials: 'omit', keepalive: true })" not in interactions:
        issues.append("technical metric request must omit credentials")
    if len(re.findall(r"\bfetch\(", interactions)) != 1:
        issues.append("interaction runtime should have exactly one bounded fetch call")

    deploy = load_deploy_module()
    manifest_paths = deploy.collect_manifest_paths(ROOT)
    deployed_html = [path for path in manifest_paths if path.suffix == ".html"]
    deployed_javascript = [path for path in manifest_paths if path.suffix == ".js"]
    external_script_pattern = re.compile(r'<script\b[^>]*\bsrc="https?://', re.I)
    for path in deployed_html:
        raw = path.read_text(encoding="utf-8", errors="ignore")
        if external_script_pattern.search(raw):
            issues.append(f"external script loads directly from HTML: {path.relative_to(ROOT)}")
        if "pagead2.googlesyndication.com/pagead/js/adsbygoogle.js" in raw:
            issues.append(f"AdSense runtime loaded before approval: {path.relative_to(ROOT)}")
        if re.search(r"document\.cookie\s*=", raw):
            issues.append(f"first-party cookie setter found in HTML: {path.relative_to(ROOT)}")
    for path in deployed_javascript:
        raw = path.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"document\.cookie\s*=", raw):
            issues.append(f"first-party cookie setter found in deployed JavaScript: {path.relative_to(ROOT)}")
        if "pagead2.googlesyndication.com/pagead/js/adsbygoogle.js" in raw:
            issues.append(f"AdSense runtime loaded before approval: {path.relative_to(ROOT)}")
    if "connect-src 'self'" not in headers:
        issues.append("CSP connect-src must remain first-party only during review")

    print(f"privacy_runtime_pages_checked={len(deployed_html)}")
    print(f"privacy_runtime_scripts_checked={len(deployed_javascript)}")
    print(f"privacy_runtime_policy_phrases_checked={len(REQUIRED_POLICY_PHRASES)}")
    print(f"privacy_runtime_storage_keys_checked={len(EXPECTED_STORAGE_KEYS)}")
    print("privacy_runtime_metric_paths_checked=2")
    print(f"privacy_runtime_issues={len(issues)}")
    for issue in issues:
        print(f"- {issue}")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
