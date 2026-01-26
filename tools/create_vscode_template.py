#!/usr/bin/env python3
"""
Create VS Code theme template from existing theme file.

This script creates a template by replacing hardcoded hex values with
mustache-style placeholders ({{base00}}, {{base08}}, etc.)

Run once to create the template, then use build.py to generate themes.
"""

import re
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
PALETTE = ROOT / "palette.toml"
THEME = ROOT / "packages/vscode-extension/themes/human-plus-plus.json"
TEMPLATE = ROOT / "templates/vscode/theme.json.tmpl"

def parse_palette():
    """Parse palette.toml and return hex -> slot mapping."""
    content = PALETTE.read_text()
    hex_to_slot = {}

    for line in content.split('\n'):
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('['):
            continue

        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()

            # Remove quotes and inline comments
            if value.startswith('"') and '"' in value[1:]:
                value = value[1:value.index('"', 1)]
            elif value.startswith("'") and "'" in value[1:]:
                value = value[1:value.index("'", 1)]

            if key.startswith('base') and value.startswith('#'):
                # Map hex (lowercase) to slot name
                hex_to_slot[value.lower()] = key

    return hex_to_slot

def create_template():
    """Create template from existing theme."""
    hex_to_slot = parse_palette()
    print(f"Found {len(hex_to_slot)} colors in palette:")
    for hex_val, slot in sorted(hex_to_slot.items(), key=lambda x: x[1]):
        print(f"  {slot}: {hex_val}")

    content = THEME.read_text()

    # Track replacements
    replacements = {}

    # Sort hex values by length (longest first) to avoid partial matches
    # e.g., replace #1a1c22bf before #1a1c22
    sorted_hexes = sorted(hex_to_slot.keys(), key=len, reverse=True)

    # First pass: replace exact hex matches (with or without alpha suffix)
    for hex_val in sorted_hexes:
        slot = hex_to_slot[hex_val]
        hex_no_hash = hex_val[1:]  # Remove # for pattern matching

        # Pattern to match this hex with optional alpha suffix
        # e.g., #1a1c22 or #1a1c2219 or #1a1c22bf
        pattern = re.compile(
            rf'(#)({re.escape(hex_no_hash)})([0-9a-fA-F]{{0,2}})(?![0-9a-fA-F])',
            re.IGNORECASE
        )

        def replace_fn(match):
            alpha = match.group(3).lower() if match.group(3) else ''
            key = f"{slot}|{alpha}" if alpha else slot
            if key not in replacements:
                replacements[key] = 0
            replacements[key] += 1

            if alpha:
                return f"{{{{{slot}}}}}{alpha}"
            else:
                return f"{{{{{slot}}}}}"

        content = pattern.sub(replace_fn, content)

    # Report replacements
    print(f"\nReplacements made:")
    for key, count in sorted(replacements.items()):
        print(f"  {key}: {count}")

    # Write template
    TEMPLATE.parent.mkdir(parents=True, exist_ok=True)
    TEMPLATE.write_text(content)
    print(f"\n✓ Template written to {TEMPLATE}")

    # Count remaining hardcoded hex values
    remaining = re.findall(r'#[0-9a-fA-F]{6,8}', content)
    remaining_unique = set(h.lower() for h in remaining)
    if remaining_unique:
        print(f"\n⚠ {len(remaining_unique)} hex values not in palette (may be intentional):")
        for hex_val in sorted(remaining_unique):
            count = sum(1 for h in remaining if h.lower() == hex_val)
            print(f"  {hex_val}: {count} occurrences")

if __name__ == '__main__':
    create_template()
