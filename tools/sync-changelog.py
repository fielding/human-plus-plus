#!/usr/bin/env python3
"""
Sync CHANGELOG.md to the website template.

Parses the markdown changelog and generates HTML for the site's changelog section.
"""

import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
CHANGELOG = ROOT / "CHANGELOG.md"
SITE_TEMPLATE = ROOT / "templates" / "site" / "index.html.tmpl"


def parse_changelog():
    """Parse CHANGELOG.md and extract versions."""
    content = CHANGELOG.read_text()
    versions = []

    # Split by version headers
    version_pattern = r'^## \[(\d+\.\d+\.\d+)\] - (\d{4}-\d{2}-\d{2})'

    parts = re.split(r'^(## \[\d+\.\d+\.\d+\])', content, flags=re.MULTILINE)

    current_version = None
    current_date = None
    current_content = []

    for part in parts:
        version_match = re.match(r'^## \[(\d+\.\d+\.\d+)\]', part)
        if version_match:
            # Save previous version if exists
            if current_version:
                versions.append({
                    'version': current_version,
                    'date': current_date,
                    'content': '\n'.join(current_content).strip()
                })
            current_version = version_match.group(1)
            current_content = []
        elif current_version:
            # Extract date from first line
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', part)
            if date_match and not current_date:
                current_date = date_match.group(1)
                # Remove the date line
                part = re.sub(r'^\s*-\s*\d{4}-\d{2}-\d{2}\s*\n?', '', part)
            current_content.append(part)

    # Don't forget the last version
    if current_version:
        versions.append({
            'version': current_version,
            'date': current_date,
            'content': '\n'.join(current_content).strip()
        })

    return versions


def markdown_to_html(md_content):
    """Convert simplified markdown to HTML for changelog."""
    html = md_content

    # Convert headers
    html = re.sub(r'^### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)

    # Convert bold
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

    # Convert inline code
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)

    # Convert list items (simplified - assumes flat lists)
    lines = html.split('\n')
    in_list = False
    result = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                result.append('<ul>')
                in_list = True
            item_content = stripped[2:]
            result.append(f'<li>{item_content}</li>')
        elif stripped.startswith('|'):
            # Skip tables for now
            continue
        else:
            if in_list and stripped:
                result.append('</ul>')
                in_list = False
            if stripped and not stripped.startswith('<'):
                result.append(f'<p>{stripped}</p>')
            elif stripped:
                result.append(stripped)

    if in_list:
        result.append('</ul>')

    return '\n            '.join(result)


def generate_changelog_html(versions, max_versions=1):
    """Generate HTML for the changelog section (latest version only)."""
    if not versions:
        return ''

    v = versions[0]  # Only show latest
    content_html = markdown_to_html(v['content'])

    return f'''        <div class="changelog-latest">
          <div class="changelog-header">
            <span class="version-number">v{v['version']}</span>
            <span class="version-date">{v['date']}</span>
          </div>
          <div class="changelog-content">
            {content_html}
          </div>
        </div>'''


def update_site_template(changelog_html):
    """Update the site template with new changelog HTML."""
    content = SITE_TEMPLATE.read_text()

    # Find and replace the changelog section
    # Look for the div.changelog and replace its contents (including the changelog-latest div)
    pattern = r'(<div class="changelog">)\s*<div class="changelog-latest">.*?</div>\s*</div>\s*(</div>\s*<p style="text-align: center)'

    replacement = f'\\1\n{changelog_html}\n      \\2'

    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    if new_content != content:
        SITE_TEMPLATE.write_text(new_content)
        print(f"  ✓ Updated site template with {len(changelog_html)} bytes of changelog")
        return True
    else:
        print("  - No changes needed to site template")
        return False


def main():
    print("Syncing changelog to site...")

    if not CHANGELOG.exists():
        print("  ! CHANGELOG.md not found")
        return

    versions = parse_changelog()
    print(f"  Found {len(versions)} versions in CHANGELOG.md")

    if not versions:
        print("  ! No versions found")
        return

    changelog_html = generate_changelog_html(versions)
    update_site_template(changelog_html)


if __name__ == "__main__":
    main()
