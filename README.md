<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="banner-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="banner-light.svg">
    <img src="banner-dark.svg" alt="Human++ - Code is cheap. Intent is scarce." width="600">
  </picture>
</p>

<p align="center">
  A Base24 color scheme for the post-artisanal coding era.
</p>

<p align="center">
  <a href="https://fielding.github.io/human-plus-plus/">Website</a> •
  <a href="#install">Install</a> •
  <a href="#the-palette">Palette</a> •
  <a href="#human-intent-markers">Markers</a>
</p>

---

As models write more code, humans spend more time reviewing, planning, and explaining intent. Human++ makes human judgment visible at a glance through a two-tier accent system and lightweight annotation markers.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="preview-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="preview-light.svg">
    <img src="preview-dark.svg" alt="Human++ Theme Preview" width="650">
  </picture>
</p>

## Philosophy

Human++ inverts the traditional syntax highlighting priority:

- **Quiet syntax** — everyday code fades into the background
- **Loud diagnostics** — errors, warnings, and human markers demand attention
- **Terminal exception** — terminal output is intentional, so terminals get loud colors

The result: when you see color, it means something.

## The Palette

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="palette-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="palette-light.svg">
    <img src="palette-dark.svg" alt="Human++ Palette" width="700">
  </picture>
</p>

Human++ Cool Balanced uses a cool charcoal grayscale with warm cream text and a full Base24 palette:

- **base00–07** — Cool grayscale from charcoal to warm cream
- **base08–0F** — Loud accents for diagnostics and signals
- **base10–17** — Quiet accents for syntax and UI

## Human Intent Markers

Use punctuation markers in comments to flag human judgment:

| Marker | Meaning | Color |
|--------|---------|-------|
| `!!` | Pay attention here | Lime (base0F) |
| `??` | I'm uncertain | Purple (base0E) |
| `>>` | See reference | Cyan (base0C) |

### Why punctuation?

- Fast to type
- Easy to scan
- Easy to grep: `rg "// !!|// \?\?|// >>"`
- Easy for editors to highlight

## Install

All theme files are generated from `palette.toml`:

```bash
git clone https://github.com/fielding/human-plus-plus
python3 build.py
```

### Supported Apps

| App | File |
|-----|------|
| Ghostty | `ghostty/config` |
| VS Code / Cursor | `vscode-extension/` |
| Vim / Neovim | `vim/colors/` |
| iTerm2 | `iterm/` |
| Shell | `shell/` |
| Sketchybar | `sketchybar/colors.sh` |
| JankyBorders | `borders/bordersrc` |
| skhd | `skhd/modes.sh` |

## License

MIT
