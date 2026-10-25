"""Generate the blue/midnight editorial graphics used by the profile README."""
from __future__ import annotations

from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
STATIC = False


def svg_start(width: int, height: int, title: str, desc: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(title)}</title>',
        f'<desc id="desc">{escape(desc)}</desc>',
    ]


def section_svg(number: str, title: str, subtitle: str, accent: str) -> str:
    p = svg_start(1200, 106, f"{number} {title}", subtitle)
    p += [
        '<defs><linearGradient id="bg" x1="0" x2="1"><stop stop-color="#071326"/><stop offset=".7" stop-color="#0c1c32"/><stop offset="1" stop-color="#10294a"/></linearGradient><linearGradient id="glow"><stop stop-color="' + accent + '"/><stop offset="1" stop-color="#38bdf8"/></linearGradient></defs>',
        '<rect width="1200" height="106" rx="16" fill="url(#bg)"/><path d="M0 105H1200" stroke="#21344d"/>',
        f'<rect x="28" y="26" width="4" height="54" rx="2" fill="url(#glow)"/>',
        f'<text x="54" y="43" fill="{accent}" font-family="Segoe UI,Arial,sans-serif" font-size="13" font-weight="700" letter-spacing="3">{number} / PROFILE</text>',
        f'<text x="54" y="72" fill="#edf5ff" font-family="Segoe UI,Arial,sans-serif" font-size="26" font-weight="700">{escape(title)}</text>',
        f'<text x="1168" y="65" text-anchor="end" fill="#8da6c4" font-family="Segoe UI,Arial,sans-serif" font-size="13">{escape(subtitle)}</text>',
        f'<path d="M1040 0L1200 0 1200 106 1116 106z" fill="{accent}" opacity=".055"/>',
        '</svg>',
    ]
    return "\n".join(p)


def about_svg() -> str:
    p = svg_start(1200, 266, "About Shivam Singh", "AI-assisted web developer, computer science engineering student specializing in AI and machine learning, and digital creator.")
    p += [
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#071326"/><stop offset="1" stop-color="#0d2440"/></linearGradient><linearGradient id="line"><stop stop-color="#38bdf8"/><stop offset="1" stop-color="#2563eb"/></linearGradient></defs>',
        '<rect width="1200" height="266" rx="18" fill="url(#bg)"/><rect x="1" y="1" width="1198" height="264" rx="17" fill="none" stroke="#203854"/>',
        '<circle cx="1082" cy="132" r="105" fill="#0ea5e9" opacity=".08"/><circle cx="1082" cy="132" r="74" fill="none" stroke="#38bdf8" stroke-opacity=".27"/><circle cx="1082" cy="132" r="48" fill="none" stroke="#38bdf8" stroke-opacity=".25"/>',
        '<path d="M1020 150l34-36 27 21 53-61" fill="none" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><circle cx="1134" cy="74" r="5" fill="#7dd3fc"/>',
        '<text x="42" y="49" fill="#7dd3fc" font-family="Segoe UI,Arial,sans-serif" font-size="14" font-weight="700" letter-spacing="2">CURIOUS BY DEFAULT · BUILDING WITH INTENT</text>',
        '<text x="42" y="94" fill="#f1f7ff" font-family="Segoe UI,Arial,sans-serif" font-size="30" font-weight="700">I turn ideas into useful web experiences.</text>',
        '<text x="42" y="132" fill="#b7c7db" font-family="Segoe UI,Arial,sans-serif" font-size="16">I’m Shivam — a Computer Science Engineering student focused on AI &amp; ML,</text>',
        '<text x="42" y="158" fill="#b7c7db" font-family="Segoe UI,Arial,sans-serif" font-size="16">building through frontend development, practical analytics, and AI-assisted workflows.</text>',
        '<text x="42" y="184" fill="#b7c7db" font-family="Segoe UI,Arial,sans-serif" font-size="16">Outside the code, I work across e-commerce operations and technology content.</text>',
        '<rect x="42" y="211" width="208" height="32" rx="16" fill="#102e4f" stroke="#22527d"/><text x="146" y="232" text-anchor="middle" fill="#bfe8ff" font-family="Segoe UI,Arial,sans-serif" font-size="12" font-weight="600">B.TECH · EXPECTED 2027</text>',
        '<rect x="262" y="211" width="178" height="32" rx="16" fill="#102e4f" stroke="#22527d"/><text x="351" y="232" text-anchor="middle" fill="#bfe8ff" font-family="Segoe UI,Arial,sans-serif" font-size="12" font-weight="600">AI &amp; MACHINE LEARNING</text>',
        '<rect x="452" y="211" width="166" height="32" rx="16" fill="#102e4f" stroke="#22527d"/><text x="535" y="232" text-anchor="middle" fill="#bfe8ff" font-family="Segoe UI,Arial,sans-serif" font-size="12" font-weight="600">WEB · DIGITAL · DATA</text>',
        '</svg>',
    ]
    return "\n".join(p)


