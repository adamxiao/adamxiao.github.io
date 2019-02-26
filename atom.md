# atom install
参考<https://atom.io>
支持三种平台：linux，mac，windows

# atom 特点
## 开源免费
基本框架是开源的，都是存储在github上，插件也可以及时更新
## 深度可定制系统
核心框架很小，基本功能都是都是插件化的，可以修改定制
## 界面是chrome html页面实现
界面ui的每一个像素都可以通过css，js来自定义控制
例如：
minimap, 代码缩略图
markdown-preview-enhanced, 实时编辑预览markdown文件
## 兼容VIM模式
就是vim-mode插件实现的
## 异步执行
vim+tmux才能实现的，在atom里异步是天然的
## atom杀手锏
- 文件目录树
- Ctrl-p 模糊文件查找
- 基于项目的查找替换（正则模式，文件模式）
- 多光标多选择编辑
- 多面板
- Snippets 代码片段
- 代码折叠
- 干净的配置UI界面, ctrl-shift-p
- 插件高度可扩展性
  代码格式化等
- 主题高度可配置性
- 实时预览markdown效果

# atom usage
参考atom官方手册<http://flight-manual.atom.io/>

## Keyboard Shortcuts
Only one key `ctrl-shift-p`, search `welcome` for Welcome Guide

- `ctrl-\`开关Tree File
- `F11` Full screen
- `ctrl-shift-i` chrome开发者工具
- `ctrl-k up` 分屏

## markdown使用
安装markdown-preview-enhanced插件
https://github.com/shd101wyy/markdown-preview-enhanced
`ctrl-m`打开markdown-preview
`ctrl-[`选中缩进
### TODO:
1. 插件语法高亮不行，包括protobuf
2. 扩展支持更好的flowcharts



## package installed
- `markdown-preview-enhanced` markdown实时预览，支持序列图
- `atom-beautify` 格式化代码，更统一的代码风格。
- `atom-terminal-panel` atom内置命令行工具
- `vim-mode-plus` 支持vim模式
- `remote-edit` 编辑服务器上的文件
- `minimap` 文件略缩图
