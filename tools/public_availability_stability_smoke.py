#!/usr/bin/env python3
"""Sample critical production pages and assets repeatedly without retrying failures."""

from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from generate_multilingual_site import (
    COMPASS_TOOL_ASSET,
    CSS_ASSET,
    GUARDIAN_EDITORIAL_ASSET,
    INTERACTIONS_ASSET,
    QUIZ_DATA_ASSETS,
)


DEFAULT_BASE_URL = "https://lovetypes.tw"
PAGE_PATHS = (
    "/",
    "/start/",
    "/guides/",
    "/guides/share-your-result/",
    "/lab/",
    "/lab/quiz-scoring-test/",
    "/characters/",
    "/characters/iris/",
    "/compass/",
    "/repair-plan/",
    "/about/",
    "/contact/",
)
ASSET_PATHS = (
    CSS_ASSET,
    GUARDIAN_EDITORIAL_ASSET,
    INTERACTIONS_ASSET,
    QUIZ_DATA_ASSETS["zh"],
    COMPASS_TOOL_ASSET,
    "/assets/lovetypes/guardians/cards/iris-card.webp",
    "/assets/lovetypes/guardians/cards/noah-card.webp",
    "/assets/lovetypes/guardians/cards/vivian-card.webp",
    "/assets/lovetypes/guardians/cards/claire-card.webp",
    "/assets/lovetypes/guardians/cards/dora-card.webp",
    "/assets/lovetypes/lab/quiz-scoring-test.webp",
    "/assets/lovetypes/lab/quiz-scoring-test-detail.webp",
)


@dataclass(frozen=True)
class Sample:
    path: str
    kind: str
    status: int
    content_type: str
    body_prefix: bytes
    elapsed_ms: int


def sample_issues(sample: Sample) -> list[str]:
    issues: list[str] = []
    content_type = sample.content_type.lower()
    if sample.status != 200:
        issues.append(f"{sample.path}: expected 200, got {sample.status}")
        return issues
    if not sample.body_prefix:
        issues.append(f"{sample.path}: empty response body")
    if sample.kind == "page":
        if not content_type.startswith("text/html"):
            issues.append(f"{sample.path}: expected text/html, got {sample.content_type!r}")
        if b"<html" not in sample.body_prefix.lower() and b"<!doctype html" not in sample.body_prefix.lower():
            issues.append(f"{sample.path}: response prefix is not HTML")
    elif content_type.startswith("text/html"):
        issues.append(f"{sample.path}: asset unexpectedly returned HTML")
    return issues


def fetch(base_url: str, path: str, kind: str) -> Sample:
    url = urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
    request = Request(
        url,
        headers={
            "User-Agent": "LoveTypes availability stability smoke/1.0",
            "Cache-Control": "no-cache",
        },
    )
    started = time.monotonic()
    try:
        with urlopen(request, timeout=20) as response:
            body_prefix = response.read(2048)
            return Sample(
                path,
                kind,
                response.status,
                response.headers.get("Content-Type", ""),
                body_prefix,
                round((time.monotonic() - started) * 1000),
            )
    except HTTPError as error:
        return Sample(
            path,
            kind,
            error.code,
            error.headers.get("Content-Type", ""),
            error.read(2048),
            round((time.monotonic() - started) * 1000),
        )
    except (URLError, TimeoutError, OSError) as error:
        return Sample(path, kind, 0, "", str(error).encode(), round((time.monotonic() - started) * 1000))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--round-delay", type=float, default=0.75)
    args = parser.parse_args()
    if args.rounds < 2 or args.workers < 1 or args.round_delay < 0:
        parser.error("rounds must be >= 2, workers >= 1 and round-delay >= 0")

    cases = [(path, "page") for path in PAGE_PATHS] + [(path, "asset") for path in ASSET_PATHS]
    issues: list[str] = []
    samples: list[Sample] = []
    failed_requests = 0
    server_errors = 0
    for round_number in range(1, args.rounds + 1):
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {
                pool.submit(fetch, args.base_url, path, kind): (path, kind)
                for path, kind in cases
            }
            for future in as_completed(futures):
                sample = future.result()
                samples.append(sample)
                current = sample_issues(sample)
                if current:
                    failed_requests += 1
                    if 500 <= sample.status <= 599:
                        server_errors += 1
                    issues.extend(f"round {round_number}: {issue}" for issue in current)
        if round_number < args.rounds and args.round_delay:
            time.sleep(args.round_delay)

    print(f"public_availability_stability_rounds={args.rounds}")
    print(f"public_availability_stability_urls_checked={len(cases)}")
    print(f"public_availability_stability_requests={len(samples)}")
    print(f"public_availability_stability_failed_requests={failed_requests}")
    print(f"public_availability_stability_server_errors={server_errors}")
    print(f"public_availability_stability_max_response_ms={max((sample.elapsed_ms for sample in samples), default=0)}")
    print(f"public_availability_stability_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
