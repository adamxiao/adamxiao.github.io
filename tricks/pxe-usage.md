# pxe安装系统

## 准备pxe环境

使用dnsmasq准备dhcp和tftp服务

#### 部署dnsmasq服务

使用dnsmasq服务部署
```
yum install -y dnsmasq
systemctl start dnsmasq
```

配置dhcp和tftp服务, dnsmasq.conf
```conf
# cat /etc/dnsmasq.d/pxe-dhcp.conf
#interface=eth0
#bind-interfaces

dhcp-range=192.168.88.100,192.168.88.200,255.255.255.0,1h
dhcp-option=3,192.168.88.1
dhcp-option=6,8.8.8.8

dhcp-match=set:efi-x86_64,option:client-arch,7
dhcp-match=set:efi-x86_64,option:client-arch,9
dhcp-match=set:efi-x86,option:client-arch,6
dhcp-match=set:efi-arm,option:client-arch,11
dhcp-match=set:bios,option:client-arch,0
dhcp-boot=tag:efi-x86_64,shim.efi,,
dhcp-boot=tag:efi-x86,shim.efi,,
dhcp-boot=tag:efi-arm,arm/shim.efi,,
dhcp-boot=tag:bios,pxelinux/pxelinux.0,,

# cat /etc/dnsmasq.d/tftp.conf
enable-tftp
tftp-root=/var/lib/tftp/
```

配置dhcp白名单
```
# dhcp白名单机制
dhcp-ignore=tag:!known
dhcp-host=52:54:84:00:05:8a,192.168.88.101,bootstrap,set:known
```

#### 准备efi等资料

在ISO镜像中，提取出如下文件
- 从 `shim` 包中提取 `shim.efi`
- 从 `grub2-efi` 包中提取 `grubx64.efi`

示例提取方法:
```
# rpm2cpio shim-version-architecture.rpm | cpio -dimv
# rpm2cpio grub2-efi-version-architecture.rpm | cpio -dimv

# cp publicly_available_directory/boot/efi/EFI/redhat/shim.efi /var/lib/tftpboot/
# cp publicly_available_directory/boot/efi/EFI/redhat/grubx64.efi /var/lib/tftpboot/
```

#### 配置centos系列grub启动项

配置centos系列grub启动项
```
set timeout=60
menuentry 'CentOS' {
  linuxefi images/CentOS-7/vmlinuz ip=dhcp inst.repo=http://10.32.5.1/mnt/archive/CentOS-7/7/Server/x86_64/os/
  initrdefi images/CentOS-7/initrd.img
}
```

镜像准备方法
```
# mkdir -p /var/lib/tftpboot/images/CentOS-7
# cp /path-to-x86-64-images/pxeboot/{vmlinuz,initrd.img} /var/lib/tftpboot/images/CentOS-7/
```

#### uefi启动模式

## pxe安装ubuntu

关键字《centos pxe install ubuntu》
参考： Configure CentOS 7 PXE Server to Install Ubuntu 18.10
https://www.centlinux.com/2018/11/configure-centos-7-pxe-server-install-ubuntu-18.html
没有尝试成功!!! =》 放弃，找不到原因，这个用nfs我也不喜欢

关键字《pxe install ubuntu desktop》
感觉这个比较靠谱，待尝试!!! => 验证安装成功了，但是有一点小问题?
https://linuxhint.com/pxe_boot_ubuntu_server/

配置legacy安装启动项 => 验证成功
```
default menu.c32
timeout 300
menu title kylin

menu title ########## PXE Boot Menu ##########

label local
  menu default
  menu label Boot from ^local drive
  localboot 0xffff

label -Ubuntu-20.04
  menu label ^Install Ubuntu 20.04 x64
  kernel image/ubuntu-2004/vmlinuz
  append initrd=image/ubuntu-2004/initrd ip=dhcp boot=casper netboot=nfs nfsroot=192.168.88.10:/data/ubuntu-2004/ splash toram ---
```

uefi启动项, grub.conf
```
set timeout=60
menuentry 'Install Ubuntu 20.04 Desktop' {
  # 验证失败
  linuxefi image/ubuntu-2004/vmlinuz ip=dhcp boot=casper netboot=nfs nfsroot=192.168.88.10:/data/ubuntu-2004/ splash toram ---
  initrdefi image/ubuntu-2004/initrd
}
```

配置ubuntu20.04的nfs存储
```
mount ubuntu-20.04.5-desktop-amd64.iso /mnt
rsync -avh /mnt/ $remote_server:/data/ubuntu-2004
```

参考:

关键字`pxe 安装 uefi ubuntu 20.04 desktop`

- [Ubuntu 20.04 – Deploy Ubuntu 20.04 Desktop through PXE (BIOS & UEFI)](https://c-nergy.be/blog/?p=16353)

- [Set up PXE Server on Ubuntu20.04 and Window 10](https://medium.com/jacklee26/set-up-pxe-server-on-ubuntu20-04-and-window-10-e69733c1de87)

## FAQ

#### PXE-09 I/O buffer allocate failed

抓dhcp的包发现:
dhcp客户端拒绝这个ip地址: `Lease is denied upon entering bound`

=> 原因是子网掩码搞错了, 255.255.250.0, 该正确就好了
可以看efi固件的源码:
https://github.com/tianocore/edk2/blob/master/NetworkPkg/Dhcp4Dxe/Dhcp4Io.c

#### mount failed: permission failed

使用F2看到的vmlinuz启动错误信息

原来是nfs路径配置错误了, 纠正后即可

## 参考资料

[Centos - Preparing for a Network Installation](https://docs.centos.org/en-US/centos/install-guide/pxe-server/#sect-network-boot-setup-uefi)
