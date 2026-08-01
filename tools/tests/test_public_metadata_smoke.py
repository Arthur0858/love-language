#!/usr/bin/env python3
import unittest

from tools.public_metadata_smoke import MetadataParser, duplicate_value_issues, expected_hreflang_map


class PublicMetadataSmokeTest(unittest.TestCase):
    def test_zh_only_hreflang_map(self):
        self.assertEqual(
            expected_hreflang_map("https://lovetypes.tw", "/guides/example/"),
            {
                "zh-TW": "https://lovetypes.tw/guides/example/",
                "x-default": "https://lovetypes.tw/guides/example/",
            },
        )

    def test_parser_collects_one_visible_h1(self):
        parser = MetadataParser()
        parser.feed("<main><h1>關係 <span>指南</span></h1></main>")
        self.assertEqual(parser.h1_count, 1)
        self.assertEqual(" ".join(parser.h1_parts), "關係  指南")

    def test_duplicate_metadata_is_reported(self):
        issues = duplicate_value_issues({"/a/": "同一標題", "/b/": "同一標題", "/c/": "不同"}, "title")
        self.assertEqual(len(issues), 1)
        self.assertIn("/a/, /b/", issues[0])

    def test_unique_metadata_passes(self):
        self.assertEqual(duplicate_value_issues({"/a/": "甲", "/b/": "乙"}, "H1"), [])


if __name__ == "__main__":
    unittest.main()
