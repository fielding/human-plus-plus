# Changelog

All notable changes to Human++ will be documented in this file.

## [1.1.0] - 2025-01-28

### Theme Changes

**Revamped color-to-token mappings** for better semantic meaning across all supported editors:

| Element | Old | New |
|---------|-----|-----|
| Functions | base13 (green) | base15 (quiet blue) |
| Strings | base12 (cream) | base17 (quiet lime) |
| Parameters | base11 (orange) | base16 (quiet purple, italic) |
| Constants | base16 (purple) | base12 (quiet yellow) |
| Headings | base0A (yellow) | base10 (pink) |
| Inline code | base14 (cyan) | base0A (loud yellow) |
| Bold/Italic | various | base15 (quiet blue) |
| Blockquotes | base15 | base14 (cyan) |
| Link text | base0F (lime) | base17 (quiet lime) |
| Link URLs | base17 | base03 (muted) |

**Added markup language support** with consistent styling:
- AsciiDoc
- LaTeX
- Org mode
- reStructuredText
- HTML/XML

### Extension Changes (VS Code / Cursor)

**Keyword aliases for markers** - Legacy comment keywords now trigger marker highlighting:

| Keywords | Maps to | Color |
|----------|---------|-------|
| `FIXME`, `BUG`, `XXX` | `!!` | Lime (base0F) |
| `TODO`, `HACK` | `??` | Purple (base0E) |
| `NOTE`, `NB` | `>>` | Cyan (base0C) |

Priority: Explicit markers (`!!`, `??`, `>>`) always take precedence over keyword aliases.

### Documentation

- Updated README with correct color roles
- Added comprehensive markdown test file
- Preview images now reflect actual color mappings

### Known Issues

- Some languages may have inconsistent highlighting - contributions welcome!
- Semantic token highlighting is disabled to prevent conflicts with TextMate scopes

---

## [1.0.0] - 2025-01-27

### Added

- Initial release of Human++ Base24 color scheme
- Two-tier accent system: loud (base08-0F) for diagnostics, quiet (base10-17) for syntax
- Human intent markers: `!!` (attention), `??` (uncertainty), `>>` (reference)
- VS Code extension with:
  - Full color theme
  - Marker highlighting with colored backgrounds
  - Inline diagnostic badges
- Support for: Ghostty, Vim/Neovim (via tinty), Sketchybar, JankyBorders, skhd
- Static site with interactive palette viewer
