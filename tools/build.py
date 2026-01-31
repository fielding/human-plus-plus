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


def hex_to_ansi_bg_fg(bg_hex, fg_hex):
    """Convert hex colors to ANSI bg+fg format (48;2;r;g;b;38;2;r;g;b)."""
    bg = bg_hex.lstrip('#')
    fg = fg_hex.lstrip('#')
    bg_r, bg_g, bg_b = int(bg[0:2], 16), int(bg[2:4], 16), int(bg[4:6], 16)
    fg_r, fg_g, fg_b = int(fg[0:2], 16), int(fg[2:4], 16), int(fg[4:6], 16)
    return f"48;2;{bg_r};{bg_g};{bg_b};38;2;{fg_r};{fg_g};{fg_b}"


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
        f"fi={hex_to_ansi256(c['base07'])}",        # regular files - brightest white
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
        # Hard links count (the number before file size)
        f"lc={hex_to_ansi256(c['base16'])}",        # link count - quiet purple
        # Size - quiet, not that important
        f"sn={hex_to_ansi256(c['base17'])}",        # size numbers - quiet lime
        f"sb={hex_to_ansi256(c['base03'])}",        # size unit - dim
        # User/group - grayscale, it's just metadata
        f"uu={hex_to_ansi256(c['base04'])}",        # current user - secondary
        f"un={hex_to_ansi256(c['base03'])}",        # other user - dim
        f"gu={hex_to_ansi256(c['base03'])}",        # current group - dim
        f"gn={hex_to_ansi256(c['base03'])}",        # other group - dim
        # Git - LOUD, git status is important
        f"ga={hex_to_ansi256(c['base0B'])}",        # git new - LOUD green
        f"gm={hex_to_ansi256(c['base0A'])}",        # git modified - LOUD amber
        f"gd={hex_to_ansi256(c['base08'])}",        # git deleted - LOUD pink
        f"gv={hex_to_ansi256(c['base0C'])}",        # git renamed - LOUD cyan
        f"gt={hex_to_ansi256(c['base03'])}",        # git ignored - dim
        # Misc
        f"da={hex_to_ansi256(c['base03'])}",        # date - dim (not important)
        f"hd={hex_to_ansi256(c['base07'])};1",      # header - brightest + bold
        f"xx={hex_to_ansi256(c['base03'])}",        # punctuation - dim
        # Special files - !! badge style (lime bg, dark text for contrast)
        f"README*={hex_to_ansi_bg_fg(c['base0F'], c['base00'])}",
        f"README.md={hex_to_ansi_bg_fg(c['base0F'], c['base00'])}",
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
        "bg:-1",                         # background - inherit terminal
        f"bg+:{c['base02']}",            # selected background - more contrast
        f"fg:{c['base07']}",             # foreground - brightest
        f"fg+:{c['base07']}",            # selected foreground - brightest
        f"hl:{c['base0F']}",             # highlighted match - LOUD lime (human marker!)
        f"hl+:{c['base0F']}",            # selected highlighted - LOUD lime
        f"info:{c['base0C']}",           # info line - LOUD cyan
        f"marker:{c['base0B']}",         # marker - LOUD green
        f"prompt:{c['base08']}",         # prompt - LOUD pink
        f"spinner:{c['base0A']}",        # spinner - LOUD amber
        f"pointer:{c['base08']}",        # pointer - LOUD pink
        f"header:{c['base07']}",         # header - brightest
        f"border:{c['base0D']}",         # border - LOUD blue
        "gutter:-1",                     # gutter - inherit terminal
        f"query:{c['base07']}",          # query text - brightest
        f"scrollbar:{c['base03']}",      # scrollbar - dim
        f"separator:{c['base02']}",      # separator line - subtle
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


