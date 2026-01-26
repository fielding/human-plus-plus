#!/usr/bin/env python3
"""
Human++ Build Script

Generates all theme files from palette.toml (the single source of truth).

Usage: python3 tools/build.py
"""

import re
import os
import json
from pathlib import Path

# Directory structure
ROOT = Path(__file__).parent.parent  # repo root (parent of tools/)
TOOLS = ROOT / "tools"
DIST = ROOT / "dist"
SITE = ROOT / "site"
PACKAGES = ROOT / "packages"
TINTY_DATA = Path.home() / ".local/share/tinted-theming/tinty"


def parse_palette():
    """Parse palette.toml and return color dict."""
    palette_path = ROOT / "palette.toml"
    content = palette_path.read_text()

    colors = {}
    meta = {}

    for line in content.split('\n'):
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('['):
            continue

        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()

            # Remove quotes first
            if value.startswith('"') and '"' in value[1:]:
                value = value[1:value.index('"', 1)]
            elif value.startswith("'") and "'" in value[1:]:
                value = value[1:value.index("'", 1)]

            if key in ['name', 'author', 'description']:
                meta[key] = value
            elif key.startswith('base') and value.startswith('#'):
                colors[key] = value

    return colors, meta


def hex_to_components(hex_color):
    """Convert #rrggbb to various formats."""
    hex_color = hex_color.lstrip('#')
    return {
        'hex': hex_color,
        'hex_hash': f'#{hex_color}',
        'hex_r': hex_color[0:2],
        'hex_g': hex_color[2:4],
        'hex_b': hex_color[4:6],
        'rgb_r': int(hex_color[0:2], 16),
        'rgb_g': int(hex_color[2:4], 16),
        'rgb_b': int(hex_color[4:6], 16),
        'dec_r': int(hex_color[0:2], 16) / 255.0,
        'dec_g': int(hex_color[2:4], 16) / 255.0,
        'dec_b': int(hex_color[4:6], 16) / 255.0,
        'argb': f'0xff{hex_color}',
    }


# =============================================================================
# Generators
# =============================================================================

def generate_ghostty(colors, meta):
    """Generate ghostty/config."""
    c = {k: hex_to_components(v) for k, v in colors.items()}

    content = f"""# Human++ - Base24
# Generated from palette.toml

background = {c['base00']['hex']}
foreground = {c['base07']['hex']}
cursor-color = {c['base07']['hex']}
selection-background = {c['base02']['hex']}
selection-foreground = {c['base05']['hex']}

# Normal colors (LOUD accents)
palette = 0=#{c['base00']['hex']}
palette = 1=#{c['base08']['hex']}
palette = 2=#{c['base0B']['hex']}
palette = 3=#{c['base0A']['hex']}
palette = 4=#{c['base0D']['hex']}
palette = 5=#{c['base0E']['hex']}
palette = 6=#{c['base0C']['hex']}
palette = 7=#{c['base06']['hex']}

# Bright colors (QUIET accents)
palette = 8=#{c['base03']['hex']}
palette = 9=#{c['base10']['hex']}
palette = 10=#{c['base13']['hex']}
palette = 11=#{c['base12']['hex']}
palette = 12=#{c['base15']['hex']}
palette = 13=#{c['base16']['hex']}
palette = 14=#{c['base14']['hex']}
palette = 15=#{c['base07']['hex']}
"""

    (DIST / "ghostty").mkdir(parents=True, exist_ok=True)
    (DIST / "ghostty/config").write_text(content)
    print("  ✓ dist/ghostty/config")


def generate_sketchybar(colors, meta):
    """Generate sketchybar/colors.sh."""
    c = {k: hex_to_components(v) for k, v in colors.items()}

    content = f"""#!/bin/bash
# Human++ - Base24
# Generated from palette.toml

# Base grayscale (cool)
export COLOR_BG={c['base00']['argb']}           # base00 - background
export COLOR_BG_LIGHT={c['base01']['argb']}     # base01 - elevation
export COLOR_BG_ALT={c['base02']['argb']}       # base02 - selection/panels
export COLOR_FG={c['base05']['argb']}           # base05 - main text
export COLOR_FG_DIM={c['base03']['argb']}       # base03 - comments
export COLOR_FG_SECONDARY={c['base04']['argb']} # base04 - UI secondary
export COLOR_TRANSPARENT=0x00000000

# Loud accents (diagnostics, signals)
export COLOR_RED={c['base08']['argb']}          # base08 - errors, attention
export COLOR_ORANGE={c['base09']['argb']}       # base09 - warnings
export COLOR_YELLOW={c['base0A']['argb']}       # base0A - caution
export COLOR_GREEN={c['base0B']['argb']}        # base0B - success
export COLOR_CYAN={c['base0C']['argb']}         # base0C - info
export COLOR_BLUE={c['base0D']['argb']}         # base0D - links, focus
export COLOR_PURPLE={c['base0E']['argb']}       # base0E - special
export COLOR_HUMAN={c['base0F']['argb']}        # base0F - human intent marker

# Quiet accents (UI state, less urgent)
export COLOR_RED_QUIET={c['base10']['argb']}    # base10
export COLOR_ORANGE_QUIET={c['base11']['argb']} # base11
export COLOR_YELLOW_QUIET={c['base12']['argb']} # base12
export COLOR_GREEN_QUIET={c['base13']['argb']}  # base13
export COLOR_CYAN_QUIET={c['base14']['argb']}   # base14
export COLOR_BLUE_QUIET={c['base15']['argb']}   # base15
export COLOR_PURPLE_QUIET={c['base16']['argb']} # base16

# Mode colors (using loud accents for visibility)
export MODE_DEFAULT={c['base08']['argb']}       # base08 - hot pink
export MODE_SWITCHER={c['base0B']['argb']}      # base0B - green
export MODE_SWAP={c['base0C']['argb']}          # base0C - cyan
export MODE_TREE={c['base0A']['argb']}          # base0A - amber
export MODE_LAYOUT={c['base0E']['argb']}        # base0E - purple
export MODE_MEET={c['base09']['argb']}          # base09 - orange
"""

    (DIST / "sketchybar").mkdir(parents=True, exist_ok=True)
    (DIST / "sketchybar/colors.sh").write_text(content)
    print("  ✓ dist/sketchybar/colors.sh")


def generate_borders(colors, meta):
    """Generate borders/bordersrc."""
    c = {k: hex_to_components(v) for k, v in colors.items()}

    content = f"""#!/bin/bash
# Human++ - borders config
# Generated from palette.toml

borders active_color={c['base08']['argb']} \\
        inactive_color=0x00000000 \\
        width=8.0 \\
        style=square \\
        hidpi=on
"""

    (DIST / "borders").mkdir(parents=True, exist_ok=True)
    (DIST / "borders/bordersrc").write_text(content)
    print("  ✓ dist/borders/bordersrc")


def generate_skhd(colors, meta):
    """Generate skhd/modes.sh."""
    c = {k: hex_to_components(v) for k, v in colors.items()}

    content = f"""#!/bin/bash
# Human++ - skhd mode colors
# Generated from palette.toml

export SKHD_MODE_DEFAULT={c['base08']['argb']}    # base08 - hot pink
export SKHD_MODE_SWITCHER={c['base0B']['argb']}   # base0B - green
export SKHD_MODE_SWAP={c['base0C']['argb']}       # base0C - cyan
export SKHD_MODE_TREE={c['base0A']['argb']}       # base0A - amber
export SKHD_MODE_LAYOUT={c['base0E']['argb']}     # base0E - purple
export SKHD_MODE_MEET={c['base09']['argb']}       # base09 - orange
"""

    (DIST / "skhd").mkdir(parents=True, exist_ok=True)
    (DIST / "skhd/modes.sh").write_text(content)
    print("  ✓ dist/skhd/modes.sh")


