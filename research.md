# Research: Vim Plugin with VS Code Extension Parity

Status: ACCEPTED  <!-- DRAFT | IN_REVIEW | ACCEPTED -->
Owner: agent
Last updated: 2026-02-25

Task statement:
- the goal is to create a vim plugin with parity to the vs code plugin in this project

---

## TL;DR (5-10 bullets)
- The VS Code extension implements **4 features**: (1) color theme, (2) human intent marker highlighting (`!!`/`??`/`>>`), (3) inline diagnostic badges, (4) markdown H1 full-line highlighting
- A basic tinty-generated Vim colorscheme already exists (`generate_tinty_themes` in build.py) but only handles base color slots — none of the 4 runtime features are ported
- The Vim plugin must target **Neovim** (0.9+) to get virtual text for diagnostic badges and the `nvim_buf_set_extmark` API — classic Vim lacks equivalent features
- All 24 palette colors are defined in `palette.toml` and flow through `tools/build.py`; the Vim plugin should follow this same pipeline (a new generator function) for the colorscheme portion
- The marker scanner logic (10 comment patterns, keyword aliases with priority, explicit `!!`/`??`/`>>` detection) must be faithfully reimplemented in Lua
- The diagnostic badge feature maps naturally to Neovim's `vim.diagnostic` API + virtual text
- The markdown H1 highlight maps to either Treesitter highlights or `matchadd()`/`nvim_buf_add_highlight`
- The plugin should be structured as a standard Neovim Lua plugin (`lua/human-plus-plus/`)
- All hardcoded colors in extension.ts use palette slots — the Vim plugin should do the same for consistency

---

## System overview

Human++ is a Base24 color scheme with 24 palette slots in 3 tiers: grayscale (base00-07), loud accents (base08-0F) for diagnostics/signals, and quiet accents (base10-17) for syntax. The design philosophy: "Code is cheap. Intent is scarce." — AI-generated comments (base03) fade into the background while human intent markers (`!!`, `??`, `>>`) use the loudest colors.

The VS Code extension (`packages/vscode-extension/`) is a single-file TypeScript implementation (687 lines) that activates on startup and provides the theme JSON + 3 runtime features via the VS Code decoration API.

The build pipeline (`tools/build.py`, 2031 lines) reads `palette.toml`, and generates configs for 22+ tools. A `generate_tinty_themes()` function already produces a basic Vim colorscheme via the tinted-vim mustache template, but this only maps base16/24 slots to basic Vim highlight groups — it does not implement markers, diagnostics, or H1 highlighting.

>> Evidence:
- >> packages/vscode-extension/src/extension.ts:L1-L687 — entire VS Code extension (single file)
- >> packages/vscode-extension/package.json:L1-L123 — extension manifest (commands, settings, activation)
- >> tools/build.py:L1883-L1951 — existing tinty Vim colorscheme generator (basic, no markers)
- >> palette.toml:L1-L37 — all 24 color slots, the single source of truth
- >> tools/build.py:L1954-L1985 — VS Code theme generator (template-based)

---

## Entry points

### VS Code extension entry points
- `activate()` — extension activation, registers commands and event listeners — >> packages/vscode-extension/src/extension.ts:L632-L681
- `human-plus-plus.toggle` command — toggles all highlighting on/off — >> packages/vscode-extension/src/extension.ts:L636-L638
- `human-plus-plus.refresh` command — forces re-decoration of current editor — >> packages/vscode-extension/src/extension.ts:L641-L644

### Build pipeline entry points
- `make build` → `python3 tools/build.py` → `main()` — >> tools/build.py:L1992
- `make apply` → `scripts/apply.sh` — applies theme to installed apps including Vim/Neovim — >> scripts/apply.sh:L83-L97

### Event-driven triggers (VS Code, must be replicated in Vim)
- `onDidChangeActiveTextEditor` → full update (markers + diagnostics + H1) — >> packages/vscode-extension/src/extension.ts:L647-L651
- `onDidChangeTextDocument` → debounced marker-only update — >> packages/vscode-extension/src/extension.ts:L653-L660
- `onDidChangeConfiguration` → recreate decoration types, full update — >> packages/vscode-extension/src/extension.ts:L662-L668
- `onDidChangeDiagnostics` → debounced diagnostic-only update — >> packages/vscode-extension/src/extension.ts:L671-L677

---

## Data model / schemas

### Palette (24 slots)
| Tier | Slots | Purpose |
|------|-------|---------|
| Grayscale | base00-base07 | Backgrounds (00-02), comments (03), UI secondary (04), text (05-07) |
| Loud accents | base08-base0F | Diagnostics, signals, human intent markers |
| Quiet accents | base10-base17 | Syntax highlighting, less urgent UI state |

