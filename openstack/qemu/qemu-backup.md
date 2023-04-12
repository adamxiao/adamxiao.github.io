# qemu备份逻辑

问题:
- qemu在备份命令执行后，把新产生的脏数据保存在哪里?
  两种思路:
  - 1.就是脏数据保存在其他地方 => 没有，sync命令时，qemu写了文件 => 是不是旧数据保留在内存中?
  - 2.就是脏数据同步到备份盘中 => 测试也不是, 功能说明也不是! => 也不一定。。。
  - 3.就是啥都没做
  - 4.估计是cow特性弄的? => raw格式虚拟机验证一下? 看文章说支持raw格式.

```
[ssh_10.60.5.113] root@node8: 6e669376-d344-3d97-ad71-d866ae94f8bb$qemu-img compare /tmp/backup.img DISK11411.IMG
Content mismatch at offset 1,048,576!
```

关键字《qemu drive-backup 原理》

[KVM/QEMU在线备份(1)](https://cloud.tencent.com/developer/article/2237600)

## qmp快设备备份相关命令

注: hmp命令就是方便我们使用

```
virsh qemu-monitor-command $DOMAIN --pretty '{ "execute": "query-block-jobs" }'
virsh qemu-monitor-command $DOMAIN --hmp 'info block-jobs'

{
  "return": [
    {
      "auto-finalize": true,
      "io-status": "ok",
      "device": "drive-virtio-disk1",
      "auto-dismiss": true,
      "busy": false,
      "len": 107374182400,
      "offset": 97771651072,
      "status": "running",
      "paused": false,
      "speed": 0,
      "ready": false,
      "type": "backup"
    }
  ],
  "id": "libvirt-57"
}
```

查询块设备
```
virsh qemu-monitor-command $DOMAIN --hmp 'info block'
```


还有其他
- block-job-cancel
- block-job-pause

- drive_backup

```
drive_backup [-n] [-f] [-c] device target [format] -- initiates a point-in-time
                        copy for a device. The device's contents are copied to the new image file,
                        excluding data that is written after the command is started.
                        The -n flag requests QEMU to reuse the image found
                        in new-image-file, instead of recreating it from scratch.
                        The -f flag requests QEMU to copy the whole disk,
                        so that the result does not need a backing file.
                        The -c flag requests QEMU to compress backup data
                        (if the target format supports it).
```

https://www.qemu.org/docs/master/interop/qemu-storage-daemon-qmp-ref.html#qapidoc-401
使用示例
```
virsh qemu-monitor-command $DOMAIN --pretty \
'{ "execute": "drive-backup", "arguments": { "device": "drive-virtio-disk1", "sync": "full", "target": "/tmp/backup.img" } }'
```

https://patents.google.com/patent/CN109471699A/zh
专利 - 基于Qcow2镜像文件的差异位图特性的虚拟机增量备份系统

drive-backup的入口函数
hmp_drive_backup

block/backup.c: backup_run
=> 猜测是否是锁住了flush锁导致的? => 感觉不像
```
qemu_co_rwlock_init(&s->flush_rwlock);
qemu_co_rwlock_wrlock(&s->flush_rwlock);
```

https://qemu.readthedocs.io/en/latest/interop/live-block-operations.html#qmp-invocation-for-drive-backup
Moving from the deprecated drive-backup to newer blockdev-backup

#### libvirt备份?

[Efficient live full disk backup](https://libvirt.org/kbase/live_full_disk_backup.html)
Two kinds of backup: "push" and "pull"

The pull-based backup provides more flexibility by letting an external tool fetch the modified bits as it sees fit, rather than waiting on libvirt to push out a full backup to a target location.

virsh backup-begin命令, libvirt6.2支持, 4.5不支持
```
virsh backup-begin $DOMAIN
Backup started
=> 我遇到报错了, ubuntu 20.04下使用win10 => 可能需要更高版本libvirt支持... (libvirt-7.2.0 and QEMU-4.2)
error: Operation not supported: incremental backup is not supported yet
=> 使用ubuntu 22.04验证可以
```

查看备份任务信息
```
virsh domjobinfo $DOMAIN --completed
Job type:         Completed
Operation:        Backup
Time elapsed:     183          ms
File processed:   39.250 MiB
File remaining:   0.000 B
File total:       39.250 MiB

Job type:         Completed
Operation:        Backup
Time elapsed:     1527         ms
File processed:   8.000 GiB
File remaining:   0.000 B
File total:       8.000 GiB
```

旧版本备份方法:
```
virsh snapshot-create-as --domain vm1 overlay1 \
    --diskspec vda,file=/var/lib/libvirt/images/overlay1.qcow2 \
    --disk-only
```
可以添加--quiesce 参数冻结文件系统

以及--no-metadata 不要快照元数据

最后合并
```
virsh blockcommit vm1 vda --active --verbose --pivot
```


[QEMU/KVM磁碟在線備份](https://kknews.cc/code/4keqo4g.html)
查詢虛擬機所有磁碟的塊信息，含bitmap 
```
virsh qemu-monitor-command $DOMAIN --pretty '{ "execute": "query-block" }'
```

## 其他

QEMU同步脏页原理
https://blog.csdn.net/huang987246510/article/details/116606147

关键字《qemu drive backup data consistency》

https://github.com/abbbi/virtnbdbackup
Backup utility for libvirt, using the latest changed block tracking features. Create online, thin provisioned full and incremental or differential backups of your kvm/qemu virtual machines.
=> TODO: 可以尝试，在ubuntu 20.04上备份虚拟机


https://www.qemu.org/docs/master/interop/qemu-storage-daemon-qmp-ref.html
=> qmp官方文档


https://wiki.qemu.org/Features/VMSnapshotEnchancement
快照原理，有图

[Qemu 中 Bitmap 的應用](https://read01.com/5nJOoan.html)

[(好)QEMU/KVM磁盘在线备份](https://zhuanlan.zhihu.com/p/56886705)
QEMU/KVM磁盘的在线完整及增量备份，是“打包”方案的一种具体实现，可实现基于时间点的备份，同时支持本地与远程2种备份方式，并可指定备份文件进行恢复。

▷ persistent dirty bitmap：是dirty bitmap的改进版，因为dirty bitmap是记录在内存中的，当qemu虚拟机关机后，dirty bitmap就消失了，就会导致需要重新做一次完整备份。persistent dirty bitmap是v2.10开始才支持
=> 持久bitmap仅支持qcow2，不支持raw格式（例如本地盘raw文件或者ceph-rbd）

虚拟机运行过程中确定要备份

如果是虚拟机已经运行一段时间了，才决定做备份，就需要用到QMP的“事务”

1️⃣ 以事务方式对磁盘创建bitmap（block-dirty-bitmap-add）及对磁盘做完整备份（"sync":"top"）

2️⃣ 接下来可以做incremental备份（"sync":"incremental"）

QMP部分功能支持事务性（事务的目的是当其中一件事失败后，会自动回滚，保证数据一致性，但这里也可用于保证创建bitmap和开始备份之间没有缺少数据），因此上述1️⃣通过事务操作

```
{ "execute": "transaction",
  "arguments": {
    "actions": [
      {"type": "block-dirty-bitmap-add",
       "data": {"node": "drive-virtio-disk0", "name": "bitmap0"} },
      {"type": "drive-backup",
       "data": {"device": "drive-virtio-disk0", "target": "/path/to/full_backup.img", "sync": "top"} }
    ]
  }
}
```

[qemu-kvm部分流程/源代码分析](https://abcdxyzk.github.io/blog/2015/07/28/kvm-pic/)
22.backup & nbd (qemu开机备份流程)
=> 有备份源码，但是还是不清楚，怎么就能备份到某个时间点的备份了呢?


问chatgpt: qemu drive-backup 怎么实现基于时间点的备份的
=> 没有问到想要的答案

关键字《qemu drive-backup 原理》

https://aspirer.wang/?p=848
libvirt/qemu live snapshot代码流程分析


虚拟机通过virsh qemu-monitor-command在线备份
https://www.cnblogs.com/ishmaelwanglin/p/17053204.html

Qemu 中 Bitmap 的应用
https://zhuanlan.zhihu.com/p/64238413

## 旧的资料

qemu在线增量备份
dirty-bitmap原理
https://events19.linuxfoundation.org/wp-content/uploads/2017/12/Qemu-Backup-Status-Vladimir-Sementsov-Ogievskiy-Virtuozzo.pdf

使用bitmap进行增量备份
https://www.qemu.org/docs/master/interop/bitmaps.html
（qemu官方bitmap增量备份文档）
https://wiki.qemu.org/Features/IncrementalBackup
使用外部快照进行在线备份
https://iclykofte.com/2016/07/17/kvm-live-online-backups-external-and-internal/
