# Human++

A Base24 color scheme for the post-artisanal coding era.

**Code is cheap. Intent is scarce.**

As models write more code, humans spend more time reviewing, planning, and explaining intent. Human++ makes human judgment visible at a glance.

## Features

### Color Theme

Human++ inverts traditional syntax highlighting priority:

- **Quiet syntax** - everyday code fades into the background
- **Loud diagnostics** - errors, warnings, and human markers demand attention

The result: when you see color, it means something.

### Human Intent Markers

Use punctuation markers in comments to flag human judgment:

| Marker | Meaning |
|--------|---------|
| `!!` | Pay attention here |
| `??` | I'm uncertain |
| `>>` | See reference |

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

Markers are highlighted with a bright lime background, making human intent instantly visible.

### Why punctuation?

- Fast to type
- Easy to scan
- Easy to grep: `rg "// !!|// \?\?|// >>"`
- Easy for editors to highlight

## Commands

- `Human++: Toggle Marker Highlighting` - Enable/disable marker highlighting
- `Human++: Refresh Marker Decorations` - Manually refresh decorations

## Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `humanpp.enable` | `true` | Enable marker highlighting |
| `humanpp.highlightRestOfLine` | `true` | Highlight text after marker |
| `humanpp.markerColor` | `#bbff00` | Marker background color |
| `humanpp.markerTextColor` | `#1b1d20` | Marker text color |

## License

MIT
