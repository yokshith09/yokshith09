#!/usr/bin/env python3
"""Generate the animated space-themed SVGs used by the profile README.

Run from the repo root:  python3 scripts/generate_assets.py
Everything is deterministic (seeded), so re-running only changes what you edit.
GitHub renders these as <img>, so animation is SMIL + CSS inside the SVG only.
"""
from __future__ import annotations

import math
import random
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)

SANS = "'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Fira Code', Consolas, 'Courier New', monospace"

BG0, BG1 = "#03040d", "#0b0a24"
CYAN, VIOLET, PINK, GREEN, AMBER, ORANGE = (
    "#22d3ee", "#a78bfa", "#f472b6", "#34d399", "#fbbf24", "#fb923c")
TEXT, MUTED = "#e2e8f0", "#94a3b8"


def esc(s: str) -> str:
    return escape(s, {'"': "&quot;"})


# ---------------------------------------------------------------- shared bits
def svg_open(w: int, h: int, title: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">'
            f'<title>{esc(title)}</title>')


def base_defs(uid: str) -> str:
    return f'''
  <linearGradient id="{uid}-bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{BG0}"/><stop offset="1" stop-color="{BG1}"/>
  </linearGradient>
  <linearGradient id="{uid}-neon" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/>
    <stop offset="1" stop-color="{PINK}"/>
  </linearGradient>
  <filter id="{uid}-glow" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="3" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="{uid}-soft" x="-100%" y="-100%" width="300%" height="300%">
    <feGaussianBlur stdDeviation="22"/>
  </filter>'''


def frame(uid: str, w: int, h: int, rx: int = 22) -> str:
    return (f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="{rx}" '
            f'fill="url(#{uid}-bg)" stroke="#1e1b4b" stroke-width="2"/>')


def stars(w: int, h: int, n: int, seed: int, clip_rx: int = 22) -> str:
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = rnd.uniform(8, w - 8), rnd.uniform(8, h - 8)
        r = rnd.choice([0.6, 0.8, 0.9, 1.1, 1.4, 1.8])
        col = rnd.choice(["#ffffff", "#ffffff", "#c7d2fe", "#a5f3fc", "#fbcfe8"])
        op = rnd.uniform(0.35, 0.95)
        if rnd.random() < 0.35:
            dur = rnd.uniform(2.2, 6.0)
            beg = rnd.uniform(0, 5)
            out.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{col}" opacity="{op:.2f}">'
                f'<animate attributeName="opacity" values="{op:.2f};0.1;{op:.2f}" '
                f'dur="{dur:.1f}s" begin="{beg:.1f}s" repeatCount="indefinite"/></circle>')
        else:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{col}" opacity="{op:.2f}"/>')
    return "<g>" + "".join(out) + "</g>"


def shooting_star(uid: str, x0: float, y0: float, dx: float, dy: float,
                  dur: float, begin: float, length: float = 120) -> str:
    ang = math.degrees(math.atan2(dy, dx))
    return f'''
<g opacity="0">
  <animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.05;.18;.25;1"
           dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>
  <animateTransform attributeName="transform" type="translate"
           values="{x0} {y0};{x0+dx} {y0+dy};{x0+dx} {y0+dy}" keyTimes="0;.25;1"
           dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>
  <g transform="rotate({ang:.1f})">
    <line x1="{-length}" y1="0" x2="0" y2="0" stroke="url(#{uid}-trail)" stroke-width="2" stroke-linecap="round"/>
    <circle r="2.4" fill="#fff" filter="url(#{uid}-glow)"/>
  </g>
</g>'''


def trail_grad(uid: str) -> str:
    return (f'<linearGradient id="{uid}-trail" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="#e0f2fe" stop-opacity=".95"/></linearGradient>')


def ellipse_path(cx: float, cy: float, rx: float, ry: float) -> str:
    # starts at the right-most point, sweeps clockwise (toward viewer first)
    return (f"M {cx+rx:.1f} {cy:.1f} A {rx:.1f} {ry:.1f} 0 1 1 {cx-rx:.1f} {cy:.1f} "
            f"A {rx:.1f} {ry:.1f} 0 1 1 {cx+rx:.1f} {cy:.1f}")


def planet_grad(pid: str, color: str) -> str:
    return (f'<radialGradient id="{pid}" cx=".35" cy=".32" r=".75">'
            f'<stop offset="0" stop-color="#ffffff" stop-opacity=".95"/>'
            f'<stop offset=".25" stop-color="{color}"/>'
            f'<stop offset="1" stop-color="#0b0a24"/></radialGradient>')


def write(name: str, body: str) -> None:
    (OUT / name).write_text(body + "</svg>\n", encoding="utf-8")
    print("wrote", OUT / name)


