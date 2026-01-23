#!/usr/bin/env python3
"""
Human++ Build Script

Generates all theme files from palette.toml (the single source of truth).

Usage: python3 build.py
"""

import re
import os
import json
from pathlib import Path

ROOT = Path(__file__).parent
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

    (ROOT / "ghostty/config").write_text(content)
    print("  ✓ ghostty/config")


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

    (ROOT / "sketchybar/colors.sh").write_text(content)
    print("  ✓ sketchybar/colors.sh")


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

    (ROOT / "borders/bordersrc").write_text(content)
    print("  ✓ borders/bordersrc")


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

    (ROOT / "skhd/modes.sh").write_text(content)
    print("  ✓ skhd/modes.sh")


def generate_swatches_html(colors, meta):
    """Generate swatches.html landing page with highlight.js."""
    c = colors

    # Build CSS variables
    css_vars = '\n'.join([f'      --{k}: {v};' for k, v in c.items()])

    # Build highlight.js theme CSS
    hljs_css = f'''
    /* highlight.js Human++ theme */
    .hljs {{
      background: var(--base00);
      color: var(--base05);
    }}
    .hljs-comment,
    .hljs-quote {{ color: var(--base03); }}
    .hljs-keyword,
    .hljs-selector-tag {{ color: var(--base10); }}
    .hljs-string,
    .hljs-template-string {{ color: var(--base12); }}
    .hljs-title,
    .hljs-title.function_,
    .hljs-function {{ color: var(--base13); }}
    .hljs-type,
    .hljs-built_in,
    .hljs-class {{ color: var(--base14); }}
    .hljs-number,
    .hljs-literal {{ color: var(--base16); }}
    .hljs-variable,
    .hljs-template-variable,
    .hljs-attr {{ color: var(--base11); }}
    .hljs-attribute {{ color: var(--base15); }}
    .hljs-symbol,
    .hljs-bullet {{ color: var(--base0B); }}
    .hljs-subst {{ color: var(--base05); }}
    .hljs-section {{ color: var(--base0D); font-weight: bold; }}
    .hljs-selector-class,
    .hljs-selector-id {{ color: var(--base14); }}
    .hljs-emphasis {{ font-style: italic; }}
    .hljs-strong {{ font-weight: bold; }}
    .hljs-link {{ color: var(--base0D); text-decoration: underline; }}
    .hljs-addition {{ color: var(--base0B); background-color: rgba(4, 179, 114, 0.1); }}
    .hljs-deletion {{ color: var(--base08); background-color: rgba(217, 4, 142, 0.1); }}

    /* Human++ marker highlighting - matches VS Code extension */
    .hljs-comment.humanpp-attention {{
      color: var(--base00);
      background: var(--base0F);
      padding: 2px 6px;
      border-radius: 3px;
      font-weight: bold;
    }}
    .hljs-comment.humanpp-uncertainty {{
      color: var(--base07);
      background: var(--base0E);
      padding: 2px 6px;
      border-radius: 3px;
      font-weight: bold;
    }}
    .hljs-comment.humanpp-reference {{
      color: var(--base00);
      background: var(--base0C);
      padding: 2px 6px;
      border-radius: 3px;
      font-weight: bold;
    }}
    '''

    # Build JS palette object
    roles = {
        'base00': 'background', 'base01': 'elevation', 'base02': 'selection',
        'base03': 'comments', 'base04': 'UI secondary', 'base05': 'main text',
        'base06': 'emphasis', 'base07': 'brightest',
        'base08': 'errors', 'base09': 'warnings', 'base0A': 'caution',
        'base0B': 'success', 'base0C': 'info', 'base0D': 'links',
        'base0E': 'special', 'base0F': 'human !!',
        'base10': 'keywords', 'base11': 'secondary', 'base12': 'strings',
        'base13': 'functions', 'base14': 'types', 'base15': 'hints',
        'base16': 'constants', 'base17': 'quiet lime',
    }

    js_palette = ',\n      '.join([
        f"{k}: {{ hex: '{v}', role: '{roles.get(k, '')}' }}"
        for k, v in c.items()
    ])

    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Human++ — A color scheme for the post-artisanal coding era</title>
  <meta name="description" content="Code is cheap. Intent is scarce. Human++ is a Base24 color scheme that makes human judgment visible at a glance.">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/base16/default-dark.min.css">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
{css_vars}
    }}
    {hljs_css}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif;
      background: var(--base00);
      color: var(--base05);
      line-height: 1.6;
    }}

    .container {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 0 24px;
    }}

    /* Hero */
    .hero {{
      min-height: 90vh;
      display: flex;
      flex-direction: column;
      justify-content: center;
      padding: 80px 0;
      position: relative;
      overflow: hidden;
    }}

    .hero::before {{
      content: '';
      position: absolute;
      top: 20%;
      right: -10%;
      width: 600px;
      height: 600px;
      background: radial-gradient(circle, var(--base0E) 0%, transparent 70%);
      opacity: 0.08;
      pointer-events: none;
    }}

    .hero::after {{
      content: '';
      position: absolute;
      bottom: 10%;
      left: -5%;
      width: 400px;
      height: 400px;
      background: radial-gradient(circle, var(--base0F) 0%, transparent 70%);
      opacity: 0.06;
      pointer-events: none;
    }}

    .hero-content {{
      position: relative;
      z-index: 1;
    }}

    .logo {{
      font-size: 72px;
      font-weight: 700;
      letter-spacing: -3px;
      margin-bottom: 8px;
      background: linear-gradient(135deg, var(--base07) 0%, var(--base05) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }}

    .logo span {{
      background: linear-gradient(135deg, var(--base0F) 0%, var(--base0B) 100%);
      -webkit-background-clip: text;
      background-clip: text;
    }}

    .tagline {{
      font-size: 28px;
      font-weight: 300;
      color: var(--base04);
      margin-bottom: 32px;
    }}

    .tagline strong {{
      color: var(--base07);
      font-weight: 500;
    }}

    .hero-description {{
      font-size: 18px;
      max-width: 600px;
      color: var(--base05);
      margin-bottom: 48px;
    }}

    .cta-row {{
      display: flex;
      gap: 16px;
      flex-wrap: wrap;
    }}

    .btn {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 14px 28px;
      border-radius: 8px;
      font-size: 15px;
      font-weight: 500;
      text-decoration: none;
      transition: all 0.2s;
      cursor: pointer;
      border: none;
    }}

    .btn-primary {{
      background: var(--base0F);
      color: var(--base00);
    }}
    .btn-primary:hover {{
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(187, 255, 0, 0.3);
    }}

    .btn-secondary {{
      background: var(--base02);
      color: var(--base06);
    }}
    .btn-secondary:hover {{
      background: var(--base01);
    }}

    /* Philosophy section */
    .section {{
      padding: 100px 0;
    }}

    .section-header {{
      text-align: center;
      margin-bottom: 64px;
    }}

    .section-title {{
      font-size: 36px;
      font-weight: 600;
      color: var(--base07);
      margin-bottom: 16px;
    }}

    .section-subtitle {{
      font-size: 18px;
      color: var(--base04);
      max-width: 600px;
      margin: 0 auto;
    }}

    .philosophy-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 32px;
    }}

    .philosophy-card {{
      background: var(--base01);
      border-radius: 16px;
      padding: 32px;
      border: 1px solid var(--base02);
    }}

    .philosophy-icon {{
      width: 48px;
      height: 48px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      margin-bottom: 20px;
    }}

    .philosophy-card h3 {{
      font-size: 20px;
      color: var(--base07);
      margin-bottom: 12px;
    }}

    .philosophy-card p {{
      font-size: 15px;
      color: var(--base04);
    }}

    /* Palette section */
    .palette-section {{
      background: var(--base01);
      border-top: 1px solid var(--base02);
      border-bottom: 1px solid var(--base02);
    }}

    .palette-row {{
      margin-bottom: 48px;
    }}

    .palette-row:last-child {{
      margin-bottom: 0;
    }}

    .palette-label {{
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 2px;
      color: var(--base04);
      margin-bottom: 16px;
    }}

    .swatches {{
      display: grid;
      grid-template-columns: repeat(8, 1fr);
      gap: 8px;
    }}

    .swatch {{
      aspect-ratio: 1;
      border-radius: 12px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      font-size: 11px;
      cursor: pointer;
      transition: transform 0.15s, box-shadow 0.15s;
      position: relative;
    }}

    .swatch:hover {{
      transform: scale(1.08);
      box-shadow: 0 8px 32px rgba(0,0,0,0.4);
      z-index: 10;
    }}

    .swatch-id {{
      font-size: 14px;
      font-weight: 700;
      margin-bottom: 4px;
    }}

    .swatch-hex {{
      font-size: 10px;
      font-family: 'SF Mono', 'Fira Code', monospace;
      opacity: 0.8;
    }}

    .swatch-role {{
      font-size: 8px;
      opacity: 0.6;
      margin-top: 4px;
      text-align: center;
      padding: 0 4px;
    }}

    /* Markers section */
    .markers-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 24px;
      margin-bottom: 48px;
    }}

    .marker-card {{
      background: var(--base01);
      border-radius: 16px;
      padding: 32px;
      text-align: center;
      border: 1px solid var(--base02);
      transition: border-color 0.2s;
    }}

    .marker-card:hover {{
      border-color: var(--base04);
    }}

    .marker-symbol {{
      font-size: 48px;
      font-weight: 700;
      font-family: 'SF Mono', 'Fira Code', monospace;
      margin-bottom: 12px;
    }}

    .marker-name {{
      font-size: 18px;
      color: var(--base07);
      margin-bottom: 8px;
    }}

    .marker-desc {{
      font-size: 14px;
      color: var(--base04);
    }}

    /* Code preview */
    .code-preview {{
      background: var(--base00);
      border: 1px solid var(--base02);
      border-radius: 12px;
      padding: 24px;
      font-family: 'SF Mono', 'Fira Code', Consolas, monospace;
      font-size: 14px;
      line-height: 1.8;
      overflow-x: auto;
    }}

    .code-preview pre {{
      margin: 0;
    }}

    .code-preview code {{
      font-family: 'SF Mono', 'Fira Code', Consolas, monospace;
    }}

    .code-comment {{ color: var(--base03); }}
    .code-keyword {{ color: var(--base10); }}
    .code-string {{ color: var(--base12); }}
    .code-function {{ color: var(--base13); }}
    .code-type {{ color: var(--base14); }}
    .code-number {{ color: var(--base16); }}
    .code-operator {{ color: var(--base04); }}

    /* Code tabs */
    .code-tabs {{
      display: flex;
      gap: 8px;
      margin-bottom: 16px;
    }}

    .code-tab {{
      padding: 10px 20px;
      background: var(--base01);
      border: 1px solid var(--base02);
      border-radius: 8px;
      color: var(--base04);
      font-size: 14px;
      cursor: pointer;
      transition: all 0.2s;
    }}

    .code-tab:hover {{
      background: var(--base02);
      color: var(--base05);
    }}

    .code-tab.active {{
      background: var(--base02);
      color: var(--base07);
      border-color: var(--base0D);
    }}

    .code-panels {{
      position: relative;
    }}

    .code-panel {{
      display: none;
      background: var(--base00);
      border: 1px solid var(--base02);
      border-radius: 12px;
      padding: 24px;
      overflow-x: auto;
    }}

    .code-panel.active {{
      display: block;
    }}

    .code-panel pre {{
      margin: 0;
    }}

    .code-panel code {{
      font-family: 'SF Mono', 'Fira Code', Consolas, monospace;
      font-size: 14px;
      line-height: 1.8;
    }}

    /* Install section */
    .install-code {{
      background: var(--base00);
      border: 1px solid var(--base02);
      border-radius: 12px;
      padding: 24px;
      font-family: 'SF Mono', 'Fira Code', monospace;
      font-size: 14px;
      margin-bottom: 32px;
      position: relative;
      line-height: 1.8;
    }}

    .install-code pre {{
      margin: 0;
      font-family: inherit;
      font-size: inherit;
      line-height: inherit;
    }}

    .install-code .prompt {{
      color: var(--base0B);
    }}

    .install-code .command {{
      color: var(--base07);
    }}

    .install-code .comment {{
      color: var(--base03);
    }}

    .apps-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
    }}

    .app-card {{
      background: var(--base01);
      border-radius: 12px;
      padding: 20px;
      text-align: center;
      border: 1px solid var(--base02);
    }}

    .app-card h4 {{
      font-size: 14px;
      color: var(--base07);
      margin-bottom: 4px;
    }}

    .app-card p {{
      font-size: 12px;
      color: var(--base04);
    }}

    /* Footer */
    .footer {{
      padding: 48px 0;
      text-align: center;
      border-top: 1px solid var(--base02);
    }}

    .footer p {{
      font-size: 14px;
      color: var(--base04);
    }}

    .footer a {{
      color: var(--base0D);
      text-decoration: none;
    }}

    .footer a:hover {{
      text-decoration: underline;
    }}

    /* Toast */
    .toast {{
      position: fixed;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%) translateY(20px);
      background: var(--base02);
      color: var(--base07);
      padding: 12px 24px;
      border-radius: 8px;
      font-size: 13px;
      opacity: 0;
      transition: all 0.3s;
      pointer-events: none;
    }}

    .toast.show {{
      opacity: 1;
      transform: translateX(-50%) translateY(0);
    }}

    /* Responsive */
    @media (max-width: 900px) {{
      .philosophy-grid,
      .markers-grid {{
        grid-template-columns: 1fr;
      }}
      .swatches,
      .comparison-grid {{
        grid-template-columns: repeat(4, 1fr);
      }}
      .apps-grid {{
        grid-template-columns: repeat(2, 1fr);
      }}
      .logo {{
        font-size: 48px;
      }}
      .tagline {{
        font-size: 20px;
      }}
    }}

    @media (max-width: 600px) {{
      .swatches,
      .comparison-grid {{
        grid-template-columns: repeat(4, 1fr);
      }}
      .apps-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>

  <!-- Hero -->
  <section class="hero">
    <div class="container">
      <div class="hero-content">
        <h1 class="logo">Human<span>++</span></h1>
        <p class="tagline"><strong>Code is cheap.</strong> Intent is scarce.</p>
        <p class="hero-description">
          A Base24 color scheme for the post-artisanal coding era. As models write more code, Human++ makes human judgment visible at a glance through a two-tier accent system and lightweight annotation markers.
        </p>
        <div class="cta-row">
          <a href="https://github.com/fielding/human-plus-plus" class="btn btn-primary">
            Get Human++
          </a>
          <a href="#palette" class="btn btn-secondary">
            View Palette
          </a>
        </div>
      </div>
    </div>
  </section>

  <!-- Philosophy -->
  <section class="section">
    <div class="container">
      <div class="section-header">
        <h2 class="section-title">The Philosophy</h2>
        <p class="section-subtitle">Traditional syntax highlighting treats all code equally. Human++ doesn't.</p>
      </div>

      <div class="philosophy-grid">
        <div class="philosophy-card">
          <div class="philosophy-icon" style="background: var(--base02); color: var(--base12);">Q</div>
          <h3>Quiet Syntax</h3>
          <p>Everyday code — keywords, strings, functions — uses muted colors that fade into the background. You've seen this code a thousand times.</p>
        </div>

        <div class="philosophy-card">
          <div class="philosophy-icon" style="background: linear-gradient(135deg, var(--base08), var(--base09)); color: var(--base00);">!</div>
          <h3>Loud Diagnostics</h3>
          <p>Errors, warnings, and human markers demand attention with vibrant, saturated colors. When you see color, it means something.</p>
        </div>

        <div class="philosophy-card">
          <div class="philosophy-icon" style="background: var(--base0F); color: var(--base00);">></div>
          <h3>Terminal Exception</h3>
          <p>Terminal output is intentional — you typed it. Terminals get loud colors for normal text, quiet for bright. Inverted from the editor.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Palette -->
  <section class="section palette-section" id="palette">
    <div class="container">
      <div class="section-header">
        <h2 class="section-title">The Palette</h2>
        <p class="section-subtitle">Cool Balanced — cool charcoal grays, warm cream text, 16 accent colors.</p>
      </div>

      <div class="palette-row">
        <div class="palette-label">Grayscale (base00–07)</div>
        <div class="swatches" id="grayscale"></div>
      </div>

      <div class="palette-row">
        <div class="palette-label">Loud Accents — Diagnostics & Signals (base08–0F)</div>
        <div class="swatches" id="loud"></div>
      </div>

      <div class="palette-row">
        <div class="palette-label">Quiet Accents — Syntax & UI (base10–17)</div>
        <div class="swatches" id="quiet"></div>
      </div>
    </div>
  </section>

  <!-- Human Markers -->
  <section class="section">
    <div class="container">
      <div class="section-header">
        <h2 class="section-title">Human Intent Markers</h2>
        <p class="section-subtitle">Lightweight punctuation markers that flag human judgment in comments.</p>
      </div>

      <div class="markers-grid">
        <div class="marker-card">
          <div class="marker-symbol" style="color: var(--base0F);">!!</div>
          <div class="marker-name">Attention</div>
          <div class="marker-desc">Pay attention here. Human decision that matters.</div>
        </div>

        <div class="marker-card">
          <div class="marker-symbol" style="color: var(--base0E);">??</div>
          <div class="marker-name">Uncertainty</div>
          <div class="marker-desc">I'm not confident. Please review this.</div>
        </div>

        <div class="marker-card">
          <div class="marker-symbol" style="color: var(--base0C);">>></div>
          <div class="marker-name">Reference</div>
          <div class="marker-desc">See related code or documentation.</div>
        </div>
      </div>

      <div class="code-preview">
<pre><code class="language-typescript">// Regular comment stays calm (base03)

async function processOrder(order: Order) {{
  // !! Critical: legacy billing depends on this exact format
  const invoice = formatLegacy(order);

  if (order.total > 10000) {{
    // ?? Not sure this handles international tax correctly
    await flagForReview(invoice);
  }}

  // >> See billing/tax.ts for the tax calculation logic
  return finalize(invoice);
}}</code></pre>
      </div>
    </div>
  </section>

  <!-- Code Showcase -->
  <section class="section" id="code">
    <div class="container">
      <div class="section-header">
        <h2 class="section-title">Theme in Action</h2>
        <p class="section-subtitle">See Human++ across different languages. Notice how syntax stays quiet while markers pop.</p>
      </div>

      <div class="code-tabs">
        <button class="code-tab active" data-lang="typescript">TypeScript</button>
        <button class="code-tab" data-lang="python">Python</button>
        <button class="code-tab" data-lang="rust">Rust</button>
      </div>

      <div class="code-panels">
        <div class="code-panel active" id="panel-typescript">
          <pre><code class="language-typescript">interface User {{
  id: string;
  email: string;
  createdAt: Date;
}}

// !! Critical: rate limiting depends on this cache key format
async function getUser(id: string): Promise&lt;User | null&gt; {{
  const cached = await redis.get(`user:${{id}}`);
  if (cached) {{
    return JSON.parse(cached);
  }}

  // ?? Should we add retry logic here?
  const user = await db.users.findUnique({{ where: {{ id }} }});

  if (user) {{
    // >> See config.ts for TTL settings
    await redis.set(`user:${{id}}`, JSON.stringify(user), 'EX', 3600);
  }}

  return user;
}}</code></pre>
        </div>

        <div class="code-panel" id="panel-python">
          <pre><code class="language-python">from dataclasses import dataclass
from typing import Optional
import asyncio

@dataclass
class Order:
    id: str
    total: float
    items: list[str]

# !! Critical: this runs in production every 5 minutes
async def process_pending_orders() -> int:
    orders = await db.fetch_pending()
    processed = 0

    for order in orders:
        # ?? Not sure if we need to handle partial refunds here
        if order.total > 10000:
            await flag_for_review(order)
            continue

        # >> See payment_gateway.py for Stripe integration
        result = await charge_customer(order)
        if result.success:
            processed += 1

    return processed</code></pre>
        </div>

        <div class="code-panel" id="panel-rust">
          <pre><code class="language-rust">use std::collections::HashMap;

#[derive(Debug, Clone)]
struct Config {{
    max_retries: u32,
    timeout_ms: u64,
}}

// !! Critical: this is called on every request
pub fn validate_token(token: &str) -> Result&lt;Claims, AuthError&gt; {{
    let parts: Vec&lt;&str&gt; = token.split('.').collect();

    if parts.len() != 3 {{
        return Err(AuthError::MalformedToken);
    }}

    // ?? Should we cache decoded tokens?
    let claims = decode_jwt(parts[1])?;

    // >> See crypto.rs for signature verification
    verify_signature(token, &claims.key_id)?;

    Ok(claims)
}}</code></pre>
        </div>
      </div>
    </div>
  </section>

  <!-- Install -->
  <section class="section" id="install">
    <div class="container">
      <div class="section-header">
        <h2 class="section-title">Get Started</h2>
        <p class="section-subtitle">Human++ works with tinty and standard Base24 tooling.</p>
      </div>

      <div class="install-code">
<pre><span class="comment"># Clone the repo</span>
<span class="prompt">$</span> <span class="command">git clone https://github.com/fielding/human-plus-plus</span>

<span class="comment"># Build all theme files from palette.toml</span>
<span class="prompt">$</span> <span class="command">python3 build.py</span>

<span class="comment"># Apply with tinty</span>
<span class="prompt">$</span> <span class="command">tinty apply base24-human-plus-plus</span></pre>
      </div>

      <div class="apps-grid">
        <div class="app-card">
          <h4>Ghostty</h4>
          <p>ghostty/config</p>
        </div>
        <div class="app-card">
          <h4>VS Code</h4>
          <p>base-cool-balanced-v2.json</p>
        </div>
        <div class="app-card">
          <h4>Vim/Neovim</h4>
          <p>vim/colors/</p>
        </div>
        <div class="app-card">
          <h4>iTerm2</h4>
          <p>iterm/</p>
        </div>
        <div class="app-card">
          <h4>Sketchybar</h4>
          <p>sketchybar/colors.sh</p>
        </div>
        <div class="app-card">
          <h4>JankyBorders</h4>
          <p>borders/bordersrc</p>
        </div>
        <div class="app-card">
          <h4>skhd</h4>
          <p>skhd/modes.sh</p>
        </div>
        <div class="app-card">
          <h4>Shell</h4>
          <p>shell/</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Footer -->
  <footer class="footer">
    <div class="container">
      <p>Human++ is MIT licensed. Made by <a href="https://github.com/fielding">fielding</a>.</p>
    </div>
  </footer>

  <div class="toast" id="toast">Copied!</div>

  <script>
    const palette = {{
      {js_palette}
    }};

    function isLight(hex) {{
      const r = parseInt(hex.slice(1,3), 16);
      const g = parseInt(hex.slice(3,5), 16);
      const b = parseInt(hex.slice(5,7), 16);
      return (r * 0.299 + g * 0.587 + b * 0.114) > 140;
    }}

    function createSwatch(key, data) {{
      const textColor = isLight(data.hex) ? '#1b1d20' : '#faf5ef';
      const swatch = document.createElement('div');
      swatch.className = 'swatch';
      swatch.style.background = data.hex;
      swatch.style.color = textColor;
      swatch.innerHTML = `
        <span class="swatch-id">${{key.replace('base', '')}}</span>
        <span class="swatch-hex">${{data.hex}}</span>
        <span class="swatch-role">${{data.role}}</span>
      `;
      swatch.onclick = () => {{
        navigator.clipboard.writeText(data.hex);
        showToast(`Copied ${{data.hex}}`);
      }};
      return swatch;
    }}

    function showToast(msg) {{
      const toast = document.getElementById('toast');
      toast.textContent = msg;
      toast.classList.add('show');
      setTimeout(() => toast.classList.remove('show'), 1500);
    }}

    // Render grayscale
    const grayscale = document.getElementById('grayscale');
    ['base00','base01','base02','base03','base04','base05','base06','base07'].forEach(key => {{
      grayscale.appendChild(createSwatch(key, palette[key]));
    }});

    // Render loud accents
    const loud = document.getElementById('loud');
    ['base08','base09','base0A','base0B','base0C','base0D','base0E','base0F'].forEach(key => {{
      loud.appendChild(createSwatch(key, palette[key]));
    }});

    // Render quiet accents
    const quiet = document.getElementById('quiet');
    ['base10','base11','base12','base13','base14','base15','base16','base17'].forEach(key => {{
      quiet.appendChild(createSwatch(key, palette[key]));
    }});

    // Tab switching
    document.querySelectorAll('.code-tab').forEach(tab => {{
      tab.addEventListener('click', () => {{
        // Update tabs
        document.querySelectorAll('.code-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        // Update panels
        const lang = tab.dataset.lang;
        document.querySelectorAll('.code-panel').forEach(p => p.classList.remove('active'));
        document.getElementById(`panel-${{lang}}`).classList.add('active');
      }});
    }});
  </script>

  <!-- Highlight.js -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/typescript.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/python.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/rust.min.js"></script>
  <script>
    // Initialize highlight.js
    hljs.highlightAll();

    // Human++ marker highlighting - add background colors to special comments
    function highlightMarkers() {{
      document.querySelectorAll('.hljs-comment').forEach(el => {{
        const text = el.textContent;
        if (text.includes('!!')) {{
          el.classList.add('humanpp-attention');
        }} else if (text.includes('??')) {{
          el.classList.add('humanpp-uncertainty');
        }} else if (text.includes('>>')) {{
          el.classList.add('humanpp-reference');
        }}
      }});
    }}

    // Run after hljs finishes processing
    setTimeout(highlightMarkers, 50);
  </script>
</body>
</html>
'''

    (ROOT / "swatches.html").write_text(html_content)
    (ROOT / "index.html").write_text(html_content)  # For GitHub Pages
    print("  ✓ swatches.html")
    print("  ✓ index.html (GitHub Pages)")


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
# Build everything
python3 build.py

# Apply with tinty
tinty apply base24-human-plus-plus
```

## Files

| File | Description |
|------|-------------|
| `palette.toml` | Source of truth |
| `build.py` | Generates all theme files |
| `ghostty/config` | Ghostty terminal |
| `shell/` | Shell theme script |
| `sketchybar/colors.sh` | Sketchybar |
| `skhd/modes.sh` | skhd mode indicators |
| `borders/bordersrc` | JankyBorders |
| `base-cool-balanced-v2.json` | VS Code / Cursor |
| `swatches.html` | Interactive palette preview |

## Preview

Open `swatches.html` in a browser to see the full palette with:

- Interactive color swatches
- Loud vs quiet comparison
- Human marker examples
- Live code preview

## License

MIT
'''

    (ROOT / "README.md").write_text(content)
    print("  ✓ README.md")


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

        # Also copy to local
        local_shell = ROOT / "shell"
        local_shell.mkdir(exist_ok=True)
        (local_shell / "base24-human-plus-plus.sh").write_text(output)
        print("  ✓ shell/base24-human-plus-plus.sh")

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
    """Update VS Code theme with new colors."""
    theme_path = ROOT / "base-cool-balanced-v2.json"

    if not theme_path.exists():
        print("  ⚠ VS Code theme not found, skipping")
        return

    content = theme_path.read_text()

    # Map old colors to new
    replacements = {
        # Grayscale - update to new values
        '#c4bbb2': colors['base05'],  # old base05 -> new base05
        '#ddd5cc': colors['base06'],  # old base06 -> new base06
        '#f2ebe4': colors['base07'],  # old base07 -> new base07
    }

    for old, new in replacements.items():
        content = content.replace(old, new)

    theme_path.write_text(content)
    print("  ✓ base-cool-balanced-v2.json")

    # Also copy to vscode-extension folder
    ext_theme_path = ROOT / "vscode-extension/themes/humanpp-cool-balanced.json"
    if ext_theme_path.parent.exists():
        import shutil
        shutil.copy(theme_path, ext_theme_path)
        print("  ✓ vscode-extension/themes/humanpp-cool-balanced.json")


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

    print("\nGenerating docs:")
    generate_swatches_html(colors, meta)
    generate_readme(colors, meta)

    print("\nGenerating tinty themes:")
    generate_tinty_themes(colors, meta)

    print("\nUpdating VS Code theme:")
    update_vscode_theme(colors, meta)

    print("\n✓ Build complete!")
    print("\nTo apply: tinty apply base24-human-plus-plus")


if __name__ == '__main__':
    main()
