# Human++

A Base16 color scheme and lightweight annotation convention for the post-artisanal coding era.

As models write more code, humans spend more time planning, reviewing, and explaining intent. Reviews become the bottleneck. Human++ helps by making human judgment visible at a glance.

## What's in the box

- A **Base16 theme** tuned for long sessions: warm charcoals, coffee comments, paper/cream foregrounds, bright expressive accents
- A **zero-ceremony convention** for marking human intent inside comments
- A dedicated `base0F` highlighter color for those markers

## The palette

| Slot | Hex | Role |
|------|-----|------|
| base00 | `#1c1917` | Background (warm charcoal) |
| base01 | `#262321` | Elevated background |
| base02 | `#353230` | Selection |
| base03 | `#8a7b6b` | Comments (coffee with milk) |
| base04 | `#8a8279` | Secondary text |
| base05 | `#c4bbb2` | Main text (warm, not white) |
| base06 | `#ddd5cc` | Emphasis |
| base07 | `#f2ebe4` | Highlights (warm near-white) |
| base08 | `#d9048e` | Red (hot pink) |
| base09 | `#f26c33` | Orange |
| base0A | `#f2a633` | Yellow (amber) |
| base0B | `#04b372` | Green (teal) |
| base0C | `#1ad0d6` | Cyan |
| base0D | `#317ad6` | Blue |
| base0E | `#8d57ff` | Magenta (purple) |
| base0F | `#bbff00` | Highlighter (human attention) |

## The Human++ convention

Use punctuation markers inside comments. No keywords required.

### Markers

- `!!` - Human intervention. "Pay attention here."
- `??` - Uncertainty. "I'm not confident. Please check."
- `///` - Strong comment. Doc-level explanation. (optional)

### Examples

```js
// !! Intentionally weird because legacy billing contracts depend on it.
// ?? Not fully confident about this edge case.
// Normal comments stay calm and readable.

/// Rationale:
/// We keep this in-process because externalizing adds 200ms tail latency.
```

### Why punctuation?

Friction kills adoption. These markers are:

- Fast to type
- Easy to scan
- Easy to grep (`rg "// !!|// \?\?"`)
- Easy for editors to highlight

## Philosophy

Human++ treats judgment as the scarce resource.

- Code can be generated. Intent cannot.
- Uncertainty is a gift to reviewers.
- We highlight interventions, not everything.
- We optimize for reviewer throughput.

## Editor support

Human++ works with standard Base16 tooling. To highlight `!!` and `??` markers, configure your editor to match these patterns and color them with `base0F`.

**Patterns:**
- `//\s*!!.*$`
- `//\s*\?\?.*$`
- `^\s*///.*$` (optional)

**VS Code:** Use a TODO highlighter extension. Add patterns for `!!` and `??`.

**JetBrains:** Settings > Editor > TODO. Add patterns, map to a strong highlight.

**Vim/Neovim:** Match these patterns and link them to a highlight group using `base0F`.

**Terminal:** Even without highlighting, the convention works. Grep for markers during review.

## Team norms (optional)

- Prefer `!!` over long "please read" comments
- Use `??` when uncertain, not just when broken
- Keep markers rare. If everything is highlighted, nothing is.

## Install

Individual configs for various tools are in their respective directories:

- `ghostty/` - Ghostty terminal
- `vim/` - Vim/Neovim colorscheme
- `iterm/` - iTerm2
- `sketchybar/` - Sketchybar colors
- `skhd/` - skhd mode colors
- `borders/` - JankyBorders

## License

MIT
