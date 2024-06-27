# vim markdown编写查看

## 获取markdown标题

#### 使用vim搜索功能

直接输入vim命令
```
ilist /^#

效果如下:
  1:    1 # vim markdown编写查看
  2:    3 ## 获取markdown标题
  3:    5 #### 使用vim搜索功能
```

#### 使用tagbar + 脚本解析tag

效果不错，就是安装依赖python

https://github.com/jszakmeister/markdown2ctags

```vim
" Add support for markdown files in tagbar.
let g:tagbar_type_markdown = {
    \ 'ctagstype': 'markdown',
    \ 'ctagsbin' : '/usr/bin/markdown2ctags.py',
    \ 'ctagsargs' : '-f - --sort=yes --sro=»',
    \ 'kinds' : [
        \ 's:sections',
        \ 'i:images'
    \ ],
    \ 'sro' : '»',
    \ 'kind2scope' : {
        \ 's' : 'section',
    \ },
    \ 'sort': 0,
\ }
```

#### 使用tagbar + Universal Ctags配置解析tag

安装简单, 内置就有markdown tag识别,
但是tag效果一般般, 没有分层标题效果

## 其他文档

https://www.youtube.com/watch?v=zbguTldYkCw&ab_channel=DaveSnider
=> 未验证

- plasticboy/vim-markdown
  语法高亮
- junegunn/goyo.vim
  markdown纯净模式
- reedes/vim-pencil
  自动换行?


## 参考文档

* https://github-wiki-see.page/m/preservim/tagbar/wiki
