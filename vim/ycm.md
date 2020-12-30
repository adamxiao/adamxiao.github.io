# vim plugin youcompleteme usage

TODO: 他的语法检测，会有很多无用的告警，怎么去除？

目前使用ycm插件，用来自动补全。
它是基于clang编译器识别自动补全的，速度快，但是需要配置(略复杂)。

配置文件 .ycm_extra_conf.py

```
let g:ycm_show_diagnostics_ui = 0
" disable syntax check
let g:ycm_confirm_extra_conf = 0
" disable ycm conf loaded confirm
```
