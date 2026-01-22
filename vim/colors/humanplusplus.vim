" Human++ - Warm humane grayscale for the post-artisanal coding era
" Author: fielding

set background=dark
hi clear
if exists("syntax_on")
    syntax reset
endif
let g:colors_name = "humanplusplus"

" Base16 palette
let s:base00 = "#1c1917"
let s:base01 = "#262321"
let s:base02 = "#353230"
let s:base03 = "#8a7b6b"
let s:base04 = "#8a8279"
let s:base05 = "#c4bbb2"
let s:base06 = "#ddd5cc"
let s:base07 = "#f2ebe4"
let s:base08 = "#d9048e"
let s:base09 = "#f26c33"
let s:base0A = "#f2a633"
let s:base0B = "#04b372"
let s:base0C = "#1ad0d6"
let s:base0D = "#317ad6"
let s:base0E = "#8d57ff"
let s:base0F = "#bbff00"

" Base
exe "hi Normal guifg=".s:base05." guibg=".s:base00
exe "hi NonText guifg=".s:base03." guibg=NONE"
exe "hi LineNr guifg=".s:base03." guibg=".s:base00
exe "hi CursorLine guibg=".s:base01." cterm=NONE"
exe "hi CursorLineNr guifg=".s:base05." guibg=".s:base01
exe "hi Visual guibg=".s:base02
exe "hi Search guifg=".s:base00." guibg=".s:base0A
exe "hi IncSearch guifg=".s:base00." guibg=".s:base09

" Syntax
exe "hi Comment guifg=".s:base03." gui=italic"
exe "hi String guifg=".s:base0B
exe "hi Number guifg=".s:base09
exe "hi Boolean guifg=".s:base09
exe "hi Float guifg=".s:base09
exe "hi Constant guifg=".s:base09
exe "hi Character guifg=".s:base08
exe "hi Identifier guifg=".s:base08
exe "hi Function guifg=".s:base0D
exe "hi Statement guifg=".s:base0E
exe "hi Conditional guifg=".s:base0E
exe "hi Repeat guifg=".s:base0E
exe "hi Label guifg=".s:base0A
exe "hi Operator guifg=".s:base05
exe "hi Keyword guifg=".s:base0E
exe "hi Exception guifg=".s:base08
exe "hi Type guifg=".s:base0A
exe "hi StorageClass guifg=".s:base0A
exe "hi Structure guifg=".s:base0E
exe "hi Typedef guifg=".s:base0A
exe "hi PreProc guifg=".s:base0A
exe "hi Include guifg=".s:base0D
exe "hi Define guifg=".s:base0E
exe "hi Macro guifg=".s:base08
exe "hi PreCondit guifg=".s:base0A
exe "hi Special guifg=".s:base0C
exe "hi SpecialChar guifg=".s:base0F
exe "hi Tag guifg=".s:base0A
exe "hi Delimiter guifg=".s:base05
exe "hi SpecialComment guifg=".s:base0C
exe "hi Debug guifg=".s:base08
exe "hi Underlined guifg=".s:base0D." gui=underline"
exe "hi Error guifg=".s:base00." guibg=".s:base08
exe "hi Todo guifg=".s:base0A." guibg=".s:base01." gui=bold"

" Human++ markers (!! and ??)
exe "hi HumanAttention guifg=".s:base00." guibg=".s:base0F." gui=bold"
exe "hi HumanUncertain guifg=".s:base00." guibg=".s:base0F." gui=bold"

" UI
exe "hi StatusLine guifg=".s:base04." guibg=".s:base01." gui=NONE"
exe "hi StatusLineNC guifg=".s:base03." guibg=".s:base01." gui=NONE"
exe "hi VertSplit guifg=".s:base02." guibg=".s:base00
exe "hi Pmenu guifg=".s:base05." guibg=".s:base01
exe "hi PmenuSel guifg=".s:base00." guibg=".s:base0D
exe "hi PmenuSbar guibg=".s:base02
exe "hi PmenuThumb guibg=".s:base07
exe "hi TabLine guifg=".s:base03." guibg=".s:base01
exe "hi TabLineSel guifg=".s:base07." guibg=".s:base00
exe "hi TabLineFill guibg=".s:base01
exe "hi ColorColumn guibg=".s:base01
exe "hi SignColumn guibg=".s:base00
exe "hi FoldColumn guifg=".s:base0C." guibg=".s:base00
exe "hi Folded guifg=".s:base03." guibg=".s:base01

" Cursor
exe "hi Cursor guifg=".s:base00." guibg=".s:base05
exe "hi CursorColumn guibg=".s:base01
exe "hi MatchParen guifg=".s:base05." guibg=".s:base03

" Git/Diff
exe "hi DiffAdd guifg=".s:base0B." guibg=".s:base01
exe "hi DiffDelete guifg=".s:base08." guibg=".s:base01
exe "hi DiffChange guifg=".s:base0A." guibg=".s:base01
exe "hi DiffText guifg=".s:base0D." guibg=".s:base01." gui=bold"
exe "hi GitGutterAdd guifg=".s:base0B." guibg=".s:base00
exe "hi GitGutterChange guifg=".s:base0A." guibg=".s:base00
exe "hi GitGutterDelete guifg=".s:base08." guibg=".s:base00

" Spelling
exe "hi SpellBad guisp=".s:base08." gui=undercurl"
exe "hi SpellCap guisp=".s:base0D." gui=undercurl"
exe "hi SpellLocal guisp=".s:base0C." gui=undercurl"
exe "hi SpellRare guisp=".s:base0E." gui=undercurl"

" Neovim diagnostics
exe "hi DiagnosticError guifg=".s:base08
exe "hi DiagnosticWarn guifg=".s:base0A
exe "hi DiagnosticInfo guifg=".s:base0D
exe "hi DiagnosticHint guifg=".s:base0C

" Match Human++ markers in comments
" Add to your config: match HumanAttention /\/\/\s*!!/
" Add to your config: match HumanUncertain /\/\/\s*??/
