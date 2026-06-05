#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "assets/lovetypes/guardians/cards"
MAX_EDGE = 560
QUALITY = 82

SOURCES = {
    "iris": ROOT / "assets/lovetypes/guardians/iris.webp",
    "noah": ROOT / "assets/lovetypes/guardians/noah.webp",
    "vivian": ROOT / "assets/lovetypes/guardians/vivian.webp",
    "claire": ROOT / "assets/lovetypes/guardians/claire.webp",
    "dora": ROOT / "assets/lovetypes/guardians/dora.webp",
}


def resize_size(width: int, height: int) -> tuple[int, int]:
    scale = MAX_EDGE / max(width, height)
    if scale >= 1:
        return width, height
    return round(width * scale), round(height * scale)


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for slug, source in SOURCES.items():
        target = OUTPUT_DIR / f"{slug}-card.webp"
        with Image.open(source) as image:
            image = image.convert("RGB")
            size = resize_size(*image.size)
            if size != image.size:
                image = image.resize(size, Image.Resampling.LANCZOS)
            image.save(target, "WEBP", quality=QUALITY, method=6)
        print(f"{target.relative_to(ROOT)} {target.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
