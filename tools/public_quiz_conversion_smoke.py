#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urldefrag, urljoin, urlparse, unquote
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://lovetypes.tw"
LANG_PATHS = {"zh": "/", "en": "/en/", "ja": "/ja/", "ko": "/ko/", "es": "/es/"}
EXPECTED_TYPES = {"W", "T", "G", "S", "P"}
TYPE_SLUGS = {"W": "iris", "T": "noah", "G": "vivian", "S": "claire", "P": "dora"}
ASSIGNMENT_RE = re.compile(r"window\.__LOVETYPES_QUIZ_DATA\s*=\s*(\{.*\})\s*;?\s*$", re.S)
QUIZ_SRC_RE = re.compile(r"^/quiz-data-(zh|en|ja|ko|es)-[^/]+\.js$")
INTERNAL_RESULT_URL_FIELDS = ("guardianUrl", "guideUrl", "resourceUrl", "lunaUrl", "collectorHallUrl", "planUrl")
RESULT_IMAGE_FIELDS = ("image", "resultImage", "storyImage", "domainProp")
RESULT_TEXT_FIELDS = ("domainTitle", "domainDesc", "domainCta", "domainAccent", "domainGlow", "domainMotif")
RESULT_NUMBER_FIELDS = ("domainPropWidth", "domainPropHeight")
ACCEPTED_EXTERNAL_STATUSES = set(range(200, 400)) | {403, 405, 429}


@dataclass
class Response:
    url: str
    status: int
    headers: dict[str, str]
    body: bytes

    @property
    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


class ScriptParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.scripts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        if tag == "script" and data.get("src"):
            self.scripts.append(data["src"])


class IdParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        if data.get("id"):
            self.ids.add(data["id"])


def normalize_base_url(value: str) -> str:
    return value.rstrip("/") or DEFAULT_BASE_URL


def request_url(url: str, *, method: str = "GET", attempts: int = 3) -> Response:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = Request(
                url,
                method=method,
                headers={
                    "User-Agent": "LoveTypes public quiz conversion smoke/1.0",
                    "Accept": "text/html,application/xhtml+xml,application/javascript,image/*,*/*;q=0.8",
                },
            )
            with urlopen(request, timeout=20) as raw:
                body = b"" if method == "HEAD" else raw.read()
                headers = {key.lower(): value for key, value in raw.headers.items()}
                return Response(raw.geturl(), raw.status, headers, body)
        except HTTPError as error:
            if method == "HEAD" and error.code in {405, 501}:
                return request_url(url, method="GET", attempts=attempts)
            body = b"" if method == "HEAD" else error.read()
            headers = {key.lower(): value for key, value in error.headers.items()}
            return Response(error.geturl(), error.code, headers, body)
        except (URLError, TimeoutError, OSError) as error:
            last_error = error
            if attempt < attempts:
                time.sleep(0.5 * attempt)
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def discover_quiz_asset(base_url: str, lang: str, path: str) -> tuple[str, list[str]]:
    issues: list[str] = []
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    if response.status != 200:
        return "", [f"{path}: expected status 200, got {response.status}"]
    parser = ScriptParser()
    parser.feed(response.text)
    quiz_scripts = [src for src in parser.scripts if QUIZ_SRC_RE.match(src)]
    if len(quiz_scripts) != 1:
        issues.append(f"{path}: expected one quiz-data script, found {quiz_scripts}")
        return "", issues
    script = quiz_scripts[0]
    match = QUIZ_SRC_RE.match(script)
    if match and match.group(1) != lang:
        issues.append(f"{path}: expected {lang} quiz data, got {script}")
    return script, issues


def parse_quiz_data(path: str, text: str) -> tuple[dict, list[str]]:
    match = ASSIGNMENT_RE.match(text.strip())
    if not match:
        return {}, [f"{path}: missing window.__LOVETYPES_QUIZ_DATA assignment"]
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError as error:
        return {}, [f"{path}: quiz data JSON is invalid: {error}"]
    return data, [] if isinstance(data, dict) else [f"{path}: quiz data should be an object"]


