#!/usr/bin/env python3
"""
Human++ Palette Analyzer

Analyzes the palette in OKLCH color space and provides insights for tuning.
Reads from palette.toml (the single source of truth).

Usage: python3 analyze.py [--no-color] [--section SECTION]
"""

import math
import sys
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════════
# Color Math (sRGB <-> OKLab <-> OKLCH)
# ═══════════════════════════════════════════════════════════════════════════════

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))

def hex_to_rgb(hex_color: str) -> tuple[float, float, float]:
    h = hex_color.strip().lstrip("#")
    return int(h[0:2], 16)/255, int(h[2:4], 16)/255, int(h[4:6], 16)/255

def rgb_to_hex(r: float, g: float, b: float) -> str:
    return f"#{int(clamp01(r)*255):02x}{int(clamp01(g)*255):02x}{int(clamp01(b)*255):02x}"

def srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def linear_to_srgb(c: float) -> float:
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1/2.4)) - 0.055

def hex_to_oklab(hex_color: str) -> tuple[float, float, float]:
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
    b = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return L, a, b

def oklab_to_oklch(L: float, a: float, b: float) -> tuple[float, float, float]:
    C = math.sqrt(a*a + b*b)
    h = math.degrees(math.atan2(b, a)) % 360
    return L, C, h

def hex_to_oklch(hex_color: str) -> tuple[float, float, float]:
    L, a, b = hex_to_oklab(hex_color)
    return oklab_to_oklch(L, a, b)

def relative_luminance(hex_color: str) -> float:
    """WCAG relative luminance"""
    r, g, b = hex_to_rgb(hex_color)
    rl, gl, bl = srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b)
    return 0.2126 * rl + 0.7152 * gl + 0.0722 * bl

def contrast_ratio(hex1: str, hex2: str) -> float:
    """WCAG contrast ratio"""
    l1 = relative_luminance(hex1)
    l2 = relative_luminance(hex2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)

# ═══════════════════════════════════════════════════════════════════════════════
# Terminal Colors
# ═══════════════════════════════════════════════════════════════════════════════

USE_COLOR = sys.stdout.isatty() and "--no-color" not in sys.argv

def rgb_bg(hex_color: str) -> str:
    """True color background"""
    if not USE_COLOR:
        return ""
    r, g, b = hex_to_rgb(hex_color)
    return f"\033[48;2;{int(r*255)};{int(g*255)};{int(b*255)}m"

def rgb_fg(hex_color: str) -> str:
    """True color foreground"""
    if not USE_COLOR:
        return ""
    r, g, b = hex_to_rgb(hex_color)
    return f"\033[38;2;{int(r*255)};{int(g*255)};{int(b*255)}m"

def reset() -> str:
    return "\033[0m" if USE_COLOR else ""

def bold() -> str:
    return "\033[1m" if USE_COLOR else ""

def dim() -> str:
    return "\033[2m" if USE_COLOR else ""

# ═══════════════════════════════════════════════════════════════════════════════
# Palette Parsing
# ═══════════════════════════════════════════════════════════════════════════════

def parse_palette(path: Path) -> dict[str, str]:
    """Parse palette.toml"""
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
            # Extract hex from quoted value like: "#1b1d20"    # comment
            if '"#' in value:
                # Find the hex value between quotes
                start = value.index('"#') + 1
                end = value.index('"', start)
                hex_val = value[start:end]
                if len(hex_val) == 7:
                    colors[key] = hex_val

    return colors

# ═══════════════════════════════════════════════════════════════════════════════
# Analysis Functions
# ═══════════════════════════════════════════════════════════════════════════════

ROLES = {
    'base00': 'background', 'base01': 'elevation', 'base02': 'selection', 'base03': 'comments',
    'base04': 'UI secondary', 'base05': 'main text', 'base06': 'emphasis', 'base07': 'brightest',
    'base08': 'errors/red', 'base09': 'warnings/orange', 'base0A': 'caution/yellow', 'base0B': 'success/green',
    'base0C': 'info/cyan', 'base0D': 'links/blue', 'base0E': 'special/purple', 'base0F': 'human !!',
    'base10': 'quiet red', 'base11': 'quiet orange', 'base12': 'quiet yellow', 'base13': 'quiet green',
    'base14': 'quiet cyan', 'base15': 'quiet blue', 'base16': 'quiet purple', 'base17': 'quiet lime',
}