PROJECTS = [
    ("elementraui", "ELEMENTRAUI", "Discover UI resources built for the next interface.", "Open-source discovery platform for components, themes, templates, tools, icons, and motion.", "React  ·  UI discovery  ·  Open source", "#38bdf8", "https://elementra-ui-website.vercel.app", "ElementraUI open-source UI resource discovery platform"),
    ("tz-roms", "TZ ROMS", "A clearer home for Android ROM discovery.", "Multi-device ROM discovery hub, including a dedicated Poco X6 Pro portal.", "Android  ·  ROM discovery  ·  Product", "#818cf8", "https://tzroms.tzlabs.in", "TZ ROMs Android ROM discovery hub"),
    ("physifer", "PHYSIFER 2.0", "Learning resources with a digital-first presence.", "Education project and channel website; I also manage social content and edit videos for PHYSIFER.", "Education  ·  Web  ·  Content", "#22d3ee", "https://physifer2-o.vercel.app", "PHYSIFER 2.0 education website and creator work"),
    ("tzlabs", "TZ LABS", "Technology, tools, and experiments under one roof.", "A technology studio website for the TZ Labs ecosystem.", "Technology  ·  Studio  ·  Web", "#60a5fa", "https://tzlabs.in", "TZ Labs technology studio website"),
    ("prayanone", "PRAYANONE", "Railway information, shaped into a web experience.", "A railway information web project designed to make trip research easier to navigate.", "Travel  ·  Information  ·  Web", "#34d399", "https://prayanone.vercel.app", "PrayanOne railway information web project"),
    ("greenera", "GREENERA ORGANICS", "E-commerce and social operations for an organic brand.", "Freelance social and e-commerce management, plus customization of the Vercel-hosted business site.", "E-commerce  ·  Social  ·  Site customization", "#a3e635", "https://greeneraorganics.vercel.app", "Greenera Organics freelance and customized site"),
    ("apnabazaar", "APNABAZAAR", "A marketplace concept brought to the web.", "An independent web project in Shivam’s product and frontend portfolio.", "Marketplace  ·  Frontend  ·  Web", "#fb923c", "https://apna-bazaar-three.vercel.app", "ApnaBazaar web project"),
]


def project_svg(project: tuple[str, str, str, str, str, str, str, str]) -> str:
    slug, name, tagline, detail, tags, accent, _url, accessible = project
    p = svg_start(1200, 214, name.title(), accessible)
    p += [
        f'<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#091526"/><stop offset="1" stop-color="#0e2035"/></linearGradient><linearGradient id="{slug}-accent"><stop stop-color="{accent}"/><stop offset="1" stop-color="#2563eb"/></linearGradient></defs>',
        '<rect width="1200" height="214" rx="18" fill="url(#bg)"/><rect x="1" y="1" width="1198" height="212" rx="17" fill="none" stroke="#203854"/>',
        f'<rect x="0" y="0" width="8" height="214" rx="4" fill="url(#{slug}-accent)"/>',
        f'<circle cx="1090" cy="106" r="72" fill="{accent}" opacity=".07"/><circle cx="1090" cy="106" r="49" fill="none" stroke="{accent}" stroke-opacity=".25"/><path d="M1060 113h20l13-25 18 41 15-24h18" fill="none" stroke="{accent}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>',
        f'<text x="38" y="41" fill="{accent}" font-family="Segoe UI,Arial,sans-serif" font-size="12" font-weight="700" letter-spacing="2">SELECTED PROJECT  /  {name}</text>',
        f'<text x="38" y="82" fill="#f1f7ff" font-family="Segoe UI,Arial,sans-serif" font-size="25" font-weight="700">{escape(tagline)}</text>',
        f'<text x="38" y="116" fill="#b7c7db" font-family="Segoe UI,Arial,sans-serif" font-size="15">{escape(detail)}</text>',
        f'<text x="38" y="163" fill="#8fa9c6" font-family="Segoe UI,Arial,sans-serif" font-size="13">{escape(tags)}</text>',
        f'<text x="38" y="192" fill="{accent}" font-family="Segoe UI,Arial,sans-serif" font-size="12" font-weight="700">OPEN PROJECT  ↗</text>',
        '</svg>',
    ]
    return "\n".join(p)


