#!/usr/bin/env python3
"""
Human++ Palette Proposal Generator

Generates proposed improvements to the palette based on OKLCH analysis.
Shows before/after comparisons and tradeoffs.
"""

import math
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════════
# Color Math
# ═══════════════════════════════════════════════════════════════════════════════

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def hex_to_rgb(hex_color):
    h = hex_color.strip().lstrip("#")
    return int(h[0:2], 16)/255, int(h[2:4], 16)/255, int(h[4:6], 16)/255

def rgb_to_hex(r, g, b):
    r, g, b = clamp(r, 0, 1), clamp(g, 0, 1), clamp(b, 0, 1)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def linear_to_srgb(c):
    c = clamp(c, 0, 1)
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1/2.4)) - 0.055

def hex_to_oklch(hex_color):
    r, g, b = hex_to_rgb(hex_color)
    rl, gl, bl = srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b)

    l = 0.4122214708 * rl + 0.5363325363 * gl + 0.0514459929 * bl
    m = 0.2119034982 * rl + 0.6806995451 * gl + 0.1073969566 * bl
    s = 0.0883024619 * rl + 0.2817188376 * gl + 0.6299787005 * bl

    l_ = l ** (1/3) if l > 0 else 0
    m_ = m ** (1/3) if m > 0 else 0
    s_ = s ** (1/3) if s > 0 else 0

    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    b_val = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_

    C = math.sqrt(a*a + b_val*b_val)
    h = math.degrees(math.atan2(b_val, a)) % 360
    return L, C, h

def oklch_to_hex(L, C, h):
    """Convert OKLCH to hex, with gamut clipping"""
    a = C * math.cos(math.radians(h))
    b = C * math.sin(math.radians(h))

    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b

    l = l_ ** 3
    m = m_ ** 3
    s = s_ ** 3

    rl = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    gl = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bl = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s

    # Gamut clip by reducing chroma if needed
    if rl < 0 or rl > 1 or gl < 0 or gl > 1 or bl < 0 or bl > 1:
        # Binary search for max chroma that fits
        lo, hi = 0, C
        for _ in range(20):
            mid = (lo + hi) / 2
            a2 = mid * math.cos(math.radians(h))
            b2 = mid * math.sin(math.radians(h))
            l_ = L + 0.3963377774 * a2 + 0.2158037573 * b2
            m_ = L - 0.1055613458 * a2 - 0.0638541728 * b2
            s_ = L - 0.0894841775 * a2 - 1.2914855480 * b2
            l, m, s = l_**3, m_**3, s_**3
            rl2 = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
            gl2 = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
            bl2 = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
            if 0 <= rl2 <= 1 and 0 <= gl2 <= 1 and 0 <= bl2 <= 1:
                lo = mid
                rl, gl, bl = rl2, gl2, bl2
            else:
                hi = mid

    r = linear_to_srgb(rl)
    g = linear_to_srgb(gl)
    b = linear_to_srgb(bl)
    return rgb_to_hex(r, g, b)

def relative_luminance(hex_color):
    r, g, b = hex_to_rgb(hex_color)
    rl, gl, bl = srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b)
    return 0.2126 * rl + 0.7152 * gl + 0.0722 * bl

def contrast_ratio(hex1, hex2):
    l1, l2 = relative_luminance(hex1), relative_luminance(hex2)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)

# ═══════════════════════════════════════════════════════════════════════════════
# Display helpers
# ═══════════════════════════════════════════════════════════════════════════════

def rgb_bg(hex_color):
    r, g, b = hex_to_rgb(hex_color)
    return f"\033[48;2;{int(r*255)};{int(g*255)};{int(b*255)}m"

def rgb_fg(hex_color):
    r, g, b = hex_to_rgb(hex_color)
    return f"\033[38;2;{int(r*255)};{int(g*255)};{int(b*255)}m"

def reset():
    return "\033[0m"

def bold():
    return "\033[1m"

def swatch(hex_color, width=6):
    return f"{rgb_bg(hex_color)}{' ' * width}{reset()}"

def print_header(title):
    print()
    print(f"{'═' * 78}")
    print(f"  {bold()}{title}{reset()}")
    print(f"{'═' * 78}")

def print_subheader(title):
    print()
    print(f"  {bold()}── {title} ──{reset()}")
    print()

# ═══════════════════════════════════════════════════════════════════════════════
# Parse current palette
# ═══════════════════════════════════════════════════════════════════════════════

def parse_palette(path):
    colors = {}
    content = path.read_text()
    for line in content.split('\n'):
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('['):
            continue
        if '=' in line and 'base' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            if '"#' in value:
                start = value.index('"#') + 1
                end = value.index('"', start)
                hex_val = value[start:end]
                if len(hex_val) == 7:
                    colors[key] = hex_val
    return colors

