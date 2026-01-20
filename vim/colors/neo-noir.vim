" Neo Noir - Cyberpunk Blade Runner aesthetic
" Author: fielding

set background=dark
hi clear
if exists("syntax_on")
    syntax reset
endif
let g:colors_name = "neo-noir"

" GUI colors
let s:bg = "#1f1f1f"
let s:bg_light = "#2b2b2b"
let s:fg = "#ededed"
let s:fg_dim = "#696969"
let s:red = "#d9048e"
let s:green = "#04b372"
let s:yellow = "#f26c33"
let s:blue = "#317ad6"
let s:magenta = "#8d57ff"
let s:cyan = "#1ad0d6"
let s:orange = "#f2a633"
let s:purple = "#8d57ff"

" Base
exe "hi Normal guifg=".s:fg." guibg=".s:bg
exe "hi NonText guifg=".s:fg_dim." guibg=NONE"
exe "hi LineNr guifg=".s:fg_dim." guibg=".s:bg
exe "hi CursorLine guibg=".s:bg_light." cterm=NONE"
exe "hi CursorLineNr guifg=".s:fg." guibg=".s:bg_light
exe "hi Visual guibg=".s:bg_light
exe "hi Search guifg=".s:bg." guibg=".s:yellow
exe "hi IncSearch guifg=".s:bg." guibg=".s:orange

" Syntax
exe "hi Comment guifg=".s:fg_dim." gui=italic"
exe "hi String guifg=".s:green
exe "hi Number guifg=".s:purple
exe "hi Constant guifg=".s:purple
exe "hi Identifier guifg=".s:cyan
exe "hi Function guifg=".s:blue
exe "hi Statement guifg=".s:red
exe "hi Keyword guifg=".s:red
exe "hi Type guifg=".s:cyan
exe "hi PreProc guifg=".s:red
exe "hi Special guifg=".s:orange
exe "hi Error guifg=".s:fg." guibg=".s:red
exe "hi Todo guifg=".s:bg." guibg=".s:yellow." gui=bold"

" UI
exe "hi StatusLine guifg=".s:fg." guibg=".s:bg_light." gui=NONE"
exe "hi StatusLineNC guifg=".s:fg_dim." guibg=".s:bg_light." gui=NONE"
exe "hi VertSplit guifg=".s:bg_light." guibg=".s:bg
exe "hi Pmenu guifg=".s:fg." guibg=".s:bg_light
exe "hi PmenuSel guifg=".s:bg." guibg=".s:red
exe "hi TabLine guifg=".s:fg_dim." guibg=".s:bg_light
exe "hi TabLineSel guifg=".s:fg." guibg=".s:bg
exe "hi TabLineFill guibg=".s:bg_light

" Git/Diff
exe "hi DiffAdd guifg=".s:green." guibg=NONE"
exe "hi DiffDelete guifg=".s:red." guibg=NONE"
exe "hi DiffChange guifg=".s:yellow." guibg=NONE"
exe "hi DiffText guifg=".s:orange." guibg=NONE gui=bold"
