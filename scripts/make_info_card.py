"""
make_info_card.py
Hand-authored neofetch-style SVG panel: title bar + colored key/value rows.
Each line fades and slides in on a short stagger. STATIC=1 emits a frozen
frame (for local Quick Look previews / non-animated fallback).
"""
import os

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "info-card.svg")
STATIC = os.environ.get("STATIC") == "1"

# --- edit this block to update the card's content ---
USER_AT_HOST = "darshil@github"
ROWS = [
    ("Now", "Cybersecurity Analyst (job hunting, OPT)"),
    ("Prev", "GTU IDEA Lab (AI/ML) - WeTheDevelopers (Java)"),
    ("Stack", "Python - SQL - Power BI - NIST 800-53/CSF/RMF"),
    ("Certs", "CompTIA Security+ - ISC2 CC"),
    ("Base", "Arlington, VA"),
    ("Grad", "MS Cybersecurity - GWU, 2026"),
]
ACCENT = "#39d353"
FG = "#c9d1d9"
DIM = "#8b949e"
BG = "#0d1117"
BORDER = "#30363d"
# ------------------------------------------------------

WIDTH = 490
LINE_H = 26
TOP_PAD = 58
LEFT_PAD = 20
HEIGHT = TOP_PAD + LINE_H * (len(ROWS) + 1) + 24


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    height = HEIGHT
    parts = []
    parts.append(
        f'<svg viewBox="0 0 {WIDTH} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Menlo, Consolas, monospace">'
    )
    parts.append(
        f'<rect x="0.5" y="0.5" width="{WIDTH-1}" height="{height-1}" rx="8" '
        f'fill="{BG}" stroke="{BORDER}"/>'
    )
    # title bar
    parts.append(f'<circle cx="18" cy="18" r="5" fill="#ff5f56"/>')
    parts.append(f'<circle cx="34" cy="18" r="5" fill="#ffbd2e"/>')
    parts.append(f'<circle cx="50" cy="18" r="5" fill="#27c93f"/>')
    parts.append(
        f'<text x="{WIDTH/2}" y="22" font-size="11" fill="{DIM}" text-anchor="middle">neofetch</text>'
    )
    parts.append(f'<line x1="0" y1="34" x2="{WIDTH}" y2="34" stroke="{BORDER}"/>')

    if not STATIC:
        parts.append("<style>")
        parts.append(".row{opacity:0; transform:translateX(-8px);}")
        for i in range(len(ROWS) + 1):
            delay = 0.15 + i * 0.14
            parts.append(
                f".r{i}{{animation:fadeIn 0.4s ease-out forwards; animation-delay:{delay:.2f}s;}}"
            )
        parts.append(
            "@keyframes fadeIn{to{opacity:1; transform:translateX(0);}}"
        )
        parts.append("</style>")
        row_class = lambda i: f'row r{i}'
    else:
        row_class = lambda i: 'row'
        # force visible when static
        parts.append("<style>.row{opacity:1 !important; transform:none !important;}</style>")

    # user@host header line
    parts.append(
        f'<text class="{row_class(0)}" x="{LEFT_PAD}" y="{TOP_PAD}" font-size="14" '
        f'font-weight="bold" fill="{ACCENT}">{esc(USER_AT_HOST)}</text>'
    )
    parts.append(
        f'<line class="{row_class(0)}" x1="{LEFT_PAD}" y1="{TOP_PAD+8}" '
        f'x2="{WIDTH-LEFT_PAD}" y2="{TOP_PAD+8}" stroke="{BORDER}"/>'
    )

    for i, (key, val) in enumerate(ROWS, start=1):
        y = TOP_PAD + LINE_H * i + 8
        parts.append(f'<g class="{row_class(i)}">')
        parts.append(
            f'<text x="{LEFT_PAD}" y="{y}" font-size="12.5" font-weight="bold" '
            f'fill="{ACCENT}">{esc(key)}</text>'
        )
        parts.append(
            f'<text x="{LEFT_PAD + 78}" y="{y}" font-size="12.5" fill="{FG}">{esc(val)}</text>'
        )
        parts.append("</g>")

    parts.append("</svg>")

    with open(OUT_PATH, "w") as f:
        f.write("\n".join(parts))
    print(f"Wrote {OUT_PATH} ({WIDTH}x{height})")


if __name__ == "__main__":
    main()