def generate_bat(colors, meta):
    """Generate bat theme (.tmTheme format) matching VS Code theme.

    Bat uses TextMate themes. After generating, run: bat cache --build
    """
    c = colors

    # tmTheme is XML/plist format - mappings match VS Code theme
    content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>name</key>
    <string>Human++</string>
    <key>author</key>
    <string>{meta.get('author', 'fielding')}</string>
    <key>settings</key>
    <array>
        <!-- Global settings -->
        <dict>
            <key>settings</key>
            <dict>
                <key>background</key>
                <string>{c['base00']}</string>
                <key>foreground</key>
                <string>{c['base07']}</string>
                <key>caret</key>
                <string>{c['base07']}</string>
                <key>selection</key>
                <string>{c['base02']}</string>
                <key>lineHighlight</key>
                <string>{c['base01']}</string>
                <key>gutterForeground</key>
                <string>{c['base04']}</string>
            </dict>
        </dict>
        <!-- Comments - base03 italic -->
        <dict>
            <key>scope</key>
            <string>comment, punctuation.definition.comment</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>{c['base03']}</string>
                <key>fontStyle</key>
                <string>italic</string>
            </dict>
        </dict>
        <!-- Strings - base17 quiet lime -->
        <dict>
            <key>scope</key>
            <string>string, string.quoted</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>{c['base17']}</string>
            </dict>
        </dict>
        <!-- Keywords - base10 quiet pink -->
        <dict>
            <key>scope</key>
            <string>keyword, keyword.control, keyword.other</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>{c['base10']}</string>
            </dict>
        </dict>
        <!-- Storage types - base14 quiet cyan italic -->
        <dict>
            <key>scope</key>
            <string>storage.type, storage.modifier</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>{c['base14']}</string>
                <key>fontStyle</key>
                <string>italic</string>
            </dict>
        </dict>
        <!-- Storage keywords - base10 quiet pink -->
        <dict>
            <key>scope</key>
            <string>storage, storage.type.function, storage.type.class</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>{c['base10']}</string>
            </dict>
        </dict>
        <!-- Functions - base15 quiet blue -->
        <dict>
            <key>scope</key>
            <string>entity.name.function, support.function, meta.function-call</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>{c['base15']}</string>
            </dict>
        </dict>
        <!-- Types/Classes - base14 quiet cyan -->
        <dict>
            <key>scope</key>
            <string>entity.name.type, entity.name.class, entity.name.namespace, support.type, support.class</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>{c['base14']}</string>
            </dict>
        </dict>
        <!-- Constants/Numbers - base12 quiet yellow -->
        <dict>
            <key>scope</key>
            <string>constant, constant.numeric, constant.language, constant.character</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>{c['base12']}</string>
            </dict>
        </dict>
        <!-- Variables - base07 white -->
        <dict>
            <key>scope</key>
            <string>variable, variable.other, variable.language</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>{c['base07']}</string>
            </dict>
        </dict>
        <!-- Parameters - base16 quiet purple italic -->
        <dict>
            <key>scope</key>
            <string>variable.parameter</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>{c['base16']}</string>
                <key>fontStyle</key>
                <string>italic</string>
            </dict>
        </dict>
        <!-- Operators/Punctuation - base04 secondary -->
        <dict>
            <key>scope</key>
            <string>keyword.operator, punctuation</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>{c['base04']}</string>
            </dict>
        </dict>
        <!-- Tags (HTML/XML) - base10 quiet pink -->
        <dict>
            <key>scope</key>
            <string>entity.name.tag</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>{c['base10']}</string>
            </dict>
        </dict>
        <!-- Attributes - base14 quiet cyan italic -->
        <dict>
            <key>scope</key>
            <string>entity.other.attribute-name</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>{c['base14']}</string>
                <key>fontStyle</key>
                <string>italic</string>
            </dict>
        </dict>
        <!-- CSS classes - base13 quiet green -->
        <dict>
            <key>scope</key>
            <string>entity.other.attribute-name.class.css</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>{c['base13']}</string>
            </dict>
        </dict>
        <!-- CSS ids - base11 quiet orange -->
        <dict>
            <key>scope</key>
            <string>entity.other.attribute-name.id.css</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>{c['base11']}</string>
            </dict>
        </dict>
        <!-- Decorators/Interpolation - base11 quiet orange -->
        <dict>
            <key>scope</key>
            <string>meta.decorator, punctuation.section.embedded, meta.interpolation</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>{c['base11']}</string>
            </dict>
        </dict>
        <!-- Markdown h1 - LOUD lime badge -->
        <dict>
            <key>scope</key>
            <string>markup.heading.1, markup.heading.1.markdown</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>{c['base00']}</string>
                <key>background</key>
                <string>{c['base0F']}</string>
                <key>fontStyle</key>
                <string>bold</string>
            </dict>
        </dict>
        <!-- Markdown headings 2-6 - base10 quiet pink -->
        <dict>
            <key>scope</key>
            <string>markup.heading, entity.name.section</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>{c['base10']}</string>
            </dict>
        </dict>
        <!-- Markdown bold/italic - base15 quiet blue -->
        <dict>
            <key>scope</key>
            <string>markup.bold, markup.italic</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>{c['base15']}</string>
            </dict>
        </dict>
        <!-- Markdown code - base09 LOUD orange -->
        <dict>
            <key>scope</key>
            <string>markup.inline.raw, markup.raw</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>{c['base09']}</string>
            </dict>
        </dict>
        <!-- Markdown links - base17 quiet lime -->
        <dict>
            <key>scope</key>
            <string>markup.underline.link, string.other.link</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>{c['base17']}</string>
            </dict>
        </dict>
        <!-- Diff inserted - base13 quiet green -->
        <dict>
            <key>scope</key>
            <string>markup.inserted</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>{c['base13']}</string>
            </dict>
        </dict>
        <!-- Diff deleted - base10 quiet pink -->
        <dict>
            <key>scope</key>
            <string>markup.deleted</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>{c['base10']}</string>
            </dict>
        </dict>
        <!-- Invalid - base08 LOUD pink -->
        <dict>
            <key>scope</key>
            <string>invalid</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>{c['base08']}</string>
                <key>fontStyle</key>
                <string>italic underline</string>
            </dict>
        </dict>
    </array>