# ---------------------------------------------------------------- hero
def hero() -> None:
    uid, W, H = "h", 1200, 640
    cx, cy = 600, 418
    planets = [  # label, rx, period(s), color, radius, phase(0..1), ring
        ("AI Agents", 150, 16, CYAN, 11, 0.10, False),
        ("Full Stack", 225, 23, VIOLET, 13, 0.62, False),
        ("Computer Vision", 300, 31, PINK, 12, 0.35, False),
        ("Robotics · SLAM", 375, 40, GREEN, 15, 0.82, True),
        ("Rust · Desktop", 450, 52, ORANGE, 12, 0.50, False),
    ]
    tilt = 0.30

    defs = base_defs(uid) + trail_grad(uid) + f'''
  <radialGradient id="{uid}-sun" cx=".42" cy=".4" r=".7">
    <stop offset="0" stop-color="#fff7d6"/><stop offset=".35" stop-color="{AMBER}"/>
    <stop offset=".8" stop-color="#f97316"/><stop offset="1" stop-color="#9a3412"/>
  </radialGradient>
  <radialGradient id="{uid}-corona" cx=".5" cy=".5" r=".5">
    <stop offset="0" stop-color="{AMBER}" stop-opacity=".55"/>
    <stop offset=".55" stop-color="#f97316" stop-opacity=".18"/>
    <stop offset="1" stop-color="#f97316" stop-opacity="0"/>
  </radialGradient>
  <clipPath id="{uid}-back"><rect x="0" y="0" width="{W}" height="{cy}"/></clipPath>
  <clipPath id="{uid}-front"><rect x="0" y="{cy}" width="{W}" height="{H-cy}"/></clipPath>
  <clipPath id="{uid}-card"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="22"/></clipPath>'''
    for i, p in enumerate(planets):
        defs += planet_grad(f"{uid}-p{i}", p[3])

    # nebulae
    neb = f'''
<g filter="url(#{uid}-soft)">
  <ellipse cx="230" cy="470" rx="230" ry="120" fill="{VIOLET}" opacity=".22">
    <animate attributeName="opacity" values=".16;.28;.16" dur="11s" repeatCount="indefinite"/></ellipse>
  <ellipse cx="980" cy="300" rx="210" ry="110" fill="{CYAN}" opacity=".14">
    <animate attributeName="opacity" values=".1;.22;.1" dur="13s" repeatCount="indefinite"/></ellipse>
  <ellipse cx="600" cy="600" rx="420" ry="70" fill="{PINK}" opacity=".10"/>
</g>'''

    # spiral galaxy (top-right), slow rotation
    rnd = random.Random(7)
    gal = []
    for arm in range(3):
        for k in range(70):
            t = k / 70 * 3.4
            r = 6 + 17 * t
            a = t * 1.35 + arm * 2 * math.pi / 3
            x = r * math.cos(a) + rnd.gauss(0, 2.2)
            y = r * math.sin(a) + rnd.gauss(0, 2.2)
            col = [CYAN, VIOLET, "#ffffff", PINK][rnd.randrange(4)]
            gal.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(.5,1.4):.1f}" '
                       f'fill="{col}" opacity="{max(.15, 1-t/3.6):.2f}"/>')
    galaxy = f'''
<g transform="translate(1065 120) scale(1 .55) rotate(-20)">
  <circle r="26" fill="{VIOLET}" opacity=".35" filter="url(#{uid}-soft)"/>
  <g>{"".join(gal)}
    <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="140s" repeatCount="indefinite"/>
  </g>
  <circle r="4" fill="#fff" filter="url(#{uid}-glow)"/>
</g>
<g transform="translate(120 150) scale(1 .5) rotate(30)" opacity=".7">
  <circle r="16" fill="{CYAN}" opacity=".3" filter="url(#{uid}-soft)"/>
  <circle r="2.5" fill="#fff"/>
</g>'''

    orbits = "".join(
        f'<ellipse cx="{cx}" cy="{cy}" rx="{p[1]}" ry="{p[1]*tilt:.1f}" fill="none" '
        f'stroke="{p[3]}" stroke-opacity=".28" stroke-width="1.2" stroke-dasharray="3 6"/>'
        for p in planets)

    def planet_layer(clip: str, dim: bool) -> str:
        g = []
        for i, (label, rx, per, col, r, phase, ring) in enumerate(planets):
            path = ellipse_path(cx, cy, rx, rx * tilt)
            beg = f"-{phase*per:.2f}s"
            ring_svg = (f'<ellipse rx="{r*2.1}" ry="{r*.55}" fill="none" stroke="{col}" '
                        f'stroke-width="2" stroke-opacity=".8" transform="rotate(-18)"/>' if ring else "")
            g.append(f'''
<g opacity="{.55 if dim else 1}">
  <animateMotion dur="{per}s" begin="{beg}" repeatCount="indefinite" path="{path}"/>
  <g><animateTransform attributeName="transform" type="scale" values="1;1.28;1;.72;1"
       keyTimes="0;.25;.5;.75;1" dur="{per}s" begin="{beg}" repeatCount="indefinite"/>
    <circle r="{r+6}" fill="{col}" opacity=".18"/>
    <circle r="{r}" fill="url(#{uid}-p{i})" filter="url(#{uid}-glow)"/>{ring_svg}
  </g>
</g>''')
        return f'<g clip-path="url(#{uid}-{clip})">' + "".join(g) + "</g>"

    labels = []
    for i, (label, rx, per, col, r, phase, ring) in enumerate(planets):
        path = ellipse_path(cx, cy, rx, rx * tilt)
        labels.append(f'''
<g>
  <animateMotion dur="{per}s" begin="-{phase*per:.2f}s" repeatCount="indefinite" path="{path}"/>
  <text y="{-r-14}" text-anchor="middle" font-family="{MONO}" font-size="13" font-weight="600"
        fill="{col}" stroke="{BG0}" stroke-width="3" paint-order="stroke">{esc(label)}</text>
</g>''')

    sun = f'''
<g>
  <circle cx="{cx}" cy="{cy}" r="120" fill="url(#{uid}-corona)">
    <animate attributeName="r" values="108;126;108" dur="6s" repeatCount="indefinite"/></circle>
  <circle cx="{cx}" cy="{cy}" r="46" fill="url(#{uid}-sun)" filter="url(#{uid}-glow)"/>
  <circle cx="{cx}" cy="{cy}" r="46" fill="none" stroke="#fde68a" stroke-opacity=".5">
    <animate attributeName="r" values="46;64" dur="3.5s" repeatCount="indefinite"/>
    <animate attributeName="stroke-opacity" values=".55;0" dur="3.5s" repeatCount="indefinite"/></circle>
  <text x="{cx}" y="{cy+7}" text-anchor="middle" font-family="{SANS}" font-size="22"
        font-weight="800" fill="#7c2d12" letter-spacing="1">YK</text>
</g>'''

    roles = ["AI Builder", "Multi-Agent Systems Engineer", "Full-Stack Developer",
             "Computer Vision &amp; Robotics Tinkerer"]
    n, slot = len(roles), 3.2
    role_svg = []
    for i, role in enumerate(roles):
        a, b = i / n, (i + 1) / n
        kt = f"0;{a:.3f};{a+.02:.3f};{b-.02:.3f};{b:.3f};1"
        role_svg.append(
            f'<text x="600" y="168" text-anchor="middle" font-family="{MONO}" font-size="20" '
            f'fill="{CYAN}" opacity="0">&gt; {role}<tspan fill="{PINK}">▌</tspan>'
            f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{kt}" '
            f'dur="{n*slot}s" repeatCount="indefinite"/></text>')

    text = f'''
<text x="600" y="64" text-anchor="middle" font-family="{MONO}" font-size="14" fill="{MUTED}"
      letter-spacing="6">// MISSION CONTROL · YOKSHITH09</text>
<text x="600" y="124" text-anchor="middle" font-family="{SANS}" font-size="56" font-weight="800"
      fill="url(#{uid}-neon)" letter-spacing="3" filter="url(#{uid}-glow)">YOKSHITH KUCHIPUDI</text>
{"".join(role_svg)}
<g font-family="{MONO}" font-size="15" text-anchor="middle">
  <text x="600" y="606" fill="{TEXT}">
    <tspan fill="{VIOLET}">◆</tspan> CSE '27 · Amrita Vishwa Vidyapeetham
    <tspan dx="18" fill="{AMBER}">✦</tspan> 2× Hackathon Winner
    <tspan dx="18" fill="{GREEN}">●</tspan> Open to opportunities
  </text>
</g>'''

    shooting = (shooting_star(uid, 80, 40, 420, 160, 9, 1.5)
                + shooting_star(uid, 760, 30, 380, 150, 12, 6.0)
                + shooting_star(uid, 300, 230, 300, 120, 15, 10.0, 90))

    body = (svg_open(W, H, "Yokshith Kuchipudi — animated solar system of skills")
            + f"<defs>{defs}</defs>" + frame(uid, W, H)
            + f'<g clip-path="url(#{uid}-card)">' + neb + stars(W, H, 230, 42) + galaxy
            + shooting + orbits + planet_layer("back", True) + sun
            + planet_layer("front", False) + "".join(labels) + "</g>" + text)
    write("hero-solar-system.svg", body)


