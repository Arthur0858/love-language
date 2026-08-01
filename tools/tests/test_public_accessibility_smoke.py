#!/usr/bin/env python3
import unittest

from tools.public_accessibility_smoke import audit_page


VALID_PAGE = """
<!doctype html>
<html lang="zh-TW">
<head><title>測試頁</title></head>
<body>
  <a class="skip-link" href="#main">跳到主要內容</a>
  <nav aria-label="主要導覽"><a href="/guides/">指南</a></nav>
  <main id="main">
    <h1>測試頁</h1>
    <label for="topic">主題</label><input id="topic" name="topic">
    <img src="/image.webp" alt="測試畫面" width="1200" height="630" loading="lazy">
    <button type="button">開始</button>
  </main>
</body>
</html>
"""


class PublicAccessibilitySmokeTest(unittest.TestCase):
    def test_valid_page_passes(self):
        issues, stats = audit_page("https://lovetypes.tw/test/", VALID_PAGE)
        self.assertEqual(issues, [])
        self.assertEqual(stats["skip_links"], 1)
        self.assertEqual(stats["main_targets"], 1)
        self.assertEqual(stats["controls"], 1)

    def test_wrong_language_and_duplicate_id_fail(self):
        raw = VALID_PAGE.replace('lang="zh-TW"', 'lang="en"').replace('<main id="main">', '<main id="main"><span id="main"></span>')
        issues, _stats = audit_page("https://lovetypes.tw/test/", raw)
        self.assertTrue(any("html lang should be" in issue for issue in issues))
        self.assertTrue(any("duplicate id #main" in issue for issue in issues))

    def test_missing_accessible_names_fail(self):
        raw = VALID_PAGE.replace('<a href="/guides/">指南</a>', '<a href="/guides/"></a>')
        raw = raw.replace('<button type="button">開始</button>', '<button type="button"></button>')
        issues, _stats = audit_page("https://lovetypes.tw/test/", raw)
        self.assertTrue(any("link /guides/ missing accessible name" in issue for issue in issues))
        self.assertTrue(any("button missing accessible name" in issue for issue in issues))

    def test_missing_image_alt_and_control_label_fail(self):
        raw = VALID_PAGE.replace(' alt="測試畫面"', '').replace('<label for="topic">主題</label>', '')
        issues, _stats = audit_page("https://lovetypes.tw/test/", raw)
        self.assertTrue(any("missing alt" in issue for issue in issues))
        self.assertTrue(any("control topic missing label" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
