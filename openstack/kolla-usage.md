# kolla部署openstack

## Kolla 概述

Kolla是OpenStack下用于自动化部署的一个项目，它基于docker和ansible来实现，其中docker主要负责镜像制作和容器管理，ansible主要负责环境的部署和管理。Kolla实际上分为两部分：Kolla部分提供了生产环境级别的镜像，涵盖了OpenStack用到的各个服务；Kolla-ansible部分提供了自动化的部署。最开始这两部分是在一个项目中的（即Kolla），OpenStack从O开头的版本开始被独立开来，这才有了用于构建所有服务镜像的Kolla项目，以及用于执行自动化部署的Kolla-ansible。

原文链接：https://blog.csdn.net/Skywin88/article/details/123124499

## ubuntu 20.04 server安装

参考官方文档: https://docs.openstack.org/project-deploy-guide/kolla-ansible/latest/quickstart.html
安装yoga版本, 参考: https://docs.openstack.org/project-deploy-guide/kolla-ansible/yoga/quickstart.html

参考: [kolla-ansible部署openstack yoga版本](https://blog.csdn.net/qq_43626147/article/details/124971363)

虚拟机安装: 双网卡, 8u16G, cpu直通
最低配置如下:
- 2 个网络接口（或者单个网络接口配置子接口）
- 8GB 主内存
- 40GB 磁盘空间

#### 安装配置ubuntu系统

* 下载ubuntu-20.04.4-live-server-amd64.iso
* 选择语言English
* 配置网卡静态ip地址
* 选择安装磁盘sda
* 配置主机名等
* 配置用户名密码xxx
* 选择安装openssh-server
* 最后开始安装, 安装完成后重启

可选优化:
* 时区配置, 时间同步配置
* 修改apt源为国内阿里源
* 修改pip源为国内豆瓣源

#### (可选)配置本地apt,pip等镜像仓库

可选, 加速相关软件包的安装

例如，配置本地nexus3搭建的镜像仓库

pip镜像仓库
```
cat > /etc/pip.conf << EOF
[global]
index-url = http://docker.iefcu.cn:5565/repository/aliyun-pypi/simple
trusted-host = docker.iefcu.cn
EOF
```

apt镜像仓库(配置完成后需要生效apt update)
```
cat > /etc/apt/sources.list << EOF
deb http://docker.iefcu.cn:5565/repository/ubuntu-cn-proxy focal main restricted
deb http://docker.iefcu.cn:5565/repository/ubuntu-cn-proxy focal-updates main restricted
deb http://docker.iefcu.cn:5565/repository/ubuntu-cn-proxy focal universe
deb http://docker.iefcu.cn:5565/repository/ubuntu-cn-proxy focal-updates universe
deb http://docker.iefcu.cn:5565/repository/ubuntu-cn-proxy focal multiverse
deb http://docker.iefcu.cn:5565/repository/ubuntu-cn-proxy focal-updates multiverse
deb http://docker.iefcu.cn:5565/repository/ubuntu-cn-proxy focal-backports main restricted universe multiverse
deb http://docker.iefcu.cn:5565/repository/ubuntu-cn-proxy focal-security main restricted
deb http://docker.iefcu.cn:5565/repository/ubuntu-cn-proxy focal-security universe
deb http://docker.iefcu.cn:5565/repository/ubuntu-cn-proxy focal-security multiverse
EOF
```

#### 安装docker

(kolla-ansible也可以自动帮我们安装全套的运行环境，包括docker)

参考官方文档安装: https://docs.docker.com/engine/install/ubuntu/

#### 安装python3等依赖

安装python3等依赖(参考官方文档)
```
apt install -y git python3-dev libffi-dev gcc libssl-dev \
  python3-docker python3-pip
```

安装pip，安装ansible等依赖
```
#pip install -U pip # 可选吧, 已经使用apt安装了略低版本的pip, 可以用
pip install 'ansible>=4,<6' # yoga版本
```

#### 安装Kolla-ansible

使用pip仓库安装yoga版本
```
# 供github上下载kolla-ansible，yoga分支
#pip install kolla-ansible==14.0.0
pip install 'kolla-ansible>=14,<15' # yoga版本
```

也可以使用源码安装
```
git clone https://github.com/openstack/kolla-ansible -b stable/yoga
pip install ./kolla-ansible
```

#### 配置kolla-ansible

配置kolla-ansible, 就是globals.yml, passwords.yml
```
# 复制相关文件
mkdir -p /etc/kolla/
cd /usr/local/share/kolla-ansible/
cp -r ./etc_examples/kolla/* /etc/kolla/
cp ./ansible/inventory/* /root/
cp ./init-runonce /root
```

修改密码, 生成密码文件
```
# (可选)自定义web登录密码
sed -i -e 's/^keystone_admin_password:.*/keystone_admin_password: adamxiao/' /etc/kolla/passwords.yml
kolla-genpwd # 随机生成其他密码配置
```

配置 /etc/kolla/globals.yml
```
cat > /etc/kolla/globals.yml << EOF
---
kolla_base_distro: "ubuntu"
kolla_internal_vip_address: "x.x.x.x" # 浮动vip
#docker_registry: "hub.iefcu.cn" # 可选配置使用私有docker镜像仓库
#docker_namespace: "public"
network_interface: "enp4s1" # 内部openstack管理网段
neutron_external_interface: "enp4s2"
#enable_cinder: "yes" # 启用cinder服务
#enable_cinder_backend_lvm: "yes"
#nova_compute_virt_type: "qemu" #使⽤虚拟机部署时，可以不开启嵌套虚拟化, 默认值为kvm  
EOF
```

修改hosts配置, 不然后续rabbitmq连接失败, FIXME: 找一下原因
=> 原来是kolla-ansible bootstrap-servers 会处理这个配置
```
# cat /etc/hosts
# BEGIN ANSIBLE GENERATED HOSTS
10.90.4.100 ubuntu
# END ANSIBLE GENERATED HOSTS
```

#### 开始安装openstack

```
kolla-ansible -i /root/all-in-one bootstrap-servers # 环境安装，这一步会自动安装docker, 配置hosts
# 前提, 需要安装依赖: kolla-ansible install-deps, 但是依赖网络，可能比较慢, 以及失败?

kolla-ansible -i /root/all-in-one prechecks # 在执行部署命令之前，先检查环境是否正确

kolla-ansible -i /root/all-in-one pull # 拉取所有的容器镜像

kolla-ansible -i /root/all-in-one deploy # 安装部署openstack
kolla-ansible -i /root/all-in-one deploy -vvv # -vvv参数可以查看部署命令详情

kolla-ansible -i /root/all-in-one destroy --yes-i-really-really-mean-it # 遇到报错，销毁已安装的环境
```

#### (可选)后续工作

https://www.golinuxcloud.com/deploy-openstack-using-kolla-ansible/

安装openstack客户端
```
pip install python-openstackclient
```

获取openrc配置
```
kolla-ansible post-deploy  /etc/kolla/admin-openrc.sh
source /etc/kolla/admin-openrc.sh
```

初始化cirros镜像,网络,子网,路由,安装组等配置
```
cd /usr/local/share/kolla-ansible/
./init-runonce
```

## 多节点部署

#### 节点规划

计划用的是KVM创建了3台虚拟机。

- 一台作为openstack的manager管理节点，上面跑了openstack的keystone身份认证和RabbitMQ、etcd等基础组件，是openstack的命根子。往后的集群扩容都要连接manager的。CPU核心要足够用，内存要足，网速还要好。存储要求不高，只要一个系统盘，100GB也就够了。
- 一台作为计算节点，是专门运行云服务器的。计算节点的特点是cpu核心和内存要大。存储几乎没要求，云服务器的系统盘和块存储、对象存储、镜像快照存储都由另一台节点提供。
- 一台作为存储节点，上面运行cinder、glance、swift等openstack存储组件。所以这类存储节点的特点就是磁盘大，网络快（不然虚拟机访问他的系统盘岂不是特别卡？）。

硬件规划

- 主机名：kolla-manager。算力：4核8GB。硬盘：200GB系统盘。网络：两个网卡都使用。IP分别是10.0.0.201和192.168.100.201
- 主机名：kolla-compute1。算力：6核16GB。硬盘：200GB系统盘。网络：两张网卡都使用。IP分别是10.0.0.202和192.168.100.202
- 主机名：kolla-storage。算力：2核4GB，硬盘200GB系统盘，另外添加两个250GB的额外硬盘，后面会把这两块盘合并成一个500GB的VG。网络：两张网卡都使用。（其实只用那个叫openstack的网卡就够了，再加一个不吃亏）IP分别是10.0.0.203和192.168.100.203

#### 配置multinode

```
vim ~/multinode
----------------------------------------
# 文件开头新增这3行，自行修改密码
manager ansible_host=10.0.0.201 ansible_user=root ansible_password=123456 ansible_python_interpreter=/usr/bin/python3
compute1 ansible_host=10.0.0.202 ansible_user=root ansible_password=123456 ansible_python_interpreter=/usr/bin/python3
storage1 ansible_host=10.0.0.203 ansible_user=root ansible_password=123456 ansible_python_interpreter=/usr/bin/python3

# 修改这几个组，其他的保留不变
[control] 
manager

[network]
control
compute1
storage1

[compute] 
compute1

[monitoring]
manager

[storage]
storage1

[deployment]
localhost ansible_connection=local become=true
```

其实通过查看原始的multinode文件，你可以发现，kolla将你所有的节点划分成了5种类型，即control类节点、network类节点、compute类、monitoring类节点、storage类节点。
这5个节点组是其他组的子组。

比方说文件下方有很多组件，比如loadbalance、trove等，都是[xxx:children]的形式，这个意思就是自由的组合这5个组。
加入我是生产环境的负责人，我手上有100台服务器，那么我会先计划将这100台机器分成5个类型。然后考虑openstack中哪些组件部署在哪种类型的节点上。

如nova是openstack的计算组件，我想把它安装在control和compute类型的机器上，我就会写
```
[nova:children]
control
compute
```

## 基于centos7云镜像, 安装docker，部署openstack

参考: [kolla单节点部署openstack](https://www.cnblogs.com/navysummer/p/14278131.html)
目前kolla-ansible不支持centos7,这个安装完成运行还不知道会有什么异常问题，安装是成功的

hostnamectl set-hostname kolla

#### 安装python3

安装各种依赖环境 => 失败, pip不再支持低版本python了(以及ansible等)
centos7 install python38
https://blog.csdn.net/fen_fen/article/details/123520752
```
# 参考: https://tecadmin.net/install-python-3-7-on-centos/
# 1. 安装依赖
yum install gcc openssl-devel bzip2-devel libffi-devel zlib-devel xz-devel
# 2.下载源码
cd /usr/src  
wget https://www.python.org/ftp/python/3.8.12/Python-3.8.12.tgz
tar xzf Python-3.8.12.tgz
# 3. 编译安装
cd Python-3.8.12 
./configure --enable-optimizations 
make altinstall 
# 建立Python3的软连接, 别名?
ln -sf /usr/local/bin/pip3.8 /usr/local/bin/pip
ln -sf /usr/local/bin/python3.8 /usr/local/bin/python
ln -sf /usr/local/bin/python3.8 /usr/bin/python
```

#### 安装kolla-ansible准备工作

```
yum install -y git libffi-devel gcc openssl-devel
pip install 'ansible>=4,<6'
```

最后安装kolla-ansible, 安装openstack

## 其他资料

[kolla一键部署openstack](https://zhuanlan.zhihu.com/p/144742124)
[Kolla部署openstack单节点-train](https://zhuanlan.zhihu.com/p/143029344)
=> 一样的, failed, 但是有参考 价值

- [kolla单节点部署openstack](https://www.cnblogs.com/navysummer/p/14278131.html)
  => failed 关键是kolla-ansible 示例配置文件不对

- [ubuntu20.04LTS单节点kolla部署openstack-train版本](https://blog.csdn.net/Skywin88/article/details/123124499)
  参考官方安装文档: https://docs.openstack.org/project-deploy-guide/kolla-ansible/latest/quickstart.html

https://blog.51cto.com/u_15301988/3085246
NOTE：进行多节点部署，还需要部署 Local Docker Register 服务器，搭建 Docker 私有仓库，详细请浏览：
 https://docs.openstack.org/kolla-ansible/latest/user/multinode.html


https://developer.aliyun.com/article/459561
小试牛刀之Kolla单节点部署

下载Kolla源码
```
git clone https://github.com/openstack/kolla-ansible
# 源码安装kolla-ansible
cd kolla-ansible
pip install .
# 复制相关文件
cp -r etc/kolla /etc/kolla/
cp ansible/inventory/* /root/
```

修改密码
```
# 编辑 /etc/kolla/password
keystone_admin_password: adamxiao
# 生成密码
kolla-genpwd
```

安装openstack
```
kolla-ansible deploy -i /root/all-in-one
```

kolla-ansible虚拟机单节点部署OpenStack
https://blog.csdn.net/qq_16942727/article/details/121081515

## 其他资料

#### 安装ceph

https://developer.aliyun.com/article/514108

1.增加一块硬盘，/dev/sdb，然后分区：
```
parted /dev/vdb -s -- mklabel gpt mkpart KOLLA_CEPH_OSD_BOOTSTRAP 1 -1
```

2.配置ceph：

创建/etc/kolla/config/ceph.conf：
```
[global]
osd pool default size = 2
osd pool default min size = 1
```
上面的配置表示ceph的对象存储副本数是2，最小副本数是1     

3.修改/etc/kolla/global.yml文件：
```
enable_cinder: "yes"
enable_ceph: "yes"
enable_ceph_rgw: "yes"
enable_ceph_rgw_keystone: "yes"
glance_backend_ceph: "yes"
```

4.修改/root/kolla-ansible-4.0.3.dev36/ansible/inventory/all-in-one文件，将localhost改为control01：
```
vim /root/kolla-ansible-4.0.3.dev36/ansible/inventory/all-in-one
:%s/localhost/control01/g
```
注意，多节点实现方法也是一样的。
=> 为什么配置名称为control01 ???

```
fatal: [control01]: FAILED! => {"changed": false, "msg": "We are sorry but enable_ceph is no longer supported. Please use external ceph support."}
```

#### 配置使用external ceph

[openstack kolla - External Ceph](https://docs.openstack.org/kolla-ansible/yoga/reference/storage/external-ceph-guide.html)

enable_cinder: "yes"

配置cinder
1.配置启用cinder ceph
```
cinder_backend_ceph: "yes"
```
2.配置ceph auth
```
ceph_cinder_keyring (default: ceph.client.cinder.keyring)
ceph_cinder_user (default: cinder)
ceph_cinder_pool_name (default: volumes)
ceph_cinder_backup_keyring (default: ceph.client.cinder-backup.keyring)
ceph_cinder_backup_user (default: cinder-backup)
ceph_cinder_backup_pool_name (default: backups)
```
3.配置(或拷贝) `/etc/kolla/config/cinder/ceph.conf`
4.配置(或拷贝) Ceph keyring file(s):
`/etc/kolla/config/cinder/cinder-volume/<ceph_cinder_keyring>`

配置nova使用外部ceph
1.启用nova ceph, 配置globals.yml
```
nova_backend_ceph: "yes"
```
2.配置nova ceph密钥, 配置globals.yml
```
ceph_nova_keyring (by default it’s the same as ceph_cinder_keyring)
ceph_nova_user (by default it’s the same as ceph_cinder_user)
ceph_nova_pool_name (default: vms)
```
3.配置(或拷贝) `/etc/kolla/config/nova/ceph.conf`
4.配置(或拷贝) Ceph keyring file(s):
`/etc/kolla/config/nova/<ceph_nova_keyring>`


#### 启用cinder-backup

参考配置, 可以使用nfs, swift, ceph等作为后端存储
```
# Valid options are [ nfs, swift, ceph ]
#cinder_backup_driver: "ceph"
#cinder_backup_share: ""
#cinder_backup_mount_options_nfs: ""
```

使用nfs作为后端存储配置示例:
```
cinder_backup_driver: "nfs"
cinder_backup_share: "10.90.3.25:/mnt/pool1/openstack-backup/10.90.4.113"
#cinder_backup_mount_options_nfs: "" # 暂不配置
```

#### kolla启用swift

关键字《kolla-ansible启用 swift》

[openstack对接swift对象存储](https://blog.csdn.net/networken/article/details/107405215)

- 准备磁盘
  sda为系统盘，由于启用了cinder，sdb作为cinder卷，因此额外准备3块磁盘sdc sdd sde用于swift对象存储。如果磁盘资源不足也可以使用一块盘创建3个分区。
  3块磁盘分区格式化，并打上KOLLA_SWIFT_DATA标签，
```
index=0
for d in vdc vdd vde; do
    parted /dev/${d} -s -- mklabel gpt mkpart KOLLA_SWIFT_DATA 1 -1
    sudo mkfs.xfs -f -L d${index} /dev/${d}1
    (( index++ ))
done
```
- 生成rings
- 生成Object Ring
- 生成Account Ring
- 生成Container Ring
- 再平衡


[Configure Swift on OpenStack Ocata standalone with Kolla](https://blog.inkubate.io/configure-swift-on-openstack-ocata-standalone-with-kolla/)
=> 关键是准备工作!

其他swift资料?
关键字《openstack swift部署》
[Openstack Swift 安装部署总结](https://blog.csdn.net/ch648966459/article/details/79315643)
https://blog.fatedier.com/2016/05/25/deploy-openstack-swift/

#### kolla启用freezer

配置globals.yml
```
enable_freezer: "yes"
```

后来发现报错`'dict object' has no attribute 'domain_name'`
使用github的yoga版本kolla-ansible即可? => 确实是的, 估计安装pip官方高版本kolla-ansible也行
```
pip install 'kolla-ansible>=14,<15' # yoga版本
```

安装freezer客户端
```
apt install python3-freezerclient
```

#### kolla启用cinder

禁用宿主机上的iscsi相关服务
```
systemctl stop iscsid.socket iscsid.service tgt.service
systemctl disable iscsid.socket iscsid.service tgt.service
```

=> 有问题，无法验证成功
镜像问题centos-source-tgtd not found
=> 使用了binary镜像替换就行了...

https://docs.openstack.org/kolla-ansible/yoga/reference/storage/cinder-guide.html

配置globals.yml
```
enable_cinder: "yes"
enable_cinder_backend_lvm: "yes"
#cinder_volume_group: "cinder-volumes"
```

准备卷工作
```
pvcreate /dev/vdb
vgcreate cinder-volumes /dev/vdb

# 或者开发阶段，使用loop文件弄
free_device=$(losetup -f)
fallocate -l 20G /var/lib/cinder_data.img
losetup $free_device /var/lib/cinder_data.img
pvcreate $free_device
vgcreate cinder-volumes $free_device
```


#### 同步kolla docker镜像

[openstack拉取kolla docker镜像到阿里云镜像仓库](https://blog.csdn.net/networken/article/details/106717259)

kolla所有组件的镜像名称在kolla项目中可以找到：
https://github.com/openstack/kolla/tree/master/docker

docker下的目录和二级目录名称跟docker镜像名称相关，所以可以遍历这些目录名称，获取所有目录名称的列表。

kolla镜像格式有一定规则，例如：
```
kolla/centos-source-nova-compute:ussuri
仓库名称/OS版本-包类型-组件名称:openstack版本
```

#### 使用本地docker镜像仓库

[容器化部署OpenStack的正确姿势](https://gist.github.com/baymaxium/6b295d44bc2aa9fce91d237de56e9d57)

编辑 /etc/kolla/globals.yml 配置文件
```
docker_registry: "hub.iefcu.cn"
docker_namespace: "public"
# 最终拉取镜像: hub.iefcu.cn/public/ubuntu-source-haproxy
```

同步如下镜像
```
# %s#.*#,"quay.io/openstack.kolla/&:yoga":"${dst_hub}/public/&"
# quay.io/openstack.kolla/ubuntu-source-fluentd:yoga
ubuntu-source-mariadb-server:yoga
ubuntu-source-mariadb-clustercheck:yoga
ubuntu-source-memcached:yoga
ubuntu-source-keepalived:yoga
ubuntu-source-kolla-toolbox:yoga
ubuntu-source-haproxy:yoga
ubuntu-source-rabbitmq:yoga
ubuntu-source-cron:yoga
ubuntu-source-horizon:yoga
ubuntu-source-heat-api:yoga
ubuntu-source-heat-api-cfn:yoga
ubuntu-source-heat-engine:yoga
ubuntu-source-neutron-server:yoga
ubuntu-source-neutron-openvswitch-agent:yoga
ubuntu-source-neutron-l3-agent:yoga
ubuntu-source-neutron-metadata-agent:yoga
ubuntu-source-neutron-dhcp-agent:yoga
ubuntu-source-nova-api:yoga
ubuntu-source-nova-ssh:yoga
ubuntu-source-nova-scheduler:yoga
ubuntu-source-nova-conductor:yoga
ubuntu-source-nova-novncproxy:yoga
ubuntu-source-nova-compute:yoga
ubuntu-source-nova-libvirt:yoga
ubuntu-source-glance-api:yoga
ubuntu-source-placement-api:yoga
ubuntu-source-keystone:yoga
ubuntu-source-keystone-ssh:yoga
ubuntu-source-keystone-fernet:yoga
ubuntu-source-openvswitch-db-server:yoga
ubuntu-source-openvswitch-vswitchd:yoga
```

执行安装OpenStack的命令
kolla-ansible deploy -i /home/all-in-one -vvvv
=> 约花费30min

2）除此外，还有一些小工具，在自己需要时，可以使用。
- kolla-ansible prechecks : 在执行部署命令之前，先检查环境是否正确；
- tools/cleanup-containers : 可用于从系统中移除部署的容器；
- tools/cleanup-host : 可用于移除由于网络变化引发的Docker启动的neutron-agents主机；
- tools/cleanup-images : 可用于从本地缓存中移除所有的docker image。

[使用kolla快速部署openstack all-in-one环境](https://cloud.tencent.com/developer/article/1158764)
kolla-build


#### 构建kolla容器镜像

https://docs.openstack.org/kolla/latest/admin/image-building.html
官方构建方法

```
apt install -y python3-pip
pip install kolla
kolla-build # 默认参数，构建所有镜像
kolla-build nova-libvirt # 单独编译libvirt
kolla-build -b ubuntu nova-libvirt # 单独编译libvirt, 基于ubuntu
```

其他参数
- --template-only
  仅仅生成Dockerfile

关键字《kolla镜像本地缓存》

https://www.sdnlab.com/17273.html

```
git clone https://github.com/openstack/kolla.git
cd kolla
# yum install python-devel # centos系列处理
sudo apt install python3-pip
pip install -r requirements.txt -r test-requirements.txt tox
```

以下如果没有特别说明，所有的操作都是在 Kolla 项目的目录里进行
首先要先生成并修改配置文件
```
tox -e genconfig
cp -rv etc/kolla /etc/
```

[使用 Kolla 构建 Pike 版本 OpenStack Docker 镜像](https://my.oschina.net/LastRitter/blog/1788277)

生成 Dockerfile
使用 Pike 版本的默认配置生成 source 类型的 Dockerfile：
```
python tools/build.py -t source --template-only --work-dir=..
```

https://www.cnblogs.com/potato-chip/p/10100667.html
kolla-build镜像时，问题汇总

[管理2000+Docker镜像，Kolla是如何做到的](https://blog.51cto.com/u_9443135/3720391)

[OpenStack Kolla源码分析–Ansible ](https://blog.51cto.com/u_15127593/2749775)

#### cinder配置

openstack service list
=> 默认没有启用cinder

cinder_target_helper(kolla-ansible源码中定义)
提供iscsi服务的程序，redhat是lioadm, 其他是tgtadm
=> 对应镜像问题centos-source-tgtd not found

#### 其他

[(好)kolla-ansible部署openstack yoga版本](https://blog.csdn.net/qq_43626147/article/details/124971363)
=> 多节点部署

[Kolla 让 OpenStack 部署更贴心](https://blog.51cto.com/u_15301988/3085246)

支持开发模式。这个对 OpenStack 的开发者很是方便。以住，开发者可能要通过 devstack 搭建完整的 OpenStack 来开发，但是部署复杂，难度高。现在 kolla-ansible 已经支持了开发模式。通过配置要开发环境的 dev_mode, 如 horizon_dev_mode: true, 那么 horizon 容器内的代码会从物理机上挂载进去，开发者对代码修改后，就可以直接看到修改后的效果。十分方便。

为了提高部署效率，这里调整了一些参数，更多 Ansible 配置项目，请浏览：
https://docs.ansible.com/ansible/latest/reference_appendices/config.html#ansible-configuration-settings

修改 ansible 配置文件：
```
mkdir /etc/ansible
vim /etc/ansible/ansible.cfg
[defaults]
host_key_checking=False
pipelining=True
forks=100
deprecation_warnings=False
```

https://developer.aliyun.com/article/459561
验证部署
kolla-ansible post-deploy

kolla-ansible deploy-containers

## FAQ

#### the role 'openstack.kolla.baremetal' was not found

执行bootstrap-server失败

https://bugs.launchpad.net/kolla-ansible/+bug/1975734
=> 原来是需要安装依赖 Install Ansible Galaxy requirements
=> 执行了一个命令解决`kolla-ansible install-deps`

#### ERROR: kolla_ansible has to be available in the Ansible PYTHONPATH.

https://bugs.launchpad.net/kolla-ansible/+bug/1903923
It's not a bug. Make sure you install both Ansible and Kolla Ansible into the same environment (e.g. both to system, both to user or both to the same venv).

=> 指的就是kolla-ansible安装位置不对?
验证发现之前可能用了其他的python安装的ansible，安装一下即可
```
pip3 install ansible
pip install 'ansible>=4,<6'
=> 不知道有一些什么区别???
```

#### ERROR: Ansible version should be between 2.9 and 2.10. Current version is 2.11.12 which is not supported.

ansible版本不匹配，安装对应的版本

```
kolla-ansible deploy -i /root/all-in-one
ERROR: Ansible version should be between 2.9 and 2.10. Current version is 2.11.12 which is not supported.
```

```
ERROR: Ansible version should be between 2.10 and 2.11. Current version is 2.12.10 which is not supported.
=> pip install --user ansible==4.9.0
Successfully installed ansible-4.9.0 ansible-core-2.11.12
```
=> 查看xena官方文档: https://docs.openstack.org/project-deploy-guide/kolla-ansible/xena/quickstart.html
```
pip install 'ansible<5.0'
```

#### ModuleNotFoundError: No module named 'docker'

https://stackoverflow.com/questions/53941356/failed-to-import-docker-or-docker-py-no-module-named-docker
```
pip install docker
=> 上面不行
apt install -y python3-docker
=> 可以了???
```

#### rabbitmq启动失败: ERROR: epmd error for host openStack: address (cannot connect to host/port)

关键字《kolla deploy disable rabbitmq》
https://bugs.launchpad.net/kolla-ansible/+bug/1855935
[kolla deploy fails due to continuous restart of rabbitmq](https://bugs.launchpad.net/kolla-ansible/+bug/1840369)

修改hosts配置
```
root@kolla2:/home/adam# cat /etc/hosts
127.0.0.1 localhost
10.90.3.22 kolla2
```

=> kolla-ansible bootstrap-servers也会自动处理

#### TASK [service-rabbitmq : nova | Ensure RabbitMQ users exist]

关键字《service-rabbitmq : nova | Ensure RabbitMQ users exist》

https://bugs.launchpad.net/kolla-ansible/+bug/1946506
=> 是bug, 在This issue was fixed in the openstack/kolla-ansible 14.0.0.0rc1 release candidate.
意味着我用的xena版本需要升级

```
failed: [localhost -> localhost] (item=None) => {
    "attempts": 5,
    "censored": "the output has been hidden due to the fact that 'no_log: true' was specified for this result",
    "changed": false
}
fatal: [localhost -> {{ service_rabbitmq_delegate_host }}]: FAILED! => {
    "censored": "the output has been hidden due to the fact that 'no_log: true' was specified for this result",
    "changed": false
}
```

```
pip install --user ansible==4.9.0 # 5.0版本 rabbitmq user问题?
```
=> 关机后再弄就可以了?

#### TASK [neutron : Copying over ssh key]

尝试ssh-keygen和copy ssh key不行
=> 原来是我使用xena版本的password配置, 没有neutron_ssh_key这个字段

```
The full traceback is:
Traceback (most recent call last):
  File "/usr/local/lib/python3.8/dist-packages/ansible/template/__init__.py", line 1121, in do_template
    res = j2_concat(rf)
  File "<template>", line 12, in root
  File "/usr/local/lib/python3.8/dist-packages/jinja2/runtime.py", line 852, in _fail_with_undefined_error
    raise self._undefined_exception(self._undefined_message)
jinja2.exceptions.UndefinedError: 'neutron_ssh_key' is undefined

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/local/lib/python3.8/dist-packages/ansible/plugins/action/template.py", line 146, in run
    resultant = templar.do_template(template_data, preserve_trailing_newlines=True, escape_backslashes=False)
  File "/usr/local/lib/python3.8/dist-packages/ansible/template/__init__.py", line 1160, in do_template
    raise AnsibleUndefinedVariable(e)
ansible.errors.AnsibleUndefinedVariable: 'neutron_ssh_key' is undefined
fatal: [localhost]: FAILED! => {
    "changed": false,
    "msg": "AnsibleUndefinedVariable: 'neutron_ssh_key' is undefined"
}
```

#### ImportError: No module named docker

没有docker模块, 安装一下

#### rabbitmq : Check if all rabbit hostnames are resolvable

修改/etc/hosts，配置域名解析问题
把所有控制节点域名ip配置能通, 例如在所有控制节点，配置如下:
```
192.168.99.11 kolla-manager
192.168.99.12 kolla-compute1
192.168.99.13 kolla-storage
```

getent ahostsv4 kolla-manager
=> 获取域名的ipv4地址?

```
TASK [rabbitmq : Check if all rabbit hostnames are resolvable] ********************************************************************************************************************************************
ok: [manager] => (item=manager)
failed: [compute1] (item=manager) => {"ansible_loop_var": "item", "changed": false, "cmd": ["getent", "ahostsv4", "kolla-manager"], "delta": "0:00:00.004259", "end": "2023-03-19 09:22:17.341381", "item": "manager", "msg": "non-zero return code", "rc": 2, "start": "2023-03-19 09:22:17.337122", "stderr": "", "stderr_lines": [], "stdout": "", "stdout_lines": []}
failed: [storage1] (item=manager) => {"ansible_loop_var": "item", "changed": false, "cmd": ["getent", "ahostsv4", "kolla-manager"], "delta": "0:00:00.004073", "end": "2023-03-19 09:22:17.330757", "item": "manager", "msg": "non-zero return code", "rc": 2, "start": "2023-03-19 09:22:17.326684", "stderr": "", "stderr_lines": [], "stdout": "", "stdout_lines": []}
failed: [manager] (item=compute1) => {"ansible_loop_var": "item", "changed": false, "cmd": ["getent", "ahostsv4", "kolla-compute1"], "delta": "0:00:00.003860", "end": "2023-03-19 09:22:17.556769", "item": "compute1", "msg": "non-zero return code", "rc": 2, "start": "2023-03-19 09:22:17.552909", "stderr": "", "stderr_lines": [], "stdout": "", "stdout_lines": []}
failed: [storage1] (item=compute1) => {"ansible_loop_var": "item", "changed": false, "cmd": ["getent", "ahostsv4", "kolla-compute1"], "delta": "0:00:00.003279", "end": "2023-03-19 09:22:17.637459", "item": "compute1", "msg": "non-zero return code", "rc": 2, "start": "2023-03-19 09:22:17.634180", "stderr": "", "stderr_lines": [], "stdout": "", "stdout_lines": []}
ok: [compute1] => (item=compute1)
failed: [manager] (item=storage1) => {"ansible_loop_var": "item", "changed": false, "cmd": ["getent", "ahostsv4", "kolla-storage"], "delta": "0:00:00.003402", "end": "2023-03-19 09:22:17.911023", "item": "storage1", "msg": "non-zero return code", "rc": 2, "start": "2023-03-19 09:22:17.907621", "stderr": "", "stderr_lines": [], "stdout": "", "stdout_lines": []}
ok: [storage1] => (item=storage1)
failed: [compute1] (item=storage1) => {"ansible_loop_var": "item", "changed": false, "cmd": ["getent", "ahostsv4", "kolla-storage"], "delta": "0:00:00.003808", "end": "2023-03-19 09:22:17.971527", "item": "storage1", "msg": "non-zero return code", "rc": 2, "start": "2023-03-19 09:22:17.967719", "stderr": "", "stderr_lines": [], "stdout": "", "stdout_lines": []}
```
