"""
make_ascii_svg.py
Downsamples source-prepped.png to a character grid (~100x53) and maps each
pixel's brightness to a glyph from a density ramp (sparse -> bright,
dense -> dark). Monochrome, single fill color -- rainbow-per-character is
what makes ASCII portraits look like static.

Animation: each row wipes in left-to-right (clip-path), staggered top to
bottom. Prints once, then freezes -- no looping.

Usage: python scripts/make_ascii_svg.py [source-prepped.png]
"""
import sys
import os

import numpy as np
from PIL import Image

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense); leading space = background
COLS = 100
ROWS = 53
CHAR_W = 6.2
CHAR_H = 11
FILL = "#c9d1d9"

IN_PATH = sys.argv[1] if len(sys.argv) > 1 else "source-prepped.png"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "darshil-ascii.svg")


def to_glyphs(img):
    img = img.convert("L").resize((COLS, ROWS))
    arr = np.array(img).astype(float)
    # brighter pixel -> earlier (sparser) ramp index
    idx = (arr / 255.0 * (len(RAMP) - 1)).astype(int)
    idx = len(RAMP) - 1 - idx  # invert: dark pixel -> dense glyph
    glyphs = [[RAMP[i] for i in row] for row in idx]
    return glyphs


def esc(ch):
    return {"&": "&amp;", "<": "&lt;", ">": "&gt;"}.get(ch, ch)


def main():
    if not os.path.exists(IN_PATH):
        print(f"Input not found: {IN_PATH}. Run prep_photo.py first.")
        sys.exit(1)

    img = Image.open(IN_PATH)
    glyphs = to_glyphs(img)

    width = COLS * CHAR_W
    height = ROWS * CHAR_H

    parts = []
    parts.append(
        f'<svg viewBox="0 0 {width:.0f} {height:.0f}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Menlo, Consolas, monospace">'
    )
    parts.append(f'<rect width="{width:.0f}" height="{height:.0f}" fill="none"/>')

    parts.append("<style>")
    parts.append(".row{opacity:0;}")
    row_delay = 0.045
    for r in range(ROWS):
        parts.append(
            f".row{r}{{animation:showRow 0.01s linear forwards; "
            f"animation-delay:{r*row_delay:.3f}s;}}"
        )
    parts.append("@keyframes showRow{to{opacity:1;}}")
    parts.append("</style>")

    for r, row in enumerate(glyphs):
        line = "".join(esc(ch) for ch in row)
        y = (r + 1) * CHAR_H
        # skip fully-blank rows to keep file size down
        if line.strip() == "":
            continue
        parts.append(
            f'<text class="row row{r}" x="0" y="{y:.1f}" font-size="{CHAR_H-1}" '
            f'fill="{FILL}" xml:space="preserve">{line}</text>'
        )

    parts.append("</svg>")

    with open(OUT_PATH, "w") as f:
        f.write("\n".join(parts))
    print(f"Wrote {OUT_PATH} ({width:.0f}x{height:.0f})")


if __name__ == "__main__":
    main()
