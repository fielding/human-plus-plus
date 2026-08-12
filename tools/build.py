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


def generate_tmux(colors, meta):
    """Generate tmux/human-plus-plus.conf theme.

    Produces a tmux conf snippet that can be sourced from tmux.conf:
        source-file /path/to/human++/dist/tmux/human-plus-plus.conf

    Uses true color hex values (#rrggbb) — requires terminal with RGB support
    and tmux set -as terminal-features ",*:RGB".
    """
    c = colors

    content = f"""# Human++ - tmux theme
# Generated from palette.toml
#
# Source this from your tmux.conf:
#   source-file /path/to/human++/dist/tmux/human-plus-plus.conf

# Status bar — LOUD cyan text on dark bg
set -g status-style "bg={c['base00']},fg={c['base0C']}"

# Session name on the left (hot pink accent)
set -g status-left "#[bg={c['base08']},fg={c['base00']},bold] #S #[default] "

# Window status — inactive (grayscale, recedes behind active)
setw -g window-status-format "#[bg={c['base01']},fg={c['base04']},noreverse]█▓░ #W "
# Window status — active (hot pink bg — grabs attention)
setw -g window-status-current-format "#[bg={c['base08']},fg={c['base00']},noreverse]█▓░ #W "

# Messages
set -g message-style "bg={c['base0B']},fg={c['base00']}"
set -g message-command-style "bg={c['base00']},fg={c['base0B']}"

# Copy / choice mode
setw -g mode-style "bg={c['base0E']},fg={c['base00']}"

# Copy mode search matches
set -g copy-mode-match-style "bg={c['base0A']},fg={c['base00']}"
set -g copy-mode-current-match-style "bg={c['base0F']},fg={c['base00']}"

# Pane borders
set -g pane-border-style "fg={c['base03']}"
set -g pane-active-border-style "fg={c['base08']}"

# Pane border titles — accent on index, dim title
set -g pane-border-format " #[fg={c['base0C']}]#{{pane_index}}#[default]:#[fg={c['base04']}] #{{pane_title}} "

# Clock (prefix + t)
set -g clock-mode-colour "{c['base0F']}"

# Menu (popup) styles
set -g menu-style "bg={c['base01']},fg={c['base0C']}"
set -g menu-selected-style "bg={c['base08']},fg={c['base00']}"
set -g menu-border-style "fg={c['base03']}"

# Popup border
set -g popup-border-style "fg={c['base03']}"

# Display-panes overlay
set -g display-panes-colour "{c['base03']}"
set -g display-panes-active-colour "{c['base08']}"
"""

    # Shell-sourceable color variables for tmux-status and other scripts
    colors_sh = f"""#!/bin/bash
# Human++ - tmux status colors
# Generated from palette.toml
# Source this from scripts that output tmux status content

HMPP_BG="{c['base00']}"          # base00 - background
HMPP_BG_ELEVATION="{c['base01']}" # base01 - elevation
HMPP_SELECTION="{c['base02']}"   # base02 - selection/panels
HMPP_DIM="{c['base03']}"         # base03 - comments
HMPP_SECONDARY="{c['base04']}"   # base04 - UI secondary
HMPP_FG="{c['base05']}"          # base05 - main text
HMPP_FG_BRIGHT="{c['base06']}"   # base06 - emphasis
HMPP_FG_MAX="{c['base07']}"      # base07 - near-white
HMPP_PINK="{c['base08']}"        # base08 - errors, attention
HMPP_ORANGE="{c['base09']}"      # base09 - warnings
HMPP_AMBER="{c['base0A']}"       # base0A - caution
HMPP_GREEN="{c['base0B']}"       # base0B - success
HMPP_CYAN="{c['base0C']}"        # base0C - info
HMPP_BLUE="{c['base0D']}"        # base0D - focus, links
HMPP_PURPLE="{c['base0E']}"      # base0E - special
HMPP_LIME="{c['base0F']}"        # base0F - human intent
"""

    (DIST / "tmux").mkdir(parents=True, exist_ok=True)
    (DIST / "tmux/human-plus-plus.conf").write_text(content)
    (DIST / "tmux/colors.sh").write_text(colors_sh)
    print("  ✓ dist/tmux/human-plus-plus.conf")
    print("  ✓ dist/tmux/colors.sh")


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
    file-style = bold "{c['base07']}"
    file-decoration-style = none
    hunk-header-style = file line-number
    hunk-header-decoration-style = "{c['base02']}" box

    # Line numbers
    line-numbers-left-style = "{c['base03']}"
    line-numbers-right-style = "{c['base03']}"
    line-numbers-minus-style = "{c['base08']}"
    line-numbers-plus-style = "{c['base0B']}"
    line-numbers-zero-style = "{c['base03']}"

    # Diff colors
    minus-style = syntax "{c['base08']}20"
    minus-emph-style = syntax "{c['base08']}40"
    plus-style = syntax "{c['base0B']}20"
    plus-emph-style = syntax "{c['base0B']}40"
    whitespace-error-style = "{c['base08']}" reverse

    # Blame
    blame-palette = "{c['base00']}" "{c['base01']}" "{c['base02']}"
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


def generate_fastfetch(colors, meta):
    """Generate fastfetch/config.jsonc."""
    c = colors

    config = {
        "$schema": "https://github.com/fastfetch-cli/fastfetch/raw/dev/doc/json_schema.json",
        "logo": {
            "type": "small",
            "color": {
                "1": c['base08'],
                "2": c['base09'],
                "3": c['base0A'],
                "4": c['base0B'],
                "5": c['base0C'],
                "6": c['base0D'],
                "7": c['base0E'],
                "8": c['base0F'],
                "9": c['base10'],
            },
        },
        "display": {
            "color": {
                "keys": c['base0C'],
                "title": c['base0F'],
                "output": c['base05'],
                "separator": c['base04'],
            },
            "separator": " → ",
            "key": {
                "width": 10,
            },
        },
        "modules": [
            "title",
            "separator",
            {"type": "os", "key": "OS"},
            {"type": "host", "key": "Host"},
            {"type": "kernel", "key": "Kernel"},
            {"type": "uptime", "key": "Uptime"},
            {"type": "shell", "key": "Shell"},
            {"type": "terminal", "key": "Term"},
            {"type": "cpu", "key": "CPU"},
            {"type": "gpu", "key": "GPU"},
            {"type": "memory", "key": "Mem"},
            {"type": "disk", "key": "Disk"},
            {"type": "battery", "key": "Bat"},
            "break",
            "colors",
        ],
    }

    (DIST / "fastfetch").mkdir(parents=True, exist_ok=True)
    (DIST / "fastfetch/config.jsonc").write_text(json.dumps(config, indent=2))
    print("  ✓ dist/fastfetch/config.jsonc")


