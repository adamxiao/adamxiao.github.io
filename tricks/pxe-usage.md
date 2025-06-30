# pxe安装系统

## 原理

#### 网络引导程序NBP

[浅谈pxe和ipxe](https://zhuanlan.zhihu.com/p/591334237)

网络引导程序（Network Bootstrap Program，NBP ） 是引导链过程中的第一个环节，它们通常通过 TFTP 请求一小组补充文件，以便运行一个极简的操作系统执行器（例如，Windows PE 或基本的 Linux 内核 + initrd）。

常见的 NBP：iPXE、PXELINUX、GRUBx64

[(好)从无盘启动看 Linux 启动原理](https://z.itpub.net/article/detail/1DF87A7A5B7FBDF9E7DA28E3A12A9075)

由于我需要从网络启动，过程会变得复杂一些，主要变化如下

- 在 MBR 引导前，需要执行一系列的 PXE 流程，目的是挂载 iscsi 磁盘。
- 在加载 linux 内核后，由于之前 iPXE 固件已经退出，还需要再次挂载 iscsi 磁盘。

无盘启动并不是说完全没有磁盘，只是客户端本身没有磁盘，我们需要在远端给机器提供一种文件存储和磁盘共享的方案。我这里选择的是 iscsi 共享，相比于 NFS 和 samba 共享，它更底层，对系统的兼容性更好。


由于 linux 内核启动后，之前 ipxe 对应的环境已经退出，因此之前挂载的 iscsi 磁盘也无法访问，需要在 initrd 的 init shell 中重新挂载 iscsi 磁盘。因此我需要在上文的 4 步骤之前挂载 iscsi 磁盘，修改如下：

- 加载网卡内核驱动
- 启动网络
- 启动 iscsi 客户端挂载网络磁盘。

可以使用如下方式编辑已经生成好的 initrd 文件。

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

# disable dns server
port=0
```

可以配置dhcp白名单, 只给指定机器使用dhcp pxe
```
# dhcp白名单机制, 可选指定ip
dhcp-ignore=tag:!known
#dhcp-host=ff:ff:ff:ff:ff:fa,192.168.88.101,bootstrap,set:known
#dhcp-host=ff:ff:ff:ff:ff:fa,set:known
```

#### 准备efi等资料

在ISO镜像中，提取出如下文件
- 从 `shim` 包中提取 `shim.efi`
- 从 `grub2-efi` 包中提取 `grubx64.efi`

获取直接下载shim包来提取
```
yumdownloader shim-x64
yumdownloader grub2-efi-x64
```

示例提取方法:
(注意文件权限, 改成755, 不然可能没权限)
```
# rpm2cpio shim-version-architecture.rpm | cpio -dimv
# rpm2cpio grub2-efi-version-architecture.rpm | cpio -dimv

# cp publicly_available_directory/boot/efi/EFI/redhat/shim.efi /var/lib/tftpboot/
# cp publicly_available_directory/boot/efi/EFI/redhat/grubx64.efi /var/lib/tftpboot/
```

#### 准备legacy启动资料

旧的启动支持, 后续基本都用efi了吧

从syslinux包中提取pxelinux.0等文件
```
yumdownloader syslinux
```

示例提取方法
```
rpm2cpio syslinux-*.rpm | cpio -dimv
mkdir -p /var/lib/tftpboot/pxelinux/
cp ./usr/share/syslinux/pxelinux.0 /var/lib/tftpboot/pxelinux/
# 后续配置/var/lib/tftpboot/pxelinux/pxelinux.cfg/{default,01-52-54-00-19-93-5b}
```

#### 配置centos系列grub启动项

配置centos系列grub启动项
```
set timeout=60
menuentry 'CentOS' {
  linuxefi images/CentOS-7/vmlinuz ip=dhcp inst.repo=http://1.1.1.1/mnt/archive/CentOS-7/7/Server/x86_64/os/
  initrdefi images/CentOS-7/initrd.img
}
```

镜像准备方法
```
# mkdir -p /var/lib/tftpboot/images/CentOS-7
# cp /path-to-x86-64-images/pxeboot/{vmlinuz,initrd.img} /var/lib/tftpboot/images/CentOS-7/
```

#### efi示例配置文件

ksvd-818-server安装
```
menuentry 'Install Ksvd-818-server arm latest (0311-0322)' {
  linuxefi vmlinuz net.ifnames=0 biosdevname=0 ip=dhcp method=http://1.1.1.1/pxe/ksvd-818-server-0311-0319 ks=http://1.1.1.1/pxe/ksvd-818-server-0311-0319/kickstart/ks.cfg devfs=nomount
  initrdefi initrd.img
}
```

kylin341a安装
```
menuentry 'Install kylin341a' {
  linuxefi image/ksvd/kylin341/vmlinuz net.ifnames=0 biosdevname=0 ip=dhcp method=http://1.1.1.1/pxe/ksvd/kylin341 devfs=nomount
  initrdefi image/ksvd/kylin341/initrd.img
}
```

#### legacy示例配置文件

rhcos安装
```
LABEL rhcos-4.8.2-bootstrap
    KERNEL http://1.1.1.1/pxe/rhcos/vmlinuz
    APPEND initrd=http://1.1.1.1/pxe/rhcos/initrd.img ignition.platform.id=metal coreos.live.rootfs_url=http://1.1.1.1/pxe/rhcos/rootfs.img coreos.inst.install_dev=/dev/sda coreos.inst.insecure coreos.inst.ignition_url=http://1.1.1.1:9090/ignition/bootstrap.ign
```

ksvd安装
```
label -ksvd-818-latest
  menu label ^Install KSVD-818-latest(0311) x64
  kernel image/ksvd-818-0311/vmlinuz
  append initrd=image/ksvd-818-0311/initrd.img net.ifnames=0 biosdevname=0 method=http://1.1.1.1/pxe/ksvd-818-0311 ks=http://1.1.1.1/pxe/ksvd-818-0311/kickstart/ks.cfg devfs=nomount
```

## pxe安装KSVD-819

类似centos

#### 构建repo配置

提取iso中的所有文件到目录: ./ksvd-819-x86
```
sudo rsync -avh /mnt/ksvd819-x86 ./
```

(可选) 然后可以更新rpm包, 重新创建repo
```
# 参考 https://blog.csdn.net/evglow/article/details/104040243
yum install -y createrepo
# 删除Package中的KSVD几个rpm，替换为818-server的几个KSVD rpm包
# 然后重新生成软件源仓库
createrepo -d -g repodata/*.comps.xml .
```

#### 构建ks配置

提取iso中的配置: ./kickstart/ks.cfg

#### 提取vmlinux等

- ./images/pxeboot/vmlinuz
- ./images/pxeboot/initrd.img

#### 最后配置uefi安装项

参考KSVD iso的相关参数: ./EFI/BOOT/grub.cfg
=> 发现818行, 819不行了, 待研究。。。
```
menuentry 'Install Ksvd-818 x86 (0408)' {
  linuxefi /images/ksvd818/vmlinuz net.ifnames=0 biosdevname=0 ip=dhcp method=http://1.1.1.1/ksvd818 ks=http://1.1.1.1/ksvd818/kickstart/ks.cfg devfs=nomount
  initrdefi /images/ksvd818/initrd.img
}
```

## pxe安装openeuler 22.03

openEuler-22.03-LTS-SP3-x86_64-dvd.iso
- 提取vmlinuz, initrd.img
  images/pxeboot/ 目录下
  (如果是ipxe的话，直接拷贝整个iso目录到http目录下)
```
mount xxx.iso /mnt/
rsync -avh /mnt/ xxx/
```
- 构建repo (可选，更新rpm包才需要做)
```
createrepo -d -g repodata/*.comps.xml .
```
- 配置ipxe选项
```
#!ipxe

goto openeuler-2203-x86-install

:openeuler-2203-x86-install
echo Starting install openEuler-22.03-LTS-SP3-x86_64-dvd.iso
set base-url ${http-url}/openeuler-x86
kernel ${base-url}/images/pxeboot/vmlinuz initrd=initrd.img ip=dhcp net.ifnames=0 biosdevname=0 inst.repo=${base-url} inst.ks=${base-url}/ks/ks.cfg devfs=nomount
initrd ${base-url}/images/pxeboot/initrd.img
boot
```

- 配置kickstart脚本自动化安装
  设置语言
  设置root密码
  设置硬盘分区
```
lang en_US.UTF-8
rootpw --iscrypted $y$j9T$c7fw7aHlK3QrGWAy0Y/NC.a9$zHFiZgjt9zMAjPHmc17k9M1WjfF1yKeTF0R2QRaHnQ/

# Disk partitioning (critical fixes below)
clearpart --all --initlabel --drives=vda
ignoredisk --only-use=vda
#clearpart --none --initlabel

# Partition scheme (adjusted sizes)
part /boot --fstype="ext4" --ondisk=vda --size=1024 --asprimary
part /boot/efi --fstype="efi" --ondisk=vda --size=1024 --fsoptions="umask=0077,shortname=winnt"
part pv.111 --fstype="lvmpv" --ondisk=vda --size=409600 --grow --asprimary  # Reduced to 400GB

# LVM configuration
volgroup openeuler --pesize=4096 pv.111
logvol / --fstype="ext4" --size=204800 --name=root --grow --vgname=openeuler  # 200GB
logvol /opt/suzaku/data --fstype="xfs" --size=102400 --name=opt_suzaku_data --vgname=openeuler  # 100GB
logvol /var/lib/docker --fstype="xfs" --size=51200 --name=var_lib_docker --vgname=openeuler  # 50GB
```

其他配置
```
selinux --disabled
firewall --disabled

network --hostname=node1 --bootproto=static --ip=10.90.6.190 --netmask=255.255.255.0 --gateway=10.90.6.1 --nameserver=192.168.168.168

# Post-installation scripts
%post
mkdir -p /etc/docker
sed -i '/\/opt\/suzaku\/data/ s/defaults /defaults,sync /' /etc/fstab
%end

# Reboot after installation
reboot
```

Installation Destination kickstart infulicent
=> 硬盘太小了，kickstart配置的分区格式至少要更大的空间才行!
  => 使用ctrl+alt+F2进入shell模式, 看看日志文件? /tmp/anaconda.log

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

uefi启动项, grub.conf => 验证成功
```
set timeout=60
menuentry 'Install Ubuntu 20.04 Desktop' {
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

## pxe安装windows

=> 未尝试成功，暂放弃, 暂时可以使用dd到硬盘上的方式pxe安装windows

[一步步搭建PXE网络装机](https://yunfwe.cn/2018/06/03/2018/%E4%B8%80%E6%AD%A5%E6%AD%A5%E6%90%AD%E5%BB%BAPXE%E7%BD%91%E7%BB%9C%E8%A3%85%E6%9C%BA/)

Windows 系统的安装需要一个 WinPE 的安装环境，先通过网络引导启动 WinPE，然后在 WinPE 环境中安装 Windows 镜像。

还记得之前和 pxelinux.0 同一目录的 memdisk 文件吧，这通过这个文件可以将 iso 镜像加载到内存中启动，就利用这个方式来启动 WinPE 镜像。

```
label Install windows for vmware (WinPE)
    menu label Install Windows for vmware (WinPE)
    kernel memdisk
    append initrd=/windows/win8pe.iso ksdevice=bootif raw iso
```

进入 WinPE 桌面环境后连接到服务端的 Samba 共享目录，然后执行 Windows 系统安装镜像中的 setup.exe

=> 暂未下载到合适的winpe带网络的iso文件
下载winpe.iso: https://www.ithome.com/0/255/784.htm

关键字《winpe iso下载》

http://www.downcc.com/k/winpe/
 
## ubuntu部署pxe服务环境

```
# 安装dnsmasq和http服务
sudo apt install -y dnsmasq apache2
# pxe安装ubuntu 20.04, 需要nfs服务
sudo apt install -y nfs-kernel-server nfs-common
```

## docker部署pxe服务器

[dreamcat4/pxe](https://hub.docker.com/r/dreamcat4/pxe)
https://github.com/dreamcat4/docker-images/tree/master/pxe
=> 这个镜像提供了tftp, ipxe, http服务，以及有pxe配置示例

里面没有dhcp，只有dhcp proxy
```
docker run --cap-add NET_ADMIN -d dreamcat4/pxe
```

https://github.com/dreamcat4/docker-images/issues/33
```
docker run  -v "/var/pxe:/pxe" -e pxe_nic="eth1" --net host dreamcat4/pxe /bin/sh
```

## ipxe命令行引导系统

https://ipxe.org/cmd/ifstat

按`Ctrl-B`进入ipxe command line模式
help 命令, 获取所有命令
config 命令, 配置变量，ip地址, 掩码, 网关等
ifopen 命令启用网卡, route命令检查网卡是否open

config命令设置额外几个变量, 以及sanboot命令启动系统
```
set initiator-iqn iqn.2022-3.org.freenas.ctl:${mac}
set root-path iscsi:1.2.3.4::::iqn.2005-10.org.freenas.ctl:ubuntu-desktop
set keep-san 1
sanboot ${root-path}
```

## FAQ

#### dracut-initque timeout

可能是repo参数不对。。。 openeuler就是跟centos7不一样，需要配置inst.repo=xxx

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
