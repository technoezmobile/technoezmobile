"""Generate the animated ASCII portrait and terminal info card for the profile README."""
from __future__ import annotations

import os
import re
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageEnhance, ImageOps

ROOT = Path(__file__).resolve().parents[1]
PHOTO = ROOT / "assets" / "Studio Portrait with Folded Arms.png"
OUT = ROOT / "assets"
STATIC = os.environ.get("STATIC") == "1"


def ascii_svg() -> str:
    image = Image.open(PHOTO).convert("RGB")
    width, height = image.size
    # The original image is square. A wide portrait crop keeps the face and folded arms
    # readable in the terminal column while reducing most of the blue studio backdrop.
    crop_h = min(height, int(width / 1.43))
    top = max(0, min(height - crop_h, int(height * 0.08)))
    image = image.crop((0, top, width, top + crop_h)).resize((96, 40), Image.Resampling.LANCZOS)
    pixels = image.load()
    gray = Image.new("L", image.size)
    gp = gray.load()
    for y in range(image.height):
        for x in range(image.width):
            r, g, b = pixels[x, y]
            is_blue_backdrop = b > 105 and b > r * 1.22 and b > g * 1.08
            gp[x, y] = 255 if is_blue_backdrop else int(0.299 * r + 0.587 * g + 0.114 * b)
    gray = ImageEnhance.Contrast(ImageOps.autocontrast(gray, cutoff=1)).enhance(1.45)
    ramp = " .,:;irsXA253hMHGS#9B&@"
    rows: list[str] = []
    for y in range(gray.height):
        line = "".join(ramp[min(len(ramp) - 1, (255 - gray.getpixel((x, y))) * (len(ramp) - 1) // 255)] for x in range(gray.width))
        rows.append(line)

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="620" height="500" viewBox="0 0 620 500" role="img" aria-labelledby="title desc">',
        '<title id="title">Animated ASCII portrait of Shivam Singh</title>',
        '<desc id="desc">A monochrome portrait types itself line by line in a terminal window.</desc>',
        '<rect width="800" height="500" rx="16" fill="#080d16"/>',
        '<rect x="1" y="1" width="798" height="498" rx="15" fill="none" stroke="#263449"/>',
        '<circle cx="24" cy="23" r="5" fill="#fb7185"/><circle cx="43" cy="23" r="5" fill="#fbbf24"/><circle cx="62" cy="23" r="5" fill="#34d399"/>',
        '<text x="310" y="27" text-anchor="middle" fill="#8493a9" font-family="monospace" font-size="12">shivam@github: ~/profile</text>',
        '<text x="24" y="57" fill="#60a5fa" font-family="monospace" font-size="14">$ whoami</text>',
        '<text x="24" y="78" fill="#e2e8f0" font-family="monospace" font-size="13">Shivam Singh</text>',
    ]
    y0, line_h, x0, char_w = 101, 9.2, 18, 8.0
    reveal = 0.025
    for row, text in enumerate(rows):
        y = y0 + row * line_h
        delay = 0 if STATIC else row * reveal
        duration = 0 if STATIC else 0.32
        parts.append(f'<clipPath id="line{row}" clipPathUnits="userSpaceOnUse"><rect x="{x0}" y="{y - 8:.2f}" width="0" height="10"><animate attributeName="width" from="0" to="{len(text) * char_w:.0f}" dur="{duration}s" begin="{delay:.3f}s" fill="freeze"/></rect></clipPath>')
        parts.append(f'<text x="{x0}" y="{y:.2f}" clip-path="url(#line{row})" xml:space="preserve" fill="#d9e4f4" font-family="Consolas,monospace" font-size="9.2">{escape(text)}</text>')
    parts.extend([
        '<text x="24" y="489" fill="#52647d" font-family="monospace" font-size="11">BUILD  ·  LEARN  ·  SHIP</text>',
        '<text x="596" y="489" text-anchor="end" fill="#60a5fa" font-family="monospace" font-size="11">[ ready ]</text>',
        '</svg>',
    ])
    return "\n".join(parts)


def info_card_svg() -> str:
    rows = [
        ("NAME", "Shivam Singh"),
        ("ROLE", "AI-assisted Web Developer"),
        ("STUDY", "CSE · AI & ML · class of 2027"),
        ("FOCUS", "Web products · useful interfaces"),
        ("STACK", "React · TypeScript · Vite · SQL"),
        ("ALSO", "E-commerce · analytics · content"),
        ("OPEN", "Web development · freelance"),
    ]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="620" height="500" viewBox="0 0 620 500" role="img" aria-labelledby="title desc">',
        '<title id="title">Shivam Singh profile info card</title>',
        '<desc id="desc">A terminal-inspired animated profile card with verified role, study, focus, tools, and interests.</desc>',
        '<rect width="620" height="500" rx="16" fill="#080d16"/><rect x="1" y="1" width="618" height="498" rx="15" fill="none" stroke="#263449"/>',
        '<circle cx="24" cy="23" r="5" fill="#fb7185"/><circle cx="43" cy="23" r="5" fill="#fbbf24"/><circle cx="62" cy="23" r="5" fill="#34d399"/>',
        '<text x="310" y="27" text-anchor="middle" fill="#8493a9" font-family="monospace" font-size="12">shivam@github: ~</text>',
        '<text x="28" y="69" fill="#60a5fa" font-family="monospace" font-size="15">$ ./profile --summary</text>',
        '<text x="28" y="98" fill="#94a3b8" font-family="monospace" font-size="12">┌─ CURRENT PROFILE ───────────────────────────┐</text>',
    ]
    for index, (key, value) in enumerate(rows):
        y = 141 + index * 39
        delay = 0 if STATIC else 0.5 + index * 0.15
        duration = 0 if STATIC else 0.32
        parts.append(f'<g opacity="{1 if STATIC else 0}"><animate attributeName="opacity" from="0" to="1" dur="{duration}s" begin="{delay:.2f}s" fill="freeze"/><text x="40" y="{y}" fill="#34d399" font-family="monospace" font-size="12">{key:<7}</text><text x="132" y="{y}" fill="#d9e4f4" font-family="monospace" font-size="12">{escape(value)}</text></g>')
    parts.extend([
        '<text x="28" y="429" fill="#94a3b8" font-family="monospace" font-size="12">└──────────────────────────────────────────────┘</text>',
        '<text x="28" y="462" fill="#60a5fa" font-family="monospace" font-size="13">$ echo "curious by default; shipping by practice"</text>',
        '<text x="28" y="482" fill="#64748b" font-family="monospace" font-size="11">Education: AI &amp; ML · Expected graduation: 2027</text>',
        '</svg>',
    ])
    return "\n".join(parts)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    (OUT / "avatar-ascii.svg").write_text(ascii_svg() + "\n", encoding="utf-8")
    (OUT / "info-card.svg").write_text(info_card_svg() + "\n", encoding="utf-8")
    print("Generated avatar-ascii.svg and info-card.svg" + (" (static preview)" if STATIC else " (animated)"))


if __name__ == "__main__":
    main()

