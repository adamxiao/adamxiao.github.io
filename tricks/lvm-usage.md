# lvm使用入门

## 清理磁盘现有的lvm

#### 1. 删除逻辑卷(logical volume)

```bash
lvdisplay # 获取逻辑卷信息
lvremove xxx
```

#### 2. 删除逻辑卷组(volume group)

```bash
vgs # 获取逻辑卷组信息
vgremove xxx
```

#### 3. 删除物理卷(physical volume)

```bash
pvs # 获取物理卷信息
pvremove xxx
wipefs -a /dev/sda # 注意修改磁盘
```


## 其他命令

### 创建物理卷 （可以是裸磁盘，裸分区）

```bash
pvcreate /dev/sdb
pvs  #查看物理卷
```

### 创建卷组
```
vgs # 查看卷组
```

#### 删除卷组
```bash
vgremove vg_* -ff -y
Volume group "vg_6d8b78a6ece3cd521704cc3443293a89" successfully removed
```

```bash
vgdisplay

lvcreate
lvcreate -qq --autobackup=n --poolmetadatasize 12288K --chunksize 256K --size 2097152K --thin vg_33c6ea2e6c9946eafa90d332a59f2e48/tp_c2f67b766f52e554fa5ebf3ee5f79453 --virtualsize 2097152K --name brick_c2f67b766f52e554fa5ebf3ee5f79453
lvcreate -L 2G -n data vg_33c6ea2e6c9946eafa90d332a59f2e48

lvconvert --type thin-pool vg_33c6ea2e6c9946eafa90d332a59f2e48/pool0
lvcreate -l 100%FREE --thinpool tp_c2f67b766f52e554fa5ebf3ee5f79453 vg_33c6ea2e6c9946eafa90d332a59f2e48


lvremove # 删除逻辑卷
lvremove /dev/vg1000/lvol0 #删除逻辑卷"lvol0" 
lvs # 查看逻辑卷组
```

### 扩容逻辑卷分区大小

lvm就是做这个事情的，防止磁盘空间不够了，需要重新安装系统的那种需求

```
vgextend  卷名 sd*
lvextend 逻辑卷名
lvextend -h
```

实际操作
```
[System not activated][root@test ~]# vgs
  VG #PV #LV #SN Attr   VSize   VFree
  ko   1   3   0 wz--n- <98.00g    0
[System not activated][root@test ~]# vgextend ko /dev/vdb
  Physical volume "/dev/vdb" successfully created.
  Volume group "ko" successfully extended

[System not activated][root@test ~]# lvs
  LV   VG Attr       LSize  Pool Origin Data%  Meta%  Move Log Cpy%Sync Convert
  data ko -wi-ao---- 44.02g
  root ko -wi-ao---- 50.00g
  swap ko -wi-ao----  3.97g
[System not activated][root@test ~]# vgs
  VG #PV #LV #SN Attr   VSize   VFree
  ko   2   3   0 wz--n- 597.99g <500.00g
[System not activated][root@test ~]# lvextend -L +100G /dev/mapper/ko-data
  Size of logical volume ko/data changed from 44.02 GiB (11270 extents) to 144.02 GiB (36870 extents).
  Logical volume ko/data successfully resized.
[System not activated][root@test ~]# lvs
  LV   VG Attr       LSize   Pool Origin Data%  Meta%  Move Log Cpy%Sync Convert
  data ko -wi-ao---- 144.02g
  root ko -wi-ao----  50.00g
  swap ko -wi-ao----   3.97g

[System not activated][root@test ~]# xfs_growfs /dev/mapper/ko-data
xfs_growfs: /dev/mapper/ko-data is not a mounted XFS filesystem
[System not activated][root@test ~]# resize2fs /dev/mapper/ko-data
resize2fs 1.45.6 (20-Mar-2020)
Filesystem at /dev/mapper/ko-data is mounted on /data; on-line resizing required
old_desc_blocks = 6, new_desc_blocks = 19
The filesystem on /dev/mapper/ko-data is now 37754880 (4k) blocks long.

[System not activated][root@test ~]# df -h | grep data
/dev/mapper/ko-data  142G  154M  136G   1% /data
```

关键字《lvm分区增大》

[Linux下对LVM逻辑卷分区大小调整 [针对xfs和ext4文件系统]](https://www.cnblogs.com/kevingrace/p/5825963.html)


特别注意的是：
```
resize2fs 命令            针对的是ext2、ext3、ext4文件系统
xfs_growfs 命令         针对的是xfs文件系统
```

关键字《centos qcow2 分区增大》
https://opengers.github.io/openstack/openstack-instance-disk-resize-and-convert/
```
#我们把40G加到分区2上     
#growpart /dev/vda 2
CHANGED: partition=2 start=33556480 old: size=50329600 end=83886080 new: size=134210315,end=167766795

#然后扩容分区2文件系统    
#xfs_growfs /
```
	
### 重复名称vg,pv处理

关键字《lvm vg show id》

https://unix.stackexchange.com/questions/677054/lvm2-how-to-list-physical-partition-identifiers-with-the-uuid-of-the-vg-they-a
```
vgs -o vg_name,vg_uuid,pv_uuid
```

先重命名一个，然后就不重复了，就可以删除了
```
vgrename 4vrdpY-MCJM-HBfT-RVhe-WnTr-2NGr-NDOJ6H old --force
```

关键字《vgremove by uuid》
还有其他方法待尝试:
https://unix.stackexchange.com/questions/587879/how-to-remove-missing-pv-when-vg-has-a-duplicate-name
```
pvremove /dev/sdb2 --force --force
wipefs -a /dev/sdb2
```

## FAQ

* 1. Cannot use /dev/sda: device is partitioned
How to fix LVM Device /dev/sdb excluded by a filter.
https://support.tools/post/how-to-fix-lvm-device-excluded-by-filter/
```
pvcreate /dev/sda
  Cannot use /dev/sda: device is partitioned
wipefs -a /dev/sda # 解决
```

#### centos 7 qcow识别lvm卷

安装lvm包
```
yum install -y lvm2
```

激活lvm卷
```
lvchange -ay vg_vrm/lv_root
lvchange -ay vg_vrm # 激活全部vg
```

原因是qemu-nbd挂载/dev/nbd0, lvm分区识别手动识别一下
最后就可以`mount /dev/mapper/vg_vrm-root /mnt/tmp`