# ---------------------------------------------------------------- divider
def divider() -> None:
    uid, W, H = "d", 1200, 36
    body = svg_open(W, H, "divider") + f'''<defs>{base_defs(uid)}
  <linearGradient id="{uid}-line" x1="0" x2="1">
    <stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset=".5" stop-color="{VIOLET}"/>
    <stop offset="1" stop-color="{PINK}" stop-opacity="0"/></linearGradient></defs>
<line x1="40" y1="18" x2="1160" y2="18" stroke="url(#{uid}-line)" stroke-width="2.5"/>
<g filter="url(#{uid}-glow)">
  <circle cy="18" r="3.5" fill="#fff"><animate attributeName="cx" values="40;1160" dur="6s" repeatCount="indefinite"/></circle>
  <circle cy="18" r="2.2" fill="{CYAN}"><animate attributeName="cx" values="1160;40" dur="9s" repeatCount="indefinite"/></circle>
</g>
<g fill="{VIOLET}"><circle cx="600" cy="18" r="5"/><circle cx="600" cy="18" r="10" fill="none" stroke="{VIOLET}" stroke-opacity=".5">
  <animate attributeName="r" values="6;14;6" dur="3s" repeatCount="indefinite"/></circle></g>'''
    write("divider.svg", body)


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
        w = 16 + len(it) * 8.7
        if cx + w > max_x:
            cx, cy = x, cy + 36
        out.append(f'<rect x="{cx:.1f}" y="{cy}" width="{w:.1f}" height="28" rx="14" fill="{color}" '
                   f'fill-opacity=".12" stroke="{color}" stroke-opacity=".55"/>'
                   f'<text x="{cx + w/2:.1f}" y="{cy+19}" text-anchor="middle" font-family="{MONO}" '
                   f'font-size="14.5" fill="{TEXT}">{esc(it)}</text>')
        cx += w + 8
    return "".join(out)


