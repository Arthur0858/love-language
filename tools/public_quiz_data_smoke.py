#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://lovetypes.tw"
LANG_PATHS = {
    "zh": "/",
    "en": "/en/",
    "ja": "/ja/",
    "ko": "/ko/",
    "es": "/es/",
}
EXPECTED_TYPES = {"W", "T", "G", "S", "P"}
EXPECTED_SLUGS = {"iris", "noah", "vivian", "claire", "dora"}
TYPE_SLUGS = {
    "W": "iris",
    "T": "noah",
    "G": "vivian",
    "S": "claire",
    "P": "dora",
}
TYPE_GUIDE_ROUTES = {
    "W": "guides/words-of-affirmation-scripts",
    "T": "guides/quality-time-long-distance",
    "G": "guides/gifts-are-not-materialism",
    "S": "guides/acts-of-service-boundaries",
    "P": "guides/physical-touch-consent-safety",
}
STORY_IMAGE_DIMENSIONS = (1080, 1920)
ASSIGNMENT_RE = re.compile(r"window\.__LOVETYPES_QUIZ_DATA\s*=\s*(\{.*\})\s*;?\s*$", re.S)
QUIZ_SRC_RE = re.compile(r"^/quiz-data-(zh|en|ja|ko|es)-[^/]+\.js$")


@dataclass(frozen=True)
class Response:
    url: str
    status: int
    text: str


class ScriptParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.scripts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        if tag == "script" and data.get("src"):
            self.scripts.append(data["src"])


def normalize_base_url(value: str) -> str:
    return value.rstrip("/") or DEFAULT_BASE_URL


def request_url(url: str, attempts: int = 3) -> Response:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = Request(url, headers={"User-Agent": "LoveTypes public quiz data smoke/1.0"})
            with urlopen(request, timeout=20) as raw:
                return Response(raw.geturl(), raw.status, raw.read().decode("utf-8", errors="replace"))
        except HTTPError as error:
            return Response(error.geturl(), error.code, error.read().decode("utf-8", errors="replace"))
        except (URLError, TimeoutError, OSError) as error:
            last_error = error
            if attempt < attempts:
                time.sleep(0.5 * attempt)
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def localized_path(lang: str, route: str) -> str:
    prefix = "" if lang == "zh" else f"/{lang}"
    if not route:
        return f"{prefix}/" if prefix else "/"
    return f"{prefix}/{route}/" if prefix else f"/{route}/"


def expected_story_cta(lang: str, slug: str) -> str:
    prefix = "" if lang == "zh" else f"/{lang}"
    return f"lovetypes.tw{prefix}/keepsakes/#keepsake-{slug}"


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
    if not isinstance(data, dict):
        return {}, [f"{path}: quiz data should be an object"]
    return data, []


def is_localized_href(value: str, lang: str, route: str) -> bool:
    expected = localized_path(lang, route)
    return value == expected or value.startswith(expected + "#")


def validate_starter_kit(path: str, lang: str, result_type: str, starter: object) -> list[str]:
    issues: list[str] = []
    if not isinstance(starter, dict):
        return [f"{path}: {result_type} starterKit should be an object"]
    steps = starter.get("steps")
    if not isinstance(steps, list) or len(steps) != 4:
        return [f"{path}: {result_type} starterKit should include four steps"]
    required_routes = {"keepsakes", "repair-plan", "luna-yoga-music", "resources"}
    seen_routes: set[str] = set()
    for index, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            issues.append(f"{path}: {result_type} starterKit step {index} should be an object")
            continue
        if not step.get("title") or not step.get("desc") or not step.get("action"):
            issues.append(f"{path}: {result_type} starterKit step {index} missing title/desc/action")
        href = step.get("href", "")
        for route in required_routes:
            if is_localized_href(href, lang, route):
                seen_routes.add(route)
    missing_routes = sorted(required_routes.difference(seen_routes))
    if missing_routes:
        issues.append(f"{path}: {result_type} starterKit missing routes {', '.join(missing_routes)}")
    return issues


