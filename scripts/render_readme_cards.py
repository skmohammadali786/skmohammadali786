#!/usr/bin/env python3
"""
render_readme_cards.py
Generates editorial animated SVG cards for SK Mohammad Ali's GitHub profile README.
Inspired by Avi Vashishta's animated SVG cards architecture.
Supports STATIC=1 mode for static snapshot previews.
"""

import os
import sys
import json
import re
import urllib.request
from datetime import datetime, timedelta
from collections import defaultdict

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARDS_DIR = os.path.join(REPO_DIR, "cards")
DATA_DIR = os.path.join(REPO_DIR, "data")
CONTRIBUTIONS_CACHE = os.path.join(DATA_DIR, "contributions.json")

USERNAME = "skmohammadali786"
NAME = "SK Mohammad Ali"
LOCATION = "Kolkata, West Bengal, India"
COLLEGE = "Aliah University · Electrical Engineering"
BIO_LINE = "Electrical Engineering Student · Hardware & Software Systems Maker"
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

    # Parse days and levels
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

    # Streaks
    current_streak = 0
    longest_streak = 0
    temp_streak = 0
    today_str = datetime.now().strftime("%Y-%m-%d")

    # Filter active days up to today
    for day in calendar:
        if day["count"] > 0:
            temp_streak += 1
            if temp_streak > longest_streak:
                longest_streak = temp_streak
        else:
            temp_streak = 0

    # Calculate current streak backwards
    for day in reversed(calendar):
        if day["date"] > today_str:
            continue
        if day["count"] > 0:
            current_streak += 1
        elif current_streak > 0:
            break

    # Group by month
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
    """Generates realistic fallback data if offline."""
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
        .fade-in, .rise-up, .swing-in, .pop-sq, .grow-bar {{ opacity: 1 !important; transform: none !important; }}
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
          0% {{ opacity: 0; transform: translateX(-4px); }}
          100% {{ opacity: 1; transform: translateX(0); }}
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


