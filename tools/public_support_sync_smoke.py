#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ssl
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = "https://lovetypes.tw"
SUPPORT_FILES = (
    "robots.txt",
    "sitemap.xml",
    "feed.xml",
    "site.webmanifest",
    "llms.txt",
    "humans.txt",
    "security.txt",
    ".well-known/security.txt",
    "ads.txt",
    "funnel-events.json",
    "commerce-catalog.json",
    "site-index.json",
    "guardian-profiles.json",
    "safety-index.json",
    "ai-discovery.json",
    "promotion-kit.json",
    "release.json",
    "site-health.json",
)


def normalize_base_url(value: str) -> str:
    return value.rstrip("/") or DEFAULT_BASE_URL


def normalize_bytes(value: bytes) -> bytes:
    return value.replace(b"\r\n", b"\n").rstrip(b"\n") + b"\n"


def request_bytes(url: str, attempts: int = 3) -> tuple[int, str, bytes]:
    context = ssl.create_default_context()
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = Request(url, headers={"User-Agent": "LoveTypes public support sync smoke/1.0"})
            with urlopen(request, timeout=20, context=context) as response:
                return response.status, response.headers.get("content-type", ""), response.read()
        except HTTPError as error:
            return error.code, error.headers.get("content-type", ""), error.read()
        except (TimeoutError, URLError, OSError) as error:
            last_error = error
            if attempt < attempts:
                time.sleep(0.5 * attempt)
    raise RuntimeError(f"failed to request {url}: {last_error}")


def robots_content_matches(local_body: bytes, public_body: bytes) -> tuple[bool, str]:
    public_text = public_body.decode("utf-8", errors="replace")
    if local_body not in public_body:
        return False, "public robots.txt does not contain local robots directives"
    required_cloudflare = (
        "# BEGIN Cloudflare Managed content",
        "Content-Signal: search=yes,ai-train=no",
        "User-agent: GPTBot",
        "User-agent: Google-Extended",
        "# END Cloudflare Managed Content",
    )
    missing = [token for token in required_cloudflare if token not in public_text]
    if missing:
        return False, "public robots.txt missing Cloudflare managed content signals: " + ", ".join(missing)
    return True, ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare public LoveTypes support files against the local deployable files.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    args = parser.parse_args()
    base_url = normalize_base_url(args.base_url)
    issues: list[str] = []
    files_checked = 0
    bytes_checked = 0
    json_files_checked = 0
    text_files_checked = 0
    xml_files_checked = 0

    for relative in SUPPORT_FILES:
        local_path = ROOT / relative
        public_url = urljoin(base_url + "/", relative)
        if not local_path.exists():
            issues.append(f"{relative}: missing local support file")
            continue
        local_body = normalize_bytes(local_path.read_bytes())
        try:
            status, content_type, public_body_raw = request_bytes(public_url)
        except RuntimeError as error:
            issues.append(f"{relative}: {error}")
            continue
        if status != 200:
            issues.append(f"{relative}: expected HTTP 200, got {status}")
            continue
        public_body = normalize_bytes(public_body_raw)
        files_checked += 1
        bytes_checked += len(public_body)
        if relative.endswith(".json") or relative.endswith(".webmanifest"):
            json_files_checked += 1
            if "json" not in content_type and "manifest" not in content_type:
                issues.append(f"{relative}: expected JSON-like content-type, got {content_type!r}")
        elif relative.endswith(".xml"):
            xml_files_checked += 1
            if "xml" not in content_type:
                issues.append(f"{relative}: expected XML content-type, got {content_type!r}")
        else:
            text_files_checked += 1
            if not any(token in content_type for token in ("text", "plain")):
                issues.append(f"{relative}: expected text content-type, got {content_type!r}")
        if relative == "robots.txt":
            matches, reason = robots_content_matches(local_body, public_body)
            if not matches:
                issues.append(f"{relative}: {reason}")
        elif local_body != public_body:
            issues.append(
                f"{relative}: public file differs from local deployable file "
                f"(local_bytes={len(local_body)}, public_bytes={len(public_body)})"
            )

    print(f"public_support_sync_files_checked={files_checked}")
    print(f"public_support_sync_json_files_checked={json_files_checked}")
    print(f"public_support_sync_text_files_checked={text_files_checked}")
    print(f"public_support_sync_xml_files_checked={xml_files_checked}")
    print(f"public_support_sync_bytes_checked={bytes_checked}")
    print(f"public_support_sync_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
