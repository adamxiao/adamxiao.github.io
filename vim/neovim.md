# neovim入门使用

#### neovim

Using Neovim as a Markdown Editor
https://www.youtube.com/watch?v=cWiTg-ItdwA&t=1083s&ab_channel=TimothyUnkert

https://www.youtube.com/watch?v=x__SZUuLOxw&ab_channel=DevOpsToolbox
=> 尝试

[Neovim 使用体验](https://luyuhuang.tech/2023/03/21/nvim.html)
像个 IDE 一样: LSP 和补全

[neovim 安装配置](https://blog.csdn.net/aiyolo/article/details/128567132)
最终留下了目前在 github 中 star 排名第一的 LunarVim

[Vim 和 Neovim 的前世今生](https://jdhao.github.io/2020/01/12/vim_nvim_history_development/)

关键字《nvim 安装插件》

[lazy-nvim插件管理器基础入门](https://www.cnblogs.com/w4ngzhen/p/17493128.html)

[Neovim插件推荐&配置](https://www.bilibili.com/read/cv22495061/)

https://github.com/ADkun/lvim-config-suggest
todo-comments.nvim
高亮注释中的关键词，按需安装。

symbols-outline.nvim
简介：以右侧栏形式显示当前文件的大纲、标题、符号

[叛逃至 Neovim](https://www.ddupan.top/posts/move-to-neovim/)
Telescope 著名的搜索插件
nvim-tree.lua 一个完全使用 Lua 编写的文件管理器插件
nvim-treesitter 代码高亮，替代 Vim 自带的正则式高亮
Gitsigns Git 集成
整套补全系统没有使用 coc.nvim 而是使用了自带的 LSP，使用了一些插件作为进行代码补全和 Snippet 管理

[如何评价 Vim9？](https://www.zhihu.com/question/364528657/answers/updated)

我目前是一套通用vim脚本，同时支持neovim和vim。但平时我基本只用neovim，偶尔切回vim9，确实似乎是变快了一些，但也懒得新学vim9的语法重写自己的配置。一直用neovim的原因主要是nvim-tree.lua和barbar.nvim这俩插件，让ui的颜值提高了一大截，纯vim插件目前还没有。之前看到有答主说很多runtime scripts会用9重写，而且社区也有很多插件会跟进吧。我这种普通用户直接安装使用就好了。

https://www.v2ex.com/t/938771
做了两期 Neovim 从零配置的教学视频(lazy.nvim + 100% lua)

#### 配置入门

$HOME/.config/nvim/init.lua
或者 $HOME/.config/nvim/init.vim (注意: 两者不能共存, 只能二选一)

init.lua 配置入门

#### lazy插件管理使用入门

lazy.nvim
如下配置可以放到init.lua配置中，也可以require包含
```
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not (vim.uv or vim.loop).fs_stat(lazypath) then
  vim.fn.system({
    "git",
    "clone",
    "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    "--branch=stable", -- latest stable release
    lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)

require("lazy").setup(plugins, opts)
```

例如配置安装使用nvim-tree插件
```
return {
  "nvim-tree/nvim-tree.lua",
  version = "*",
  lazy = false,
  dependencies = {
    "nvim-tree/nvim-web-devicons",
  },
  config = function()
    require("nvim-tree").setup {}
  end,
}
```

配置快捷键
```
vim.keymap.set('n', '<leader>sf', require('telescope.builtin').find_files, { desc = '[S]earch [F]iles' })
vim.api.nvim_command('nmap <F3> :NvimTreeToggle<CR>')
```

#### 字体安装

关键字《gnome-terminal install Nerd Font》

https://docs.rockylinux.org/books/nvchad/nerd_fonts/#:~:text=If%20you%20are%20using%20the,Nerd%20Font%20for%20your%20profile.

[记录LazyVim安装使用过程中解决的一些问题](https://zhuanlan.zhihu.com/p/671439100)
```
https://www.nerdfonts.com/font-downloads
unzip Unbuntu.zip
mv *.ttf /usr/local/share/fonts/
fc-list
fc-cache -fv
```

#### 杂项

https://wsdjeg.net/

Vim Script 中调用 Lua
Lua 中调用 Vim Script 函数

关键字《init.lua source vimrc》
https://www.reddit.com/r/neovim/comments/mkmbl0/initlua_beginner_can_i_source_a_vim_file_from/
```
vim.cmd('source ' .. nvimrc .. '/lua/config/goyo.vim')```
The vim file is under nvim/lua/config
```

[从 init.vim 到 init.lua - 速成课程](https://www-notonlycode-org.translate.goog/neovim-lua-config/?_x_tr_sl=en&_x_tr_tl=zh-CN&_x_tr_hl=zh-CN&_x_tr_pto=sc)
```
vim.cmd([[
set notimeout
set encoding=utf-8
]])
```

## 尝试别人的配置组合

#### Lazyvim

优点:

- 命令行在中间
- 快捷键提示
  例如`<leader>sf`为文件名搜索, 敲出`<leader>`键就会提示
  但是这个搜索插件性能不如fzf(大量文件下不如)...
- snip补全提示不错
- 浮动补全窗口挺不错

缺点:

- 命令行没有补全?

#### omerxx

youtube上看到的

https://www.youtube.com/watch?v=x__SZUuLOxw&ab_channel=DevOpsToolbox

- 命令行在中间
- 命令行有列表补全
  => nvim默认版本自带的... 按tab键触发
- 普通搜索会展示搜索到了多少个结果
- markdown会隐藏链接地址等信息 => 算优点还是缺点呢?
  代码块也会隐藏
  缺点居然还会隐藏图片markdown

## 优秀插件

- Telescope
  搜索插件
  fzf-native 集成更快? 大项目
- Gitsigns
  Git 集成

- nvim-tree.lua
  一个完全使用 Lua 编写的文件管理器插件
- nvim-treesitter
  代码高亮，替代 Vim 自带的正则式高亮

https://www.makeuseof.com/customize-neovim-for-development-on-linux/
- NERDTree:
  Easy and resourceful file system explorer for Neovim. NERDTree allows you to integrate a directory tree explorer into your Neovim setup which functions similarly to the file manager sidebar in GUI-based code editors like Visual Studio Code, Sublime Text, etc.
- Telescope:
  Customization fuzzy finder for Neovim that helps you quickly search and navigate through files, tags, buffers, symbols, and other parts of your project.
- mason.nvim:
  Package manager for Neovim that you can use to install and manage LSP servers, DAP servers, linters, and formatters.
  关键命令 `:Mason`

https://medium.com/@shaikzahid0713/file-explorer-for-neovim-c324d2c53657
Nvim-Tree Alternatives
- ChadTree
- Neo-Tree
- Tree
- NerdTree
- Defx

#### 文件夹管理

#### snip代码块

L3MON4D3/LuaSnip
=> 配合参考代码块使用 rafamadriz/friendly-snippets

#### git版本管理

#### 配色

#### 搜索显示匹配个数

关键字《neovim展示搜索总数插件》

如下命令虽然可以，但是不方便
```
%s/xxx//gn
```

https://yyq123.github.io/learn-vim/learn-vi-106-plugin-searchindex.html
自8.1.1270版本开始，Vim已经内置对搜索结果的计数显示，而不再需要安装额外的插件。
搜索结果计数器(searchindex)

https://github.com/dyng/ctrlsf.vim/issues/249
安装 airline 插件以后，可以显示当前文件名和当前位于第几个匹配处。

https://jdhao.github.io/nvim-config/
Show search index and count with nvim-hlslens. => 这个插件可以.

nvim使用这个插件 `folke/noice.nvim`, 是一个UI插件

#### LSP研究

关键字《vim 支持LSP》

https://www.kawabangga.com/posts/3745

https://breezetemple.github.io/2019/12/25/vim-lsp/
coc.nvim 选择 ccls 作为 C LSP

探索 Vim LSP：提升你的代码编辑体验
https://blog.csdn.net/gitblog_00045/article/details/136931491
vim-lsp  https://github.com/prabirshrestha/vim-lsp

从零开始配置vim(23)——lsp基础配置
https://blog.csdn.net/lanuage/article/details/126738380

[(好)Vim LSP 配置](https://www.kawabangga.com/posts/3745)
首先需要安装 Python 的 Language Server。推荐使用 pipx 安装。
```
pipx install python-language-server
```

http://liwuzhi.art/?p=592
现在比较火的lsp插件是neoclide/coc.nvim和dense-analysis/ale。他们安装在vim中，属于lsp协议中的client。通过和lsp server通讯，带来强大的语法功能

#### 图片查看

https://www.youtube.com/watch?v=0O3kqGwNzTI&ab_channel=linkarzu

[View and paste images in neovim](https://linkarzu.com/posts/neovim/images-neovim/)

https://superuser.com/questions/104599/how-can-i-launch-the-gnome-image-viewer-from-the-terminal
```
eog filename
xdg-open filename # 比较合适
gnome-open filename # 没有命令
```

## FAQ

#### 如何在init.lua中嵌入 vim脚本配置

https://github.com/glepnir/nvim-lua-guide-zh
```
vim.api.nvim_command('set nonumber')
```

#### lazy.nvim混用非lua插件

貌似没找到资料...

关键字《lazy.nvim use nerdtree》
[bug: Vim:Lua module not found for config of nerdtree. Please use a config() function instead](https://github.com/folke/lazy.nvim/discussions/1460)
```
return {
  {
    "preservim/nerdtree",
    lazy = true,
    keys = { { "<leader>n", "<cmd>NERDTreeToggle<cr>", desc = "Toggle NERDTree." } },
    cmd = { "NERDTree" },
    opts = { },
  }
}
```