def validate_result(path: str, lang: str, result_type: str, result: object) -> list[str]:
    issues: list[str] = []
    if not isinstance(result, dict):
        return [f"{path}: result {result_type} should be an object"]
    slug = TYPE_SLUGS[result_type]
    required_text_fields = {
        "name",
        "type",
        "desc",
        "guideTitle",
        "supplyTitle",
        "supplyDesc",
        "supplyMission",
        "supplyBook",
        "planLabel",
        "collectorTitle",
    }
    for key in sorted(required_text_fields):
        if not isinstance(result.get(key), str) or not result.get(key, "").strip():
            issues.append(f"{path}: {result_type} missing text field {key}")
    if result.get("slug") != slug:
        issues.append(f"{path}: {result_type} slug should be {slug!r}, got {result.get('slug')!r}")
    guide_route = TYPE_GUIDE_ROUTES[result_type]
    if not is_localized_href(result.get("guideUrl", ""), lang, guide_route):
        issues.append(f"{path}: {result_type} guideUrl should point to localized {guide_route}")
    if f"#guide-{slug}" not in result.get("guideUrl", ""):
        issues.append(f"{path}: {result_type} guideUrl should target #guide-{slug}")
    if not is_localized_href(result.get("guardianUrl", ""), lang, f"characters/{slug}"):
        issues.append(f"{path}: {result_type} guardianUrl not localized for {slug}")
    if not is_localized_href(result.get("resourceUrl", ""), lang, "resources"):
        issues.append(f"{path}: {result_type} resourceUrl should point to localized resources")
    if f"#supply-{slug}" not in result.get("resourceUrl", ""):
        issues.append(f"{path}: {result_type} resourceUrl should target #supply-{slug}")
    if not is_localized_href(result.get("lunaUrl", ""), lang, "luna-yoga-music") or f"#luna-{slug}" not in result.get("lunaUrl", ""):
        issues.append(f"{path}: {result_type} lunaUrl should target localized Luna section")
    if not is_localized_href(result.get("planUrl", ""), lang, "repair-plan") or f"#plan-{slug}" not in result.get("planUrl", ""):
        issues.append(f"{path}: {result_type} planUrl should target localized repair plan")
    if not is_localized_href(result.get("collectorHallUrl", ""), lang, "keepsakes") or f"#keepsake-{slug}" not in result.get("collectorHallUrl", ""):
        issues.append(f"{path}: {result_type} collectorHallUrl should target localized keepsake")
    if not isinstance(result.get("tips"), list) or len(result.get("tips", [])) < 2:
        issues.append(f"{path}: {result_type} should include at least two tips")
    supply_book_url = result.get("supplyBookUrl", "")
    if not supply_book_url.startswith("https://www.books.com.tw/"):
        issues.append(f"{path}: {result_type} supplyBookUrl should point to books.com.tw")
    for token in ("arthur0858", "utm_campaign=ap-202604"):
        if token not in supply_book_url:
            issues.append(f"{path}: {result_type} supplyBookUrl missing {token}")
    for image_key in ("image", "resultImage", "storyImage"):
        image = result.get(image_key, "")
        if not isinstance(image, str) or not image.startswith("/assets/lovetypes/"):
            issues.append(f"{path}: {result_type} {image_key} should use LoveTypes asset path")
    expected_story_image = f"/assets/lovetypes/share/{slug}-story-{lang}.webp"
    if result.get("storyImage") != expected_story_image:
        issues.append(f"{path}: {result_type} storyImage should be {expected_story_image}")
    for size_key in ("imageWidth", "imageHeight", "resultImageWidth", "resultImageHeight", "storyImageWidth", "storyImageHeight"):
        if not isinstance(result.get(size_key), int) or result[size_key] <= 0:
            issues.append(f"{path}: {result_type} {size_key} should be a positive integer")
    expected_story_width, expected_story_height = STORY_IMAGE_DIMENSIONS
    if result.get("storyImageWidth") != expected_story_width:
        issues.append(f"{path}: {result_type} storyImageWidth should be {expected_story_width}")
    if result.get("storyImageHeight") != expected_story_height:
        issues.append(f"{path}: {result_type} storyImageHeight should be {expected_story_height}")
    if result.get("collectorStoryCta") != expected_story_cta(lang, slug):
        issues.append(f"{path}: {result_type} collectorStoryCta should target localized keepsake {slug}")
    issues.extend(validate_starter_kit(path, lang, result_type, result.get("starterKit")))
    return issues