def hex_to_ansi256(hex_color):
    """Convert hex color to ANSI 256 escape code format (38;2;r;g;b for true color)."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"38;2;{r};{g};{b}"


def generate_eza(colors, meta):
    """Generate eza/colors.sh with EZA_COLORS environment variable.

    Terminal philosophy: output is intentional, use LOUD colors.
    """
    c = colors

    # Build EZA_COLORS string using true color (38;2;r;g;b format)
    # Two-letter codes: https://github.com/eza-community/eza/blob/main/man/eza_colors.5.md
    # Terminal = high signal, use LOUD palette
    eza_parts = [
        # Filetypes - LOUD colors, this is what you're looking at
        f"di={hex_to_ansi256(c['base0D'])}",        # directories - LOUD blue
        f"ln={hex_to_ansi256(c['base0C'])}",        # symlinks - LOUD cyan
        f"ex={hex_to_ansi256(c['base0B'])}",        # executables - LOUD green
        f"fi={hex_to_ansi256(c['base05'])}",        # regular files - main text
        f"pi={hex_to_ansi256(c['base0A'])}",        # pipes - LOUD amber
        f"so={hex_to_ansi256(c['base0E'])}",        # sockets - LOUD purple
        f"bd={hex_to_ansi256(c['base09'])}",        # block devices - LOUD orange
        f"cd={hex_to_ansi256(c['base09'])}",        # char devices - LOUD orange
        f"or={hex_to_ansi256(c['base08'])}",        # orphan symlinks - LOUD pink
        f"mi={hex_to_ansi256(c['base08'])}",        # missing files - LOUD pink
        # Permissions - LOUD for important, dim for less important
        f"ur={hex_to_ansi256(c['base0A'])}",        # user read - LOUD amber
        f"uw={hex_to_ansi256(c['base08'])}",        # user write - LOUD pink
        f"ux={hex_to_ansi256(c['base0B'])}",        # user exec - LOUD green
        f"ue={hex_to_ansi256(c['base0B'])}",        # user exec (other) - LOUD green
        f"gr={hex_to_ansi256(c['base04'])}",        # group read - secondary
        f"gw={hex_to_ansi256(c['base09'])}",        # group write - LOUD orange
        f"gx={hex_to_ansi256(c['base0B'])}",        # group exec - LOUD green
        f"tr={hex_to_ansi256(c['base03'])}",        # other read - dim
        f"tw={hex_to_ansi256(c['base08'])}",        # other write - LOUD pink (dangerous!)
        f"tx={hex_to_ansi256(c['base03'])}",        # other exec - dim
        # Size - LOUD colors scale with size
        f"sn={hex_to_ansi256(c['base0B'])}",        # size numbers - LOUD green
        f"sb={hex_to_ansi256(c['base04'])}",        # size unit - secondary
        # User/group
        f"uu={hex_to_ansi256(c['base0C'])}",        # current user - LOUD cyan
        f"un={hex_to_ansi256(c['base04'])}",        # other user - secondary
        f"gu={hex_to_ansi256(c['base0C'])}",        # current group - LOUD cyan
        f"gn={hex_to_ansi256(c['base04'])}",        # other group - secondary
        # Git - LOUD, git status is important
        f"ga={hex_to_ansi256(c['base0B'])}",        # git new - LOUD green
        f"gm={hex_to_ansi256(c['base0A'])}",        # git modified - LOUD amber
        f"gd={hex_to_ansi256(c['base08'])}",        # git deleted - LOUD pink
        f"gv={hex_to_ansi256(c['base0C'])}",        # git renamed - LOUD cyan
        f"gt={hex_to_ansi256(c['base03'])}",        # git ignored - dim
        # Misc
        f"da={hex_to_ansi256(c['base0E'])}",        # date - LOUD purple
        f"hd={hex_to_ansi256(c['base07'])};1",      # header - brightest + bold
        f"xx={hex_to_ansi256(c['base03'])}",        # punctuation - dim
    ]

    eza_colors = ":".join(eza_parts)

    content = f'''#!/bin/bash
# Human++ - eza colors
# Generated from palette.toml
# Source this file or add to your shell rc

export EZA_COLORS="{eza_colors}"
'''

    (DIST / "eza").mkdir(parents=True, exist_ok=True)
    (DIST / "eza/colors.sh").write_text(content)
    print("  ✓ dist/eza/colors.sh")


def generate_fzf(colors, meta):
    """Generate fzf/colors.sh with FZF_DEFAULT_OPTS.

    Terminal philosophy: output is intentional, use LOUD colors.
    """
    c = colors

    # fzf uses hex colors directly with --color flag
    # Format: --color=KEY:VALUE where VALUE is #rrggbb
    # Use LOUD colors - fzf is interactive, high signal
    fzf_colors = ",".join([
        f"bg:{c['base00']}",           # background
        f"bg+:{c['base02']}",          # selected background - more contrast
        f"fg:{c['base05']}",           # foreground
        f"fg+:{c['base07']}",          # selected foreground - brightest
        f"hl:{c['base0F']}",           # highlighted match - LOUD lime (human marker!)
        f"hl+:{c['base0F']}",          # selected highlighted - LOUD lime
        f"info:{c['base0C']}",         # info line - LOUD cyan
        f"marker:{c['base0B']}",       # marker - LOUD green
        f"prompt:{c['base08']}",       # prompt - LOUD pink
        f"spinner:{c['base0A']}",      # spinner - LOUD amber
        f"pointer:{c['base08']}",      # pointer - LOUD pink
        f"header:{c['base07']}",       # header - brightest
        f"border:{c['base0D']}",       # border - LOUD blue
        f"gutter:{c['base00']}",       # gutter
        f"query:{c['base07']}",        # query text - brightest
    ])

    content = f'''#!/bin/bash
# Human++ - fzf colors
# Generated from palette.toml
# Source this file or add to your shell rc

export FZF_DEFAULT_OPTS="$FZF_DEFAULT_OPTS --color={fzf_colors}"
'''

    (DIST / "fzf").mkdir(parents=True, exist_ok=True)
    (DIST / "fzf/colors.sh").write_text(content)
    print("  ✓ dist/fzf/colors.sh")


def generate_palette_json(colors, meta):
    """Generate site/data/palette.json for the website."""
    roles = {
        'base00': 'Background',
        'base01': 'Elevation',
        'base02': 'Selection',
        'base03': 'Comments (AI voice)',
        'base04': 'UI secondary',
        'base05': 'Main text',
        'base06': 'Emphasis',
        'base07': 'Brightest',
        'base08': 'Errors',
        'base09': 'Warnings',
        'base0A': 'Caution',
        'base0B': 'Success',
        'base0C': 'Info',
        'base0D': 'Links',
        'base0E': 'Special',
        'base0F': 'Human !!',
        'base10': 'Keywords',
        'base11': 'Secondary',
        'base12': 'Strings',
        'base13': 'Functions',
        'base14': 'Types',
        'base15': 'Hints',
        'base16': 'Constants',
        'base17': 'Quiet lime',
    }

    data = {
        'name': meta.get('name', 'Human++'),
        'author': meta.get('author', 'fielding'),
        'description': meta.get('description', 'A Base24 color scheme for the post-artisanal coding era'),
        'colors': colors,
        'roles': roles,
        'slots': {
            'grayscale': ['base00', 'base01', 'base02', 'base03', 'base04', 'base05', 'base06', 'base07'],
            'loud': ['base08', 'base09', 'base0A', 'base0B', 'base0C', 'base0D', 'base0E', 'base0F'],
            'quiet': ['base10', 'base11', 'base12', 'base13', 'base14', 'base15', 'base16', 'base17'],
        }
    }

    data_dir = SITE / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "palette.json").write_text(json.dumps(data, indent=2))
    print("  ✓ site/data/palette.json")

    # Generate meta.json with version info
    import subprocess
    from datetime import datetime, timezone

    try:
        version = subprocess.check_output(
            ['git', 'describe', '--tags', '--always'],
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        version = 'dev'

    try:
        commit = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'],
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        commit = 'unknown'

    meta_data = {
        'name': meta.get('name', 'Human++'),
        'version': version,
        'commit': commit,
        'built': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    }
    (data_dir / "meta.json").write_text(json.dumps(meta_data, indent=2))
    print("  ✓ site/data/meta.json")


def generate_site(colors, meta):
    """Generate the static site from templates."""
    SITE.mkdir(parents=True, exist_ok=True)

    # Copy the HTML template (it loads palette.json at runtime)
    template_path = ROOT / "templates" / "site" / "index.html.tmpl"
    if template_path.exists():
        content = template_path.read_text()
        (SITE / "index.html").write_text(content)
        print("  ✓ site/index.html")
    else:
        print("  ! templates/site/index.html.tmpl not found, skipping site generation")


def generate_svgs(colors, meta):
    """Generate SVG assets for README and site."""
    c = colors
    assets_dir = SITE / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    # Banner (dark mode)
    banner_dark = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 200">
  <defs>
    <linearGradient id="humanGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{c['base07']}"/>
      <stop offset="100%" style="stop-color:{c['base05']}"/>
    </linearGradient>
    <linearGradient id="plusGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{c['base0F']}"/>
      <stop offset="100%" style="stop-color:{c['base0B']}"/>
    </linearGradient>
  </defs>
  <rect width="800" height="200" fill="{c['base00']}"/>
  <text x="400" y="95" text-anchor="middle" font-family="-apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif" font-size="72" font-weight="700" letter-spacing="-3">
    <tspan fill="url(#humanGradient)">Human</tspan><tspan fill="url(#plusGradient)">++</tspan>
  </text>
  <text x="400" y="145" text-anchor="middle" font-family="-apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif" font-size="20" font-weight="300" fill="{c['base04']}">
    <tspan font-weight="500" fill="{c['base07']}">Code is cheap.</tspan>
    <tspan> Intent is scarce.</tspan>
  </text>
</svg>
'''
    (assets_dir / "banner-dark.svg").write_text(banner_dark)

    # Banner (light mode - transparent bg, inverted text)
    # Keep the ++ as lime (base0F) - it's the signature color even if contrast isn't perfect
    banner_light = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 200">
  <defs>
    <linearGradient id="humanGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{c['base00']}"/>
      <stop offset="100%" style="stop-color:{c['base02']}"/>
    </linearGradient>
    <linearGradient id="plusGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{c['base0F']}"/>
      <stop offset="100%" style="stop-color:{c['base0B']}"/>
    </linearGradient>
  </defs>
  <text x="400" y="95" text-anchor="middle" font-family="-apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif" font-size="72" font-weight="700" letter-spacing="-3">
    <tspan fill="url(#humanGradient)">Human</tspan><tspan fill="url(#plusGradient)">++</tspan>
  </text>
  <text x="400" y="145" text-anchor="middle" font-family="-apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif" font-size="20" font-weight="300" fill="{c['base03']}">
    <tspan font-weight="500" fill="{c['base00']}">Code is cheap.</tspan>
    <tspan> Intent is scarce.</tspan>
  </text>
</svg>
'''
    (assets_dir / "banner-light.svg").write_text(banner_light)
    print("  ✓ site/assets/banner-dark.svg, banner-light.svg")

    # Palette visualization (dark mode)
    palette_dark = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 320">
  <rect width="800" height="320" fill="{c['base00']}"/>

  <!-- Grayscale row -->
  <text x="24" y="35" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base04']}" letter-spacing="1">Grayscale</text>
  <rect x="24" y="48" width="88" height="56" rx="8" fill="{c['base00']}" stroke="{c['base02']}" stroke-width="1"/>
  <rect x="120" y="48" width="88" height="56" rx="8" fill="{c['base01']}"/>
  <rect x="216" y="48" width="88" height="56" rx="8" fill="{c['base02']}"/>
  <rect x="312" y="48" width="88" height="56" rx="8" fill="{c['base03']}"/>
  <rect x="408" y="48" width="88" height="56" rx="8" fill="{c['base04']}"/>
  <rect x="504" y="48" width="88" height="56" rx="8" fill="{c['base05']}"/>
  <rect x="600" y="48" width="88" height="56" rx="8" fill="{c['base06']}"/>
  <rect x="696" y="48" width="88" height="56" rx="8" fill="{c['base07']}"/>

  <text x="68" y="82" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base07']}" text-anchor="middle">00</text>
  <text x="164" y="82" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base07']}" text-anchor="middle">01</text>
  <text x="260" y="82" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base07']}" text-anchor="middle">02</text>
  <text x="356" y="82" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base07']}" text-anchor="middle">03</text>
  <text x="452" y="82" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">04</text>
  <text x="548" y="82" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">05</text>
  <text x="644" y="82" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">06</text>
  <text x="740" y="82" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">07</text>

  <!-- Loud Accents row -->
  <text x="24" y="135" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base04']}" letter-spacing="1">Loud Accents — Diagnostics</text>
  <rect x="24" y="148" width="88" height="56" rx="8" fill="{c['base08']}"/>
  <rect x="120" y="148" width="88" height="56" rx="8" fill="{c['base09']}"/>
  <rect x="216" y="148" width="88" height="56" rx="8" fill="{c['base0A']}"/>
  <rect x="312" y="148" width="88" height="56" rx="8" fill="{c['base0B']}"/>
  <rect x="408" y="148" width="88" height="56" rx="8" fill="{c['base0C']}"/>
  <rect x="504" y="148" width="88" height="56" rx="8" fill="{c['base0D']}"/>
  <rect x="600" y="148" width="88" height="56" rx="8" fill="{c['base0E']}"/>
  <rect x="696" y="148" width="88" height="56" rx="8" fill="{c['base0F']}"/>

  <text x="68" y="182" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">08</text>
  <text x="164" y="182" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">09</text>
  <text x="260" y="182" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">0A</text>
  <text x="356" y="182" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">0B</text>
  <text x="452" y="182" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">0C</text>
  <text x="548" y="182" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base07']}" text-anchor="middle">0D</text>
  <text x="644" y="182" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base07']}" text-anchor="middle">0E</text>
  <text x="740" y="182" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">0F</text>

  <!-- Quiet Accents row -->
  <text x="24" y="235" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base04']}" letter-spacing="1">Quiet Accents — Syntax</text>
  <rect x="24" y="248" width="88" height="56" rx="8" fill="{c['base10']}"/>
  <rect x="120" y="248" width="88" height="56" rx="8" fill="{c['base11']}"/>
  <rect x="216" y="248" width="88" height="56" rx="8" fill="{c['base12']}"/>
  <rect x="312" y="248" width="88" height="56" rx="8" fill="{c['base13']}"/>
  <rect x="408" y="248" width="88" height="56" rx="8" fill="{c['base14']}"/>
  <rect x="504" y="248" width="88" height="56" rx="8" fill="{c['base15']}"/>
  <rect x="600" y="248" width="88" height="56" rx="8" fill="{c['base16']}"/>
  <rect x="696" y="248" width="88" height="56" rx="8" fill="{c['base17']}"/>

  <text x="68" y="282" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">10</text>
  <text x="164" y="282" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">11</text>
  <text x="260" y="282" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">12</text>
  <text x="356" y="282" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">13</text>
  <text x="452" y="282" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">14</text>
  <text x="548" y="282" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base07']}" text-anchor="middle">15</text>
  <text x="644" y="282" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base07']}" text-anchor="middle">16</text>
  <text x="740" y="282" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">17</text>
</svg>
'''
    (assets_dir / "palette-dark.svg").write_text(palette_dark)

    # Palette visualization (light mode - transparent bg)
    palette_light = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 320">
  <!-- Grayscale row -->
  <text x="24" y="35" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base03']}" letter-spacing="1">Grayscale</text>
  <rect x="24" y="48" width="88" height="56" rx="8" fill="{c['base00']}"/>
  <rect x="120" y="48" width="88" height="56" rx="8" fill="{c['base01']}"/>
  <rect x="216" y="48" width="88" height="56" rx="8" fill="{c['base02']}"/>
  <rect x="312" y="48" width="88" height="56" rx="8" fill="{c['base03']}"/>
  <rect x="408" y="48" width="88" height="56" rx="8" fill="{c['base04']}"/>
  <rect x="504" y="48" width="88" height="56" rx="8" fill="{c['base05']}"/>
  <rect x="600" y="48" width="88" height="56" rx="8" fill="{c['base06']}"/>
  <rect x="696" y="48" width="88" height="56" rx="8" fill="{c['base07']}" stroke="{c['base04']}" stroke-width="1"/>

  <text x="68" y="82" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base07']}" text-anchor="middle">00</text>
  <text x="164" y="82" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base07']}" text-anchor="middle">01</text>
  <text x="260" y="82" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base07']}" text-anchor="middle">02</text>
  <text x="356" y="82" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base07']}" text-anchor="middle">03</text>
  <text x="452" y="82" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">04</text>
  <text x="548" y="82" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">05</text>
  <text x="644" y="82" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">06</text>
  <text x="740" y="82" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">07</text>

  <!-- Loud Accents row -->
  <text x="24" y="135" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base03']}" letter-spacing="1">Loud Accents — Diagnostics</text>
  <rect x="24" y="148" width="88" height="56" rx="8" fill="{c['base08']}"/>
  <rect x="120" y="148" width="88" height="56" rx="8" fill="{c['base09']}"/>
  <rect x="216" y="148" width="88" height="56" rx="8" fill="{c['base0A']}"/>
  <rect x="312" y="148" width="88" height="56" rx="8" fill="{c['base0B']}"/>
  <rect x="408" y="148" width="88" height="56" rx="8" fill="{c['base0C']}"/>
  <rect x="504" y="148" width="88" height="56" rx="8" fill="{c['base0D']}"/>
  <rect x="600" y="148" width="88" height="56" rx="8" fill="{c['base0E']}"/>
  <rect x="696" y="148" width="88" height="56" rx="8" fill="{c['base0F']}"/>

  <text x="68" y="182" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">08</text>
  <text x="164" y="182" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">09</text>
  <text x="260" y="182" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">0A</text>
  <text x="356" y="182" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">0B</text>
  <text x="452" y="182" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">0C</text>
  <text x="548" y="182" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base07']}" text-anchor="middle">0D</text>
  <text x="644" y="182" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base07']}" text-anchor="middle">0E</text>
  <text x="740" y="182" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">0F</text>

  <!-- Quiet Accents row -->
  <text x="24" y="235" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base03']}" letter-spacing="1">Quiet Accents — Syntax</text>
  <rect x="24" y="248" width="88" height="56" rx="8" fill="{c['base10']}"/>
  <rect x="120" y="248" width="88" height="56" rx="8" fill="{c['base11']}"/>
  <rect x="216" y="248" width="88" height="56" rx="8" fill="{c['base12']}"/>
  <rect x="312" y="248" width="88" height="56" rx="8" fill="{c['base13']}"/>
  <rect x="408" y="248" width="88" height="56" rx="8" fill="{c['base14']}"/>
  <rect x="504" y="248" width="88" height="56" rx="8" fill="{c['base15']}"/>
  <rect x="600" y="248" width="88" height="56" rx="8" fill="{c['base16']}"/>
  <rect x="696" y="248" width="88" height="56" rx="8" fill="{c['base17']}"/>

  <text x="68" y="282" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">10</text>
  <text x="164" y="282" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">11</text>
  <text x="260" y="282" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">12</text>
  <text x="356" y="282" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">13</text>
  <text x="452" y="282" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">14</text>
  <text x="548" y="282" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base07']}" text-anchor="middle">15</text>
  <text x="644" y="282" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base07']}" text-anchor="middle">16</text>
  <text x="740" y="282" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" text-anchor="middle">17</text>
</svg>
'''
    (assets_dir / "palette-light.svg").write_text(palette_light)
    print("  ✓ site/assets/palette-dark.svg, palette-light.svg")

    # Code preview (dark mode)
    preview_dark = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 340">
  <rect width="680" height="340" rx="10" fill="{c['base00']}"/>

  <!-- Title bar -->
  <rect width="680" height="36" rx="10" fill="{c['base01']}"/>
  <rect y="26" width="680" height="10" fill="{c['base01']}"/>
  <circle cx="20" cy="18" r="6" fill="{c['base08']}"/>
  <circle cx="40" cy="18" r="6" fill="{c['base0A']}"/>
  <circle cx="60" cy="18" r="6" fill="{c['base0B']}"/>
  <text x="340" y="23" text-anchor="middle" font-family="SF Mono, Consolas, monospace" font-size="12" fill="{c['base04']}">user-service.ts</text>

  <!-- Line numbers -->
  <text x="28" y="68" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base03']}" text-anchor="end">1</text>
  <text x="28" y="92" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base03']}" text-anchor="end">2</text>
  <text x="28" y="116" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base03']}" text-anchor="end">3</text>
  <text x="28" y="140" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base03']}" text-anchor="end">4</text>
  <text x="28" y="164" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base03']}" text-anchor="end">5</text>
  <text x="28" y="188" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base03']}" text-anchor="end">6</text>
  <text x="28" y="212" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base03']}" text-anchor="end">7</text>
  <text x="28" y="236" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base03']}" text-anchor="end">8</text>
  <text x="28" y="260" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base03']}" text-anchor="end">9</text>
  <text x="28" y="284" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base03']}" text-anchor="end">10</text>
  <text x="28" y="308" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base03']}" text-anchor="end">11</text>

  <!-- Line 1: interface User {{ -->
  <text x="44" y="68" font-family="SF Mono, Consolas, monospace" font-size="13">
    <tspan fill="{c['base10']}">interface</tspan>
    <tspan fill="{c['base05']}"> </tspan>
    <tspan fill="{c['base14']}">User</tspan>
    <tspan fill="{c['base05']}"> {{</tspan>
  </text>

  <!-- Line 2: id: string; -->
  <text x="44" y="92" font-family="SF Mono, Consolas, monospace" font-size="13">
    <tspan fill="{c['base05']}">  id: </tspan>
    <tspan fill="{c['base14']}">string</tspan>
    <tspan fill="{c['base05']}">;</tspan>
  </text>

  <!-- Line 3: }} -->
  <text x="44" y="116" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base05']}">}}</text>

  <!-- Line 5: !! marker -->
  <rect x="40" y="150" width="596" height="22" rx="4" fill="{c['base0F']}"/>
  <text x="44" y="164" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base00']}" font-weight="bold">// !! Critical: rate limiting depends on this cache format</text>

  <!-- Line 6: async function -->
  <text x="44" y="188" font-family="SF Mono, Consolas, monospace" font-size="13">
    <tspan fill="{c['base10']}">async function</tspan>
    <tspan fill="{c['base05']}"> </tspan>
    <tspan fill="{c['base13']}">getUser</tspan>
    <tspan fill="{c['base05']}">(id: </tspan>
    <tspan fill="{c['base14']}">string</tspan>
    <tspan fill="{c['base05']}">): </tspan>
    <tspan fill="{c['base14']}">Promise</tspan>
    <tspan fill="{c['base05']}">&lt;</tspan>
    <tspan fill="{c['base14']}">User</tspan>
    <tspan fill="{c['base05']}">&gt; {{</tspan>
  </text>

  <!-- Line 7: const cached -->
  <text x="44" y="212" font-family="SF Mono, Consolas, monospace" font-size="13">
    <tspan fill="{c['base05']}">  </tspan>
    <tspan fill="{c['base10']}">const</tspan>
    <tspan fill="{c['base05']}"> cached = </tspan>
    <tspan fill="{c['base10']}">await</tspan>
    <tspan fill="{c['base05']}"> redis.</tspan>
    <tspan fill="{c['base13']}">get</tspan>
    <tspan fill="{c['base05']}">(</tspan>
    <tspan fill="{c['base12']}">`user:</tspan>
    <tspan fill="{c['base05']}">${{id}}</tspan>
    <tspan fill="{c['base12']}">`</tspan>
    <tspan fill="{c['base05']}">);</tspan>
  </text>

  <!-- Line 8: ?? marker -->
  <rect x="40" y="222" width="380" height="22" rx="4" fill="{c['base0E']}"/>
  <text x="44" y="236" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base07']}" font-weight="bold">  // ?? Should we add retry logic here?</text>

  <!-- Line 9: return -->
  <text x="44" y="260" font-family="SF Mono, Consolas, monospace" font-size="13">
    <tspan fill="{c['base05']}">  </tspan>
    <tspan fill="{c['base10']}">return</tspan>
    <tspan fill="{c['base05']}"> cached;</tspan>
  </text>

  <!-- Line 10: }} -->
  <text x="44" y="284" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base05']}">}}</text>

  <!-- Line 11: error -->
  <text x="44" y="308" font-family="SF Mono, Consolas, monospace" font-size="13">
    <tspan fill="{c['base05']}">user.</tspan>
    <tspan fill="{c['base05']}">name</tspan>
    <tspan fill="{c['base05']}"> = </tspan>
    <tspan fill="{c['base16']}">null</tspan>
    <tspan fill="{c['base05']}">;</tspan>
  </text>
  <rect x="180" y="294" width="290" height="20" rx="4" fill="{c['base08']}"/>
  <text x="188" y="308" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base00']}" font-weight="600">Type 'null' is not assignable to 'string'</text>
</svg>
'''
    (assets_dir / "preview-dark.svg").write_text(preview_dark)

    # Code preview (light mode)
    preview_light = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 340">
  <rect width="680" height="340" rx="10" fill="{c['base07']}" stroke="{c['base04']}" stroke-width="1"/>

  <!-- Title bar -->
  <rect width="680" height="36" rx="10" fill="{c['base06']}"/>
  <rect y="26" width="680" height="10" fill="{c['base06']}"/>
  <circle cx="20" cy="18" r="6" fill="{c['base08']}"/>
  <circle cx="40" cy="18" r="6" fill="{c['base0A']}"/>
  <circle cx="60" cy="18" r="6" fill="{c['base0B']}"/>
  <text x="340" y="23" text-anchor="middle" font-family="SF Mono, Consolas, monospace" font-size="12" fill="{c['base03']}">user-service.ts</text>

  <!-- Line numbers -->
  <text x="28" y="68" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base04']}" text-anchor="end">1</text>
  <text x="28" y="92" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base04']}" text-anchor="end">2</text>
  <text x="28" y="116" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base04']}" text-anchor="end">3</text>
  <text x="28" y="140" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base04']}" text-anchor="end">4</text>
  <text x="28" y="164" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base04']}" text-anchor="end">5</text>
  <text x="28" y="188" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base04']}" text-anchor="end">6</text>
  <text x="28" y="212" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base04']}" text-anchor="end">7</text>
  <text x="28" y="236" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base04']}" text-anchor="end">8</text>
  <text x="28" y="260" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base04']}" text-anchor="end">9</text>
  <text x="28" y="284" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base04']}" text-anchor="end">10</text>
  <text x="28" y="308" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base04']}" text-anchor="end">11</text>

  <!-- Line 1: interface User {{ -->
  <text x="44" y="68" font-family="SF Mono, Consolas, monospace" font-size="13">
    <tspan fill="{c['base10']}">interface</tspan>
    <tspan fill="{c['base00']}"> </tspan>
    <tspan fill="{c['base15']}">User</tspan>
    <tspan fill="{c['base00']}"> {{</tspan>
  </text>

  <!-- Line 2: id: string; -->
  <text x="44" y="92" font-family="SF Mono, Consolas, monospace" font-size="13">
    <tspan fill="{c['base00']}">  id: </tspan>
    <tspan fill="{c['base15']}">string</tspan>
    <tspan fill="{c['base00']}">;</tspan>
  </text>

  <!-- Line 3: }} -->
  <text x="44" y="116" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base00']}">}}</text>

  <!-- Line 5: !! marker -->
  <rect x="40" y="150" width="596" height="22" rx="4" fill="{c['base0B']}"/>
  <text x="44" y="164" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base00']}" font-weight="bold">// !! Critical: rate limiting depends on this cache format</text>

  <!-- Line 6: async function -->
  <text x="44" y="188" font-family="SF Mono, Consolas, monospace" font-size="13">
    <tspan fill="{c['base10']}">async function</tspan>
    <tspan fill="{c['base00']}"> </tspan>
    <tspan fill="{c['base0B']}">getUser</tspan>
    <tspan fill="{c['base00']}">(id: </tspan>
    <tspan fill="{c['base15']}">string</tspan>
    <tspan fill="{c['base00']}">): </tspan>
    <tspan fill="{c['base15']}">Promise</tspan>
    <tspan fill="{c['base00']}">&lt;</tspan>
    <tspan fill="{c['base15']}">User</tspan>
    <tspan fill="{c['base00']}">&gt; {{</tspan>
  </text>

  <!-- Line 7: const cached -->
  <text x="44" y="212" font-family="SF Mono, Consolas, monospace" font-size="13">
    <tspan fill="{c['base00']}">  </tspan>
    <tspan fill="{c['base10']}">const</tspan>
    <tspan fill="{c['base00']}"> cached = </tspan>
    <tspan fill="{c['base10']}">await</tspan>
    <tspan fill="{c['base00']}"> redis.</tspan>
    <tspan fill="{c['base0B']}">get</tspan>
    <tspan fill="{c['base00']}">(</tspan>
    <tspan fill="{c['base09']}">`user:</tspan>
    <tspan fill="{c['base00']}">${{id}}</tspan>
    <tspan fill="{c['base09']}">`</tspan>
    <tspan fill="{c['base00']}">);</tspan>
  </text>

  <!-- Line 8: ?? marker -->
  <rect x="40" y="222" width="380" height="22" rx="4" fill="{c['base0E']}"/>
  <text x="44" y="236" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base07']}" font-weight="bold">  // ?? Should we add retry logic here?</text>

  <!-- Line 9: return -->
  <text x="44" y="260" font-family="SF Mono, Consolas, monospace" font-size="13">
    <tspan fill="{c['base00']}">  </tspan>
    <tspan fill="{c['base10']}">return</tspan>
    <tspan fill="{c['base00']}"> cached;</tspan>
  </text>

  <!-- Line 10: }} -->
  <text x="44" y="284" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base00']}">}}</text>

  <!-- Line 11: error -->
  <text x="44" y="308" font-family="SF Mono, Consolas, monospace" font-size="13">
    <tspan fill="{c['base00']}">user.</tspan>
    <tspan fill="{c['base00']}">name</tspan>
    <tspan fill="{c['base00']}"> = </tspan>
    <tspan fill="{c['base0E']}">null</tspan>
    <tspan fill="{c['base00']}">;</tspan>
  </text>
  <rect x="180" y="294" width="290" height="20" rx="4" fill="{c['base08']}"/>
  <text x="188" y="308" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base07']}" font-weight="600">Type 'null' is not assignable to 'string'</text>
</svg>
'''
    (assets_dir / "preview-light.svg").write_text(preview_light)
    print("  ✓ site/assets/preview-dark.svg, preview-light.svg")



def generate_readme(colors, meta):
    """Generate README.md."""
    c = colors

    content = f'''<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="site/assets/banner-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="site/assets/banner-light.svg">
    <img src="site/assets/banner-dark.svg" alt="Human++ - Code is cheap. Intent is scarce." width="600">
  </picture>
</p>

<p align="center">
  A Base24 color scheme for the post-artisanal coding era.
</p>

<p align="center">
  <a href="https://fielding.github.io/human-plus-plus/">Website</a> •
  <a href="#install">Install</a> •
  <a href="#the-palette">Palette</a> •
  <a href="#human-intent-markers">Markers</a>
</p>

---

As models write more code, humans spend more time reviewing, planning, and explaining intent. Human++ makes human judgment visible at a glance through a two-tier accent system and lightweight annotation markers.

<p align="center">
  <img src="site/assets/preview-dark.svg" alt="Human++ Theme Preview" width="650">
</p>

## Philosophy

Human++ inverts the traditional syntax highlighting priority:

- **Quiet syntax** — everyday code fades into the background
- **Loud diagnostics** — errors, warnings, and human markers demand attention
- **Terminal exception** — terminal output is intentional, so terminals get loud colors

The result: when you see color, it means something.

## The Palette

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="site/assets/palette-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="site/assets/palette-light.svg">
    <img src="site/assets/palette-dark.svg" alt="Human++ Palette" width="700">
  </picture>
</p>

Human++ uses a cool charcoal grayscale with warm cream text and a full Base24 palette:

- **base00–07** — Cool grayscale from charcoal to warm cream
- **base08–0F** — Loud accents for diagnostics and signals
- **base10–17** — Quiet accents for syntax and UI

<details>
<summary>Full palette reference</summary>

### Grayscale

| Slot | Hex | Role |
|------|-----|------|
| base00 | `{c['base00']}` | Background |
| base01 | `{c['base01']}` | Elevation |
| base02 | `{c['base02']}` | Selection |
| base03 | `{c['base03']}` | Comments |
| base04 | `{c['base04']}` | UI secondary |
| base05 | `{c['base05']}` | Main text |
| base06 | `{c['base06']}` | Emphasis |
| base07 | `{c['base07']}` | Brightest |

### Loud Accents (Diagnostics & Signals)

| Slot | Hex | Role |
|------|-----|------|
| base08 | `{c['base08']}` | Errors, attention |
| base09 | `{c['base09']}` | Warnings |
| base0A | `{c['base0A']}` | Caution |
| base0B | `{c['base0B']}` | Success |
| base0C | `{c['base0C']}` | Info |
| base0D | `{c['base0D']}` | Links, focus |
| base0E | `{c['base0E']}` | Special |
| base0F | `{c['base0F']}` | Human intent marker |

### Quiet Accents (Syntax & UI)

| Slot | Hex | Role |
|------|-----|------|
| base10 | `{c['base10']}` | Keywords |
| base11 | `{c['base11']}` | Secondary |
| base12 | `{c['base12']}` | Strings |
| base13 | `{c['base13']}` | Functions |
| base14 | `{c['base14']}` | Types |
| base15 | `{c['base15']}` | Hints |
| base16 | `{c['base16']}` | Constants |
| base17 | `{c['base17']}` | Quiet lime |

</details>

## Human Intent Markers

Use punctuation markers in comments to flag human judgment:

| Marker | Meaning | Color |
|--------|---------|-------|
| `!!` | Pay attention here | Lime (base0F) |
| `??` | I'm uncertain | Purple (base0E) |
| `>>` | See reference | Cyan (base0C) |

```js
// Regular comment stays calm (base03)

// !! Critical: don't change without talking to Sarah
if (legacyMode) {{
  // ?? Not sure this handles the edge case
  return transformLegacy(data);
}}

// >> See utils.ts for the transform logic
return transform(data);
```

### Why punctuation?

- Fast to type
- Easy to scan
- Easy to grep: `rg "// !!|// \\?\\?|// >>"`
- Easy for editors to highlight

## Install

### VS Code / Cursor (Recommended)

The VS Code extension includes the full theme plus **marker highlighting** and **inline diagnostics**:

```bash
# Build and install from source
cd packages/vscode-extension
npm install && npx @vscode/vsce package
code --install-extension human-plus-plus-1.0.0.vsix
```

Or download `human-plus-plus-*.vsix` from [Releases](https://github.com/fielding/human-plus-plus/releases).

**Features:**
- Color theme with quiet syntax + loud diagnostics
- Marker highlighting (`!!`, `??`, `>>`) with colored backgrounds
- Inline diagnostic badges for errors/warnings

### Other Apps

All theme files are generated from `palette.toml`:

```bash
git clone https://github.com/fielding/human-plus-plus
cd human-plus-plus
make build    # Generate all themes
make apply    # Apply to installed apps
```

| App | Location |
|-----|----------|
| Ghostty | `dist/ghostty/config` |
| Vim / Neovim | via tinty |
| Sketchybar | `dist/sketchybar/colors.sh` |
| JankyBorders | `dist/borders/bordersrc` |
| skhd | `dist/skhd/modes.sh` |

### With tinty

```bash
tinty apply base24-human-plus-plus
```

## Development

```bash
make build          # Build all theme files
make preview        # Preview palette in terminal
make colortest      # Display terminal ANSI mapping
make apply-dry      # Preview what apply would do
make analyze        # Analyze palette in OKLCH
```

### Repository Structure

```
palette.toml          # Single source of truth (edit this)
templates/            # Theme templates
tools/                # Python generators
scripts/              # Shell orchestration
site/assets/          # Logos and images
```

**Generated (gitignored):**
```
dist/                 # Theme outputs
site/data/            # Palette JSON
```

## License

MIT
'''

    (ROOT / "README.md").write_text(content)
    print("  ✓ README.md")


def generate_colortest(colors, meta):
    """Generate colortest.sh with current palette values."""
    c = colors

    content = f'''#!/usr/bin/env bash
# Human++ Color Test
# Displays the current terminal palette and Human++ color values
# Generated from palette.toml

# Force bash 4+ features
if [ -z "$BASH_VERSION" ] || [ "${{BASH_VERSINFO[0]}}" -lt 4 ]; then
    echo "This script requires bash 4.0 or later"
    exit 1
fi

cat << 'HEADER'

  ╔═══════════════════════════════════════════════════════════════════╗
  ║                       Human++                       ║
  ║           Code is cheap. Intent is scarce.                        ║
  ╚═══════════════════════════════════════════════════════════════════╝

HEADER

# Display ANSI 0-15 (what your terminal actually shows)
echo "  ┌─────────────────────────────────────────────────────────────────┐"
echo "  │  TERMINAL ANSI COLORS (0-15)                                    │"
echo "  └─────────────────────────────────────────────────────────────────┘"
echo ""
echo -n "   Normal:  "
for i in 0 1 2 3 4 5 6 7; do
  printf "\\033[48;5;${{i}}m   \\033[0m"
done
echo ""
echo -n "   Bright:  "
for i in 8 9 10 11 12 13 14 15; do
  printf "\\033[48;5;${{i}}m   \\033[0m"
done
echo ""
echo ""

# Detailed view
echo "  ┌─────────────────────────────────────────────────────────────────┐"
echo "  │  ANSI TO BASE24 MAPPING                                         │"
echo "  └─────────────────────────────────────────────────────────────────┘"
echo ""
printf "   %-5s %-12s %-8s %-10s %s\\n" "ANSI" "Name" "Slot" "Hex" ""
printf "   %-5s %-12s %-8s %-10s %s\\n" "────" "────" "────" "───" ""

# ANSI to base24 mapping (Human++ terminal style: LOUD normal, QUIET bright)
print_row() {{
  local ansi=$1 name=$2 slot=$3 hex=$4
  printf "   %-5s %-12s %-8s %-10s \\033[48;5;${{ansi}}m      \\033[0m\\n" "$ansi" "$name" "$slot" "$hex"
}}

print_row 0  "Black"       "base00" "{c['base00']}"
print_row 1  "Red"         "base08" "{c['base08']}"
print_row 2  "Green"       "base0B" "{c['base0B']}"
print_row 3  "Yellow"      "base0A" "{c['base0A']}"
print_row 4  "Blue"        "base0D" "{c['base0D']}"
print_row 5  "Magenta"     "base0E" "{c['base0E']}"
print_row 6  "Cyan"        "base0C" "{c['base0C']}"
print_row 7  "White"       "base06" "{c['base06']}"
print_row 8  "Br.Black"    "base03" "{c['base03']}"
print_row 9  "Br.Red"      "base10" "{c['base10']}"
print_row 10 "Br.Green"    "base13" "{c['base13']}"
print_row 11 "Br.Yellow"   "base12" "{c['base12']}"
print_row 12 "Br.Blue"     "base15" "{c['base15']}"
print_row 13 "Br.Magenta"  "base16" "{c['base16']}"
print_row 14 "Br.Cyan"     "base14" "{c['base14']}"
print_row 15 "Br.White"    "base07" "{c['base07']}"
echo ""

# Full palette reference
echo "  ┌─────────────────────────────────────────────────────────────────┐"
echo "  │  HUMAN++ FULL PALETTE                                           │"
echo "  └─────────────────────────────────────────────────────────────────┘"
echo ""
echo "   GRAYSCALE"
printf "   base00 {c['base00']} background    base04 {c['base04']} UI secondary\\n"
printf "   base01 {c['base01']} elevation     base05 {c['base05']} main text\\n"
printf "   base02 {c['base02']} selection     base06 {c['base06']} emphasis\\n"
printf "   base03 {c['base03']} comments      base07 {c['base07']} brightest\\n"
echo ""
echo "   LOUD ACCENTS — Diagnostics & Signals"
printf "   base08 {c['base08']} errors        base0C {c['base0C']} info\\n"
printf "   base09 {c['base09']} warnings      base0D {c['base0D']} links\\n"
printf "   base0A {c['base0A']} caution       base0E {c['base0E']} special\\n"
printf "   base0B {c['base0B']} success       base0F {c['base0F']} human !!\\n"
echo ""
echo "   QUIET ACCENTS — Syntax & UI"
printf "   base10 {c['base10']} keywords      base14 {c['base14']} types\\n"
printf "   base11 {c['base11']} secondary     base15 {c['base15']} hints\\n"
printf "   base12 {c['base12']} strings       base16 {c['base16']} constants\\n"
printf "   base13 {c['base13']} functions     base17 {c['base17']} quiet lime\\n"
echo ""

# Visual comparison
echo "  ┌─────────────────────────────────────────────────────────────────┐"
echo "  │  LOUD vs QUIET COMPARISON                                       │"
echo "  └─────────────────────────────────────────────────────────────────┘"
echo ""
echo -n "   Loud:   "
for i in 1 3 2 4 5 6; do
  printf "\\033[48;5;${{i}}m    \\033[0m"
done
echo "  ← base08-0E (LOUD)"

echo -n "   Quiet:  "
for i in 9 11 10 12 13 14; do
  printf "\\033[48;5;${{i}}m    \\033[0m"
done
echo "  ← base10-16 (quiet)"
echo ""

# Base24 color blocks (true color)
echo "  ┌─────────────────────────────────────────────────────────────────┐"
echo "  │  ALL 24 BASE24 COLORS (true color)                              │"
echo "  └─────────────────────────────────────────────────────────────────┘"
echo ""

# Helper for true color swatch
tc_swatch() {{
  local hex=$1
  local r=$((16#${{hex:1:2}}))
  local g=$((16#${{hex:3:2}}))
  local b=$((16#${{hex:5:2}}))
  printf "\\033[48;2;%d;%d;%dm       \\033[0m" "$r" "$g" "$b"
}}

echo "   Grayscale (base00-07)"
echo -n "   "
for hex in "{c['base00']}" "{c['base01']}" "{c['base02']}" "{c['base03']}" "{c['base04']}" "{c['base05']}" "{c['base06']}" "{c['base07']}"; do
  tc_swatch "$hex"
done
echo ""
echo -n "   "
for hex in "{c['base00']}" "{c['base01']}" "{c['base02']}" "{c['base03']}" "{c['base04']}" "{c['base05']}" "{c['base06']}" "{c['base07']}"; do
  tc_swatch "$hex"
done
echo ""
echo ""

echo "   Loud Accents (base08-0F)"
echo -n "   "
for hex in "{c['base08']}" "{c['base09']}" "{c['base0A']}" "{c['base0B']}" "{c['base0C']}" "{c['base0D']}" "{c['base0E']}" "{c['base0F']}"; do
  tc_swatch "$hex"
done
echo ""
echo -n "   "
for hex in "{c['base08']}" "{c['base09']}" "{c['base0A']}" "{c['base0B']}" "{c['base0C']}" "{c['base0D']}" "{c['base0E']}" "{c['base0F']}"; do
  tc_swatch "$hex"
done
echo ""
echo ""

echo "   Quiet Accents (base10-17)"
echo -n "   "
for hex in "{c['base10']}" "{c['base11']}" "{c['base12']}" "{c['base13']}" "{c['base14']}" "{c['base15']}" "{c['base16']}" "{c['base17']}"; do
  tc_swatch "$hex"
done
echo ""
echo -n "   "
for hex in "{c['base10']}" "{c['base11']}" "{c['base12']}" "{c['base13']}" "{c['base14']}" "{c['base15']}" "{c['base16']}" "{c['base17']}"; do
  tc_swatch "$hex"
done
echo ""
'''

    (DIST / "scripts").mkdir(parents=True, exist_ok=True)
    (DIST / "scripts/colortest.sh").write_text(content)
    os.chmod(DIST / "scripts/colortest.sh", 0o755)
    print("  ✓ dist/scripts/colortest.sh")


def generate_base24_yaml(colors, meta):
    """Generate human-plus-plus.yaml (Base24 registry format)."""
    # Order colors properly
    grayscale = [f'base0{i}' for i in range(8)]
    loud = ['base08', 'base09', 'base0A', 'base0B', 'base0C', 'base0D', 'base0E', 'base0F']
    quiet = ['base10', 'base11', 'base12', 'base13', 'base14', 'base15', 'base16', 'base17']

    lines = [
        'system: "base24"',
        f'name: "{meta.get("name", "Human++")}"',
        f'author: "{meta.get("author", "fielding")}"',
        'variant: "dark"',
        'palette:',
    ]

    # Grayscale
    lines.append('  # Cool gray base')
    for slot in grayscale:
        lines.append(f'  {slot}: "{colors[slot]}"')

    # Loud accents
    lines.append('  # Loud accents (diagnostics, signals)')
    for slot in loud:
        lines.append(f'  {slot}: "{colors[slot]}"')

    # Quiet accents
    lines.append('  # Quiet accents (syntax, UI state)')
    for slot in quiet:
        lines.append(f'  {slot}: "{colors[slot]}"')

    content = '\n'.join(lines) + '\n'
    (DIST / "base24").mkdir(parents=True, exist_ok=True)
    (DIST / "base24/human-plus-plus.yaml").write_text(content)
    print("  ✓ dist/base24/human-plus-plus.yaml")


def generate_tinty_themes(colors, meta):
    """Generate tinty theme files."""
    c = {k: hex_to_components(v) for k, v in colors.items()}

    # Build template vars
    vars = {
        'scheme-name': meta.get('name', 'Human++'),
        'scheme-author': meta.get('author', 'fielding'),
        'scheme-slug': 'human-plus-plus',
        'scheme-system': 'base24',
    }

    for key, value in colors.items():
        comps = hex_to_components(value)
        vars[f'{key}-hex'] = comps['hex']
        vars[f'{key}-hex-r'] = comps['hex_r']
        vars[f'{key}-hex-g'] = comps['hex_g']
        vars[f'{key}-hex-b'] = comps['hex_b']
        vars[f'{key}-rgb-r'] = comps['rgb_r']
        vars[f'{key}-rgb-g'] = comps['rgb_g']
        vars[f'{key}-rgb-b'] = comps['rgb_b']
        vars[f'{key}-dec-r'] = comps['dec_r']
        vars[f'{key}-dec-g'] = comps['dec_g']
        vars[f'{key}-dec-b'] = comps['dec_b']

    def render_mustache(template_content):
        result = template_content
        for key, value in vars.items():
            result = result.replace('{{' + key + '}}', str(value))
            result = result.replace('{{ ' + key + ' }}', str(value))
        return result

    # Shell
    shell_template = TINTY_DATA / "repos/tinted-shell/templates/base24.mustache"
    shell_output = TINTY_DATA / "repos/tinted-shell/scripts/base24-human-plus-plus.sh"
    if shell_template.exists():
        output = render_mustache(shell_template.read_text())
        shell_output.write_text(output)
        os.chmod(shell_output, 0o755)

        # Also copy to local dist
        (DIST / "base24").mkdir(parents=True, exist_ok=True)
        (DIST / "base24/base24-human-plus-plus.sh").write_text(output)
        print("  ✓ dist/base24/base24-human-plus-plus.sh")

    # Vim
    vim_template = TINTY_DATA / "repos/tinted-vim/templates/tinted-vim.mustache"
    vim_output = TINTY_DATA / "repos/tinted-vim/colors/base24-human-plus-plus.vim"
    if vim_template.exists():
        output = render_mustache(vim_template.read_text())
        vim_output.write_text(output)
        print("  ✓ tinty vim theme")

    # Ghostty (for tinty)
    ghostty_template = TINTY_DATA / "repos/tinted-ghostty/templates/base24.mustache"
    ghostty_output = TINTY_DATA / "repos/tinted-ghostty/themes/base24-human-plus-plus"
    if ghostty_template.exists():
        output = render_mustache(ghostty_template.read_text())
        # Customize foreground to base07
        output = output.replace(
            f"foreground = {vars['base05-hex']}",
            f"foreground = {vars['base07-hex']}"
        )
        output = output.replace(
            f"cursor-color = {vars['base05-hex']}",
            f"cursor-color = {vars['base07-hex']}"
        )
        ghostty_output.write_text(output)
        print("  ✓ tinty ghostty theme")


def generate_vscode_theme(colors, meta):
    """Generate VS Code theme from template.

    Uses mustache-style placeholders ({{base00}}, {{base08}}, etc.) in
    templates/vscode/human-plus-plus.json.tmpl and renders with current palette.
    """
    import shutil

    template_path = ROOT / "templates/vscode/human-plus-plus.json.tmpl"

    if not template_path.exists():
        print("  ⚠ VS Code template not found, skipping")
        return

    content = template_path.read_text()

    # Replace all {{baseXX}} placeholders with current palette values
    for slot, hex_value in colors.items():
        placeholder = '{{' + slot + '}}'
        content = content.replace(placeholder, hex_value.lower())

    # Write to dist/
    (DIST / "vscode").mkdir(parents=True, exist_ok=True)
    theme_path = DIST / "vscode/human-plus-plus.json"
    theme_path.write_text(content)
    print("  ✓ dist/vscode/human-plus-plus.json")

    # Also copy to vscode-extension package
    ext_theme_path = PACKAGES / "vscode-extension/themes/human-plus-plus.json"
    if ext_theme_path.parent.exists():
        shutil.copy(theme_path, ext_theme_path)
        print("  ✓ packages/vscode-extension/themes/human-plus-plus.json")


# =============================================================================
# Main
# =============================================================================

def main():
    print("Building Human++ from palette.toml...\n")

    colors, meta = parse_palette()

    print("Generating configs:")
    generate_ghostty(colors, meta)
    generate_sketchybar(colors, meta)
    generate_borders(colors, meta)
    generate_skhd(colors, meta)
    generate_eza(colors, meta)
    generate_fzf(colors, meta)
    generate_colortest(colors, meta)

    print("\nGenerating site:")
    generate_palette_json(colors, meta)
    generate_site(colors, meta)
    generate_svgs(colors, meta)
    generate_readme(colors, meta)

    print("\nGenerating theme registry files:")
    generate_base24_yaml(colors, meta)
    generate_tinty_themes(colors, meta)

    print("\nGenerating VS Code theme:")
    generate_vscode_theme(colors, meta)

    print("\n✓ Build complete!")
    print("\nTo apply: tinty apply base24-human-plus-plus")


if __name__ == '__main__':
    main()