def win_card(fname: str, event: str, title: str, tagline: str, bullets: list[str],
             stack: list[str], color: str, seed: int) -> None:
    uid, W, H = f"w{seed}", 600, 440
    per = 2 * (W - 4 + H - 4)
    trophy = f'''
<g transform="translate(528 66)" filter="url(#{uid}-glow)">
  <animateTransform attributeName="transform" type="translate" values="528 66;528 60;528 66" dur="4s" repeatCount="indefinite"/>
  <path d="M-18 -22 H18 V-4 A18 18 0 0 1 -18 -4 Z" fill="{AMBER}"/>
  <path d="M-18 -16 H-28 A10 10 0 0 0 -16 2 M18 -16 H28 A10 10 0 0 1 16 2" fill="none" stroke="{AMBER}" stroke-width="3.5"/>
  <rect x="-4" y="12" width="8" height="10" fill="{AMBER}"/><rect x="-14" y="22" width="28" height="6" rx="2" fill="{AMBER}"/>
  <path d="M0 -17 l3 6 6.5 1 -4.7 4.6 1.1 6.5 -5.9 -3.1 -5.9 3.1 1.1 -6.5 -4.7 -4.6 6.5 -1 z" fill="#fff7d6"/>
</g>'''
    sparkles = "".join(
        f'<path d="M{x} {y} l2 6 6 2 -6 2 -2 6 -2 -6 -6 -2 6 -2z" fill="{AMBER}" opacity="0">'
        f'<animate attributeName="opacity" values="0;1;0" dur="2.6s" begin="{b}s" repeatCount="indefinite"/></path>'
        for x, y, b in [(478, 38, 0), (572, 104, .9), (490, 112, 1.7)])
    blines = []
    yy = 182
    for b in bullets:
        for j, ln in enumerate(wrap(b, 54)):
            prefix = f'<tspan fill="{color}">▸ </tspan>' if j == 0 else "   "
            blines.append(f'<text x="30" y="{yy}" font-family="{SANS}" font-size="17" fill="{TEXT}" '
                          f'xml:space="preserve">{prefix}{esc(ln)}</text>')
            yy += 24
        yy += 3
    body = svg_open(W, H, f"{event} — {title}") + f"<defs>{base_defs(uid)}</defs>" + frame(uid, W, H) + \
        stars(W, H, 60, seed) + f'''
<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="21" fill="none" stroke="{AMBER}" stroke-width="2.5"
      stroke-dasharray="140 {per-140}" filter="url(#{uid}-glow)">
  <animate attributeName="stroke-dashoffset" values="0;-{per}" dur="7s" repeatCount="indefinite"/></rect>
<rect x="28" y="26" width="190" height="28" rx="14" fill="{AMBER}" fill-opacity=".15" stroke="{AMBER}"/>
<text x="123" y="45" text-anchor="middle" font-family="{MONO}" font-size="13" font-weight="700"
      fill="{AMBER}" letter-spacing="2">🏆 HACKATHON WIN</text>
<text x="30" y="92" font-family="{SANS}" font-size="34" font-weight="800" fill="url(#{uid}-neon)">{esc(title)}</text>
<text x="30" y="118" font-family="{MONO}" font-size="16" fill="{AMBER}">{esc(event)}</text>
<text x="30" y="146" font-family="{SANS}" font-size="17" font-style="italic" fill="{MUTED}">{esc(tagline)}</text>
{"".join(blines)}
{chips(30, H-52, stack, color, W-30)}
{trophy}{sparkles}'''
    write(fname, body)