def skills_svg() -> str:
    p = svg_start(1200, 368, "Shivam Singh toolkit", "Skills and tools across frontend development, data analytics, AI-assisted workflows, digital operations, and creative production.")
    p += ['<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#071326"/><stop offset="1" stop-color="#0d2440"/></linearGradient></defs>', '<rect width="1200" height="368" rx="18" fill="url(#bg)"/><rect x="1" y="1" width="1198" height="366" rx="17" fill="none" stroke="#203854"/>']
    groups = [
        ("01", "WEB & PRODUCT", ["HTML / CSS", "TypeScript", "React", "Vite", "Tailwind CSS", "WordPress", "Git · GitHub · Vercel"], "#38bdf8"),
        ("02", "DATA & ANALYTICS", ["SQL", "Excel", "Google Sheets", "Data cleaning", "Dashboards", "Reporting"], "#34d399"),
        ("03", "AI-ASSISTED WORK", ["ChatGPT", "Claude", "Gemini", "Cursor", "Prompt engineering"], "#a78bfa"),
        ("04", "DIGITAL OPERATIONS", ["SEO", "Search Console", "E-commerce", "Amazon listings"], "#fbbf24"),
        ("05", "CREATIVE", ["Canva", "Graphic design", "Video editing", "Wondershare Filmora"], "#fb7185"),
    ]
    for i, (number, label, items, color) in enumerate(groups):
        x = 28 + i * 232
        p.append(f'<rect x="{x}" y="28" width="212" height="312" rx="14" fill="#0a1728" stroke="#203854"/>')
        p.append(f'<text x="{x+18}" y="61" fill="{color}" font-family="Segoe UI,Arial,sans-serif" font-size="12" font-weight="700" letter-spacing="1">{number} / TOOLKIT</text>')
        p.append(f'<text x="{x+18}" y="91" fill="#eaf3ff" font-family="Segoe UI,Arial,sans-serif" font-size="14" font-weight="700">{escape(label)}</text>')
        p.append(f'<path d="M{x+18} 108h176" stroke="{color}" stroke-opacity=".45"/>')
        for j, item in enumerate(items):
            y = 140 + j * 27
            p.append(f'<circle cx="{x+23}" cy="{y-4}" r="3" fill="{color}"/>')
            p.append(f'<text x="{x+35}" y="{y}" fill="#b7c7db" font-family="Segoe UI,Arial,sans-serif" font-size="12">{escape(item)}</text>')
    p.append('</svg>')
    return "\n".join(p)