>> Evidence:
- >> palette.toml:L6-L25 — base16 slots (grayscale + loud accents)
- >> palette.toml:L27-L37 — base24 slots (quiet accents)

### Marker definitions
| Type | Symbol | Background | Foreground | Keywords (aliases) | Priority |
|------|--------|------------|------------|-------------------|----------|
| intervention | `!!` | `#bbff00` (base0F) | `#1a1c22` (base00) | FIXME, BUG, XXX | 1 (strongest) |
| uncertainty | `??` | `#9871fe` (base0E) | `#f8f6f2` (base07) | TODO, HACK | 2 |
| directive | `>>` | `#1ad0d6` (base0C) | `#1a1c22` (base00) | NOTE, NB | 3 (weakest) |

>> Evidence:
- >> packages/vscode-extension/src/extension.ts:L13-L31 — MARKERS constant
- >> packages/vscode-extension/src/extension.ts:L36-L40 — MARKER_KEYWORDS constant
- >> packages/vscode-extension/src/extension.ts:L43-L47 — MARKER_PRIORITY constant

### Diagnostic badge colors
| Level | Background | Foreground | Palette |
|-------|------------|------------|---------|
| error | `#e7349c` | `#1a1c22` | base08 on base00 |
| warning | `#f26c33` | `#1a1c22` | base09 on base00 |
| info | `#1ad0d6` | `#1a1c22` | base0C on base00 |
| hint | `#5e84b6` | `#f8f6f2` | base15 on base07 |

>> Evidence:
- >> packages/vscode-extension/src/extension.ts:L57-L74 — DIAGNOSTIC_COLORS constant

### Comment patterns recognized (10 patterns)
```
///          doc comments
//           C-style
#            Python/Shell/Ruby
--           SQL/Lua/Haskell
;            Lisp/Assembly
/* or /**    block start
*            block continuation
<!--         HTML/XML
%            LaTeX/Prolog
rem          Basic/Batch (case-insensitive)
```

>> Evidence:
- >> packages/vscode-extension/src/extension.ts:L77-L88 — COMMENT_PATTERNS array

### Configuration settings (11 toggles)
| Key | Default | What it controls |
|-----|---------|-----------------|
| `enable` | true | Master on/off |
| `debounceMs` | 200 (50-1000) | Rescan delay on text edit |
| `markers.intervention.enable` | true | `!!` / FIXME/BUG/XXX marker |
| `markers.uncertainty.enable` | true | `??` / TODO/HACK marker |
| `markers.directive.enable` | true | `>>` / NOTE/NB marker |
| `diagnostics.enable` | true | Master diagnostic badge toggle |
| `diagnostics.error.enable` | true | Error badges |
| `diagnostics.warning.enable` | true | Warning badges |
| `diagnostics.info.enable` | true | Info badges |
| `diagnostics.hint.enable` | **false** | Hint badges (off by default) |
| `markdown.h1Highlight.enable` | true | H1 lime background |

>> Evidence:
- >> packages/vscode-extension/package.json:L50-L111 — configuration schema

---

## End-to-end flows

### Flow A: Marker scanning and decoration
1) Editor opens or text changes → event fires — >> packages/vscode-extension/src/extension.ts:L647-L660
2) Debounce timer (200ms default) fires → `updateMarkerDecorations()` — >> packages/vscode-extension/src/extension.ts:L552-L560
3) `MarkerScanner.scan()` iterates every line of the document — >> packages/vscode-extension/src/extension.ts:L146-L211
4) For each line, try all 10 `COMMENT_PATTERNS` in order; stop at first match — >> packages/vscode-extension/src/extension.ts:L169-L207
5) If comment found, check for explicit markers (`!!`, `??`, `>>`) via regex `^\s*(pattern)(?=\s|$)` — these always win — >> packages/vscode-extension/src/extension.ts:L179-L188
6) If no explicit marker, `findKeywordMatch()` does case-insensitive word-boundary search across all keyword aliases; lowest priority number wins — >> packages/vscode-extension/src/extension.ts:L218-L245
7) Match records: `{type, lineNum, startChar (from leading whitespace), endChar (trimmed end)}` — >> packages/vscode-extension/src/extension.ts:L196-L204
8) Matches grouped by type, applied as decorations with background color, bold, no-italic override, 0.9em font, border-radius — >> packages/vscode-extension/src/extension.ts:L492-L512