def generate_shell_init(colors, meta):
    """Generate shell-init.sh loader that conditionally sources configs.

    Users add one line to their .zshrc/.bashrc:
        source /path/to/human++/dist/shell-init.sh

    The loader automatically sources configs for installed programs.
    """
    c = {k: hex_to_components(v) for k, v in colors.items()}

    # 256-color extended slots 16-23: the 8 base24 colors without ANSI 0-15 slots
    # Slots 16-20 follow the base16-shell convention; 21 repurposed for base05;
    # 22-23 are the base24 extension (quiet orange, quiet lime)
    extended_slots = [
        (16, 'base09', 'orange'),
        (17, 'base0F', 'lime'),
        (18, 'base01', 'elevation'),
        (19, 'base02', 'selection'),
        (20, 'base04', 'UI secondary'),
        (21, 'base05', 'main text'),
        (22, 'base11', 'quiet orange'),
        (23, 'base17', 'quiet lime'),
    ]

    remap_lines = []
    for slot_num, base_key, label in extended_slots:
        r = c[base_key]['hex_r']
        g = c[base_key]['hex_g']
        b = c[base_key]['hex_b']
        remap_lines.append(
            f"  printf '\\e]4;{slot_num};rgb:{r}/{g}/{b}\\e\\\\'   # {base_key} {label}"
        )

    remap_block = '\n'.join(remap_lines)

    content = f'''#!/bin/bash
# Human++ Shell Loader
# Generated from palette.toml
#
# Add this to your .zshrc or .bashrc:
#   source /path/to/human++/dist/shell-init.sh
#
# Or selectively source individual configs from dist/

# Determine the directory where this script lives
HUMAN_PP_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]:-$0}}")" && pwd)"

# Base24 extended palette (slots 16-23)
# Maps the 8 base24 colors that lack ANSI 0-15 assignments into 256-color
# extended slots, so scripts can reference them via \\e[38;5;16-23m
if [[ $- == *i* ]]; then
{remap_block}
fi

# eza - modern ls replacement
if command -v eza &>/dev/null; then
  source "$HUMAN_PP_DIR/eza/colors.sh"
fi

# fzf - fuzzy finder
if command -v fzf &>/dev/null; then
  source "$HUMAN_PP_DIR/fzf/colors.sh"
fi

# fastfetch - system info (only symlink if no config exists yet)
if command -v fastfetch &>/dev/null; then
  mkdir -p "$HOME/.config/fastfetch"
  if [ ! -e "$HOME/.config/fastfetch/config.jsonc" ]; then
    ln -sf "$HUMAN_PP_DIR/fastfetch/config.jsonc" "$HOME/.config/fastfetch/config.jsonc"
  fi
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

    # Comment marker alias preview for issue triage / README clarity.
    marker_preview = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 366" role="img" aria-labelledby="title desc">
  <title id="title">Human++ comment marker preview</title>
  <desc id="desc">Preview of Human++ comment marker badges for explicit punctuation and legacy keyword aliases.</desc>
  <rect width="760" height="366" rx="12" fill="{c['base00']}"/>

  <rect width="760" height="36" rx="12" fill="{c['base01']}"/>
  <rect y="26" width="760" height="10" fill="{c['base01']}"/>
  <circle cx="20" cy="18" r="6" fill="{c['base08']}"/>
  <circle cx="40" cy="18" r="6" fill="{c['base0A']}"/>
  <circle cx="60" cy="18" r="6" fill="{c['base0B']}"/>
  <text x="380" y="23" text-anchor="middle" font-family="SF Mono, Consolas, monospace" font-size="12" fill="{c['base04']}">marker-aliases.ts</text>

  <text x="28" y="67" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base03']}" text-anchor="end">1</text>
  <text x="28" y="95" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base03']}" text-anchor="end">2</text>
  <text x="28" y="123" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base03']}" text-anchor="end">3</text>
  <text x="28" y="151" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base03']}" text-anchor="end">4</text>
  <text x="28" y="179" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base03']}" text-anchor="end">5</text>
  <text x="28" y="207" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base03']}" text-anchor="end">6</text>
  <text x="28" y="235" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base03']}" text-anchor="end">7</text>
  <text x="28" y="263" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base03']}" text-anchor="end">8</text>
  <text x="28" y="291" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base03']}" text-anchor="end">9</text>
  <text x="28" y="319" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base03']}" text-anchor="end">10</text>

  <text x="44" y="67" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base03']}">// Regular comment stays calm and low-contrast</text>

  <rect x="40" y="78" width="590" height="22" rx="4" fill="{c['base0F']}"/>
  <text x="48" y="95" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base00']}" font-weight="700">// FIXME: payment retry can double-submit</text>
  <text x="650" y="95" font-family="SF Mono, Consolas, monospace" font-size="12" fill="{c['base0F']}" font-weight="700">!!</text>

  <rect x="40" y="106" width="590" height="22" rx="4" fill="{c['base0F']}"/>
  <text x="48" y="123" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base00']}" font-weight="700">// BUG: cache invalidation skips deleted users</text>
  <text x="650" y="123" font-family="SF Mono, Consolas, monospace" font-size="12" fill="{c['base0F']}" font-weight="700">!!</text>

  <rect x="40" y="134" width="590" height="22" rx="4" fill="{c['base0F']}"/>
  <text x="48" y="151" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base00']}" font-weight="700">// XXX: verify migration before rollout</text>
  <text x="650" y="151" font-family="SF Mono, Consolas, monospace" font-size="12" fill="{c['base0F']}" font-weight="700">!!</text>

  <rect x="40" y="162" width="590" height="22" rx="4" fill="{c['base0E']}"/>
  <text x="48" y="179" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base07']}" font-weight="700">// TODO: choose a better empty-state copy</text>
  <text x="650" y="179" font-family="SF Mono, Consolas, monospace" font-size="12" fill="{c['base0E']}" font-weight="700">??</text>

  <rect x="40" y="190" width="590" height="22" rx="4" fill="{c['base0E']}"/>
  <text x="48" y="207" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base07']}" font-weight="700">// HACK: keep legacy slug routing alive for now</text>
  <text x="650" y="207" font-family="SF Mono, Consolas, monospace" font-size="12" fill="{c['base0E']}" font-weight="700">??</text>

  <rect x="40" y="218" width="590" height="22" rx="4" fill="{c['base0C']}"/>
  <text x="48" y="235" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base00']}" font-weight="700">// NOTE: this mirrors the server-side validator</text>
  <text x="650" y="235" font-family="SF Mono, Consolas, monospace" font-size="12" fill="{c['base0C']}" font-weight="700">&gt;&gt;</text>

  <rect x="40" y="246" width="590" height="22" rx="4" fill="{c['base0C']}"/>
  <text x="48" y="263" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base00']}" font-weight="700">// NB: redirects intentionally preserve the query string</text>
  <text x="650" y="263" font-family="SF Mono, Consolas, monospace" font-size="12" fill="{c['base0C']}" font-weight="700">&gt;&gt;</text>

  <rect x="40" y="274" width="590" height="22" rx="4" fill="{c['base0F']}"/>
  <text x="48" y="291" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base00']}" font-weight="700">// !! Explicit punctuation always works too</text>
  <text x="650" y="291" font-family="SF Mono, Consolas, monospace" font-size="12" fill="{c['base0F']}" font-weight="700">!!</text>

  <rect x="40" y="302" width="590" height="22" rx="4" fill="{c['base0C']}"/>
  <text x="48" y="319" font-family="SF Mono, Consolas, monospace" font-size="13" fill="{c['base00']}" font-weight="700">// &gt;&gt; Explicit context note stays visible</text>
  <text x="650" y="319" font-family="SF Mono, Consolas, monospace" font-size="12" fill="{c['base0C']}" font-weight="700">&gt;&gt;</text>

  <text x="44" y="346" font-family="SF Mono, Consolas, monospace" font-size="12" fill="{c['base04']}">Aliases are case-insensitive; strongest marker wins when multiple keywords appear.</text>
</svg>
'''
    (assets_dir / "comment-marker-preview.svg").write_text(marker_preview)
    print("  ✓ site/assets/comment-marker-preview.svg")



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


