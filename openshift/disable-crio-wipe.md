# 禁止crio-wipe自动清理镜像

参考https://github.com/code-ready/crc/issues/2791#issuecomment-936436839

## 1. 使用livecd进入系统

咨询过mzg，在ostree系统里面，修改/usr目录下的文件，暂没改成功，所以还是livecd改

* 挂载系统分区
```
sudo mount /dev/vda4 /mnt
```

是第四个分区，注意硬盘，虚拟机硬盘一般就是vda，物理机器可能是sda，或者sdb

## 2. 修改crio-wipe.service文件

路径可能是/mnt/ostree/.../usr/systemd/system/crio-wipe.service

修改服务命令为/bin/ture，最终内容如下

```
[Unit]
Description=CRI-O Auto Update Script
Before=crio.service
RequiresMountsFor=/var/lib/containers

[Service]
ExecStart=/bin/true
Type=oneshot

[Install]
WantedBy=multi-user.target
```
