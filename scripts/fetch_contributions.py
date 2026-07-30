"""
fetch_contributions.py
Scrapes the public contribution calendar fragment GitHub serves at
https://github.com/users/<username>/contributions (no auth, no GraphQL token)
and writes data/contributions.json with raw days + derived stats.
"""
import json
import os
import sys
from datetime import date, datetime

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_USERNAME", "pateldarshil8")
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")

HEADERS = {"User-Agent": "Mozilla/5.0 (profile-readme-bot)"}


def fetch_days():
    resp = requests.get(URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    cells = soup.select("td.ContributionCalendar-day")
    if not cells:
        # newer markup uses <table> rows of <td> without the class in some cases;
        # fall back to any element carrying a data-date attribute
        cells = soup.select("[data-date]")

    days = []
    for cell in cells:
        d = cell.get("data-date")
        if not d:
            continue
        level = cell.get("data-level")
        if level is None:
            # derive from the ContributionCalendar-day--LEVEL class
            cls = cell.get("class", [])
            level = next(
                (c.split("--")[-1] for c in cls if c.startswith("ContributionCalendar-day--")),
                "0",
            )
        tooltip_id = cell.get("id")
        count = 0
        tooltip = soup.find(attrs={"for": tooltip_id}) if tooltip_id else None
        if tooltip:
            text = tooltip.get_text(strip=True)
            digits = "".join(ch for ch in text.split(" ")[0] if ch.isdigit())
            count = int(digits) if digits else (0 if "No contributions" in text else 0)
        days.append({"date": d, "level": int(level), "count": count})

    days.sort(key=lambda x: x["date"])
    return days


def derive_stats(days):
    if not days:
        return {}

    total = sum(d["count"] for d in days)

    # streaks
    current_streak = 0
    longest_streak = 0
    running = 0
    for d in days:
        if d["count"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0
    # current streak counts back from the most recent day
    for d in reversed(days):
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    best_day = max(days, key=lambda x: x["count"]) if days else None

    monthly = {}
    for d in days:
        month = d["date"][:7]
        monthly[month] = monthly.get(month, 0) + d["count"]

    return {
        "username": USERNAME,
        "total_contributions": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly_totals": monthly,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


def main():
    days = fetch_days()
    stats = derive_stats(days)
    payload = {"days": days, "stats": stats}

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(payload, f, indent=2)

    print(f"Wrote {len(days)} days -> {OUT_PATH}")
    if stats:
        print(f"Total contributions (last year): {stats['total_contributions']}")
        print(f"Current streak: {stats['current_streak']} | Longest streak: {stats['longest_streak']}")


if __name__ == "__main__":
    main()