### Flow B: Diagnostic badge rendering
1) `onDidChangeDiagnostics` event fires (from LSP or built-in checkers) — >> packages/vscode-extension/src/extension.ts:L671-L677
2) Debounced → `updateDiagnostics()` called — >> packages/vscode-extension/src/extension.ts:L562-L570
3) Fetch diagnostics for current document URI via `vscode.languages.getDiagnostics(uri)` — >> packages/vscode-extension/src/extension.ts:L290
4) Group by line: one badge per line, highest severity wins (lower number = higher) — >> packages/vscode-extension/src/extension.ts:L293-L306
5) Check if severity level is individually enabled via config — >> packages/vscode-extension/src/extension.ts:L317-L320
6) Truncate message to 50 chars (47 + `...`) — >> packages/vscode-extension/src/extension.ts:L323-L325
7) Render as `after` pseudo-element: `contentText = "  ${msg}  "`, 3em left margin, border-radius, positioned at trimmed line end — >> packages/vscode-extension/src/extension.ts:L328-L341
8) Applied in batch per severity level — >> packages/vscode-extension/src/extension.ts:L347-L352

### Flow C: Markdown H1 highlighting
1) Editor opens or switches to a markdown file — >> packages/vscode-extension/src/extension.ts:L647-L651
2) `updateHeadings()` checks `languageId === 'markdown'`, clears if not — >> packages/vscode-extension/src/extension.ts:L412-L418
3) Scan for ATX H1: regex `/^#\s+.+$/` per line — >> packages/vscode-extension/src/extension.ts:L424-L433
4) Scan for setext H1: any non-empty line followed by `/^=+\s*$/` — both lines highlighted — >> packages/vscode-extension/src/extension.ts:L436-L445
5) Apply whole-line decoration: background `#bbff00` (base0F), color `#1a1c22` (base00), bold — >> packages/vscode-extension/src/extension.ts:L392-L399

### Flow D: Configuration change
1) `onDidChangeConfiguration` fires for `human-plus-plus.*` changes — >> packages/vscode-extension/src/extension.ts:L662-L668
2) Re-read `enable` flag, recreate decoration types (colors may change), full update — >> packages/vscode-extension/src/extension.ts:L593-L603

---

## Invariants / constraints (write as `!!`)

!! Marker detection MUST only occur inside comments — bare `!!` in code should NOT be highlighted. The 10 comment-pattern regexes are the gatekeeper.
!! Explicit markers (`!!`, `??`, `>>`) always override keyword aliases on the same line. A comment `// TODO !! fix this` should be intervention, not uncertainty.
!! Keyword matching is case-insensitive with word boundaries — `TODOBUG` should NOT match TODO or BUG.
!! Only ONE badge per line for diagnostics — highest severity wins (error > warning > info > hint).
!! Diagnostic messages truncated to 50 chars (47 + `...` if over).
!! Hints are disabled by default (the only setting that defaults to false).
!! Marker decoration covers from the start of the comment symbol (including leading whitespace) to the end of trimmed line text — not the whole line.
!! Markdown H1 highlighting is whole-line (`isWholeLine: true`) — this is different from marker highlighting.
!! The color theme uses quiet accents (base10-17) for syntax and loud accents (base08-0F) for diagnostics/markers — mixing these breaks the design philosophy.
!! base0F (lime) is RESERVED for human intent marker `!!` — it must not be used for general syntax highlighting.

>> Evidence:
- >> packages/vscode-extension/src/extension.ts:L169-L207 — comment-gated scanning
- >> packages/vscode-extension/src/extension.ts:L179-L188 — explicit markers override keywords
- >> packages/vscode-extension/src/extension.ts:L232 — word boundary regex for keywords
- >> packages/vscode-extension/src/extension.ts:L293-L306 — one badge per line, highest severity
- >> packages/vscode-extension/src/extension.ts:L323-L325 — 50-char truncation
- >> packages/vscode-extension/package.json:L100-L103 — hint defaults to false
- >> packages/vscode-extension/src/extension.ts:L196-L204 — marker range: startChar to trimmedEnd
- >> packages/vscode-extension/src/extension.ts:L396 — isWholeLine for H1
- >> palette.toml:L25 — base0F reserved for human intent

---

## Existing patterns to copy

### 1. Tinty Vim colorscheme generator
- >> tools/build.py:L1883-L1951 — `generate_tinty_themes()` renders a mustache template for Vim colors
  - Copy: The approach of generating a Vim colorscheme from palette.toml via build.py
  - Avoid: Depending on tinty being installed — the new plugin should include its own generator or ship pre-built colors