def validate_quiz_data(path: str, lang: str, data: dict) -> tuple[list[str], int, int]:
    issues: list[str] = []
    labels = data.get("labels")
    if not isinstance(labels, dict):
        issues.append(f"{path}: labels should be an object")
    else:
        for key in ("start", "next", "see", "result_label", "primary_route", "secondary_plan", "luna_action", "book_action", "boundary"):
            if not isinstance(labels.get(key), str) or not labels.get(key, "").strip():
                issues.append(f"{path}: missing label {key}")

    questions = data.get("questions")
    questions_checked = 0
    if not isinstance(questions, list) or len(questions) != 15:
        issues.append(f"{path}: expected 15 questions, got {len(questions) if isinstance(questions, list) else 'invalid'}")
    elif questions:
        for index, question in enumerate(questions, start=1):
            if not isinstance(question, dict) or not question.get("text"):
                issues.append(f"{path}: question {index} missing text")
                continue
            options = question.get("options")
            if not isinstance(options, list) or len(options) != 5:
                issues.append(f"{path}: question {index} should include five options")
                continue
            option_types = [option.get("type") for option in options if isinstance(option, dict)]
            if set(option_types) != EXPECTED_TYPES or len(option_types) != 5:
                issues.append(f"{path}: question {index} option types should be W/T/G/S/P once, got {option_types}")
            if any(not isinstance(option.get("text"), str) or not option.get("text", "").strip() for option in options if isinstance(option, dict)):
                issues.append(f"{path}: question {index} option text missing")
            questions_checked += 1

    results = data.get("results")
    results_checked = 0
    if not isinstance(results, dict) or set(results) != EXPECTED_TYPES:
        issues.append(f"{path}: results should contain W/T/G/S/P, got {sorted(results) if isinstance(results, dict) else 'invalid'}")
    elif results:
        seen_slugs = set()
        for result_type in sorted(EXPECTED_TYPES):
            result = results[result_type]
            if isinstance(result, dict):
                seen_slugs.add(result.get("slug"))
            issues.extend(validate_result(path, lang, result_type, result))
            results_checked += 1
        if seen_slugs != EXPECTED_SLUGS:
            issues.append(f"{path}: result slugs should be {sorted(EXPECTED_SLUGS)}, got {sorted(seen_slugs)}")

    return issues, questions_checked, results_checked


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public LoveTypes quiz data payloads across languages.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Public deployment base URL.")
    args = parser.parse_args()
    base_url = normalize_base_url(args.base_url)

    issues: list[str] = []
    quiz_assets_checked = 0
    quiz_questions_checked = 0
    quiz_results_checked = 0
    quiz_guide_urls_checked = 0
    quiz_story_images_checked = 0
    quiz_story_ctas_checked = 0
    quiz_starter_steps_checked = 0
    seen_assets: set[str] = set()

    for lang, path in LANG_PATHS.items():
        script, discovery_issues = discover_quiz_asset(base_url, lang, path)
        issues.extend(discovery_issues)
        if not script:
            continue
        seen_assets.add(script)
        response = request_url(urljoin(base_url + "/", script.lstrip("/")))
        if response.status != 200:
            issues.append(f"{script}: expected status 200, got {response.status}")
            continue
        data, parse_issues = parse_quiz_data(script, response.text)
        issues.extend(parse_issues)
        if parse_issues:
            continue
        data_issues, questions_checked, results_checked = validate_quiz_data(script, lang, data)
        issues.extend(data_issues)
        quiz_assets_checked += 1
        quiz_questions_checked += questions_checked
        quiz_results_checked += results_checked
        if isinstance(data.get("results"), dict):
            quiz_guide_urls_checked += sum(
                1
                for result_type, result in data["results"].items()
                if result_type in TYPE_GUIDE_ROUTES
                and isinstance(result, dict)
                and is_localized_href(result.get("guideUrl", ""), lang, TYPE_GUIDE_ROUTES[result_type])
                and f"#guide-{TYPE_SLUGS[result_type]}" in result.get("guideUrl", "")
            )
            quiz_story_images_checked += sum(
                1
                for result_type, result in data["results"].items()
                if result_type in TYPE_SLUGS
                and isinstance(result, dict)
                and result.get("storyImage") == f"/assets/lovetypes/share/{TYPE_SLUGS[result_type]}-story-{lang}.webp"
                and result.get("storyImageWidth") == STORY_IMAGE_DIMENSIONS[0]
                and result.get("storyImageHeight") == STORY_IMAGE_DIMENSIONS[1]
            )
            quiz_story_ctas_checked += sum(
                1
                for result_type, result in data["results"].items()
                if result_type in TYPE_SLUGS
                and isinstance(result, dict)
                and result.get("collectorStoryCta") == expected_story_cta(lang, TYPE_SLUGS[result_type])
            )
        if isinstance(data.get("results"), dict):
            for result in data["results"].values():
                if isinstance(result, dict) and isinstance(result.get("starterKit"), dict):
                    steps = result["starterKit"].get("steps")
                    if isinstance(steps, list):
                        quiz_starter_steps_checked += len(steps)

    if len(seen_assets) != len(LANG_PATHS):
        issues.append(f"expected five unique quiz assets, found {len(seen_assets)}")

    print(f"public_quiz_assets_checked={quiz_assets_checked}")
    print(f"public_quiz_questions_checked={quiz_questions_checked}")
    print(f"public_quiz_results_checked={quiz_results_checked}")
    print(f"public_quiz_guide_urls_checked={quiz_guide_urls_checked}")
    print(f"public_quiz_story_images_checked={quiz_story_images_checked}")
    print(f"public_quiz_story_ctas_checked={quiz_story_ctas_checked}")
    print(f"public_quiz_starter_steps_checked={quiz_starter_steps_checked}")
    print(f"public_quiz_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
