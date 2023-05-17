# ubuntu zfs使用

安装
```
apt install zfsutils-linux
```

列觉池
```
zpool list
```

zpool import -N -f 'boot-pool'

## FAQ

#### cannot import 'boot-pool': one or more devices is read only

```
zpool import -N -f 'boot-pool'
cannot import 'boot-pool': one or more devices is read only
```

```
zpool import -o readonly -F -R /mnt boot-pool
zpool import -o readonly -N -f 'boot-pool'
zpool import -V -o readonly -N -f 'boot-pool'
```

## 其他

```
/sbin/zpool import -N -f 'boot-pool'
one or more devices is read only
```

```
sdb         zfs_member boot-pool 16672127188688975952
├─sdb1
├─sdb2      vfat       EFI       4607-0C18
└─sdb3      zfs_member boot-pool 16672127188688975952
```

