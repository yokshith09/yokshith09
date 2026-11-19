#!/usr/bin/env python3
"""Generate the animated racing-studio SVGs used by the profile README.

Run from the repo root:  python3 scripts/generate_assets.py
Output is deterministic, so re-running only changes what you edit here.
GitHub renders these as <img>, so all animation is SMIL inside the SVG.
"""
from __future__ import annotations

import math
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)

SANS = "'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif"
DISPLAY = "'Arial Black', 'Segoe UI Black', 'Helvetica Neue', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Fira Code', Consolas, 'Courier New', monospace"

ASPHALT, CARBON = "#0b0b0d", "#141519"
RED, YELLOW, CYAN, GREEN, PURPLE, WHITE = (
    "#ff1e1e", "#ffd200", "#00e5ff", "#00d26a", "#b14cff", "#f5f5f5")
TEXT, MUTED = "#e5e7eb", "#9ca3af"

# The track used by the hero: a hand-drawn closed circuit.
CIRCUIT = ("M 700 500 L 1000 500 C 1100 500 1130 440 1100 390 L 1040 300 "
           "C 1010 250 1060 210 1100 190 C 1150 160 1120 100 1060 100 L 820 100 "
           "C 760 100 740 140 770 180 L 830 260 C 860 300 830 340 780 340 L 700 340 "
           "C 640 340 630 380 650 420 C 660 450 650 500 700 500 Z")


def esc(s: str) -> str:
    return escape(s, {'"': "&quot;"})


# ---------------------------------------------------------------- shared bits
def svg_open(w: int, h: int, title: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">'
            f'<title>{esc(title)}</title>')


def base_defs(uid: str) -> str:
    return f'''
  <pattern id="{uid}-carbon" width="8" height="8" patternUnits="userSpaceOnUse">
    <rect width="8" height="8" fill="{ASPHALT}"/>
    <rect width="4" height="4" fill="{CARBON}"/><rect x="4" y="4" width="4" height="4" fill="{CARBON}"/>
  </pattern>
  <pattern id="{uid}-check" width="16" height="16" patternUnits="userSpaceOnUse">
    <rect width="16" height="16" fill="{WHITE}"/>
    <rect width="8" height="8" fill="#111"/><rect x="8" y="8" width="8" height="8" fill="#111"/>
  </pattern>
  <radialGradient id="{uid}-sheen" cx=".3" cy="0" r="1.1">
    <stop offset="0" stop-color="#ffffff" stop-opacity=".07"/>
    <stop offset=".6" stop-color="#000" stop-opacity="0"/>
    <stop offset="1" stop-color="#000" stop-opacity=".55"/>
  </radialGradient>
  <linearGradient id="{uid}-hot" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{RED}"/><stop offset=".55" stop-color="#ff6a00"/>
    <stop offset="1" stop-color="{YELLOW}"/>
  </linearGradient>
  <filter id="{uid}-glow" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="2.6" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>'''


def frame(uid: str, w: int, h: int, rx: int = 14) -> str:
    return (f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="{rx}" fill="url(#{uid}-carbon)"/>'
            f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="{rx}" fill="url(#{uid}-sheen)" '
            f'stroke="#2a2b31" stroke-width="2"/>')


def car(color: str, scale: float = 1.0) -> str:
    """Top-down open-wheel car pointing along +x, centred on the origin."""
    return f'''<g transform="scale({scale})">
  <rect x="-13" y="-8" width="5" height="4" rx="1" fill="#0a0a0a"/><rect x="-13" y="4" width="5" height="4" rx="1" fill="#0a0a0a"/>
  <rect x="5" y="-8" width="5" height="4" rx="1" fill="#0a0a0a"/><rect x="5" y="4" width="5" height="4" rx="1" fill="#0a0a0a"/>
  <rect x="-16" y="-6" width="3" height="12" fill="{color}"/>
  <path d="M -13 -3.5 L 6 -3 L 15 -1 L 15 1 L 6 3 L -13 3.5 Z" fill="{color}"/>
  <rect x="13" y="-6" width="2.5" height="12" fill="{color}"/>
  <ellipse cx="-1" cy="0" rx="3.2" ry="2" fill="#0a0a0a"/>
</g>'''


