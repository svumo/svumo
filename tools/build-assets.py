"""Builds assets/*.svg for the svumo profile README.
Run: python -I C:\\wt\\build\\build.py
"""
import base64, io, re, os
from PIL import Image

ICONS = r"C:\wt\icons\node_modules"
DL = r"C:\wt\dl"
OUT = r"C:\wt\svumo\assets"
os.makedirs(OUT, exist_ok=True)

FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'JetBrains Mono',Menlo,Consolas,monospace"

BG1, BG2 = "#1f2937", "#0f172a"      # pfp slate
TEAL, TEAL_L = "#14b8a6", "#5eead4"  # pfp teal
VIOLET = "#a78bfa"
AMBER = "#fbbf24"
SKY = "#38bdf8"
INK, MUTED, DIM = "#f1f5f9", "#cbd5e1", "#94a3b8"


def si(slug, pkg="simple-icons"):
    txt = open(os.path.join(ICONS, pkg, "icons", slug + ".svg"), encoding="utf8").read()
    return re.search(r' d="([^"]+)"', txt).group(1)


def b64png(path, crop=None, size=None, fmt="PNG"):
    im = Image.open(path).convert("RGBA" if fmt == "PNG" else "RGB")
    if crop:
        im = im.crop(crop)
    if size:
        im = im.resize(size, Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, fmt, optimize=True, **({"quality": 85} if fmt == "JPEG" else {}))
    mime = "png" if fmt == "PNG" else "jpeg"
    return f"data:image/{mime};base64," + base64.b64encode(buf.getvalue()).decode()


# ---------- custom (non simple-icons) marks, each drawn into a 24x24 box ----------
def mark_crowdstrike(c):
    return (f'<g transform="translate(-0.5 -2.2) scale(0.82)" fill="{c}">'
            '<path d="m29.82 31c-1.039-2.378-3.126-5.429-11.3-9.786-3.77-2.096-10.21-5.323-16-11.46 0.525 2.214 3.215 7.079 14.78 13.15 3.204 1.753 8.622 3.397 12.52 8.088"/>'
            '<path d="m29.3 26.93c-0.986-2.81-2.766-6.408-11.21-11.75-4.111-2.694-10.15-6.077-18.09-14.7 0.568 2.325 3.078 8.371 15.73 16.22 4.156 2.816 9.52 4.553 13.57 10.23"/>'
            '</g>')


def mark_osquery(c):
    txt = open(os.path.join(DL, "osquery-pin.svg"), encoding="utf8").read()
    paths = "".join(f'<path d="{d}"/>' for d in re.findall(r'<path d="([^"]+)"', txt, re.S))
    # potrace output: 700x700 box with its own transform
    return (f'<g transform="scale({24/700})"><g transform="translate(0,700) scale(0.1,-0.1)" fill="{c}">'
            f'{paths}</g></g>')


def mark_ida(_c):
    return ('<g transform="scale(0.55) translate(0 -1)">'
            '<defs><linearGradient id="idaA" x1="27.6" y1="23.4" x2="22.9" y2="23.1" gradientUnits="userSpaceOnUse"><stop stop-color="#fff"/><stop offset="1" stop-color="#B8B9BA"/></linearGradient></defs>'
            '<rect y="0.97" width="42.07" height="42.07" rx="12" fill="#2b2b2b" stroke="#4b5563" stroke-width="1"/>'
            '<path d="M34.436 23.8638L18.6842 33.2597L18.6842 14.4792L34.436 23.8638Z" fill="url(#idaA)"/>'
            '<path d="M7.63184 20.5682L21.905 10.7396L21.905 29.52L7.63184 20.5682Z" fill="#fff"/>'
            '<path d="M21.8989 29.5037L18.6845 33.2597L18.6845 27.5066L21.8989 29.5037Z" fill="#cfd2d6"/>'
            '</g>')


NMAP_PNG = None


def mark_nmap(_c):
    global NMAP_PNG
    if NMAP_PNG is None:
        NMAP_PNG = b64png(os.path.join(DL, "nmap-site.png"), crop=(18, 2, 150, 66), size=(132, 64))
    return (f'<defs><clipPath id="nmc"><rect x="-5" y="1" width="34" height="22" rx="6"/></clipPath></defs>'
            f'<image href="{NMAP_PNG}" x="-5" y="1" width="34" height="22" clip-path="url(#nmc)" preserveAspectRatio="xMidYMid slice"/>')


# ---------- stack definition ----------
def S(label, slug, color, pkg="simple-icons"):
    return (label, ("si", slug, pkg), color)


