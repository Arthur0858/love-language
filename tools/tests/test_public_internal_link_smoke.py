import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.public_internal_link_smoke import (
    AnchorEvidence,
    AnchorParser,
    InternalLink,
    allowed_noindex_internal_target,
)


class PublicInternalLinkSmokeTest(unittest.TestCase):
    def test_parser_records_commercial_footer_context_and_nested_text(self):
        parser = AnchorParser()
        parser.feed(
            '<p class="footer-commercial"><a href="/resources/">'
            '<span>延伸資源與</span>商業揭露</a></p>'
        )
        self.assertEqual(parser.anchors, [("/resources/", "延伸資源與商業揭露", True)])

    def test_exact_commercial_disclosure_footer_link_is_allowed(self):
        link = InternalLink(
            "https://lovetypes.tw/resources/",
            ("/", "/start/"),
            (
                AnchorEvidence("/", "/resources/", "延伸資源與商業揭露", True),
                AnchorEvidence("/start/", "/resources/", "延伸資源與商業揭露", True),
            ),
        )
        self.assertTrue(allowed_noindex_internal_target(link, "/resources/"))

    def test_resources_link_in_body_or_with_other_label_is_rejected(self):
        body_link = InternalLink(
            "https://lovetypes.tw/resources/",
            ("/",),
            (AnchorEvidence("/", "/resources/", "立即取得補給", False),),
        )
        mislabeled_footer = InternalLink(
            "https://lovetypes.tw/resources/",
            ("/",),
            (AnchorEvidence("/", "/resources/", "更多內容", True),),
        )
        self.assertFalse(allowed_noindex_internal_target(body_link, "/resources/"))
        self.assertFalse(allowed_noindex_internal_target(mislabeled_footer, "/resources/"))

    def test_mixed_links_to_resources_from_one_page_are_rejected(self):
        link = InternalLink(
            "https://lovetypes.tw/resources/",
            ("/",),
            (
                AnchorEvidence("/", "/resources/", "延伸資源與商業揭露", True),
                AnchorEvidence("/", "/resources/", "立即購買", False),
            ),
        )
        self.assertFalse(allowed_noindex_internal_target(link, "/resources/"))

    def test_query_links_and_unapproved_noindex_targets_are_rejected(self):
        query_link = InternalLink(
            "https://lovetypes.tw/resources/?source=footer",
            ("/",),
            (AnchorEvidence("/", "/resources/?source=footer", "延伸資源與商業揭露", True),),
        )
        other_noindex = InternalLink("https://lovetypes.tw/keepsakes/", ("/",), ())
        self.assertFalse(allowed_noindex_internal_target(query_link, "/resources/"))
        self.assertFalse(allowed_noindex_internal_target(other_noindex, "/keepsakes/"))

    def test_lab_evidence_links_remain_limited_to_lab_index(self):
        from_lab_index = InternalLink("https://lovetypes.tw/lab/quiz-test/", ("/lab/",), ())
        from_home = InternalLink("https://lovetypes.tw/lab/quiz-test/", ("/",), ())
        self.assertTrue(allowed_noindex_internal_target(from_lab_index, "/lab/quiz-test/"))
        self.assertFalse(allowed_noindex_internal_target(from_home, "/lab/quiz-test/"))


if __name__ == "__main__":
    unittest.main()
