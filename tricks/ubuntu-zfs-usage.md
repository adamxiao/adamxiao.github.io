# ubuntu zfs使用

安装
```
apt install zfsutils-linux
```

列觉池
```
zpool list
```

zpool import -N -f 'boot-pool'

[ZFS on Ubuntu](https://zhouyuqian.com/2021/04/02/zfs/)

查看存储池列表
```
zfs list
```

查看存储池的状态信息
```
zpool status data1
```

显示 ZFS 存储池命令历史记录 `zpool history`

#### 概念

[(好,全)在Linux上安装和使用ZFS](https://www.escapelife.site/posts/caf259ea.html)

ZFS 非常的优秀，这是一个真正现代的文件系统，内置的功能对于处理大量的数据很有意义。现在，如果您正在考虑将 ZFS 用于您的超高速 NVMe SSD，这可能不是一个最佳选择。 它比别的文件系统要慢，不过，这完全没有问题， 它旨在存储大量的数据并保持安全。

ZFS 消除了建立传统 RAID 阵列(独立磁盘冗余阵列)的需要。 相反，您可以创建 ZFS 池，甚至可以随时将驱动器添加到这些池中。ZFS 池的行为操作与 RAID 几乎完全相同，但功能内置于文件系统中。
ZFS 也可以替代 LVM(逻辑盘卷管理)，使您能够动态地进行分区和管理分区，而无需处理底层的细节，也不必担心相关的风险。
这也是一个 CoW(写时复制)文件系统。 这里不会提及太多的技术性，这意味着 ZFS 可以保护您的数据免受逐渐损坏的影响。 ZFS 会创建文件的校验和，并允许您将这些文件回滚到以前的工作版本。

[1] ZFS 使其受欢迎的特性是：

- 数据完整性 —— 数据一致性和完整性通过即写即拷和校验技术保证。
- 存储空间池 —— 可用存储驱动器一起放入称为 zpool 的单个池。
- 软件 RAID —— 像发出一个命令一样，建立一个 raidz 数组。
- 内置的卷管理器 —— ZFS 充当卷管理器。
- Snapshots、克隆、压缩 —— 这些都是一些 ZFS 提供的高级功能。

[2] ZFS 的常用的术语：

- Pool
  存储驱动器的逻辑分组，它是 ZFS 的基本构建块，从这里将存储空间分配给数据集。
- Datasets
  ZFS 文件系统的组件即文件系统、克隆、快照和卷被称为数据集。
- Mirror
  一个虚拟设备存储相同的两个或两个以上的磁盘上的数据副本，在一个磁盘失败的情况下,相同的数据是可以用其他磁盘上的镜子。
- Resilvering
  在恢复设备时将数据从一个磁盘复制到另一个磁盘的过程。
- Scrub
  擦除用于一致性检验在 ZFS 像在其他文件系统如何使用 fsck。

#### 创建池

[如何在 Ubuntu 上使用 ZFS 文件系统](https://zhuanlan.zhihu.com/p/33833767)

```
zpool create new-pool raidz1 /dev/sdb /dev/sdc /dev/sdd
```

池的种类
- raid0
  RAID0 只是把你的硬盘集中到一个池子里面，就像一个巨大的驱动器一样。 它可以提高你的驱动器速度，（LCTT 译注：数据条带化后，并行访问，可以提高文件读取速度）但是如果你的驱动器有损坏，你可能会失丢失数据。
  要使用 ZFS 实现 RAID0，只需创建一个普通的池。
  `sudo zpool create your-pool /dev/sdc /dev/sdd`
- raid1
  在 ZFS 中使用 mirror 关键字来实现 RAID1 功能
  `sudo zpool create your-pool mirror /dev/sdc /dev/sdd`
- raid5/raidz1
  ZFS 将 RAID5 功能实现为 RAIDZ1。 RAID5 要求驱动器至少是 3 个。并允许您通过将备份奇偶校验数据写入驱动器空间的 1/n（n 是驱动器数），留下的是可用的存储空间。
  `sudo zpool create your-pool raidz1 /dev/sdc /dev/sdd /dev/sde`
- raid6/raidz2
  RAID6 与 RAID5 几乎完全相同，但它至少需要四个驱动器。 它将奇偶校验数据加倍，最多允许两个驱动器损坏，而不会导致阵列关闭
  `sudo zpool create your-pool raidz2 /dev/sdc /dev/sdd /dev/sde /dev/sdf`
- raid10（条带化镜像）
  RAID10 旨在通过数据条带化提高存取速度和数据冗余来成为一个两全其美的解决方案。 你至少需要四个驱动器，但只能使用一半的空间。
  `sudo zpool create your-pool mirror /dev/sdc /dev/sdd mirror /dev/sde /dev/sdf`

[Linux ubuntu系统使用zfs记录](https://www.cnblogs.com/cjdty/p/16813040.html)

创建zfs池
```
zpool create -f pool2 /dev/sda -m /export
```
这样就能把/dev/sda 作为zfs分区，然后挂载到/export目录

查看开启去重的分区
```
zfs get dedup pool1
```

设置开启去重
```
zfs set dedup=on pool1
```

#### 快照管理

创建快照
```
sudo zfs snapshot data_ar@v01
```

备份zpool快照
```
zfs send data_ar@v01 | gzip > /mnt/d/backupfile.gz
```

修改挂载点
```
sudo zfs set mountpoint=/myspecialfolder mypool
```

获取挂载点
```
zfs get mounted data1/nfs
```

覆盖挂载
```
zfs cannot mount 'xxx': directory is not empty
sudo zfs set overlay=on data1/adam-backup
```

https://serverfault.com/questions/340837/how-to-delete-all-but-last-n-zfs-snapshots
快照列举, 以及批量删除
```
zfs list -t snapshot -o name | grep ^tank@Auto | tac | tail -n +16 | xargs -n 1 zfs destroy -r
```

可以看到空的snap(USED=0)? 然后删除掉?
```
zfs list -t all
```

https://docs.oracle.com/cd/E36784_01/html/E36835/gbcya.html
查看保留的快照?
```
zfs holds -r tank/home@now
```

zfs获取快照的自动删除属性
```
zfs get com.sun:auto-snapshot poolname
```

获取dataset的属性
```
zfs get all tank/home
```

#### 快照定时创建和删除

关键字《zfs快照定时删除》

https://blog.vgot.net/archives/zfsnap.html
=> 未验证
```
# Auto ZFS Snapshot
0	*/8	*	*	*	root	zfsnap snapshot -v -a 1w tank/docs >> /var/log/zfsnap.log
0	18	*	*	1-5	root	zfsnap snapshot -v -a 1w tank/public >> /var/log/zfsnap.log
0	23	*	*	*	root	zfsnap destroy -rv tank >> /var/log/zfsnap.log
```

#### 加密存储数据

[在Ubuntu Server上使用ZFS加密存储数据](https://im.salty.fish/index.php/archives/using-zfs.html)

开机自动挂载ZFS分区

chatgpt: zfs命令行创建加密文件系统

```
sudo zfs create -o encryption=aes-256-gcm -o keyformat=passphrase data1/enc1
=> 然后输入密码, 居然自动创建，并且挂载了。。。
sudo zfs list
下次开机可以再导入存储池, 挂载这个文件系统
sudo zpool import -N -f 'data1'
sudo zfs load-key data1/enc1 # 解密
sudo zfs mount data1/enc1
```

#### 用loopback虚拟硬盘测试 zfs

关键字《使用loop文件制作zfs分区》

https://wuli.wiki/online/ZFS.html

```
创建一个 500MB 虚拟硬盘文件
dd if=/dev/zero of=adam.bin bs=1M count=500
制作 loopback 设备
sudo losetup -fP --show adam.bin # 会返回设备路径如 /dev/loop0
创建zfs数据池
sudo zpool create data1 /dev/loop0
```

#### zfs zvol copy

https://www.truenas.com/community/threads/how-to-copy-zvol-to-new-pool.107395/
```
zfs send oldpool/path/to/zvol | zfs receive newpool/path/to/zvol
zfs send vmhd2/win2016 | zfs recv vmhd2/win2016T2
```

#### ZFS优缺点

[zfs文件系统优缺点](https://juejin.cn/s/zfs%E6%96%87%E4%BB%B6%E7%B3%BB%E7%BB%9F%E4%BC%98%E7%BC%BA%E7%82%B9)

- 消耗内存
- 某些情况性能略低
- 配置管理复杂

优点:
- 数据完整性：ZFS以数据完整性为重点，采用了强大的校验和机制，以检测和修复数据损坏。
- 快照和克隆：ZFS具有出色的快照和克隆功能，可以轻松创建、回滚和管理文件系统的快照。
- 可扩展性：ZFS支持非常大的存储容量，可以轻松地添加新的存储设备并扩展存储池的容量。
- 高级功能：ZFS提供了许多高级功能，如RAID-Z数据保护、数据压缩、数据加密等。

https://m.mysmth.net/article/DigiHome/324896?p=4

## FAQ

#### cannot import 'boot-pool': one or more devices is read only

```
zpool import -N -f 'boot-pool'
cannot import 'boot-pool': one or more devices is read only
```

```
zpool import -o readonly -F -R /mnt boot-pool
zpool import -o readonly -N -f 'boot-pool'
zpool import -V -o readonly -N -f 'boot-pool'
```

#### 坏一个bit问题

https://blog.csdn.net/weixin_36165751/article/details/116901431
现在zfs给人的印象是：我一个bit都不会错，于是大家觉得太适合存储宝贵的照片、文档之类的宝贝了。可是不用ecc内存电话，还有后半句呢：要错我就全错光片甲不留啊……

## 其他

```
/sbin/zpool import -N -f 'boot-pool'
one or more devices is read only
```

```
sdb         zfs_member boot-pool 16672127188688975952
├─sdb1
├─sdb2      vfat       EFI       4607-0C18
└─sdb3      zfs_member boot-pool 16672127188688975952
```

