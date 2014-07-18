set nu
set autoindent
set softtabstop=4
set tabstop=4
set modeline
set expandtab
set shiftwidth=4
set ruler
set colorcolumn=80

" handles cut-and-paste issue
nnoremap <F2> :set invpaste paste?<CR>
set pastetoggle=<F2>
set showmode

hi LineNr ctermfg=darkcyan ctermbg=black
filetype plugin indent on
syntax on
colorscheme blackboard