def project_card(fname: str, title: str, tagline: str, bullets: list[str], stack: list[str],
                 color: str, seed: int, badge: str | None = None) -> None:
    uid, W, H = f"p{seed}", 600, 372
    rnd = random.Random(seed)
    ring_tilt = rnd.uniform(-25, 25)
    planet = f'''
<g transform="translate(536 64)">
  <circle r="30" fill="{color}" opacity=".14" filter="url(#{uid}-glow)"/>
  <circle r="20" fill="url(#{uid}-pl)"/>
  <ellipse rx="34" ry="8" fill="none" stroke="{color}" stroke-opacity=".7" stroke-width="1.6"
           transform="rotate({ring_tilt:.0f})"/>
  <g><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="{rnd.uniform(6,10):.1f}s" repeatCount="indefinite"/>
    <circle cx="40" cy="0" r="3.2" fill="#fff" filter="url(#{uid}-glow)"/></g>
</g>'''
    blines, yy = [], 146
    for b in bullets:
        for j, ln in enumerate(wrap(b, 54)):
            prefix = f'<tspan fill="{color}">▸ </tspan>' if j == 0 else "   "
            blines.append(f'<text x="28" y="{yy}" font-family="{SANS}" font-size="17" fill="{TEXT}" '
                          f'xml:space="preserve">{prefix}{esc(ln)}</text>')
            yy += 24
        yy += 3
    badge_svg = ""
    if badge:
        bw = 18 + len(badge) * 8.6
        badge_svg = (f'<rect x="{W-28-bw:.0f}" y="{H-50}" width="{bw:.0f}" height="28" rx="14" fill="{AMBER}" '
                     f'fill-opacity=".15" stroke="{AMBER}"/><text x="{W-28-bw/2:.0f}" y="{H-31}" '
                     f'text-anchor="middle" font-family="{MONO}" font-size="14.5" fill="{AMBER}">{esc(badge)}</text>')
    body = svg_open(W, H, f"Project: {title}") + \
        f"<defs>{base_defs(uid)}{planet_grad(uid + '-pl', color)}</defs>" + frame(uid, W, H) + \
        stars(W, H, 45, seed) + f'''
<rect x="0" y="22" width="5" height="64" rx="2" fill="{color}" filter="url(#{uid}-glow)"/>
<text x="28" y="60" font-family="{SANS}" font-size="31" font-weight="800" fill="{TEXT}">{esc(title)}</text>
<text x="28" y="90" font-family="{SANS}" font-size="17" fill="{color}">{esc(tagline)}</text>
<line x1="28" y1="108" x2="{W-28}" y2="108" stroke="{color}" stroke-opacity=".25"/>
{"".join(blines)}
{chips(28, H-50, stack, color, W - 40 - (18 + len(badge) * 8.6 if badge else 0))}
{badge_svg}{planet}'''
    write(fname, body)


# ---------------------------------------------------------------- skills
SKILLS = [
    ("LANGUAGES", CYAN, ["Python", "TypeScript", "JavaScript", "Rust", "Java", "SQL"]),
    ("AI · AGENTS · LLMs", VIOLET, ["LLMs — Gemini, Groq", "RAG · pgvector", "Embeddings · vector search",
                                    "MCP · NitroStack", "Fetch.ai uAgents", "ASI:One · Agentverse"]),
    ("VISION · ML", PINK, ["YOLOv8 (detect + seg)", "OpenCV", "PyTorch", "ONNX Runtime",
                           "scikit-learn", "MediaPipe"]),
    ("FRONTEND · DESKTOP", AMBER, ["React", "Next.js", "Tailwind CSS", "Tauri", "HTML · CSS"]),
    ("BACKEND · DATA", GREEN, ["Node.js · Express", "FastAPI · Flask", "PostgreSQL · Supabase",
                               "MongoDB · Firebase", "Redis · SQLite"]),
    ("CLOUD · ROBOTICS · TOOLS", ORANGE, ["GCP · Cloud Run", "Docker · Linux", "Git · GitHub Actions",
                                          "CoppeliaSim · SLAM", "Raspberry Pi 4"]),
]


