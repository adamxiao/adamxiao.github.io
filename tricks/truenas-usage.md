# truenas安装使用

我之前默认使用uefi安装的, bios安装也行

很容易安装，主要是设置web用户admin密码, 以及配置网络
配置网络先在linux后台配置(控制台有问题?), 然后再web页面上固定网络配置。

#### iscsi创建

关键字《truenas set iscsi》

参考: https://www.informaticar.net/how-to-create-iscsi-target-in-truenas/

From the left menu select Sharing | Block Shares (iSCSI) | click on Wizard in top right part of the screen.

监听地址一定要选择一个

## FAQ

- 虚拟机使用磁盘创建pool, 需要uuid
- NFS共享默认是v3协议,需要手动开启v4协议
- samba默认不开启v1认证支持,windows10不能挂载
- ftp需要用户有主目录?

## 参考资料

https://blog.51cto.com/riverxyz/4572290
