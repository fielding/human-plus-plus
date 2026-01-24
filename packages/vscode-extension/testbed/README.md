# Human++ Highlighter Test Workspace

Open this folder in the Extension Development Host (F5) to test Human++ marker highlighting.

## Markers

| Marker | Meaning |
|--------|---------|
| `!!` | **Intervention** - Human must pay attention |
| `??` | **Uncertainty** - Needs verification |
| `>>` | **Directive** - Decision / invariant / rationale |

## Test Files

| File | Language | Comment Style | Markers |
|------|----------|---------------|---------|
| `main.ts` | TypeScript | `//` | `!!` `??` `>>` |
| `app.py` | Python | `#` | `!!` `??` `>>` |
| `main.go` | Go | `//` | `!!` `??` `>>` |
| `main.rs` | Rust | `//` | `!!` `??` `>>` |
| `main.zig` | Zig | `//` | `!!` `??` `>>` |
| `lib.c` | C | `//` | `!!` `??` `>>` |
| `query.sql` | SQL | `--` | `!!` `??` `>>` |
| `script.sh` | Shell | `#` | `!!` `??` `>>` |

## What to Check

### Should highlight:
- `// !! comment text` → marker + rest of line
- `# ?? question` → marker + rest of line
- `-- >> directive` → marker + rest of line

### Should NOT highlight:
- `foo ?? bar` → nullish coalescing operator in code
- `#!/usr/bin/env bash` → shebang
- `// This !! is mid-comment` → marker not at start
- `"!! in a string"` → inside string literal

## Quick Test

1. Open `main.ts` - verify `??` operator in code is NOT highlighted
2. Open `app.py` - verify `#` comment markers work
3. Open `query.sql` - verify `--` comment markers work
4. Open `script.sh` - verify shebang is NOT highlighted
5. Scroll through each file - should see ~3 markers per file, well-spaced
