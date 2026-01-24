#!/usr/bin/env python3
"""
Derive a Base24-style "quiet" accent set from a Base16 palette using OKLCH.

- Reads a Base16 palette from either:
  1) TOML (e.g. palette.toml with keys base00..base0F)
  2) JSON (same keys)
- Produces new keys base16..base1D (quiet variants of base08..base0F by default)
- Uses OKLCH adjustments (keep hue, reduce chroma, nudge lightness)
- Gamut-clips safely back into sRGB

Usage examples:
  python derive_base24.py palette.toml
  python derive_base24.py palette.toml --out palette_base24.toml
  python derive_base24.py palette.toml --chroma 0.78 --lightness +0.035
  python derive_base24.py palette.toml --map base08=base16 base09=base17

Notes:
- OKLCH is a great default for "quiet siblings" because it preserves hue identity.
- Recommended starting knobs:
    chroma_mult: 0.72–0.82
    lightness_add: +0.02–+0.05
"""

from __future__ import annotations

import argparse
import json
import math
import os
from dataclasses import dataclass
from typing import Dict, Tuple

try:
    import tomllib  # py3.11+
except Exception:
    tomllib = None


# ----------------------------
# Color math: sRGB <-> OKLab <-> OKLCH
# ----------------------------

def clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)

def srgb_to_linear(c: float) -> float:
    # IEC 61966-2-1:1999
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4

def linear_to_srgb(c: float) -> float:
    if c <= 0.0031308:
        return 12.92 * c
    return 1.055 * (c ** (1 / 2.4)) - 0.055

def hex_to_rgb01(hex_color: str) -> Tuple[float, float, float]:
    h = hex_color.strip().lstrip("#")
    if len(h) != 6:
        raise ValueError(f"Expected 6-digit hex like #RRGGBB, got: {hex_color}")
    r = int(h[0:2], 16) / 255.0
    g = int(h[2:4], 16) / 255.0
    b = int(h[4:6], 16) / 255.0
    return r, g, b

def rgb01_to_hex(rgb: Tuple[float, float, float]) -> str:
    r, g, b = rgb
    r8 = int(round(clamp01(r) * 255))
    g8 = int(round(clamp01(g) * 255))
    b8 = int(round(clamp01(b) * 255))
    return f"#{r8:02x}{g8:02x}{b8:02x}"

def srgb_hex_to_oklab(hex_color: str) -> Tuple[float, float, float]:
    r, g, b = hex_to_rgb01(hex_color)
    rl, gl, bl = srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b)

    # linear sRGB -> LMS
    l = 0.4122214708 * rl + 0.5363325363 * gl + 0.0514459929 * bl
    m = 0.2119034982 * rl + 0.6806995451 * gl + 0.1073969566 * bl
    s = 0.0883024619 * rl + 0.2817188376 * gl + 0.6299787005 * bl

    l_ = l ** (1 / 3)
    m_ = m ** (1 / 3)
    s_ = s ** (1 / 3)

    # LMS -> OKLab
    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    b = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return L, a, b

def oklab_to_srgb_hex(Lab: Tuple[float, float, float]) -> str:
    L, a, b = Lab

    # OKLab -> LMS'
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b

    # cube
    l = l_ ** 3
    m = m_ ** 3
    s = s_ ** 3

    # LMS -> linear sRGB
    rl = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    gl = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bl = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s

    # linear -> srgb (with clamp)
    r = clamp01(linear_to_srgb(rl))
    g = clamp01(linear_to_srgb(gl))
    b = clamp01(linear_to_srgb(bl))
    return rgb01_to_hex((r, g, b))

def oklab_to_oklch(Lab: Tuple[float, float, float]) -> Tuple[float, float, float]:
    L, a, b = Lab
    C = math.sqrt(a * a + b * b)
    h = math.degrees(math.atan2(b, a)) % 360.0
    return L, C, h

def oklch_to_oklab(LCh: Tuple[float, float, float]) -> Tuple[float, float, float]:
    L, C, h = LCh
    hr = math.radians(h)
    a = C * math.cos(hr)
    b = C * math.sin(hr)
    return (L, a, b)

def gamut_clip_oklch(LCh: Tuple[float, float, float], max_iter: int = 18) -> Tuple[float, float, float]:
    """
    If OKLCH converts outside sRGB gamut, reduce chroma until it fits.
    Conservative + stable for theme work.
    """
    L, C, h = LCh

    def in_gamut(hex_color: str) -> bool:
        # if converting produced clamped values, we can't directly detect,
        # so we do a "round trip" tolerance check in linear space.
        # Practical shortcut: attempt convert and see if any channel would be outside [0,1]
        # by converting without clamp. We'll approximate by checking OKLab->linear sRGB.
        Lab = oklch_to_oklab((L, C, h))
        L2, a2, b2 = Lab
        l_ = L2 + 0.3963377774 * a2 + 0.2158037573 * b2
        m_ = L2 - 0.1055613458 * a2 - 0.0638541728 * b2
        s_ = L2 - 0.0894841775 * a2 - 1.2914855480 * b2
        l = l_ ** 3
        m = m_ ** 3
        s = s_ ** 3
        rl = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
        gl = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
        bl = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
        # check linear channels in [0,1]
        return (0.0 <= rl <= 1.0) and (0.0 <= gl <= 1.0) and (0.0 <= bl <= 1.0)

    if in_gamut(oklab_to_srgb_hex(oklch_to_oklab((L, C, h)))):
        return (L, C, h)

    lo, hi = 0.0, C
    for _ in range(max_iter):
        mid = (lo + hi) / 2.0
        if in_gamut(oklab_to_srgb_hex(oklch_to_oklab((L, mid, h)))):
            lo = mid
        else:
            hi = mid
    return (L, lo, h)


