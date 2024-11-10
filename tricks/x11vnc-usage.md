# x11vnc使用

## ubuntu x11vnc systemctl 服务

以前记到腾讯文档上的。。
ubuntu 18.04配置x11vnc服务

### 基本使用

#### 安装x11vnc

```
sudo apt install -y x11vnc
```

#### 准备vnc密码

(可选) 也可以设置不要密码

生成vnc密码到指定文件
```
sudo x11vnc -storepasswd /etc/x11vnc.pass
```

#### 常用启动命令

常用的启动命令如下
```
x11vnc -auth guess -forever -loop -noxdamage -repeat -rfbauth /home/USERNAME/.vnc/passwd -rfbport 5900 -shared
```

启动时的常用配置说明

- 使用 -nopw -accept popup:0 设置可以不使用 VNC 密码进行连接
- 使用 -once 设置同时只允许存在一个最新的连接
- 使用 -forever 设置允许任意个连接同时存在
- 使用 -viewonly 设置只允许查看，不允许操作

### ubuntu 20.04设置x11vnc服务开机启动

参考: [Ubuntu20.4 使用 x11vnc](https://blog.ws.lu/posts/linux/ubuntu/ubuntu20.4-x11vnc/)

x11vnc 是一个不依赖任何图形界面的 VNC 服务。在电脑重启后没有进行图形界面登录时，也可以使用。
但是由于 GNOME 的管理机制，连接成功登录后，会黑屏（有不完美的解决方案）。

#### 概述

需要 x11vnc 服务在不登录的时候也能成功启动

修改 /etc/gdm3/custom.conf 文件，取消 WaylandEnable=false 前的 #，重启电脑

使用 sudo loginctl 查看登录用户
```
SESSION  UID USER     SEAT  TTY 
     c1  125 gdm      seat0 tty1
```
记住 gdm 用户的 UID



#### 配置systemctl服务

创建配置文件 /lib/systemd/system/x11vnc.service => 系统登录后启动, 验证ok, **未登录不行!!!**
```
[Unit]
Description=Start x11vnc at startup.
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/bin/x11vnc -loop -forever -bg -rfbport 5901 -xkb -noxrecord -noxfixes -noxdamage -shared -norc -auth /run/user/125/gdm/Xauthority -rfbauth /etc/x11vnc.pass

[Install]
WantedBy=multi-user.target
```

启动服务并设置为开机自启
```
sudo systemctl daemon-reload
sudo systemctl start x11vnc.service
sudo systemctl enable x11vnc.service
```

重启电脑后，进行连接，会进入登录界面。但是输入密码登录后会黑屏。

### 黑屏解决方案

- 解决方案1：自启另一个 x11vnc 服务
- 解决方案2：使用 vino 作为另一个 vnc 服务

关键字《ubuntu 启动vnc服务》
https://www.yisu.com/zixun/7577.html

解决方案1：自启另一个 x11vnc 服务
点击 Activities 搜索 Startup Applications，添加一个自启脚本
```
x11vnc -auth guess -rfbport 5901 -rfbauth /home/USERNAME/.vnc/passwd
x11vnc -auth guess -forever -loop -noxdamage -repeat -rfbauth /home/adam/.vnc/passwd -rfbport 5900 -shared
```

解决方案2：使用 vino 作为另一个 vnc 服务
vino 的安装使用参考 [Ubuntu20.4 使用 vino VNC](https://blog.ws.lu/posts/linux/ubuntu/ubuntu20.4-x11vnc/ubuntu20.4-vino-vnc.md)。

为不同用户修改 vino server 的监听端口
```
$ gsettings set org.gnome.Vino alternative-port 5901
$ gsettings set org.gnome.Vino use-alternative-port true
```

#### 参考文档

- [ubuntu 18.04配置x11vnc systemctl 服务](https://blupa.info/books/short-linux-guides/page/x11vnc-systemd-service-xubuntu-1804-%28lightdm%29)
  ubuntu 18.04使用lightdm, x11vnc参数可以是`-auth /var/run/lightdm/root/:0 -display WAIT:0`
- [Ubuntu20.4 使用 x11vnc](https://blog.ws.lu/posts/linux/ubuntu/ubuntu20.4-x11vnc/)

## x11vnc源码编译

单号 #21173
当时x11vnc旧版本不能自适应屏幕分辨率
(2020-04-26左右的版本)

#### 获取源码

libvncserver, x11vnc
```
git clone https://github.com/LibVNC/libvncserver.git
git clone https://github.com/LibVNC/x11vnc.git
```

#### 编译libvncserver

暂不整理, 后续有需要再处理

编译, 源自readme.md
```
mkdir build
cd build
cmake ..
cmake --build .
```

## 旧的资料

#### 旧的x11vnc资料

最终结果: 自研3D协议开始支持Linux系统了，x11vnc转入备用。

查资料发现x11vnc可能不支持分辨率自动调整，但是正在支持中，需要最新的还没发布的libvncserver支持实现。
https://github.com/LibVNC/x11vnc/issues/91
(tigervnc支持分辨率自动调整，已经验证了)

使用别人提交的x11vnc支持调整size的merge分支，加上新版libvncserver，编译验证，可以在gpu镜像中提供vnc调整窗口大小服务。
https://github.com/LibVNC/x11vnc/pull/107

普通镜像vnc自动调整分辨率，使用xrandr的一条命令直接适配
```
xrandr --fb 1024x768 --output Virtual-0 --mode 1024x768 --panning 1024x768
```
参考： https://christianhujer.github.io/Xrandr-Virtual-Desktop-Size/

#### x11vnc service

旧的service, lightdm桌面系统, 无密码, 自适应屏幕分辨率
```
[Unit]
Description=VNC Server for X11
Requires=lightdm.service
After=lightdm.service

[Service]
Type=forking
ExecStart=/usr/bin/x11vnc -noxdamage -o /var/log/x11vnc.log -capslock -nomodtweak \
 -nevershared -forever -bg -repeat -rfbport 5901 -auth guess -setdesktopsize
ExecStop=/usr/bin/killall x11vnc
Restart=on-failure

[Install]
WantedBy=graphical.target
```

有些系统略有不同, requires, wantedby等
```
[Unit]
Description=VNC Server for X11
Requires=graphical.target
After=graphical.target

[Service]
Type=forking
ExecStart=/usr/bin/x11vnc -noxdamage -o /var/log/x11vnc.log -capslock -nomodtweak \
 -nevershared -forever -bg -repeat -rfbport 5911 -auth guess -setdesktopsize
ExecStop=/usr/bin/killall x11vnc
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

#### x11vnc启动脚本

x11vnc-server.sh
```
#!/bin/sh

pid=`pidof x11vnc`
if [ $? -eq 0 ];then
        echo "x11vnc is already runing, pid is $pid"
        exit 0
fi

/usr/bin/x11vnc -noxdamage -o /var/log/x11vnc.log -capslock -nomodtweak -nevershared -forever -bg -repeat -rfbport 5901 -auth guess
```