### 2. Bat/TextMate theme (scope-to-color mapping reference)
- >> tools/build.py:L436-L733 — `generate_bat()` maps TextMate scopes to palette colors
  - Copy: The scope-to-color mapping as a reference for Vim highlight group assignments
  - Avoid: Using XML/plist format — Vim uses `highlight` commands

### 3. VS Code tokenColors template (comprehensive scope mapping)
- >> templates/vscode/human-plus-plus.json.tmpl:L584-L2328 — ~180 TextMate scope rules
  - Copy: The semantic color assignments (which syntax elements get which palette slot)
  - Avoid: 1:1 scope translation — Vim/Treesitter has different group names; map by semantic intent

### 4. Shell init (256-color slot remapping)
- >> tools/build.py:L1054-L1076 — `generate_shell_init()` remaps 256-color slots 16-23 to palette slots
  - Copy: This pattern enables the Vim colorscheme to use `ctermfg=16` etc. for 256-color terminals where 16-23 are remapped
  - Avoid: Assuming GUI-only — should provide both `guifg` and `ctermfg` values

### 5. Apply script (Vim/Neovim deployment)
- >> scripts/apply.sh:L83-L97 — existing Vim/Neovim theme copy logic
  - Copy: The deployment paths (`~/.vim/colors/`, `~/.config/nvim/colors/`)
  - Avoid: Hard-dependency on tinty — new plugin should work standalone

---

## Footguns / risk areas

- **Comment pattern false positives**: The `*` pattern (line 84 in extension.ts) matches block comment continuations but could also match markdown list items or glob patterns. The VS Code extension breaks on first comment match, so the order matters. Vim implementation must preserve the same pattern order.
  >> packages/vscode-extension/src/extension.ts:L84

- **Performance on large files**: The VS Code extension scans every line on each update. For a Vim plugin, Treesitter queries or incremental matching may be needed for very large files. The debounce (200ms) helps but full-document scan could be costly.
  >> packages/vscode-extension/src/extension.ts:L165-L208

- **Neovim API version requirements**: Virtual text (`nvim_buf_set_extmark`) requires Neovim 0.5+; `vim.diagnostic` requires 0.6+; sign columns and highlight namespaces have varying support. Need to pick a minimum Neovim version.

- **Terminal vs GUI color fidelity**: VS Code always uses true color. Neovim in terminal may be limited to 256 colors unless `termguicolors` is set. The plugin should set/require `termguicolors` or provide 256-color fallbacks.

- **Treesitter vs regex for comment detection**: Using Treesitter to identify comment nodes would be more robust than regex patterns, but Treesitter may not be available for all filetypes. A hybrid approach (Treesitter where available, regex fallback) adds complexity.

- **Classic Vim incompatibility**: Classic Vim has no virtual text, no `vim.diagnostic`, no Lua runtime. Full feature parity requires Neovim. A degraded mode for Vim (colorscheme only) may be needed.

---

## Resolved decisions (formerly `??`)

1. **Target**: Neovim-only Lua plugin. Classic Vim degraded mode deferred to later.
2. **Minimum Neovim version**: 0.9+
3. **Colorscheme generation**: Generated by `tools/build.py` from `palette.toml` — single source of truth for all implementations.
4. **Comment detection**: Treesitter comment node queries (performant, well-supported in Neovim 0.9+, covers the majority of users). Regex fallback for filetypes without Treesitter parsers.

---

## Neovim feature mapping (VS Code → Neovim equivalents)

| VS Code Feature | Neovim Equivalent |
|---|---|
| `TextEditorDecorationType` (background highlight) | `nvim_buf_add_highlight()` or `nvim_buf_set_extmark()` with `hl_group` |
| `DecorationOptions.after.contentText` (virtual text) | `nvim_buf_set_extmark()` with `virt_text` parameter |
| `isWholeLine: true` decoration | Extmark with `end_col = 0, end_row = line+1` or `hl_eol = true` |
| `overviewRulerColor` | Sign column signs (`nvim_buf_set_extmark` with `sign_text`) |
| `vscode.languages.getDiagnostics()` | `vim.diagnostic.get(bufnr)` |
| `onDidChangeDiagnostics` event | `vim.diagnostic.handlers` or `LspDiagnosticsChanged` autocmd |
| `onDidChangeTextDocument` event | `TextChanged`/`TextChangedI` autocmds (or `nvim_buf_attach` for byte-level) |
| `onDidChangeActiveTextEditor` event | `BufEnter`/`BufWinEnter` autocmd |
| `workspace.getConfiguration()` | `vim.g.human_plus_plus_*` variables or `vim.fn` setup |
| Commands (`toggle`, `refresh`) | `:HumanPPToggle`, `:HumanPPRefresh` user commands |
| Debounce timer | `vim.defer_fn()` or `vim.loop.new_timer()` |