# ----------------------------
# IO helpers
# ----------------------------

def load_palette(path: str) -> Dict[str, str]:
    ext = os.path.splitext(path)[1].lower()
    with open(path, "rb") as f:
        raw = f.read()

    if ext in (".toml",):
        if tomllib is None:
            raise RuntimeError("tomllib not available. Use Python 3.11+ or convert palette to JSON.")
        data = tomllib.loads(raw.decode("utf-8"))
        # allow either flat keys or [palette] table
        if "palette" in data and isinstance(data["palette"], dict):
            data = data["palette"]
        # check for [base16] section
        if "base16" in data and isinstance(data["base16"], dict):
            data = data["base16"]
        # normalize hex strings
        return {k: v for k, v in data.items() if k.startswith("base") and isinstance(v, str)}
    elif ext in (".json",):
        data = json.loads(raw.decode("utf-8"))
        if "palette" in data and isinstance(data["palette"], dict):
            data = data["palette"]
        return {k: v for k, v in data.items() if k.startswith("base") and isinstance(v, str)}
    else:
        raise ValueError(f"Unsupported input extension: {ext} (use .toml or .json)")

def dump_toml(palette: Dict[str, str]) -> str:
    # minimal TOML writer for flat key/value
    lines = []
    for k in sorted(palette.keys()):
        lines.append(f'{k} = "{palette[k]}"')
    return "\n".join(lines) + "\n"

def dump_json(palette: Dict[str, str]) -> str:
    return json.dumps(palette, indent=2) + "\n"


# ----------------------------
# Derivation logic
# ----------------------------

@dataclass
class DeriveParams:
    chroma_mult: float
    lightness_add: float
    chroma_floor: float = 0.001  # avoid weird hue at 0
    lightness_min: float = 0.0
    lightness_max: float = 1.0

def derive_quiet(hex_color: str, p: DeriveParams) -> str:
    Lab = srgb_hex_to_oklab(hex_color)
    L, C, h = oklab_to_oklch(Lab)

    # adjust
    L2 = max(p.lightness_min, min(p.lightness_max, L + p.lightness_add))
    C2 = max(p.chroma_floor, C * p.chroma_mult)

    # gamut clip by chroma reduction if needed
    LCh2 = gamut_clip_oklch((L2, C2, h))
    return oklab_to_srgb_hex(oklch_to_oklab(LCh2))

def build_base24(palette: Dict[str, str], p: DeriveParams, include_highlighter: bool = False) -> Dict[str, str]:
    """
    By default derives:
      base16..base1D  from base08..base0F
    You can exclude base0F (highlighter) if you want it to stay "nuclear".
    """
    out = dict(palette)

    src_keys = ["base08","base09","base0A","base0B","base0C","base0D","base0E","base0F"]
    dst_keys = ["base16","base17","base18","base19","base1A","base1B","base1C","base1D"]

    for s, d in zip(src_keys, dst_keys):
        if s == "base0F" and not include_highlighter:
            continue
        if s not in palette:
            raise KeyError(f"Missing {s} in input palette.")
        out[d] = derive_quiet(palette[s], p)

    return out


# ----------------------------
# CLI
# ----------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("palette_path", help="Path to palette TOML/JSON containing base00..base0F")
    ap.add_argument("--out", help="Write output palette to this path (extension decides format)")
    ap.add_argument("--chroma", type=float, default=0.78, help="Multiply chroma by this (quieting). Default 0.78")
    ap.add_argument("--lightness", type=float, default=0.035, help="Add to OKLCH lightness. Default +0.035")
    ap.add_argument("--include-highlighter", action="store_true", help="Also derive a quiet variant of base0F (usually NO).")
    args = ap.parse_args()

    pal = load_palette(args.palette_path)
    params = DeriveParams(chroma_mult=args.chroma, lightness_add=args.lightness)

    out = build_base24(pal, params, include_highlighter=args.include_highlighter)

    # print a helpful diff-ish view
    print("Derived Base24 accents (quiet) from Base16:")
    mapping = [
        ("base08", "base16"),
        ("base09", "base17"),
        ("base0A", "base18"),
        ("base0B", "base19"),
        ("base0C", "base1A"),
        ("base0D", "base1B"),
        ("base0E", "base1C"),
        ("base0F", "base1D"),
    ]
    for s, d in mapping:
        if d not in out:
            continue
        print(f"  {d}  (quiet of {s})  {out[d]}   <- {pal.get(s)}")

    if args.out:
        ext = os.path.splitext(args.out)[1].lower()
        if ext == ".toml":
            content = dump_toml(out)
        elif ext == ".json":
            content = dump_json(out)
        else:
            raise ValueError("Output extension must be .toml or .json")
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\nWrote: {args.out}")
    else:
        # default to stdout in same format as input
        in_ext = os.path.splitext(args.palette_path)[1].lower()
        if in_ext == ".toml":
            print("\n--- palette (toml) ---")
            print(dump_toml(out))
        else:
            print("\n--- palette (json) ---")
            print(dump_json(out))


if __name__ == "__main__":
    main()
