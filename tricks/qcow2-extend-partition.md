# qcow2磁盘分区扩容

lvm-usage中也有一部分

关键字《centos qcow2 分区增大》
https://opengers.github.io/openstack/openstack-instance-disk-resize-and-convert/
```
#我们把40G加到分区2上     
#growpart /dev/vda 2
CHANGED: partition=2 start=33556480 old: size=50329600 end=83886080 new: size=134210315,end=167766795

#然后扩容分区2文件系统    
#xfs_growfs /
```

## centos7 qcow2镜像根分区扩容

加大磁盘
```
qemu-img resize centos7.img +10G
```

## ubuntu 20.04 server扩容分区

```
pvresize /dev/vda3
lvextend -L +100G /dev/mapper/ubuntu--vg-ubuntu--lv
resize2fs /dev/mapper/ubuntu--vg-ubuntu--lv
```

## ubuntu 缩小分区

**注意: 使用livecd进入系统，缩容分区，防止数据丢失**
**注意: 磁盘分区的UUID可能会改变，需要通过blkid命令来查看，并相应地更改/etc/fstab配置文件中指定的/home分区的UUID**

[Ubuntu缩小磁盘分区大小](https://www.bwangel.me/2016/07/17/ubuntu%E7%BC%A9%E5%B0%8F%E7%A3%81%E7%9B%98%E5%88%86%E5%8C%BA%E5%A4%A7%E5%B0%8F/)
=> 验证失败, 系统起不来...

- 1.通过resize2fs调整文件系统大小
- 2.通过parted调整磁盘分区大小

调整文件系统大小
```
e2fsck -f /dev/sda5 # 首先检查分区文件系统
resize2fs /dev/sda5 4G # 缩容ext4分区
```

调整分区大小
```
parted /dev/sda
(parted) resizepart 5 5G
```

还可以通过gui工具调整? GParted => 能缩小分区验证系统正常，但是qcow2镜像缩小就有问题?
[ubuntu20调整分区大小的方法](https://blog.csdn.net/weixin_45464501/article/details/118727120)

最后还可以缩容qcow2镜像 => 缩就报错系统起不来!
```
qemu-img resize --shrink  new.img 70G
```

关键字《qcow2缩容》

最好还是使用`virt-resize --shrink` => 未验证成功

[缩减镜像 virtual size 记](http://wsfdl.com/openstack/2018/07/04/shrink_image_virtual_size.html)


https://zhuanlan.zhihu.com/p/408648931
=> 使用clonezilla => clonezilla 不支持大硬盘 到小硬盘的迁移 ???

关键字《Invalid argument during seek for read on》

[How to clone a GPT drive to a smaller drive?](https://bbs.archlinux.org/viewtopic.php?id=154057)

```
gdisk -l /dev/nbd0
GPT fdisk (gdisk) version 0.8.10

Warning! Disk size is smaller than the main header indicates! Loading
secondary header from the last sector of the disk! You should use 'v' to
verify disk integrity, and perhaps options on the experts' menu to repair
the disk.
Caution: invalid backup GPT header, but valid main header; regenerating
backup header from main header.

Warning! One or more CRCs don't match. You should repair the disk!

Partition table scan:
  MBR: protective
  BSD: not present
  APM: not present
  GPT: damaged

****************************************************************************
Caution: Found protective or hybrid MBR and corrupt GPT. Using GPT, but disk
verification and recovery are STRONGLY recommended.
****************************************************************************
Disk /dev/nbd0: 146800640 sectors, 70.0 GiB
Logical sector size: 512 bytes
Disk identifier (GUID): 561E7572-CEA1-4C94-B410-B829FF1BC4DF
Partition table holds up to 128 entries
First usable sector is 34, last usable sector is 209715166
Partitions will be aligned on 2048-sector boundaries
Total free space is 102404029 sectors (48.8 GiB)

Number  Start (sector)    End (sector)  Size       Code  Name
   1            2048         1050623   512.0 MiB   EF00  EFI System Partition
   2         1050624       107313151   50.7 GiB    8300
```

使用如下方法解决了, 使用gdisk进入专家模式，写入磁盘长度信息
```
┌─[11:07:09/starlancer/amadar/~]
└─╼ sudo gdisk /dev/sdb
[sudo] password for root: xxxxxxxxxxxx
GPT fdisk (gdisk) version 0.8.5

Warning! Disk size is smaller than the main header indicates! Loading
secondary header from the last sector of the disk! You should use 'v' to
verify disk integrity, and perhaps options on the experts' menu to repair
the disk.
Caution: invalid backup GPT header, but valid main header; regenerating
backup header from main header.

Warning! One or more CRCs don't match. You should repair the disk!

Partition table scan:
  MBR: protective
  BSD: not present
  APM: not present
  GPT: damaged

****************************************************************************
Caution: Found protective or hybrid MBR and corrupt GPT. Using GPT, but disk
verification and recovery are STRONGLY recommended.
****************************************************************************

Command (? for help): v

Caution: The CRC for the backup partition table is invalid. This table may
be corrupt. This program will automatically create a new backup partition
table when you save your partitions.

Problem: The secondary header's self-pointer indicates that it doesn't reside
at the end of the disk. If you've added a disk to a RAID array, use the 'e'
option on the experts' menu to adjust the secondary header's and partition
table's locations.

Problem: Disk is too small to hold all the data!
(Disk size is 312581808 sectors, needs to be 1465149168 sectors.)
The 'e' option on the experts' menu may fix this problem.

Identified 3 problems!

Command (? for help): x

Expert command (? for help): e
Relocating backup data structures to the end of the disk

Expert command (? for help): w

Final checks complete. About to write GPT data. THIS WILL OVERWRITE EXISTING
PARTITIONS!!

Do you want to proceed? (Y/N): y
OK; writing new GUID partition table (GPT) to /dev/sdb.
The operation has completed successfully.
```

## windows缩小分区

=> 最后还是在ubuntu livecd, 使用GParted缩小ntfs分区 => 验证可以正常使用

关键字《windows10 缩小分区》

开始-> 右键单击"计算机"->"管理"。 在左侧的"存储"下找到"磁盘管理"，并单击以选择"磁盘管理"。 右键单击要剪切的分区，然后选择"收缩卷"。 在"输入要缩小的空间量"的右侧调整大小。
