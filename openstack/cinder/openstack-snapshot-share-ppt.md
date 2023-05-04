# openstack快照和备份分享

关键字
- snapshot
- backup

## 快照

- openstack实例快照

- qemu内存快照

- qemu事务多磁盘快照 snapshot

#### 先带着问题

- 做实例快照时，虚拟机是否暂停了?
- 文件系统缓存在内存, 没有写到磁盘, 怎么办?
- 单独对一个磁盘做快照, 什么时候写文件刷新到磁盘中去?

#### 快照要点

如果在生产系统中执行 snapshot 操作，必须确保此操作快速且安全。
- 1.快速
    为保证数据的一致性，snapshot 时需要 pause instance，操作完后再 resume。
    在这个过程中 instance 是无法对外服务的，为了减少对业务的影响，我们希望 snapshot 越快越好。

- 2.安全
    即数据一致性，snapshot 出来的 image 不能有没落盘的数据，能够正常启动。
    所以通常在执行 snapshot 前要 pause instance，暂停所有的 IO 操作。

  真正的解决方案  
默认 snapshot 的问题在于 qemu-img convert 耗时太长，而耗时太长的原因是 instance 的系统盘是文件，拷贝文件本身就是一个耗时的操作。真正的解决方案是：

让 instance 从 cinder volume 启动，利用 storage provider 自己的 snapshot 技术实现快速复制。

## 备份

- qemu备份命令drive-backup
  TODO: 问题, 怎么做到check-point的?

- cinder-backup

- openstack第三方备份freezer
