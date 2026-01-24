"""
Palette parsing and validation for Human++ color scheme.
"""
from pathlib import Path
from typing import Dict, Tuple, Any

# Expected Base24 slots
BASE24_SLOTS = [
    'base00', 'base01', 'base02', 'base03', 'base04', 'base05', 'base06', 'base07',
    'base08', 'base09', 'base0A', 'base0B', 'base0C', 'base0D', 'base0E', 'base0F',
    'base10', 'base11', 'base12', 'base13', 'base14', 'base15', 'base16', 'base17',
]


def load_palette(palette_path: Path) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Parse palette.toml and return (colors, meta) dicts.

    colors: {'base00': '#1a1c22', ...}
    meta: {'name': '...', 'author': '...', 'description': '...'}
    """
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

            # Remove quotes
            if value.startswith('"') and '"' in value[1:]:
                value = value[1:value.index('"', 1)]
            elif value.startswith("'") and "'" in value[1:]:
                value = value[1:value.index("'", 1)]

            if key in ['name', 'author', 'description']:
                meta[key] = value
            elif key.startswith('base') and value.startswith('#'):
                colors[key] = value

    return colors, meta


def validate_palette(colors: Dict[str, str]) -> list:
    """
    Validate that all Base24 slots are present and have valid hex colors.
    Returns list of error messages (empty if valid).
    """
    errors = []

    for slot in BASE24_SLOTS:
        if slot not in colors:
            errors.append(f"Missing required slot: {slot}")
        elif not colors[slot].startswith('#') or len(colors[slot]) != 7:
            errors.append(f"Invalid hex color for {slot}: {colors[slot]}")

    return errors


def palette_to_json(colors: Dict[str, str], meta: Dict[str, str]) -> Dict[str, Any]:
    """
    Convert palette to JSON-serializable dict for site/data/palette.json.
    """
    return {
        'name': meta.get('name', 'Human++'),
        'author': meta.get('author', ''),
        'description': meta.get('description', ''),
        'colors': colors,
        'slots': {
            'grayscale': ['base00', 'base01', 'base02', 'base03', 'base04', 'base05', 'base06', 'base07'],
            'loud': ['base08', 'base09', 'base0A', 'base0B', 'base0C', 'base0D', 'base0E', 'base0F'],
            'quiet': ['base10', 'base11', 'base12', 'base13', 'base14', 'base15', 'base16', 'base17'],
        },
        'roles': {
            'base00': 'Background',
            'base01': 'Elevation',
            'base02': 'Selection',
            'base03': 'Comments (AI voice)',
            'base04': 'UI secondary',
            'base05': 'Main text',
            'base06': 'Emphasis',
            'base07': 'Brightest',
            'base08': 'Errors, attention',
            'base09': 'Warnings',
            'base0A': 'Caution',
            'base0B': 'Success',
            'base0C': 'Info',
            'base0D': 'Links, focus',
            'base0E': 'Special',
            'base0F': 'Human intent marker',
            'base10': 'Keywords',
            'base11': 'Secondary',
            'base12': 'Strings',
            'base13': 'Functions',
            'base14': 'Types',
            'base15': 'Hints',
            'base16': 'Constants',
            'base17': 'Quiet lime',
        }
    }