def kerb_path(d: str, width: int, extra: str = "") -> str:
    """Asphalt ribbon with red/white kerbs along both edges."""
    return (f'<path d="{d}" fill="none" stroke="{WHITE}" stroke-width="{width+8}" stroke-linejoin="round" {extra}/>'
            f'<path d="{d}" fill="none" stroke="{RED}" stroke-width="{width+8}" stroke-dasharray="12 12" '
            f'stroke-linejoin="round" {extra}/>'
            f'<path d="{d}" fill="none" stroke="#24252b" stroke-width="{width}" stroke-linejoin="round" {extra}/>')


def flag(x: float, y: float, uid: str, w: int = 90, h: int = 60, dur: float = 1.6) -> str:
    a = f"M0 0 C {w/3:.0f} -8, {2*w/3:.0f} 8, {w} 0 L {w} {h} C {2*w/3:.0f} {h+8}, {w/3:.0f} {h-8}, 0 {h} Z"
    b = f"M0 0 C {w/3:.0f} 8, {2*w/3:.0f} -8, {w} 0 L {w} {h} C {2*w/3:.0f} {h-8}, {w/3:.0f} {h+8}, 0 {h} Z"
    return f'''<g transform="translate({x} {y})">
  <rect x="-4" y="-6" width="4" height="{h+70}" rx="2" fill="#9ca3af"/>
  <path d="{a}" fill="url(#{uid}-check)" stroke="#000" stroke-opacity=".4">
    <animate attributeName="d" values="{a};{b};{a}" dur="{dur}s" repeatCount="indefinite"/></path>
</g>'''


def speed_lines(uid: str, x0: int, x1: int, ys: list[int], color: str = WHITE) -> str:
    out = []
    for i, y in enumerate(ys):
        ln = 80 + (i * 37) % 120
        dur = 0.9 + (i * 0.23) % 0.8
        out.append(f'<line x1="0" y1="{y}" x2="{ln}" y2="{y}" stroke="{color}" stroke-opacity=".35" '
                   f'stroke-width="{1 + i % 2}" stroke-linecap="round">'
                   f'<animateTransform attributeName="transform" type="translate" values="{x1} 0;{x0-ln} 0" '
                   f'dur="{dur:.2f}s" begin="{i*0.17:.2f}s" repeatCount="indefinite"/></line>')
    return "".join(out)


def write(name: str, body: str) -> None:
    (OUT / name).write_text(body + "</svg>\n", encoding="utf-8")
    print("wrote", OUT / name)


# ---------------------------------------------------------------- hero
TOWER = [  # position, label, colour, lap time in seconds for its car
    ("AI AGENTS", RED, 9.0),
    ("FULL STACK", CYAN, 9.6),
    ("COMPUTER VISION", YELLOW, 10.3),
    ("ROBOTICS · SLAM", GREEN, 11.1),
    ("RUST · DESKTOP", PURPLE, 11.8),
]


