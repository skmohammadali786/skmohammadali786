#!/usr/bin/env python3
"""
render_readme_cards.py
Generates editorial animated SVG cards for SK Mohammad Ali's GitHub profile README.
Includes pure vector SVG portrait generated from user's photograph,
colorful graphical cards for Education, Certifications, Engineering Projects, and Technical Stack.
Supports STATIC=1 mode for static snapshot previews.
"""

import os
import sys
import json
import re
import ctypes
import urllib.request
from datetime import datetime, timedelta
from collections import defaultdict

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARDS_DIR = os.path.join(REPO_DIR, "cards")
DATA_DIR = os.path.join(REPO_DIR, "data")
ASSETS_DIR = os.path.join(REPO_DIR, "assets")
CONTRIBUTIONS_CACHE = os.path.join(DATA_DIR, "contributions.json")
PROFILE_IMAGE_PATH = os.path.join(ASSETS_DIR, "profile.jpg")

USERNAME = "skmohammadali786"
NAME = "SK Mohammad Ali"
LOCATION = "Kalyanpur, Dwarbasini, West Bengal, India"
COLLEGE = "Aliah University · B.Tech Electrical Engineering"
BIO_LINE = "ESP32 Prototyping · Building Electrical Systems (TGA) · Practical Systems Maker"
PORTFOLIO_URL = "https://www.skmohammadali.in"

IS_STATIC = os.environ.get("STATIC", "0") == "1" or "--static" in sys.argv

# Editorial Paper & Ink Palette
COLOR_PAPER = "#FAF7F2"
COLOR_PAPER_SURFACE = "#F4EFE6"
COLOR_BORDER = "#E5DEC9"
COLOR_BORDER_LIGHT = "#EFECE6"
COLOR_INK = "#1A1A1A"
COLOR_INK_MUTED = "#55504A"
COLOR_INK_FAINT = "#8A847C"
COLOR_BLUE = "#1E40AF"
COLOR_BLUE_LIGHT = "#3B82F6"
COLOR_BLUE_PALE = "#DBEAFE"
COLOR_RED = "#DC2626"
COLOR_YELLOW = "#D97706"
COLOR_EMERALD = "#059669"
COLOR_PURPLE = "#7C3AED"

# Fonts
SERIF_FAMILY = "'Instrument Serif', 'Newsreader', Georgia, 'Times New Roman', serif"
MONO_FAMILY = "'Geist Mono', 'SF Mono', Menlo, Monaco, Consolas, 'Courier New', monospace"
SANS_FAMILY = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"


