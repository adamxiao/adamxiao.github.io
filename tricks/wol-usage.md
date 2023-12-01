# WOL远程唤醒开机

- WOL
- Wake On Lan

安装wol客户端
```
apt install wakeonlan
yum -y install wol # epel-release
```

环境某台机器，需要知道网卡mac地址
```
wakeonlan 8c:ec:4b:b6:60:5a
```

前提，BIOS需要开启WOL功能， 一般是在电源管理 -> WOL中

网卡需要配置开启WOL功能, 例如
```
ethtool --change enp4s0 wol g
ethtool -s eth0 wol g
```

- p	Wake on PHY activity
- u	Wake on unicast messages
- m	Wake on multicast messages
- b	Wake on broadcast messages
- g	Wake on MagicPacket messages

3,当机器重启后，eth0的设置又会回复到Wake-on: d 状态,
这个问题怎么解决？
两个办法：第一个，也是我们的惯性思维;
把/sbin/ethtool -s eth0 wol g 这条命令附加到/etc/rc.local这个文件中，
则下次开机后会自动执行

第二个: 编辑/etc/sysconfig/network-scripts/ifcfg-eth0
（eth0网卡的配置文件），添加上一行：
```
ETHTOOL_OPTS="wol g"
```

#### 设置网卡支持WOL

https://blog.csdn.net/bigcat133/article/details/125035386

当时我的ubuntu是设置了这个服务wol
 /etc/systemd/system/wol.service
```
[Unit]
Description=Enable Wake On Lan

[Service]
Type=oneshot
ExecStart = /sbin/ethtool --change enp4s0 wol g

[Install]
WantedBy=basic.target
```

自动设置网卡
```
sudo systemctl daemon-reload
sudo systemctl enable wol.service
```

#### 设置BIOS支持WOL

https://www.cnblogs.com/mar-q/p/6404558.html
设置BIOS开启WOL：不同主板设置大同小异，都要实现两步，一是找到Power电源管理或Wake on Lan等类似选项，设置Power on by PCIE为enable；第二部关闭Power电源管理等关于节能的设置。

## 参考资料

- [linux安装远程唤醒](https://blog.csdn.net/m0_37416550/article/details/108590757)