def hero() -> None:
    uid, W, H = "h", 1200, 640
    body = [svg_open(W, H, "Yokshith Kuchipudi — racing pit-wall dashboard with five cars, one per skill domain"),
            f"<defs>{base_defs(uid)}<clipPath id='{uid}-card'><rect x='1' y='1' width='{W-2}' "
            f"height='{H-2}' rx='14'/></clipPath></defs>", frame(uid, W, H),
            f'<g clip-path="url(#{uid}-card)">']

    # top broadcast bar
    body.append(f'''
<rect x="0" y="0" width="{W}" height="46" fill="#0a0a0a"/>
<rect x="0" y="44" width="{W}" height="3" fill="url(#{uid}-hot)"/>
<rect x="24" y="12" width="64" height="22" rx="3" fill="{RED}"/>
<circle cx="38" cy="23" r="4" fill="#fff"><animate attributeName="opacity" values="1;.2;1" dur="1.2s" repeatCount="indefinite"/></circle>
<text x="48" y="28" font-family="{MONO}" font-size="12" font-weight="700" fill="#fff">LIVE</text>
<text x="104" y="29" font-family="{MONO}" font-size="13" fill="{TEXT}" letter-spacing="3">PIT WALL · YOKSHITH09 · SEASON 2026</text>''')

    # start lights (top right): five pairs light up, then go out together
    lights = []
    for i in range(5):
        on = 0.5 + i * 0.5
        kt = f"0;{on/8:.4f};{on/8+0.0001:.4f};{3.5/8:.4f};{3.5/8+0.0001:.4f};1"
        for row in (0, 1):
            lights.append(
                f'<circle cx="{1004 + i*34}" cy="{17 + row*14}" r="5.5" fill="#3a0b0b">'
                f'<animate attributeName="fill" values="#3a0b0b;#3a0b0b;{RED};{RED};#3a0b0b;#3a0b0b" '
                f'keyTimes="{kt}" dur="8s" repeatCount="indefinite"/></circle>')
    body.append(f'<rect x="988" y="6" width="182" height="36" rx="6" fill="#050505" stroke="#333"/>' + "".join(lights))

    # name block with speed lines
    body.append(f'<g>{speed_lines(uid, 0, 600, [86, 104, 130, 152, 178, 196, 214])}</g>')
    body.append(f'''
<g transform="skewX(-12) translate(40 0)">
  <text x="40" y="142" font-family="{DISPLAY}" font-size="66" font-weight="900" fill="{WHITE}" letter-spacing="1">YOKSHITH</text>
  <text x="40" y="208" font-family="{DISPLAY}" font-size="66" font-weight="900" fill="none" stroke="url(#{uid}-hot)"
        stroke-width="2.2" letter-spacing="1">KUCHIPUDI</text>
  <rect x="40" y="224" width="420" height="6" fill="url(#{uid}-hot)"/>
</g>''')

    roles = ["AI BUILDER", "MULTI-AGENT SYSTEMS ENGINEER", "FULL-STACK DEVELOPER",
             "COMPUTER VISION &amp; ROBOTICS"]
    n, slot = len(roles), 3.2
    for i, role in enumerate(roles):
        a, b = i / n, (i + 1) / n
        kt = f"0;{a:.3f};{a+.02:.3f};{b-.02:.3f};{b:.3f};1"
        body.append(f'<text x="64" y="268" font-family="{MONO}" font-size="18" font-weight="700" fill="{YELLOW}" '
                    f'opacity="0">▶ {role}<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{kt}" '
                    f'dur="{n*slot}s" repeatCount="indefinite"/></text>')

    # timing tower
    tx, ty = 40, 300
    body.append(f'<rect x="{tx}" y="{ty}" width="500" height="264" rx="8" fill="#08080a" fill-opacity=".85" stroke="#2a2b31"/>'
                f'<rect x="{tx}" y="{ty}" width="500" height="34" rx="8" fill="#111"/>'
                f'<text x="{tx+18}" y="{ty+22}" font-family="{MONO}" font-size="13" font-weight="700" fill="{TEXT}" '
                f'letter-spacing="3">TIMING TOWER · TECH DOMAINS</text>'
                f'<text x="{tx+482}" y="{ty+22}" text-anchor="end" font-family="{MONO}" font-size="12" fill="{PURPLE}">● FASTEST</text>')
    for i, (label, col, _) in enumerate(TOWER):
        ry = ty + 46 + i * 42
        body.append(f'''
<g>
  <rect x="{tx+10}" y="{ry}" width="480" height="36" rx="5" fill="#16171c"/>
  <rect x="{tx+10}" y="{ry}" width="40" height="36" rx="5" fill="{WHITE}"/>
  <text x="{tx+30}" y="{ry+25}" text-anchor="middle" font-family="{DISPLAY}" font-size="17" font-weight="900" fill="#111">{i+1}</text>
  <rect x="{tx+58}" y="{ry+6}" width="5" height="24" fill="{col}"/>
  <text x="{tx+76}" y="{ry+24}" font-family="{SANS}" font-size="17" font-weight="700" fill="{TEXT}" letter-spacing="1">{esc(label)}</text>
  <g transform="translate({tx+430} {ry+18})">{car(col, .95)}</g>
</g>''')
    # purple "fastest lap" sweep down the tower
    body.append(f'<rect x="{tx+10}" y="{ty+46}" width="480" height="36" rx="5" fill="{PURPLE}" fill-opacity=".18" '
                f'stroke="{PURPLE}" stroke-opacity=".7"><animate attributeName="y" '
                f'values="{";".join(str(ty+46+i*42) for i in range(5))};{ty+46}" dur="6s" calcMode="discrete" '
                f'repeatCount="indefinite"/></rect>')

    # circuit + cars
    body.append(f'<g>{kerb_path(CIRCUIT, 24)}'
                f'<path d="{CIRCUIT}" fill="none" stroke="#fff" stroke-opacity=".35" stroke-width="1.5" stroke-dasharray="10 12"/>'
                f'<path d="{CIRCUIT}" pathLength="1000" fill="none" stroke="{PURPLE}" stroke-width="5" stroke-linecap="round" '
                f'stroke-dasharray="70 930" filter="url(#{uid}-glow)"><animate attributeName="stroke-dashoffset" '
                f'values="0;-1000" dur="4.5s" repeatCount="indefinite"/></path>'
                f'<rect x="752" y="486" width="12" height="28" fill="url(#{uid}-check)"/></g>')
    for i, (label, col, lap) in enumerate(TOWER):
        body.append(f'<g><animateMotion dur="{lap}s" begin="-{i*1.7:.1f}s" repeatCount="indefinite" rotate="auto" '
                    f'path="{CIRCUIT}"/><g filter="url(#{uid}-glow)">{car(col, 1.15)}</g></g>')
    body.append(f'<text x="925" y="545" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{MUTED}" '
                f'letter-spacing="3">CIRCUIT · PROJECT LAB</text>')

    # bottom strip
    body.append(f'''
<rect x="0" y="584" width="{W}" height="56" fill="#0a0a0a"/>
<rect x="0" y="584" width="{W}" height="2" fill="url(#{uid}-hot)"/>
<text x="600" y="618" text-anchor="middle" font-family="{MONO}" font-size="15" fill="{TEXT}">
  <tspan fill="{CYAN}">◆</tspan> CSE '27 · Amrita Vishwa Vidyapeetham
  <tspan dx="18" fill="{YELLOW}">🏆</tspan> 2× Hackathon Winner
  <tspan dx="18" fill="{GREEN}">●</tspan> Open to opportunities
</text>''')
    body.append("</g>")
    write("hero-pit-wall.svg", "".join(body))


