# ubuntu使用指南

## ubuntu install rtl8812au driver

* 无线驱动
* Realtek
* RTL8812AU

```bash
git clone https://ubuntuhandbook.org/index.php/2019/11/install-rtl8814au-driver-ubuntu-19-10-kernel-5-13/
sudo apt install git build-essential dkms
git clone https://github.com/aircrack-ng/rtl8812au.git
cd rtl8812au && sudo ./dkms-install.sh
# => 直接make和sudo make install解决的。
sudo modprobe 88XXau
```

rtl8822be驱动

https://askubuntu.com/questions/1263141/rtl8822be-driver-for-ubuntu-18-04-and-20-04
=> 未验证成功
```
sudo apt install git dkms
git clone https://github.com/aircrack-ng/rtl8812au.git
cd rtl8812au
sudo make dkms_install
```

https://devicetests.com/install-rtl8822be-wifi-driver-ubuntu-hp-15-da1009ne
=> 已废弃
```
git clone https://github.com/mid-kid/r8822be.git
cd r8822be
./make
sudo rmmod rtwpci rtw88
sudo ./make install
sudo modprobe r8822be
```

## ubuntu刻录安装windows iso

关键字《ubuntu 刻录windows iso》

使用woeusb
```
ERROR: WoeUSB requires wimlib-imagex command in the executable search path, but it is not found.
apt-get install wimtools
```

## ubuntu安装windows软件

使用Bottles安装

关键字《ubuntu 使用 Bottles》

[22 Things You MUST DO After Installing Ubuntu 22.04 LTS (JAMMY JELLY FISH)](https://www.youtube.com/watch?v=CRXbjLbepqc&ab_channel=KskRoyal)

[如何在Linux執行Windows exe檔，用Bottles管理多版本的Wine容器](https://ivonblog.com/posts/setup-linux-bottles/)

Flatpak是跨發行版的套件管理員，大部分的Linux發行版都支援。請至Flatpak官網查看對應發行版的安裝指令。

安装flatpak
```
sudo apt install flatpak
```

配置仓库
```
flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
```

裝Bottles，輸入y確認，大約需要1GB空間 (Flatpak把應用程式的依賴套件都包在一塊因此很肥)
```
flatpak install flathub com.usebottles.bottles
```

#### ubuntu安装wechat微信

https://www.ubuntukylin.com/applications/114-en.html
=> ubuntu 20.04验证安装使用微信成功

deepin深度系统上也有wechat等安装包

## 启用防火墙

默认是没有启用的
```
systemctl status ufw
● ufw.service - Uncomplicated firewall
```

可以开启防火墙
```
systemctl enable ufw
```

可以安装gui工具管理
```
apt install gufw
```

或者使用命令行管理
```
sudo ufw status
sudo ufw allow 22/tcp
sudo ufw deny 22/tcp
```

ufw status inactive
=> 需要先安装?
```
sudo apt install ufw
sudo ufw enable
```

https://serverspace.io/support/help/basic-commands-ufw/
```
sudo ufw app list # 只是查看应用列表?
sudo ufw allow OpenSSH # 放行ssh服务
sudo ufw allow from 91.198.174.0/24 proto tcp to any port 22 # 放行特定ip访问特定端口
sudo ufw delete allow OpenSSH # 删除规则
```

## 投屏到电视

[电脑如何投屏电视，所有方法汇总-2023](https://www.zhihu.com/tardis/zm/art/360544450?source_id=1003)

https://www.lebo.cn/news/AboutNewsContent?id=858

https://www.599cn.com/post/8119.html 

## 加密home目录

- 可以使用lvm全盘加密
- 还有文件级别的加密
  => 不考虑这种，不好用
  mount -t encryptfs xxx xxx
- 加密分区?
  https://www.tecmint.com/encrypt-disk-installing-ubuntu/
- 使用zfs

关键字《ubuntu install with encryption home》

[The easiest way to install Ubuntu on an encrypted partition](https://maciej-sady.medium.com/the-easiest-way-to-install-ubuntu-on-an-encrypted-partition-a882320dd6bb)
=> 创建一个lvm加密卷作为home分区, 开机时提示解密!

https://gist.github.com/superjamie/d56d8bc3c9261ad603194726e3fef50f
How to install Ubuntu with LUKS Encryption on LVM

https://blog.wtm.moe/articles/btrfs-on-luks/
LUKS on Partition
- 优点是配置方便，可以自由添加和更换加密密钥。
- 缺点是不灵活，必须预先分配要加密的磁盘空间。 可以但很麻烦，而且需求很少。

https://www.eallion.com/ubuntu-zfs-encryption/
https://gist.github.com/superjamie/d56d8bc3c9261ad603194726e3fef50f

## 其他

#### 绑定本地目录

编辑fstab配置文件
```
/data/local /usr/local     ext4   default,bind  0 0
```

#### 录屏

关键字《linux 录屏》

https://access.redhat.com/documentation/zh-cn/red_hat_enterprise_linux/7/html/desktop_migration_and_administration_guide/screencast-recording
GNOME Shell 具有内置录屏功能，允许用户记录会话期间的桌面或应用程序活动，并以 webm 格式将录制的内容作为高分辨率视频文件分发。
Ctrl+Alt+Shift+R => 开始和停止都按这个

https://blog.csdn.net/sazass/article/details/124111191
- 录屏默认的时长30秒，超时会自动结束！ => 可以调整
- 录屏后文件默认存放在主目录内的视频目录中
- 录屏是直接录制
- 不能录制声音

gsettings set org.gnome.settings-daemon.plugins.media-keys max-screencast-length 300


https://www.zhihu.com/question/51920876
SimpleScreenRecorder

录屏配置需要在音频输入选择
后端： PulseAudio
源：Family 17th

```
sudo add-apt-repository ppa:maarten-baert/simplescreenrecorder
sudo apt update
sudo apt install simplescreenrecorder
```

#### 刻录DVD

```
sudo apt install brasero
```

#### 生成二维码图片

https://www.omgubuntu.co.uk/2011/03/how-to-create-qr-codes-in-ubuntu

```
apt install -y qrencode
qrencode -o google.png 'http://google.com'
=> 控制二维码图片大小
qrencode -o ~/Desktop/google.png -s 6 'http://google.com'
```

[Software to read a QR code?](https://askubuntu.com/questions/22871/software-to-read-a-qr-code)

https://blog.csdn.net/wangweiqiang1325/article/details/72832531
二维码解析
```
apt install zbar-tools
zbarimg xxx.png
```

#### 播放 mkv 格式的视频
 
执行下面命令即可。
```
sudo apt install ffmpeg
sudo apt install mplayer
sudo apt install smplayer # 这个可以生效
```
之后将 mkv 文件的打开方式设置为 Smplayer 即可。
