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



## FAQ

* 1. Cannot use /dev/sda: device is partitioned
How to fix LVM Device /dev/sdb excluded by a filter.
https://support.tools/post/how-to-fix-lvm-device-excluded-by-filter/
```
pvcreate /dev/sda
  Cannot use /dev/sda: device is partitioned
wipefs -a /dev/sda # 解决
```
