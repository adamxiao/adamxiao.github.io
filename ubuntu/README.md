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
