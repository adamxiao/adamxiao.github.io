# nmcli命令配置网络

参考如下示例, 配置网卡ip,gateway,dns等

```bash
sudo nmcli c delete 'Wired connection 1'
sudo nmcli c add con-name enp3s0 type ethernet ifname enp3s0
sudo nmcli c mod enp3s0 ipv4.addresses 10.90.3.84/24 ipv4.gateway 10.90.3.1 ipv4.method manual
sudo nmcli c mod enp3s0 ipv4.dns 10.90.3.38
sudo nmcli c mod enp3s0 ipv6.method disabled
# confirm /etc/NetworkManager/system-connections/enp3s0.nmconnection
sudo nmcli c up enp3s0
```

#### 新增ip地址（网卡多ip配置）

关键字《nmcli 设置接口多ip》

https://www.linuxidc.com/Linux/2017-07/145573.htm

```
nmcli connection modify test2 +ipv4.addresses 10.10.10.10/8
```

对应nmcli配置文件内容为
```
addresses2=xxx
```

#### 添加静态路由

参考: https://access.redhat.com/documentation/zh-cn/red_hat_enterprise_linux/8/html/configuring_and_managing_networking/configuring-static-routes_configuring-and-managing-networking

```bash
$ sudo nmcli connection modify example +ipv4.routes "192.0.2.0/24 198.51.100.1"
```

```bash
$ sudo nmcli connection modify example +ipv4.routes "192.0.2.0/24 198.51.100.1, 203.0.113.0/24 198.51.100.1"
```

#### 配置接口unmanaged

关键字《ubuntu desktop network manager unmanaged》

https://access.redhat.com/documentation/zh-tw/red_hat_enterprise_linux/8/html/configuring_and_managing_networking/configuring-networkmanager-to-ignore-certain-devices_configuring-and-managing-networking#temporarily-configuring-a-device-as-unmanaged-in-networkmanager_configuring-networkmanager-to-ignore-certain-devices

15.2. Temporarily configuring a device as unmanaged in NetworkManager
```
# nmcli device status
DEVICE  TYPE      STATE         CONNECTION
enp1s0  ethernet  disconnected  --
...

nmcli device set enp1s0 managed no
```

## 管理ovs接口

关键字《nmcli config ovs bridge》

参考: https://blog.oddbit.com/post/2020-02-15-configuring-open-vswitch-with/

创建一个ovs桥:
```bash
nmcli c add type ovs-bridge conn.interface br-house con-name br-house
nmcli c add type ovs-port conn.interface br-house master br-house con-name ovs-port-br-house
nmcli c add type ovs-interface slave-type ovs-port conn.interface br-house master ovs-port-br-house  con-name ovs-if-br-house
```
Unlike ovs-vsctl, creating the bridge won’t automatically create an interface for you. The two additional commands above get us an actual interface named br-house (configured using DHCP, because we didn’t explicitly set ipv4.method on the interface).

将物理网卡eth0加入到ovs桥
```bash
nmcli c add type ovs-port conn.interface eth0 master br-house con-name ovs-port-eth0
nmcli c add type ethernet conn.interface eth0 master ovs-port-eth0 con-name ovs-if-eth0
```

And finally, we create some ports to expose specific vlans:
```
nmcli c add type ovs-port conn.interface vlan1 master br-house ovs-port.tag 1 con-name ovs-port-vlan1
nmcli c add type ovs-interface slave-type ovs-port conn.interface vlan1 master ovs-port-vlan1 con-name ovs-if-vlan1 ipv4.method static ipv4.address 192.168.7.1/24

nmcli c add type ovs-port conn.interface vlan101 master br-house ovs-port.tag 101 con-name ovs-port-vlan101
nmcli c add type ovs-interface slave-type ovs-port conn.interface vlan101 master ovs-port-vlan101 con-name ovs-if-vlan101 ipv4.method static ipv4.address 192.168.11.1/24

nmcli c add type ovs-port conn.interface vlan102 master br-house ovs-port.tag 102 con-name ovs-port-vlan102
nmcli c add type ovs-interface slave-type ovs-port conn.interface vlan102 master ovs-port-vlan102 con-name ovs-if-vlan102 ipv4.method static ipv4.address 192.168.13.1/24
```

手动修改ip地址
```
nmcli c modify ovs-if-br-house ipv4.address 10.90.3.38/24 ipv4.method manual
```

## 旧的网络管理方式

https://www.skynats.com/blog/how-to-manage-networking-with-networkmanager/

Using Legacy Network Script

The deprecated Network script doesn’t come by default in RHEL/CentOS 8.

In order to use it, you can install the network-scripts package.

```
 # yum install network-scripts
```

https://www.cnblogs.com/my-show-time/p/14826875.html

三、3种网络配置方法#
 在讲3种配置方法前，需要先明白ifcfg和NM connection的关联：虽然network.service被废弃了，但是redhat为了兼容传统的ifcfg，通过NM进行网络配置时候，会自动将connection同步到ifcfg配置文件中。也可以通过nmcli c reload或者nmcli c load /etc/sysconfig/network-scripts/ifcfg-ethX的方式来让NM读取ifcfg配置文件到connection中。因此ifcfg和connection是一对一的关系，另外上面有提到，connection和device是多对一的关系。

手工配置ifcfg，通过NM来生效
通过NM自带工具配ip，比如nmcli
手工配置ifcfg，通过传统network.service来生效

2、nmcli device#
 设备，是网络设备的接口，可理解为实际存在的网卡（包括物理网卡和虚拟网卡）。可以简写为nmcli d

 在NM里，有2个维度：连接（connection）和设备（device），这是多对一的关系。想给某个网卡配ip，首先NM要能纳管这个网卡。设备里存在的网卡（即 nmcli d可以看到的），就是NM纳管的。接着，可以为一个设备配置多个连接（即 nmcli c可以看到的），每个连接可以理解为一个ifcfg配置文件，那么如前面说的，一个device可以拥有多个连接，也就是可以拥有多个配置文件。同一时刻，一个设备只能有一个连接活跃。可以通过 nmcli c up 切换连接，在 up 一个device 的连接时另外一个活跃的 连接会自动 down 。

## FAQ

#### 禁止自动生成接口的dhcp连接

关键字《disable nm auto Wired connection 1》

https://askubuntu.com/questions/1257549/is-there-any-way-to-disable-automatically-connect-to-this-network-when-availabl

验证成功
```
adding no-auto-default=* under [main]
```

其他资料

[How do I prevent Network Manager from controlling an interface?](https://support.qacafe.com/knowledge-base/how-do-i-prevent-network-manager-from-controlling-an-interface/)

## 参考资料

* [27 nmcli command examples (cheatsheet), compare nm-settings with if-cfg file](https://www.golinuxcloud.com/nmcli-command-examples-cheatsheet-centos-rhel/)
* [rhel7 - 2.7. Using NetworkManager with sysconfig files](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/networking_guide/sec-using_networkmanager_with_sysconfig_files)
