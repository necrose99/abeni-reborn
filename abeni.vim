" -*- vim -*-
" FILE: abeni.vim
" LAST MODIFICATION: 2004/08/06 19:00
" (C) Copyright 2004 Rob Cakebread <pythonhead@gentoo.org>
" Version: 0.1

" USAGE:
"
" Put this file in /usr/share/vim/vimfiles/plugin/
"
" REQUIREMENTS:
" abeni (>=0.0.19)
"
" Shortcuts:
"   F1 - digest
"   F2 - unpack
"   F3 - compile
"   F4 - install
"   F5 - qmerge


autocmd BufRead *.ebuild nmap <F1> :!/usr/bin/abeni_ctrl digest*%<cr>
autocmd BufRead *.ebuild nmap <F2> :!/usr/bin/abeni_ctrl unpack*%<cr>
autocmd BufRead *.ebuild nmap <F3> :!/usr/bin/abeni_ctrl compile*%<cr>
autocmd BufRead *.ebuild nmap <F4> :!/usr/bin/abeni_ctrl install*%<cr>
autocmd BufRead *.ebuild nmap <F5> :!/usr/bin/abeni_ctrl qmerge*%<cr>

" Menu entries
vmenu <silent> &Abeni.digest
    \:call Ebuild("digest")<CR>

vmenu <silent> &Abeni.unpack
    \:call Ebuild("unpack")<CR>

vmenu <silent> &Abeni.compile
    \:call Ebuild("compile")<CR>

vmenu <silent> &Abeni.install
    \:call Ebuild("install")<CR>

vmenu <silent> &Abeni.qmerge
    \:call Ebuild("qmerge")<CR>


function! Ebuild(cmd)
  execute '!/usr/bin/abeni_ctrl digest*%<cr>'
endfunction

