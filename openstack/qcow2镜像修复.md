# qcow2镜像修复

起因:
虚拟机镜像xxx.qcow2手动使用glusterfs命令解锁
```
glusterfs v clear-locks data /xxx/xxx.qcow2
```

然后虚拟机镜像就损坏了，qemu使用此镜像报错: `Image is corrupt; cannot be read/write`

分析:
使用`qemu-img check`检查镜像, 报错

修复:
l2 table损坏的场景

qcow2_dump工具


镜像损坏问题分析解决
起因分析
虚拟机镜像xxx.qcow2手动使用glusterfs命令解锁glusterfs v clear-locks data /xxx/xxx.qcow2
然后虚拟机镜像就损坏了，qemu使用此镜像报错: Image is corrupt; cannot be read

## 第一个镜像损坏分析修复

分析:
使用qemu-img check检查镜像, 报错，也无法修复

使用qcow2_dump工具检查，发现l2 table有问题
```
unaligned: 6086, invalid: 77
```

修复:
定制修改qcow2_dump工具, 将损坏的l2 table指向0,表示这块内容为0
https://github.com/ming1/qcow2-dump
https://github.com/zhangyoujia/qcow2-dump

修复完成之后，镜像损坏flag还存在，需要使用工具再清理一下。
```
qcow2_dump -C corrupt DISK40.IMG
```
清理完成之后，就可以使用qemu-nbd挂载起来了，有少量数据结构需要清理，是日志等无关紧要的问题，不管了。
使用qemu-nbd挂载后，里面还是lvm分区，需要处理一下，才能挂载:
vgs
vgchange -ay 卷组
然后lvs看一下。
有lvm逻辑卷就在/dev/mapper/xxx下面，直接挂载就可以

## 第二个镜像数据修复

镜像问题:
也是多虚拟机读写同一个虚拟机镜像，导致USER.IMG损坏了。
镜像seeksize特别大， 7.3E (注意: 比T还大的单位)

使用qcow2_dump工具检测，也报错: Line: 3560 | realloc failed

两种修复方法：
- 1.通过qemu-img命令将原始qcow2镜像直接转成一个新的qcow2镜像
  最终使用这个方法的
- 2.dd原始镜像, 缩小到合适的大小（例如236G）

然后使用修复好的镜像开机，结果镜像里面的ext4文件系统结构需要清理, 开机后，系统还是不太正常，而且使用fsck.ext4修复也未成功

然后就创建一个新的user_new.img， 格式化为ext4分区，使用qemu-nbd挂载起来，然后使用rsync将旧的user.img数据通过过来，然后就能正常开机使用了。
```
qemu-nbd -c /dev/nbd0 ./user_new.img
mkfs.ext4 /dev/nbd0
mount /dev/nbd0 /mnt/userimg
rsync -ah /mnt/userimg.org./ ./

```
同步完成后，还需要卸载qemu-nbd
```
umount /mnt/userimg/
qemu-nbd -d /dev/nbd0
```
