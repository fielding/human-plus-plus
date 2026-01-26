# Human++ for VS Code

A Base24 color scheme for the post-artisanal coding era.

**Code is cheap. Intent is scarce.**

## Features

### 1. Color Theme

Human++ inverts traditional syntax highlighting priority:

- **Quiet syntax** — everyday code fades into the background
- **Loud diagnostics** — errors, warnings, and human markers demand attention

The result: when you see color, it means something.

### 2. Human Intent Markers

Use punctuation markers in comments to flag human judgment:

| Marker | Meaning | Color |
|--------|---------|-------|
| `!!` | Pay attention here | Lime |
| `??` | I'm uncertain | Purple |
| `>>` | See reference | Cyan |

```js
// Regular comment stays calm

// !! Critical: don't change without talking to Sarah
if (legacyMode) {
  // ?? Not sure this handles the edge case
  return transformLegacy(data);
}

// >> See utils.ts for the transform logic
return transform(data);
```

Markers are highlighted with bright backgrounds, making human intent instantly visible.

### 3. Inline Diagnostics

Errors and warnings appear as inline badges at the end of lines, so you don't need to hover or check the Problems panel.

## Commands

- `Human++: Toggle Marker Highlighting` — Enable/disable all highlighting
- `Human++: Refresh Marker Decorations` — Manually refresh decorations

## Settings

### Marker Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `human-plus-plus.enable` | `true` | Enable Human++ marker highlighting |
| `human-plus-plus.debounceMs` | `200` | Debounce delay for rescanning on edit |
| `human-plus-plus.markers.intervention.enable` | `true` | Enable `!!` marker |
| `human-plus-plus.markers.uncertainty.enable` | `true` | Enable `??` marker |
| `human-plus-plus.markers.directive.enable` | `true` | Enable `>>` marker |

### Diagnostic Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `human-plus-plus.diagnostics.enable` | `true` | Enable inline diagnostic badges |
| `human-plus-plus.diagnostics.error.enable` | `true` | Show error diagnostics |
| `human-plus-plus.diagnostics.warning.enable` | `true` | Show warning diagnostics |
| `human-plus-plus.diagnostics.info.enable` | `true` | Show info diagnostics |
| `human-plus-plus.diagnostics.hint.enable` | `false` | Show hint diagnostics |

## Why punctuation markers?

- Fast to type
- Easy to scan
- Easy to grep: `rg "// !!|// \?\?|// >>"`
- Works in any language with comments

## Links

- [Human++ on GitHub](https://github.com/fielding/human-plus-plus)
- [Website](https://fielding.github.io/human-plus-plus/)

## License

MIT