def C(label, fn, color):
    return (label, ("fn", fn, None), color)


SECTIONS = [
    ("Security", TEAL, [
        S("Metasploit", "metasploit", "#2596CD"),
        S("Burp Suite", "burpsuite", "#FF6633"),
        C("Nmap", mark_nmap, "#38bdf8"),
        S("Wireshark", "wireshark", "#3CA0E0"),
        S("Kali Linux", "kalilinux", "#5B8DEF"),
        C("IDA Pro", mark_ida, "#e5e7eb"),
        S("ELK Stack", "elasticstack", "#00BFB3"),
        C("CrowdStrike", mark_crowdstrike, "#FF3B3B"),
        C("osquery", mark_osquery, "#A596FF"),
    ]),
    ("Cloud &amp; Identity", VIOLET, [
        S("AWS", "amazonaws", "#FF9900", "si10"),
        S("Google Cloud", "googlecloud", "#4285F4"),
        S("Azure", "microsoftazure", "#2F9BF0", "si10"),
        S("Okta", "okta", "#2E9BEF", "si10"),
        S("Workspace", "google", "#34A853"),
    ]),
    ("Languages &amp; Tooling", AMBER, [
        S("Python", "python", "#FFD43B"),
        S("JavaScript", "javascript", "#F7DF1E"),
        S("TypeScript", "typescript", "#4A90E2"),
        S("C", "c", "#A8B9CC"),
        S("Bash", "gnubash", "#4EAA25"),
        S("Git", "git", "#F05032"),
        S("Docker", "docker", "#2496ED"),
        S("Linux", "linux", "#FCC624"),
        S("VS Code", "visualstudiocode", "#23A8F2", "si10"),
        S("Claude", "claude", "#D97757"),
    ]),
    ("Web &amp; Data", SKY, [
        S("Next.js", "nextdotjs", INK),
        S("React", "react", "#61DAFB"),
        S("Node.js", "nodedotjs", "#5FA04E"),
        S("Tailwind", "tailwindcss", "#06B6D4"),
        S("MongoDB", "mongodb", "#47A248"),
        S("PostgreSQL", "postgresql", "#6B8CEF"),
        S("MySQL", "mysql", "#F29111"),
        S("Redis", "redis", "#FF4438"),
    ]),
]


