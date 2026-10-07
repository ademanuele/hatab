#!/usr/bin/env python3
"""Regenerate WebP assets with cwebp (brew install webp).

Original JPEGs stay in img/. HTML uses the generated files in img/optimized/.
"""

import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def encode(source, destination, width, height=0):
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "cwebp", "-quiet", "-preset", "photo", "-q", "75", "-m", "6",
            "-metadata", "icc", "-resize", str(width), str(height),
            "-resize_mode", "down_only", str(source), "-o", str(destination),
        ],
        check=True,
    )


def main():
    if not shutil.which("cwebp"):
        raise SystemExit("Install cwebp first: brew install webp")

    for name, widths in (("hero", (640, 1280, 1920)), ("me", (480, 960))):
        for width in widths:
            encode(ROOT / "img" / (name + ".jpg"),
                   ROOT / "img/optimized" / f"{name}-{width}.webp", width)

    # The portfolio documents the original for each displayed photograph.
    html = (ROOT / "index.html").read_text()
    sources = sorted(set(re.findall(r'data-original="(img/[^" ]+\.(?:jpg|jpeg))"', html)))
    for relative in sources:
        source = ROOT / relative
        folder = ROOT / "img/optimized" / source.parent.name
        for width in (320, 640):
            encode(source, folder / f"{source.stem}-{width}.webp", width)
        # A width bound keeps portrait photographs detailed in the lightbox.
        encode(source, folder / f"{source.stem}-1600.webp", 1600)

    print(f"Generated responsive images for {len(sources)} portfolio photos, hero and portrait.")


if __name__ == "__main__":
    main()