def render_hero_card():
    """Renders the top Hero SVG card with editorial typography, ASCII IC circuit and SMIL shine."""
    width = 900
    height = 360

    # Stylized Hardware IC & Embedded Architecture ASCII
    ascii_rows = [
        "+-----------------------------------------+",
        "|  [ALIAH-EE]   ALIAH UNIVERSITY // KOLKATA|",
        "|  +====================================+ |",
        "|  |   SK-MOHAMMAD-ALI // ARCHITECTURE  | |",
        "|  |  .------.       .-----.    .------.| |",
        "|  |  |SENSOR|------>| MCU |<-->| RF/4G || |",
        "|  |  '------'       '-----'    '------'| |",
        "|  |     |         [SYSTEMS]        |   | |",
        "|  |   =====     I2C  SPI  PWM    ===== | |",
        "|  |    GND      SDA  CLK  IO5     3V3  | |",
        "|  +====================================+ |",
        "|  PIN: 01 02 03 04 05 06 07 08 09 10 11  |",
        "|  STATUS: EMBEDDED + FULLSTACK ONLINE ●  |",
        "+-----------------------------------------+"
    ]

    ascii_svg_elements = []
    base_y = 120
    for idx, row in enumerate(ascii_rows):
        delay = 0 if IS_STATIC else 250 + (idx * 40)
        anim_attr = f'style="animation: printRow 0.4s ease-out {delay}ms forwards; opacity: {"1" if IS_STATIC else "0"};"'
        # escape row
        escaped_row = row.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        ascii_svg_elements.append(
            f'<text x="515" y="{base_y + (idx * 16)}" font-family="{MONO_FAMILY}" font-size="11" fill="{COLOR_INK}" letter-spacing="0.5" {anim_attr}>{escaped_row}</text>'
        )
    ascii_content = "\n    ".join(ascii_svg_elements)

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
  <text x="24" y="32" font-family="{MONO_FAMILY}" font-size="10" fill="{COLOR_INK_FAINT}">+ REF.01</text>
  <text x="{width - 70}" y="32" font-family="{MONO_FAMILY}" font-size="10" fill="{COLOR_INK_FAINT}">EST. 2024 +</text>

  <!-- Left Column: Identity & Bio -->
  <g class="rise-up" style="animation-delay: 100ms; opacity: {'1' if IS_STATIC else '0'};">
    <!-- Top Metadata Badge -->
    <rect x="42" y="52" width="250" height="24" rx="12" fill="{COLOR_PAPER_SURFACE}" stroke="{COLOR_BORDER}" stroke-width="1" />
    <circle cx="56" cy="64" r="4" fill="#10B981" />
    <circle cx="56" cy="64" r="4" fill="#10B981" class="pulse-beacon" />
    <text x="68" y="68" font-family="{MONO_FAMILY}" font-size="10.5" font-weight="600" fill="{COLOR_INK_MUTED}" letter-spacing="0.5">ALIAH UNIV // KOLKATA, IN</text>
    
    <!-- Primary Heading: Name -->
    <text x="42" y="132" font-family="{SERIF_FAMILY}" font-size="52" font-weight="700" fill="url(#heroInkShine)" letter-spacing="-0.5">
      {NAME}
    </text>

    <!-- Subtitle: Role & Specialty -->
    <text x="43" y="168" font-family="{SERIF_FAMILY}" font-size="21" font-style="italic" fill="{COLOR_BLUE}" letter-spacing="0.2">
      Electrical Engineering &amp; Practical Systems Maker
    </text>

    <!-- Bio Paragraph -->
    <text x="43" y="206" font-family="{SANS_FAMILY}" font-size="14.5" fill="{COLOR_INK_MUTED}" font-weight="400">
      Bridging software intelligence and physical electronics.
    </text>
    <text x="43" y="228" font-family="{SANS_FAMILY}" font-size="14.5" fill="{COLOR_INK_MUTED}" font-weight="400">
      Designing safety IoT firmware, full-stack apps, and connected products.
    </text>

    <!-- Live Status Pill -->
    <g transform="translate(43, 262)">
      <rect x="0" y="0" width="415" height="42" rx="6" fill="{COLOR_PAPER_SURFACE}" stroke="{COLOR_BORDER}" stroke-width="1" />
      <text x="16" y="26" font-family="{MONO_FAMILY}" font-size="11.5" fill="{COLOR_INK}" font-weight="500">
        <tspan fill="{COLOR_YELLOW}">⚡ CURRENTLY:</tspan> Building RailGuard &amp; Logistics Apps
      </text>
    </g>
  </g>

  <!-- Divider Line -->
  <line x1="485" y1="50" x2="485" y2="310" stroke="{COLOR_BORDER}" stroke-width="1" stroke-dasharray="3 3" />

  <!-- Right Column: Hardware & Circuit ASCII -->
  <g>
    <!-- ASCII Container Box -->
    <rect x="500" y="90" width="365" height="235" rx="6" fill="{COLOR_PAPER_SURFACE}" stroke="{COLOR_BORDER}" stroke-width="1" />
    <rect x="500" y="55" width="180" height="26" rx="4" fill="{COLOR_PAPER}" stroke="{COLOR_BORDER}" stroke-width="1" />
    <text x="512" y="72" font-family="{MONO_FAMILY}" font-size="10.5" font-weight="600" fill="{COLOR_INK_MUTED}">CIRCUIT_SCHEMATIC.TXT</text>
    {ascii_content}
  </g>
</svg>"""
    return svg


def render_tile_card(tile_id, category, title, metric, description, accent_color, delay_ms=0):
    """Renders one interactive World Tile card (width 300 x height 190)."""
    width = 300
    height = 190

    # SMIL count up simulation or clean typography
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
    <!-- Background Card -->
    <rect x="0" y="0" width="{width}" height="{height}" rx="10" fill="{COLOR_PAPER}" stroke="{COLOR_BORDER}" stroke-width="1.5" />
    
    <!-- Top Accent Stripe -->
    <path d="M0 10 Q0 0 10 0 L{width - 10} 0 Q{width} 0 {width} 10 L{width} 6 L0 6 Z" fill="{accent_color}" />

    <!-- Corner Beacon -->
    <circle cx="{width - 24}" cy="28" r="4" fill="{accent_color}" />
    <circle cx="{width - 24}" cy="28" r="4" fill="{accent_color}" class="pulse-beacon" />

    <!-- Category Header -->
    <text x="24" y="34" font-family="{MONO_FAMILY}" font-size="11" font-weight="700" fill="{accent_color}" letter-spacing="1">
      {category}
    </text>

    <!-- Main Title in Serif -->
    <text x="24" y="78" font-family="{SERIF_FAMILY}" font-size="34" font-weight="700" fill="{COLOR_INK}" letter-spacing="-0.3">
      {title}
    </text>

    <!-- Big Metric Number -->
    <text x="24" y="116" font-family="{SERIF_FAMILY}" font-size="23" font-style="italic" fill="url(#tileShine_{tile_id})">
      {metric}
    </text>

    <!-- Description / Tech Subtitle -->
    <text x="24" y="146" font-family="{SANS_FAMILY}" font-size="13" fill="{COLOR_INK_MUTED}">
      {description}
    </text>

    <!-- Link / Action Arrow Footer -->
    <line x1="24" y1="162" x2="{width - 24}" y2="162" stroke="{COLOR_BORDER_LIGHT}" stroke-width="1" />
    <text x="24" y="178" font-family="{MONO_FAMILY}" font-size="10.5" fill="{COLOR_INK_FAINT}">EXPLORE ARCHIVE</text>
    <g transform="translate({width - 38}, 170)" class="nudge-arrow">
      <text x="0" y="8" font-family="{MONO_FAMILY}" font-size="14" font-weight="bold" fill="{accent_color}">→</text>
    </g>
  </g>
</svg>"""
    return svg