def stack_svg():
    W = 1000
    TW, TH, GAP = 84, 86, 8
    PAD = 40
    y = 34
    body = []
    defs = []
    n = 0
    for title, accent, items in SECTIONS:
        # section header
        body.append(f'<circle cx="{PAD + 5}" cy="{y + 7}" r="5" fill="{accent}"/>')
        body.append(f'<text x="{PAD + 18}" y="{y + 12}" font-size="14" font-weight="700" letter-spacing="1.6" fill="{accent}">{title.upper().replace("&AMP;","&amp;")}</text>')
        tw = len(title.replace('&amp;','&')) * 10.4 + 30
        body.append(f'<line x1="{PAD + 18 + tw}" y1="{y + 7}" x2="{W - PAD}" y2="{y + 7}" stroke="{accent}" stroke-opacity=".22"/>')
        y += 30
        row_w = len(items) * TW + (len(items) - 1) * GAP
        x0 = PAD
        for i, (label, (kind, ref, pkg), color) in enumerate(items):
            x = x0 + i * (TW + GAP)
            gid = f"g{n}"
            defs.append(f'<radialGradient id="{gid}" cx=".5" cy=".38" r=".62"><stop offset="0" stop-color="{color}" stop-opacity=".30"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>')
            if kind == "si":
                mark = f'<path d="{si(ref, pkg)}" fill="{color}"/>'
            else:
                mark = ref(color)
            delay = n * 0.035
            body.append(
                f'<g class="t" style="animation-delay:{delay:.3f}s" transform="translate({x} {y})">'
                f'<rect width="{TW}" height="{TH}" rx="16" fill="#ffffff" fill-opacity=".035" stroke="{color}" stroke-opacity=".28"/>'
                f'<rect width="{TW}" height="{TH}" rx="16" fill="url(#{gid})"/>'
                f'<g transform="translate({TW/2 - 17} 14) scale({34/24})">{mark}</g>'
                f'<text x="{TW/2}" y="{TH - 13}" text-anchor="middle" font-size="11.5" fill="{MUTED}">{label}</text>'
                f'</g>')
            n += 1
        y += TH + 30
    H = y - 6
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Tools I use: security, cloud and identity, languages and tooling, web and data" font-family="{FONT}">
<style>
</style>
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG1}"/><stop offset="1" stop-color="{BG2}"/></linearGradient>
<linearGradient id="edge" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{TEAL}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{AMBER}"/></linearGradient>
{"".join(defs)}
</defs>
<rect width="{W}" height="{H}" rx="24" fill="url(#bg)"/>
<rect x="40" y="0" width="{W - 80}" height="3" rx="1.5" fill="url(#edge)" opacity=".9"/>
{"".join(body)}
</svg>
'''


def banner_svg():
    W, H = 1200, 320
    lines = [
        ("$", "whoami", TEAL_L),
        (">", "cybersecurity · offense + defense", MUTED),
        (">", "identity &amp; access management", MUTED),
        (">", "full-stack when a project needs it", MUTED),
        ("$", "status", TEAL_L),
    ]
    term = []
    ty = 128
    for i, (p, t, c) in enumerate(lines):
        pc = TEAL if p == "$" else VIOLET
        term.append(f'<g class="l" style="animation-delay:{0.25 + i * 0.22:.2f}s"><text x="676" y="{ty}" font-family="{MONO}" font-size="17"><tspan fill="{pc}">{p}</tspan><tspan dx="10" fill="{c}">{t}</tspan></text></g>')
        ty += 29
    ty_last = ty
    term.append(f'<g class="l" style="animation-delay:{0.25 + 5 * 0.22:.2f}s"><text x="676" y="{ty_last}" font-family="{MONO}" font-size="17"><tspan fill="{VIOLET}">&gt;</tspan><tspan dx="10" fill="{AMBER}">still learning</tspan></text>'
                f'<rect class="cur" x="{676 + 10.2 + 10 + 15 * 10.2:.1f}" y="{ty_last - 15}" width="10" height="19" rx="2" fill="{TEAL_L}"/></g>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="svumo (Daniel). Cybersecurity, offensive and defensive, identity and access management, and full-stack builds. Still learning." font-family="{FONT}">
<style>
.cur{{animation:blink 1.1s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
.orb{{animation:drift 14s ease-in-out infinite alternate}}
@keyframes drift{{to{{transform:translate(40px,-18px)}}}}
@media (prefers-reduced-motion:reduce){{.l,.cur,.orb{{animation:none}}}}
</style>
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG1}"/><stop offset="1" stop-color="{BG2}"/></linearGradient>
<radialGradient id="o1"><stop offset="0" stop-color="{TEAL}" stop-opacity=".45"/><stop offset="1" stop-color="{TEAL}" stop-opacity="0"/></radialGradient>
<radialGradient id="o2"><stop offset="0" stop-color="#7c3aed" stop-opacity=".38"/><stop offset="1" stop-color="#7c3aed" stop-opacity="0"/></radialGradient>
<radialGradient id="o3"><stop offset="0" stop-color="{AMBER}" stop-opacity=".16"/><stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></radialGradient>
<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.1" fill="#ffffff" fill-opacity=".06"/></pattern>
<linearGradient id="edge" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{TEAL}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{AMBER}"/></linearGradient>
<clipPath id="card"><rect width="{W}" height="{H}" rx="28"/></clipPath>
</defs>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<rect width="{W}" height="{H}" fill="url(#dots)"/>
<circle class="orb" cx="170" cy="250" r="260" fill="url(#o1)"/>
<circle class="orb" cx="1080" cy="40" r="300" fill="url(#o2)" style="animation-direction:alternate-reverse"/>
<circle cx="640" cy="330" r="220" fill="url(#o3)"/>
<rect x="0" y="{H - 4}" width="{W}" height="4" fill="url(#edge)"/>
</g>
<text x="76" y="178" font-size="112" font-weight="800" letter-spacing="-4" fill="{INK}"><tspan fill="{TEAL}">s</tspan>vumo</text>
<text x="80" y="226" font-size="26" fill="{MUTED}">Daniel · security · identity · builds things</text>
<g transform="translate(80 252)" font-size="15" font-weight="600">
<rect width="126" height="30" rx="15" fill="{TEAL}" fill-opacity=".14" stroke="{TEAL}" stroke-opacity=".5"/><text x="63" y="20" text-anchor="middle" fill="{TEAL_L}">offense</text>
<rect x="136" width="126" height="30" rx="15" fill="#7c3aed" fill-opacity=".16" stroke="{VIOLET}" stroke-opacity=".5"/><text x="199" y="20" text-anchor="middle" fill="{VIOLET}">defense</text>
<rect x="272" width="126" height="30" rx="15" fill="{AMBER}" fill-opacity=".10" stroke="{AMBER}" stroke-opacity=".45"/><text x="335" y="20" text-anchor="middle" fill="{AMBER}">identity</text>
</g>
<g>
<rect x="652" y="44" width="500" height="240" rx="16" fill="#0b1220" fill-opacity=".78" stroke="#ffffff" stroke-opacity=".08"/>
<circle cx="676" cy="68" r="6" fill="#ff5f57"/><circle cx="696" cy="68" r="6" fill="#febc2e"/><circle cx="716" cy="68" r="6" fill="#28c840"/>
<text x="1128" y="73" text-anchor="end" font-family="{MONO}" font-size="13" fill="{DIM}">~/svumo</text>
<line x1="652" y1="88" x2="1152" y2="88" stroke="#ffffff" stroke-opacity=".06"/>
{"".join(term)}
</g>
</svg>
'''


