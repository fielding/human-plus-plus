"""
Color math utilities for Human++ color scheme.
"""
from typing import Tuple, Dict


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert #rrggbb to (r, g, b) tuple (0-255)."""
    hex_color = hex_color.lstrip('#')
    return (
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16),
    )


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert (r, g, b) tuple to #rrggbb."""
    return f'#{r:02x}{g:02x}{b:02x}'


def hex_to_components(hex_color: str) -> Dict:
    """
    Convert #rrggbb to various formats for template rendering.

    Returns dict with:
        hex: 'rrggbb' (no hash)
        hex_hash: '#rrggbb'
        hex_r, hex_g, hex_b: individual hex components
        rgb_r, rgb_g, rgb_b: 0-255 integers
        dec_r, dec_g, dec_b: 0.0-1.0 floats
        argb: '0xffrrggbb' (for macOS APIs)
    """
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    return {
        'hex': hex_color,
        'hex_hash': f'#{hex_color}',
        'hex_r': hex_color[0:2],
        'hex_g': hex_color[2:4],
        'hex_b': hex_color[4:6],
        'rgb_r': r,
        'rgb_g': g,
        'rgb_b': b,
        'dec_r': r / 255.0,
        'dec_g': g / 255.0,
        'dec_b': b / 255.0,
        'argb': f'0xff{hex_color}',
    }


def luminance(hex_color: str) -> float:
    """
    Calculate relative luminance per WCAG 2.1.
    Returns value between 0 (black) and 1 (white).
    """
    r, g, b = hex_to_rgb(hex_color)

    def channel_luminance(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    return (
        0.2126 * channel_luminance(r) +
        0.7152 * channel_luminance(g) +
        0.0722 * channel_luminance(b)
    )


def contrast_ratio(color1: str, color2: str) -> float:
    """
    Calculate WCAG contrast ratio between two colors.
    Returns value between 1 (identical) and 21 (black/white).
    """
    l1 = luminance(color1)
    l2 = luminance(color2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def is_light(hex_color: str) -> bool:
    """Return True if color is perceptually light (for text color selection)."""
    r, g, b = hex_to_rgb(hex_color)
    # Using perceived brightness formula
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return brightness > 128
