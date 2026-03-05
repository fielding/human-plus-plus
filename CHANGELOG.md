# Changelog

All notable changes to Human++ will be documented in this file.

## [1.5.0] - 2026-03-05

### Added

- **Comprehensive markdown syntax highlighting** for VS Code, Cursor, and Neovim
  - Headings (H1-H6): H1 lime badge, H2-H6 loud pink (base08)
  - Bold: loud blue (base0D), Italic: quiet blue (base15)
  - Inline code: amber (base0A), Code blocks: quiet cyan (base14)
  - Blockquotes: quiet cyan italic (base14)
  - Links: quiet lime (base17), URLs: dimmed (base03)
  - Table pipes and list bullets: dimmed (base04)
  - Markup delimiters (`**`, `*`, `` ` ``): dimmed (base04)
- **Neovim treesitter auto-activation** for markdown files (no manual setup needed)
- **Neovim heading extmarks** for H1-H6 with reliable priority override
- **Traditional vim syntax fallback** groups for non-treesitter markdown (plasticboy/vim-markdown, vim-polyglot)
- **Markdown tab** on the project landing page showcasing syntax highlighting
- Markdown body text uses base07 (brightest foreground) via window-local highlight

### Changed

- VS Code/Cursor list items now use normal foreground text; only the bullet character is dimmed (base04)

### Fixed

- Neovim `!!` marker no longer falsely triggers mid-line in markdown prose (now requires start-of-line)
- Neovim markdown inline code was using wrong color (base09 loud orange instead of base0A amber)

---

## [1.4.0] - 2026-02-22

### Added

- **Fastfetch generator** - `dist/fastfetch/config.jsonc` with palette-matched logo, key, title, and output colors
- **256-color extended slot remapping** - Shell-init now maps slots 16-23 to the 8 base24 colors that lack ANSI 0-15 assignments (base09, base0F, base01, base02, base04, base05, base11, base17), making all 24 colors addressable via `\e[38;5;16-23m`
- Fastfetch config auto-symlinked in `shell-init.sh` when fastfetch is installed

### Fixed

- **Delta config quoting** - Hex values in generated `delta/config.gitconfig` now properly quoted to prevent gitconfig `#`-as-comment parsing (fixes `blame-palette must be empty` error)

---

## [1.3.0] - 2026-02-06

### Added

- **Tmux theme generator** - `dist/tmux/human-plus-plus.conf` and `dist/tmux/colors.sh` with full palette support
- README extracted to template (`templates/README.md.tmpl`) for easier contributions

### Fixed

- Duplicate entries in README apps table
- Shell tools added to README with git include instructions

---

## [1.2.0] - 2026-01-29

### Added

- **Shell tool themes** - eza, fzf, bat, glow, delta, and git color generators
- **Shell init loader** (`dist/shell-init.sh`) - Single-line sourcing for all shell tool configs
- **h1 markdown highlighting** - Lime badge style for top-level headings in bat and glow
- Badge-style README highlighting in eza

### Changed

- Refined eza colors: quiet metadata, grayscale for user/group
- Site changelog simplified to full-width 2-column grid
- Version badge in site hero links to changelog section

---

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