def fetch_contributions(username=USERNAME):
    """Scrapes public GitHub contribution calendar data."""
    os.makedirs(DATA_DIR, exist_ok=True)
    url = f"https://github.com/users/{username}/contributions"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    html = None
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8")
    except Exception as e:
        print(f"[!] Warning: Failed to fetch live contributions ({e}). Checking local cache...")
        if os.path.exists(CONTRIBUTIONS_CACHE):
            with open(CONTRIBUTIONS_CACHE, "r", encoding="utf-8") as f:
                return json.load(f)
        return generate_mock_contributions()

    days_data = re.findall(r'data-date="([^"]+)"[^>]*id="([^"]+)"[^>]*data-level="([0-9])"', html)
    tooltips = dict(re.findall(r'for="([^"]+)"[^>]*>([^<]+)</tool-tip>', html))

    calendar = []
    for date_str, comp_id, level in days_data:
        tip = tooltips.get(comp_id, "")
        count = 0
        m = re.search(r'([0-9]+)\s+contribution', tip)
        if m:
            count = int(m.group(1))
        calendar.append({"date": date_str, "count": count, "level": int(level)})

    calendar.sort(key=lambda x: x["date"])

    total = sum(x["count"] for x in calendar)
    busiest = max(calendar, key=lambda x: x["count"]) if calendar else {"date": "", "count": 0}

    current_streak = 0
    longest_streak = 0
    temp_streak = 0
    today_str = datetime.now().strftime("%Y-%m-%d")

    for day in calendar:
        if day["count"] > 0:
            temp_streak += 1
            if temp_streak > longest_streak:
                longest_streak = temp_streak
        else:
            temp_streak = 0

    for day in reversed(calendar):
        if day["date"] > today_str:
            continue
        if day["count"] > 0:
            current_streak += 1
        elif current_streak > 0:
            break

    monthly = defaultdict(int)
    for day in calendar:
        m_key = day["date"][:7]
        monthly[m_key] += day["count"]

    active_days = sum(1 for d in calendar if d["count"] > 0)

    data = {
        "username": username,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "total_contributions": total,
        "active_days": active_days,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "busiest_day": busiest,
        "monthly": dict(monthly),
        "calendar": calendar
    }

    with open(CONTRIBUTIONS_CACHE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return data


def generate_mock_contributions():
    now = datetime.now()
    calendar = []
    monthly = defaultdict(int)
    total = 0
    for i in range(365, -1, -1):
        d = now - timedelta(days=i)
        d_str = d.strftime("%Y-%m-%d")
        count = (i % 7) * 2 if (i % 3 != 0) else 0
        lvl = min(4, count // 2)
        calendar.append({"date": d_str, "count": count, "level": lvl})
        monthly[d_str[:7]] += count
        total += count

    return {
        "username": USERNAME,
        "updated_at": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "total_contributions": total,
        "active_days": 180,
        "current_streak": 7,
        "longest_streak": 28,
        "busiest_day": {"date": "2026-04-18", "count": 42},
        "monthly": dict(monthly),
        "calendar": calendar
    }


def get_base_css():
    """Returns CSS styles and animations for editorial cards."""
    if IS_STATIC:
        return f"""
        * {{ box-sizing: border-box; }}
        .fade-in, .rise-up, .swing-in, .pop-sq, .grow-bar, .p-row {{ opacity: 1 !important; transform: none !important; }}
        """
    return f"""
        * {{ box-sizing: border-box; }}
        
        @keyframes riseUp {{
          0% {{ opacity: 0; transform: translateY(18px); }}
          100% {{ opacity: 1; transform: translateY(0); }}
        }}

        @keyframes swingIn {{
          0% {{ opacity: 0; transform: translateY(35px) rotate(1.2deg); }}
          70% {{ transform: translateY(-3px) rotate(-0.4deg); }}
          100% {{ opacity: 1; transform: translateY(0) rotate(0); }}
        }}

        @keyframes printRow {{
          0% {{ opacity: 0; transform: translateY(-2.5px); }}
          100% {{ opacity: 1; transform: translateY(0); }}
        }}

        @keyframes pulseDot {{
          0%, 100% {{ opacity: 0.9; transform: scale(1); }}
          50% {{ opacity: 0.3; transform: scale(1.6); }}
        }}

        @keyframes arrowNudge {{
          0%, 100% {{ transform: translateX(0); }}
          50% {{ transform: translateX(5px); }}
        }}

        @keyframes popSquare {{
          0% {{ opacity: 0; transform: scale(0.2); }}
          75% {{ transform: scale(1.15); }}
          100% {{ opacity: 1; transform: scale(1); }}
        }}

        @keyframes growBar {{
          0% {{ transform: scaleY(0); }}
          100% {{ transform: scaleY(1); }}
        }}

        @keyframes popNumber {{
          0% {{ opacity: 0; transform: translateY(6px) scale(0.85); }}
          100% {{ opacity: 1; transform: translateY(0) scale(1); }}
        }}

        .rise-up {{
          animation: riseUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }}

        .pulse-beacon {{
          transform-origin: center;
          animation: pulseDot 2.4s ease-in-out infinite;
        }}

        .nudge-arrow {{
          animation: arrowNudge 2s ease-in-out infinite;
        }}

        @media (prefers-reduced-motion: reduce) {{
          *, *::before, *::after {{
            animation-duration: 0.001ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.001ms !important;
            animation-delay: 0ms !important;
            transform: none !important;
            opacity: 1 !important;
          }}
        }}
    """


def generate_vector_portrait_svg_elements(box_x=600, box_y=44, box_w=295, box_h=295):
    """Generates pure vector SVG circles from the user's photo using libturbojpeg."""
    if not os.path.exists(PROFILE_IMAGE_PATH):
        return ""

    try:
        tj = ctypes.CDLL('/data/user/0/com.termux/files/usr/lib/libturbojpeg.so')
        tj.tjInitDecompress.restype = ctypes.c_void_p
        tj.tjDestroy.argtypes = [ctypes.c_void_p]
        handle = tj.tjInitDecompress()

        with open(PROFILE_IMAGE_PATH, 'rb') as f:
            jpeg_data = f.read()

        w = ctypes.c_int()
        h = ctypes.c_int()
        subsamp = ctypes.c_int()
        colorspace = ctypes.c_int()

        tj.tjDecompressHeader3.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_ulong, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
        tj.tjDecompressHeader3(handle, jpeg_data, len(jpeg_data), ctypes.byref(w), ctypes.byref(h), ctypes.byref(subsamp), ctypes.byref(colorspace))

        tj.tjDecompress2.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_ulong, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        buf = (ctypes.c_ubyte * (w.value * h.value * 3))()
        tj.tjDecompress2(handle, jpeg_data, len(jpeg_data), buf, w.value, 0, h.value, 0, 0)
        tj.tjDestroy(handle)

        W = w.value
        H = h.value

        x0, x1 = 360, 1680
        y0, y1 = 480, 1920

        COLS = 54
        ROWS = 56

        step_x = box_w / COLS
        step_y = box_h / ROWS

        rows_svg = []

        for r in range(ROWS):
            py = int(y0 + (r / ROWS) * (y1 - y0))
            row_circles = []
            for c in range(COLS):
                px = int(x0 + (c / COLS) * (x1 - x0))
                r_sum = g_sum = b_sum = 0
                cnt = 0
                for dy in range(-3, 4):
                    for dx in range(-3, 4):
                        sx = min(W-1, max(0, px + dx))
                        sy = min(H-1, max(0, py + dy))
                        idx = (sy * W + sx) * 3
                        r_sum += buf[idx]
                        g_sum += buf[idx+1]
                        b_sum += buf[idx+2]
                        cnt += 1
                avg_r = int(r_sum / cnt)
                avg_g = int(g_sum / cnt)
                avg_b = int(b_sum / cnt)
                lum = 0.299 * avg_r + 0.587 * avg_g + 0.114 * avg_b

                cx = round(box_x + c * step_x + step_x/2, 1)
                cy = round(box_y + r * step_y + step_y/2, 1)
                rad = round(2.3 + (1.0 - lum/255.0) * 0.8, 1)
                hex_col = f"#{avg_r:02x}{avg_g:02x}{avg_b:02x}"
                row_circles.append(f'<circle cx="{cx}" cy="{cy}" r="{rad}" fill="{hex_col}" />')

            delay = 0 if IS_STATIC else 100 + (r * 18)
            anim_css = f'style="animation: printRow 0.35s ease-out {delay}ms forwards; opacity: {"1" if IS_STATIC else "0"};"'
            rows_svg.append(f'<g class="p-row" {anim_css}>{"".join(row_circles)}</g>')

        return "\n    ".join(rows_svg)
    except Exception as e:
        print(f"[!] Warning: Vector portrait generation error: {e}")
        return ""


def render_standalone_portrait_svg():
    """Renders a standalone portrait.svg file."""
    box_w = 320
    box_h = 320
    elements = generate_vector_portrait_svg_elements(box_x=10, box_y=10, box_w=300, box_h=300)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {box_w} {box_h}" width="100%" height="100%">
  <defs>
    <style>
      {get_base_css()}
    </style>
  </defs>
  <rect width="{box_w}" height="{box_h}" rx="14" fill="#18151D" />
  <rect x="10" y="10" width="300" height="300" rx="10" fill="none" stroke="{COLOR_BORDER}" stroke-width="1.5" />
  {elements}
</svg>"""
    return svg


def render_hero_card():
    """Renders the top Hero SVG card with pure vector color portrait and comprehensive resume details."""
    width = 940
    height = 380

    portrait_vector_elements = generate_vector_portrait_svg_elements(box_x=600, box_y=44, box_w=295, box_h=295)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  <defs>
    <style>
      {get_base_css()}
    </style>
    <linearGradient id="heroInkShine" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{COLOR_INK}" />
      <stop offset="35%" stop-color="{COLOR_INK}" />
      <stop offset="50%" stop-color="{COLOR_BLUE}" />
      <stop offset="65%" stop-color="{COLOR_INK}" />
      <stop offset="100%" stop-color="{COLOR_INK}" />
      {"<animateTransform attributeName='gradientTransform' type='translate' from='-600,0' to='700,0' dur='5.5s' repeatCount='indefinite' />" if not IS_STATIC else ""}
    </linearGradient>
    <pattern id="dotGrid" width="20" height="20" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="0.75" fill="#E6DFD2" opacity="0.7" />
    </pattern>
  </defs>

  <!-- Paper Card Base -->
  <rect x="0" y="0" width="{width}" height="{height}" rx="12" fill="{COLOR_PAPER}" stroke="{COLOR_BORDER}" stroke-width="1.5" />
  <rect x="12" y="12" width="{width - 24}" height="{height - 24}" rx="8" fill="url(#dotGrid)" opacity="0.6" />
  <rect x="16" y="16" width="{width - 32}" height="{height - 32}" rx="6" fill="none" stroke="{COLOR_BORDER_LIGHT}" stroke-width="1" stroke-dasharray="4 4" />

  <!-- Corner Blueprint Marks -->
  <text x="24" y="32" font-family="{MONO_FAMILY}" font-size="10" fill="{COLOR_INK_FAINT}">+ REF.01 // PORTFOLIO</text>
  <text x="{width - 95}" y="32" font-family="{MONO_FAMILY}" font-size="10" fill="{COLOR_INK_FAINT}">EST. 2024 +</text>

  <!-- Left Column: Identity & Comprehensive Resume Details -->
  <g class="rise-up" style="animation-delay: 100ms; opacity: {'1' if IS_STATIC else '0'};">
    <!-- Top Metadata Badge -->
    <rect x="42" y="44" width="280" height="24" rx="12" fill="{COLOR_PAPER_SURFACE}" stroke="{COLOR_BORDER}" stroke-width="1" />
    <circle cx="56" cy="56" r="4" fill="#10B981" />
    <circle cx="56" cy="56" r="4" fill="#10B981" class="pulse-beacon" />
    <text x="68" y="60" font-family="{MONO_FAMILY}" font-size="10" font-weight="600" fill="{COLOR_INK_MUTED}" letter-spacing="0.5">ALIAH UNIV // EE · KOLKATA, IN</text>
    
    <!-- Primary Heading: Name (Ample margin, completely visible) -->
    <text x="42" y="112" font-family="{SERIF_FAMILY}" font-size="40" font-weight="700" fill="url(#heroInkShine)" letter-spacing="-0.3">
      {NAME}
    </text>

    <!-- Subtitle: Role & Core Specialization -->
    <text x="43" y="142" font-family="{SERIF_FAMILY}" font-size="18.5" font-style="italic" fill="{COLOR_BLUE}" letter-spacing="0.2">
      B.Tech Electrical Engineering · Embedded &amp; Practical Systems Maker
    </text>

    <!-- Specific Resume Project & Technical Highlights -->
    <g transform="translate(43, 170)" font-family="{SANS_FAMILY}" font-size="13" fill="{COLOR_INK_MUTED}">
      <text x="0" y="0">
        <tspan font-weight="600" fill="{COLOR_INK}">• Embedded Prototyping:</tspan> ESP32, Motor-Drivers, Voice Wheelchair
      </text>
      <text x="0" y="20">
        <tspan font-weight="600" fill="{COLOR_INK}">• Systems &amp; TGA:</tspan> Building Electrical Systems, Control &amp; AutoCAD
      </text>
      <text x="0" y="40">
        <tspan font-weight="600" fill="{COLOR_INK}">• Software Platforms:</tspan> UConnect App, RailGuard, Next.js, React Native
      </text>
      <text x="0" y="60">
        <tspan font-weight="600" fill="{COLOR_INK}">• Coordination:</tspan> Student Leadership, Task Scheduling &amp; Documentation
      </text>
    </g>

    <!-- Live Status Pill & Internship Target -->
    <g transform="translate(43, 256)">
      <rect x="0" y="0" width="510" height="78" rx="6" fill="{COLOR_PAPER_SURFACE}" stroke="{COLOR_BORDER}" stroke-width="1" />
      <text x="14" y="24" font-family="{MONO_FAMILY}" font-size="11" fill="{COLOR_INK}" font-weight="600">
        <tspan fill="{COLOR_YELLOW}">⚡ CURRENT FOCUS:</tspan> Assistive Tech &amp; Building Electrical Systems
      </text>
      <text x="14" y="46" font-family="{MONO_FAMILY}" font-size="10.5" fill="{COLOR_INK_MUTED}">
        🎯 SEEKING: 2027 Student Internship in Engineering &amp; Systems
      </text>
      <text x="14" y="66" font-family="{MONO_FAMILY}" font-size="10" fill="{COLOR_INK_FAINT}">
        LANGUAGES: Bengali (Native) · English · Hindi · German (B1)
      </text>
    </g>
  </g>

  <!-- Divider Line -->
  <line x1="575" y1="45" x2="575" y2="345" stroke="{COLOR_BORDER}" stroke-width="1" stroke-dasharray="3 3" />

  <!-- Right Column: Pure Vector SVG Color Portrait -->
  <g class="rise-up" style="animation-delay: 200ms; opacity: {'1' if IS_STATIC else '0'};">
    <rect x="596" y="40" width="303" height="303" rx="16" fill="#18151D" stroke="{COLOR_BORDER}" stroke-width="1.5" />
    
    <!-- Vector Portrait Points -->
    {portrait_vector_elements}

    <!-- Frame Border -->
    <rect x="600" y="44" width="295" height="295" rx="14" fill="none" stroke="{COLOR_BORDER}" stroke-width="1.5" />

    <!-- Top Label Badge on Photo -->
    <rect x="612" y="56" width="160" height="22" rx="4" fill="{COLOR_PAPER}" stroke="{COLOR_BORDER}" stroke-width="1" opacity="0.94" />
    <text x="620" y="71" font-family="{MONO_FAMILY}" font-size="10" font-weight="700" fill="{COLOR_BLUE}">SK MOHAMMAD ALI</text>

    <!-- Corner Live Pulse Beacon -->
    <circle cx="880" cy="56" r="4.5" fill="#10B981" />
    <circle cx="880" cy="56" r="4.5" fill="#10B981" class="pulse-beacon" />

    <!-- Bottom Tag -->
    <rect x="612" y="308" width="180" height="20" rx="4" fill="{COLOR_PAPER}" stroke="{COLOR_BORDER}" stroke-width="1" opacity="0.94" />
    <text x="620" y="322" font-family="{MONO_FAMILY}" font-size="9" font-weight="600" fill="{COLOR_INK}">VECTOR PHOTOMETRIC // SVG</text>
  </g>
</svg>"""
    return svg


def render_tile_card(tile_id, category, title, metric, description, accent_color, delay_ms=0):
    """Renders one interactive World Tile card (width 300 x height 190)."""
    width = 300
    height = 190

    anim_style = f"animation: swingIn 0.8s cubic-bezier(0.16, 1, 0.3, 1) {delay_ms}ms forwards; opacity: {'1' if IS_STATIC else '0'};"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  <defs>
    <style>
      {get_base_css()}
    </style>
    <linearGradient id="tileShine_{tile_id}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{accent_color}" />
      <stop offset="40%" stop-color="{accent_color}" />
      <stop offset="50%" stop-color="#FFFFFF" />
      <stop offset="60%" stop-color="{accent_color}" />
      <stop offset="100%" stop-color="{accent_color}" />
      {"<animateTransform attributeName='gradientTransform' type='translate' from='-300,0' to='400,0' dur='4s' repeatCount='indefinite' />" if not IS_STATIC else ""}
    </linearGradient>
  </defs>

  <g style="{anim_style}">
    <rect x="0" y="0" width="{width}" height="{height}" rx="10" fill="{COLOR_PAPER}" stroke="{COLOR_BORDER}" stroke-width="1.5" />
    <path d="M0 10 Q0 0 10 0 L{width - 10} 0 Q{width} 0 {width} 10 L{width} 6 L0 6 Z" fill="{accent_color}" />

    <circle cx="{width - 24}" cy="28" r="4" fill="{accent_color}" />
    <circle cx="{width - 24}" cy="28" r="4" fill="{accent_color}" class="pulse-beacon" />

    <text x="24" y="34" font-family="{MONO_FAMILY}" font-size="11" font-weight="700" fill="{accent_color}" letter-spacing="1">
      {category}
    </text>

    <text x="24" y="78" font-family="{SERIF_FAMILY}" font-size="34" font-weight="700" fill="{COLOR_INK}" letter-spacing="-0.3">
      {title}
    </text>

    <text x="24" y="116" font-family="{SERIF_FAMILY}" font-size="22" font-style="italic" fill="url(#tileShine_{tile_id})">
      {metric}
    </text>

    <text x="24" y="146" font-family="{SANS_FAMILY}" font-size="12.5" fill="{COLOR_INK_MUTED}">
      {description}
    </text>

    <line x1="24" y1="162" x2="{width - 24}" y2="162" stroke="{COLOR_BORDER_LIGHT}" stroke-width="1" />
    <text x="24" y="178" font-family="{MONO_FAMILY}" font-size="10.5" fill="{COLOR_INK_FAINT}">EXPLORE ARCHIVE</text>
    <g transform="translate({width - 38}, 170)" class="nudge-arrow">
      <text x="0" y="8" font-family="{MONO_FAMILY}" font-size="14" font-weight="bold" fill="{accent_color}">→</text>
    </g>
  </g>
</svg>"""
    return svg


def render_education_card():
    """Renders a colorful graphic card for Academic Education with spacious non-overlapping layout."""
    width = 440
    height = 270

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  <defs>
    <style>
      {get_base_css()}
    </style>
    <linearGradient id="eduGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{COLOR_BLUE}" />
      <stop offset="100%" stop-color="#4F46E5" />
    </linearGradient>
  </defs>

  <g class="rise-up" style="animation-delay: 200ms; opacity: {'1' if IS_STATIC else '0'};">
    <!-- Card Frame -->
    <rect x="0" y="0" width="{width}" height="{height}" rx="10" fill="{COLOR_PAPER}" stroke="{COLOR_BORDER}" stroke-width="1.5" />
    <path d="M0 10 Q0 0 10 0 L{width - 10} 0 Q{width} 0 {width} 10 L{width} 5 L0 5 Z" fill="url(#eduGrad)" />

    <!-- Header with Graduation Icon -->
    <g transform="translate(24, 22)">
      <rect x="0" y="0" width="30" height="30" rx="6" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="1" />
      <text x="7" y="21" font-size="16">🎓</text>

      <text x="40" y="14" font-family="{MONO_FAMILY}" font-size="10" font-weight="700" fill="{COLOR_BLUE}" letter-spacing="1">ACADEMIC FOUNDATION</text>
      <text x="40" y="28" font-family="{SERIF_FAMILY}" font-size="18" font-weight="700" fill="{COLOR_INK}">Formal Engineering Education</text>
    </g>

    <line x1="24" y1="64" x2="{width - 24}" y2="64" stroke="{COLOR_BORDER_LIGHT}" stroke-width="1" />

    <!-- Timeline Entry 1: Aliah University -->
    <g transform="translate(24, 76)">
      <!-- Connecting Vertical Line -->
      <line x1="6" y1="16" x2="6" y2="82" stroke="{COLOR_BLUE_PALE}" stroke-width="2" />

      <!-- Node Dot -->
      <circle cx="6" cy="6" r="6" fill="{COLOR_BLUE}" />
      <circle cx="6" cy="6" r="3" fill="#FFFFFF" />

      <!-- Date Badge + Status Pill Aligned Side-by-Side (Zero Overlap) -->
      <text x="24" y="9" font-family="{MONO_FAMILY}" font-size="10.5" font-weight="700" fill="{COLOR_BLUE}">AUG 2024 – PRESENT</text>
      <rect x="180" y="-3" width="92" height="17" rx="3.5" fill="#ECFDF5" stroke="#A7F3D0" stroke-width="1" />
      <circle cx="188" cy="5.5" r="2.5" fill="#10B981" />
      <text x="195" y="9.5" font-family="{MONO_FAMILY}" font-size="8.5" font-weight="600" fill="#047857">IN PROGRESS</text>

      <!-- Details -->
      <text x="24" y="28" font-family="{SERIF_FAMILY}" font-size="16.5" font-weight="700" fill="{COLOR_INK}">B.Tech, Electrical Engineering</text>
      <text x="24" y="46" font-family="{SANS_FAMILY}" font-size="12" font-weight="600" fill="{COLOR_INK_MUTED}">Aliah University, Kolkata</text>
      <text x="24" y="62" font-family="{SANS_FAMILY}" font-size="11" fill="{COLOR_INK_FAINT}">Embedded Control · Motor Drivers · TGA Systems</text>
    </g>

    <!-- Timeline Entry 2: Al-Ameen Mission -->
    <g transform="translate(24, 168)">
      <!-- Node Dot -->
      <circle cx="6" cy="6" r="6" fill="{COLOR_EMERALD}" />
      <circle cx="6" cy="6" r="3" fill="#FFFFFF" />

      <!-- Date Badge + Status Pill Aligned Side-by-Side (Zero Overlap) -->
      <text x="24" y="9" font-family="{MONO_FAMILY}" font-size="10.5" font-weight="700" fill="{COLOR_EMERALD}">2018 – 2024</text>
      <rect x="110" y="-3" width="86" height="17" rx="3.5" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="1" />
      <text x="153" y="9.5" font-family="{MONO_FAMILY}" font-size="8.5" font-weight="600" fill="{COLOR_BLUE}" text-anchor="middle">✓ COMPLETED</text>

      <!-- Details -->
      <text x="24" y="28" font-family="{SERIF_FAMILY}" font-size="16.5" font-weight="700" fill="{COLOR_INK}">Intermediate Science &amp; High School</text>
      <text x="24" y="46" font-family="{SANS_FAMILY}" font-size="12" font-weight="600" fill="{COLOR_INK_MUTED}">Al-Ameen Mission</text>
      <text x="24" y="62" font-family="{SANS_FAMILY}" font-size="11" fill="{COLOR_INK_FAINT}">Mathematics · Physics · Chemistry Foundation</text>
    </g>
  </g>
</svg>"""
    return svg


def render_certifications_card():
    """Renders a colorful graphic card for Verified Certifications with spacious non-overlapping layout."""
    width = 440
    height = 270

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  <defs>
    <style>
      {get_base_css()}
    </style>
    <linearGradient id="certGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{COLOR_YELLOW}" />
      <stop offset="100%" stop-color="#EA580C" />
    </linearGradient>
  </defs>

  <g class="rise-up" style="animation-delay: 250ms; opacity: {'1' if IS_STATIC else '0'};">
    <!-- Card Frame -->
    <rect x="0" y="0" width="{width}" height="{height}" rx="10" fill="{COLOR_PAPER}" stroke="{COLOR_BORDER}" stroke-width="1.5" />
    <path d="M0 10 Q0 0 10 0 L{width - 10} 0 Q{width} 0 {width} 10 L{width} 5 L0 5 Z" fill="url(#certGrad)" />

    <!-- Header with Medal Icon -->
    <g transform="translate(24, 22)">
      <rect x="0" y="0" width="30" height="30" rx="6" fill="#FEF3C7" stroke="#FDE68A" stroke-width="1" />
      <text x="7" y="21" font-size="16">🏆</text>

      <text x="40" y="14" font-family="{MONO_FAMILY}" font-size="10" font-weight="700" fill="{COLOR_YELLOW}" letter-spacing="1">HONORS &amp; CERTIFICATIONS</text>
      <text x="40" y="28" font-family="{SERIF_FAMILY}" font-size="18" font-weight="700" fill="{COLOR_INK}">Recognitions &amp; Competitions</text>
    </g>

    <line x1="24" y1="64" x2="{width - 24}" y2="64" stroke="{COLOR_BORDER_LIGHT}" stroke-width="1" />

    <!-- Certification 1: Samsung Solve for Tomorrow (Spacious, Zero Overlap) -->
    <g transform="translate(24, 74)">
      <rect x="0" y="0" width="{width - 48}" height="82" rx="7" fill="{COLOR_PAPER_SURFACE}" stroke="{COLOR_BORDER}" stroke-width="1" />
      <rect x="0" y="0" width="5" height="82" rx="2" fill="#0284C7" />
      
      <!-- Top Row: Title + National Pill -->
      <text x="16" y="24" font-family="{SERIF_FAMILY}" font-size="16" font-weight="700" fill="{COLOR_INK}">Samsung Solve for Tomorrow</text>
      <rect x="{width - 132}" y="10" width="76" height="18" rx="3" fill="#0284C7" />
      <text x="{width - 94}" y="22.5" font-family="{MONO_FAMILY}" font-size="8.5" font-weight="700" fill="#FFFFFF" text-anchor="middle">NATIONAL</text>

      <!-- Subtitle -->
      <text x="16" y="45" font-family="{SANS_FAMILY}" font-size="11.5" fill="{COLOR_INK_MUTED}">National Innovation Challenge Participation Certificate</text>
      <text x="16" y="64" font-family="{MONO_FAMILY}" font-size="9.5" fill="#0369A1" font-weight="600">INNOVATION · ASSISTIVE HARDWARE · IMPACT</text>
    </g>

    <!-- Certification 2: AURA Participation Certificate (Spacious, Zero Overlap) -->
    <g transform="translate(24, 168)">
      <rect x="0" y="0" width="{width - 48}" height="82" rx="7" fill="{COLOR_PAPER_SURFACE}" stroke="{COLOR_BORDER}" stroke-width="1" />
      <rect x="0" y="0" width="5" height="82" rx="2" fill="{COLOR_YELLOW}" />
      
      <!-- Top Row: Title + Honor Pill -->
      <text x="16" y="24" font-family="{SERIF_FAMILY}" font-size="16" font-weight="700" fill="{COLOR_INK}">AURA Participation Certificate</text>
      <rect x="{width - 132}" y="10" width="76" height="18" rx="3" fill="{COLOR_YELLOW}" />
      <text x="{width - 94}" y="22.5" font-family="{MONO_FAMILY}" font-size="8.5" font-weight="700" fill="#FFFFFF" text-anchor="middle">HONOR</text>

      <!-- Subtitle -->
      <text x="16" y="45" font-family="{SANS_FAMILY}" font-size="11.5" fill="{COLOR_INK_MUTED}">Engineering &amp; Technical Prototyping Challenge</text>
      <text x="16" y="64" font-family="{MONO_FAMILY}" font-size="9.5" fill="{COLOR_YELLOW}" font-weight="600">SYSTEMS DESIGN · ELECTRONICS · TEAMWORK</text>
    </g>
  </g>
</svg>"""
    return svg


def render_engineering_projects_card():
    """Renders a colorful full-width card highlighting Voice Wheelchair & Building Systems TGA."""
    width = 900
    height = 210

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  <defs>
    <style>
      {get_base_css()}
    </style>
  </defs>

  <g class="rise-up" style="animation-delay: 150ms; opacity: {'1' if IS_STATIC else '0'};">
    <rect x="0" y="0" width="{width}" height="{height}" rx="12" fill="{COLOR_PAPER}" stroke="{COLOR_BORDER}" stroke-width="1.5" />

    <!-- Header -->
    <g transform="translate(36, 32)">
      <text x="0" y="0" font-family="{MONO_FAMILY}" font-size="11" font-weight="700" fill="{COLOR_BLUE}" letter-spacing="1">
        TECHNICAL EXPERTISE // PROTOTYPING &amp; BUILDING SYSTEMS
      </text>
      <text x="0" y="22" font-family="{SERIF_FAMILY}" font-size="22" font-weight="700" fill="{COLOR_INK}">
        Core Assistive &amp; Electrical Engineering Projects
      </text>
    </g>

    <!-- Left Half: Voice-Controlled Wheelchair Prototype -->
    <g transform="translate(36, 75)">
      <rect x="0" y="0" width="395" height="110" rx="8" fill="{COLOR_PAPER_SURFACE}" stroke="{COLOR_BORDER}" stroke-width="1" />
      <rect x="0" y="0" width="5" height="110" rx="2" fill="{COLOR_BLUE}" />

      <text x="24" y="28" font-family="{SERIF_FAMILY}" font-size="18" font-weight="700" fill="{COLOR_INK}">
        Voice-Controlled Wheelchair Prototype
      </text>
      <text x="24" y="48" font-family="{SANS_FAMILY}" font-size="12" fill="{COLOR_INK_MUTED}">
        Assistive mobility device powered by an ESP32 microcontroller.
      </text>
      <text x="24" y="66" font-family="{SANS_FAMILY}" font-size="11.5" fill="{COLOR_INK_MUTED}">
        Engineered logic-power isolation and motor-driver interfacing.
      </text>

      <!-- Tags -->
      <g transform="translate(24, 80)">
        <rect x="0" y="0" width="55" height="18" rx="3" fill="#DBEAFE" />
        <text x="27" y="13" font-family="{MONO_FAMILY}" font-size="9" font-weight="600" fill="{COLOR_BLUE}" text-anchor="middle">ESP32</text>

        <rect x="62" y="0" width="85" height="18" rx="3" fill="#EFF6FF" />
        <text x="104" y="13" font-family="{MONO_FAMILY}" font-size="9" font-weight="600" fill="{COLOR_INK}" text-anchor="middle">MOTOR-DRIVER</text>

        <rect x="154" y="0" width="95" height="18" rx="3" fill="#ECFDF5" />
        <text x="201" y="13" font-family="{MONO_FAMILY}" font-size="9" font-weight="600" fill="#047857" text-anchor="middle">ASSISTIVE TECH</text>
      </g>
    </g>

    <!-- Vertical Divider -->
    <line x1="450" y1="75" x2="450" y2="185" stroke="{COLOR_BORDER}" stroke-width="1" stroke-dasharray="3 3" />

    <!-- Right Half: Building Electrical Systems (TGA) -->
    <g transform="translate(468, 75)">
      <rect x="0" y="0" width="395" height="110" rx="8" fill="{COLOR_PAPER_SURFACE}" stroke="{COLOR_BORDER}" stroke-width="1" />
      <rect x="0" y="0" width="5" height="110" rx="2" fill="{COLOR_YELLOW}" />

      <text x="24" y="28" font-family="{SERIF_FAMILY}" font-size="18" font-weight="700" fill="{COLOR_INK}">
        Building Electrical Systems (TGA)
      </text>
      <text x="24" y="48" font-family="{SANS_FAMILY}" font-size="12" fill="{COLOR_INK_MUTED}">
        Technical building equipment planning &amp; electrical consulting.
      </text>
      <text x="24" y="66" font-family="{SANS_FAMILY}" font-size="11.5" fill="{COLOR_INK_MUTED}">
        System coordination, AutoCAD electrical schematics &amp; power.
      </text>

      <!-- Tags -->
      <g transform="translate(24, 80)">
        <rect x="0" y="0" width="80" height="18" rx="3" fill="#FEF3C7" />
        <text x="40" y="13" font-family="{MONO_FAMILY}" font-size="9" font-weight="600" fill="{COLOR_YELLOW}" text-anchor="middle">TGA SYSTEMS</text>

        <rect x="88" y="0" width="65" height="18" rx="3" fill="#EFF6FF" />
        <text x="120" y="13" font-family="{MONO_FAMILY}" font-size="9" font-weight="600" fill="{COLOR_BLUE}" text-anchor="middle">AUTOCAD</text>

        <rect x="160" y="0" width="95" height="18" rx="3" fill="#F3F4F6" />
        <text x="207" y="13" font-family="{MONO_FAMILY}" font-size="9" font-weight="600" fill="{COLOR_INK}" text-anchor="middle">POWER PLANNING</text>
      </g>
    </g>
  </g>
</svg>"""
    return svg


def render_tech_stack_card():
    """Renders a colorful graphic card for Practical Systems & Technical Stack (replacing ASCII table)."""
    width = 940
    height = 320

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  <defs>
    <style>
      {get_base_css()}
    </style>
  </defs>

  <!-- Base Card -->
  <rect x="0" y="0" width="{width}" height="{height}" rx="12" fill="{COLOR_PAPER}" stroke="{COLOR_BORDER}" stroke-width="1.5" />

  <!-- Section Header -->
  <g transform="translate(42, 34)">
    <text x="0" y="0" font-family="{MONO_FAMILY}" font-size="11" font-weight="700" fill="{COLOR_BLUE}" letter-spacing="1">
      TECHNICAL CAPABILITIES // SYSTEMS, ARCHITECTURE &amp; SKILLS
    </text>
    <text x="0" y="22" font-family="{SERIF_FAMILY}" font-size="22" font-weight="700" fill="{COLOR_INK}">
      Practical Systems, Engineering Experience &amp; Technical Stack
    </text>
  </g>

  <!-- 2x2 Grid of Colorful Skill Domains -->
  <!-- Block 1: Electrical & Embedded -->
  <g transform="translate(42, 74)">
    <rect x="0" y="0" width="415" height="105" rx="8" fill="{COLOR_PAPER_SURFACE}" stroke="{COLOR_BORDER}" stroke-width="1" />
    <rect x="0" y="0" width="5" height="105" rx="2" fill="{COLOR_BLUE}" />

    <text x="20" y="24" font-family="{MONO_FAMILY}" font-size="10.5" font-weight="700" fill="{COLOR_BLUE}" letter-spacing="0.5">01 // ELECTRICAL &amp; EMBEDDED</text>
    <text x="20" y="44" font-family="{SERIF_FAMILY}" font-size="16.5" font-weight="700" fill="{COLOR_INK}">Hardware, Firmware &amp; Interfacing</text>
    <text x="20" y="62" font-family="{SANS_FAMILY}" font-size="11" fill="{COLOR_INK_MUTED}">ESP32, Voice Wheelchair, Motor Drivers, Sensors, PCB, Control</text>

    <!-- Colorful Pills -->
    <g transform="translate(20, 74)">
      <rect x="0" y="0" width="50" height="18" rx="3" fill="#DBEAFE" />
      <text x="25" y="12.5" font-family="{MONO_FAMILY}" font-size="8.5" font-weight="600" fill="{COLOR_BLUE}" text-anchor="middle">ESP32</text>

      <rect x="56" y="0" width="82" height="18" rx="3" fill="#EFF6FF" />
      <text x="97" y="12.5" font-family="{MONO_FAMILY}" font-size="8.5" font-weight="600" fill="{COLOR_INK}" text-anchor="middle">MOTOR DRIVER</text>

      <rect x="144" y="0" width="70" height="18" rx="3" fill="#ECFDF5" />
      <text x="179" y="12.5" font-family="{MONO_FAMILY}" font-size="8.5" font-weight="600" fill="#047857" text-anchor="middle">CONTROL</text>

      <rect x="220" y="0" width="45" height="18" rx="3" fill="#F3F4F6" />
      <text x="242" y="12.5" font-family="{MONO_FAMILY}" font-size="8.5" font-weight="600" fill="{COLOR_INK}" text-anchor="middle">PCB</text>
    </g>
  </g>

  <!-- Block 2: Building Systems (TGA) -->
  <g transform="translate(483, 74)">
    <rect x="0" y="0" width="415" height="105" rx="8" fill="{COLOR_PAPER_SURFACE}" stroke="{COLOR_BORDER}" stroke-width="1" />
    <rect x="0" y="0" width="5" height="105" rx="2" fill="{COLOR_YELLOW}" />

    <text x="20" y="24" font-family="{MONO_FAMILY}" font-size="10.5" font-weight="700" fill="{COLOR_YELLOW}" letter-spacing="0.5">02 // BUILDING SYSTEMS (TGA)</text>
    <text x="20" y="44" font-family="{SERIF_FAMILY}" font-size="16.5" font-weight="700" fill="{COLOR_INK}">Infrastructure &amp; Planning</text>
    <text x="20" y="62" font-family="{SANS_FAMILY}" font-size="11" fill="{COLOR_INK_MUTED}">Technical Building Equipment, AutoCAD, MATLAB, Power Distribution</text>

    <!-- Colorful Pills -->
    <g transform="translate(20, 74)">
      <rect x="0" y="0" width="78" height="18" rx="3" fill="#FEF3C7" />
      <text x="39" y="12.5" font-family="{MONO_FAMILY}" font-size="8.5" font-weight="600" fill="{COLOR_YELLOW}" text-anchor="middle">TGA SYSTEMS</text>

      <rect x="84" y="0" width="60" height="18" rx="3" fill="#EFF6FF" />
      <text x="114" y="12.5" font-family="{MONO_FAMILY}" font-size="8.5" font-weight="600" fill="{COLOR_BLUE}" text-anchor="middle">AUTOCAD</text>

      <rect x="150" y="0" width="56" height="18" rx="3" fill="#EFF6FF" />
      <text x="178" y="12.5" font-family="{MONO_FAMILY}" font-size="8.5" font-weight="600" fill="{COLOR_BLUE}" text-anchor="middle">MATLAB</text>

      <rect x="212" y="0" width="90" height="18" rx="3" fill="#F3F4F6" />
      <text x="257" y="12.5" font-family="{MONO_FAMILY}" font-size="8.5" font-weight="600" fill="{COLOR_INK}" text-anchor="middle">POWER PLANNING</text>
    </g>
  </g>

  <!-- Block 3: Full-Stack & Platforms -->
  <g transform="translate(42, 195)">
    <rect x="0" y="0" width="415" height="105" rx="8" fill="{COLOR_PAPER_SURFACE}" stroke="{COLOR_BORDER}" stroke-width="1" />
    <rect x="0" y="0" width="5" height="105" rx="2" fill="{COLOR_EMERALD}" />

    <text x="20" y="24" font-family="{MONO_FAMILY}" font-size="10.5" font-weight="700" fill="{COLOR_EMERALD}" letter-spacing="0.5">03 // SOFTWARE &amp; PLATFORMS</text>
    <text x="20" y="44" font-family="{SERIF_FAMILY}" font-size="16.5" font-weight="700" fill="{COLOR_INK}">Full-Stack &amp; Mobile Ecosystems</text>
    <text x="20" y="62" font-family="{SANS_FAMILY}" font-size="11" fill="{COLOR_INK_MUTED}">TypeScript, Next.js, React Native, Node.js, PostgreSQL, Supabase</text>

    <!-- Colorful Pills -->
    <g transform="translate(20, 74)">
      <rect x="0" y="0" width="70" height="18" rx="3" fill="#DBEAFE" />
      <text x="35" y="12.5" font-family="{MONO_FAMILY}" font-size="8.5" font-weight="600" fill="{COLOR_BLUE}" text-anchor="middle">TYPESCRIPT</text>

      <rect x="76" y="0" width="60" height="18" rx="3" fill="#F3F4F6" />
      <text x="106" y="12.5" font-family="{MONO_FAMILY}" font-size="8.5" font-weight="600" fill="{COLOR_INK}" text-anchor="middle">NEXT.JS</text>

      <rect x="142" y="0" width="76" height="18" rx="3" fill="#E0F2FE" />
      <text x="180" y="12.5" font-family="{MONO_FAMILY}" font-size="8.5" font-weight="600" fill="#0284C7" text-anchor="middle">REACT NATIVE</text>

      <rect x="224" y="0" width="68" height="18" rx="3" fill="#ECFDF5" />
      <text x="258" y="12.5" font-family="{MONO_FAMILY}" font-size="8.5" font-weight="600" fill="#047857" text-anchor="middle">SUPABASE</text>
    </g>
  </g>

  <!-- Block 4: Leadership, Projects & Languages -->
  <g transform="translate(483, 195)">
    <rect x="0" y="0" width="415" height="105" rx="8" fill="{COLOR_PAPER_SURFACE}" stroke="{COLOR_BORDER}" stroke-width="1" />
    <rect x="0" y="0" width="5" height="105" rx="2" fill="{COLOR_PURPLE}" />

    <text x="20" y="24" font-family="{MONO_FAMILY}" font-size="10.5" font-weight="700" fill="{COLOR_PURPLE}" letter-spacing="0.5">04 // COORDINATION &amp; LANGUAGES</text>
    <text x="20" y="44" font-family="{SERIF_FAMILY}" font-size="16.5" font-weight="700" fill="{COLOR_INK}">Project Leadership &amp; Communication</text>
    <text x="20" y="62" font-family="{SANS_FAMILY}" font-size="11" fill="{COLOR_INK_MUTED}">Student Leadership, Milestone Planning, Event Coordination</text>

    <!-- Colorful Pills -->
    <g transform="translate(20, 74)">
      <rect x="0" y="0" width="70" height="18" rx="3" fill="#F3E8FF" />
      <text x="35" y="12.5" font-family="{MONO_FAMILY}" font-size="8.5" font-weight="600" fill="{COLOR_PURPLE}" text-anchor="middle">LEADERSHIP</text>

      <rect x="76" y="0" width="80" height="18" rx="3" fill="#EFF6FF" />
      <text x="116" y="12.5" font-family="{MONO_FAMILY}" font-size="8.5" font-weight="600" fill="{COLOR_BLUE}" text-anchor="middle">PLANNING</text>

      <rect x="162" y="0" width="70" height="18" rx="3" fill="#ECFDF5" />
      <text x="197" y="12.5" font-family="{MONO_FAMILY}" font-size="8.5" font-weight="600" fill="#047857" text-anchor="middle">GERMAN (B1)</text>

      <rect x="238" y="0" width="80" height="18" rx="3" fill="#FEF3C7" />
      <text x="278" y="12.5" font-family="{MONO_FAMILY}" font-size="8.5" font-weight="600" fill="{COLOR_YELLOW}" text-anchor="middle">EN · BN · HI</text>
    </g>
  </g>
</svg>"""
    return svg


def render_contributions_chart(data):
    """Renders the monthly contributions bar chart with streak & activity metrics."""
    width = 900
    height = 250

    monthly = data.get("monthly", {})
    sorted_months = sorted(monthly.keys())[-12:]
    
    max_val = max([monthly[m] for m in sorted_months] + [1])
    chart_h = 100
    chart_bottom_y = 175

    bars_svg = []
    start_x = 45
    bar_w = 26
    step_x = 38

    peak_month = max(sorted_months, key=lambda m: monthly[m]) if sorted_months else ""

    for idx, m_key in enumerate(sorted_months):
        count = monthly[m_key]
        bar_h = int((count / max_val) * chart_h) if max_val > 0 else 4
        bar_h = max(bar_h, 4)
        bar_x = start_x + (idx * step_x)
        bar_y = chart_bottom_y - bar_h

        is_peak = (m_key == peak_month)
        fill_color = COLOR_BLUE if is_peak else ("#93C5FD" if count > 0 else "#E5DEC9")

        try:
            m_dt = datetime.strptime(m_key, "%Y-%m")
            label = m_dt.strftime("%b")
        except:
            label = m_key[-2:]

        delay = 0 if IS_STATIC else 300 + (idx * 45)
        anim_css = f"transform-origin: {bar_x + bar_w/2}px {chart_bottom_y}px; animation: growBar 0.7s cubic-bezier(0.16, 1, 0.3, 1) {delay}ms forwards; transform: scaleY({'1' if IS_STATIC else '0'});"

        peak_badge = ""
        if is_peak:
            peak_delay = delay + 350
            peak_anim = f"animation: popNumber 0.5s ease-out {peak_delay}ms forwards; opacity: {'1' if IS_STATIC else '0'};"
            peak_badge = f"""
            <g style="{peak_anim}">
              <rect x="{bar_x - 10}" y="{bar_y - 28}" width="46" height="20" rx="4" fill="{COLOR_BLUE}" />
              <text x="{bar_x + 13}" y="{bar_y - 14}" font-family="{MONO_FAMILY}" font-size="10" font-weight="700" fill="#FFFFFF" text-anchor="middle">{count}</text>
              <polygon points="{bar_x + 9},{bar_y - 8} {bar_x + 17},{bar_y - 8} {bar_x + 13},{bar_y - 4}" fill="{COLOR_BLUE}" />
            </g>
            """

        bars_svg.append(f"""
        <g>
          {peak_badge}
          <rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="3" fill="{fill_color}" style="{anim_css}" />
          <text x="{bar_x + bar_w/2}" y="{chart_bottom_y + 16}" font-family="{MONO_FAMILY}" font-size="10" fill="{COLOR_INK_MUTED}" text-anchor="middle">{label}</text>
        </g>
        """)

    bars_content = "\n".join(bars_svg)

    total_contribs = data.get("total_contributions", 1297)
    active_days = data.get("active_days", 140)
    current_streak = data.get("current_streak", 0)
    longest_streak = data.get("longest_streak", 18)
    busiest = data.get("busiest_day", {})
    busiest_count = busiest.get("count", 0)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  <defs>
    <style>
      {get_base_css()}
    </style>
  </defs>

  <rect x="0" y="0" width="{width}" height="{height}" rx="12" fill="{COLOR_PAPER}" stroke="{COLOR_BORDER}" stroke-width="1.5" />

  <g transform="translate(42, 38)">
    <text x="0" y="0" font-family="{MONO_FAMILY}" font-size="11" font-weight="700" fill="{COLOR_BLUE}" letter-spacing="1">
      ACTIVITY // MONTHLY CONTRIBUTIONS CADENCE
    </text>
    <text x="0" y="24" font-family="{SERIF_FAMILY}" font-size="24" font-weight="700" fill="{COLOR_INK}">
      12-Month GitHub Commit Frequency
    </text>
  </g>

  <g>
    <line x1="40" y1="{chart_bottom_y}" x2="495" y2="{chart_bottom_y}" stroke="{COLOR_BORDER}" stroke-width="1" />
    {bars_content}
  </g>

  <line x1="530" y1="35" x2="530" y2="{height - 35}" stroke="{COLOR_BORDER}" stroke-width="1" stroke-dasharray="3 3" />

  <g transform="translate(560, 42)">
    <g transform="translate(0, 0)">
      <text x="0" y="12" font-family="{MONO_FAMILY}" font-size="10" font-weight="600" fill="{COLOR_INK_FAINT}">ANNUAL CONTRIBUTIONS</text>
      <text x="0" y="44" font-family="{SERIF_FAMILY}" font-size="34" font-weight="700" fill="{COLOR_BLUE}">{total_contribs:,}</text>
    </g>

    <g transform="translate(160, 0)">
      <text x="0" y="12" font-family="{MONO_FAMILY}" font-size="10" font-weight="600" fill="{COLOR_INK_FAINT}">ACTIVE COMMIT DAYS</text>
      <text x="0" y="44" font-family="{SERIF_FAMILY}" font-size="34" font-weight="700" fill="{COLOR_INK}">{active_days} <tspan font-size="16" font-style="italic">days</tspan></text>
    </g>

    <g transform="translate(0, 75)">
      <text x="0" y="12" font-family="{MONO_FAMILY}" font-size="10" font-weight="600" fill="{COLOR_INK_FAINT}">LONGEST STREAK</text>
      <text x="0" y="44" font-family="{SERIF_FAMILY}" font-size="34" font-weight="700" fill="{COLOR_INK}">{longest_streak} <tspan font-size="16" font-style="italic">days</tspan></text>
    </g>

    <g transform="translate(160, 75)">
      <text x="0" y="12" font-family="{MONO_FAMILY}" font-size="10" font-weight="600" fill="{COLOR_INK_FAINT}">BUSIEST 24H WINDOW</text>
      <text x="0" y="44" font-family="{SERIF_FAMILY}" font-size="34" font-weight="700" fill="{COLOR_YELLOW}">{busiest_count} <tspan font-size="16" font-style="italic">commits</tspan></text>
    </g>

    <rect x="0" y="132" width="295" height="26" rx="4" fill="{COLOR_PAPER_SURFACE}" stroke="{COLOR_BORDER}" stroke-width="1" />
    <circle cx="12" cy="145" r="3.5" fill="#10B981" />
    <text x="24" y="149" font-family="{MONO_FAMILY}" font-size="9.5" fill="{COLOR_INK_MUTED}">AUTOMATED GITHUB CRON REFRESH // DAILY</text>
  </g>
</svg>"""
    return svg


def render_contribution_graph(data):
    """Renders the full 52-week contribution heatmap in Avi's blue palette on paper with sweep pop-in."""
    width = 900
    height = 185

    calendar = data.get("calendar", [])
    display_days = calendar[-364:] if len(calendar) >= 364 else calendar

    LEVEL_COLORS = [
        "#EAE5DB",
        "#BFDBFE",
        "#60A5FA",
        "#2563EB",
        "#1E3A8A"
    ]

    cell_size = 11
    cell_gap = 3.5
    start_x = 48
    start_y = 68

    cells_svg = []
    col = 0
    row = 0

    for idx, day in enumerate(display_days):
        lvl = min(4, max(0, day.get("level", 0)))
        color = LEVEL_COLORS[lvl]
        x = start_x + (col * (cell_size + cell_gap))
        y = start_y + (row * (cell_size + cell_gap))

        delay = 0 if IS_STATIC else 150 + (col * 14)
        anim_css = f"transform-origin: {x + cell_size/2}px {y + cell_size/2}px; animation: popSquare 0.4s ease-out {delay}ms forwards; opacity: {'1' if IS_STATIC else '0'};"

        cells_svg.append(
            f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" rx="2.5" fill="{color}" style="{anim_css}" />'
        )

        row += 1
        if row == 7:
            row = 0
            col += 1

    cells_content = "\n    ".join(cells_svg)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  <defs>
    <style>
      {get_base_css()}
    </style>
  </defs>

  <rect x="0" y="0" width="{width}" height="{height}" rx="12" fill="{COLOR_PAPER}" stroke="{COLOR_BORDER}" stroke-width="1.5" />

  <g transform="translate(48, 38)">
    <text x="0" y="0" font-family="{MONO_FAMILY}" font-size="11" font-weight="700" fill="{COLOR_BLUE}" letter-spacing="1">
      HEATMAP // 52-WEEK COMMIT TIMELINE
    </text>
    <text x="{width - 240}" y="0" font-family="{MONO_FAMILY}" font-size="10.5" fill="{COLOR_INK_MUTED}">
      TOTAL: <tspan font-weight="bold" fill="{COLOR_INK}">{data.get('total_contributions', 1297):,}</tspan> CONTRIBUTIONS
    </text>
  </g>

  <g font-family="{MONO_FAMILY}" font-size="9" fill="{COLOR_INK_FAINT}">
    <text x="24" y="{start_y + 11}">Mon</text>
    <text x="24" y="{start_y + 40}">Wed</text>
    <text x="24" y="{start_y + 69}">Fri</text>
  </g>

  <g>
    {cells_content}
  </g>

  <g transform="translate({width - 220}, {height - 20})" font-family="{MONO_FAMILY}" font-size="9" fill="{COLOR_INK_MUTED}">
    <text x="0" y="9">Less</text>
    <rect x="28" y="0" width="10" height="10" rx="2" fill="{LEVEL_COLORS[0]}" />
    <rect x="42" y="0" width="10" height="10" rx="2" fill="{LEVEL_COLORS[1]}" />
    <rect x="56" y="0" width="10" height="10" rx="2" fill="{LEVEL_COLORS[2]}" />
    <rect x="70" y="0" width="10" height="10" rx="2" fill="{LEVEL_COLORS[3]}" />
    <rect x="84" y="0" width="10" height="10" rx="2" fill="{LEVEL_COLORS[4]}" />
    <text x="100" y="9">More</text>
  </g>
</svg>"""
    return svg


def render_repo_card(name, role_badge, description, lang, lang_color, accent_color, link_url):
    """Renders one featured project repository card (width 440 x height 160)."""
    width = 440
    height = 160

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  <defs>
    <style>
      {get_base_css()}
    </style>
  </defs>

  <g class="rise-up" style="animation-delay: 200ms; opacity: {'1' if IS_STATIC else '0'};">
    <rect x="0" y="0" width="{width}" height="{height}" rx="10" fill="{COLOR_PAPER}" stroke="{COLOR_BORDER}" stroke-width="1.5" />
    <rect x="0" y="0" width="5" height="{height}" rx="2" fill="{accent_color}" />

    <rect x="24" y="22" width="165" height="20" rx="4" fill="{COLOR_PAPER_SURFACE}" stroke="{COLOR_BORDER}" stroke-width="1" />
    <text x="32" y="36" font-family="{MONO_FAMILY}" font-size="9.5" font-weight="600" fill="{accent_color}">{role_badge}</text>

    <text x="24" y="68" font-family="{SERIF_FAMILY}" font-size="24" font-weight="700" fill="{COLOR_INK}">
      {name}
    </text>

    <text x="24" y="94" font-family="{SANS_FAMILY}" font-size="12" fill="{COLOR_INK_MUTED}">
      {description}
    </text>

    <g transform="translate(24, 122)">
      <circle cx="5" cy="5" r="4.5" fill="{lang_color}" />
      <text x="16" y="9" font-family="{MONO_FAMILY}" font-size="11" fill="{COLOR_INK}" font-weight="500">{lang}</text>
    </g>

    <g transform="translate({width - 45}, 120)" class="nudge-arrow">
      <text x="0" y="10" font-family="{MONO_FAMILY}" font-size="16" font-weight="bold" fill="{accent_color}">→</text>
    </g>
  </g>
</svg>"""
    return svg


def main():
    print(f"[*] Rendering animated SVG cards (STATIC={IS_STATIC})...")
    os.makedirs(CARDS_DIR, exist_ok=True)

    data = fetch_contributions(USERNAME)
    print(f"[*] Total contributions: {data.get('total_contributions')}")

    # 1. Hero Card (Embeds pure vector SVG portrait)
    hero_svg = render_hero_card()
    with open(os.path.join(CARDS_DIR, "hero.svg"), "w", encoding="utf-8") as f:
        f.write(hero_svg)
    print("[+] Rendered cards/hero.svg (with pure vector SVG portrait)")

    # 2. Standalone Portrait SVG
    portrait_svg = render_standalone_portrait_svg()
    with open(os.path.join(CARDS_DIR, "portrait.svg"), "w", encoding="utf-8") as f:
        f.write(portrait_svg)
    print("[+] Rendered cards/portrait.svg")

    # 3. Three World Tiles
    t1_svg = render_tile_card(
        tile_id="hardware",
        category="01 / HARDWARE &amp; IOT",
        title="HARDWARE",
        metric="ESP32 &amp; SENSORS",
        description="Voice Wheelchair · RailGuard · Motors &amp; PCB",
        accent_color=COLOR_BLUE,
        delay_ms=200
    )
    with open(os.path.join(CARDS_DIR, "tile_hardware.svg"), "w", encoding="utf-8") as f:
        f.write(t1_svg)
    print("[+] Rendered cards/tile_hardware.svg")

    t2_svg = render_tile_card(
        tile_id="software",
        category="02 / FULL-STACK &amp; APPS",
        title="SOFTWARE",
        metric="UCONNECT APP",
        description="Campus &amp; Delivery Logistics · React Native · Next.js",
        accent_color=COLOR_RED,
        delay_ms=350
    )
    with open(os.path.join(CARDS_DIR, "tile_software.svg"), "w", encoding="utf-8") as f:
        f.write(t2_svg)
    print("[+] Rendered cards/tile_software.svg")

    t3_svg = render_tile_card(
        tile_id="innovation",
        category="03 / SYSTEMS &amp; TGA",
        title="INNOVATION",
        metric="PROJECT COORD",
        description="Building Electrical (TGA) · Control · Documentation",
        accent_color=COLOR_YELLOW,
        delay_ms=500
    )
    with open(os.path.join(CARDS_DIR, "tile_innovation.svg"), "w", encoding="utf-8") as f:
        f.write(t3_svg)
    print("[+] Rendered cards/tile_innovation.svg")

    # 4. Core Engineering Projects Card (Voice Wheelchair + TGA Systems)
    projects_svg = render_engineering_projects_card()
    with open(os.path.join(CARDS_DIR, "card_engineering_projects.svg"), "w", encoding="utf-8") as f:
        f.write(projects_svg)
    print("[+] Rendered cards/card_engineering_projects.svg")

    # 5. Colorful Practical Systems & Technical Stack Card
    stack_svg = render_tech_stack_card()
    with open(os.path.join(CARDS_DIR, "card_tech_stack.svg"), "w", encoding="utf-8") as f:
        f.write(stack_svg)
    print("[+] Rendered cards/card_tech_stack.svg")

    # 6. Education Card (Fixed spacing, zero overlapping text)
    edu_svg = render_education_card()
    with open(os.path.join(CARDS_DIR, "card_education.svg"), "w", encoding="utf-8") as f:
        f.write(edu_svg)
    print("[+] Rendered cards/card_education.svg")

    # 7. Certifications Card (Fixed spacing, zero overlapping text)
    cert_svg = render_certifications_card()
    with open(os.path.join(CARDS_DIR, "card_certifications.svg"), "w", encoding="utf-8") as f:
        f.write(cert_svg)
    print("[+] Rendered cards/card_certifications.svg")

    # 8. Monthly Contributions Chart
    chart_svg = render_contributions_chart(data)
    with open(os.path.join(CARDS_DIR, "contributions_chart.svg"), "w", encoding="utf-8") as f:
        f.write(chart_svg)
    print("[+] Rendered cards/contributions_chart.svg")

    # 9. 52-Week Blue Contribution Heatmap
    graph_svg = render_contribution_graph(data)
    with open(os.path.join(CARDS_DIR, "contribution_graph.svg"), "w", encoding="utf-8") as f:
        f.write(graph_svg)
    print("[+] Rendered cards/contribution_graph.svg")

    # 10. Featured Repos (RailGuard & UConnect App)
    repo1_svg = render_repo_card(
        name="RailGuard",
        role_badge="IOT &amp; EMBEDDED SYSTEM",
        description="Railway safety &amp; automated track collision monitoring.",
        lang="Kotlin · Arduino / C++",
        lang_color="#A97BFF",
        accent_color=COLOR_BLUE,
        link_url="https://github.com/skmohammadali786/RailGuard"
    )
    with open(os.path.join(CARDS_DIR, "repo_railguard.svg"), "w", encoding="utf-8") as f:
        f.write(repo1_svg)
    print("[+] Rendered cards/repo_railguard.svg")

    repo2_svg = render_repo_card(
        name="UConnect App",
        role_badge="FULL-STACK PLATFORM",
        description="Real-time campus &amp; community logistics connectivity suite.",
        lang="TypeScript · React Native",
        lang_color="#3178C6",
        accent_color=COLOR_RED,
        link_url="https://github.com/skmohammadali786"
    )
    with open(os.path.join(CARDS_DIR, "repo_uconnect.svg"), "w", encoding="utf-8") as f:
        f.write(repo2_svg)
    print("[+] Rendered cards/repo_uconnect.svg")

    print("[✔] All animated SVG cards generated successfully in cards/!")


if __name__ == "__main__":
    main()
