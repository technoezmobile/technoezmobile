"""Refresh profile contribution JSON and SVG from GitHub's public calendar."""
from __future__ import annotations

import json
import re
import urllib.request
from datetime import date, timedelta
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
USERNAME = "technoezmobile"
URL = f"https://github.com/users/{USERNAME}/contributions"
PALETTE = ["#18212b", "#0c3b32", "#087b5b", "#12a875", "#6ee7b7"]


class CalendarParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.days: dict[str, dict[str, int]] = {}
        self.cell_dates: dict[str, str] = {}
        self.tooltip_date: str | None = None
        self.tooltip_text = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "td" and values.get("data-date"):
            day = values["data-date"]
            self.days[day] = {"count": 0, "level": int(values.get("data-level") or 0)}
            if values.get("id"):
                self.cell_dates[values["id"]] = day
        elif tag == "tool-tip" and values.get("for") in self.cell_dates:
            self.tooltip_date = self.cell_dates[values["for"]]
            self.tooltip_text = ""

    def handle_endtag(self, tag: str) -> None:
        if tag == "tool-tip" and self.tooltip_date:
            match = re.search(r"([\d,]+) contributions?", self.tooltip_text, re.I)
            if match:
                self.days[self.tooltip_date]["count"] = int(match.group(1).replace(",", ""))
            self.tooltip_date = None

    def handle_data(self, data: str) -> None:
        if self.tooltip_date:
            self.tooltip_text += data


def fetch_days() -> list[dict[str, int | str]]:
    request = urllib.request.Request(URL, headers={"User-Agent": "technoezmobile-profile/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        source = response.read().decode("utf-8")
    parser = CalendarParser()
    parser.feed(source)
    if len(parser.days) < 300:
        raise RuntimeError(f"Expected a full contribution calendar, found {len(parser.days)} days")
    return [{"date": key, **value} for key, value in sorted(parser.days.items())]


def render_svg(days: list[dict[str, int | str]]) -> str:
    levels = {str(day["date"]): int(day["level"]) for day in days}
    start = date.fromisoformat(str(days[0]["date"]))
    end = date.fromisoformat(str(days[-1]["date"]))
    grid_start = start - timedelta(days=(start.weekday() + 1) % 7)
    weeks = ((end - grid_start).days // 7) + 1
    cell, gap, left, top = 12, 4, 40, 34
    width, height = left + weeks * (cell + gap) + 8, top + 7 * (cell + gap) + 42
    total = sum(int(day["count"]) for day in days)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Shivam Singh’s GitHub contribution calendar</title>',
        f'<desc id="desc">A calendar showing {total:,} contributions from GitHub’s public contribution page over the last year. Calendar cells reveal in a subtle diagonal animation.</desc>',
        '<style>@keyframes reveal{from{opacity:0;transform:translateY(-5px)}to{opacity:1;transform:translateY(0)}}.wave{animation:reveal .4s ease-out both}@media(prefers-reduced-motion:reduce){.wave{animation:none;opacity:1}}</style>',
        f'<text x="{left}" y="18" fill="#e6f2ff" font-family="Segoe UI,Arial,sans-serif" font-size="13" font-weight="700">A YEAR OF BUILDING  <tspan fill="#647e9c" font-weight="400">/  {total:,} public contributions</tspan></text>',
        f'<path d="M{left} 25H{width-12}" stroke="#203854"/>',
    ]
    for label, weekday in (("Mon", 1), ("Wed", 3), ("Fri", 5)):
        y = top + weekday * (cell + gap) + 10
        parts.append(f'<text x="3" y="{y}" fill="#64748b" font-family="Segoe UI,Arial,sans-serif" font-size="10">{label}</text>')
    month_seen: set[tuple[int, int]] = set()
    paths: dict[int, dict[int, list[str]]] = {}
    max_wave = 0
    for offset in range((end - grid_start).days + 1):
        current = grid_start + timedelta(days=offset)
        col, row = offset // 7, (current.weekday() + 1) % 7
        x, y = left + col * (cell + gap), top + row * (cell + gap)
        level = min(4, levels.get(current.isoformat(), 0))
        wave = col + row
        max_wave = max(max_wave, wave)
        paths.setdefault(wave, {item: [] for item in range(len(PALETTE))})[level].append(f'M{x} {y}h{cell}v{cell}h-{cell}z')
        key = (current.year, current.month)
        if current.day == 1 and key not in month_seen:
            month_seen.add(key)
            parts.append(f'<text x="{x}" y="{top - 8}" fill="#64748b" font-family="Segoe UI,Arial,sans-serif" font-size="10">{current.strftime("%b")}</text>')
    parts.append('<style>' + ''.join(f'.w{wave}{{animation-delay:{wave * 0.018:.3f}s}}' for wave in range(max_wave + 1)) + '</style>')
    # Calendar cells are grouped by diagonal so a compact SVG can animate the real grid.
    for wave in sorted(paths):
        parts.append(f'<g class="wave w{wave}">')
        for level, commands in paths[wave].items():
            if commands:
                parts.append(f'<path fill="{PALETTE[level]}" d="{"".join(commands)}"/>')
        parts.append('</g>')
    legend_y = top + 7 * (cell + gap) + 18
    parts.append(f'<text x="{left}" y="{legend_y}" fill="#64748b" font-family="Segoe UI,Arial,sans-serif" font-size="10">Less</text>')
    for level, color in enumerate(PALETTE):
        x = left + 31 + level * (cell + gap)
        parts.append(f'<rect x="{x}" y="{legend_y - 10}" width="{cell}" height="{cell}" rx="3" fill="{color}"/>')
    parts.append(f'<text x="{left + 31 + len(PALETTE) * (cell + gap)}" y="{legend_y}" fill="#64748b" font-family="Segoe UI,Arial,sans-serif" font-size="10">More</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    days = fetch_days()
    payload = {
        "username": USERNAME,
        "days": [[day["date"], day["count"], day["level"]] for day in days],
        "total": sum(int(day["count"]) for day in days),
    }
    (ROOT / "data" / "contributions.json").write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")
    (ROOT / "assets" / "contributions.svg").write_text(render_svg(days) + "\n", encoding="utf-8")
    print(f"Updated {len(days)} days; total={payload['total']}")


if __name__ == "__main__":
    main()