def render_contributions_chart(data):
    """Renders the monthly contributions bar chart with streak & activity metrics."""
    width = 900
    height = 250

    monthly = data.get("monthly", {})
    # Take the last 12 months in order
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

        # Month label: format YYYY-MM to 'Jan', 'Feb', etc.
        try:
            m_dt = datetime.strptime(m_key, "%Y-%m")
            label = m_dt.strftime("%b")
        except:
            label = m_key[-2:]

        delay = 0 if IS_STATIC else 300 + (idx * 45)
        anim_css = f"transform-origin: {bar_x + bar_w/2}px {chart_bottom_y}px; animation: growBar 0.7s cubic-bezier(0.16, 1, 0.3, 1) {delay}ms forwards; transform: scaleY({'1' if IS_STATIC else '0'});"

        # Peak indicator badge
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

    # Right stats metrics
    total_contribs = data.get("total_contributions", 1297)
    active_days = data.get("active_days", 140)
    current_streak = data.get("current_streak", 0)
    longest_streak = data.get("longest_streak", 18)
    busiest = data.get("busiest_day", {})
    busiest_count = busiest.get("count", 0)
    busiest_date = busiest.get("date", "N/A")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  <defs>
    <style>
      {get_base_css()}
    </style>
  </defs>

  <!-- Base Paper -->
  <rect x="0" y="0" width="{width}" height="{height}" rx="12" fill="{COLOR_PAPER}" stroke="{COLOR_BORDER}" stroke-width="1.5" />

  <!-- Section Header -->
  <g transform="translate(42, 38)">
    <text x="0" y="0" font-family="{MONO_FAMILY}" font-size="11" font-weight="700" fill="{COLOR_BLUE}" letter-spacing="1">
      ACTIVITY // MONTHLY CONTRIBUTIONS CADENCE
    </text>
    <text x="0" y="24" font-family="{SERIF_FAMILY}" font-size="24" font-weight="700" fill="{COLOR_INK}">
      12-Month GitHub Commit Frequency
    </text>
  </g>

  <!-- Left: Monthly Bars -->
  <g>
    <!-- Baseline -->
    <line x1="40" y1="{chart_bottom_y}" x2="495" y2="{chart_bottom_y}" stroke="{COLOR_BORDER}" stroke-width="1" />
    {bars_content}
  </g>

  <!-- Vertical Divider -->
  <line x1="530" y1="35" x2="530" y2="{height - 35}" stroke="{COLOR_BORDER}" stroke-width="1" stroke-dasharray="3 3" />

  <!-- Right: Stat Blocks -->
  <g transform="translate(560, 42)">
    <!-- Stat 1: Total Contributions -->
    <g transform="translate(0, 0)">
      <text x="0" y="12" font-family="{MONO_FAMILY}" font-size="10" font-weight="600" fill="{COLOR_INK_FAINT}">ANNUAL CONTRIBUTIONS</text>
      <text x="0" y="44" font-family="{SERIF_FAMILY}" font-size="34" font-weight="700" fill="{COLOR_BLUE}">{total_contribs:,}</text>
    </g>

    <!-- Stat 2: Active Days -->
    <g transform="translate(160, 0)">
      <text x="0" y="12" font-family="{MONO_FAMILY}" font-size="10" font-weight="600" fill="{COLOR_INK_FAINT}">ACTIVE COMMIT DAYS</text>
      <text x="0" y="44" font-family="{SERIF_FAMILY}" font-size="34" font-weight="700" fill="{COLOR_INK}">{active_days} <tspan font-size="16" font-style="italic">days</tspan></text>
    </g>

    <!-- Stat 3: Longest Streak -->
    <g transform="translate(0, 75)">
      <text x="0" y="12" font-family="{MONO_FAMILY}" font-size="10" font-weight="600" fill="{COLOR_INK_FAINT}">LONGEST STREAK</text>
      <text x="0" y="44" font-family="{SERIF_FAMILY}" font-size="34" font-weight="700" fill="{COLOR_INK}">{longest_streak} <tspan font-size="16" font-style="italic">days</tspan></text>
    </g>

    <!-- Stat 4: Peak Output Day -->
    <g transform="translate(160, 75)">
      <text x="0" y="12" font-family="{MONO_FAMILY}" font-size="10" font-weight="600" fill="{COLOR_INK_FAINT}">BUSIEST 24H WINDOW</text>
      <text x="0" y="44" font-family="{SERIF_FAMILY}" font-size="34" font-weight="700" fill="{COLOR_YELLOW}">{busiest_count} <tspan font-size="16" font-style="italic">commits</tspan></text>
    </g>

    <!-- Footer Timestamp -->
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
    # 52 weeks * 7 days = 364 days
    display_days = calendar[-364:] if len(calendar) >= 364 else calendar

    # Ink & Blue Palette
    LEVEL_COLORS = [
        "#EAE5DB", # Level 0 (soft paper cavity)
        "#BFDBFE", # Level 1 (pale sky)
        "#60A5FA", # Level 2 (medium blue)
        "#2563EB", # Level 3 (vibrant royal blue)
        "#1E3A8A"  # Level 4 (deep ink cobalt)
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

  <!-- Paper Card Background -->
  <rect x="0" y="0" width="{width}" height="{height}" rx="12" fill="{COLOR_PAPER}" stroke="{COLOR_BORDER}" stroke-width="1.5" />

  <!-- Graph Header -->
  <g transform="translate(48, 38)">
    <text x="0" y="0" font-family="{MONO_FAMILY}" font-size="11" font-weight="700" fill="{COLOR_BLUE}" letter-spacing="1">
      HEATMAP // 52-WEEK COMMIT TIMELINE
    </text>
    <text x="{width - 240}" y="0" font-family="{MONO_FAMILY}" font-size="10.5" fill="{COLOR_INK_MUTED}">
      TOTAL: <tspan font-weight="bold" fill="{COLOR_INK}">{data.get('total_contributions', 1297):,}</tspan> CONTRIBUTIONS
    </text>
  </g>

  <!-- Day Labels -->
  <g font-family="{MONO_FAMILY}" font-size="9" fill="{COLOR_INK_FAINT}">
    <text x="24" y="{start_y + 11}">Mon</text>
    <text x="24" y="{start_y + 40}">Wed</text>
    <text x="24" y="{start_y + 69}">Fri</text>
  </g>

  <!-- Grid of cells -->
  <g>
    {cells_content}
  </g>

  <!-- Legend -->
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
    <!-- Card Frame -->
    <rect x="0" y="0" width="{width}" height="{height}" rx="10" fill="{COLOR_PAPER}" stroke="{COLOR_BORDER}" stroke-width="1.5" />
    
    <!-- Left Accent Strip -->
    <rect x="0" y="0" width="5" height="{height}" rx="2" fill="{accent_color}" />

    <!-- Top Badge -->
    <rect x="24" y="22" width="140" height="20" rx="4" fill="{COLOR_PAPER_SURFACE}" stroke="{COLOR_BORDER}" stroke-width="1" />
    <text x="32" y="36" font-family="{MONO_FAMILY}" font-size="9.5" font-weight="600" fill="{accent_color}">{role_badge}</text>

    <!-- Repo Name -->
    <text x="24" y="68" font-family="{SERIF_FAMILY}" font-size="24" font-weight="700" fill="{COLOR_INK}">
      {name}
    </text>

    <!-- Description -->
    <text x="24" y="94" font-family="{SANS_FAMILY}" font-size="12.5" fill="{COLOR_INK_MUTED}">
      {description}
    </text>

    <!-- Tech Stack Pill & Arrow -->
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

    # 1. Fetch / Cache contributions
    data = fetch_contributions(USERNAME)
    print(f"[*] Total contributions: {data.get('total_contributions')}")

    # 2. Render Hero Card
    hero_svg = render_hero_card()
    with open(os.path.join(CARDS_DIR, "hero.svg"), "w", encoding="utf-8") as f:
        f.write(hero_svg)
    print("[+] Rendered cards/hero.svg")

    # 3. Render Three World Tiles
    # Tile 1: HARDWARE (Cobalt Blue)
    t1_svg = render_tile_card(
        tile_id="hardware",
        category="01 / HARDWARE &amp; IOT",
        title="HARDWARE",
        metric="12+ BOARDS &amp; CIRCUITS",
        description="RailGuard · IoT Safety · Microcontrollers",
        accent_color=COLOR_BLUE,
        delay_ms=200
    )
    with open(os.path.join(CARDS_DIR, "tile_hardware.svg"), "w", encoding="utf-8") as f:
        f.write(t1_svg)
    print("[+] Rendered cards/tile_hardware.svg")

    # Tile 2: SOFTWARE (Vermillion Red)
    t2_svg = render_tile_card(
        tile_id="software",
        category="02 / FULL-STACK &amp; APPS",
        title="SOFTWARE",
        metric="16+ REPOSITORIES",
        description="Bringo Apps · Next.js · React Native",
        accent_color=COLOR_RED,
        delay_ms=350
    )
    with open(os.path.join(CARDS_DIR, "tile_software.svg"), "w", encoding="utf-8") as f:
        f.write(t2_svg)
    print("[+] Rendered cards/tile_software.svg")

    # Tile 3: INNOVATION (Goldenrod Yellow)
    t3_svg = render_tile_card(
        tile_id="innovation",
        category="03 / SYSTEMS &amp; LABS",
        title="INNOVATION",
        metric="100% BUILDER",
        description="Startups · Practical Engineering · R&amp;D",
        accent_color=COLOR_YELLOW,
        delay_ms=500
    )
    with open(os.path.join(CARDS_DIR, "tile_innovation.svg"), "w", encoding="utf-8") as f:
        f.write(t3_svg)
    print("[+] Rendered cards/tile_innovation.svg")

    # 4. Render Monthly Contributions Chart
    chart_svg = render_contributions_chart(data)
    with open(os.path.join(CARDS_DIR, "contributions_chart.svg"), "w", encoding="utf-8") as f:
        f.write(chart_svg)
    print("[+] Rendered cards/contributions_chart.svg")

    # 5. Render Blue Contribution Graph
    graph_svg = render_contribution_graph(data)
    with open(os.path.join(CARDS_DIR, "contribution_graph.svg"), "w", encoding="utf-8") as f:
        f.write(graph_svg)
    print("[+] Rendered cards/contribution_graph.svg")

    # 6. Render Featured Repos
    repo1_svg = render_repo_card(
        name="RailGuard",
        role_badge="IOT &amp; EMBEDDED SYSTEM",
        description="Railway safety &amp; automated track collision monitoring.",
        lang="Kotlin · C++ / Arduino",
        lang_color="#A97BFF",
        accent_color=COLOR_BLUE,
        link_url="https://github.com/skmohammadali786/RailGuard"
    )
    with open(os.path.join(CARDS_DIR, "repo_railguard.svg"), "w", encoding="utf-8") as f:
        f.write(repo1_svg)
    print("[+] Rendered cards/repo_railguard.svg")

    repo2_svg = render_repo_card(
        name="Bringo Apps",
        role_badge="FULL-STACK PLATFORM",
        description="On-demand delivery agent &amp; customer mobile logistics suite.",
        lang="TypeScript · React Native",
        lang_color="#3178C6",
        accent_color=COLOR_RED,
        link_url="https://github.com/skmohammadali786/Bringo-deliveryagent-app"
    )
    with open(os.path.join(CARDS_DIR, "repo_bringo.svg"), "w", encoding="utf-8") as f:
        f.write(repo2_svg)
    print("[+] Rendered cards/repo_bringo.svg")

    print("[✔] All animated SVG cards generated successfully in cards/!")


if __name__ == "__main__":
    main()