def skills() -> None:
    uid, W, H = "s", 1200, 640
    body = [svg_open(W, H, "Skills constellation map"), f"<defs>{base_defs(uid)}</defs>",
            frame(uid, W, H), stars(W, H, 170, 99)]
    body.append(f'<text x="600" y="48" text-anchor="middle" font-family="{MONO}" font-size="14" '
                f'fill="{MUTED}" letter-spacing="5">// TECH CONSTELLATIONS</text>')
    rnd = random.Random(5)
    for idx, (name, col, items) in enumerate(SKILLS):
        gx, gy = 40 + (idx % 3) * 380, 78 + (idx // 3) * 280
        body.append(f'<rect x="{gx}" y="{gy}" width="360" height="262" rx="16" fill="{col}" '
                    f'fill-opacity=".04" stroke="{col}" stroke-opacity=".25"/>')
        body.append(f'<text x="{gx+20}" y="{gy+34}" font-family="{MONO}" font-size="14" font-weight="700" '
                    f'fill="{col}" letter-spacing="2">✦ {esc(name)}</text>')
        pts = []
        for k in range(len(items)):
            x = gx + 34 + (k % 2) * 26 + rnd.uniform(-4, 4)
            y = gy + 70 + k * 34
            pts.append((x, y))
        d = " ".join(f"{'M' if i == 0 else 'L'} {x:.1f} {y:.1f}" for i, (x, y) in enumerate(pts))
        length = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
        body.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-opacity=".55" stroke-width="1.3" '
                    f'stroke-dasharray="{length:.0f}" stroke-dashoffset="{length:.0f}">'
                    f'<animate attributeName="stroke-dashoffset" values="{length:.0f};0;0;{length:.0f}" '
                    f'keyTimes="0;.35;.85;1" dur="9s" begin="{idx*.6}s" repeatCount="indefinite"/></path>')
        for k, ((x, y), it) in enumerate(zip(pts, items)):
            body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="{col}" opacity=".15"/>'
                        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#fff" filter="url(#{uid}-glow)">'
                        f'<animate attributeName="r" values="3.2;4.8;3.2" dur="{2.5+k*.4:.1f}s" '
                        f'repeatCount="indefinite"/></circle>'
                        f'<text x="{x+22:.1f}" y="{y+5:.1f}" font-family="{SANS}" font-size="16" '
                        f'fill="{TEXT}">{esc(it)}</text>')
    write("skills-constellations.svg", "".join(body))


# ---------------------------------------------------------------- journey
JOURNEY = [
    ("2025", "FOUNDATIONS", CYAN, ["Flask + Bootstrap web apps", "Fake-currency detection (LBP + RF)",
                                   "Smart pet-feeder IoT (C)"]),
    ("EARLY 2026", "SECURITY · EDGE AI", VIOLET, ["NIST 800-63 MFA travel app", "PasswordPal (Tauri + Rust)",
                                                  "WeedPlucker: YOLOv8 on RPi 4"]),
    ("MID 2026", "FULL-STACK PRODUCTS", PINK, ["DRIP 3D AI fitting room", "WearShare + RAG assistant",
                                               "Diabetic retinopathy grading"]),
    ("LATE 2026", "AGENTS · RUST · ROBOTS", AMBER, ["🏆 Fetchathon 3.0 · 🏆 NitroStack", "PLUTO Voice in Rust",
                                                    "AgentArena · Quadruped SLAM"]),
]


def journey() -> None:
    uid, W, H = "j", 1200, 380
    xs = [150, 450, 750, 1050]
    ys = [250, 190, 140, 92]
    d = f"M 40 300 C 100 280, 120 {ys[0]}, {xs[0]} {ys[0]}"
    for i in range(1, 4):
        mx = (xs[i - 1] + xs[i]) / 2
        d += f" C {mx} {ys[i-1]}, {mx} {ys[i]}, {xs[i]} {ys[i]}"
    d += f" C 1110 70, 1140 50, 1170 40"
    body = [svg_open(W, H, "Developer journey flight path"), f"<defs>{base_defs(uid)}</defs>",
            frame(uid, W, H), stars(W, H, 120, 11),
            f'<text x="40" y="44" font-family="{MONO}" font-size="14" fill="{MUTED}" letter-spacing="5">// FLIGHT LOG</text>',
            f'<path d="{d}" fill="none" stroke="url(#{uid}-neon)" stroke-width="2.5" stroke-dasharray="2 8" '
            f'stroke-linecap="round"><animate attributeName="stroke-dashoffset" values="0;-40" dur="2s" '
            f'repeatCount="indefinite"/></path>']
    for (yr, phase, col, items), x, y in zip(JOURNEY, xs, ys):
        body.append(f'<circle cx="{x}" cy="{y}" r="22" fill="{col}" opacity=".15"><animate attributeName="r" '
                    f'values="18;28;18" dur="4s" repeatCount="indefinite"/></circle>'
                    f'<circle cx="{x}" cy="{y}" r="9" fill="{col}" filter="url(#{uid}-glow)"/>'
                    f'<text x="{x}" y="{y-34}" text-anchor="middle" font-family="{MONO}" font-size="15" '
                    f'font-weight="700" fill="{col}">{yr}</text>')
        ty = y + 44
        body.append(f'<text x="{x}" y="{ty}" text-anchor="middle" font-family="{MONO}" font-size="12.5" '
                    f'fill="{TEXT}" letter-spacing="1.5" font-weight="700">{esc(phase)}</text>')
        for k, it in enumerate(items):
            body.append(f'<text x="{x}" y="{ty+24+k*20}" text-anchor="middle" font-family="{SANS}" '
                        f'font-size="14" fill="{MUTED}">{esc(it)}</text>')
    body.append(f'''
<g>
  <animateMotion dur="14s" repeatCount="indefinite" rotate="auto" path="{d}"/>
  <g filter="url(#{uid}-glow)">
    <path d="M14 0 L-8 -7 L-4 0 L-8 7 Z" fill="#fff"/>
    <path d="M-6 -3 L-20 0 L-6 3 Z" fill="{ORANGE}"><animate attributeName="d"
      values="M-6 -3 L-20 0 L-6 3 Z;M-6 -3 L-28 0 L-6 3 Z;M-6 -3 L-20 0 L-6 3 Z" dur=".4s" repeatCount="indefinite"/></path>
  </g>
</g>''')
    write("journey-flight-path.svg", "".join(body))


