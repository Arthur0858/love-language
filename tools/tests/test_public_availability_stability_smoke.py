#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.public_availability_stability_smoke import Sample, sample_issues


class PublicAvailabilityStabilitySmokeTest(unittest.TestCase):
    def test_html_page_and_binary_asset_pass(self):
        page = Sample("/", "page", 200, "text/html; charset=utf-8", b"<!doctype html><html>", 100)
        asset = Sample("/asset.webp", "asset", 200, "image/webp", b"RIFF", 100)
        self.assertEqual(sample_issues(page), [])
        self.assertEqual(sample_issues(asset), [])

    def test_server_error_and_html_asset_fail(self):
        unavailable = Sample("/", "page", 502, "text/html", b"bad gateway", 100)
        wrong_asset = Sample("/asset.css", "asset", 200, "text/html", b"<!doctype html>", 100)
        self.assertTrue(any("got 502" in issue for issue in sample_issues(unavailable)))
        self.assertTrue(any("returned HTML" in issue for issue in sample_issues(wrong_asset)))


if __name__ == "__main__":
    unittest.main()
