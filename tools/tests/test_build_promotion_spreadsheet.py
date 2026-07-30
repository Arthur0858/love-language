#!/usr/bin/env python3
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "tools" / "build_promotion_spreadsheet.mjs"


class PromotionSpreadsheetBuilderTest(unittest.TestCase):
    def test_check_mode_is_dependency_free_and_validates_all_sheets(self):
        syntax = subprocess.run(["node", "--check", str(BUILDER)], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(syntax.returncode, 0, syntax.stderr)
        result = subprocess.run(["node", str(BUILDER), "--check"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("promotion_spreadsheet=check-only", result.stdout)
        self.assertIn("promotion_spreadsheet_sheets=12", result.stdout)
        self.assertIn("promotion_spreadsheet_rendered_sheets=12", result.stdout)


if __name__ == "__main__":
    unittest.main()
