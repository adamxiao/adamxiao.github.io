# 安装ubuntu需要做的事情

## 软件安装

### 1. 更新软件源，加快软件下载速度

/etc/apt/source.list
```
# deb cdrom:[Ubuntu 16.04.1 LTS _Xenial Xerus_ - Release amd64 (20160719)]/ xenial main restricted
deb http://mirrors.163.com/ubuntu/ xenial main restricted
deb-src http://mirrors.163.com/ubuntu/ xenial main restricted
deb http://mirrors.163.com/ubuntu/ xenial-updates main restricted
deb-src http://mirrors.163.com/ubuntu/ xenial-updates main restricted
deb http://mirrors.163.com/ubuntu/ xenial universe
deb-src http://mirrors.163.com/ubuntu/ xenial universe
deb http://mirrors.163.com/ubuntu/ xenial-updates universe
deb-src http://mirrors.163.com/ubuntu/ xenial-updates universe
deb http://mirrors.163.com/ubuntu/ xenial multiverse
deb-src http://mirrors.163.com/ubuntu/ xenial multiverse
deb http://mirrors.163.com/ubuntu/ xenial-updates multiverse
deb-src http://mirrors.163.com/ubuntu/ xenial-updates multiverse
deb http://mirrors.163.com/ubuntu/ xenial-backports main restricted universe multiverse
deb-src http://mirrors.163.com/ubuntu/ xenial-backports main restricted universe multiverse
deb http://mirrors.163.com/ubuntu/ xenial-security main restricted
deb-src http://mirrors.163.com/ubuntu/ xenial-security main restricted
deb http://mirrors.163.com/ubuntu/ xenial-security universe
deb-src http://mirrors.163.com/ubuntu/ xenial-security universe
deb http://mirrors.163.com/ubuntu/ xenial-security multiverse
deb-src http://mirrors.163.com/ubuntu/ xenial-security multiverse

deb http://cn.archive.ubuntu.com/ubuntu/ xenial main restricted
deb http://cn.archive.ubuntu.com/ubuntu/ xenial-updates main restricted
deb http://cn.archive.ubuntu.com/ubuntu/ xenial universe
deb http://cn.archive.ubuntu.com/ubuntu/ xenial-updates universe
deb http://cn.archive.ubuntu.com/ubuntu/ xenial multiverse
deb http://cn.archive.ubuntu.com/ubuntu/ xenial-updates multiverse
deb http://cn.archive.ubuntu.com/ubuntu/ xenial-backports main restricted universe multiverse
deb http://security.ubuntu.com/ubuntu xenial-security main restricted
deb http://security.ubuntu.com/ubuntu xenial-security universe
deb http://security.ubuntu.com/ubuntu xenial-security multiverse
```

### 2. 系统重要编程软件安装

```bash
sudo apt-get install vim exuberant-ctags openssh-server git subversion \
	autoconf libtool valgrind unrar cmake
```

### 3. 其他软件安装

- 安装chrome浏览器
```bash
wget -q -O - https://raw.githubusercontent.com/longhr/ubuntu1604hub/master/linux_signing_key.pub | sudo apt-key add
sudo sh -c 'echo "deb [ arch=amd64 ] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt-get update
sudo apt-get install google-chrome-stable
```
- 安装virtualbox
- 安装中文输入法以及中文语言包fcitx-googlepinyin
- 以及参考其他人安装的好用的软件
http://www.cnblogs.com/jxldjsn/p/5686197.html
http://blog.csdn.net/fuchaosz/article/details/51882935

## 数据配置恢复

### 1. vim配置恢复

从github上仓库下载配置

### 2. wiki恢复

从github上仓库下载配置

### 其他数据恢复

- 下载firefox的xmarks插件，同步书签
- firefox插件恢复
- chrome插件恢复
- 其他备份数据恢复
fstab数据分区自动挂载, blkid查看uuid
```
# /adam data partition
UUID=33e9ae3c-24bb-4fd5-bfb8-f90dc5275379 /adam           ext4    defaults        0       2
```

## 其他

#### uniface ubuntu 22.04起不来

修改入口脚本: /opt/ksvd/usr/bin/uniface

export GDK_BACKEND=x11
```
if [ -d "/opt/ksvd/usr/lib/ksvd_client" ];
then
    export GDK_BACKEND=x11
fi
```

以及制作pcap库的链接
```
ln -sf /usr/lib/x86_64-linux-gnu/libpcap.so.1.10.1 /usr/lib/x86_64-linux-gnu/libpcap.so.1
```

其他
```
sudo apt install -y virt-viewer libqt5core5a
libqt5glib-2.0-0 => ubuntu2404?
```

#### 配置Desktop等目录位置

https://blog.csdn.net/m0_49448331/article/details/113844705

修改配置文件: ~/.config/user-dirs.dirs
```
XDG_DESKTOP_DIR="$HOME/Desktop"
XDG_DOWNLOAD_DIR="$HOME/Downloads"
XDG_TEMPLATES_DIR="$HOME/"
XDG_PUBLICSHARE_DIR="$HOME/"
XDG_DOCUMENTS_DIR="$HOME/Documents"
XDG_MUSIC_DIR="$HOME/"
XDG_PICTURES_DIR="$HOME/"
XDG_VIDEOS_DIR="$HOME/"
```
