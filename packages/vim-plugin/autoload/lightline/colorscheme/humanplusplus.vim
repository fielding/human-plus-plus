" Lightline theme — Human++ Base24
" Generated from palette.toml — DO NOT EDIT
" Rebuild: make build
"
" Mode color mapping:
"   normal=blue, insert=green, visual=purple, replace=red, tabsel=lime

let s:base00  = [ '#1a1c22', 0  ]
let s:base01  = [ '#282b31', 8  ]
let s:base02  = [ '#3a3d42', 8  ]
let s:base03  = [ '#5a5d62', 8  ]
let s:base04  = [ '#828079', 7  ]
let s:base05  = [ '#dbd6cc', 15 ]
let s:base06  = [ '#eeeae2', 15 ]
let s:base07  = [ '#f8f6f2', 15 ]

let s:red     = [ '#e7349c', 1  ]
let s:orange  = [ '#f26c33', 9  ]
let s:amber   = [ '#f2a633', 3  ]
let s:green   = [ '#04b372', 2  ]
let s:cyan    = [ '#1ad0d6', 6  ]
let s:blue    = [ '#458ae2', 4  ]
let s:purple  = [ '#9871fe', 5  ]
let s:lime    = [ '#bbff00', 10 ]

let s:p = {'normal': {}, 'inactive': {}, 'insert': {}, 'replace': {}, 'visual': {}, 'tabline': {}}

let s:p.normal.left    = [ [ s:base00, s:blue   ], [ s:base06, s:base02 ] ]
let s:p.normal.right   = [ [ s:base00, s:base04 ], [ s:base05, s:base02 ] ]
let s:p.normal.middle  = [ [ s:base04, s:base01 ] ]
let s:p.normal.error   = [ [ s:base07, s:red    ] ]
let s:p.normal.warning = [ [ s:base00, s:amber  ] ]

let s:p.insert.left    = [ [ s:base00, s:green  ], [ s:base06, s:base02 ] ]
let s:p.insert.right   = copy(s:p.normal.right)
let s:p.insert.middle  = copy(s:p.normal.middle)

let s:p.replace.left   = [ [ s:base00, s:red    ], [ s:base06, s:base02 ] ]
let s:p.replace.right  = copy(s:p.normal.right)
let s:p.replace.middle = copy(s:p.normal.middle)

let s:p.visual.left    = [ [ s:base00, s:purple ], [ s:base06, s:base02 ] ]
let s:p.visual.right   = copy(s:p.normal.right)
let s:p.visual.middle  = copy(s:p.normal.middle)

let s:p.inactive.left   = [ [ s:base04, s:base01 ], [ s:base03, s:base01 ] ]
let s:p.inactive.right  = [ [ s:base04, s:base01 ], [ s:base03, s:base01 ] ]
let s:p.inactive.middle = [ [ s:base03, s:base01 ] ]

let s:p.tabline.left    = [ [ s:base05, s:base02 ] ]
let s:p.tabline.tabsel  = [ [ s:base00, s:lime   ] ]
let s:p.tabline.middle  = [ [ s:base03, s:base00 ] ]
let s:p.tabline.right   = [ [ s:base05, s:base02 ] ]

let g:lightline#colorscheme#humanplusplus#palette = lightline#colorscheme#flatten(s:p)