def generate_zed_theme(colors, meta):
    """Generate Zed theme from template.

    Uses mustache-style placeholders ({{base00}}, {{base08}}, etc.) in
    templates/zed/human-plus-plus.json.tmpl and renders with current palette.
    Colors in Zed use 8-digit RGBA hex; the template appends alpha suffixes
    directly (e.g. {{base00}}ff for fully opaque, {{base08}}1a for 10% alpha).
    """
    import shutil

    template_path = ROOT / "templates/zed/human-plus-plus.json.tmpl"

    if not template_path.exists():
        print("  ⚠ Zed template not found, skipping")
        return

    content = template_path.read_text()

    # Replace all {{baseXX}} placeholders with current palette values
    for slot, hex_value in colors.items():
        placeholder = '{{' + slot + '}}'
        content = content.replace(placeholder, hex_value.lower())

    # Write to dist/
    (DIST / "zed").mkdir(parents=True, exist_ok=True)
    theme_path = DIST / "zed/human-plus-plus.json"
    theme_path.write_text(content)
    print("  ✓ dist/zed/human-plus-plus.json")

    # Also copy to zed-extension package
    ext_theme_path = PACKAGES / "zed-extension/themes/human-plus-plus.json"
    if ext_theme_path.parent.exists():
        shutil.copy(theme_path, ext_theme_path)
        print("  ✓ packages/zed-extension/themes/human-plus-plus.json")


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


