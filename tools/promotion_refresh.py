#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFRESH_FLAG = "LOVETYPES_PROMOTION_DAILY_REFRESH_RUNNING"


def run_daily_ops_refresh() -> None:
    if os.environ.get(REFRESH_FLAG) == "1":
        return
    env = {**os.environ, REFRESH_FLAG: "1"}
    subprocess.run([sys.executable, "tools/promotion_daily_ops_refresh.py"], cwd=ROOT, env=env, check=True)

