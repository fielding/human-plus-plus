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

    content = f"""# Human++ Cool Balanced - Base24
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
# Human++ Cool Balanced - Base24
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
# Human++ Cool Balanced - borders config
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
# Human++ Cool Balanced - skhd mode colors
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



def generate_readme(colors, meta):
    """Generate README.md."""
    c = colors

    content = f'''# Human++

A Base24 color scheme for the post-artisanal coding era.

**Code is cheap. Intent is scarce.**

As models write more code, humans spend more time reviewing, planning, and explaining intent. Human++ makes human judgment visible at a glance through a two-tier accent system and lightweight annotation markers.

## Philosophy

Human++ inverts the traditional syntax highlighting priority:

- **Quiet syntax** — everyday code fades into the background
- **Loud diagnostics** — errors, warnings, and human markers demand attention
- **Terminal exception** — terminal output is intentional, so terminals get loud colors

The result: when you see color, it means something.

## The Palette

Human++ Cool Balanced uses a cool charcoal grayscale with warm text and a full Base24 palette.

### Grayscale

| Slot | Hex | Role |
|------|-----|------|
| base00 | `{c['base00']}` | Background |
| base01 | `{c['base01']}` | Elevation |
| base02 | `{c['base02']}` | Selection |
| base03 | `{c['base03']}` | Comments (coffee brown) |
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

## Build

All theme files are generated from `palette.toml`:

```bash
make build          # Build all theme files
make preview        # Preview palette in terminal
make colortest      # Display terminal ANSI mapping
make apply          # Apply theme to installed apps
make apply-dry      # Preview what apply would do
make analyze        # Analyze palette in OKLCH
```

Or apply with tinty: `tinty apply base24-human-plus-plus`

## Repository Structure

```
palette.toml          # Single source of truth (edit this)
Makefile              # Build orchestration
templates/            # HTML templates (no hardcoded hex)
tools/                # Python generators
scripts/              # Shell orchestration
site/assets/          # Logos and images (committed)
```

**Generated (not committed):**
```
dist/                 # Theme outputs (ghostty, vim, vscode, etc.)
site/index.html       # Landing page (from template)
site/data/            # Palette JSON for the website
```

Run `make build` locally, or let CI generate everything on push.

## CI/CD

- **Pull requests**: Build + analyze palette
- **Push to main**: Deploy site to GitHub Pages
- **Tags (`v*`)**: Create GitHub Release with dist/ artifacts

Download pre-built theme files from [Releases](https://github.com/fielding/human-plus-plus/releases).

## Preview

Visit [fielding.github.io/human-plus-plus](https://fielding.github.io/human-plus-plus/) for the live site.

To preview locally:
```bash
make build
python3 -m http.server -d site 8000
# Open http://localhost:8000
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
  ║                       Human++ Cool Balanced                       ║
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
        f'name: "{meta.get("name", "Human++ Cool Balanced")}"',
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
        'scheme-name': meta.get('name', 'Human++ Cool Balanced'),
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


def update_vscode_theme(colors, meta):
    """Update VS Code theme with new colors.

    Uses a cache file to track previous palette values and replace them
    with new values throughout the theme file.
    """
    import json
    import re
    import shutil

    (DIST / "vscode").mkdir(parents=True, exist_ok=True)
    theme_path = DIST / "vscode/base-cool-balanced-v2.json"
    cache_path = ROOT / ".palette-cache.json"

    if not theme_path.exists():
        print("  ⚠ VS Code theme not found, skipping")
        return

    content = theme_path.read_text()

    # Load previous palette from cache (if exists)
    old_colors = {}
    if cache_path.exists():
        try:
            old_colors = json.loads(cache_path.read_text())
        except:
            pass

    # Build replacement map: old hex -> new hex
    replacements = {}
    for slot, new_hex in colors.items():
        new_hex_lower = new_hex.lower()
        # If we have an old value for this slot, map it to the new value
        if slot in old_colors:
            old_hex = old_colors[slot].lower()
            if old_hex != new_hex_lower:
                replacements[old_hex] = new_hex_lower

    # Apply replacements (case-insensitive)
    total_replacements = 0
    for old_hex, new_hex in replacements.items():
        # Count occurrences
        pattern = re.compile(re.escape(old_hex), re.IGNORECASE)
        matches = len(pattern.findall(content))
        if matches > 0:
            content = pattern.sub(new_hex, content)
            total_replacements += matches

    theme_path.write_text(content)

    if total_replacements > 0:
        print(f"  ✓ dist/vscode/base-cool-balanced-v2.json ({total_replacements} color replacements)")
    else:
        print("  ✓ dist/vscode/base-cool-balanced-v2.json (no changes needed)")

    # Save current palette to cache for next build
    cache_path.write_text(json.dumps(colors, indent=2))

    # Also copy to vscode-extension package
    ext_theme_path = PACKAGES / "vscode-extension/themes/humanpp-cool-balanced.json"
    if ext_theme_path.parent.exists():
        shutil.copy(theme_path, ext_theme_path)
        print("  ✓ packages/vscode-extension/themes/humanpp-cool-balanced.json")


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
    generate_colortest(colors, meta)

    print("\nGenerating site:")
    generate_palette_json(colors, meta)
    generate_site(colors, meta)
    generate_readme(colors, meta)

    print("\nGenerating theme registry files:")
    generate_base24_yaml(colors, meta)
    generate_tinty_themes(colors, meta)

    print("\nUpdating VS Code theme:")
    update_vscode_theme(colors, meta)

    print("\n✓ Build complete!")
    print("\nTo apply: tinty apply base24-human-plus-plus")


if __name__ == '__main__':
    main()
