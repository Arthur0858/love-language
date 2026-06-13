#!/usr/bin/env python3
from __future__ import annotations

import sys

import promotion_profile_url_smoke


def main() -> int:
    sys.argv = [sys.argv[0], "--public", "--check", *sys.argv[1:]]
    return promotion_profile_url_smoke.main()


if __name__ == "__main__":
    raise SystemExit(main())
