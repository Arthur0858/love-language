from pathlib import Path
import unittest

from tools import public_revenue_path_smoke


class PublicRevenuePathSmokeModuleTest(unittest.TestCase):
    def test_module_root_points_to_love_language_repository(self):
        expected_root = Path(__file__).resolve().parents[2]
        self.assertEqual(public_revenue_path_smoke.ROOT, expected_root)
        self.assertTrue((public_revenue_path_smoke.ROOT / "funnel-events.json").is_file())

    def test_luna_product_url_requires_attribution_and_sponsored_rel(self):
        link = {
            "href": "https://lunayogamusic.gumroad.com/l/healing-vibes-starter?utm_source=lovetypes&utm_medium=luna-page&utm_campaign=luna_gumroad_offer&utm_content=healing-vibes-starter",
            "data-luna-product": "healing-vibes-starter",
            "data-funnel-event": "luna_gumroad_pack_click",
            "rel": "noopener noreferrer sponsored",
        }
        self.assertTrue(public_revenue_path_smoke.is_gumroad_product_link(link))
        self.assertFalse(public_revenue_path_smoke.is_gumroad_product_link({**link, "rel": "noopener noreferrer"}))

    def test_luna_starter_url_uses_its_dedicated_event(self):
        link = {
            "href": "https://lunayogamusic.gumroad.com/l/healing-vibes-starter?utm_source=lovetypes&utm_medium=luna-page&utm_campaign=luna_gumroad_offer&utm_content=healing-vibes-starter",
            "data-luna-product": "healing-vibes-starter",
            "data-funnel-event": "luna_starter_pack_click",
            "rel": "noopener noreferrer sponsored",
        }
        self.assertTrue(public_revenue_path_smoke.is_gumroad_product_link(link, "luna_starter_pack_click"))

    def test_html_parser_reads_noindex_directive(self):
        parser = public_revenue_path_smoke.parse_html('<meta name="robots" content="noindex, follow">')
        self.assertEqual(parser.robots, "noindex, follow")


if __name__ == "__main__":
    unittest.main()
