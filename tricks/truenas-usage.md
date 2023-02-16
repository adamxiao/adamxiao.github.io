# truenas安装使用

我之前默认使用uefi安装的, bios安装也行

很容易安装，主要是设置web用户admin密码, 以及配置网络
配置网络先在linux后台配置(控制台有问题?), 然后再web页面上固定网络配置。

#### 配置静态ip地址

在控制台配置:

- 1.首先选择`1) Configure network interface`
  配置网卡为静态模式，以及静态ip地址
  - 配置ipv4_dhcp: no
  - 配置alias: 10.90.3.25/24
  - 最后要测试一下，然后生效持久化保存
- 2.然后选择`2) Configure network settings`
  配置默认网关
  - 配置ipv4gateway: 10.90.3.1

#### iscsi创建

关键字《truenas set iscsi》

参考: https://www.informaticar.net/how-to-create-iscsi-target-in-truenas/

From the left menu select Sharing | Block Shares (iSCSI) | click on Wizard in top right part of the screen.

监听地址一定要选择一个

ipsan iscsi相关概念:
- target
- init
- lun

## FAQ

- 虚拟机使用磁盘创建pool, 需要uuid
- NFS共享默认是v3协议,需要手动开启v4协议
- samba默认不开启v1认证支持,windows10不能挂载
- ftp需要用户有主目录?

## 参考资料

https://blog.51cto.com/riverxyz/4572290