def cache_key(url: str) -> str:
    base, _fragment = urldefrag(url)
    return base


def check_internal_url(
    base_url: str,
    source: str,
    field: str,
    value: str,
    page_cache: dict[str, tuple[Response, set[str]]],
) -> tuple[list[str], int]:
    issues: list[str] = []
    absolute = urljoin(base_url + "/", value.lstrip("/") if value.startswith("/") else value)
    parsed = urlparse(absolute)
    base_host = urlparse(base_url).netloc
    if parsed.scheme not in {"http", "https"} or parsed.netloc != base_host:
        return [f"{source}: {field} should be an internal LoveTypes URL, got {value!r}"], 0

    page_url, fragment = urldefrag(absolute)
    if page_url not in page_cache:
        try:
            response = request_url(page_url)
        except RuntimeError as error:
            return [f"{source}: {field} request failed for {value!r}: {error}"], 0
        ids: set[str] = set()
        if response.status == 200 and "text/html" in response.headers.get("content-type", ""):
            parser = IdParser()
            parser.feed(response.text)
            ids = parser.ids
        page_cache[page_url] = (response, ids)
    response, ids = page_cache[page_url]
    if response.status != 200:
        issues.append(f"{source}: {field} expected status 200 for {value!r}, got {response.status}")
    checked_anchor = 0
    if fragment:
        checked_anchor = 1
        decoded_fragment = unquote(fragment)
        if fragment not in ids and decoded_fragment not in ids:
            issues.append(f"{source}: {field} missing anchor #{fragment} for {value!r}")
    return issues, checked_anchor


def check_image_url(base_url: str, source: str, field: str, value: str, image_cache: dict[str, Response]) -> list[str]:
    if not isinstance(value, str) or not value.startswith("/assets/lovetypes/"):
        return [f"{source}: {field} should use a LoveTypes asset path, got {value!r}"]
    absolute = urljoin(base_url + "/", value.lstrip("/"))
    if absolute not in image_cache:
        try:
            image_cache[absolute] = request_url(absolute, method="HEAD")
        except RuntimeError as error:
            return [f"{source}: {field} image request failed for {value!r}: {error}"]
    response = image_cache[absolute]
    issues: list[str] = []
    if response.status != 200:
        issues.append(f"{source}: {field} expected status 200 for {value!r}, got {response.status}")
    content_type = response.headers.get("content-type", "")
    if not content_type.startswith("image/"):
        issues.append(f"{source}: {field} expected image content-type for {value!r}, got {content_type!r}")
    if urlparse(base_url).scheme == "https":
        cache_control = response.headers.get("cache-control", "")
        if "max-age=31536000" not in cache_control.lower() or "immutable" not in cache_control.lower():
            issues.append(f"{source}: {field} expected immutable cache for {value!r}, got {cache_control!r}")
    return issues


