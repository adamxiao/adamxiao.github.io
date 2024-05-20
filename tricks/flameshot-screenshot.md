# ubuntu 使用flameshot截图

## 安装

安装flameshot，配置开机启动
（注意好像是要安装snap中的flameshot）
```
apt install flameshot
# 或者软件管理安装flameshot
```

## 使用

然后配置快捷键Ctrl+Alt+A开启截图
(ubuntu 22.04中flameshot局部截图有问题!)
```
/snap/bin/flameshot gui

Usage: /snap/flameshot/181/usr/local/bin/flameshot [flameshot-options] [arguments]

Per default runs Flameshot in the background and adds a tray icon for configuration.

Options:
  -h, --help     Displays this help
  -v, --version  Displays version information

Arguments:
  gui            Start a manual capture in GUI mode.
  screen         Capture a single screen.
  full           Capture the entire desktop.
  launcher       Open the capture launcher.
  config         Configure flameshot.
```

Ctrl-C保存截图到剪切板，就可以直接拷贝到腾讯文档中了。

## FAQ

#### ubuntu 2404 flameshot error unable to capture screen

关键字《flameshot error unable to capture screen》

https://github.com/flameshot-org/flameshot/issues/3365
=> 验证可以

创建可执行脚本文件: /usr/bin/fixflameshot
```
#!/bin/bash
env QT_QPA_PLATFORM=wayland flameshot gui
EOF
```
