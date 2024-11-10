# fstrim使用

缩小guest.qcow2镜像大小

#### fstrim实现原理

《fstrim实现原理》

fstrim 是一个用于 TRIM 操作的 Linux 命令，它用于通知文件系统底层存储设备回收闲置的块，以提高性能和延长固态硬盘（SSD）的寿命。fstrim 命令是与底层存储设备通信的用户空间工具，它并不直接执行 TRIM 操作，而是发送 TRIM 操作请求给文件系统和存储设备驱动程序。

具体来说，fstrim 的实现原理如下：

1. 文件系统支持：首先，文件系统需要支持 TRIM 操作。常见的文件系统如 ext4、XFS、Btrfs 等都支持 TRIM。文件系统会在内部维护一个闲置块列表，TRIM 操作通知底层存储设备将这些闲置块标记为可用。

2. fstrim 命令执行：当你执行 fstrim 命令时，它会遍历指定的文件系统，并计算出哪些文件和区域是闲置的。fstrim 会通过 ioctl 系统调用向文件系统发送 TRIM 请求。

3. 文件系统处理：文件系统收到 TRIM 请求后，会根据文件系统的机制将闲置的块信息传递给存储设备驱动程序。文件系统可能会将闲置块信息传递给驱动程序的 TRIM 接口，或者使用其他机制实现 TRIM 操作。

4. 存储设备驱动程序处理：存储设备驱动程序接收到 TRIM 请求后，将根据设备的支持和实现方式执行 TRIM 操作。TRIM 操作可以在闲置块中擦除数据，以便将其标记为可用状态。具体的 TRIM 实现方式可能因存储设备的类型和厂商而异。

总之，fstrim 命令通过文件系统和存储设备驱动程序的协作，将 TRIM 请求传递给底层存储设备，以回收闲置块并提高性能。每个环节的具体实现取决于所使用的文件系统和存储设备驱动程序。

#### qcow2镜像缩小

gzl的调研fstrim单号: 61711
```
总结
一、fstrim功能针对不同类型（virtio-blk，virtio-scsi）的磁盘分析
1、virtio-blk磁盘

需qemu版本大于等于4.0，guest的内核版本大于等于5.0，才能支持。
2、virtio-scsi磁盘

qemu2.12就支持此功能。网上描述说scsi的磁盘不稳定之类，待考验。
二、开销分析

释放IMG空间可以通过2种方式：

1、通过调用fstrim一次性释放，对磁盘的IO有一定的影响。(释放的块并非连续，根据gdb的调试，释放分很多次。）

2、可以通过配置挂载选项mount -o discard，在guest删除文件时，自动调用discard的操作释放host上面IMG的空间，因为每次删除文件时，同时调用discard释放空间，和fstrim命令相比，分散了对磁盘的IO的操作，影响小。

总体来说，819版本的qemu已经升级到4.1，如kylinos的内核版本可以集成virtio-blk的discard功能，是一个有利于释放host上面IMG占用空间的功能。
```

gpt: 通过qemu-nbd 和 fstrim缩减qcow2
```
sudo fstrim /mnt/qemu-image
```
=> 执行了没效果

gpt: 通过qemu-nbd 和 fstrim缩减qcow2镜像大小，没有缩小
发现再次qemu-img convert之后会变小???

```
qemu-nbd -c /dev/nbd0 GUEST.IMG
qemu-nbd --discard=on -c /dev/nbd0 GUEST.IMG # => ok, 后面普通mount就行
qemu-nbd --discard=unmap -c /dev/nbd0 GUEST.IMG

mount /dev/nbd0p1 /mnt/
mount -o discard /dev/nbd0p1 /mnt/

fstrim /mnt # xfs ok
```

关键字《virsh add disk discard=unmap》

https://chrisirwin.ca/posts/discard-with-kvm-2020/
```
<driver name='qemu' type='qcow2' discard='unmap'/>
sudo fstrim -av
sudo systemctl enable --now fstrim.timer
```

#### zfs qcow2镜像缩小

=> 注意，可能需要比较长的时间才能trim完成, 变为sparse文件, du容量缩小

gtp关键字《the discard operation is not supported zfs》

首先配置虚拟机的磁盘qcow2属性`discard=unmap`
```
<driver name='qemu' type='qcow2' discard='unmap'/>
```

手动trim
```
zpool trim pool1
```

设置自动trim
```
zpool get autotrim
zpool set autotrim=on pool1
```
