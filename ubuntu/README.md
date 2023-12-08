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

## 投屏到电视

[电脑如何投屏电视，所有方法汇总-2023](https://www.zhihu.com/tardis/zm/art/360544450?source_id=1003)

https://www.lebo.cn/news/AboutNewsContent?id=858

## 其他

#### 播放 mkv 格式的视频
 
执行下面命令即可。
```
sudo apt install ffmpeg
sudo apt install mplayer
sudo apt install smplayer # 这个可以生效
```
之后将 mkv 文件的打开方式设置为 Smplayer 即可。
