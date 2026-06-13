#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import promotion_post_writeback as writeback


ROOT = Path(__file__).resolve().parents[1]
POST_IMPORT_TOOL = ROOT / "tools" / "promotion_post_text_import.py"
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
PLACEHOLDER_URLS = (
    "https://example.com/post",
    "https://example.com/replace-with-real-post-url",
    "https://www.youtube.com/shorts/replace-with-real-post-id",
    "https://www.youtube.com/shorts/placeholder",
)
SAFE_SAMPLE_URL = "https://www.youtube.com/shorts/lovetypes-proof-url-123"
WRONG_PLATFORM_URLS = {
    "youtube_shorts": "https://www.tiktok.com/@lovetypes/video/1234567890",
    "tiktok": "https://www.instagram.com/reel/lovetypes-proof-url-123/",
    "instagram_reels": "https://www.youtube.com/shorts/lovetypes-proof-url-123",
}
FORBIDDEN_DOC_SNIPPETS = (
    "https://example.com/post",
    "https://example.com/replace-with-real-post-url",
    "https://www.youtube.com/shorts/replace-with-real-post-url",
    "https://www.youtube.com/shorts/replace-with-real-post-id",
    "https://www.youtube.com/shorts/lovetypes-proof-url-123",
)
DOC_SUFFIXES = (".md", ".json", ".csv")


def sample_text(post_url: str, platform: str = "youtube_shorts", task_id: str = "publish-lt-s01-iris-silence") -> str:
    return "\n".join([
        "LoveTypes platform post writeback",
        f"platform: {platform}",
        f"task_id: {task_id}",
        "status: published",
        "published_date: 2026-06-15",
        f"post_url: {post_url}",
        "views: 0",
        "site_clicks: 0",
        "quiz_starts: 0",
        "quiz_completions: 0",
        "proof_note: post URL and first metrics verified",
        "",
    ])


def run_import_check(text: str) -> tuple[int, str]:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as handle:
        handle.write(text)
        temp_path = Path(handle.name)
    try:
        result = subprocess.run(
            [sys.executable, str(POST_IMPORT_TOOL), "check", "--input", str(temp_path)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    finally:
        temp_path.unlink(missing_ok=True)
    return result.returncode, result.stdout


def validate() -> tuple[dict[str, int], list[str]]:
    issues: list[str] = []
    rejected_by_validator = 0
    rejected_by_import = 0
    rejected_wrong_domain_by_validator = 0
    rejected_wrong_domain_by_import = 0
    for url in PLACEHOLDER_URLS:
        if writeback.valid_post_url(url):
            issues.append(f"placeholder URL should be rejected by validator: {url}")
        else:
            rejected_by_validator += 1
        code, output = run_import_check(sample_text(url))
        if code == 0 or "promotion_post_text_import_issues=0" in output:
            issues.append(f"placeholder URL should be rejected by import check: {url}")
        else:
            rejected_by_import += 1

    safe_validator_passed = 1 if writeback.valid_post_url(SAFE_SAMPLE_URL) else 0
    safe_code, safe_output = run_import_check(sample_text(SAFE_SAMPLE_URL))
    safe_import_passed = 1 if safe_code == 0 and "promotion_post_text_import_issues=0" in safe_output else 0
    if not safe_validator_passed:
        issues.append("safe sample URL should pass validator")
    if not safe_import_passed:
        issues.append("safe sample URL should pass import check")
    if not writeback.post_url_matches_platform("youtube_shorts", SAFE_SAMPLE_URL):
        issues.append("safe sample URL should match youtube_shorts platform domain")

    task_ids = {
        "youtube_shorts": "publish-lt-s01-iris-silence",
        "tiktok": "publish-lt-s01-iris-silence",
        "instagram_reels": "publish-lt-s01-iris-silence",
    }
    for platform, url in WRONG_PLATFORM_URLS.items():
        if writeback.valid_post_url(url) and not writeback.post_url_matches_platform(platform, url):
            rejected_wrong_domain_by_validator += 1
        else:
            issues.append(f"wrong-platform URL should pass URL shape but fail platform domain: {platform} {url}")
        code, output = run_import_check(sample_text(url, platform=platform, task_id=task_ids[platform]))
        if code == 0 or "promotion_post_text_import_issues=0" in output:
            issues.append(f"wrong-platform URL should be rejected by import check: {platform} {url}")
        elif "post_url to match platform domain" in output:
            rejected_wrong_domain_by_import += 1
        else:
            issues.append(f"wrong-platform URL rejected for unexpected reason: {platform} {output.strip()}")
    docs_checked = 0
    doc_hits = 0
    for path in sorted(PROMOTION_DIR.glob("*")):
        if path.suffix not in DOC_SUFFIXES:
            continue
        docs_checked += 1
        text = path.read_text(encoding="utf-8")
        for snippet in FORBIDDEN_DOC_SNIPPETS:
            if snippet in text:
                doc_hits += 1
                issues.append(f"{path.relative_to(ROOT)} should not contain stale placeholder {snippet}")

    return {
        "placeholderUrls": len(PLACEHOLDER_URLS),
        "rejectedByValidator": rejected_by_validator,
        "rejectedByImport": rejected_by_import,
        "safeValidatorPassed": safe_validator_passed,
        "safeImportPassed": safe_import_passed,
        "wrongPlatformUrls": len(WRONG_PLATFORM_URLS),
        "wrongPlatformRejectedByValidator": rejected_wrong_domain_by_validator,
        "wrongPlatformRejectedByImport": rejected_wrong_domain_by_import,
        "docsChecked": docs_checked,
        "docHits": doc_hits,
    }, issues


def main() -> int:
    metrics, issues = validate()
    print(f"promotion_placeholder_url_checked={metrics['placeholderUrls']}")
    print(f"promotion_placeholder_url_rejected_by_validator={metrics['rejectedByValidator']}")
    print(f"promotion_placeholder_url_rejected_by_import={metrics['rejectedByImport']}")
    print(f"promotion_placeholder_url_safe_validator_passed={metrics['safeValidatorPassed']}")
    print(f"promotion_placeholder_url_safe_import_passed={metrics['safeImportPassed']}")
    print(f"promotion_placeholder_url_wrong_platform_checked={metrics['wrongPlatformUrls']}")
    print(f"promotion_placeholder_url_wrong_platform_rejected_by_validator={metrics['wrongPlatformRejectedByValidator']}")
    print(f"promotion_placeholder_url_wrong_platform_rejected_by_import={metrics['wrongPlatformRejectedByImport']}")
    print(f"promotion_placeholder_url_docs_checked={metrics['docsChecked']}")
    print(f"promotion_placeholder_url_doc_hits={metrics['docHits']}")
    print(f"promotion_placeholder_url_safety_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
