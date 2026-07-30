"""
render_heatmap_svg.py
Renders data/contributions.json as a 53-week x 7-day calendar of rounded
boxes. Reveals once with a diagonal, line-after-line slide-down (CSS
keyframes that play on load, then freeze -- no looping).
Output: contrib-heatmap.svg (written to repo root).
"""
import json
import os
from datetime import datetime
from collections import defaultdict

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "contrib-heatmap.svg")

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
CELL = 12
GAP = 3
LEFT_PAD = 30
TOP_PAD = 40
BOTTOM_PAD = 46
DAY_LABELS = ["Mon", "", "Wed", "", "Fri", "", ""]


def load_data():
    with open(DATA_PATH) as f:
        return json.load(f)


def bucket_by_week(days):
    weeks = defaultdict(dict)
    for d in days:
        dt = datetime.strptime(d["date"], "%Y-%m-%d")
        week_idx = dt.isocalendar()[1] + (52 * (dt.year - datetime.strptime(days[0]["date"], "%Y-%m-%d").year))
        weekday = dt.weekday()  # Monday=0
        weeks[week_idx][weekday] = d
    ordered_weeks = sorted(weeks.keys())
    return [weeks[w] for w in ordered_weeks]


def month_labels(days, weeks):
    labels = []
    last_month = None
    dt0 = datetime.strptime(days[0]["date"], "%Y-%m-%d")
    week_start_dates = []
    idx = 0
    for wk in weeks:
        first_day = next(iter(sorted(wk.items())), None)
        if first_day:
            week_start_dates.append(datetime.strptime(wk[first_day[0]]["date"], "%Y-%m-%d"))
        else:
            week_start_dates.append(None)
    for i, d in enumerate(week_start_dates):
        if d and d.month != last_month:
            labels.append((i, d.strftime("%b")))
            last_month = d.month
    return labels


def main():
    payload = load_data()
    days = payload["days"]
    stats = payload.get("stats", {})
    weeks = bucket_by_week(days)
    n_weeks = len(weeks)

    width = LEFT_PAD + n_weeks * (CELL + GAP) + 220  # extra room for legend/footer
    height = TOP_PAD + 7 * (CELL + GAP) + BOTTOM_PAD

    svg_parts = []
    svg_parts.append(
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Menlo, Consolas, monospace">'
    )
    svg_parts.append(
        f'<rect width="{width}" height="{height}" fill="#0d1117" rx="8"/>'
    )

    svg_parts.append("<style>")
    svg_parts.append(".cell{opacity:0;}")
    delay_step = 0.012
    max_cells = n_weeks * 7
    for i in range(max_cells + 1):
        svg_parts.append(
            f".d{i}{{animation:reveal 0.35s ease-out forwards; animation-delay:{i*delay_step:.3f}s;}}"
        )
    svg_parts.append(
        "@keyframes reveal{0%{opacity:0; transform:translate(-6px,-6px);}"
        "100%{opacity:1; transform:translate(0,0);}}"
    )
    svg_parts.append("</style>")

    # day-of-week labels
    for wd, label in enumerate(DAY_LABELS):
        if label:
            y = TOP_PAD + wd * (CELL + GAP) + CELL - 2
            svg_parts.append(
                f'<text x="4" y="{y}" font-size="9" fill="#8b949e">{label}</text>'
            )

    # month labels
    for week_idx, label in month_labels(days, weeks):
        x = LEFT_PAD + week_idx * (CELL + GAP)
        svg_parts.append(
            f'<text x="{x}" y="{TOP_PAD - 10}" font-size="10" fill="#8b949e">{label}</text>'
        )

    # cells
    cell_i = 0
    for week_idx, wk in enumerate(weeks):
        for weekday in range(7):
            d = wk.get(weekday)
            x = LEFT_PAD + week_idx * (CELL + GAP)
            y = TOP_PAD + weekday * (CELL + GAP)
            level = d["level"] if d else 0
            level = max(0, min(level, len(PALETTE) - 1))
            color = PALETTE[level]
            title = f'{d["count"]} contributions on {d["date"]}' if d else ""
            svg_parts.append(
                f'<rect class="cell d{cell_i}" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                f'rx="2.5" fill="{color}"><title>{title}</title></rect>'
            )
            cell_i += 1

    # legend
    legend_x = LEFT_PAD + n_weeks * (CELL + GAP) + 20
    legend_y = TOP_PAD
    svg_parts.append(
        f'<text x="{legend_x}" y="{legend_y - 12}" font-size="9" fill="#8b949e">Less</text>'
    )
    for i, color in enumerate(PALETTE):
        svg_parts.append(
            f'<rect x="{legend_x + i*(CELL+2)}" y="{legend_y}" width="{CELL-2}" height="{CELL-2}" '
            f'rx="2" fill="{color}"/>'
        )
    svg_parts.append(
        f'<text x="{legend_x + len(PALETTE)*(CELL+2) + 4}" y="{legend_y + 9}" '
        f'font-size="9" fill="#8b949e">More</text>'
    )

    # footer stats
    total = stats.get("total_contributions", 0)
    streak = stats.get("longest_streak", 0)
    footer = f'{total} contributions in the last year - longest streak {streak} day{"s" if streak != 1 else ""}'
    svg_parts.append(
        f'<text x="{LEFT_PAD}" y="{height - 16}" font-size="11" fill="#c9d1d9">{footer}</text>'
    )

    svg_parts.append("</svg>")

    with open(OUT_PATH, "w") as f:
        f.write("\n".join(svg_parts))
    print(f"Wrote {OUT_PATH} ({width}x{height})")


if __name__ == "__main__":
    main()
