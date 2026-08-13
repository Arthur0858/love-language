#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import promotion_render_bridge as bridge


class ScheduleSafetyTest(unittest.TestCase):
    def test_active_read_only_health_check_does_not_require_pause(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            schedules = Path(tmp) / "schedules.toml"
            schedules.write_text(
                """[[schedules]]
id = "lovetypes-nightly-shorts-render"
status = "ACTIVE"
command = ["python3", "scripts/check_lovetypes_offload_health.py"]
""",
                encoding="utf-8",
            )
            original = bridge.SCHEDULES
            bridge.SCHEDULES = schedules
            try:
                self.assertFalse(bridge.schedule_requires_pause())
            finally:
                bridge.SCHEDULES = original


if __name__ == "__main__":
    unittest.main()
