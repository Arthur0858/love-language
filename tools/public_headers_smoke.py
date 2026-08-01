#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import re
import socket
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener


DEFAULT_BASE_URL = "https://lovetypes.tw"
PREVIEW_BASE_URL = "https://lovetypes.pages.dev"
ROOT = Path(__file__).resolve().parents[1]


def load_generator_config():
    spec = importlib.util.spec_from_file_location("lovetypes_generator", ROOT / "tools" / "generate_multilingual_site.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load generate_multilingual_site.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GENERATOR_CONFIG = load_generator_config()
CSP_REQUIRED_DIRECTIVES = {
    "default-src": ("'self'",),
    "script-src": ("'self'", "'unsafe-inline'", "https://static.cloudflareinsights.com"),
    "style-src": ("'self'", "'unsafe-inline'"),
    "img-src": ("'self'", "data:", "https:"),
    "font-src": ("'self'",),
    "connect-src": ("'self'",),
    "object-src": ("'none'",),
    "base-uri": ("'self'",),
    "frame-ancestors": ("'self'",),
    "form-action": ("'self'", "mailto:"),
    "upgrade-insecure-requests": (),
}
GLOBAL_HEADERS = {
    "x-content-type-options": "nosniff",
    "referrer-policy": "strict-origin-when-cross-origin",
    "x-frame-options": "SAMEORIGIN",
    "permissions-policy": "camera=(), microphone=(), geolocation=(), payment=()",
}
IMMUTABLE_CACHE_RE = re.compile(r"max-age=31536000.*immutable", re.I)
HTML_CACHE_RE = re.compile(r"max-age=600", re.I)
@dataclass(frozen=True)
class HeaderCase:
    name: str
    path: str
    expected_status: int = 200
    immutable: bool = False
    html: bool = False
    expect_noindex: bool = False
    expected_location: str = ""


CORE_HTML_CASES = [
    HeaderCase(f"core-zh-{route or 'home'}", f"/{route}/" if route else "/", html=True)
    for route in GENERATOR_CONFIG.site_index_paths()
] + [
    HeaderCase(f"noindex-{route}", f"/{route}/", html=True)
    for route in ("resources", "keepsakes", "luna-yoga-music")
]


CASES = [
    *CORE_HTML_CASES,
    *[
        HeaderCase(f"noindex-support-{path.strip('/').replace('/', '-')}", path, expect_noindex=True)
        for path in GENERATOR_CONFIG.NOINDEX_SUPPORT_PATHS
    ],
    HeaderCase("css", GENERATOR_CONFIG.CSS_ASSET, immutable=True),
    HeaderCase("interactions", GENERATOR_CONFIG.INTERACTIONS_ASSET, immutable=True),
    HeaderCase("quiz-data", GENERATOR_CONFIG.QUIZ_DATA_ASSETS["zh"], immutable=True),
    HeaderCase("compass-tool", GENERATOR_CONFIG.COMPASS_TOOL_ASSET, immutable=True),
    HeaderCase("image", "/assets/lovetypes/backgrounds/guardian-garden-mobile.webp", immutable=True),
    HeaderCase("luna-redirect", "/luna/", expected_status=301, expected_location="/luna-yoga-music/"),
    *[
        HeaderCase(f"language-{lang}-redirect", f"/{lang}/", expected_status=302, expected_location="/")
        for lang in ("en", "ja", "ko", "es")
    ],
]


def normalize_base_url(base_url: str) -> str:
    return base_url if base_url.endswith("/") else f"{base_url}/"


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: N802
        return None


NO_REDIRECT_OPENER = build_opener(NoRedirectHandler)


def fetch_head(url: str, attempts: int = 3) -> tuple[int, dict[str, str]]:
    last_error: BaseException | None = None
    for attempt in range(1, attempts + 1):
        request = Request(url, method="HEAD", headers={"User-Agent": "LoveTypes public headers smoke"})
        try:
            with NO_REDIRECT_OPENER.open(request, timeout=30) as response:
                return response.status, {key.lower(): value for key, value in response.headers.items()}
        except HTTPError as error:
            return error.code, {key.lower(): value for key, value in error.headers.items()}
        except (TimeoutError, socket.timeout, URLError, OSError) as error:
            last_error = error
            if attempt < attempts:
                time.sleep(0.75 * attempt)
    raise RuntimeError(f"{url}: failed after {attempts} attempts: {last_error}") from last_error


def check_global_headers(case: HeaderCase, headers: dict[str, str], require_csp: bool) -> tuple[list[str], int]:
    issues: list[str] = []
    csp_tokens_checked = 0
    for name, expected in GLOBAL_HEADERS.items():
        actual = headers.get(name, "")
        if actual != expected:
            issues.append(f"{case.name}: {name} expected {expected!r}, got {actual!r}")
    hsts = headers.get("strict-transport-security", "")
    if "max-age=31536000" not in hsts:
        issues.append(f"{case.name}: missing one-year strict-transport-security")
    csp = headers.get("content-security-policy", "")
    if require_csp and not csp:
        issues.append(f"{case.name}: missing content-security-policy")
    elif require_csp:
        for directive, tokens in CSP_REQUIRED_DIRECTIVES.items():
            if directive not in csp:
                issues.append(f"{case.name}: CSP missing {directive}")
                continue
            csp_tokens_checked += 1
            for token in tokens:
                if token not in csp:
                    issues.append(f"{case.name}: CSP {directive} missing {token}")
                else:
                    csp_tokens_checked += 1
    return issues, csp_tokens_checked


def check_case(base_url: str, case: HeaderCase) -> tuple[list[str], int]:
    url = urljoin(normalize_base_url(base_url), case.path.lstrip("/"))
    status, headers = fetch_head(url)
    issues: list[str] = []
    if status != case.expected_status:
        issues.append(f"{case.name}: HTTP status expected {case.expected_status}, got {status}")
    global_issues, csp_tokens_checked = check_global_headers(case, headers, require_csp=case.html)
    issues.extend(global_issues)
    if case.html:
        cache_control = headers.get("cache-control", "")
        if not HTML_CACHE_RE.search(cache_control):
            issues.append(f"{case.name}: HTML cache-control should include max-age=600, got {cache_control!r}")
    if case.immutable:
        cache_control = headers.get("cache-control", "")
        if not IMMUTABLE_CACHE_RE.search(cache_control):
            issues.append(f"{case.name}: immutable cache-control missing, got {cache_control!r}")
    if case.expected_location:
        location = headers.get("location", "")
        parsed_location = urlparse(location)
        location_path = parsed_location.path or location
        if location_path != case.expected_location:
            issues.append(f"{case.name}: location expected {case.expected_location}, got {location!r}")
    if case.expect_noindex and "noindex" not in {
        token.strip() for token in headers.get("x-robots-tag", "").lower().split(",")
    }:
        issues.append(f"{case.name}: expected x-robots-tag to contain noindex")
    return issues, csp_tokens_checked


def main() -> int:
    parser = argparse.ArgumentParser(description="Check deployed LoveTypes security and cache headers.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--preview-base-url", default=PREVIEW_BASE_URL)
    args = parser.parse_args()

    issues: list[str] = []
    checked = 0
    core_html_cases_checked = 0
    csp_tokens_checked = 0
    for case in CASES:
        checked += 1
        if case.html and case.name.startswith("core-"):
            core_html_cases_checked += 1
        case_issues, case_csp_tokens = check_case(args.base_url, case)
        issues.extend(case_issues)
        csp_tokens_checked += case_csp_tokens

    preview_cases = [
        HeaderCase("pages-preview-home", "/", html=True, expect_noindex=True),
    ]
    for case in preview_cases:
        checked += 1
        case_issues, case_csp_tokens = check_case(args.preview_base_url, case)
        issues.extend(case_issues)
        csp_tokens_checked += case_csp_tokens

    print(f"public_header_cases_checked={checked}")
    print(f"public_header_core_html_cases_checked={core_html_cases_checked}")
    print(f"public_header_csp_tokens_checked={csp_tokens_checked}")
    print(f"public_header_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