# ---------------------------------------------------------------- telemetry
TELEMETRY = [  # value, label, sub, color  — snapshot from github.com/yokshith09, Nov 19 2026
    ("860", "CONTRIBUTIONS", "last 12 months", CYAN),
    ("319", "COMMITS", "Nov 2026 · 4 repos", VIOLET),
    ("30", "PULL REQUESTS", "opened · Nov 2026", PINK),
    ("36", "PUBLIC REPOS", "and counting", GREEN),
    ("×2", "PULL SHARK", "GitHub achievement", AMBER),
]


def telemetry() -> None:
    uid, W, H = "t", 1200, 300
    body = [svg_open(W, H, "GitHub telemetry snapshot"), f"<defs>{base_defs(uid)}</defs>",
            frame(uid, W, H), stars(W, H, 90, 23),
            f'<text x="40" y="44" font-family="{MONO}" font-size="14" fill="{MUTED}" letter-spacing="5">'
            f'// TELEMETRY</text>',
            f'<text x="1160" y="44" text-anchor="end" font-family="{MONO}" font-size="12" fill="{MUTED}">'
            f'snapshot · 19 Nov 2026</text>']
    for i, (val, lab, sub, col) in enumerate(TELEMETRY):
        x, y = 140 + i * 230, 148
        body.append(f'''
<g>
  <ellipse cx="{x}" cy="{y}" rx="74" ry="74" fill="{col}" fill-opacity=".05" stroke="{col}" stroke-opacity=".3"/>
  <ellipse cx="{x}" cy="{y}" rx="90" ry="26" fill="none" stroke="{col}" stroke-opacity=".35" stroke-dasharray="3 5"
           transform="rotate(-15 {x} {y})"/>
  <g transform="rotate(-15 {x} {y})">
    <circle r="5" fill="{col}" filter="url(#{uid}-glow)">
      <animateMotion dur="{5+i*.8:.1f}s" repeatCount="indefinite" path="{ellipse_path(x, y, 90, 26)}"/></circle>
  </g>
  <text x="{x}" y="{y+14}" text-anchor="middle" font-family="{SANS}" font-size="44" font-weight="800"
        fill="{col}" filter="url(#{uid}-glow)">{esc(val)}</text>
  <text x="{x}" y="{y+108}" text-anchor="middle" font-family="{MONO}" font-size="14" font-weight="700"
        fill="{TEXT}" letter-spacing="2">{esc(lab)}</text>
  <text x="{x}" y="{y+128}" text-anchor="middle" font-family="{SANS}" font-size="13" fill="{MUTED}">{esc(sub)}</text>
</g>''')
    write("telemetry.svg", "".join(body))


