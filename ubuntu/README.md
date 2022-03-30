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