</dict>
</plist>
'''

    (DIST / "bat").mkdir(parents=True, exist_ok=True)
    (DIST / "bat/Human++.tmTheme").write_text(content)
    print("  ✓ dist/bat/Human++.tmTheme")
    print("    → Install: mkdir -p ~/.config/bat/themes && cp dist/bat/Human++.tmTheme ~/.config/bat/themes/ && bat cache --build")


def generate_glow(colors, meta):
    """Generate glow (markdown renderer) style.

    Glow uses glamour JSON styles for markdown rendering.
    """
    c = colors
    import json

    style = {
        "document": {
            "color": c['base07'],
            "margin": 2
        },
        "block_quote": {
            "indent": 2,
            "color": c['base14'],
            "italic": True
        },
        "paragraph": {},
        "list": {
            "level_indent": 2
        },
        "heading": {
            "color": c['base10'],
            "bold": True
        },
        "h1": {
            "prefix": "# ",
            "color": c['base00'],
            "background_color": c['base0F'],
            "bold": True
        },
        "h2": {
            "prefix": "## ",
            "color": c['base10'],
            "bold": True
        },
        "h3": {
            "prefix": "### ",
            "color": c['base10']
        },
        "h4": {
            "prefix": "#### ",
            "color": c['base10']
        },
        "h5": {
            "prefix": "##### ",
            "color": c['base10']
        },
        "h6": {
            "prefix": "###### ",
            "color": c['base10']
        },
        "text": {},
        "strikethrough": {
            "crossed_out": True
        },
        "emph": {
            "color": c['base15'],
            "italic": True
        },
        "strong": {
            "color": c['base15'],
            "bold": True
        },
        "hr": {
            "color": c['base02'],
            "format": "--------"
        },
        "item": {
            "block_prefix": "• "
        },
        "enumeration": {
            "block_prefix": ". "
        },
        "task": {
            "ticked": "[✓] ",
            "unticked": "[ ] "
        },
        "link": {
            "color": c['base17'],
            "underline": True
        },
        "link_text": {
            "color": c['base0D'],
            "bold": True
        },
        "image": {
            "color": c['base17'],
            "underline": True
        },
        "image_text": {
            "color": c['base0E'],
            "format": "Image: {{.text}}"
        },
        "code": {
            "color": c['base09'],
            "background_color": c['base01']
        },
        "code_block": {
            "color": c['base07'],
            "margin": 2,
            "chroma": {
                "text": {"color": c['base07']},
                "error": {"color": c['base08']},
                "comment": {"color": c['base03'], "italic": True},
                "comment_preproc": {"color": c['base03']},
                "keyword": {"color": c['base10']},
                "keyword_reserved": {"color": c['base10']},
                "keyword_namespace": {"color": c['base10']},
                "keyword_type": {"color": c['base14'], "italic": True},
                "operator": {"color": c['base04']},
                "punctuation": {"color": c['base04']},
                "name": {"color": c['base07']},
                "name_builtin": {"color": c['base15']},
                "name_tag": {"color": c['base10']},
                "name_attribute": {"color": c['base14'], "italic": True},
                "name_class": {"color": c['base14']},
                "name_constant": {"color": c['base12']},
                "name_decorator": {"color": c['base11']},
                "name_exception": {"color": c['base08']},
                "name_function": {"color": c['base15']},
                "name_other": {"color": c['base07']},
                "literal": {"color": c['base12']},
                "literal_number": {"color": c['base12']},
                "literal_date": {"color": c['base12']},
                "literal_string": {"color": c['base17']},
                "literal_string_escape": {"color": c['base12']},
                "generic_deleted": {"color": c['base10']},
                "generic_emph": {"italic": True},
                "generic_inserted": {"color": c['base13']},
                "generic_strong": {"bold": True},
                "generic_subheading": {"color": c['base10']},
                "background": {"background_color": c['base00']}
            }
        },
        "table": {
            "center_separator": "┼",
            "column_separator": "│",
            "row_separator": "─"
        },
        "definition_list": {},
        "definition_term": {},
        "definition_description": {},
        "html_block": {},
        "html_span": {}
    }

    (DIST / "glow").mkdir(parents=True, exist_ok=True)
    (DIST / "glow/human-plus-plus.json").write_text(json.dumps(style, indent=2))
    print("  ✓ dist/glow/human-plus-plus.json")
    print("    → Install: glow -s ~/path/to/dist/glow/human-plus-plus.json README.md")


def generate_delta(colors, meta):
    """Generate delta (git pager) configuration.

    Add to ~/.gitconfig or include from there.
    """
    c = colors

    content = f'''# Human++ delta configuration