# ═══════════════════════════════════════════════════════════════════════════════
# Proposal Generation
# ═══════════════════════════════════════════════════════════════════════════════

def propose_grayscale(colors):
    """Generate proposed grayscale with smooth progression"""
    print_header("GRAYSCALE PROPOSAL")

    # Get current values
    current = {}
    for i in range(8):
        slot = f"base0{i}"
        L, C, h = hex_to_oklch(colors[slot])
        current[slot] = {'hex': colors[slot], 'L': L, 'C': C, 'h': h}

    # Design principles:
    # - base00-02: backgrounds, keep cool (h ≈ 270-280°)
    # - base03: comments, warm brown voice (h ≈ 70-85°), needs good contrast
    # - base04: UI secondary, can be neutral or warm
    # - base05-07: text, warm cream (h ≈ 70-90°)

    # Target lightness curve (smooth progression with room for mid-tones)
    # Current: 0.23, 0.27, 0.33, 0.59, 0.61, 0.90, 0.94, 0.97
    # Problem: gap at 0.33→0.59, then 0.59≈0.61, then gap at 0.61→0.90

    # CONSTRAINT: base03 (comments) needs ~4:1 contrast with bg for readability
    # At L=0.23 bg, we need base03 L ≥ ~0.55 for decent contrast

    # Strategy: Keep base03 readable, push base04 UP to create separation
    # Fill the base02→base03 gap by raising base02 slightly
    target_L = {
        'base00': 0.230,  # keep - background
        'base01': 0.290,  # slight bump
        'base02': 0.370,  # bump up to fill gap toward base03
        'base03': 0.550,  # lower slightly but keep ~4:1 contrast
        'base04': 0.700,  # RAISE significantly to create clear separation
        'base05': 0.870,  # main text - high contrast
        'base06': 0.925,  # emphasis
        'base07': 0.970,  # brightest
    }

    # Generate new colors preserving hue and adjusting chroma appropriately
    proposed = {}
    for slot in [f'base0{i}' for i in range(8)]:
        curr = current[slot]
        new_L = target_L[slot]

        # For grayscale, we want low chroma
        # Backgrounds: cool hue (270-280°), very low chroma
        # Text: warm hue (75-85°), very low chroma
        if slot in ['base00', 'base01', 'base02']:
            # Cool backgrounds - blue-gray undertone
            new_h = 265  # cool blue-gray
            new_C = 0.015  # subtle cool tint
        elif slot == 'base03':
            # Comments: warm coffee brown - the "human voice"
            # More chroma for character, distinct from neutral UI
            new_h = 65  # warm brown/tan
            new_C = 0.050  # noticeable warmth - this is the character color
        elif slot == 'base04':
            # UI secondary: cooler, more neutral than comments
            new_h = 80  # slightly warm but more neutral
            new_C = 0.022
        else:
            # Text: warm cream
            new_h = 85
            new_C = 0.020

        new_hex = oklch_to_hex(new_L, new_C, new_h)
        proposed[slot] = {'hex': new_hex, 'L': new_L, 'C': new_C, 'h': new_h}

    # Display comparison
    print_subheader("Current vs Proposed")

    bg = colors['base00']

    print(f"  {'Slot':<8} {'Current':<12} {'Proposed':<12} {'ΔL':>8} {'Contrast':>10} {'Swatches'}")
    print(f"  {'─'*8} {'─'*12} {'─'*12} {'─'*8} {'─'*10} {'─'*20}")

    for slot in [f'base0{i}' for i in range(8)]:
        curr = current[slot]
        prop = proposed[slot]
        delta_L = prop['L'] - curr['L']

        # Contrast with background
        curr_cr = contrast_ratio(curr['hex'], bg)
        prop_cr = contrast_ratio(prop['hex'], bg)

        curr_sw = swatch(curr['hex'], 4)
        prop_sw = swatch(prop['hex'], 4)

        cr_change = prop_cr - curr_cr
        cr_color = "#04b372" if cr_change >= 0 else "#f2a633"

        print(f"  {slot:<8} {curr['hex']:<12} {prop['hex']:<12} {delta_L:>+8.3f} {prop_cr:>6.2f} ({cr_change:+.2f}) {curr_sw} → {prop_sw}")

    # Show lightness progression
    print_subheader("Lightness Progression")
    print(f"  {'Step':<16} {'Current ΔL':>12} {'Proposed ΔL':>12} {'Assessment'}")
    print(f"  {'─'*16} {'─'*12} {'─'*12} {'─'*20}")

    slots = [f'base0{i}' for i in range(8)]
    for i in range(1, 8):
        prev, curr_slot = slots[i-1], slots[i]
        curr_delta = current[curr_slot]['L'] - current[prev]['L']
        prop_delta = proposed[curr_slot]['L'] - proposed[prev]['L']

        if prop_delta < 0.05:
            assessment = "Too close"
            color = "#f2a633"
        elif prop_delta > 0.20:
            assessment = "Large step"
            color = "#f2a633"
        else:
            assessment = "Good"
            color = "#04b372"

        print(f"  {prev}→{curr_slot:<6} {curr_delta:>+12.3f} {prop_delta:>+12.3f} {rgb_fg(color)}{assessment}{reset()}")

    # Visual comparison
    print_subheader("Visual Comparison")
    print("  Current:  ", end="")
    for i in range(8):
        print(swatch(current[f'base0{i}']['hex'], 8), end="")
    print()
    print("  Proposed: ", end="")
    for i in range(8):
        print(swatch(proposed[f'base0{i}']['hex'], 8), end="")
    print()

    return proposed