def generate_neovim(colors, meta):
    """Generate Neovim colorscheme (Lua) from palette.

    Produces a complete colorscheme file that can be loaded with
    :colorscheme humanplusplus. Also defines custom highlight groups
    used by the Human++ runtime plugin (markers, diagnostics, h1).
    """
    c = colors

    content = f'''-- Human++ Neovim Colorscheme
-- Generated from palette.toml — DO NOT EDIT
-- Rebuild: make build

vim.cmd.highlight('clear')
vim.g.colors_name = 'humanplusplus'
vim.o.termguicolors = true

local hi = function(group, opts)
  vim.api.nvim_set_hl(0, group, opts)
end

-- ============================================================================
-- Editor UI
-- ============================================================================
hi('Normal',       {{ fg = '{c["base05"]}', bg = '{c["base00"]}' }})
hi('NormalFloat',  {{ fg = '{c["base05"]}', bg = '{c["base01"]}' }})
hi('FloatBorder',  {{ fg = '{c["base03"]}', bg = '{c["base01"]}' }})
hi('FloatTitle',   {{ fg = '{c["base07"]}', bg = '{c["base01"]}', bold = true }})
hi('Cursor',       {{ fg = '{c["base00"]}', bg = '{c["base07"]}' }})
hi('CursorLine',   {{ bg = '{c["base01"]}' }})
hi('CursorLineNr', {{ fg = '{c["base07"]}', bg = '{c["base01"]}', bold = true }})
hi('LineNr',       {{ fg = '{c["base03"]}' }})
hi('Visual',       {{ bg = '{c["base02"]}' }})
hi('VisualNOS',    {{ bg = '{c["base02"]}' }})
hi('Search',       {{ fg = '{c["base00"]}', bg = '{c["base0A"]}' }})
hi('IncSearch',    {{ fg = '{c["base00"]}', bg = '{c["base09"]}' }})
hi('CurSearch',    {{ fg = '{c["base00"]}', bg = '{c["base09"]}' }})
hi('Substitute',   {{ fg = '{c["base00"]}', bg = '{c["base09"]}' }})
hi('StatusLine',   {{ fg = '{c["base07"]}', bg = '{c["base01"]}' }})
hi('StatusLineNC', {{ fg = '{c["base04"]}', bg = '{c["base01"]}' }})
hi('TabLine',      {{ fg = '{c["base04"]}', bg = '{c["base01"]}' }})
hi('TabLineFill',  {{ bg = '{c["base00"]}' }})
hi('TabLineSel',   {{ fg = '{c["base07"]}', bg = '{c["base00"]}' }})
hi('WinSeparator', {{ fg = '{c["base02"]}' }})
hi('Pmenu',        {{ fg = '{c["base05"]}', bg = '{c["base01"]}' }})
hi('PmenuSel',     {{ fg = '{c["base07"]}', bg = '{c["base02"]}' }})
hi('PmenuSbar',    {{ bg = '{c["base02"]}' }})
hi('PmenuThumb',   {{ bg = '{c["base04"]}' }})
hi('Folded',       {{ fg = '{c["base04"]}', bg = '{c["base01"]}' }})
hi('FoldColumn',   {{ fg = '{c["base03"]}', bg = '{c["base00"]}' }})
hi('SignColumn',   {{ fg = '{c["base03"]}', bg = '{c["base00"]}' }})
hi('ColorColumn',  {{ bg = '{c["base01"]}' }})
hi('MatchParen',   {{ fg = '{c["base07"]}', bg = '{c["base02"]}', bold = true }})
hi('Directory',    {{ fg = '{c["base0D"]}' }})
hi('Title',        {{ fg = '{c["base07"]}', bold = true }})
hi('ErrorMsg',     {{ fg = '{c["base08"]}' }})
hi('WarningMsg',   {{ fg = '{c["base09"]}' }})
hi('MoreMsg',      {{ fg = '{c["base0B"]}' }})
hi('Question',     {{ fg = '{c["base0B"]}' }})
hi('ModeMsg',      {{ fg = '{c["base07"]}', bold = true }})
hi('NonText',      {{ fg = '{c["base02"]}' }})
hi('SpecialKey',   {{ fg = '{c["base02"]}' }})
hi('Whitespace',   {{ fg = '{c["base02"]}' }})
hi('Conceal',      {{ fg = '{c["base04"]}' }})
hi('SpellBad',     {{ undercurl = true, sp = '{c["base08"]}' }})
hi('SpellCap',     {{ undercurl = true, sp = '{c["base09"]}' }})
hi('SpellLocal',   {{ undercurl = true, sp = '{c["base0C"]}' }})
hi('SpellRare',    {{ undercurl = true, sp = '{c["base0E"]}' }})
hi('WildMenu',     {{ fg = '{c["base00"]}', bg = '{c["base0A"]}' }})

-- ============================================================================
-- Diff
-- ============================================================================
hi('DiffAdd',    {{ bg = '#0e2919' }})
hi('DiffChange', {{ bg = '#2b2311' }})
hi('DiffDelete', {{ fg = '{c["base08"]}', bg = '#2e1525' }})
hi('DiffText',   {{ bg = '#3d3118' }})
hi('Added',      {{ fg = '{c["base13"]}' }})
hi('Changed',    {{ fg = '{c["base0A"]}' }})
hi('Removed',    {{ fg = '{c["base10"]}' }})

-- ============================================================================
-- Syntax (quiet accents for code, loud reserved for signals)
-- ============================================================================
hi('Comment',     {{ fg = '{c["base03"]}', italic = true }})
hi('String',      {{ fg = '{c["base17"]}' }})
hi('Character',   {{ fg = '{c["base17"]}' }})
hi('Number',      {{ fg = '{c["base12"]}' }})
hi('Float',       {{ fg = '{c["base12"]}' }})
hi('Boolean',     {{ fg = '{c["base12"]}' }})
hi('Constant',    {{ fg = '{c["base12"]}' }})
hi('Identifier',  {{ fg = '{c["base07"]}' }})
hi('Function',    {{ fg = '{c["base15"]}' }})
hi('Statement',   {{ fg = '{c["base10"]}' }})
hi('Keyword',     {{ fg = '{c["base10"]}' }})
hi('Conditional', {{ fg = '{c["base10"]}' }})
hi('Repeat',      {{ fg = '{c["base10"]}' }})
hi('Operator',    {{ fg = '{c["base04"]}' }})
hi('Exception',   {{ fg = '{c["base10"]}' }})
hi('PreProc',     {{ fg = '{c["base10"]}' }})
hi('Include',     {{ fg = '{c["base10"]}' }})
hi('Define',      {{ fg = '{c["base10"]}' }})
hi('Macro',       {{ fg = '{c["base11"]}' }})
hi('Type',        {{ fg = '{c["base14"]}' }})
hi('StorageClass',{{ fg = '{c["base14"]}', italic = true }})
hi('Structure',   {{ fg = '{c["base14"]}' }})
hi('Typedef',     {{ fg = '{c["base14"]}' }})
hi('Special',     {{ fg = '{c["base11"]}' }})
hi('SpecialChar', {{ fg = '{c["base12"]}' }})
hi('Tag',         {{ fg = '{c["base10"]}' }})
hi('Delimiter',   {{ fg = '{c["base04"]}' }})
hi('Debug',       {{ fg = '{c["base08"]}' }})
hi('Underlined',  {{ fg = '{c["base0D"]}', underline = true }})
hi('Error',       {{ fg = '{c["base08"]}' }})
hi('Todo',        {{ fg = '{c["base0F"]}', bg = '{c["base00"]}', bold = true }})

-- ============================================================================
-- Treesitter highlight groups (Neovim 0.9+)
-- ============================================================================
hi('@comment',               {{ link = 'Comment' }})
hi('@string',                {{ link = 'String' }})
hi('@string.escape',         {{ fg = '{c["base12"]}' }})
hi('@character',             {{ link = 'Character' }})
hi('@number',                {{ link = 'Number' }})
hi('@float',                 {{ link = 'Float' }})
hi('@boolean',               {{ link = 'Boolean' }})
hi('@constant',              {{ link = 'Constant' }})
hi('@constant.builtin',      {{ fg = '{c["base12"]}' }})
hi('@variable',              {{ fg = '{c["base07"]}' }})
hi('@variable.parameter',    {{ fg = '{c["base16"]}', italic = true }})
hi('@variable.builtin',      {{ fg = '{c["base07"]}' }})
hi('@variable.member',       {{ fg = '{c["base07"]}' }})
hi('@function',              {{ link = 'Function' }})
hi('@function.call',         {{ fg = '{c["base15"]}' }})
hi('@function.builtin',      {{ fg = '{c["base15"]}' }})
hi('@function.method',       {{ fg = '{c["base15"]}' }})
hi('@function.method.call',  {{ fg = '{c["base15"]}' }})
hi('@keyword',               {{ link = 'Keyword' }})
hi('@keyword.function',      {{ fg = '{c["base10"]}' }})
hi('@keyword.return',        {{ fg = '{c["base10"]}' }})
hi('@keyword.operator',      {{ fg = '{c["base04"]}' }})
hi('@keyword.import',        {{ fg = '{c["base10"]}' }})
hi('@keyword.storage',       {{ fg = '{c["base14"]}', italic = true }})
hi('@type',                  {{ link = 'Type' }})
hi('@type.builtin',          {{ fg = '{c["base14"]}' }})
hi('@type.definition',       {{ fg = '{c["base14"]}' }})
hi('@constructor',           {{ fg = '{c["base14"]}' }})
hi('@operator',              {{ link = 'Operator' }})
hi('@punctuation',           {{ fg = '{c["base04"]}' }})
hi('@punctuation.bracket',   {{ fg = '{c["base04"]}' }})
hi('@punctuation.delimiter', {{ fg = '{c["base04"]}' }})
hi('@punctuation.special',   {{ fg = '{c["base11"]}' }})
hi('@tag',                   {{ fg = '{c["base10"]}' }})
hi('@tag.attribute',         {{ fg = '{c["base14"]}', italic = true }})
hi('@tag.delimiter',         {{ fg = '{c["base04"]}' }})
hi('@attribute',             {{ fg = '{c["base11"]}' }})
hi('@property',              {{ fg = '{c["base07"]}' }})
hi('@label',                 {{ fg = '{c["base16"]}' }})
hi('@module',                {{ fg = '{c["base14"]}' }})

-- Markup (markdown)
hi('@markup',                {{ fg = '{c["base07"]}' }})
hi('HppMarkdownNormal',     {{ fg = '{c["base07"]}', bg = '{c["base00"]}' }})
hi('@conceal.markdown_inline', {{ fg = '{c["base04"]}' }})
hi('@conceal.markdown',        {{ fg = '{c["base04"]}' }})
hi('@markup.heading',        {{ fg = '{c["base07"]}', bold = true }})
hi('@markup.heading.1',      {{ fg = '{c["base00"]}', bg = '{c["base0F"]}', bold = true }})
hi('@markup.heading.2',      {{ fg = '{c["base08"]}', bold = true }})
hi('@markup.heading.3',      {{ fg = '{c["base08"]}' }})
hi('@markup.heading.4',      {{ fg = '{c["base08"]}' }})
hi('@markup.heading.5',      {{ fg = '{c["base08"]}' }})
hi('@markup.heading.6',      {{ fg = '{c["base08"]}' }})
hi('@markup.strong',         {{ fg = '{c["base0D"]}', bold = true }})
hi('@markup.italic',         {{ fg = '{c["base15"]}', italic = true }})
hi('@markup.raw',            {{ fg = '{c["base0A"]}' }})
hi('@markup.raw.block',      {{ fg = '{c["base14"]}' }})
hi('@markup.link',           {{ fg = '{c["base17"]}' }})
hi('@markup.link.url',       {{ fg = '{c["base03"]}', underline = true }})
hi('@markup.list',           {{ fg = '{c["base04"]}' }})
hi('@markup.quote',          {{ fg = '{c["base14"]}', italic = true }})
hi('@markup.strikethrough',  {{ strikethrough = true }})
hi('@punctuation.special.markdown', {{ fg = '{c["base04"]}' }})

-- Traditional vim markdown syntax groups (fallback for non-treesitter)
hi('markdownH1',                  {{ fg = '{c["base00"]}', bg = '{c["base0F"]}', bold = true }})
hi('markdownH2',                  {{ fg = '{c["base08"]}', bold = true }})
hi('markdownH3',                  {{ fg = '{c["base08"]}' }})
hi('markdownH4',                  {{ fg = '{c["base08"]}' }})
hi('markdownH5',                  {{ fg = '{c["base08"]}' }})
hi('markdownH6',                  {{ fg = '{c["base08"]}' }})
hi('markdownHeadingDelimiter',    {{ fg = '{c["base08"]}' }})
hi('markdownBold',                {{ fg = '{c["base0D"]}', bold = true }})
hi('markdownItalic',              {{ fg = '{c["base15"]}', italic = true }})
hi('markdownBoldItalic',          {{ fg = '{c["base0D"]}', bold = true, italic = true }})
hi('markdownCode',                {{ fg = '{c["base0A"]}' }})
hi('markdownCodeBlock',           {{ fg = '{c["base14"]}' }})
hi('markdownCodeDelimiter',       {{ fg = '{c["base04"]}' }})
hi('markdownLinkText',            {{ fg = '{c["base17"]}' }})
hi('markdownUrl',                 {{ fg = '{c["base03"]}', underline = true }})
hi('markdownListMarker',          {{ fg = '{c["base04"]}' }})
hi('markdownOrderedListMarker',   {{ fg = '{c["base04"]}' }})
hi('markdownBlockquote',          {{ fg = '{c["base14"]}', italic = true }})
hi('markdownRule',                {{ fg = '{c["base04"]}' }})
hi('markdownStrikethrough',       {{ strikethrough = true }})
hi('htmlH1',                      {{ fg = '{c["base00"]}', bg = '{c["base0F"]}', bold = true }})
hi('htmlH2',                      {{ fg = '{c["base08"]}', bold = true }})
hi('htmlH3',                      {{ fg = '{c["base08"]}' }})
hi('htmlH4',                      {{ fg = '{c["base08"]}' }})
hi('htmlH5',                      {{ fg = '{c["base08"]}' }})
hi('htmlH6',                      {{ fg = '{c["base08"]}' }})
hi('htmlBold',                    {{ fg = '{c["base0D"]}', bold = true }})
hi('htmlItalic',                  {{ fg = '{c["base15"]}', italic = true }})
hi('mkdHeading',                  {{ fg = '{c["base08"]}' }})
hi('mkdCode',                     {{ fg = '{c["base0A"]}' }})
hi('mkdCodeDelimiter',            {{ fg = '{c["base04"]}' }})
hi('mkdCodeStart',                {{ fg = '{c["base04"]}' }})
hi('mkdCodeEnd',                  {{ fg = '{c["base04"]}' }})
hi('mkdLink',                     {{ fg = '{c["base17"]}' }})
hi('mkdURL',                      {{ fg = '{c["base03"]}', underline = true }})
hi('mkdBlockquote',               {{ fg = '{c["base14"]}', italic = true }})
hi('mkdListItem',                 {{ fg = '{c["base04"]}' }})
hi('mkdRule',                     {{ fg = '{c["base04"]}' }})

hi('@diff.plus',             {{ fg = '{c["base13"]}' }})
hi('@diff.minus',            {{ fg = '{c["base10"]}' }})
hi('@diff.delta',            {{ fg = '{c["base0A"]}' }})

-- ============================================================================
-- LSP Diagnostics
-- ============================================================================
hi('DiagnosticError',            {{ fg = '{c["base08"]}' }})
hi('DiagnosticWarn',             {{ fg = '{c["base09"]}' }})
hi('DiagnosticInfo',             {{ fg = '{c["base0C"]}' }})
hi('DiagnosticHint',             {{ fg = '{c["base15"]}' }})
hi('DiagnosticUnderlineError',   {{ undercurl = true, sp = '{c["base08"]}' }})
hi('DiagnosticUnderlineWarn',    {{ undercurl = true, sp = '{c["base09"]}' }})
hi('DiagnosticUnderlineInfo',    {{ undercurl = true, sp = '{c["base0C"]}' }})
hi('DiagnosticUnderlineHint',    {{ undercurl = true, sp = '{c["base15"]}' }})
hi('DiagnosticVirtualTextError', {{ fg = '{c["base08"]}', bg = '{c["base01"]}' }})
hi('DiagnosticVirtualTextWarn',  {{ fg = '{c["base09"]}', bg = '{c["base01"]}' }})
hi('DiagnosticVirtualTextInfo',  {{ fg = '{c["base0C"]}', bg = '{c["base01"]}' }})
hi('DiagnosticVirtualTextHint',  {{ fg = '{c["base15"]}', bg = '{c["base01"]}' }})
hi('DiagnosticSignError',        {{ fg = '{c["base08"]}' }})
hi('DiagnosticSignWarn',         {{ fg = '{c["base09"]}' }})
hi('DiagnosticSignInfo',         {{ fg = '{c["base0C"]}' }})
hi('DiagnosticSignHint',         {{ fg = '{c["base15"]}' }})

-- ============================================================================
-- Git signs (gitsigns.nvim etc.)
-- ============================================================================
hi('GitSignsAdd',    {{ fg = '{c["base0B"]}' }})
hi('GitSignsChange', {{ fg = '{c["base0A"]}' }})
hi('GitSignsDelete', {{ fg = '{c["base08"]}' }})

-- ============================================================================
-- Telescope
-- ============================================================================
hi('TelescopeNormal',       {{ fg = '{c["base05"]}', bg = '{c["base00"]}' }})
hi('TelescopeBorder',       {{ fg = '{c["base03"]}', bg = '{c["base00"]}' }})
hi('TelescopePromptNormal', {{ fg = '{c["base07"]}', bg = '{c["base01"]}' }})
hi('TelescopePromptBorder', {{ fg = '{c["base01"]}', bg = '{c["base01"]}' }})
hi('TelescopePromptTitle',  {{ fg = '{c["base00"]}', bg = '{c["base0D"]}' }})
hi('TelescopePreviewTitle', {{ fg = '{c["base00"]}', bg = '{c["base0B"]}' }})
hi('TelescopeResultsTitle', {{ fg = '{c["base00"]}', bg = '{c["base0C"]}' }})
hi('TelescopeSelection',    {{ bg = '{c["base01"]}' }})
hi('TelescopeMatching',     {{ fg = '{c["base0A"]}', bold = true }})

-- ============================================================================
-- Human++ custom groups (used by the runtime plugin)
-- ============================================================================
hi('HppMarkerIntervention', {{ fg = '{c["base00"]}', bg = '{c["base0F"]}', bold = true }})
hi('HppMarkerUncertainty',  {{ fg = '{c["base07"]}', bg = '{c["base0E"]}', bold = true }})
hi('HppMarkerDirective',    {{ fg = '{c["base00"]}', bg = '{c["base0C"]}', bold = true }})
hi('HppDiagError',          {{ fg = '{c["base00"]}', bg = '{c["base08"]}' }})
hi('HppDiagWarn',           {{ fg = '{c["base00"]}', bg = '{c["base09"]}' }})
hi('HppDiagInfo',           {{ fg = '{c["base00"]}', bg = '{c["base0C"]}' }})
hi('HppDiagHint',           {{ fg = '{c["base07"]}', bg = '{c["base15"]}' }})
hi('HppMarkdownH1',         {{ fg = '{c["base00"]}', bg = '{c["base0F"]}', bold = true }})
hi('HppMarkdownH2',         {{ fg = '{c["base08"]}', bold = true }})
hi('HppMarkdownH3',         {{ fg = '{c["base08"]}' }})
hi('HppMarkdownH4',         {{ fg = '{c["base08"]}' }})
hi('HppMarkdownH5',         {{ fg = '{c["base08"]}' }})
hi('HppMarkdownH6',         {{ fg = '{c["base08"]}' }})
'''

    # Write to packages/neovim-plugin/colors/
    nvim_dir = PACKAGES / "neovim-plugin/colors"
    nvim_dir.mkdir(parents=True, exist_ok=True)
    (nvim_dir / "humanplusplus.lua").write_text(content)
    print("  ✓ packages/neovim-plugin/colors/humanplusplus.lua")


