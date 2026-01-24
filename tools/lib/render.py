"""
Template rendering utilities for Human++ color scheme.
"""
import re
from pathlib import Path
from typing import Dict


def render_template(template: str, colors: Dict[str, str], meta: Dict[str, str] = None) -> str:
    """
    Render a template string with palette values.

    Supports:
        {{base00}} -> #1a1c22
        {{name}} -> palette name
        {{author}} -> palette author
        {{description}} -> palette description

    Template placeholders use double braces to avoid conflicts with
    CSS/JS single braces.
    """
    result = template

    # Replace color placeholders
    for slot, hex_color in colors.items():
        result = result.replace(f'{{{{{slot}}}}}', hex_color)

    # Replace meta placeholders
    if meta:
        for key, value in meta.items():
            result = result.replace(f'{{{{{key}}}}}', value)

    return result


def render_template_file(template_path: Path, output_path: Path,
                         colors: Dict[str, str], meta: Dict[str, str] = None) -> None:
    """
    Read template file, render with palette, write to output.
    """
    template = template_path.read_text()
    rendered = render_template(template, colors, meta)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered)


def generate_css_vars(colors: Dict[str, str], indent: str = '  ') -> str:
    """
    Generate CSS custom properties from palette.

    Returns:
        --base00: #1a1c22;
        --base01: #282b31;
        ...
    """
    lines = []
    for slot in sorted(colors.keys(), key=lambda s: (len(s), s)):
        lines.append(f'{indent}--{slot}: {colors[slot]};')
    return '\n'.join(lines)


def generate_css_root(colors: Dict[str, str]) -> str:
    """
    Generate complete :root block with CSS variables.

    Returns:
        :root {
          --base00: #1a1c22;
          ...
        }
    """
    vars_block = generate_css_vars(colors)
    return f':root {{\n{vars_block}\n}}'