def propose_quiet_accents(colors):
    """Propose adjusted quiet accents for better differentiation"""
    print_header("QUIET ACCENT PROPOSAL")

    pairs = [
        ('base08', 'base10', 'red'),
        ('base09', 'base11', 'orange'),
        ('base0A', 'base12', 'yellow'),
        ('base0B', 'base13', 'green'),
        ('base0C', 'base14', 'cyan'),
        ('base0D', 'base15', 'blue'),
        ('base0E', 'base16', 'purple'),
        ('base0F', 'base17', 'lime'),
    ]

    # Target deltas for quieting:
    # ΔL: +0.02 to +0.04 (slightly lighter)
    # ΔC: -0.06 to -0.10 (noticeably less saturated)
    # Δh: 0 (preserve hue)

    print_subheader("Current Analysis")
    print(f"  {'Color':<8} {'Loud':<10} {'Quiet':<10} {'ΔL':>8} {'ΔC':>8} {'Issue'}")
    print(f"  {'─'*8} {'─'*10} {'─'*10} {'─'*8} {'─'*8} {'─'*20}")

    proposed = {}
    issues = []

    for loud_slot, quiet_slot, name in pairs:
        loud_L, loud_C, loud_h = hex_to_oklch(colors[loud_slot])
        quiet_L, quiet_C, quiet_h = hex_to_oklch(colors[quiet_slot])

        dL = quiet_L - loud_L
        dC = quiet_C - loud_C

        issue = ""
        if dC > -0.05:
            issue = "Low ΔC (too similar)"
            issues.append((quiet_slot, name, loud_L, loud_C, loud_h))

        issue_color = "#f2a633" if issue else "#04b372"
        print(f"  {name:<8} {colors[loud_slot]:<10} {colors[quiet_slot]:<10} {dL:>+8.3f} {dC:>+8.3f} {rgb_fg(issue_color)}{issue}{reset()}")

    if issues:
        print_subheader("Proposed Fixes")
        print(f"  {'Color':<8} {'Current':<10} {'Proposed':<10} {'New ΔC':>8} {'Swatches'}")
        print(f"  {'─'*8} {'─'*10} {'─'*10} {'─'*8} {'─'*20}")

        for quiet_slot, name, loud_L, loud_C, loud_h in issues:
            # Target: ΔL = +0.025, ΔC = -0.07
            new_L = loud_L + 0.025
            new_C = loud_C - 0.07  # More aggressive chroma reduction
            new_h = loud_h  # Preserve hue exactly

            new_hex = oklch_to_hex(new_L, new_C, new_h)
            curr_hex = colors[quiet_slot]
            new_dC = new_C - loud_C

            curr_sw = swatch(curr_hex, 4)
            new_sw = swatch(new_hex, 4)

            proposed[quiet_slot] = new_hex
            print(f"  {name:<8} {curr_hex:<10} {new_hex:<10} {new_dC:>+8.3f} {curr_sw} → {new_sw}")
    else:
        print("\n  All quiet accents have good differentiation!")

    return proposed

