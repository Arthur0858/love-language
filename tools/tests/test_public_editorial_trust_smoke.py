#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.public_editorial_trust_smoke import similarity_issues


class PublicEditorialTrustSmokeTest(unittest.TestCase):
    def test_distinct_articles_pass(self):
        maximum_jaccard, maximum_containment, issues = similarity_issues(
            "guide",
            {"a": frozenset({"甲", "乙"}), "b": frozenset({"丙", "丁"})},
        )
        self.assertEqual(maximum_jaccard, 0.0)
        self.assertEqual(maximum_containment, 0.0)
        self.assertEqual(issues, [])

    def test_contained_article_is_reported(self):
        maximum_jaccard, maximum_containment, issues = similarity_issues(
            "lab",
            {"a": frozenset({"甲", "乙", "丙"}), "b": frozenset({"甲", "乙", "丙", "丁"})},
        )
        self.assertGreaterEqual(maximum_jaccard, 0.30)
        self.assertEqual(maximum_containment, 1.0)
        self.assertEqual(len(issues), 1)
        self.assertIn("lab pages too similar", issues[0])


if __name__ == "__main__":
    unittest.main()
