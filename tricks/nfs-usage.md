# NFS服务搭建使用

* nfs

关键字《centos启用NFS》

exportfs -r
重新export，可以看错误信息

## 安装方法：

```bash
# centos
yum install nfs-utils
# ubuntu
apt install nfs-kernel-server nfs-common
```

#### KSVD部署文档中的资料

NFS服务器的配置方法说明:

1.创建共享目录

1）在nas服务器上 ：
```
mkdir  -p  /home/8.1.5data_center
```

2）创建uid和gid为2000的kylin-ksvd用户：
```
useradd kylin-ksvd -u 2000 
```

3）修改共享目录属主属组：
```
chown  -R 2000:2000  /home/8.1.5data_center
```

2.修改NFS配置文件/etc/exports, 添加如下行：
```
# 注意：“*(”之间没有空格 ，如果有空格，mount可以挂载成功，但是会提示无法写入
/home/8.1.5data_center *(rw,no_root_squash,sync)
```

3.启动nfs服务并关闭防火墙
```
systemctl restart nfs
systemctl enable nfs

systemctl stop firewalld
systemctl disable firewalld
```

4.确认配置是否生效
执行exportfs命令，出现/home/8.1.5data_center字样则说明配置成功。

## 配置方法

/etc/exports示例
```
/mnt/pxe  *(ro,no_root_squash,sync)
/ubuntu-1804  *(ro,no_root_squash,sync)
/ubuntu-2004  *(ro,no_root_squash,sync)
/mnt/iso  *(ro,no_root_squash,sync)
/home/data/adam  10.200.2.6(rw,no_root_squash,sync)
```


查询nfs共享路径是否生效
```
showmount -e 127.0.0.1 
```

nfs挂载
```
mount -t nfs 10.20.1.100:/home/export/kylin-data /home/kylin-data -o rw,vers=4,noatime,nodiratime

mount -t nfs 10.20.1.12:/home/data/adam /mnt -o rw,vers=4,noatime,nodiratime
```


nfs选项说明
```
/home/wwkj0108/nfsboot——NFS服务器端的目录，用于与nfs客户端共享
*——允许所有的网段访问，也可以使用具体的IP
rw——挂接此目录的客户端对该共享目录具有读写权限
sync——资料同步写入内存和硬盘
no_root_squash——root用户具有对根目录的完全管理访问权限
no_subtree_check——不检查父目录的权限
```

## linux开机自动挂载

关键字《linux 开机自动挂载nfs》
参考: https://blog.csdn.net/zhongbeida_xue/article/details/81112529

修改/etc/fstab文件, 添加内容如下:
```
<nfs_server_IP>:/<remote_directory> /mnt/nfs_share nfs defaults,_rnetdev 0 0
```

其中，<nfs_server_IP> 是 NFS 服务器的 IP 地址，<remote_directory> 是远程共享目录的路径。请根据实际情况修改这两个参数。
- `_rnetdev`表示主机无法挂载直接跳过，避免无法挂载主机无法启动
  => 验证失败, 会挂载失败

可以使用如下命令立即挂载
```
sudo mount -a
```

确认挂载是否成功：
```
df -h
```

## FAQ

#### Permission denied

https://www.truenas.com/community/threads/nfs-share-problem.93617/

配置Maproot User为root, Maproot Group 为root
这样root就有权限写文件了

#### NFS挂载卡住df问题

关键字《nfs 挂载卡住》

总结:
- 解决方法要么是恢复nfs服务器
- 要么是umount

https://blog.csdn.net/BrotherDong90/article/details/51735632
hard-mount: 当客户端加载NFS不成功时,一直重试，直到NFS服务器有响应。hard-mount 是系统的缺省值。在选定hard-mount 时，最好同时选 intr , 允许中断系统的调用请求，避免引起系统的挂起。
=> 确实dmesg看到nfs挂载timed out

http://smilejay.cn/2020/07/mount-nfs-hang/
umount -f -l /mnt/test 进行lazy umount，这个一般都可以了。

https://cloud.tencent.com/developer/article/1993384
fuser -ck /nfsdir => 杀死相关进程?

[NFS问题诊断](https://blog.51cto.com/u_15704227/5436439)
检查nfs服务是否可用

https://codeantenna.com/a/WaU8ou1ezn
df 命令卡死，使用 strace 追踪命令跑到哪一步
使用强制卸载： umount -l   /mnt/secondary

https://codeantenna.com/a/T7WslSLx8j
df -h 卡死，ctrl+C都没用。
原因一：如果有网络盘挂载，如nfs、samba这类挂载，很有可能对端服务失效，目录卡死的原因，
原因二：本地目录卡死的功能。

acloud的nfs挂载
```
Sangfor:aSV/host-525484000bb2 /sf # mount | grep nfs
rpc_pipefs on /var/lib/nfs/rpc_pipefs type rpc_pipefs (rw,relatime)
nfsd on /proc/fs/nfsd type nfsd (rw,relatime)
192.168.83.102:/ on /sf/share/nfs_cluster_data type nfs4 (rw,relatime,sync,dirsync,vers=4.0,rsize=1048576,wsize=1048576,namlen=255,acregmin=0,acregmax=0,acdirmin=0,acdirmax=0,soft,noac,proto=tcp,port=5049,timeo=10,retrans=3,sec=sys,clientaddr=192.168.83.100,local_lock=none,addr=192.168.83.102)
127.0.0.1:/3c471bd1_vs_vol_rep3 on /sf/data/3c471bd1_vs_vol_rep3 type nfs (rw,relatime,vers=3,rsize=1048576,wsize=1048576,namlen=255,acregmin=1,acregmax=1,acdirmin=0,acdirmax=0,hard,nolock,noresvport,proto=tcp,timeo=600,retrans=2,sec=sys,mountaddr=127.0.0.1,mountvers=3,mountport=38465,mountproto=tcp,lookupcache=none,local_lock=all,addr=127.0.0.1)
127.0.0.1:/3c471bd1_vs_vol_rep3 on /sf/data/vs/gfs/3c471bd1_vs_vol_rep3 type nfs (rw,relatime,vers=3,rsize=1048576,wsize=1048576,namlen=255,acregmin=1,acregmax=1,acdirmin=0,acdirmax=0,hard,nolock,noresvport,proto=tcp,timeo=600,retrans=2,sec=sys,mountaddr=127.0.0.1,mountvers=3,mountport=38465,mountproto=tcp,lookupcache=none,local_lock=all,addr=127.0.0.1)
```

KSVD的nfs挂载
```
[ssh_10.60.5.113] root@node7: bin$mount | grep nfs
sunrpc on /var/lib/nfs/rpc_pipefs type rpc_pipefs (rw,relatime)
10.90.4.70:/home/nfs on /mnt type nfs4 (rw,relatime,vers=4.1,rsize=1048576,wsize=1048576,namlen=255,hard,proto=tcp,timeo=600,retrans=2,sec=sys,clientaddr=10.60.5.113,local_lock=none,addr=10.90.4.70)
192.168.99.112:/home/nfs_dir/data on /home/ksvd_backups/192.168.99.112:homenfs_dirdata type nfs4 (rw,relatime,vers=4.1,rsize=524288,wsize=524288,namlen=255,soft,proto=tcp,timeo=30,retrans=2,sec=sys,clientaddr=192.168.99.113,local_lock=none,addr=192.168.99.112)
```