def feature_svg(title, desc_lines, lang, lang_color, tags, icon, accent):
    W, H = 600, 190
    tag_svg = []
    tx = 136
    for t, c in tags:
        w = len(t) * 7.6 + 22
        tag_svg.append(f'<rect x="{tx}" y="138" width="{w:.0f}" height="24" rx="12" fill="{c}" fill-opacity=".14" stroke="{c}" stroke-opacity=".45"/>'
                       f'<text x="{tx + w/2:.0f}" y="154.5" text-anchor="middle" font-size="12.5" font-weight="600" fill="{c}">{t}</text>')
        tx += w + 8
    desc = "".join(f'<text x="136" y="{86 + i * 22}" font-size="16.5" fill="{MUTED}">{d}</text>' for i, d in enumerate(desc_lines))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{title}: {' '.join(desc_lines)}" font-family="{FONT}">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG1}"/><stop offset="1" stop-color="{BG2}"/></linearGradient>
<radialGradient id="glow" cx="0" cy="0" r="1"><stop offset="0" stop-color="{accent}" stop-opacity=".30"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
<clipPath id="c"><rect width="{W}" height="{H}" rx="20"/></clipPath>
<clipPath id="ic"><rect x="28" y="28" width="84" height="84" rx="20"/></clipPath>
</defs>
<g clip-path="url(#c)">
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<circle cx="70" cy="70" r="200" fill="url(#glow)"/>
<rect width="{W}" height="3" fill="{accent}"/>
</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="20" fill="none" stroke="{accent}" stroke-opacity=".3"/>
<g clip-path="url(#ic)">{icon}</g>
<text x="136" y="56" font-size="27" font-weight="700" letter-spacing="-.4" fill="{INK}">{title}</text>
<text x="{W - 28}" y="54" text-anchor="end" font-size="13.5" fill="{DIM}"><tspan fill="{lang_color}">●</tspan> {lang}</text>
{desc}
{"".join(tag_svg)}
</svg>
'''


def crosstalk_icon():
    txt = open(os.path.join(DL, "crosstalk-logo.svg"), encoding="utf8").read()
    inner = re.sub(r"^.*?<svg[^>]*>|</svg>\s*$", "", txt, flags=re.S)
    return f'<svg x="28" y="28" width="84" height="84" viewBox="0 0 512 512">{inner}</svg>'


def drunkdeer_icon():
    data = b64png(os.path.join(DL, "dd-logo.png"), crop=(150, 30, 874, 754), size=(168, 168), fmt="JPEG")
    return f'<image href="{data}" x="28" y="28" width="84" height="84"/>'


if __name__ == "__main__":
    files = {
        "banner.svg": banner_svg(),
        "stack.svg": stack_svg(),
        "crosstalk.svg": feature_svg(
            "claude-crosstalk",
            ["Let your Claude Code sessions talk to each other,", "across Claude accounts and other AI providers."],
            "JavaScript", "#F7DF1E",
            [("Claude Code plugin", TEAL_L), ("MCP", VIOLET), ("multi-agent", AMBER)],
            crosstalk_icon(), TEAL),
        "drunkdeer.svg": feature_svg(
            "DrunkDeer Control",
            ["Profile manager and per-key actuation tuning", "for DrunkDeer mechanical keyboards."],
            "C#", "#9B6BFF",
            [(".NET 8", VIOLET), ("Windows", SKY), ("HID", TEAL_L)],
            drunkdeer_icon(), VIOLET),
    }
    for name, svg in files.items():
        with open(os.path.join(OUT, name), "w", encoding="utf8", newline="\n") as f:
            f.write(svg)
        print(name, len(svg))