# Add to ~/.gitconfig under [delta] section, or include this file

[delta]
    navigate = true
    dark = true
    syntax-theme = Human++
    line-numbers = true
    side-by-side = false

    # File header
    file-style = bold {c['base07']}
    file-decoration-style = none
    hunk-header-style = file line-number
    hunk-header-decoration-style = {c['base02']} box

    # Line numbers
    line-numbers-left-style = {c['base03']}
    line-numbers-right-style = {c['base03']}
    line-numbers-minus-style = {c['base08']}
    line-numbers-plus-style = {c['base0B']}
    line-numbers-zero-style = {c['base03']}

    # Diff colors
    minus-style = syntax {c['base08']}20
    minus-emph-style = syntax {c['base08']}40
    plus-style = syntax {c['base0B']}20
    plus-emph-style = syntax {c['base0B']}40
    whitespace-error-style = {c['base08']} reverse

    # Blame
    blame-palette = {c['base00']} {c['base01']} {c['base02']}
'''

    (DIST / "delta").mkdir(parents=True, exist_ok=True)
    (DIST / "delta/config.gitconfig").write_text(content)
    print("  ✓ dist/delta/config.gitconfig")
    print("    → Install: Add [include] path = ~/path/to/dist/delta/config.gitconfig to ~/.gitconfig")


def generate_git_colors(colors, meta):
    """Generate git color configuration.

    These are the colors git uses for status, diff, branch, etc.
    """
    c = colors

    content = f'''# Human++ git colors
