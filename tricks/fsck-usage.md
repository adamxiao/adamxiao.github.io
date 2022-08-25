# fsck使用修复文件系统

* fsck
* xfs_repair

```
fsck /dev/vda3
xfs_repair -L  /dev/mappper/xxx-root ?
```

rhcos的修复方法:
```
[root@master2 mapper]# fsck /dev/vdb2
fsck from util-linux 2.32.1
fsck.fat 4.1 (2017-01-24)
0x25: Dirty bit is set. Fs was not properly unmounted and some data may be corrupt.
1) Remove dirty bit
2) No action
? 1
Perform changes ? (y/n) y
/dev/vdb2: 14 files, 3432/64879 clusters
[root@master2 mapper]# fsck /dev/vdb3
fsck from util-linux 2.32.1
e2fsck 1.45.6 (20-Mar-2020)
boot: clean, 120/98304 files, 193448/393216 blocks
[root@master2 mapper]# fsck /dev/vdb4
fsck from util-linux 2.32.1
If you wish to check the consistency of an XFS filesystem or
repair a damaged filesystem, see xfs_repair(8).
[root@master2 mapper]# xfs_repair /dev/vdb4
Phase 1 - find and verify superblock...

[root@master2 mapper]# xfs_repair -L /dev/vdb4
Phase 1 - find and verify superblock...
        - reporting progress in intervals of 15 minutes
Phase 2 - using internal log
        - zero log...
```
