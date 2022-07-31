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

## 参考资料

* [(好)tmux guide - readthedoc](https://tmuxguide.readthedocs.io/en/latest/tmux/tmux.html)
