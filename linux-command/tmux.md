# tmux 配置使用

## 屏幕窗口创建

#### 创建屏幕

横向分屏幕
```
Ctrl-Q + -
```

竖向分屏幕
```
Ctrl-Q + |
```

先横向再竖向分屏的效果:

```
-------

-------
   |
-------
```

#### pane移动

Ctrl-Q + { 向上移动
Ctrl-Q + } 向下移动

#### 屏幕移动到其他窗口中

使用`join-pane`命令
可以Ctrl-Q + m标识一个pane, 然后到其他窗口中, 使用join-pane命令(Ctrl-Q + :)

[How to join two tmux windows into one, as panes?](https://stackoverflow.com/questions/9592969/how-to-join-two-tmux-windows-into-one-as-panes)

#### 创建窗口


```
Ctrl-Q + c
```

#### 选择窗口屏幕

切换到下一个窗口
```
Ctrl-Q + n
```

切换到第1号窗口
```
Ctrl-Q + 1
```

## 其他配置

#### 配置使用鼠标

临时开启配置
```
set -g mouse on
```

永久开启配置, 则写入配置文件

#### 配置窗口从1开始

```
set-option -g base-index 1
```

## 参考资料

* [(好)tmux guide - readthedoc](https://tmuxguide.readthedocs.io/en/latest/tmux/tmux.html)

## FAQ

#### 偶现复制模式复制到多余空格

Text copied from vim inside a tmux session is padded with spaces to the right
https://stackoverflow.com/questions/28749919/text-copied-from-vim-inside-a-tmux-session-is-padded-with-spaces-to-the-right

待尝试
```
TERM=xterm vim

or use below in ~/.tmux.conf

set -g default-terminal "xterm"
```

Trailing spaces when copying from console
https://unix.stackexchange.com/questions/218248/trailing-spaces-when-copying-from-console

https://github.com/microsoft/terminal/issues/8976
Line breaks are ignored inconsistently when copying text in tmux copy mode #8976
=> 未解决
