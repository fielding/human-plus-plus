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

```js
// Regular comment stays calm (base03)

// !! Critical: don't change without talking to Sarah
if (legacyMode) {
  // ?? Not sure this handles the edge case
  return transformLegacy(data);
}

// >> See utils.ts for the transform logic
return transform(data);
```

### Why punctuation?

- Fast to type
- Easy to scan
- Easy to grep: `rg "// !!|// \?\?|// >>"`
- Easy for editors to highlight

## Install

All theme files are generated from `palette.toml`:

```bash
# Clone the repo
git clone https://github.com/fielding/human-plus-plus

# Build everything
python3 build.py

# Apply with tinty
tinty apply base24-human-plus-plus
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

## Preview

Visit the [landing page](https://fielding.github.io/human-plus-plus/) or open `swatches.html` locally to see:

- Interactive color swatches
- Loud vs quiet comparison
- Human marker examples
- Live code preview

## License

MIT
