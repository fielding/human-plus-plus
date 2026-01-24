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
| base03 | `#5a5d62` | Comments (coffee brown) |
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
make build          # Build all theme files
make preview        # Preview palette in terminal
make colortest      # Display terminal ANSI mapping
make apply          # Apply theme to installed apps
make apply-dry      # Preview what apply would do
make analyze        # Analyze palette in OKLCH
```

Or apply with tinty: `tinty apply base24-human-plus-plus`

## Repository Structure

```
palette.toml          # Single source of truth (edit this)
Makefile              # Build orchestration
templates/            # HTML templates (no hardcoded hex)
tools/                # Python generators
scripts/              # Shell orchestration
site/assets/          # Logos and images (committed)
```

**Generated (not committed):**
```
dist/                 # Theme outputs (ghostty, vim, vscode, etc.)
site/index.html       # Landing page (from template)
site/data/            # Palette JSON for the website
```

Run `make build` locally, or let CI generate everything on push.

## CI/CD

- **Pull requests**: Build + analyze palette
- **Push to main**: Deploy site to GitHub Pages
- **Tags (`v*`)**: Create GitHub Release with dist/ artifacts

Download pre-built theme files from [Releases](https://github.com/fielding/human-plus-plus/releases).

## Preview

Visit [fielding.github.io/human-plus-plus](https://fielding.github.io/human-plus-plus/) for the live site.

To preview locally:
```bash
make build
python3 -m http.server -d site 8000
# Open http://localhost:8000
```

## License

MIT
