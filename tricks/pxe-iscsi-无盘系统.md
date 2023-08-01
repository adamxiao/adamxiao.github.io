# pxe iscsi 无盘系统

关键字《pxe iscsi》《pxe iscsi无盘启动》

[PXE打造ISCSI 无盘系统ESXI WINPE Debian11安装盘配合TrueNAS SCALE 安装教程](https://www.truenasscale.com/2022/03/06/761.html)
=> 原理就是使用ipxe安装，启动windows，debian系统
=> 使用truenas配置iscsi硬盘, http, tftp等服务
下载了相关文件: https://cloud.189.cn/web/share?code=q2EJvyYJJBVf（访问码：kk56）

- ipxe.efi 是uefi启动
undionly64.kpxe是bios启动

https://www.wunote.cn/article/4986/
本教程仅供参考，有些地方需要自己会随机应变，比如你的电脑比较新，那么就无需ipxe.pxe文件启动，可采用链式启动；你的网卡不是小螃蟹的，就不需要处理小螃蟹驱动的问题

[从无盘启动看Linux启动原理](https://zhuanlan.zhihu.com/p/270269074)

编译时添加 EMBED={脚本名称} 可以关联一个启动脚本。推荐一个大佬做好的脚本 http://boot.netboot.xyz/menu.ipxe 可以直接使用。
```
git clone git://git.ipxe.org/ipxe.git
cd ./ipxe/src
wget http://boot.netboot.xyz/menu.ipxe
make bin-i386-pcbios/ipxe.pxe EMBED=menu.ipxe
```

[Tiny pxe网络启动–远程安装、维护系统](https://www.cnblogs.com/python-learn/p/16746636.html)

Tiny PXE Server是一款小巧而功能强大的网络系统启动软件，支持DHCP/TFTP/HTTP/BINL/DNS等多个协议，支持grub4dos,pxelinux,ipxe等多个引导器，支持从PXE/gPXE/IPXE启动，支持http协议启动或传输文件。

Tiny PXE Server下载地址：http://erwan.labalec.fr/tinypxeserver/pxesrv.zip

[PXE+ISCSI＝无盘！玩转ＮＡＳ进阶篇(图文教程，附资源）部分](https://blog.ggrarea.cn/archives/11006.html)

首先下载我网盘上的引导文件
http://pan.baidu.com/s/1ntpxMKp
```
#!ipxe
   set menu-timeout 5000
   set menu-default WINDOWS
   isset ${ip} || dhcp

:start
  menu iPXE Boot Menu
  item --gap --             --------------------------------- WIN --------------------------------
  item WINDOWS                 BOOT WINDOWS(ISCSI)
  item install                 install windows to ISCSI
  item --gap --             ---------------------------- Advanced options -----------------------
  item --key c config       Configure settings                                   -- c
  item --key r reboot               reboot computer                              -- r
  item --key x exit         Exit iPXE and continue BIOS boot                     -- x
  choose --timeout ${menu-timeout} --default ${menu-default} selected
  goto ${selected}

:reboot
  reboot

:exit
  exit

:config
  config
  goto start

:WINDOWS
  sanboot iscsi:192.168.0.218::::iqn.win8

:install
  sanhook iscsi:192.168.0.218::::iqn.win8
  exit
```

https://discourse.ubuntu.com/t/installation-iscsi/11321

=> 关键就是
```
iPXE> dhcp
Configuring (net0 52:54:00:a4:f2:a9)....... ok
iPXE> sanboot iscsi:192.168.1.29::::iqn.2016-03.TrustyS-iscsitarget:storage.sys0
```
=> sanboot iscsi:10.90.3.25::::iqn.2005-10.org.freenas.ctl:ubuntu1

https://www.wunote.cn/article/4986/
理解chain...
```
#!ipxe
dhcp
chain --autofree http://172.16.1.4:8080/ipxe/boot.ipxe
# 注意，此处URL替换为你刚刚创建的Web服务器地址
```

set iscsi-server 172.16.1.4 #修改为你的iSCSI服务器IP，也就是你群晖的IP

在其中配置你iSCSI的IQN和CHAP认证的账户名密码
```
#!ipxe
set username test #CHAP认证的账户名
set password ttttttttt123 #CHAP认证的密码
set iscsi-iqn iqn.2000-01.com.synology:DiskStation-3.Target-1.35355  #iSCSI的IQN
```

## ipxe入门

[ipxe官网](https://ipxe.org/)

- boot from a web server via HTTP
- boot from an iSCSI SAN
- boot from a Fibre Channel SAN via FCoE
- boot from an AoE SAN
- boot from a wireless network
- boot from a wide-area network
- boot from an Infiniband network
- control the boot process with a script

https://www.jianshu.com/p/f9070d76892a

dhcp option配置，以dnsmasq配置文件格式为示例:
```
dhcp-match=set:bios,option:client-arch,0
dhcp-match=set:x64-uefi,option:client-arch,7
dhcp-match=set:x64-uefi,option:client-arch,9
dhcp-match=set:aarch64-uefi,option:client-arch,11
dhcp-match=set:ipxe,175

dhcp-boot=tag:x64-uefi,ipxe-x86_64.efi
dhcp-boot=tag:bios,undionly.kpxe
dhcp-boot=tag:aarch64-uefi,ipxe-x86_64.efi
dhcp-boot=tag:ipxe,boot.ipxe
```

ipxe启动原理：
网卡在进行pxe启动时会进行第一次dhcp请求，并附带client-arch选项。
- 如果系统使用普通bios模式启动，那么client-arch就是0；
- 如果是x86 uefi启动，就是7或者9；
- 如果是arm64 uefi启动，就是11。

dnsmasq会给为请求打上tag，例如dhcp-match=set:x64-uefi,option:client-arch,7，如果发现请求有这个tag，就推送对应的启动文件，
例如dhcp-boot=tag:aarch64-uefi,ipxe-x86_64.efi。此时，主机就会使用tftp协议去下载ipxe，并且执行。

当ipxe开始运行后，ipxe会再次进行dhcp请求，并且带上参数175。dnsmasq收到这个请求后，会推送boot.ipxe，就是下面这两行：
```
dhcp-match=set:ipxe,175 dhcp-boot=tag:ipxe,boot.ipxe
```
而boot.ipxe就是ipxe的主配置文件。boot.ipxe里面还会引用其他配置文件，ipxe也将一一加载。
至此，ipxe已经成功加载并且获取到了配置文件。

[iPXE的使用](https://www.twblogs.net/a/5bb2a7012b71770e645e0a59/?lang=zh-cn)
加入ipxe指定的一些参数（http://ipxe.org/howto/dhcpd）。这些参数对于传统的dhcp服务是不识别的，所以放心加吧，不会对dhcp服务有其他影响。


https://t17.techbang.com/topics/50767-build-a-remote-boot-system-using-synology-nas-ipxe-part-ii-install-and-start-ubuntu-linux-on-an-iscsi-disk
=> 可以安装，启动, 在ISCSI硬盘上

winpe的安装到iscsi硬盘上配置?
```
:winpe-install
echo Booting Windows PE ${arch} installer for ${initiator-iqn}
echo (for installing Windows)
set base-url http://${nas_ip}/Install/WinPE
cpuid --ext 29 && set arch amd64 || set arch x86
kernel wimboot
initrd ${base-url}/${arch}/media/Boot/BCD BCD
initrd ${base-url}/${arch}/media/Boot/boot.sdi boot.sdi
initrd ${base-url}/${arch}/media/sources/boot.wim boot.wim
set netX/gateway ${iscsi-server}
set root-path ${base-iscsi}:${hostname}.Windows
sanhook ${root-path} || goto failed
boot || goto failed
goto start
```

关键字《boot ubuntu from iSCSI》


#### 修改menu.ipxe配置文件

```
#!ipxe

# Variables are specified in boot.ipxe.cfg

# Some menu defaults
# set menu-timeout 0 if no client-specific settings found
set menu-timeout 0 
isset ${menu-timeout} || set menu-timeout 10000
set submenu-timeout ${menu-timeout}
isset ${menu-default} || set menu-default exit

# Figure out if client is 64-bit capable
cpuid --ext 29 && set arch x64 || set arch x86
cpuid --ext 29 && set archl amd64 || set archl i386

######################   ENV   ##############################

set SAN_IP 10.10.3.1 # http服务器的ip地址

###################### MAIN MENU ####################################

:start
menu iPXE boot menu for ALL

item --gap --              ------------------------- Linux ------------------------------
menu Diagnostic tools
item CentOSInstall          CentOS install
# item 启动项   启动项说明

item --gap --              ------------------------- Windows PE ------------------------------
item HiPEX64                Boot from HiPEX64.wim
item --gap --              ------------------------- Advanced options -------------------------------
item Mt86p_UEFI            UEFI Boot from mt86plus_64.iso
item reboot                Reboot computer
item --key x exit          Exit iPXE and continue BIOS boot
choose --timeout ${menu-timeout} --default ${menu-default} selected || goto cancel
set menu-timeout 0
goto ${selected}

############### Other tools   #########################
:Mt86p_UEFI                                            
set Mt86p_URL http://${SAN_IP}/mt86plus_64.iso                                              
sanboot ${Mt86p_URL} || goto failed                                                                  
goto start                          

#########  Windows PE ITEMS ############

:HiPEX64
kernel wimboot
initrd http://${SAN_IP}/HiPEX64/BCD
initrd http://${SAN_IP}/HiPEX64/boot.sdi
initrd http://${SAN_IP}/HiPEX64/HiPEX64.wim
boot || goto failed
goto start

###################### Linux  #############################
# 一个item的具体定义如下：冒号后面必须跟启动项名称
:CentOSInstall
echo Starting CentOS Install ${archl} for ${initiator-iqn}
cpuid --ext 29 && set arch amd64 || set arch x86
set base-url http://${SAN_IP}/centos7
kernel ${base-url}/images/pxeboot/vmlinuz inst.repo=${base-url}/ initrd=initrd.img
initrd ${base-url}/images/pxeboot/initrd.img
boot || goto failed
goto start
```

## 无盘启动系统

https://learn.microsoft.com/en-us/answers/questions/599494/how-do-i-create-a-diskless-windows-10-pc-booting-f
=> 系统如果有支持iscsi的网卡，则任意系统都能支持无盘iscsi启动了!

## ubuntu ipxe iscsi启动

关键字《iscsi ipxe启动ubuntu》

https://blog.csdn.net/JourneyBean/article/details/105547860
nfs共享启动...(还有iscsi, samba, ftp等共享盘启动?)

配置iPXE启动菜单
```
:Ubuntu_18_04_02
  set server_ip 192.168.1.123
  set nfs_path /path/to/ubuntu/rootfs
  kernel nfs://${server_ip}${nfs_path}/vmlinuz || read void
  initrd nfs://${server_ip}${nfs_path}/initrd.img || read void
  imgargs vmlinuz initrd=initrd.img root=/dev/nfs netboot=nfs nfsroot=${server_ip}:${nfs_path} ip=dhcp splash quiet -- || read void
  boot || read void
```

关键字《iscsi boot ubuntu》

=> 验证成功，虚拟机和物理服务器都行, 参考了如下两篇文章!!!

[(好)How to Configure Synology NAS for Diskless Booting Ubuntu 22.04 LTS via iSCSI and iPXE](https://linuxhint.com/configure-synology-nas-iscsi-ipxe/#post-186660-_Toc104626544)

Configuring Ubuntu Desktop 22.04 LTS to Boot From iSCSI Disk
=> 关键还需要配置，在引导节点连接了iscsi硬盘，ubuntu系统启动后还需要继续连接!

```
export dir=/media/adam
mount /dev/sdb1 $dir
mount /dev/sdb15 $dir/boot/efi/
mount -t proc proc $dir/proc/
mount -t sysfs sys $dir/sys/
mount -o bind /dev $dir/dev
mount -t devpts pts $dir/dev/pts

umount $dir/dev/pts
umount $dir/dev
umount $dir/sys
umount $dir/proc
umount $dir/boot/efi
umount $dir
```

```
apt install -y open-iscsi
可选配置iscsi客户端名称? /etc/iscsi/initiatorname.iscsi 
```

To automatically mount the iSCSI target `iqn.2022-05.com.linuxhint:pc-01-target` at boot time, create a new file `/etc/iscsi/iscsi.initramfs` and open it with the nano text editor as follows:

Set the variables ISCSI_INITIATOR, ISCSI_TARGET_NAME, and ISCSI_TARGET_IP in the iscsi.initramfs file. Once you’re done, press <Ctrl> + X followed by Y and <Enter> to save the iscsi.initramfs file.

NOTE: Here, ISCSI_INITIATOR is a unique IQN for the iSCSI client program. Set it to the same IQN as you’ve set on the /etc/iscsi/initatorname.iscsi configuration file. ISCSI_TARGET_NAME is the IQN of the iSCSI target of your Synology NAS that you want to log in to. ISCSI_TARGET_IP is the IP address of your Synology NAS. If you need an in-depth explanation of these iSCSI terms, read the article [Configure iSCSI Storage Server on Ubuntu 18.04 LTS](https://linuxhint.com/iscsi_storage_server_ubuntu/).
```
ISCSI_INITIATOR=iqn.1993-08.org.debian:01:e0b4a87655f9
ISCSI_TARGET_NAME=iqn.2005-10.org.freenas.ctl:ubuntu1
ISCSI_TARGET_IP=10.90.3.25
```

最后还需要更新initramfs
```
update-initramfs -u
```

[How to create an bootable iSCSI target with Linux as Operating System?](https://github.com/intel/intelRSD/issues/26#issuecomment-311656769)
=> 验证成功
- 1.Install Ubuntu 16.04 Server on a VM (in BIOS Legacy mode for remote booting via iPXE, or UEFI mode for iSCSI Out of Band)
- 2.Start the VM and switch in it to a root account
- 3.Install packages for iSCSI:
```
apt-get install open-iscsi initramfs-tools
```
- 4.Include iSCSI in list of modules:
```
echo "iscsi" >> /etc/initramfs-tools/modules
```
- 5.Enable automatic iSCSI connection in initramfs:
```
echo "ISCSI_AUTO=true" > /etc/iscsi/iscsi.initramfs
```
- 6.Run initramfs update:
```
update-initramfs -u
```
- 7.Shutdown the VM and convert it to a raw format image
- 8.Copy the image to your base logical volume

### ubuntu UEFI和BIOS双启动

关键字《配置uefi安装的ubuntu能够bios启动》

[BIOS/UEFI双引导U盘安装Ubuntu](https://maxwell-lyu.github.io/2021/02/13/Tech-20210213-Ubuntu%E5%8F%8C%E5%90%AF%E5%8A%A8/)

使用GPT分区表, 预留bios_grub分区, 先进行UEFI引导下的安装, 之后添加BIOS引导

使用iso安装时，try ubuntu, 开始自定义分区:
=> 可以参考官方ubuntu20.04 cloud image的分区方法: `fdisk -l`
```
Device      Start       End   Sectors  Size Type
/dev/vda1  227328 209715166 209487839 99.9G Linux filesystem
/dev/vda14   2048     10239      8192    4M BIOS boot
/dev/vda15  10240    227327    217088  106M EFI System
```

重启虚拟机， 安装BIOS启动引导
```
grub-install --target=i386-pc --boot-directory=/boot /dev/sda
```

虚拟机应当成功引导进入Ubuntu桌面, 执行下面的命令, 以验证当前的引导类型
```
ls /sys/firmware/efi # 若成功执行, 说明为UEFI引导; 若提示找不到文件, 则为BIOS引导
```


## centos pxe iscsi启动

=> 不行

关键字《centos boot from iscsi》

在youtube上搜到教程, 但是/boot分区
https://www.youtube.com/watch?v=BxWCjf9hjwc&ab_channel=AndroidandTechSolutions

## windows pxe iscsi启动

youtube关键字《boot windows 10 from iscsi》

https://www.youtube.com/watch?v=_elwqBKIlLI&ab_channel=RetroTechChris

其实最后就是下载了别人构建好的windows镜像，就可以iscsi无盘启动了, 自己的win10镜像不行，估计还需要配置些东西!!!
=> 而且也是bios启动, 没有efi分区 => 原来下载的是bios镜像

windows无盘启动镜像下载: https://www.ccboot.com/super-image.htm

CCBoot功能简介
通过CCBoot可以让服务器实现Windows系列多款操作系统的无盘启动，CCBoot内置DHCP、gPXE、TFTP、镜像上传、和iSCSI Target 功能，iSCSI 启动的All-in-one解决方案。

#### 构建windows无盘镜像

关键字《build diskless windows image》

[Windows 10 - 11 installation on a iSCSI target #324](https://github.com/ipxe/ipxe/discussions/324)
=> 没啥收获

[CCBoot - Create Boot Image](https://www.ccboot.com/wiki-creating-boot-image.htm)
=> 使用CCBoot配置无盘启动服务器...
Note: If the uploaded image doesnot boot good or has long boot time then try our super image instead. 
但是里面提到使用vmware创建boot image: 4) Install the CCBoot Client software and then restart.

[CCBoot - Using VMware to Create Boot Image](https://www.ccboot.com/wiki-create-ccboot-image-using-vmware.htm)
- 1) Install VMware Workstation on a computer.
- 2) Create a virtual machine in VMware.
- 3) Install Windows system in the virtual machine, named it as "Windows 7 x64" and optimize the system if it’s necessary.
- 4) Install the CCBoot Client software and then restart.
- 5) Shutdown virtual machine.

[CCBoot - Create Boot Image](https://www.ccboot.com/wiki-creating-boot-image.htm)
[CCBoot - Standard Method to Create Boot Image for Legacy PCs](https://www.ccboot.com/wiki-standard-method-for-creating-image.htm)

## 编译ipxe

官方文档: https://ipxe.org/download

https://www.lategege.com/?p=716

作为无盘引导的核心技术就是IPXE了，ipxe官网地址：https://ipxe.org/

基于ubuntu 20.04
```
安装依赖包
apt install gcc binutils make perl liblzma-dev mtools mkisofs syslinux
下载源码编译
git clone git://git.ipxe.org/ipxe.git    
make bin/undionly.kpxe
```

因为ipxe是一个固件，所以编译后它的实体有很多种类型，有iso、usb格式的(刷入u盘的)，rom格式的(刷入网卡芯片)，有通过pxe传统链式引导的就是上面的undionly.kpxe，有用于efi引导的ipxe.efi，这些全部都是ipxe固件，只是格式不同而已，我采用的是传统引导并且通过PXE进入ipxe，所以要编译成undionly.kpxe，详细的编译编译方式参考ipxe官网：https://ipxe.org/download

只要群晖开启tftp,将编译成的undionly.kpxe传入tftp根目录，爱快dhcp两个字段配置好，局域网中同网段的主机开启pxe启动后就会获取到tftp服务器地址和启动文件名，从而进入ipxe环境。

补充：如果你的虚拟机或者物理机选择了uefi启动模式，那么你的ipxe需要编译成ipxe.efi，make bin-x86_64-efi/ipxe.efi，此时，爱快option67就要根据ipxe.efi这个名称去填写了。

## 网启菜单的编写

http://bbs.c3.wuyou.net/archiver/?tid-424838.html&page=1

TODO:

#### 使用ipxe安装ubuntu

关键字《ubuntu install use ipxe》

https://gist.github.com/robinsmidsrod/21a15a562bc45d4ce25dcde507fb3100
配置nfs服务器，然后启动ubuntu desktop live os
```
set nfs-server          ${next-server}
set nfs-mountpt         /srv/nfs
set nfs-root-boot      nfs://${nfs-server}/${nfs-mountpt}/ubuntu2004/
set nfs-root-linux      ${nfs-server}:${nfs-mountpt}/ubuntu2004/

:ubuntu2004_live
kernel ${nfs-root-boot}/vmlinuz
initrd ${nfs-root-boot}/initrd
imgargs vmlinuz initrd=initrd nfsroot=${nfs-root-linux} netboot=nfs boot=casper ip=dhcp
boot
goto start
```

使用如下menu配置，验证成功
```
:ubuntu2-install
set base-url http://10.90.3.25:9080/ubuntu2004
kernel ${base-url}/vmlinuz
initrd ${base-url}/initrd
imgargs vmlinuz initrd=initrd ip=dhcp boot=casper netboot=nfs nfsroot=10.90.3.25:/mnt/pool1/pxe/ubuntu2004/ splash toram ---
boot || goto failed
goto start
```

## 其他资料(未验证)

[Arch Linux iSCSI/Boot](https://wiki.archlinux.org/title/ISCSI/Boot)
Arch Linux can be installed on an iSCSI target.

关键字《centos boot from iscsi target》《centos boot from iscsi lun》

[CentOS iSCSI Disks](https://docs.centos.org/en-US/centos/install-guide/iSCSI/)
https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/installation_guide/sect-iscsi-disks-startup


https://forums.centos.org/viewtopic.php?t=71900
I can install CentOS to an iSCSI volume, no issue. But I am unsure how to boot into the installation. My computer does not support configuring iscsi in the bios, so I am unable to use the ibft boot table.

## FAQ

#### Could not open SAN device: Error 0x3232094

需要新版本的ipxe, 更新之后确实可以了!!!(自己编译的)

未知错误?
https://ipxe.org/err/3232094

#### Could not open SAN device: No such device

iqn没有被允许访问target lun

在iPXE上使用命令查询自己的iqn: echo ${initiator-iqn}

原来是配置文件中使用hostname作为iqn后缀导致的... => dhcp给这个主机分配了hostname了。。。
```
boot.ipxe.cfg:isset ${hostname} && set initiator-iqn ${base-iqn}:${hostname} || set initiator-iqn ${base-iqn}:${mac}
```

#### window10 bios系统起不来

windows过一会就转圈圈，iscsi就没有连接了

我的虚拟机内存配置为4g，一直转圈圈, 改为8g内存可以了?
=> 还是不行，ksvd的虚拟机就行。。。ubuntu 20.04的virt虚拟机不行?

#### Security Violation

UEFI固件换一下就好了
```
	<loader readonly='yes' type='rom'>/usr/share/OVMF/OVMF_CODE-pure-efi.fd</loader>
```
