#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import generate_multilingual_site as generator


class PromotionSourceFallbackTest(unittest.TestCase):
    def test_tracked_manifest_is_used_when_ignored_sources_are_absent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            manifest = json.loads((ROOT / "promotion-kit.json").read_text(encoding="utf-8"))
            (temp_root / "promotion-kit.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            with mock.patch.object(generator, "ROOT", temp_root):
                result = generator.collect_promotion_kit()
        self.assertEqual(len(result["publishingTasks"]), 15)
        self.assertEqual(len(result["publishingCalendar"]), 15)

    def test_partial_source_set_is_not_silently_mixed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            source_dir = temp_root / "docs" / "promotion" / "first-round"
            source_dir.mkdir(parents=True)
            (source_dir / "publishing-calendar.csv").write_text(
                "week,slot\n1,1\n", encoding="utf-8"
            )
            with mock.patch.object(generator, "ROOT", temp_root):
                with self.assertRaisesRegex(FileNotFoundError, "promotion source set is incomplete"):
                    generator.collect_promotion_kit()


if __name__ == "__main__":
    unittest.main()
