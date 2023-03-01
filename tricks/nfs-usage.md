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

可以使用如下命令立即挂载
```
sudo mount -a
```

确认挂载是否成功：
```
df -h
```
