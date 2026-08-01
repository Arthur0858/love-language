#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.public_adsense_review_smoke import Response, crawler_parity_issues, page_signature


def response(body: str, *, status: int = 200, url: str = "https://lovetypes.tw/guides/example/") -> Response:
    return Response(status=status, url=url, headers={"Content-Type": "text/html"}, body=body.encode())


BASE_HTML = """
<!doctype html><html lang="zh-TW"><head>
<link rel="canonical" href="https://lovetypes.tw/guides/example/">
<meta name="robots" content="index, follow">
</head><body><main><h1>關係指南</h1><p>可供讀者直接閱讀的正文。</p></main></body></html>
"""


class PublicAdsenseReviewSmokeTest(unittest.TestCase):
    def test_signature_ignores_markup_inside_main(self):
        signature = page_signature(response(BASE_HTML))
        self.assertEqual(signature["h1"], "關係指南")
        self.assertEqual(signature["main"], "關係指南 可供讀者直接閱讀的正文。")

    def test_identical_crawler_response_passes(self):
        baseline = response(BASE_HTML)
        crawler = response(BASE_HTML.replace("<body>", '<body data-cf-beacon="injected">'))
        self.assertEqual(crawler_parity_issues("/guides/example/", baseline, crawler, "Googlebot"), [])

    def test_changed_main_or_status_is_reported(self):
        baseline = response(BASE_HTML)
        changed = response(BASE_HTML.replace("可供讀者直接閱讀的正文。", "存取遭拒。"), status=403)
        issues = crawler_parity_issues("/guides/example/", baseline, changed, "AdsBot-Google")
        self.assertTrue(any("status differs" in issue for issue in issues))
        self.assertTrue(any("main content differs" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
