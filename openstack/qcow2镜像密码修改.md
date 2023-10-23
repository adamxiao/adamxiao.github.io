# qcow2镜像密码修改

## 在线修改

通过qemu-guest-agent修改(前提是虚拟机中安装运行了qga)
```
virsh set-user-password  ${domain} root xxxxxx
```

## 离线修改

#### 使用qemu-ndb挂载修改

```
# Step 1 - Enable NBD on the Host
modprobe nbd max_part=8 

# Step 2 - Connect the QCOW2 as network block device
qemu-nbd --connect=/dev/nbd0 USER.IMG 

# Step 3 - Find The Virtual Machine Partitions
fdisk /dev/nbd0 -l 

# Step 4 - Mount the partition from the VM
mount /dev/nbd0p1 /mnt/

# Step 5 - After you done, unmount and disconnect
umount /mnt/
qemu-nbd --disconnect /dev/nbd0 
rmmod nbd
```

可能需要激活lvm卷, 挂载lvm卷分区
```
lvchange -ay vg_vrm # 激活全部vg
mount /dev/mapper/vg_vrm-root /mnt/tmp
# 最后就可以通过chroot /mnt/tmp, 然后passwd修改密码了
```

#### 使用guestfish修改

```
yum -y install guestfish
virt-customize -a GUEST.IMG --root-password password:ksvd2020
```

关键字：“libguestfs-tools 获取文件”
```
yum install libguestfs libguestfs-tools -y
mkdir /tmp/tmpdir
guestmount -a USER.IMG  -m /dev/sda  --rw /tmp/tmpdir
```


```
root@box1 # guestfish --rw -a ./rhel-guest-image-7.1-20150224.0.x86_64.qcow2
><fs> run
><fs> list-filesystems
><fs> mount /dev/sda1 /
><fs> vi /etc/shadow

NOTE: after you perform the following steps you use "quit" to exit. 
DO NOT EXIT NOW, proceed with the following steps
```

## 参考文档

* [virt-customize修改镜像文件](https://access.redhat.com/discussions/664843)

* [how-to-mount-qcow2-image](https://unix.stackexchange.com/questions/268460/how-to-mount-qcow2-image)
  https://unix.stackexchange.com/questions/268460/how-to-mount-qcow2-image/506399

* [qemu-nbd技术分析](https://cloud.tencent.com/developer/article/1087439)