HUE_NAMES = {
    (0, 30): "red", (30, 60): "orange", (60, 90): "yellow", (90, 150): "green",
    (150, 210): "cyan", (210, 270): "blue", (270, 330): "purple/magenta", (330, 360): "red"
}

def hue_name(h: float) -> str:
    for (lo, hi), name in HUE_NAMES.items():
        if lo <= h < hi:
            return name
    return "red"

def print_header(title: str):
    width = 78
    print()
    print(f"{'═' * width}")
    print(f"  {bold()}{title}{reset()}")
    print(f"{'═' * width}")

def print_subheader(title: str):
    print()
    print(f"  {bold()}── {title} ──{reset()}")
    print()

def swatch(hex_color: str, width: int = 2) -> str:
    """Create a color swatch"""
    return f"{rgb_bg(hex_color)}{' ' * width}{reset()}"

def labeled_swatch(hex_color: str, width: int = 6) -> str:
    """Swatch with hex value inside"""
    L, _, _ = hex_to_oklch(hex_color)
    fg = "#000000" if L > 0.6 else "#ffffff"
    return f"{rgb_bg(hex_color)}{rgb_fg(fg)}{hex_color:^{width}}{reset()}"

def lightness_bar(L: float, width: int = 30) -> str:
    """Visual bar showing lightness"""
    filled = int(L * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"{dim()}{bar}{reset()}"

def delta_indicator(delta: float, threshold_warn: float = 0.15, threshold_bad: float = 0.25) -> str:
    """Color-coded delta indicator"""
    if abs(delta) > threshold_bad:
        return f"{rgb_fg('#d9048e')}██{reset()}"  # red/pink - big jump
    elif abs(delta) > threshold_warn:
        return f"{rgb_fg('#f2a633')}▓▓{reset()}"  # yellow - notable
    else:
        return f"{rgb_fg('#04b372')}░░{reset()}"  # green - smooth

def analyze_grayscale(colors: dict[str, str]):
    print_header("GRAYSCALE ANALYSIS (base00-base07)")

    slots = [f"base0{i}" for i in range(8)]
    data = [(slot, colors[slot], *hex_to_oklch(colors[slot])) for slot in slots]

    # Table header
    print(f"  {'Slot':<8} {'Hex':<10} {'Swatch':<8} {'L':>6} {'C':>7} {'H':>6}  {'Lightness Bar':<32} Role")
    print(f"  {'─'*8} {'─'*10} {'─'*8} {'─'*6} {'─'*7} {'─'*6}  {'─'*32} {'─'*12}")

    for slot, hex_val, L, C, h in data:
        role = ROLES.get(slot, '')
        sw = swatch(hex_val, 6)
        bar = lightness_bar(L)
        print(f"  {slot:<8} {hex_val:<10} {sw} {L:>6.3f} {C:>7.4f} {h:>6.1f}° {bar} {role}")

    # Lightness progression
    print_subheader("Lightness Steps")
    print(f"  {'Transition':<16} {'ΔL':>8}  {'Assessment':<20} Visual")
    print(f"  {'─'*16} {'─'*8}  {'─'*20} {'─'*10}")

    for i in range(1, len(data)):
        prev_slot, _, prev_L, _, _ = data[i-1]
        curr_slot, _, curr_L, _, _ = data[i]
        delta = curr_L - prev_L

        if delta < 0.05:
            assessment = "Too close!"
            color = "#d9048e"
        elif delta > 0.2:
            assessment = "Large gap"
            color = "#f2a633"
        else:
            assessment = "Good"
            color = "#04b372"

        indicator = delta_indicator(delta, 0.08, 0.2)
        print(f"  {prev_slot} → {curr_slot:<6} {delta:>+8.4f}  {rgb_fg(color)}{assessment:<20}{reset()} {indicator}")

    # Ideal vs actual
    print_subheader("Ideal Distribution")
    ideal_L = [0.23, 0.30, 0.38, 0.48, 0.58, 0.75, 0.88, 0.97]  # Smooth curve
    print(f"  {'Slot':<8} {'Actual L':>10} {'Ideal L':>10} {'Δ':>8}")
    print(f"  {'─'*8} {'─'*10} {'─'*10} {'─'*8}")
    for i, (slot, hex_val, L, C, h) in enumerate(data):
        diff = L - ideal_L[i]
        color = "#04b372" if abs(diff) < 0.05 else "#f2a633" if abs(diff) < 0.1 else "#d9048e"
        print(f"  {slot:<8} {L:>10.3f} {ideal_L[i]:>10.3f} {rgb_fg(color)}{diff:>+8.3f}{reset()}")

def analyze_accents(colors: dict[str, str]):
    print_header("ACCENT COLORS ANALYSIS")

    loud_slots = ['base08', 'base09', 'base0A', 'base0B', 'base0C', 'base0D', 'base0E', 'base0F']
    quiet_slots = ['base10', 'base11', 'base12', 'base13', 'base14', 'base15', 'base16', 'base17']

    print_subheader("Loud Accents (base08-0F) — Diagnostics & Signals")
    print(f"  {'Slot':<8} {'Hex':<10} {'Swatch':<8} {'L':>6} {'C':>7} {'H':>6}°  Hue Name")
    print(f"  {'─'*8} {'─'*10} {'─'*8} {'─'*6} {'─'*7} {'─'*7}  {'─'*12}")

    for slot in loud_slots:
        hex_val = colors[slot]
        L, C, h = hex_to_oklch(hex_val)
        sw = swatch(hex_val, 6)
        hn = hue_name(h)
        print(f"  {slot:<8} {hex_val:<10} {sw} {L:>6.3f} {C:>7.4f} {h:>6.1f}°  {hn}")

    print_subheader("Quiet Accents (base10-17) — Syntax & UI")
    print(f"  {'Slot':<8} {'Hex':<10} {'Swatch':<8} {'L':>6} {'C':>7} {'H':>6}°  Hue Name")
    print(f"  {'─'*8} {'─'*10} {'─'*8} {'─'*6} {'─'*7} {'─'*7}  {'─'*12}")

    for slot in quiet_slots:
        hex_val = colors[slot]
        L, C, h = hex_to_oklch(hex_val)
        sw = swatch(hex_val, 6)
        hn = hue_name(h)
        print(f"  {slot:<8} {hex_val:<10} {sw} {L:>6.3f} {C:>7.4f} {h:>6.1f}°  {hn}")

def analyze_pairs(colors: dict[str, str]):
    print_header("LOUD vs QUIET PAIR ANALYSIS")

    pairs = [
        ('base08', 'base10', 'red/pink'),
        ('base09', 'base11', 'orange'),
        ('base0A', 'base12', 'yellow'),
        ('base0B', 'base13', 'green'),
        ('base0C', 'base14', 'cyan'),
        ('base0D', 'base15', 'blue'),
        ('base0E', 'base16', 'purple'),
        ('base0F', 'base17', 'lime'),
    ]

    print_subheader("Side-by-Side Comparison")
    print(f"  {'Color':<10} {'Loud':<10} {'Quiet':<10} {'Swatches':<16}")
    print(f"  {'─'*10} {'─'*10} {'─'*10} {'─'*16}")

    for loud, quiet, name in pairs:
        loud_sw = swatch(colors[loud], 6)
        quiet_sw = swatch(colors[quiet], 6)
        print(f"  {name:<10} {colors[loud]:<10} {colors[quiet]:<10} {loud_sw} → {quiet_sw}")

    print_subheader("OKLCH Deltas (Loud → Quiet)")
    print(f"  {'Color':<10} {'ΔL':>8} {'ΔC':>8} {'Δh':>8}  Assessment")
    print(f"  {'─'*10} {'─'*8} {'─'*8} {'─'*8}  {'─'*30}")

    for loud, quiet, name in pairs:
        L1, C1, h1 = hex_to_oklch(colors[loud])
        L2, C2, h2 = hex_to_oklch(colors[quiet])

        dL = L2 - L1
        dC = C2 - C1
        dh = h2 - h1
        if dh > 180: dh -= 360
        if dh < -180: dh += 360

        issues = []
        if dL < 0:
            issues.append("darker (unusual)")
        if dC > -0.03:
            issues.append("low chroma reduction")
        if abs(dh) > 10:
            issues.append(f"hue drift")

        assessment = ", ".join(issues) if issues else "Good"
        color = "#d9048e" if issues else "#04b372"

        print(f"  {name:<10} {dL:>+8.4f} {dC:>+8.4f} {dh:>+8.1f}° {rgb_fg(color)}{assessment}{reset()}")

    print_subheader("Ideal Quieting Formula")
    print("  Target: ΔL ≈ +0.02 to +0.05 (slightly lighter)")
    print("          ΔC ≈ -0.05 to -0.10 (less saturated)")
    print("          Δh ≈ 0° (preserve hue identity)")

def analyze_contrast(colors: dict[str, str]):
    print_header("CONTRAST ANALYSIS")

    bg = colors['base00']

    print_subheader("Text on Background (base00)")
    print(f"  {'Color':<10} {'Hex':<10} {'Swatch':<8} {'Ratio':>7}  WCAG")
    print(f"  {'─'*10} {'─'*10} {'─'*8} {'─'*7}  {'─'*20}")

    text_slots = ['base03', 'base04', 'base05', 'base06', 'base07']
    for slot in text_slots:
        hex_val = colors[slot]
        ratio = contrast_ratio(hex_val, bg)
        sw = swatch(hex_val, 6)

        if ratio >= 7:
            wcag = "AAA (excellent)"
            color = "#04b372"
        elif ratio >= 4.5:
            wcag = "AA (good)"
            color = "#04b372"
        elif ratio >= 3:
            wcag = "AA Large only"
            color = "#f2a633"
        else:
            wcag = "Fails"
            color = "#d9048e"

        role = ROLES.get(slot, '')
        print(f"  {slot:<10} {hex_val:<10} {sw} {ratio:>7.2f}  {rgb_fg(color)}{wcag}{reset()} ({role})")

    print_subheader("Accent Colors on Background")
    accent_slots = ['base08', 'base09', 'base0A', 'base0B', 'base0C', 'base0D', 'base0E', 'base0F']
    for slot in accent_slots:
        hex_val = colors[slot]
        ratio = contrast_ratio(hex_val, bg)
        sw = swatch(hex_val, 6)

        if ratio >= 4.5:
            wcag = "AA"
            color = "#04b372"
        elif ratio >= 3:
            wcag = "Large"
            color = "#f2a633"
        else:
            wcag = "Low"
            color = "#d9048e"

        print(f"  {slot:<10} {hex_val:<10} {sw} {ratio:>7.2f}  {rgb_fg(color)}{wcag}{reset()}")

def analyze_hue_wheel(colors: dict[str, str]):
    print_header("HUE DISTRIBUTION")

    accents = ['base08', 'base09', 'base0A', 'base0B', 'base0C', 'base0D', 'base0E', 'base0F']

    print_subheader("Hue Positions (0-360°)")

    # Sort by hue
    hue_data = []
    for slot in accents:
        L, C, h = hex_to_oklch(colors[slot])
        hue_data.append((h, slot, colors[slot], C))

    hue_data.sort(key=lambda x: x[0])

    # Visual hue wheel (simplified ASCII)
    print("  Hue wheel (sorted by position):")
    print()
    for h, slot, hex_val, C in hue_data:
        sw = swatch(hex_val, 4)
        bar_pos = int(h / 360 * 40)
        bar = " " * bar_pos + "●"
        print(f"  {sw} {slot} {h:>6.1f}° {rgb_fg(hex_val)}{bar}{reset()}")

    print()
    print(f"  {'─'*45}")
    print(f"  0°       90°      180°      270°      360°")
    print(f"  red    yellow    cyan     blue      red")

    # Gap analysis
    print_subheader("Hue Gaps")
    print(f"  {'From':<8} {'To':<8} {'Gap':>8}")
    print(f"  {'─'*8} {'─'*8} {'─'*8}")

    for i in range(len(hue_data)):
        h1, slot1, _, _ = hue_data[i]
        h2, slot2, _, _ = hue_data[(i+1) % len(hue_data)]

        gap = h2 - h1
        if gap < 0:
            gap += 360

        color = "#d9048e" if gap > 60 else "#f2a633" if gap > 45 else "#04b372"
        print(f"  {slot1:<8} {slot2:<8} {rgb_fg(color)}{gap:>8.1f}°{reset()}")

def show_palette_visual(colors: dict[str, str]):
    print_header("VISUAL PALETTE")

    print_subheader("Grayscale")
    print("  ", end="")
    for i in range(8):
        slot = f"base0{i}"
        print(labeled_swatch(colors[slot], 10), end="")
    print()
    print("  ", end="")
    for i in range(8):
        print(f"{'base0' + str(i):^10}", end="")
    print()

    print_subheader("Loud Accents")
    print("  ", end="")
    for slot in ['base08', 'base09', 'base0A', 'base0B', 'base0C', 'base0D', 'base0E', 'base0F']:
        print(labeled_swatch(colors[slot], 10), end="")
    print()
    print("  ", end="")
    for slot in ['base08', 'base09', 'base0A', 'base0B', 'base0C', 'base0D', 'base0E', 'base0F']:
        print(f"{slot:^10}", end="")
    print()

    print_subheader("Quiet Accents")
    print("  ", end="")
    for slot in ['base10', 'base11', 'base12', 'base13', 'base14', 'base15', 'base16', 'base17']:
        print(labeled_swatch(colors[slot], 10), end="")
    print()
    print("  ", end="")
    for slot in ['base10', 'base11', 'base12', 'base13', 'base14', 'base15', 'base16', 'base17']:
        print(f"{slot:^10}", end="")
    print()

    print_subheader("Loud → Quiet Pairs")
    pairs = [
        ('base08', 'base10'), ('base09', 'base11'), ('base0A', 'base12'), ('base0B', 'base13'),
        ('base0C', 'base14'), ('base0D', 'base15'), ('base0E', 'base16'), ('base0F', 'base17'),
    ]
    for loud, quiet in pairs:
        loud_sw = swatch(colors[loud], 8)
        quiet_sw = swatch(colors[quiet], 8)
        print(f"  {loud_sw} → {quiet_sw}  {loud} → {quiet}")

def suggest_grayscale(colors: dict[str, str]):
    print_header("GRAYSCALE SUGGESTIONS")

    print_subheader("Current vs Suggested Lightness")

    # Current values
    current = []
    for i in range(8):
        slot = f"base0{i}"
        L, C, h = hex_to_oklch(colors[slot])
        current.append((slot, colors[slot], L, C, h))

    # Suggested smooth progression
    # Keep base00-02 (backgrounds), base05-07 (text) mostly as-is
    # Redistribute base03-04 to fill the mid-range
    suggested_L = [
        current[0][2],  # base00 - keep
        current[1][2],  # base01 - keep
        current[2][2],  # base02 - keep
        0.48,           # base03 - lower (was 0.59)
        0.62,           # base04 - slightly higher to separate from base03
        current[5][2],  # base05 - keep
        current[6][2],  # base06 - keep
        current[7][2],  # base07 - keep
    ]

    print(f"  {'Slot':<8} {'Current L':>10} {'Suggest L':>10} {'Change':>10}")
    print(f"  {'─'*8} {'─'*10} {'─'*10} {'─'*10}")

    for i, (slot, hex_val, L, C, h) in enumerate(current):
        diff = suggested_L[i] - L
        if abs(diff) < 0.01:
            note = "(keep)"
            color = "#04b372"
        else:
            note = f"{diff:+.3f}"
            color = "#f2a633"
        print(f"  {slot:<8} {L:>10.3f} {suggested_L[i]:>10.3f} {rgb_fg(color)}{note:>10}{reset()}")

    print()
    print("  Note: base03 (comments) and base04 (UI) are currently too close.")
    print("  Consider lowering base03 to ~0.48 to create better separation.")

# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    root = Path(__file__).parent.parent  # repo root (parent of tools/)
    palette_path = root / "palette.toml"

    if not palette_path.exists():
        print(f"Error: {palette_path} not found")
        sys.exit(1)

    colors = parse_palette(palette_path)

    print()
    print(f"  {bold()}Human++ Palette Analyzer{reset()}")
    print(f"  Reading from: {palette_path}")
    print(f"  Found {len(colors)} colors")

    # Check for section filter
    section = None
    for arg in sys.argv[1:]:
        if arg.startswith("--section="):
            section = arg.split("=")[1].lower()

    if section is None or section == "visual":
        show_palette_visual(colors)

    if section is None or section == "grayscale":
        analyze_grayscale(colors)

    if section is None or section == "accents":
        analyze_accents(colors)

    if section is None or section == "pairs":
        analyze_pairs(colors)

    if section is None or section == "contrast":
        analyze_contrast(colors)

    if section is None or section == "hue":
        analyze_hue_wheel(colors)

    if section is None or section == "suggest":
        suggest_grayscale(colors)

    print()

if __name__ == "__main__":
    main()