#
# Include this file in your ~/.gitconfig:
#   https://git-scm.com/docs/git-config#_includes
#
# For all repos:
#   [include]
#     path = ~/path/to/human-plus-plus/dist/git/colors.gitconfig
#
# Or conditionally for specific directories:
#   [includeIf "gitdir:~/Projects/"]
#     path = ~/path/to/human-plus-plus/dist/git/colors.gitconfig

[color]
    ui = auto

[color "branch"]
    current = bold {c['base0F']}
    local = {c['base07']}
    remote = {c['base0B']}
    upstream = {c['base0C']}

[color "diff"]
    meta = {c['base0E']}
    frag = {c['base0C']}
    context = {c['base04']}
    old = {c['base08']}
    new = {c['base0B']}
    oldMoved = {c['base11']}
    newMoved = {c['base14']}
    whitespace = {c['base08']} reverse

[color "status"]
    added = {c['base0B']}
    changed = {c['base0A']}
    untracked = {c['base03']}
    deleted = {c['base08']}
    branch = bold {c['base0F']}
    localBranch = bold {c['base0F']}
    remoteBranch = {c['base0B']}

[color "decorate"]
    HEAD = bold {c['base08']}
    branch = bold {c['base0F']}
    remoteBranch = {c['base0B']}
    tag = {c['base0A']}
'''

    (DIST / "git").mkdir(parents=True, exist_ok=True)
    (DIST / "git/colors.gitconfig").write_text(content)
    print("  ✓ dist/git/colors.gitconfig")


def generate_shell_init(colors, meta):
    """Generate shell-init.sh loader that conditionally sources configs.

    Users add one line to their .zshrc/.bashrc:
        source /path/to/human++/dist/shell-init.sh

    The loader automatically sources configs for installed programs.
    """
    content = '''#!/bin/bash
# Human++ Shell Loader
# Generated from palette.toml
#
# Add this to your .zshrc or .bashrc:
#   source /path/to/human++/dist/shell-init.sh
#
# Or selectively source individual configs from dist/

# Determine the directory where this script lives
HUMAN_PP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"

# eza - modern ls replacement
if command -v eza &>/dev/null; then
  source "$HUMAN_PP_DIR/eza/colors.sh"
fi

# fzf - fuzzy finder
if command -v fzf &>/dev/null; then
  source "$HUMAN_PP_DIR/fzf/colors.sh"
fi

# Terminal palette (base24) - only if running interactively
# Uncomment if you want Human++ to set your terminal colors on shell startup
# if [[ $- == *i* ]]; then
#   source "$HUMAN_PP_DIR/base24/base24-human-plus-plus.sh"
# fi

# sketchybar - macOS menu bar (uncomment if using)
# if command -v sketchybar &>/dev/null; then
#   source "$HUMAN_PP_DIR/sketchybar/colors.sh"
# fi

