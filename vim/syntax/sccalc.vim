if exists('b:current_syntax')
  finish
endif

syn match sccalccommand "\v^\s*![A-Za-z_][A-Za-z0-9_]*"
syn match sccalcnumber  "\v<\d+>"
syn match sccalccomment "\v^\s*#.*$"
syn region sccalcstr matchgroup=bqnstr start=/"/ end=/"/ contains=bqnquo

hi link sccalccommand type
hi link sccalcnumber number
hi link sccalccomment string
hi link sccalcstr string

let b:current_syntax='sccalc'