def generate_vim(colors, meta):
    """Generate vanilla-vim colorscheme (vimscript) from palette.

    Mirrors the neovim plugin's highlight set but as vimscript, so users
    running plain `vim` (no lua) get the same look. Also generates a
    matching lightline theme.
    """
    c = colors

    # palette block — only piece interpolated from palette.toml.
    # The rest of the file references s:baseXX vim-level variables.
    palette_block = '\n'.join([
        f"let s:base00 = '{c['base00']}'",
        f"let s:base01 = '{c['base01']}'",
        f"let s:base02 = '{c['base02']}'",
        f"let s:base03 = '{c['base03']}'",
        f"let s:base04 = '{c['base04']}'",
        f"let s:base05 = '{c['base05']}'",
        f"let s:base06 = '{c['base06']}'",
        f"let s:base07 = '{c['base07']}'",
        f"let s:base08 = '{c['base08']}'",
        f"let s:base09 = '{c['base09']}'",
        f"let s:base0A = '{c['base0A']}'",
        f"let s:base0B = '{c['base0B']}'",
        f"let s:base0C = '{c['base0C']}'",
        f"let s:base0D = '{c['base0D']}'",
        f"let s:base0E = '{c['base0E']}'",
        f"let s:base0F = '{c['base0F']}'",
        f"let s:base10 = '{c['base10']}'",
        f"let s:base11 = '{c['base11']}'",
        f"let s:base12 = '{c['base12']}'",
        f"let s:base13 = '{c['base13']}'",
        f"let s:base14 = '{c['base14']}'",
        f"let s:base15 = '{c['base15']}'",
        f"let s:base16 = '{c['base16']}'",
        f"let s:base17 = '{c['base17']}'",
    ])

    colorscheme = f'''" Human++ vim colorscheme
" Generated from palette.toml — DO NOT EDIT
" Rebuild: make build

hi clear
if exists('syntax_on')
  syntax reset
endif
let g:colors_name = 'humanplusplus'
set background=dark

if has('termguicolors') && !&termguicolors
  set termguicolors
endif

" palette ---------------------------------------------------------------------
{palette_block}

" helper ----------------------------------------------------------------------
function! s:hi(group, fg, bg, ...) abort
  let l:cmd = 'hi ' . a:group
  if a:fg !=# ''
    let l:cmd .= ' guifg=' . a:fg
  endif
  if a:bg !=# ''
    let l:cmd .= ' guibg=' . a:bg
  endif
  if a:0 && !empty(a:1)
    let l:cmd .= ' gui=' . a:1 . ' cterm=' . a:1
  else
    let l:cmd .= ' gui=NONE cterm=NONE'
  endif
  execute l:cmd
endfunction

" editor UI -------------------------------------------------------------------
call s:hi('Normal',       s:base05, s:base00, '')
call s:hi('NormalNC',     s:base05, s:base00, '')
call s:hi('NormalFloat',  s:base05, s:base01, '')
call s:hi('FloatBorder',  s:base03, s:base01, '')
call s:hi('FloatTitle',   s:base07, s:base01, 'bold')
call s:hi('Cursor',       s:base00, s:base07, '')
call s:hi('CursorLine',   '',       s:base01, '')
call s:hi('CursorColumn', '',       s:base01, '')
call s:hi('CursorLineNr', s:base07, s:base01, 'bold')
call s:hi('LineNr',       s:base03, '',       '')
call s:hi('Visual',       '',       s:base02, '')
call s:hi('VisualNOS',    '',       s:base02, '')
call s:hi('Search',       s:base00, s:base0A, '')
call s:hi('IncSearch',    s:base00, s:base09, '')
call s:hi('CurSearch',    s:base00, s:base09, '')
call s:hi('Substitute',   s:base00, s:base09, '')
call s:hi('StatusLine',   s:base07, s:base01, '')
call s:hi('StatusLineNC', s:base04, s:base01, '')
call s:hi('TabLine',      s:base04, s:base01, '')
call s:hi('TabLineFill',  '',       s:base00, '')
call s:hi('TabLineSel',   s:base07, s:base00, '')
call s:hi('VertSplit',    s:base02, '',       '')
call s:hi('WinSeparator', s:base02, '',       '')
call s:hi('Pmenu',        s:base05, s:base01, '')
call s:hi('PmenuSel',     s:base07, s:base02, '')
call s:hi('PmenuSbar',    '',       s:base02, '')
call s:hi('PmenuThumb',   '',       s:base04, '')
call s:hi('Folded',       s:base04, s:base01, '')
call s:hi('FoldColumn',   s:base03, s:base00, '')
call s:hi('SignColumn',   s:base03, s:base00, '')
call s:hi('ColorColumn',  '',       s:base01, '')
call s:hi('MatchParen',   s:base07, s:base02, 'bold')
call s:hi('Directory',    s:base0D, '',       '')
call s:hi('Title',        s:base07, '',       'bold')
call s:hi('ErrorMsg',     s:base08, '',       '')
call s:hi('WarningMsg',   s:base09, '',       '')
call s:hi('MoreMsg',      s:base0B, '',       '')
call s:hi('Question',     s:base0B, '',       '')
call s:hi('ModeMsg',      s:base07, '',       'bold')
call s:hi('NonText',      s:base02, '',       '')
call s:hi('EndOfBuffer',  s:base02, s:base00, '')
call s:hi('SpecialKey',   s:base02, '',       '')
call s:hi('Whitespace',   s:base02, '',       '')
call s:hi('Conceal',      s:base04, '',       '')
call s:hi('WildMenu',     s:base00, s:base0A, '')
exe 'hi SpellBad   gui=undercurl cterm=undercurl guisp=' . s:base08
exe 'hi SpellCap   gui=undercurl cterm=undercurl guisp=' . s:base09
exe 'hi SpellLocal gui=undercurl cterm=undercurl guisp=' . s:base0C
exe 'hi SpellRare  gui=undercurl cterm=undercurl guisp=' . s:base0E

" diff ------------------------------------------------------------------------
call s:hi('DiffAdd',    '',       '#0e2919', '')
call s:hi('DiffChange', '',       '#2b2311', '')
call s:hi('DiffDelete', s:base08, '#2e1525', '')
call s:hi('DiffText',   '',       '#3d3118', '')
call s:hi('Added',      s:base13, '',        '')
call s:hi('Changed',    s:base0A, '',        '')
call s:hi('Removed',    s:base10, '',        '')

" syntax (quiet accents for code, loud reserved for signals) -----------------
call s:hi('Comment',      s:base03, '', 'italic')
call s:hi('String',       s:base17, '', '')
call s:hi('Character',    s:base17, '', '')
call s:hi('Number',       s:base12, '', '')
call s:hi('Float',        s:base12, '', '')
call s:hi('Boolean',      s:base12, '', '')
call s:hi('Constant',     s:base12, '', '')
call s:hi('Identifier',   s:base07, '', '')
call s:hi('Function',     s:base15, '', '')
call s:hi('Statement',    s:base10, '', '')
call s:hi('Keyword',      s:base10, '', '')
call s:hi('Conditional',  s:base10, '', '')
call s:hi('Repeat',       s:base10, '', '')
call s:hi('Operator',     s:base04, '', '')
call s:hi('Exception',    s:base10, '', '')
call s:hi('PreProc',      s:base10, '', '')
call s:hi('Include',      s:base10, '', '')
call s:hi('Define',       s:base10, '', '')
call s:hi('Macro',        s:base11, '', '')
call s:hi('Type',         s:base14, '', '')
call s:hi('StorageClass', s:base14, '', 'italic')
call s:hi('Structure',    s:base14, '', '')
call s:hi('Typedef',      s:base14, '', '')
call s:hi('Special',      s:base11, '', '')
call s:hi('SpecialChar',  s:base12, '', '')
call s:hi('Tag',          s:base10, '', '')
call s:hi('Delimiter',    s:base04, '', '')
call s:hi('Debug',        s:base08, '', '')
call s:hi('Underlined',   s:base0D, '', 'underline')
call s:hi('Error',        s:base08, '', '')
call s:hi('Todo',         s:base0F, s:base00, 'bold')

" markdown (vim native syntax) ------------------------------------------------
call s:hi('markdownH1',                s:base00, s:base0F, 'bold')
call s:hi('markdownH2',                s:base08, '',       'bold')
call s:hi('markdownH3',                s:base08, '',       '')
call s:hi('markdownH4',                s:base08, '',       '')
call s:hi('markdownH5',                s:base08, '',       '')
call s:hi('markdownH6',                s:base08, '',       '')
call s:hi('markdownHeadingDelimiter',  s:base08, '',       '')
call s:hi('markdownBold',              s:base0D, '',       'bold')
call s:hi('markdownItalic',            s:base15, '',       'italic')
call s:hi('markdownBoldItalic',        s:base0D, '',       'bold,italic')
call s:hi('markdownCode',              s:base0A, '',       '')
call s:hi('markdownCodeBlock',         s:base14, '',       '')
call s:hi('markdownCodeDelimiter',     s:base04, '',       '')
call s:hi('markdownLinkText',          s:base17, '',       '')
call s:hi('markdownUrl',               s:base03, '',       'underline')
call s:hi('markdownListMarker',        s:base04, '',       '')
call s:hi('markdownOrderedListMarker', s:base04, '',       '')
call s:hi('markdownBlockquote',        s:base14, '',       'italic')
call s:hi('markdownRule',              s:base04, '',       '')
call s:hi('htmlH1',                    s:base00, s:base0F, 'bold')
call s:hi('htmlH2',                    s:base08, '',       'bold')
call s:hi('htmlBold',                  s:base0D, '',       'bold')
call s:hi('htmlItalic',                s:base15, '',       'italic')

" ALE -------------------------------------------------------------------------
call s:hi('ALEErrorSign',   s:base08, s:base00, '')
call s:hi('ALEWarningSign', s:base09, s:base00, '')
call s:hi('ALEInfoSign',    s:base0C, s:base00, '')
call s:hi('ALEError',       '',       '',       'undercurl')
call s:hi('ALEWarning',     '',       '',       'undercurl')

" gitgutter -------------------------------------------------------------------
call s:hi('GitGutterAdd',          s:base0B, s:base00, '')
call s:hi('GitGutterChange',       s:base0A, s:base00, '')
call s:hi('GitGutterDelete',       s:base08, s:base00, '')
call s:hi('GitGutterChangeDelete', s:base09, s:base00, '')

" indent-guides ---------------------------------------------------------------
call s:hi('IndentGuidesOdd',  '', s:base00, '')
call s:hi('IndentGuidesEven', '', s:base01, '')

" startify --------------------------------------------------------------------
call s:hi('StartifyHeader',  s:base0F, '', 'bold')
call s:hi('StartifyFile',    s:base05, '', '')
call s:hi('StartifyPath',    s:base04, '', '')
call s:hi('StartifySlash',   s:base03, '', '')
call s:hi('StartifyBracket', s:base03, '', '')
call s:hi('StartifyNumber',  s:base0A, '', 'bold')
call s:hi('StartifySection', s:base0C, '', 'bold')
call s:hi('StartifySpecial', s:base04, '', '')
call s:hi('StartifyFooter',  s:base03, '', 'italic')

" terminal colors -------------------------------------------------------------
if has('nvim')
  let g:terminal_color_0  = s:base00
  let g:terminal_color_1  = s:base08
  let g:terminal_color_2  = s:base0B
  let g:terminal_color_3  = s:base0A
  let g:terminal_color_4  = s:base0D
  let g:terminal_color_5  = s:base0E
  let g:terminal_color_6  = s:base0C
  let g:terminal_color_7  = s:base06
  let g:terminal_color_8  = s:base03
  let g:terminal_color_9  = s:base10
  let g:terminal_color_10 = s:base13
  let g:terminal_color_11 = s:base12
  let g:terminal_color_12 = s:base15
  let g:terminal_color_13 = s:base16
  let g:terminal_color_14 = s:base14
  let g:terminal_color_15 = s:base07
endif
'''

    lightline = f'''" Lightline theme — Human++ Base24
" Generated from palette.toml — DO NOT EDIT
" Rebuild: make build
"
" Mode color mapping:
"   normal=blue, insert=green, visual=purple, replace=red, tabsel=lime

let s:base00  = [ '{c['base00']}', 0  ]
let s:base01  = [ '{c['base01']}', 8  ]
let s:base02  = [ '{c['base02']}', 8  ]
let s:base03  = [ '{c['base03']}', 8  ]
let s:base04  = [ '{c['base04']}', 7  ]
let s:base05  = [ '{c['base05']}', 15 ]
let s:base06  = [ '{c['base06']}', 15 ]
let s:base07  = [ '{c['base07']}', 15 ]

let s:red     = [ '{c['base08']}', 1  ]
let s:orange  = [ '{c['base09']}', 9  ]
let s:amber   = [ '{c['base0A']}', 3  ]
let s:green   = [ '{c['base0B']}', 2  ]
let s:cyan    = [ '{c['base0C']}', 6  ]
let s:blue    = [ '{c['base0D']}', 4  ]
let s:purple  = [ '{c['base0E']}', 5  ]
let s:lime    = [ '{c['base0F']}', 10 ]

let s:p = {{'normal': {{}}, 'inactive': {{}}, 'insert': {{}}, 'replace': {{}}, 'visual': {{}}, 'tabline': {{}}}}

let s:p.normal.left    = [ [ s:base00, s:blue   ], [ s:base06, s:base02 ] ]
let s:p.normal.right   = [ [ s:base00, s:base04 ], [ s:base05, s:base02 ] ]
let s:p.normal.middle  = [ [ s:base04, s:base01 ] ]
let s:p.normal.error   = [ [ s:base07, s:red    ] ]
let s:p.normal.warning = [ [ s:base00, s:amber  ] ]

let s:p.insert.left    = [ [ s:base00, s:green  ], [ s:base06, s:base02 ] ]
let s:p.insert.right   = copy(s:p.normal.right)
let s:p.insert.middle  = copy(s:p.normal.middle)

let s:p.replace.left   = [ [ s:base00, s:red    ], [ s:base06, s:base02 ] ]
let s:p.replace.right  = copy(s:p.normal.right)
let s:p.replace.middle = copy(s:p.normal.middle)

let s:p.visual.left    = [ [ s:base00, s:purple ], [ s:base06, s:base02 ] ]
let s:p.visual.right   = copy(s:p.normal.right)
let s:p.visual.middle  = copy(s:p.normal.middle)

let s:p.inactive.left   = [ [ s:base04, s:base01 ], [ s:base03, s:base01 ] ]
let s:p.inactive.right  = [ [ s:base04, s:base01 ], [ s:base03, s:base01 ] ]
let s:p.inactive.middle = [ [ s:base03, s:base01 ] ]

let s:p.tabline.left    = [ [ s:base05, s:base02 ] ]
let s:p.tabline.tabsel  = [ [ s:base00, s:lime   ] ]
let s:p.tabline.middle  = [ [ s:base03, s:base00 ] ]
let s:p.tabline.right   = [ [ s:base05, s:base02 ] ]

let g:lightline#colorscheme#humanplusplus#palette = lightline#colorscheme#flatten(s:p)
'''

    colors_dir = PACKAGES / "vim-plugin/colors"
    colors_dir.mkdir(parents=True, exist_ok=True)
    (colors_dir / "humanplusplus.vim").write_text(colorscheme)
    print("  ✓ packages/vim-plugin/colors/humanplusplus.vim")

    lightline_dir = PACKAGES / "vim-plugin/autoload/lightline/colorscheme"
    lightline_dir.mkdir(parents=True, exist_ok=True)
    (lightline_dir / "humanplusplus.vim").write_text(lightline)
    print("  ✓ packages/vim-plugin/autoload/lightline/colorscheme/humanplusplus.vim")


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
    generate_tmux(colors, meta)
    generate_eza(colors, meta)
    generate_fzf(colors, meta)
    generate_bat(colors, meta)
    generate_glow(colors, meta)
    generate_delta(colors, meta)
    generate_git_colors(colors, meta)
    generate_fastfetch(colors, meta)
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

    print("\nGenerating Zed theme:")
    generate_zed_theme(colors, meta)

    print("\nGenerating Neovim plugin:")
    generate_neovim(colors, meta)

    print("\nGenerating Vim plugin:")
    generate_vim(colors, meta)

    print("\n✓ Build complete!")
    print("\nTo apply: tinty apply base24-human-plus-plus")


if __name__ == '__main__':
    main()