# skhd mode colors (uncomment if using)
# if command -v skhd &>/dev/null; then
#   source "$HUMAN_PP_DIR/skhd/modes.sh"
# fi
'''

    (DIST / "shell-init.sh").write_text(content)
    os.chmod(DIST / "shell-init.sh", 0o755)
    print("  ✓ dist/shell-init.sh")


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

    # Process the HTML template, substituting color placeholders
    # This ensures fallback CSS variables have real values if palette.json fails to load
    template_path = ROOT / "templates" / "site" / "index.html.tmpl"
    if template_path.exists():
        content = template_path.read_text()

        # Substitute color placeholders with actual values
        for slot, hex_value in colors.items():
            placeholder = '{{' + slot + '}}'
            content = content.replace(placeholder, hex_value.lower())

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
    <tspan fill="{c['base15']}">getUser</tspan>
    <tspan fill="{c['base05']}">(</tspan>
    <tspan fill="{c['base16']}" font-style="italic">id</tspan>
    <tspan fill="{c['base05']}">: </tspan>
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
    <tspan fill="{c['base15']}">get</tspan>
    <tspan fill="{c['base05']}">(</tspan>
    <tspan fill="{c['base17']}">`user:</tspan>
    <tspan fill="{c['base05']}">${{id}}</tspan>
    <tspan fill="{c['base17']}">`</tspan>
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
    <tspan fill="{c['base12']}">null</tspan>
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
    <tspan fill="{c['base0C']}">User</tspan>
    <tspan fill="{c['base00']}"> {{</tspan>
  </text>

  <!-- Line 2: id: string; -->
  <text x="44" y="92" font-family="SF Mono, Consolas, monospace" font-size="13">
    <tspan fill="{c['base00']}">  id: </tspan>
    <tspan fill="{c['base0C']}">string</tspan>
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
    <tspan fill="{c['base0D']}">getUser</tspan>
    <tspan fill="{c['base00']}">(</tspan>
    <tspan fill="{c['base0E']}" font-style="italic">id</tspan>
    <tspan fill="{c['base00']}">: </tspan>
    <tspan fill="{c['base0C']}">string</tspan>
    <tspan fill="{c['base00']}">): </tspan>
    <tspan fill="{c['base0C']}">Promise</tspan>
    <tspan fill="{c['base00']}">&lt;</tspan>
    <tspan fill="{c['base0C']}">User</tspan>
    <tspan fill="{c['base00']}">&gt; {{</tspan>
  </text>

  <!-- Line 7: const cached -->
  <text x="44" y="212" font-family="SF Mono, Consolas, monospace" font-size="13">
    <tspan fill="{c['base00']}">  </tspan>
    <tspan fill="{c['base10']}">const</tspan>
    <tspan fill="{c['base00']}"> cached = </tspan>
    <tspan fill="{c['base10']}">await</tspan>
    <tspan fill="{c['base00']}"> redis.</tspan>
    <tspan fill="{c['base0D']}">get</tspan>
    <tspan fill="{c['base00']}">(</tspan>
    <tspan fill="{c['base0B']}">`user:</tspan>
    <tspan fill="{c['base00']}">${{id}}</tspan>
    <tspan fill="{c['base0B']}">`</tspan>
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
    <tspan fill="{c['base0A']}">null</tspan>
    <tspan fill="{c['base00']}">;</tspan>
  </text>
  <rect x="180" y="294" width="290" height="20" rx="4" fill="{c['base08']}"/>
  <text x="188" y="308" font-family="SF Mono, Consolas, monospace" font-size="11" fill="{c['base07']}" font-weight="600">Type 'null' is not assignable to 'string'</text>
</svg>
'''
    (assets_dir / "preview-light.svg").write_text(preview_light)
    print("  ✓ site/assets/preview-dark.svg, preview-light.svg")



def generate_readme(colors, meta):
    """Generate README.md from template.

    Uses mustache-style placeholders ({{base00}}, {{base08}}, etc.) in
    templates/README.md.tmpl and renders with current palette.
    """
    template_path = ROOT / "templates/README.md.tmpl"

    if not template_path.exists():
        print("  ⚠ README template not found, skipping")
        return

    content = template_path.read_text()

    # Replace all {{baseXX}} placeholders with current palette values
    for slot, hex_value in colors.items():
        placeholder = '{{' + slot + '}}'
        content = content.replace(placeholder, hex_value.lower())

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
    generate_bat(colors, meta)
    generate_glow(colors, meta)
    generate_delta(colors, meta)
    generate_git_colors(colors, meta)
    generate_shell_init(colors, meta)
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
