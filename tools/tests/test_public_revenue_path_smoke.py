from pathlib import Path
import unittest

from tools import public_revenue_path_smoke


class PublicRevenuePathSmokeModuleTest(unittest.TestCase):
    def test_module_root_points_to_love_language_repository(self):
        expected_root = Path(__file__).resolve().parents[2]
        self.assertEqual(public_revenue_path_smoke.ROOT, expected_root)
        self.assertTrue((public_revenue_path_smoke.ROOT / "funnel-events.json").is_file())


if __name__ == "__main__":
    unittest.main()
