# neovim入门使用

#### neovim

Using Neovim as a Markdown Editor
https://www.youtube.com/watch?v=cWiTg-ItdwA&t=1083s&ab_channel=TimothyUnkert

https://www.youtube.com/watch?v=x__SZUuLOxw&ab_channel=DevOpsToolbox
=> 尝试

https://luyuhuang.tech/2023/03/21/nvim.html
https://blog.csdn.net/aiyolo/article/details/128567132
https://jdhao.github.io/2020/01/12/vim_nvim_history_development/

关键字《nvim 安装插件》

[lazy-nvim插件管理器基础入门](https://www.cnblogs.com/w4ngzhen/p/17493128.html)

[Neovim插件推荐&配置](https://www.bilibili.com/read/cv22495061/)

https://github.com/ADkun/lvim-config-suggest
todo-comments.nvim
高亮注释中的关键词，按需安装。

symbols-outline.nvim
简介：以右侧栏形式显示当前文件的大纲、标题、符号

https://www.ddupan.top/posts/move-to-neovim/
Telescope 著名的搜索插件
nvim-tree.lua 一个完全使用 Lua 编写的文件管理器插件
nvim-treesitter 代码高亮，替代 Vim 自带的正则式高亮
Gitsigns Git 集成

https://www.zhihu.com/question/364528657/answers/updated

我目前是一套通用vim脚本，同时支持neovim和vim。但平时我基本只用neovim，偶尔切回vim9，确实似乎是变快了一些，但也懒得新学vim9的语法重写自己的配置。一直用neovim的原因主要是nvim-tree.lua和barbar.nvim这俩插件，让ui的颜值提高了一大截，纯vim插件目前还没有。之前看到有答主说很多runtime scripts会用9重写，而且社区也有很多插件会跟进吧。我这种普通用户直接安装使用就好了。

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

## FAQ

#### 如何在init.lua中嵌入 vim脚本配置

https://github.com/glepnir/nvim-lua-guide-zh
```
vim.api.nvim_command('set nonumber')
```

#### lazy.nvim混用非lua插件

貌似没找到资料...
