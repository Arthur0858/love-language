#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener


DEFAULT_BASE_URL = "https://lovetypes.tw"
PREVIEW_BASE_URL = "https://lovetypes.pages.dev"
CSP_REQUIRED_DIRECTIVES = {
    "default-src": "'self'",
    "script-src": "https://static.cloudflareinsights.com",
    "style-src": "'unsafe-inline'",
    "object-src": "'none'",
    "base-uri": "'self'",
    "frame-ancestors": "'self'",
    "form-action": "mailto:",
    "upgrade-insecure-requests": "",
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


CASES = [
    HeaderCase("home", "/", html=True),
    HeaderCase("characters", "/characters/", html=True),
    HeaderCase("resources", "/resources/", html=True),
    HeaderCase("css", "/shared-20260605-contrast.css", immutable=True),
    HeaderCase("interactions", "/site-interactions-20260605-contrast.js", immutable=True),
    HeaderCase("quiz-data", "/quiz-data-zh-20260605-contrast.js", immutable=True),
    HeaderCase("image", "/assets/lovetypes/backgrounds/guardian-garden-mobile.webp", immutable=True),
    HeaderCase("luna-redirect", "/luna/", expected_status=301, expected_location="/luna-yoga-music/"),
]


def normalize_base_url(base_url: str) -> str:
    return base_url if base_url.endswith("/") else f"{base_url}/"


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: N802
        return None


NO_REDIRECT_OPENER = build_opener(NoRedirectHandler)


def fetch_head(url: str) -> tuple[int, dict[str, str]]:
    request = Request(url, method="HEAD", headers={"User-Agent": "LoveTypes public headers smoke"})
    try:
        with NO_REDIRECT_OPENER.open(request, timeout=30) as response:
            return response.status, {key.lower(): value for key, value in response.headers.items()}
    except HTTPError as error:
        return error.code, {key.lower(): value for key, value in error.headers.items()}
    except URLError as error:
        raise RuntimeError(f"{url}: {error}") from error


def check_global_headers(case: HeaderCase, headers: dict[str, str]) -> list[str]:
    issues: list[str] = []
    for name, expected in GLOBAL_HEADERS.items():
        actual = headers.get(name, "")
        if actual != expected:
            issues.append(f"{case.name}: {name} expected {expected!r}, got {actual!r}")
    hsts = headers.get("strict-transport-security", "")
    if "max-age=31536000" not in hsts:
        issues.append(f"{case.name}: missing one-year strict-transport-security")
    csp = headers.get("content-security-policy", "")
    if not csp:
        issues.append(f"{case.name}: missing content-security-policy")
    else:
        for directive, token in CSP_REQUIRED_DIRECTIVES.items():
            if directive not in csp:
                issues.append(f"{case.name}: CSP missing {directive}")
            elif token and token not in csp:
                issues.append(f"{case.name}: CSP {directive} missing {token}")
    return issues


def check_case(base_url: str, case: HeaderCase) -> list[str]:
    url = urljoin(normalize_base_url(base_url), case.path.lstrip("/"))
    status, headers = fetch_head(url)
    issues: list[str] = []
    if status != case.expected_status:
        issues.append(f"{case.name}: HTTP status expected {case.expected_status}, got {status}")
    issues.extend(check_global_headers(case, headers))
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
    if case.expect_noindex and headers.get("x-robots-tag", "").lower() != "noindex":
        issues.append(f"{case.name}: expected x-robots-tag noindex")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Check deployed LoveTypes security and cache headers.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--preview-base-url", default=PREVIEW_BASE_URL)
    args = parser.parse_args()

    issues: list[str] = []
    checked = 0
    for case in CASES:
        checked += 1
        issues.extend(check_case(args.base_url, case))

    preview_cases = [
        HeaderCase("pages-preview-home", "/", html=True, expect_noindex=True),
    ]
    for case in preview_cases:
        checked += 1
        issues.extend(check_case(args.preview_base_url, case))

    print(f"public_header_cases_checked={checked}")
    print(f"public_header_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