def journey_svg() -> str:
    p = svg_start(1200, 250, "Digital work and experience", "Freelance projects and creator work documented in Shivam Singh's portfolio information report.")
    p += ['<defs><linearGradient id="bg" x1="0" x2="1"><stop stop-color="#071326"/><stop offset="1" stop-color="#0d2440"/></linearGradient></defs>', '<rect width="1200" height="250" rx="18" fill="url(#bg)"/><rect x="1" y="1" width="1198" height="248" rx="17" fill="none" stroke="#203854"/>', '<path d="M72 58H1125" stroke="#284664" stroke-width="2"/>']
    entries = [
        ("2020—2024", "FIVERR", "Freelance graphic design\nand video editing", "#818cf8"),
        ("JAN 2026—NOW", "PHYSIFER", "Social content management\nand video editing", "#22d3ee"),
        ("MAY—SEP 2026", "GREENERA ORGANICS", "Social + e-commerce\nsite customization", "#a3e635"),
    ]
    for i, (date, name, desc, color) in enumerate(entries):
        x = 74 + i * 370
        p.append(f'<circle cx="{x}" cy="58" r="8" fill="{color}"/><circle cx="{x}" cy="58" r="15" fill="none" stroke="{color}" stroke-opacity=".25"/>')
        p.append(f'<text x="{x}" y="96" fill="{color}" font-family="Segoe UI,Arial,sans-serif" font-size="12" font-weight="700" letter-spacing="1">{escape(date)}</text>')
        p.append(f'<text x="{x}" y="126" fill="#edf5ff" font-family="Segoe UI,Arial,sans-serif" font-size="19" font-weight="700">{escape(name)}</text>')
        for j, line in enumerate(desc.split("\n")):
            p.append(f'<text x="{x}" y="158" dy="{j*22}" fill="#aebfd4" font-family="Segoe UI,Arial,sans-serif" font-size="14">{escape(line)}</text>')
    p.append('<text x="74" y="221" fill="#647e9c" font-family="Segoe UI,Arial,sans-serif" font-size="12">Freelance and creator work · details and dates kept to the supplied portfolio report</text>')
    p.append('</svg>')
    return "\n".join(p)


def footer_svg() -> str:
    p = svg_start(1200, 156, "Build with curiosity, ship with purpose", "Connect with Shivam Singh through his portfolio, LinkedIn, Instagram, YouTube, or email.")
    p += ['<defs><linearGradient id="bg" x1="0" x2="1"><stop stop-color="#071326"/><stop offset="1" stop-color="#0e2440"/></linearGradient><linearGradient id="line"><stop stop-color="#38bdf8"/><stop offset="1" stop-color="#2563eb"/></linearGradient></defs>', '<rect width="1200" height="156" rx="18" fill="url(#bg)"/><rect x="1" y="1" width="1198" height="154" rx="17" fill="none" stroke="#203854"/>', '<text x="38" y="53" fill="#7dd3fc" font-family="Segoe UI,Arial,sans-serif" font-size="12" font-weight="700" letter-spacing="2">HAVE A GOOD PROBLEM TO SOLVE?</text>', '<text x="38" y="91" fill="#f1f7ff" font-family="Segoe UI,Arial,sans-serif" font-size="27" font-weight="700">Let’s build something useful.</text>', '<text x="38" y="122" fill="#9db2ca" font-family="Segoe UI,Arial,sans-serif" font-size="14">Web development · freelance projects · technology content</text>', '<path d="M850 0l350 0v156H990z" fill="#38bdf8" opacity=".05"/><path d="M884 86h255" stroke="url(#line)" stroke-width="2"/><circle cx="1139" cy="86" r="5" fill="#7dd3fc"/>', '<text x="1170" y="124" text-anchor="end" fill="#647e9c" font-family="monospace" font-size="12">TECHNOEZMOBILE  /  2026</text>', '</svg>']
    return "\n".join(p)


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    for number, title, subtitle, accent in [
        ("01", "A little about me", "Curiosity, craft, and practical problem-solving", "#38bdf8"),
        ("02", "Selected work", "A few things I’ve been building and supporting", "#818cf8"),
        ("03", "Digital work", "Freelance and creator experience", "#34d399"),
        ("04", "The toolkit", "Tools I use to make, measure, and improve", "#fbbf24"),
        ("05", "Find me around the web", "Open to thoughtful conversations and collaboration", "#22d3ee"),
    ]:
        (ASSETS / f"section-{number}.svg").write_text(section_svg(number, title, subtitle, accent) + "\n", encoding="utf-8")
    (ASSETS / "about-card.svg").write_text(about_svg() + "\n", encoding="utf-8")
    for project in PROJECTS:
        (ASSETS / f"project-{project[0]}.svg").write_text(project_svg(project) + "\n", encoding="utf-8")
    (ASSETS / "toolkit.svg").write_text(skills_svg() + "\n", encoding="utf-8")
    (ASSETS / "journey.svg").write_text(journey_svg() + "\n", encoding="utf-8")
    (ASSETS / "footer.svg").write_text(footer_svg() + "\n", encoding="utf-8")
    print("Generated 16 editorial profile SVG assets")


if __name__ == "__main__":
    main()

