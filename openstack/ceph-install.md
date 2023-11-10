# ceph 安装

## ceph概念

- OSD
- monitor
- pool
- image

## ceph安装方式

关键字《ceph 部署方法》

- ceph-ansible
  https://docs.27ops.com/%E5%AD%98%E5%82%A8/centos8-ceph/

- ceph-deploy
  https://juejin.cn/post/7086381284733222948
  ceph-deploy部署方式ceph官方通知已不再维护，没有在Nautilus(v14.x)之后的版本测试过
  Ceph-deploy 只用于部署和管理 ceph 集群，客户端需要访问 ceph，需要部署客户端工具。

- kolla-ansible
  https://blog.csdn.net/boxrice007/article/details/112609646
  Train以及之前旧版本, 支持部署ceph

- kolla-ceph
  [(自动化)基于kolla的自动化部署ceph集群](https://www.cnblogs.com/acommoners/p/15946642.html)
  剥离自kolla-ansible?

- cephadm
  https://m.starcto.com/storage_scheme/302.html
  1.2 cephadm安装方式支持命令行CLI和GUI图形化（未来趋势）

### ceph-deploy部署

关键字《ceph-deploy 部署集群》

https://m.starcto.com/storage_scheme/302.html

## ubuntu 20.04 安装ceph

[Ubuntu 20.04 LTS 使用 cephadm 部署 ceph octopus 实验记录](https://www.cnblogs.com/varden/p/15270628.html)

[Ubuntu20.04部署ceph16(pacific)集群 - 傻瓜式教程](https://juejin.cn/post/6996864938329243679)
=> ceph-deploy安装的..

[Ubuntu20.04LTS环境docker+cephadm方式部署Ceph 17.2.5](https://blog.51cto.com/u_16142959/6376072)


https://blog.51cto.com/u_16142959/6376072
3.2. 创建集群
使用 cephadm 创建 Ceph 集群的流程为：

- 初始化第一个 mon 节点
- 配置 ceph 命令行
- 扩展集群 osd 节点

## ubuntu 20.04 安装ceph 16

[Ubuntu20.04部署ceph16(pacific)集群 - 傻瓜式教程](https://juejin.cn/post/6996864938329243679)
来源：稀土掘金 => 这个是使用ceph-deploy工具

```
wget -q -O- 'http://mirrors.ustc.edu.cn/ceph/keys/release.asc' | sudo apt-key add -
echo deb http://mirrors.ustc.edu.cn/ceph/debian-pacific/ $(lsb_release -sc) main | sudo tee /etc/apt/sources.list.d/ceph.list
apt-get update
```

[Ubuntu 20.04 LTS 使用 cephadm 部署 ceph octopus 实验记录](https://www.cnblogs.com/varden/p/15270628.html)

[(好)cephadm安装ceph集群](https://blog.51cto.com/wangguishe/5789231)
=> 安装ceph 16 (获取ceph16的源) `./cephadm add-repo --release pacific`

```
apt-cache madison cephadm
```

使用cephadm创建引导集群（创建第一个 mon 节点）
```
cephadm bootstrap \
  --mon-ip 172.27.9.211 \
  --initial-dashboard-user admin \
  --initial-dashboard-password Str0ngAdminP@ssw0rd
```

### 添加新服务器进ceph集群

先加密钥
```
ssh-copy-id -f -i /etc/ceph/ceph.pub root@ceph136
```

可以在页面上添加: Cluster -> Host -> Create
```
ceph orch host add ceph136
```

## 存储部署

### CephFS部署

部署cephfs的mds服务，指定集群名及mds的数量
```
ceph orch apply mds fs-cluster --placement=3
```

https://www.cnblogs.com/varden/p/15270628.html
有几种方法可以创建新的 OSD：

```
告诉 Ceph 消耗任何可用和未使用的存储设备：
# ceph orch apply osd --all-available-devices
```

ceph -s

ceph cluster expand

## 命令使用

启用 CEPH CLI
Cephadm 不需要在主机上安装任何 Ceph 包。但是，我们建议启用对ceph 命令的轻松访问。做这件事有很多种方法：

该命令会在安装了所有 Ceph 包的容器中启动一个 bash shell。
```
# cephadm shell
```
要执行ceph命令，您还可以像这样运行命令：
```
# cephadm shell -- ceph -s
```
您可以安装该ceph-common软件包，其中包含所有ceph命令，包括ceph、rbd、mount.ceph（用于挂载 CephFS 文件系统）等：
```
# cephadm add-repo --release octopus
# cephadm install ceph-common
```
或者，本实验使用APT直接安装软件包：apt install ceph-common ceph-base

确认该ceph命令可访问：
```
# ceph -v
```
使用以下ceph命令确认该命令可以连接到集群及其状态：

```
# ceph status
```

#### OSD管理

https://www.twblogs.net/a/605899285c734b15c55120ae/?lang=zh-cn
```
ceph osd tree
```

#### 创建pool

```
ceph osd lspools
```

```
ceph osd pool create adam1 200
ceph osd pool ls
```

删除pool
```
ceph osd pool delete kube kube --yes-i-really-really-mean-it
```

参数调整
```
ceph tell mon.* injectargs --mon-allow-pool-delete=true
```

#### 创建image

```
rbd create block1 --size 10G --pool adam1
```

#### 用户auth密钥管理

创建用户, 获取密钥
https://blog.51cto.com/u_15301988/3087403
```
cd /etc/ceph/
ceph auth get-or-create client.adam1 mon 'allow r' osd 'allow object_prefix rbd_children, allow rwx pool=adam1'  -o ceph.client.adam1.keyring
Error EINVAL: osd capability parse failed, stopped at 'allow object_prefix rbd_children, allow rwx pool=adam1' of 'allow object_prefix rbd_children, allow rwx pool=adam1'

# 创建用户client.adam1
ceph auth get-or-create client.adam1 mon 'profile rbd' osd 'profile rbd pool=adam1' # ok
# 获取用户client.adam1的密钥文件
ceph auth get client.adam1 -o ceph.client.adam1.keyring
```

#### libvirt使用rbd设备

定义secret.xml
```
<secret ephemeral='no' private='no'>
  <usage type='ceph'>
     <name>client.libvirt secret</name>
  </usage>
  <uuid>fdcb5967-d3e5-4618-98f5-5919a723e414</uuid>
</secret>
```

设置secret值
```
virsh secret-set-value --secret fdcb5967-d3e5-4618-98f5-5919a723e414 --base64 xxx
```

## 客户端使用

ubuntu 20.04安装ceph客户端
```
apt install ceph-common
```

配置ceph.conf
```
[global]
fsid = b7432491-955c-4cbd-b223-74b1be877e8e
mon_initial_members = ceph-node1
mon_host = 10.90.4.240
auth_cluster_required = cephx
auth_service_required = cephx
auth_client_required = cephx
rbd_default_format = 2
```

获取ceph密钥
/etc/ceph/ceph.client.admin.keyring
```
[client.admin]
        key = AQCxAO9k0RlEHBAABuNRk08vHvYaNPWRYWkgaA==
        caps mds = "allow *"
        caps mon = "allow *"
        caps osd = "allow *"
```

映射为本地块设备
```
rbd map volume-20977fb7-ed46-4931-898c-0a2e68778fb7 --pool volumes
```

导入卷
```
rbd import --pool volumes --order 22 /var/lib/cinder/conversion/tmpgpf_kptv volume-232cf08c-fc2f-4f2f-8685-74890e057515 --new-format --cluster ceph --conf /etc/ceph/ceph.conf
```

导出卷
```
rbd export {pool-name}/{image-name}@{snap-name}  /root/rbd-test.img
```

## openstack接入使用ceph

https://cloud.tencent.com/developer/news/239371

主要的思路是：

- 1、在ceph集群中创建相应的pool：
  - a、创建rbd块设备的pool池“vms”作为nova虚拟机使用的存储池；
  - b、创建rbd块设备的pool池“images” 作为glance镜像的存储池；
  - c、创建rbd块设备的pool池“volumes” 作为cinder的存储池；
  - d、创建rbd块设备的pool池“backups” 作为cinder卷备份的存储池；
- 2、修改kolla全局配置文件globals.yml，关闭openstack自身的ceph存储，打开nova、glance、cinder、cinder-backup等组件使用ceph的开关；
- 3、配置外部ceph，使用kolla的合并配置特性，对相应的组件的ceph存储pool池进行配置；
- 4、使用kolla-ansible deploy重新部署；

```
ceph osd pool create adam1 200
ceph osd pool ls
```

创建用户, 获取密钥
https://blog.51cto.com/u_15301988/3087403
```
cd /etc/ceph/
ceph auth get-or-create client.adam1 mon 'allow r' osd 'allow object_prefix rbd_children, allow rwx pool=adam1'  -o ceph.client.adam1.keyring
Error EINVAL: osd capability parse failed, stopped at 'allow object_prefix rbd_children, allow rwx pool=adam1' of 'allow object_prefix rbd_children, allow rwx pool=adam1'

# 创建用户client.adam1
ceph auth get-or-create client.adam1 mon 'profile rbd' osd 'profile rbd pool=adam1' # ok
# 获取用户client.adam1的密钥文件
ceph auth get client.adam1 -o ceph.client.adam1.keyring
```

```
[global]
fsid = b7432491-955c-4cbd-b223-74b1be877e8e
mon_initial_members = ceph21
mon_host = 192.168.101.21
auth_cluster_required = cephx
auth_service_required = cephx
auth_client_required = cephx
rbd_default_format = 2
```

拷贝ceph-1上/etc/ceph 目录下的文件ceph.conf 和 ceph.client.glance.keyring 文件到/etc/kolla/config/glance/目录下，kolla在部署的时候会将这个目录下`ceph.*`拷贝到对应容器的/etc/ceph/目录下。

## 旧的资料

[openstack ussuri版本基于内网三台物理机集群kolla-ansible部署及与ceph 集群 集成](https://www.cnblogs.com/weiwei2021/p/14200722.html)

[OpenStack集成Ceph](https://www.orchome.com/16757)

https://www.cnblogs.com/MarkGuo/p/17095781.html
安装部署ceph
7、ceph为对接openstack做准备

cephadm rm-cluster => 删除集群?

## 原理

[Redhat 3.12. 引导新存储集群](https://access.redhat.com/documentation/zh-cn/red_hat_ceph_storage/5/html/installation_guide/bootstrapping-a-new-storage-cluster_install)

cephadm 实用程序在 bootstrap 过程中执行以下任务：

- 为本地节点上的新 Red Hat Ceph Storage 集群安装并启动 Ceph 监控守护进程和 Ceph 管理器守护进程，作为容器。
- 创建 /etc/ceph 目录。
- 将公钥的副本写入 Red Hat Ceph Storage 集群的 /etc/ceph/ceph.pub，并将 SSH 密钥添加到 root 用户的 /root/.ssh/authorized_keys 文件中。
- 将 `_admin` 标签应用到 bootstrap 节点。
- 编写与新集群通信所需的最小配置文件到 /etc/ceph/ceph.conf。
- 将 client.admin 管理 secret 密钥的副本写入 /etc/ceph/ceph.client.admin.keyring。
- 使用 Prometheus、Grafana 和其他工具（如 node-exporter 和 alert-manager）部署基本的监控堆栈。

https://www.cnblogs.com/varden/p/15270628.html
引导一个新集群
您需要知道集群的第一个监视器守护程序使用哪个IP 地址。这通常只是第一台主机的 IP。如果有多个网络和接口，请确保选择一个可供访问 Ceph 集群的任何主机访问的网络和接口。

要引导集群：

```
# mkdir -p /etc/ceph
# cephadm bootstrap --mon-ip <mon-ip>
```
此命令将：

- 在本地主机上为新集群创建一个 monitor 和 manager 守护进程。
- 为 Ceph 集群生成一个新的 SSH 密钥并将其添加到 root 用户的/root/.ssh/authorized_keys文件中。
- 将与新集群通信所需的最小配置文件写入/etc/ceph/ceph.conf.
- 将client.admin管理（特权！）密钥的副本写入/etc/ceph/ceph.client.admin.keyring.
- 将公钥的副本写入 /etc/ceph/ceph.pub.

## FAQ

#### handle_auth_bad_method server allowed_methods [2] but i only support [2,1]

https://stackoverflow.com/questions/72193315/monclienthunting-handle-auth-bad-method-server-allowed-method

错误的keyring名称, 改正确就好了
```
rbd ls --pool adam1 -n client.adam1
```

## 参考资料

- [cephadm部署集群 - 官方文档](https://docs.ceph.com/en/latest/cephadm/install/#cephadm-deploying-new-cluster)