# ---------------------------------------------------------------- divider
def divider() -> None:
    uid, W, H = "d", 1200, 40
    checks = "".join(
        f'<rect x="{40 + i*10}" y="{14 + (i % 2)*6}" width="10" height="6" fill="#e5e7eb" fill-opacity=".22"/>'
        f'<rect x="{40 + i*10}" y="{14 + ((i+1) % 2)*6}" width="10" height="6" fill="#000" fill-opacity=".0"/>'
        for i in range(112))
    body = svg_open(W, H, "divider") + f'''<defs>{base_defs(uid)}</defs>
<rect x="40" y="14" width="1120" height="12" fill="#111" fill-opacity=".6"/>{checks}
<g>
  <animateTransform attributeName="transform" type="translate" values="-60 20;1260 20" dur="3.2s" repeatCount="indefinite"/>
  <line x1="-120" y1="0" x2="-18" y2="0" stroke="url(#{uid}-hot)" stroke-width="3" stroke-linecap="round" stroke-opacity=".8"/>
  <g filter="url(#{uid}-glow)">{car(RED, 1.2)}</g>
</g>'''
    write("divider-checkered.svg", body)


# ---------------------------------------------------------------- cards
def wrap(text: str, width: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines


def chips(x: float, y: float, items: list[str], color: str, max_x: float) -> str:
    out, cx, cy = [], x, y
    for it in items:
        w = 18 + len(it) * 8.7
        if cx + w > max_x:
            cx, cy = x, cy + 36
        out.append(f'<g transform="translate({cx:.1f} {cy})"><path d="M 6 0 H {w:.1f} L {w-6:.1f} 28 H 0 Z" '
                   f'fill="{color}" fill-opacity=".14" stroke="{color}" stroke-opacity=".7"/>'
                   f'<text x="{w/2:.1f}" y="19" text-anchor="middle" font-family="{MONO}" font-size="14.5" '
                   f'fill="{TEXT}">{esc(it)}</text></g>')
        cx += w + 8
    return "".join(out)


def win_card(fname: str, event: str, title: str, tagline: str, bullets: list[str],
             stack: list[str], color: str, seed: int) -> None:
    uid, W, H = f"w{seed}", 600, 440
    per = 2 * (W - 4 + H - 4)
    blines, yy = [], 192
    for b in bullets:
        for j, ln in enumerate(wrap(b, 54)):
            prefix = f'<tspan fill="{color}">▶ </tspan>' if j == 0 else "   "
            blines.append(f'<text x="30" y="{yy}" font-family="{SANS}" font-size="17" fill="{TEXT}" '
                          f'xml:space="preserve">{prefix}{esc(ln)}</text>')
            yy += 24
        yy += 3
    body = svg_open(W, H, f"{event} — {title}") + f"<defs>{base_defs(uid)}</defs>" + frame(uid, W, H) + f'''
<rect x="1" y="1" width="{W-2}" height="10" fill="url(#{uid}-check)" opacity=".85"/>
<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="13" fill="none" stroke="{YELLOW}" stroke-width="2.5"
      stroke-dasharray="160 {per-160}" filter="url(#{uid}-glow)">
  <animate attributeName="stroke-dashoffset" values="0;-{per}" dur="5s" repeatCount="indefinite"/></rect>
<path d="M 28 30 H 236 L 228 60 H 20 Z" fill="{YELLOW}"/>
<text x="126" y="51" text-anchor="middle" font-family="{MONO}" font-size="14" font-weight="700"
      fill="#111" letter-spacing="2">🏆 HACKATHON WIN</text>
<g transform="skewX(-10)">
  <text x="48" y="108" font-family="{DISPLAY}" font-size="36" font-weight="900" fill="{WHITE}">{esc(title)}</text>
</g>
<rect x="30" y="118" width="120" height="4" fill="url(#{uid}-hot)"/>
<text x="30" y="146" font-family="{MONO}" font-size="16" fill="{YELLOW}">{esc(event)}</text>
<text x="30" y="170" font-family="{SANS}" font-size="17" font-style="italic" fill="{MUTED}">{esc(tagline)}</text>
{"".join(blines)}
{chips(30, H-52, stack, color, W-30)}
{flag(500, 34, uid)}'''
    write(fname, body)


# ---------------------------------------------------------------- skills
SKILLS = [
    ("POWER UNIT · LANGUAGES", RED, ["Python", "TypeScript", "JavaScript", "Rust", "Java", "SQL"]),
    ("AERO · AI, AGENTS &amp; LLMs", PURPLE, ["LLMs — Gemini, Groq", "RAG · pgvector", "Embeddings · vector search",
                                         "MCP · NitroStack", "Fetch.ai uAgents", "ASI:One · Agentverse"]),
    ("SENSORS · VISION &amp; ML", YELLOW, ["YOLOv8 (detect + seg)", "OpenCV", "PyTorch", "ONNX Runtime",
                                       "scikit-learn", "MediaPipe"]),
    ("COCKPIT · FRONTEND &amp; DESKTOP", CYAN, ["React", "Next.js", "Tailwind CSS", "Tauri", "HTML · CSS"]),
    ("CHASSIS · BACKEND &amp; DATA", GREEN, ["Node.js · Express", "FastAPI · Flask", "PostgreSQL · Supabase",
                                         "MongoDB · Firebase", "Redis · SQLite"]),
    ("PIT CREW · CLOUD, ROBOTICS, TOOLS", WHITE, ["GCP · Cloud Run", "Docker · Linux", "Git · GitHub Actions",
                                              "CoppeliaSim · SLAM", "Raspberry Pi 4"]),
]


def skills() -> None:
    uid, W, H = "s", 1200, 640
    body = [svg_open(W, H, "Technical specifications: skills by category"), f"<defs>{base_defs(uid)}</defs>",
            frame(uid, W, H),
            f'<text x="40" y="44" font-family="{MONO}" font-size="14" fill="{MUTED}" letter-spacing="5">'
            f'// TECHNICAL SPECIFICATIONS</text>',
            f'<text x="1160" y="44" text-anchor="end" font-family="{MONO}" font-size="12" fill="{MUTED}">'
            f'CAR No. 09 · BUILD 2026</text>']
    for idx, (name, col, items) in enumerate(SKILLS):
        gx, gy = 40 + (idx % 3) * 380, 66 + (idx // 3) * 286
        pid = f"{uid}-c{idx}"
        body.append(f'<clipPath id="{pid}"><rect x="{gx}" y="{gy}" width="360" height="268" rx="10"/></clipPath>'
                    f'<g clip-path="url(#{pid})">'
                    f'<rect x="{gx}" y="{gy}" width="360" height="268" fill="#0e0f12" stroke="#2a2b31"/>'
                    f'<rect x="{gx}" y="{gy}" width="360" height="40" fill="{col}" fill-opacity=".14"/>'
                    f'<rect x="{gx}" y="{gy}" width="6" height="268" fill="{col}"/>'
                    f'<text x="{gx+20}" y="{gy+26}" font-family="{MONO}" font-size="13" font-weight="700" '
                    f'fill="{col}" letter-spacing="1.5">{name}</text>')
        for k, it in enumerate(items):
            ry = gy + 52 + k * 35
            shade = "#15161b" if k % 2 == 0 else "#101115"
            body.append(f'<rect x="{gx+6}" y="{ry}" width="354" height="32" fill="{shade}"/>'
                        f'<text x="{gx+20}" y="{ry+21}" font-family="{MONO}" font-size="12" fill="{col}">'
                        f'{k+1:02d}</text>'
                        f'<text x="{gx+50}" y="{ry+22}" font-family="{SANS}" font-size="16.5" fill="{TEXT}">'
                        f'{esc(it)}</text>')
        body.append(f'<rect x="{gx}" y="{gy+40}" width="360" height="2" fill="{col}" opacity=".85" '
                    f'filter="url(#{uid}-glow)"><animate attributeName="y" values="{gy+40};{gy+266};{gy+40}" '
                    f'dur="{5+idx*.5:.1f}s" repeatCount="indefinite"/></rect></g>')
    write("tech-specs.svg", "".join(body))


# ---------------------------------------------------------------- journey
JOURNEY = [
    ("R1 · 2025", "FOUNDATIONS", CYAN, ["Flask + Bootstrap web apps", "Fake-currency detection (LBP + RF)",
                                        "Smart pet-feeder IoT (C)"]),
    ("R2 · EARLY 2026", "SECURITY · EDGE AI", GREEN, ["NIST 800-63 MFA travel app", "PasswordPal (Tauri + Rust)",
                                                      "WeedPlucker: YOLOv8 on RPi 4"]),
    ("R3 · MID 2026", "FULL-STACK PRODUCTS", YELLOW, ["DRIP 3D AI fitting room", "WearShare + RAG assistant",
                                                      "Diabetic retinopathy grading"]),
    ("R4 · LATE 2026", "AGENTS · RUST · ROBOTS", RED, ["🏆 Fetchathon 3.0 · 🏆 NitroStack", "PLUTO Voice in Rust",
                                                       "AgentArena · Quadruped SLAM"]),
]


def journey() -> None:
    uid, W, H = "j", 1200, 400
    xs = [150, 450, 750, 1050]
    y = 130
    d = (f"M 30 {y} L {xs[0]} {y} C {xs[0]+90} {y}, {xs[0]+60} {y+60}, 300 {y+60} "
         f"C {xs[1]-60} {y+60}, {xs[1]-90} {y}, {xs[1]} {y} C {xs[1]+90} {y}, {xs[1]+60} {y+60}, 600 {y+60} "
         f"C {xs[2]-60} {y+60}, {xs[2]-90} {y}, {xs[2]} {y} C {xs[2]+90} {y}, {xs[2]+60} {y+60}, 900 {y+60} "
         f"C {xs[3]-60} {y+60}, {xs[3]-90} {y}, {xs[3]} {y} L 1170 {y}")
    body = [svg_open(W, H, "Season timeline: developer journey as race rounds"), f"<defs>{base_defs(uid)}</defs>",
            frame(uid, W, H),
            f'<text x="40" y="44" font-family="{MONO}" font-size="14" fill="{MUTED}" letter-spacing="5">'
            f'// SEASON TIMELINE</text>',
            kerb_path(d, 16, 'stroke-linecap="butt"'),
            f'<path d="{d}" fill="none" stroke="#fff" stroke-opacity=".35" stroke-width="1.2" stroke-dasharray="8 10"/>',
            f'<rect x="1150" y="{y-14}" width="14" height="28" fill="url(#{uid}-check)"/>']
    for (rnd, phase, col, items), x in zip(JOURNEY, xs):
        body.append(f'<g><rect x="{x-64}" y="{y-58}" width="128" height="26" rx="4" fill="{col}"/>'
                    f'<text x="{x}" y="{y-40}" text-anchor="middle" font-family="{MONO}" font-size="13" '
                    f'font-weight="700" fill="#111">{rnd}</text>'
                    f'<line x1="{x}" y1="{y-32}" x2="{x}" y2="{y-14}" stroke="{col}" stroke-width="2"/>'
                    f'<circle cx="{x}" cy="{y}" r="9" fill="{col}" stroke="#111" stroke-width="3">'
                    f'<animate attributeName="r" values="8;11;8" dur="2s" repeatCount="indefinite"/></circle></g>')
        ty = y + 120
        body.append(f'<text x="{x}" y="{ty}" text-anchor="middle" font-family="{MONO}" font-size="13" '
                    f'fill="{col}" letter-spacing="1.5" font-weight="700">{esc(phase)}</text>')
        for k, it in enumerate(items):
            body.append(f'<text x="{x}" y="{ty+26+k*22}" text-anchor="middle" font-family="{SANS}" '
                        f'font-size="15" fill="{TEXT}">{esc(it)}</text>')
    body.append(f'<g><animateMotion dur="9s" repeatCount="indefinite" rotate="auto" path="{d}"/>'
                f'<g filter="url(#{uid}-glow)">{car(RED, 1.3)}</g></g>')
    write("season-timeline.svg", "".join(body))


# ---------------------------------------------------------------- telemetry
TELEMETRY = [  # value, label, sub, colour — snapshot from github.com/yokshith09, 19 Nov 2026
    ("860", "CONTRIBUTIONS", "last 12 months", RED),
    ("319", "COMMITS", "Nov 2026 · 4 repos", YELLOW),
    ("30", "PULL REQUESTS", "opened · Nov 2026", CYAN),
    ("36", "PUBLIC REPOS", "and counting", GREEN),
    ("×2", "PULL SHARK", "GitHub achievement", PURPLE),
]


def telemetry() -> None:
    uid, W, H = "t", 1200, 320
    body = [svg_open(W, H, "GitHub telemetry snapshot as dashboard gauges"), f"<defs>{base_defs(uid)}</defs>",
            frame(uid, W, H),
            f'<text x="40" y="44" font-family="{MONO}" font-size="14" fill="{MUTED}" letter-spacing="5">'
            f'// LIVE TELEMETRY</text>',
            f'<text x="1160" y="44" text-anchor="end" font-family="{MONO}" font-size="12" fill="{MUTED}">'
            f'snapshot · 19 Nov 2026</text>']
    # rev-light strip
    leds = []
    cols = [GREEN] * 5 + [RED] * 5 + [PURPLE] * 5
    for i, c in enumerate(cols):
        x = 460 + i * 19
        t = i / len(cols)
        leds.append(f'<circle cx="{x}" cy="38" r="6" fill="#222"><animate attributeName="fill" '
                    f'values="#222;#222;{c};{c};#222" keyTimes="0;{t*.7:.3f};{t*.7+.01:.3f};.85;1" '
                    f'dur="2.4s" repeatCount="indefinite"/></circle>')
    body.append("".join(leds))
    r = 70
    for i, (val, lab, sub, col) in enumerate(TELEMETRY):
        cx, cy = 140 + i * 230, 160
        # 240° arc gauge from 150° to 390°
        def pt(a: float) -> tuple[float, float]:
            return cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))
        (x0, y0), (x1, y1) = pt(150), pt(390)
        arc = f"M {x0:.1f} {y0:.1f} A {r} {r} 0 1 1 {x1:.1f} {y1:.1f}"
        ticks = "".join(
            f'<line x1="{cx + (r-14)*math.cos(math.radians(a)):.1f}" y1="{cy + (r-14)*math.sin(math.radians(a)):.1f}" '
            f'x2="{cx + (r-6)*math.cos(math.radians(a)):.1f}" y2="{cy + (r-6)*math.sin(math.radians(a)):.1f}" '
            f'stroke="#555" stroke-width="2"/>' for a in range(150, 391, 24))
        body.append(f'''
<g>
  <circle cx="{cx}" cy="{cy}" r="{r+12}" fill="#0b0c0f" stroke="#2a2b31" stroke-width="2"/>
  {ticks}
  <path d="{arc}" fill="none" stroke="#24252b" stroke-width="9" stroke-linecap="round"/>
  <path d="{arc}" pathLength="100" fill="none" stroke="{col}" stroke-width="9" stroke-linecap="round"
        stroke-dasharray="100 100" filter="url(#{uid}-glow)">
    <animate attributeName="stroke-dashoffset" values="100;0;0;100" keyTimes="0;.3;.85;1" dur="{4+i*.4:.1f}s" repeatCount="indefinite"/></path>
  <text x="{cx}" y="{cy+14}" text-anchor="middle" font-family="{DISPLAY}" font-size="38" font-weight="900"
        fill="{WHITE}">{esc(val)}</text>
  <text x="{cx}" y="{cy+118}" text-anchor="middle" font-family="{MONO}" font-size="14" font-weight="700"
        fill="{TEXT}" letter-spacing="2">{esc(lab)}</text>
  <text x="{cx}" y="{cy+138}" text-anchor="middle" font-family="{SANS}" font-size="13" fill="{MUTED}">{esc(sub)}</text>
</g>''')
    write("telemetry-dash.svg", "".join(body))


