# Human++

A Base24 color scheme for the post-artisanal coding era.

**Code is cheap. Intent is scarce.**

As models write more code, humans spend more time reviewing, planning, and explaining intent. Human++ makes human judgment visible at a glance through a two-tier accent system and lightweight annotation markers.

## Philosophy

Human++ inverts the traditional syntax highlighting priority:

- **Quiet syntax** — everyday code fades into the background
- **Loud diagnostics** — errors, warnings, and human markers demand attention
- **Terminal exception** — terminal output is intentional, so terminals get loud colors

The result: when you see color, it means something.

## The Palette

Human++ Cool Balanced uses a cool charcoal grayscale with warm text and a full Base24 palette.

### Grayscale

| Slot | Hex | Role |
|------|-----|------|
| base00 | `#1a1c22` | Background |
| base01 | `#282b31` | Elevation |
| base02 | `#3a3d42` | Selection |
| base03 | `#5a5d62` | Comments (cool gray) |
| base04 | `#828079` | UI secondary |
| base05 | `#dbd6cc` | Main text |
| base06 | `#eeeae2` | Emphasis |
| base07 | `#f8f6f2` | Brightest |

### Loud Accents (Diagnostics & Signals)

| Slot | Hex | Role |
|------|-----|------|
| base08 | `#e7349c` | Errors, attention |
| base09 | `#f26c33` | Warnings |
| base0A | `#f2a633` | Caution |
| base0B | `#04b372` | Success |
| base0C | `#1ad0d6` | Info |
| base0D | `#458ae2` | Links, focus |
| base0E | `#9871fe` | Special |
| base0F | `#bbff00` | Human intent marker |

### Quiet Accents (Syntax & UI)

| Slot | Hex | Role |
|------|-----|------|
| base10 | `#c8518f` | Keywords |
| base11 | `#d68c6f` | Secondary |
| base12 | `#dfb683` | Strings |
| base13 | `#61b186` | Functions |
| base14 | `#91cbcd` | Types |
| base15 | `#5e84b6` | Hints |
| base16 | `#8f72e3` | Constants |
| base17 | `#d2fc91` | Quiet lime |

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

## Build

All theme files are generated from `palette.toml`:

```bash
# Build everything
python3 build.py

# Apply with tinty
tinty apply base24-human-plus-plus
```

## Files

| File | Description |
|------|-------------|
| `palette.toml` | Source of truth |
| `build.py` | Generates all theme files |
| `ghostty/config` | Ghostty terminal |
| `shell/` | Shell theme script |
| `sketchybar/colors.sh` | Sketchybar |
| `skhd/modes.sh` | skhd mode indicators |
| `borders/bordersrc` | JankyBorders |
| `vim/colors/` | Vim/Neovim |
| `iterm/` | iTerm2 |
| `vscode-extension/` | VS Code / Cursor extension |
| `index.html` | Landing page |
| `swatches.html` | Interactive palette preview |

## Preview

Open `swatches.html` in a browser to see the full palette with:

- Interactive color swatches
- Loud vs quiet comparison
- Human marker examples
- Live code preview

## License

MIT