---

## Proposed plugin structure

```
packages/vim-plugin/
├── lua/
│   └── human-plus-plus/
│       ├── init.lua          -- setup(), config, autocommands, user commands
│       ├── markers.lua       -- comment detection, marker scanning, decoration
│       ├── diagnostics.lua   -- inline diagnostic badge virtual text
│       ├── headings.lua      -- markdown H1 full-line highlighting
│       ├── colors.lua        -- palette slot constants, highlight group definitions
│       └── config.lua        -- default configuration, user overrides
├── colors/
│   └── humanplusplus.lua     -- colorscheme (`:colorscheme humanplusplus`)
├── plugin/
│   └── human-plus-plus.lua   -- auto-load entry point
└── README.md
```

This follows the standard Neovim Lua plugin layout. The `colors/` directory allows `:colorscheme humanplusplus` to work. The `plugin/` directory auto-loads on startup (matching VS Code's `onStartupFinished`).

---

## Syntax highlight group mapping (VS Code TextMate scopes → Vim/Treesitter)

| Semantic Role | Palette Slot | Color | VS Code Scope | Vim Group | Treesitter Capture |
|---|---|---|---|---|---|
| Comments | base03 | `#5a5d62` | `comment` | `Comment` | `@comment` |
| Strings | base17 | `#d2fc91` | `string` | `String` | `@string` |
| Keywords | base10 | `#c8518f` | `keyword` | `Keyword`, `Statement` | `@keyword` |
| Storage type/modifier | base14 | `#91cbcd` | `storage.type`, `storage.modifier` | `StorageClass`, `Type` | `@keyword.storage` |
| Functions | base15 | `#5e84b6` | `entity.name.function` | `Function` | `@function` |
| Types/classes | base14 | `#91cbcd` | `entity.name.type` | `Type`, `Structure` | `@type` |
| Constants/numbers | base12 | `#dfb683` | `constant`, `constant.numeric` | `Constant`, `Number` | `@constant`, `@number` |
| Variables | base07 | `#f8f6f2` | `variable` | `Identifier` | `@variable` |
| Parameters | base16 | `#8f72e3` | `variable.parameter` | `@variable.parameter` link | `@variable.parameter` |
| Operators/punctuation | base04 | `#828079` | `keyword.operator` | `Operator` | `@operator` |
| HTML tags | base10 | `#c8518f` | `entity.name.tag` | `Tag` | `@tag` |
| Attributes | base14 | `#91cbcd` | `entity.other.attribute-name` | `@tag.attribute` link | `@tag.attribute` |
| CSS classes | base13 | `#61b186` | `entity.other.attribute-name.class.css` | custom | `@type.css` |
| Decorators | base11 | `#d68c6f` | `meta.decorator` | custom | `@attribute` |
| Markdown H1 | base0F on base00 | `#bbff00`/`#1a1c22` | `markup.heading.1` | `markdownH1` | `@markup.heading.1` |
| Markdown H2-H6 | base10 | `#c8518f` | `markup.heading` | `markdownH2`-`H6` | `@markup.heading.2`+ |
| Diff inserted | base13 | `#61b186` | `markup.inserted` | `DiffAdd` | `@diff.plus` |
| Diff deleted | base10 | `#c8518f` | `markup.deleted` | `DiffDelete` | `@diff.minus` |
| Errors (diagnostic) | base08 | `#e7349c` | N/A (decoration) | `DiagnosticError` | N/A |
| Warnings (diagnostic) | base09 | `#f26c33` | N/A (decoration) | `DiagnosticWarn` | N/A |
| Info (diagnostic) | base0C | `#1ad0d6` | N/A (decoration) | `DiagnosticInfo` | N/A |
| Hints (diagnostic) | base15 | `#5e84b6` | N/A (decoration) | `DiagnosticHint` | N/A |

>> Evidence:
- >> templates/vscode/human-plus-plus.json.tmpl:L584-L780 — tokenColor scope rules
- >> tools/build.py:L436-L733 — bat/TextMate theme (same mapping)

---

## Research checklist
- [x] Every major claim has at least one `>>` pointer.
- [x] Entry points identified and traced.
- [x] Invariants captured as `!!`.
- [x] Open questions captured as `??` (and minimized).
- [x] No hand-wavy "probably" statements without follow-up investigation.
