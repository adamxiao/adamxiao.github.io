# openeuler使用

注: kylinsec344,345是基于openeuler的, unikylin341是基于centos的

关键字《openEuler-20.03 安装桌面》

https://zhuanlan.zhihu.com/p/229861153

配置使用使用清华源
```
[osrepo]
name=osrepo
baseurl=https://mirrors.tuna.tsinghua.edu.cn/openeuler/openEuler-20.03-LTS/OS/x86_64/
enabled=1
gpgcheck=1
gpgkey=https://mirrors.tuna.tsinghua.edu.cn/openeuler/openEuler-20.03-LTS/OS/x86_64/RPM-GPG-KEY-openEuler
```

安装 GNOME
```
sudo dnf install gnome-shell gdm gnome-session
```

设置 gdm 开机自启
```
sudo systemctl enable gdm.service
sudo systemctl set-default graphical.target
```

补全丢失文件
在上一节已经说过了，在 openEuler 直接未经修改直接启动 gdm 会遇到无法登陆的问题，具体表现为登陆了过几秒就直接回到了 gdm 的登陆界面。这个问题是由于 openEuler 的 gdm 的配置文件不全导致的。具体来说，是 /etc/gdm/Xsession 指向的 /etc/X11/Xsession 不存在。
```
cd /tmp
wget https://gitee.com/name1e5s/xsession/raw/master/Xsession
mv Xsession /etc/gdm/
chmod 0777 /etc/gdm/Xsession
```

至此，openEuler 的桌面环境已经完全可用，如果你注意到了没有终端，直接 dnf install gnome-terminal 即可安装。以下是安装好后的背景
