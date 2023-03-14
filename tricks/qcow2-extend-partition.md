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
