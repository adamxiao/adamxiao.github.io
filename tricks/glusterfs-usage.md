# glusterfs使用

查询文件落到哪个副本
```
getfattr -n trusted.glusterfs.pathinfo -e text /home/kylin-data/data/
```

查询副本分布
```
gluster v info
```

副本重新均匀
```
gluster volume reblance test start
gluster volume reblance test status
```

## FAQ

#### ls卡住

可能由于heal进程在修复目录下的文件

单号: 10793
```
strace ls -al /home/kylin-ksvd/logs可以看到卡住的文件
```

然后用下面命令解锁
```
gluster volume clear-locks 卷名 /logs/xxx-VIA.log  kind granted inode
```

#### 宿主机宕机导致glusterfs锁丢失

宿主机上的qemu锁定的guest.img的锁，没有释放导致, 可以主动解锁

旧的问题单号: 58981 63839

```
gluster volume clear-locks MStorage  /logs/10.90.6.172-mc.log kind granted inode
Volume clear-locks successful
No locks cleared.
No locks cleared.
No locks cleared.
```

```
[ssh_10.60.5.116] root@node4: ~$gluster volume clear-locks FStorage  /ksvd-orgs/org-0/users/0local/mcadmin1/72f4d78b-51f0-3128-a7a7-346f77e80722/GUEST.IMG kind granted posix
Volume clear-locks successful
node5:/export/heketi/vg_4e068/device_6134d/data_6eff6/: posix blocked locks=0 granted locks=1
No locks cleared.
No locks cleared.
```
