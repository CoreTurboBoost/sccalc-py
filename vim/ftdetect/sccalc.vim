au BufRead,BufNewFile *.sccalc setf sccalc
au BufRead,BufNewFile * if getline(1) =~ '^#!.*sccalc\.py$' | setf sccalc | endif
