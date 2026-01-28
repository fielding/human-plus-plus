# Changelog

All notable changes to the Human++ VS Code extension will be documented in this file.

## [1.1.0] - 2025-01-28

### Added
- **Keyword aliases for markers**: Legacy comment keywords now map to Human++ markers:
  - `FIXME`, `BUG`, `XXX` → `!!` (intervention/attention) - Lime
  - `TODO`, `HACK` → `??` (uncertainty) - Purple
  - `NOTE`, `NB` → `>>` (reference/directive) - Cyan
- Support for multiple markup languages (AsciiDoc, LaTeX, Org mode, RST, HTML/XML)

### Changed
- **Revamped color-to-token mappings** for better semantic meaning:
  - Functions: base15 (quiet blue)
  - Strings: base17 (quiet lime)
  - Types/Classes: base14 (cyan)
  - Parameters: base16 (quiet purple, italic)
  - Constants: base12 (quiet yellow)
  - Keywords: base10 (quiet pink)
- Markdown styling improvements:
  - Headings: base10 (pink)
  - Bold/Italic: base15 (quiet blue)
  - Inline code: base0A (loud yellow)
  - Blockquotes: base14 (cyan)
  - Links: base17 (quiet lime) / base03 (URL)
- Updated preview images to reflect new color mappings

### Fixed
- Markdown heading scopes now properly target all heading levels
- Consistent color usage across all supported markup languages

## [1.0.0] - 2025-01-27

### Added
- Initial release
- Base24 color theme with two-tier accent system
- Human intent marker highlighting (`!!`, `??`, `>>`)
- Inline diagnostic badges for errors/warnings
- Support for TypeScript, JavaScript, Python, Rust, Go, and more
