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

## glusterfs编译

dzh => https://docs.gluster.org/en/latest/Developer-guide/compiling-rpms/#common-steps

```
git clone -b release-6 https://github.com/gluster/glusterfs.git
```

配置
```
./autogen.sh
./configure --enable-fusermount
make dist
```

构建rpm包
```
cd extras/LinuxRPM
make glusterrpms
```

#### 调试手段

获取gfid
```
getfattr -n glusterfs.gfid.string -e text /home/kylin-data/data1/ksvd-orgs/org-0/users/0local/mcadmin1/68acbbfd-a1ec-3fe7-a827-63dee3d5cffc/GUEST.IMG
0e13ea23-7fe4-4be3-a992-4f039cced86a
```

简易ipc入口测试
```
pid=$(cat /run/vs/rpc/fuse.pid)
printf 'PING\n' | nc -U /run/vs/rpc/fuse-$pid.sock
printf 'LIST <gfid>\n' | nc -U /run/vs/rpc/fuse-$pid.sock
```

日志
/var/log/glusterfs/home-kylin-data-data1.log

#### 10x系列编译环境准备

修改glusterfs.spec, 安装依赖包
```
yum install -y libacl-devel libtirpc-devel userspace-rcu-devel libcurl-devel
```

参考官方文档准备，去除了pyliblzma, pyxattr, 以及python相关的
```
yum -y install git autoconf \
  automake bison dos2unix flex fuse-devel glib2-devel libaio-devel \
  libattr-devel libibverbs-devel librdmacm-devel libtool libxml2-devel lvm2-devel make \
  openssl-devel pkgconfig \
  readline-devel \
  rpm-build systemtap-sdt-devel tar libcmocka-devel
```

#### R011系列编译环境准备

暂使用了源码编译安装userspace-rcu-devel
```
export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH
```

发现可以配置源安装?
```
baseurl=https://xiaoyun:Kylin.123@jfrog.kylinsec.com.cn/artifactory/ctrl-OS-Repos/KSVD/KY3.3-6-KSVD-V7R024/x86_64/os/
baseurl=https://yupeng:Nunickyss%401@jfrog.kylinsec.com.cn/artifactory/ctrl-OS-Repos/KSVD/KY3.3-6-KSVD-V7R024/x86_64/os/
```

libuuid-devel

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