def propose_loud_accents(colors):
    """Analyze and potentially adjust loud accents for better hue distribution and contrast"""
    print_header("LOUD ACCENT ANALYSIS")

    bg = colors['base00']

    slots = ['base08', 'base09', 'base0A', 'base0B', 'base0C', 'base0D', 'base0E', 'base0F']
    names = ['red/pink', 'orange', 'yellow', 'green', 'cyan', 'blue', 'purple', 'lime']

    print_subheader("Contrast with Background")
    print(f"  {'Color':<10} {'Hex':<10} {'L':>6} {'Contrast':>10} {'WCAG':<15} {'Suggestion'}")
    print(f"  {'─'*10} {'─'*10} {'─'*6} {'─'*10} {'─'*15} {'─'*20}")

    proposed = {}

    for slot, name in zip(slots, names):
        hex_val = colors[slot]
        L, C, h = hex_to_oklch(hex_val)
        cr = contrast_ratio(hex_val, bg)

        if cr >= 4.5:
            wcag = "AA"
            wcag_color = "#04b372"
            suggestion = ""
        elif cr >= 3.0:
            wcag = "AA Large"
            wcag_color = "#f2a633"
            # Suggest lightening
            suggestion = "Consider lightening"
        else:
            wcag = "Fails"
            wcag_color = "#d9048e"
            suggestion = "Needs lightening"

        print(f"  {name:<10} {hex_val:<10} {L:>6.3f} {cr:>10.2f} {rgb_fg(wcag_color)}{wcag:<15}{reset()} {suggestion}")

        # Generate proposal for low-contrast colors
        if cr < 4.0:
            # Increase lightness while preserving hue and reducing chroma slightly
            new_L = L + 0.05
            new_C = C * 0.95  # Slight chroma reduction to help with gamut
            new_hex = oklch_to_hex(new_L, new_C, h)
            new_cr = contrast_ratio(new_hex, bg)
            proposed[slot] = {'hex': new_hex, 'old_cr': cr, 'new_cr': new_cr}

    if proposed:
        print_subheader("Proposed Contrast Improvements")
        print(f"  {'Color':<10} {'Current':<10} {'Proposed':<10} {'CR Change'}")
        print(f"  {'─'*10} {'─'*10} {'─'*10} {'─'*15}")

        for slot, data in proposed.items():
            name = names[slots.index(slot)]
            curr_sw = swatch(colors[slot], 4)
            new_sw = swatch(data['hex'], 4)
            print(f"  {name:<10} {colors[slot]:<10} {data['hex']:<10} {data['old_cr']:.2f} → {data['new_cr']:.2f} {curr_sw} → {new_sw}")

    return proposed

def generate_palette_toml(colors, grayscale_props, quiet_props, loud_props):
    """Generate proposed palette.toml content"""
    print_header("PROPOSED PALETTE.TOML")

    # Merge proposals
    new_colors = dict(colors)

    for slot, data in grayscale_props.items():
        new_colors[slot] = data['hex']

    for slot, hex_val in quiet_props.items():
        new_colors[slot] = hex_val

    for slot, data in loud_props.items():
        new_colors[slot] = data['hex']

    print()
    print('  [meta]')
    print('  name = "Human++ Cool Balanced"')
    print('  author = "fielding"')
    print('  description = "Cool balanced grayscale with quiet syntax, loud diagnostics"')
    print()
    print('  [base16]')

    comments = {
        'base00': 'bg (cool charcoal)',
        'base01': 'bg+ (elevation)',
        'base02': 'selection (panels)',
        'base03': 'comments (warm brown voice)',
        'base04': 'fg- (UI secondary)',
        'base05': 'fg (main text)',
        'base06': 'fg+ (emphasis)',
        'base07': 'fg++ (brightest)',
        'base08': 'red/pink (LOUD - errors)',
        'base09': 'orange (LOUD - warnings)',
        'base0A': 'yellow (LOUD - caution)',
        'base0B': 'green (LOUD - success)',
        'base0C': 'cyan (LOUD - info)',
        'base0D': 'blue (LOUD - links)',
        'base0E': 'purple (LOUD - special)',
        'base0F': 'lime (LOUD - human !!)',
    }

    for i in range(16):
        if i < 10:
            slot = f'base0{i}'
        else:
            slot = f'base0{chr(ord("A") + i - 10)}'

        if slot in new_colors:
            comment = comments.get(slot, '')
            print(f'  {slot} = "{new_colors[slot]}"    # {comment}')

    print()
    print('  [base24]')
    print('  # Quiet accent variants')

    quiet_comments = {
        'base10': 'quiet red',
        'base11': 'quiet orange',
        'base12': 'quiet yellow (strings)',
        'base13': 'quiet green (functions)',
        'base14': 'quiet cyan (types)',
        'base15': 'quiet blue (hints)',
        'base16': 'quiet purple (constants)',
        'base17': 'quiet lime',
    }

    for i in range(10, 18):
        slot = f'base{i}'
        if slot in new_colors:
            comment = quiet_comments.get(slot, '')
            print(f'  {slot} = "{new_colors[slot]}"    # {comment}')

    return new_colors

# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    root = Path(__file__).parent
    palette_path = root / "palette.toml"

    if not palette_path.exists():
        print(f"Error: {palette_path} not found")
        return

    colors = parse_palette(palette_path)

    print()
    print(f"  {bold()}Human++ Palette Proposal Generator{reset()}")
    print(f"  Analyzing current palette and generating improvements...")

    # Generate proposals
    grayscale_props = propose_grayscale(colors)
    quiet_props = propose_quiet_accents(colors)
    loud_props = propose_loud_accents(colors)

    # Generate final palette
    generate_palette_toml(colors, grayscale_props, quiet_props, loud_props)

    print()

if __name__ == "__main__":
    main()