def check_affiliate_url(source: str, value: str, affiliate_cache: dict[str, Response]) -> list[str]:
    parsed = urlparse(value)
    issues: list[str] = []
    if parsed.scheme != "https" or parsed.netloc != "www.books.com.tw":
        issues.append(f"{source}: supplyBookUrl should use https://www.books.com.tw, got {value!r}")
    for token in ("arthur0858", "utm_campaign=ap-202604"):
        if token not in value:
            issues.append(f"{source}: supplyBookUrl missing {token}")
    if value not in affiliate_cache:
        try:
            affiliate_cache[value] = request_url(value, method="HEAD", attempts=2)
        except RuntimeError as error:
            return issues + [f"{source}: supplyBookUrl request failed: {error}"]
    response = affiliate_cache[value]
    if response.status not in ACCEPTED_EXTERNAL_STATUSES:
        issues.append(f"{source}: supplyBookUrl expected reachable status, got {response.status} final={response.url}")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public quiz result conversion URLs, anchors, images, and affiliate resources.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Public deployment base URL.")
    args = parser.parse_args()
    base_url = normalize_base_url(args.base_url)

    issues: list[str] = []
    page_cache: dict[str, tuple[Response, set[str]]] = {}
    image_cache: dict[str, Response] = {}
    affiliate_cache: dict[str, Response] = {}
    assets_checked = 0
    results_checked = 0
    result_internal_urls_checked = 0
    result_anchor_targets_checked = 0
    result_images_checked = 0
    result_affiliate_links_checked = 0
    result_pass_fields_checked = 0

    for lang, home_path in LANG_PATHS.items():
        script, discovery_issues = discover_quiz_asset(base_url, lang, home_path)
        issues.extend(discovery_issues)
        if not script:
            continue
        response = request_url(urljoin(base_url + "/", script.lstrip("/")))
        if response.status != 200:
            issues.append(f"{script}: expected status 200, got {response.status}")
            continue
        data, parse_issues = parse_quiz_data(script, response.text)
        issues.extend(parse_issues)
        if parse_issues:
            continue
        labels = data.get("labels", {})
        if not isinstance(labels, dict):
            issues.append(f"{script}: labels should be an object")
        else:
            for label in ("pass_title", "pass_code", "next_pack_title", "primary_route"):
                result_pass_fields_checked += 1
                if not isinstance(labels.get(label), str) or not labels[label].strip():
                    issues.append(f"{script}: labels missing {label}")
        assets_checked += 1
        results = data.get("results")
        if not isinstance(results, dict) or set(results) != EXPECTED_TYPES:
            issues.append(f"{script}: results should contain W/T/G/S/P")
            continue
        for result_type in sorted(EXPECTED_TYPES):
            result = results[result_type]
            slug = TYPE_SLUGS[result_type]
            source = f"{script}:{result_type}:{slug}"
            if not isinstance(result, dict):
                issues.append(f"{source}: result should be an object")
                continue
            results_checked += 1
            for field in RESULT_TEXT_FIELDS:
                result_pass_fields_checked += 1
                if not isinstance(result.get(field), str) or not result[field].strip():
                    issues.append(f"{source}: missing {field}")
            for field in RESULT_NUMBER_FIELDS:
                result_pass_fields_checked += 1
                if not isinstance(result.get(field), int) or result[field] <= 0:
                    issues.append(f"{source}: missing numeric {field}")
            for field in INTERNAL_RESULT_URL_FIELDS:
                value = result.get(field, "")
                if not isinstance(value, str) or not value:
                    issues.append(f"{source}: missing {field}")
                    continue
                result_internal_urls_checked += 1
                url_issues, anchor_checked = check_internal_url(base_url, source, field, value, page_cache)
                issues.extend(url_issues)
                result_anchor_targets_checked += anchor_checked
            for field in RESULT_IMAGE_FIELDS:
                result_images_checked += 1
                issues.extend(check_image_url(base_url, source, field, result.get(field, ""), image_cache))
            result_affiliate_links_checked += 1
            issues.extend(check_affiliate_url(source, result.get("supplyBookUrl", ""), affiliate_cache))

    print(f"public_quiz_conversion_assets_checked={assets_checked}")
    print(f"public_quiz_conversion_results_checked={results_checked}")
    print(f"public_quiz_conversion_internal_urls_checked={result_internal_urls_checked}")
    print(f"public_quiz_conversion_anchor_targets_checked={result_anchor_targets_checked}")
    print(f"public_quiz_conversion_images_checked={result_images_checked}")
    print(f"public_quiz_conversion_affiliate_links_checked={result_affiliate_links_checked}")
    print(f"public_quiz_conversion_pass_fields_checked={result_pass_fields_checked}")
    print(f"public_quiz_conversion_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
