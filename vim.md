# vim usage

## vim configure
详细配置存储在[github](https://github.com/adamxiao/ubuntu_10.04_etc)上
```vim
" 扩展*, 选中文本搜索
vnoremap <silent> * y/<C-R>=substitute(escape(@", '^$~.*\\/[]'), "\n", '\\n', 'g')<CR><CR>
set hls " 高亮搜索关键字
set laststatus=2 " 显示状态栏

" TODO: 其他配置以及插件配置
" set plugin on
filetype plugin on
filetype plugin indent on

```

## vim 杀手锏
- 1. 多模式
- 2. 可视化操作, eg. `ctrl-v`列选择修改

## vim之道
基本概念：
1. 三种模式:  insert, normal, extern
只有在insert模式下才能输入文字
```sequence
Normal->Insert: i, a, o ...
Insert->Normal: Esc or Ctrl-c
Normal->Extern: Q
Extern->Normal: visual
```

### 窗口面板操作
1. split + vsplit 分割面板

2. ctrl-w + 面板窗口命令字
ctrl-w + h(jkl) => 切换光标到上下左右面板窗口
ctrl-w + H(JKL) => 移动面板窗口位置
ctrl-w + +(-<>) => 调整面板大小
ctrl-w + q => 关闭当前面板

3. tabnew + gt 创建和切换tab

### 光标移动
神龙见首不见尾
1. hjkl 上下左右
2. ctrl + f(b du ye) 翻页移动(一页,半页,一行)
3. w b e (W B E) 单词移动
4. 0 $ ^ 行头行尾移动
5. f(t) + 字符 ; , 查找字符移动
6. [[ { 段落移动
7. gg G 全文收尾移动
8. 指定行号移动
9. % 括号匹配移动
10. /xxx * # gd n N 查找关键字移动
11. ' + .  ' + ,  ' + a 标识位置移动
12. ctrl + ]   ctrl + t 定义taglist跳转移动
13. ]c 文件diff段落移动
14. H M L 当前页上中下一种
15. zt zz zb 居上，居中，居下移动
16. ctrl-^ 最近编辑的两个文件切换

### 文本替换删除粘贴
1. d s c x y p
2. ctrl - a (ctrl - x) 数字加减
3. ves 选中替换输入
4. gU 转换为大写字母
5. = <> 缩进
6. o插入一行
7. J 合并多行
8. dd + p 快速移动行
9. ctrl-v操作多行，增删改
10. . redo
0. TODO: ...

### vim预定义变量
1. % 表示当前文件名(包括相对路径) %:p代表完整路径 %:p:h表示文件目录
2. ctrl-r 输出当前文件名(包括相对路径)

### 颜色高亮
1. 搜索命令字
2. highlight 语法规则（用的少）
3. mark.vim插件

### Quickfix list
1. copen 打开quickfix list窗口
1. make
2. vimgrep

## vim常用插件
- buddle 插件管理
- taglist 符号表(ctags)
- snipmate 自定义模板补全

### vim vs IDE
1. 符号快速定位
2. 自动补全
3. 文件符号搜索
4. 断点调试
5. jar包管理系统
老蒋：1. 符号快速定位 2. 断点调试 3. jar包管理 XXX: 没有缺点
hardy: 1. 符号快速定位 2. 自动补全 3.文件符号模糊搜索

## vim 编译安装
```
./configure --prefix=$ADAM_PREFIX \
            --with-features=huge \
            --enable-multibyte \
            --enable-pythoninterp=yes \
            --enable-rubyinterp=yes \
            --enable-luainterp=yes \
            --enable-cscope
```

## 我的vim待改进问题
1. 异步make,vimgrep? 
   使用vim 8.0, 安装async异步插件
2. c++自动非常慢
	是用快速的YouCompleteMe, 或者不用

## FAQ

### vim自动对一个文件做特别设置
```
Per-file settings can be done using "modeline magic".

The basic idea is that you can add a comment to an individual file like this:

/* vim: set tabstop=8:softtabstop=8:shiftwidth=8:noexpandtab */ 
Within vim, you should review:

:help auto-setting
:help modeline
:help modelines
```