# ---------------------------------------------------------------- footer
def footer() -> None:
    uid, W, H = "f", 1200, 260
    body = [svg_open(W, H, "Lights out. Let's build."), f"<defs>{base_defs(uid)}</defs>", frame(uid, W, H),
            f'<rect x="1" y="1" width="{W-2}" height="12" fill="url(#{uid}-check)" opacity=".85"/>',
            f'<rect x="1" y="{H-13}" width="{W-2}" height="12" fill="url(#{uid}-check)" opacity=".85"/>',
            speed_lines(uid, 0, 1200, [70, 96, 150, 176, 204]),
            f'<g transform="skewX(-12)"><text x="660" y="112" text-anchor="middle" font-family="{DISPLAY}" '
            f'font-size="44" font-weight="900" fill="{WHITE}">LIGHTS OUT. <tspan fill="url(#{uid}-hot)">'
            f'LET\'S BUILD.</tspan></text></g>',
            f'<text x="600" y="150" text-anchor="middle" font-family="{MONO}" font-size="15" fill="{TEXT}">'
            f'Open to AI / software engineering internships, collaborations &amp; hackathon teams</text>',
            f'<text x="600" y="215" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{MUTED}" '
            f'letter-spacing="4">— CHEQUERED FLAG —</text>',
            flag(70, 50, uid, 80, 54, 1.4), flag(1060, 50, uid, 80, 54, 1.7)]
    write("footer-chequered.svg", "".join(body))


if __name__ == "__main__":
    hero()
    divider()
    skills()
    journey()
    telemetry()
    footer()
    win_card("win-fetchathon.svg", "Fetchathon 3.0 · Fetch.ai", "SUPPLYSHOCK",
             "Multi-agent supply-chain disruption response",
             ["6 autonomous uAgents — Sentinel, Exposure, Sourcing, Strategy, Action + Orchestrator",
              "Detects disruptions (cyclones, port strikes), scores supplier exposure, sources alternatives",
              "Runs inside ASI:One chat with interactive approval cards — human-in-the-loop"],
             ["Python", "Fetch.ai uAgents", "Agentverse", "ASI:One"], RED, 301)
    win_card("win-symbioforge.svg", "NitroStack Hackathon · team of 4", "SYMBIOFORGE",
             "AI platform for industrial symbiosis",
             ["8 autonomous AI agents match factory waste streams to reuse opportunities",
              "14 MCP tools: product invention, impact validation, compliance automation",
              "Live on Vercel + NitroCloud with a Next.js 14 dashboard"],
             ["TypeScript", "MCP", "NitroStack", "Next.js", "Zod"], CYAN, 302)