# ---------------------------------------------------------------- footer
def footer() -> None:
    uid, W, H = "f", 1200, 260
    body = [svg_open(W, H, "Let's build something out of this world"),
            f'''<defs>{base_defs(uid)}{trail_grad(uid)}
  <radialGradient id="{uid}-planet" cx=".5" cy="0" r="1">
    <stop offset="0" stop-color="{VIOLET}" stop-opacity=".9"/><stop offset=".25" stop-color="#312e81"/>
    <stop offset="1" stop-color="{BG0}"/></radialGradient>
  <clipPath id="{uid}-card"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="22"/></clipPath></defs>''',
            frame(uid, W, H), f'<g clip-path="url(#{uid}-card)">', stars(W, H, 120, 77),
            shooting_star(uid, 900, 20, 260, 100, 8, 2),
            f'<ellipse cx="600" cy="980" rx="980" ry="800" fill="url(#{uid}-planet)"/>',
            f'<ellipse cx="600" cy="980" rx="980" ry="800" fill="none" stroke="{CYAN}" stroke-opacity=".7" '
            f'stroke-width="2" filter="url(#{uid}-glow)"><animate attributeName="stroke-opacity" '
            f'values=".35;.9;.35" dur="5s" repeatCount="indefinite"/></ellipse>', "</g>",
            f'<text x="600" y="86" text-anchor="middle" font-family="{SANS}" font-size="34" font-weight="800" '
            f'fill="url(#{uid}-neon)" filter="url(#{uid}-glow)">Let\'s build something out of this world.</text>',
            f'<text x="600" y="122" text-anchor="middle" font-family="{MONO}" font-size="15" fill="{TEXT}">'
            f'Open to AI / software engineering internships, collaborations &amp; hackathon teams</text>',
            f'<text x="600" y="232" text-anchor="middle" font-family="{MONO}" font-size="13" fill="#e0e7ff" '
            f'letter-spacing="4">— END OF TRANSMISSION —</text>']
    write("footer-horizon.svg", "".join(body))


if __name__ == "__main__":
    hero()
    divider()
    skills()
    journey()
    telemetry()
    footer()

    win_card("win-fetchathon.svg", "Fetchathon 3.0 · Fetch.ai", "SupplyShock",
             "Multi-agent supply-chain disruption response",
             ["6 autonomous uAgents — Sentinel, Exposure, Sourcing, Strategy, Action + Orchestrator",
              "Detects disruptions (cyclones, port strikes), scores supplier exposure, sources alternatives",
              "Runs inside ASI:One chat with interactive approval cards — human-in-the-loop"],
             ["Python", "Fetch.ai uAgents", "Agentverse", "ASI:One"], CYAN, 301)
    win_card("win-symbioforge.svg", "NitroStack Hackathon · team of 4", "SymBioForge",
             "AI platform for industrial symbiosis",
             ["8 autonomous AI agents match factory waste streams to reuse opportunities",
              "14 MCP tools: product invention, impact validation, compliance automation",
              "Live on Vercel + NitroCloud with a Next.js 14 dashboard"],
             ["TypeScript", "MCP", "NitroStack", "Next.js", "Zod"], VIOLET, 302)

    project_card("proj-pluto-voice.svg", "PLUTO Voice", "Voice-first desktop assistant for meetings",
                 ["Push-to-talk, dictation, meeting recording, recaps & commitment recall",
                  "Hinglish, Tanglish, Kannada-English and English",
                  "Gemini + Groq clients behind a fallback router; local-first privacy"],
                 ["Rust", "Tauri", "TypeScript", "Gemini", "Groq"], ORANGE, 401)
    project_card("proj-pluto-desktop.svg", "PLUTO Desktop", "Local-first productivity companion",
                 ["Notes, tasks, meetings and an automatic daily work log",
                  "Modular Rust core with a thin Tauri shell and React UI",
                  "Shipping tagged releases (v0.6.0)"],
                 ["Rust", "Tauri", "React", "TypeScript"], AMBER, 402, badge="★ most starred")
    project_card("proj-agentarena.svg", "AgentArena", "Controlled benchmarking for AI agents",
                 ["Identical scenarios for every agent, measured through a Bifrost proxy",
                  "Pass rate, cost, tool calls and latency per run",
                  "Fault injection for resilience scoring + live dashboard"],
                 ["Python", "Node.js", "Docker", "PostgreSQL"], CYAN, 403)
    project_card("proj-quadruped-slam.svg", "Quadruped SLAM", "Autonomous navigation & perception",
                 ["Closed-loop SLAM for a quadruped robot in CoppeliaSim",
                  "ICP localization, frontier exploration, room segmentation",
                  "Semantic extraction with evaluation metrics"],
                 ["Python", "CoppeliaSim", "SLAM", "ICP"], GREEN, 404)
    project_card("proj-drip.svg", "DRIP", "3D AI fitting room for fashion e-commerce",
                 ["Avatar Studio for 3D garment try-on + Style DNA scanner",
                  "Import garments from other retailers by product URL",
                  "OWASP-minded API security; CI/CD via Actions + Vercel"],
                 ["Next.js", "React", "TypeScript", "AI"], PINK, 405)
    project_card("proj-wearshare.svg", "WearShare", "Peer-to-peer fashion rental marketplace",
                 ["Listings, bookings, payments, dashboards and reviews",
                  "Wren: RAG assistant on Gemini embeddings + pgvector",
                  "Razorpay payments, Redis, Cloudflare R2 storage"],
                 ["Next.js", "TypeScript", "PostgreSQL", "Redis"], VIOLET, 406)
