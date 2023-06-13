# devstack安装openstack集群

疑问:
* 1.在多节点配置时，一般保留私有地址的前十个, 什么意思?
* 最后还是有github的etcd文件下载
https://github.com/etcd-io/etcd/releases/download/v3.3.12/etcd-v3.3.12-linux-amd64.tar.gz

## 单节点allinone安装

最新版devstack(yoga)支持ubuntu 20.04, 旧版本ubuntu未适配了

### 安装基础系统ubuntu 20.04 server

之前就尝试过, 现在使用ubuntu 20.04安装Yoga版本成功 - 2022-05-11

* 下载ubuntu-20.04.4-live-server-amd64.iso
* 选择语言English
* 配置网卡静态ip地址
* 选择安装磁盘vda
* 配置用户名密码xxx
* 选择安装openssh-server
* 最后开始安装, 安装完成后重启

可选优化(我暂时没做):
* 时区配置, 时间同步配置
* 修改apt源为国内阿里源
* 修改pip源为国内豆瓣源?

最后关闭虚拟机, 克隆几个副本出来, 修改主机名和ip地址:
```bash
hostnamectl set-hostname xxx
```

#### 修改ip地址

[ubuntu server修改配置静态ip地址](https://www.myfreax.com/how-to-configure-static-ip-address-on-ubuntu-18-04/)

修改配置文件 /etc/netplan/xxx.yaml
```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    ens3:
      dhcp4: no
      addresses:
        - 192.168.121.199/24
      gateway4: 192.168.121.1
      nameservers:
          addresses: [8.8.8.8, 8.8.4.4]
```

ip修改配置生效
```bash
sudo netplan apply
```

#### 修改apt软件源

自己搭建的私有nexus源, 缓存之后速度非常快

配置focal, ubuntu 20.04的源: /etc/apt/sources.list
```
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
```

#### 修改pip仓库源

自己搭建的私有nexus源, 缓存之后速度非常快

```
#mkdir -p $HOME/.pip
#$HOME/.pip/pip.conf
cat > /etc/pip.conf << EOF
[global]
index-url = http://docker.iefcu.cn:5565/repository/aliyun-pypi/simple
trusted-host = docker.iefcu.cn
EOF
```

### 安装准备工作

#### 配置代理

可选, 需要访问github, 下载apt, pypi软件包, 配置代理比较合适, openstack节点都可以不需要外网权限

参考: [代理配置](../tricks/proxy.md)

#### 安装git基础软件

```bash
sudo apt install -y git
```

#### 创建stack用户

创建一个用户来运行DevStack, 参考devstack的脚本[create-stack-user.sh](https://github.com/openstack/devstack/blob/master/tools/create-stack-user.sh)
```bash
sudo useradd -s /bin/bash -d /opt/stack -m stack
echo "stack ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/stack
```

### 安装allinone环境

#### 下载devstack工具

切到stack用户, 下载DevStack
```bash
sudo su - stack
#git clone https://github.com/openstack-dev/devstack -b stable/yoga
# 使用私有git代码
git clone https://gitlab.iefcu.cn/openstack/devstack.git -b stable/yoga
```

#### 配置local.conf进行安装

编写local.conf配置文件(注意修改ip等信息)
尝试使用私有git代码仓库来部署openstack
=> GIT_BASE字段, 项目名必须为openstack ...
```ini
[[local|localrc]]
# Define images to be automatically downloaded during the DevStack built process.
DOWNLOAD_DEFAULT_IMAGES=False
IMAGE_URLS="http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img"

# use adam git mirror
GIT_BASE=https://gitlab.iefcu.cn
NOVNC_REPO=https://gitlab.iefcu.cn/openstack/noVNC.git
SPICE_REPO=https://gitlab.iefcu.cn/openstack/spice-html5.git

# Credentials
DATABASE_PASSWORD=admin
ADMIN_PASSWORD=admin
SERVICE_PASSWORD=admin
SERVICE_TOKEN=admin
RABBIT_PASSWORD=admin
#FLAT_INTERFACE=enp0s3 => ag devstack 没有

HOST_IP="your vm ip"
```

尝试: 由于devstack无法在localrc中配置项目名, 所有手动修改一下
=> 最后使用nginx的rewrite模块更好`rewrite /openstack/(.*) /adam/$1 break;`
```
#CINDER_REPO=${CINDER_REPO:-${GIT_BASE}/openstack/cinder.git}
sed -i -e 's#:-${GIT_BASE}/openstack/#:-${GIT_BASE}/adam/#' stackrc
```

切换到files目录下，执行如下命令
(可选把, 为啥要这样做?)
(注: devstack的stackrc配置文件定义了etcd的版本)
```bash
cd files/
# 这里可以通过代理下载
https_proxy=http://proxy.iefcu.cn:20172 wget https://github.com/etcd-io/etcd/releases/download/v3.3.12/etcd-v3.3.12-linux-amd64.tar.gz -O /opt/stack/devstack/files/etcd-v3.3.12-linux-amd64.tar.gz
http_proxy=http://proxy.iefcu.cn:20172 https_proxy=http://proxy.iefcu.cn:20172 wget http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img -O /opt/stack/devstack/files/cirros-0.3.4-x86_64-disk.img


https://github.com/etcd-io/etcd/releases/download/v3.3.12/etcd-v3.3.12-linux-amd64.tar.gz
++functions:get_extra_file:68               wget --progress=dot:giga -t 2 -c https://github.com/etcd-io/etcd/releases/download/v3.3.12/etcd-v3.3.12-linux-amd64.tar.gz -O /opt/stack/devstack/files/etcd-v3.3.12-linux-amd64.tar.gz
+functions:upload_image:142                wget --progress=dot:giga -c http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img -O /opt/stack/devstack/files/cirros-0.3.4-x86_64-disk.img
```

切回到/devstack目录下, cd ..

运行 ./stack.sh

安装完成
```
=========================
DevStack Component Timing
 (times are in seconds)
=========================
wait_for_service      16
pip_install          398
apt-get              983
run_process           30
dbsync                 6
git_timed            690
apt-get-update         6
test_with_retry        5
async_wait           138
osc                  249
-------------------------
Unaccounted time     206
=========================
Total runtime        2727

=================
 Async summary
=================
 Time spent in the background minus waits: 398 sec
 Elapsed time: 2727 sec
 Time if we did everything serially: 3125 sec
 Speedup:  1.14595



This is your host IP address: 10.90.3.33
This is your host IPv6 address: ::1
Horizon is now available at http://10.90.3.33/dashboard
Keystone is serving at http://10.90.3.33/identity/
The default users are: admin and demo
The password: admin

Services are running under systemd unit files.
For more information see:
https://docs.openstack.org/devstack/latest/systemd.html

DevStack Version: zed
Change: d450e146ccc9b43ce151f57523e4e4c88b9fdafb Merge "Global option for enforcing scope (ENFORCE_SCOPE)" 2022-05-07 10:51:35 +0000
OS Version: Ubuntu 20.04 focal

2022-05-11 04:34:10.467 | stack.sh completed in 2727 seconds.
```


## 集群安装

目前就是简单的添加额外的计算节点

https://blog.csdn.net/m0_49212388/article/details/107606727
请参考devstack官方文档[《Multi-Node Lab》](https://docs.openstack.org/devstack/latest/guides/multinode-lab.html)

参考[openstack部署方式](https://zhuanlan.zhihu.com/p/44905003)
选用[devstack](https://github.com/openstack/devstack)进行安装

[openstack基础架构以及部署资料 (好)](https://cloud.tencent.com/developer/article/1026128)

#### 集群节点配置准备

* 修改hostname和ip
* 配置ssh互相免密登录
  (可选, 为后续vm迁移使用)
* xxx

注意，首先安装控制节点，再控制节点安装成功后，再安装nova计算节点，计算节点和控制节点之间要通讯正常。

#### (可选)注入密钥

未验证密钥真实用处

注入密钥 => 测试ok
```bash
# 手动注入ssh密钥到stack用户?
# sudo su - stack
mkdir ~/.ssh; chmod 700 ~/.ssh
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCaQ9Zpb5/nyiZEw9sR1mqpdpXgRi7WMnSeDyF2R7g7ZH3kUWZhY/Kkf/LoHWeNR82Wb1gq7s5YvEzSAy9R0VnCAGtMZ6nDFR7VgWiqj2q4nexnkrTFSNA6esrAQlpbbtCXLvKSCIUEuZa73naY87H1++DrxA51FqmRlO2ni+qDKlWcl6d/Jr+0Z+JqfWAdKmGmLDtU/L3qol4VIUolMaL1g7I8O07gbQJovXGTVypkoijLdEZ/mYnL6/3ODuPRBQZfw/A7rG39BiBJ3AxU2UYv8Mfh1Cai3CTqyX/k2wxpxDv/bPHH8fj/Qf1Ib7gZmW7KteNpC0pEl4k3r9f7j5xOwkO2D/h1q0/X1w4PdfxdSzIr1SdP1l0bHDcRGUGmrYb2ZDy9M2U14D0JBT9QWWL36CNOKHNYtrE3nu+g7f7nIUHPijc6MkUZ/h1rYsREWdOSwrTSIkmDS2ajH5CLfX+FsXuExiIor1jyhaPzk8r6M2QxgGJwUZxpEdqa5N+Od0wUDRvkjtleElRZE4ssasqTvugfzZnY+gjvyoU7e1VaMUU1WUHjCjSWxOxCUC7Z4G4pHw2u/DReJ4YMq7qsCLenDE3GvcywZXTN3XA0L+69cWFe5eOC7kG5ggAsVOtXyCFk3+DgBA6vmd415RSQeafyfoitHpPpCr3aeYsOlljyDw== root@bastion.openshift4.kylin.com" > ~/.ssh/authorized_keys
```

#### 配置集群local.conf

The cluster controller runs all OpenStack services.

关键就是改动了local.conf吧?
```ini
[[local|localrc]]
#Define images to be automatically downloaded during the DevStack built process.
DOWNLOAD_DEFAULT_IMAGES=False
IMAGE_URLS="http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img"

#用gitclone.com吧，git clone https://gitclone.com/github.com/xxx/yyy.git 
GIT_BASE=https://gitclone.com/github.com
NOVNC_REPO=https://gitclone.com/github.com/kanaka/noVNC.git
SPICE_REPO=https://gitclone.com/github.com/git/spice/sice-html5.git

#Credentials
##根据具体情况设置主机ip
HOST_IP=192.168.42.11
##根据实际情况设定内网ip
FIXED_RANGE=10.4.128.0/20
##根据实际情况设定浮动ip
FLOATING_RANGE=192.168.42.128/25
LOGFILE=/opt/stack/logs/stack.sh.log
ADMIN_PASSWORD=admin
DATABASE_PASSWORD=admin
RABBIT_PASSWORD=admin
SERVICE_PASSWORD=admin
```

#### nova计算节点local.conf配置

[openstack devstack Multi Node配置](https://docs.openstack.org/devstack/latest/guides/multinode-lab.html)
尝试中
```
[[local|localrc]]
HOST_IP=192.168.42.12 # change this per compute node
FIXED_RANGE=10.4.128.0/20
FLOATING_RANGE=192.168.42.128/25
LOGFILE=/opt/stack/logs/stack.sh.log
ADMIN_PASSWORD=labstack
DATABASE_PASSWORD=supersecret
RABBIT_PASSWORD=supersecret
SERVICE_PASSWORD=supersecret
DATABASE_TYPE=mysql
SERVICE_HOST=192.168.42.11
MYSQL_HOST=$SERVICE_HOST
RABBIT_HOST=$SERVICE_HOST
GLANCE_HOSTPORT=$SERVICE_HOST:9292
ENABLED_SERVICES=n-cpu,c-vol,placement-client,ovn-controller,ovs-vswitchd,ovsdb-server,q-ovn-metadata-agent
NOVA_VNC_ENABLED=True
NOVNCPROXY_URL="http://$SERVICE_HOST:6080/vnc_lite.html"
VNCSERVER_LISTEN=$HOST_IP
VNCSERVER_PROXYCLIENT_ADDRESS=$VNCSERVER_LISTEN
```

https://blog.csdn.net/m0_49212388/article/details/107606727
```
[[local|localrc]]
#Define images to be automatically downloaded during the DevStack built process.
DOWNLOAD_DEFAULT_IMAGES=False
IMAGE_URLS="http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img"

#用gitclone.com吧，git clone https://gitclone.com/github.com/xxx/yyy.git 
GIT_BASE=https://gitclone.com/github.com
NOVNC_REPO=https://gitclone.com/github.com/kanaka/noVNC.git
SPICE_REPO=https://gitclone.com/github.com/git/spice/sice-html5.git

#Credentials
HOST_IP=192.168.42.12 # change this per compute node
FIXED_RANGE=10.4.128.0/20
FLOATING_RANGE=192.168.42.128/25
LOGFILE=/opt/stack/logs/stack.sh.log
ADMIN_PASSWORD=admin
DATABASE_PASSWORD=admin
RABBIT_PASSWORD=admin
SERVICE_PASSWORD=admin
DATABASE_TYPE=mysql
SERVICE_HOST=192.168.42.11
MYSQL_HOST=$SERVICE_HOST
RABBIT_HOST=$SERVICE_HOST
GLANCE_HOSTPORT=$SERVICE_HOST:9292
ENABLED_SERVICES=n-cpu,q-agt,c-vol,placement-client
NOVA_VNC_ENABLED=True
NOVNCPROXY_URL="http://$SERVICE_HOST:6080/vnc_lite.html"
VNCSERVER_LISTEN=$HOST_IP
VNCSERVER_PROXYCLIENT_ADDRESS=$VNCSERVER_LISTEN
```

## 更多资料

#### 启用swift

https://blog.51cto.com/u_15301988/3125269#52swift%E8%8A%82%E7%82%B9
```
enable_service s-proxy s-object s-container s-account
```

https://www.cnblogs.com/edisonxiang/p/5051666.html
```
SWIFT_HASH=66a3d6b56c1f479c8b4e70ab5c2000f5 # 干嘛用的? 还必须要填，否则会提示: ENTER A RANDOM SWIFT HASH
SWIFT_REPLICAS=1
```

#### 启用freezer插件

关键字《devstack enable freezer》

https://docs.openstack.org/freezer/latest/install/devstack_plugin.html
修改local.conf配置:
```
enable_plugin freezer-api https://git.openstack.org/openstack/freezer-api.git master
enable_plugin freezer https://git.openstack.org/openstack/freezer.git master
enable_plugin freezer-web-ui https://git.openstack.org/openstack/freezer-web-ui.git master
export FREEZER_BACKEND='sqlalchemy' # 不使用ES作为数据库
```

或者使用本地git仓库
```
enable_plugin freezer-api https://gitlab.iefcu.cn/openstack/freezer-api.git stable/yoga
enable_plugin freezer https://gitlab.iefcu.cn/openstack/freezer.git stable/yoga
enable_plugin freezer-web-ui https://gitlab.iefcu.cn/openstack/freezer-web-ui.git stable/yoga
export FREEZER_BACKEND='sqlalchemy' # 不使用ES作为数据库, ES部署暂时有问题...
```

#### openstack git镜像仓库

根据devstack里面的stackrc配置，可以看到官方git仓库是opendev.org
```
GIT_BASE=${GIT_BASE:-https://opendev.org}
NOVNC_REPO=${NOVNC_REPO:-https://github.com/novnc/novnc.git}
SPICE_REPO=${SPICE_REPO:-http://anongit.freedesktop.org/git/spice/spice-html5.git}
```

有如下一些git镜像仓库, 拉取速度更快一些:
(当然，在本地搭建git镜像仓库，速度最快)
- git.trystack.cn
```
# http://git.trystack.cn/cgit/openstack/cinder/
GIT_BASE=http://git.trystack.cn
NOVNC_REPO=http://git.trystack.cn/kanaka/noVNC.git
SPICE_REPO=http://git.trystack.cn/git/spice/spice-html5.git
```

- gitclone.com
```
GIT_BASE=https://gitclone.com/github.com
NOVNC_REPO=https://gitclone.com/github.com/kanaka/noVNC.git
SPICE_REPO=https://gitclone.com/github.com/git/spice/spice-html5.git
```

- gitlab.iefcu.cn
```
GIT_BASE=https://gitlab.iefcu.cn
NOVNC_REPO=https://gitlab.iefcu.cn/openstack/noVNC.git
SPICE_REPO=https://gitlab.iefcu.cn/openstack/spice-html5.git
```
  自己搭建的本地私有git镜像仓库(注意必须在组织openstack下)
  FIXME: 怎么快捷的导入所有的git仓库?
  手动导入如下git仓库, 安装一个all-in-one就行
  - cinder.git
  - glance.git
  - horizon.git
  - keystone.git
  - neutron.git
  - nova.git
  - placement.git
  - requirements.git
  - tempest.git
  - **noVNC.git**

#### local.conf配置详解

[Devstack配置文件local.conf参数说明](http://www.chenshake.com/local-conf-devstack-profile-parameter-description/)

先梳理一下自己理解的一些字段
* FIXED_RANGE 内网ip?
  可选的吧，之前没配置也单节点安装成功了
  FIXED_RANGE=10.4.128.0/20
* FLOATING_RANGE 浮动ip范围?
  可选的吧，之前没配置也单节点安装成功了
  FLOATING_RANGE=192.168.42.128/25

=> 以上两个字段没配置会怎么样?

* SERVICE_HOST ?
* ENABLED_SERVICES 计算节点只启用的服务?
  ENABLED_SERVICES=n-cpu,q-agt,c-vol,placement-client

https://gist.github.com/pajayrao/af864f618b0dd78e7244f79009fd7dd7
* ADMIN_PASSWORD -> Admin Password
* DATABASE_PASSWORD -> Database Password
* RABBIT_PASSWORD -> Password for rabbit queue
* SERVICE_PASSWORD -> Password for other services
* HOST_IP -> Controller node IP
* FLAT_INTERFACE -> Interface for bridge
* FIXED_RANGE -> Fixed IP range for assignment
* FIXED_NETWORK_SIZE -> Size of the FIXED IP range
* FLOATING_RANGE -> External IP range for assignment
* MULTI_HOST -> 1 # for multinode

#### 网络配置

配置网络
OpenStack至少需要两个网卡，一个用于连接外部网络，一个用于连接内部网络。

外部网络
公共网络，外部或Internet可以访问的网络。

内部网络
管理网络，用于OpenStack组件以及MySQL DB Server, RabbitMQ messaging server之间的通信。
————————————————
版权声明：本文为CSDN博主「Gane_Cheng」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
原文链接：https://blog.csdn.net/Gane_Cheng/article/details/53538203

```
## Neutron options
Q_USE_SECGROUP=True
FLOATING_RANGE="192.168.0.0/24"
FIXED_RANGE="10.0.0.0/24"
NETWORK_GATEWAY="10.0.0.2"
Q_FLOATING_ALLOCATION_POOL=start=192.168.0.150,end=192.168.0.180
PUBLIC_NETWORK_GATEWAY="192.168.0.1"
Q_L3_ENABLED=True
PUBLIC_INTERFACE=eth0 => ok
Q_USE_PROVIDERNET_FOR_PUBLIC=True
OVS_PHYSICAL_BRIDGE=br-ex
PUBLIC_BRIDGE=br-ex
OVS_BRIDGE_MAPPINGS=public:br-ex

# #VLAN configuration.
Q_PLUGIN=ml2
ENABLE_TENANT_VLANS=True
```

https://www.cnblogs.com/jmilkfan-fanguiju/p/7532338.html
1 单网卡的网络节点配置
在有些开发者实验环境中，主机有且只有一个可用的网卡可用的情况。这种情况下物理网卡加入到Open vSwitch中，然后IP地址配在网桥中。这样这个接口充当着三个角色，为自己网络节点服务传输数据，为OpenStack API传输数据，为管理节点传输数据。
警告：当配置单网卡模式的网络节点时，有可能会出现一个临时故障，有可能你的IP地址从你的机器的物理网卡中移除，然后配置在了OVS网桥上。如果你从其他机器用SSH链接到这台机器，可能有一定的风险导致你的SSH会话session中断（因为的arp缓存失效），这样的话将可能中断stack.sh脚本的运行，使整个部署处于一个未完成的状态。为了解决这种情况可以为stack.sh单独的开一个session这样能让stack.sh脚本继续运行。

#### 查看openstack版本

[查看Openstack版本信息](https://blog.csdn.net/tangyh521/article/details/78862129)

* 1、通过openstack --version命令后会得到一个版本信息。
* 2、访问官网版本发布信息的网址：https://releases.openstack.org/
* 3、找到对应的Team版本信息
* 4、点击相应的连接进入到对应的组件版本信息
    这样就很明确地知道自己安装的版本，我的是属于Pike版本下的3.12.0版本。
* 5、同理，我们还可以查询譬如：
      网站：https://releases.openstack.org/下的neutron
        通过查看到相应的版本为：pike的版本6.5.0
     相应的版本信息查询完成。

#### 列出devstack的所有组件

```bash
ll /etc/systemd/system/ | grep devstack | awk '{print $9}'

devstack@c-api.service
devstack@c-sch.service
devstack@c-vol.service
devstack@dstat.service
devstack@etcd.service
devstack@g-api.service
devstack@keystone.service
devstack@n-api-meta.service
devstack@n-api.service
devstack@n-cond-cell1.service
devstack@n-cpu.service
devstack@n-novnc-cell1.service
devstack@n-sch.service
devstack@n-super-cond.service
devstack@placement-api.service
devstack@q-agt.service
devstack@q-dhcp.service
devstack@q-l3.service
devstack@q-meta.service
devstack@q-svc.service

c-*是cinder，g-*是glance，n-*是nova，o-*是octavia，q-*是neutron

最新版本(估计是yoga?)
devstack@c-api.service
devstack@c-sch.service
devstack@c-vol.service
devstack@dstat.service
devstack@etcd.service
devstack@g-api.service
devstack@keystone.service
devstack@n-api-meta.service
devstack@n-api.service
devstack@n-cond-cell1.service
devstack@n-cpu.service
devstack@n-novnc-cell1.service
devstack@n-sch.service
devstack@n-super-cond.service
devstack@placement-api.service
devstack@q-ovn-metadata-agent.service
devstack@q-svc.service
```

#### 安装途中遇到的坑

收集一点别人遇到的坑

https://www.daimajiaoliu.com/daima/4ed5946659003e8

#### 使用kvm虚拟机安装devstack

准备一个ubuntu cloud镜像: ubuntu-20.04-server-cloudimg-amd64.img (例如release-0506)

配置cloud init配置: ubuntu-devstack.yml
=> 配置了用户; apt mirror; pip mirror;等等
```
#cloud-config
apt:
  primary:
    - arches: [default]
      uri: http://docker.iefcu.cn:5565/repository/ubuntu-cn-proxy
hostname: devstack
timezone: Asia/Shanghai
ssh_pwauth: False

write_files:
  - path: /etc/pip.conf
    permissions: '0755'
    content: |
      [global]
      index-url = http://docker.iefcu.cn:5565/repository/aliyun-pypi/simple
      trusted-host = docker.iefcu.cn

#runcmd:
#  - echo 10.90.3.38 docker.iefcu.cn >> /etc/hosts

users:
  - name: adam
    sudo: ["ALL=(ALL) NOPASSWD:ALL"]
    shell: /bin/bash
    plain_text_passwd: ksvd2020
    lock_passwd: false
  - name: stack
    homedir: /opt/stack
    ssh_authorized_keys:
      - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC5c83qpURHtdTE01HbIstsIQ4LHtVK6NFMVXrEnxcXvYccNaKfhuCU/7gh3f6ZLNd/osOrsL2ab89mzmBidI4KHlpvD+kOWf+VYfw4fhA4kSGb9wKdp0jiFY2MVBq4aWlT5u5pMnWNLQXyqNWmsV02qPrmKelQ5SroMP+OElrURFHzC8Qt2SyxBbMy+T1u5P7SlBzx3riYhHIwPjUZ1qf0YPto8X0yab3bUQmBXocIGetzn+tKe3oO8TRVgt8xoghHmK34j6mPuoUXp162BcCnai71ChXrBThZ/fC+a/JFaNyHXk6Q77JNNi16Fh+AsFg88cOqGAy5OVL7Oa0GTLDLGU697qY96q9W+jsWHMv5uT4a9gRFzHbz5OxFxNaVFe9ShMsDqjendSjL/ACudknQpHEHRseBptzkhbsL+b8vDOJSiHyjzhUrg4FPvU8qBMC1PK6lvbbCdUK1UbWBtSkqIp/a8WvjQF3iZcdwbkD1L12J5m1sq1Aw3/p8K3lrWjU= xiaoyun@KSVDI-VDI-02bm
    sudo: ["ALL=(ALL) NOPASSWD:ALL"]
    shell: /bin/bash
```

本机简单测试:
```
rm -f ubuntu-devstack.iso
cloud-localds ubuntu-devstack.iso ubuntu-devstack.yml
qemu-img create -f qcow2 -b /home/vm-images/ubuntu-20.04-server-cloudimg-amd64.img /home/vm-images/ubuntu.img
virt-install --os-variant ubuntu20.04 \
        --name ubuntu \
        --memory 2048 \
        --vcpus 4 \
        --network bridge=virbr0 \
        --disk ubuntu.img,device=disk,bus=virtio \
        --disk ubuntu-devstack.iso,device=cdrom \
        --graphics none \
        --import
```

#### devstack neutron网络配置

devstack neutron config
[Using DevStack with neutron Networking](https://docs.openstack.org/devstack/latest/guides/neutron.html)

```
## Neutron options
Q_USE_SECGROUP=True
FLOATING_RANGE="172.18.161.0/24"
IPV4_ADDRS_SAFE_TO_USE="10.0.0.0/22"
Q_FLOATING_ALLOCATION_POOL=start=172.18.161.250,end=172.18.161.254
PUBLIC_NETWORK_GATEWAY="172.18.161.1"
PUBLIC_INTERFACE=eth0

# Open vSwitch provider networking configuration
Q_USE_PROVIDERNET_FOR_PUBLIC=True
OVS_PHYSICAL_BRIDGE=br-ex
PUBLIC_BRIDGE=br-ex
OVS_BRIDGE_MAPPINGS=public:br-ex
```

## FAQ

#### (未解决)Unable to create the network. No tenant network is available for allocation

最后想调试neutron程序, 结果重启neutron服务就可以了?
```
sudo systemctl restart devstack@q-svc.service
```

https://docs.openstack.org/neutron/latest/admin/config-network-segment-ranges.html#create-a-tenant-network

发现居然没有netowrk-segment-range插件?
```
$ openstack network segment range list
Network segment ranges list not supported by Network API: No Extension found for network-segment-range
```

应该是这个provider分配不了导致?
```
$ openstack network show net1
+---------------------------+--------------------------------------+
| Field                     | Value                                |
+---------------------------+--------------------------------------+
| provider:network_type     | vxlan                                |
| provider:physical_network | None                                 |
| provider:segmentation_id  | 875                                  |
```

#### Socket /var/run/openvswitch/ovnnb_db.sock not found

肯定是没有清理干净残留数据...

#### ln: failed to create symbolic link '/var/run/ovn/openvswitch': File exists

删除残留数据? rm /var/run/ovn/openvswitch
```
+lib/neutron_plugins/ovn_agent:install_ovn:363  sudo ln -s /var/run/openvswitch /var/run/ovn
ln: failed to create symbolic link '/var/run/ovn/openvswitch': File exists
```

#### Unable to acquire the dpkg frontend lock (/var/lib/dpkg/lock-frontend), is another process using it?

关键字《ubuntu 禁用 apt.systemd.daily install》

修改apt.daily配置文件: /etc/apt/apt.conf.d/20auto-upgrades
```
APT::Periodic::Update-Package-Lists "0";
APT::Periodic::Unattended-Upgrade "0";
```

禁用apt.daily服务
```
sudo systemctl stop apt-daily.service
sudo systemctl disable apt-daily.service
sudo systemctl stop apt-daily-upgrade.service
sudo systemctl disable apt-daily-upgrade.service
```

#### ovs-vsctl: unix:/var/run/openvswitch/db.sock: database connection failed (No such file or directory)

启动这个ovs服务即可? 至少有这个db.sock了!
```
sudo systemctl start openvswitch-switch
```

#### pass_env values cannot contain whitespace

=> tox4的支持性问题， 估计我当时使用pip安装的不是tox4吧
=> 更新tempest源码, 使用最新版本: https://opendev.org/openstack/tempest.git

https://github.com/python/mypy/issues/14522
tox4 does not support pass_env values with whitespace in tox.ini.

https://github.com/napari/cookiecutter-napari-plugin/issues/146
Since tox 4 its no longer accepts two variables in one line. 

https://github.com/python/mypy/pull/14578/files
把变量换行
```
-passenv = PYTEST_XDIST_WORKER_COUNT PROGRAMDATA PROGRAMFILES(X86) PYTEST_ADDOPTS
+passenv =
+    PYTEST_XDIST_WORKER_COUNT
+    PROGRAMDATA
+    PROGRAMFILES(X86)
+    PYTEST_ADDOPTS
```

```
++lib/tempest:configure_tempest:633         tox -revenv-tempest --notest
venv-tempest: remove tox env folder .tox/tempest
venv-tempest: failed with pass_env values cannot contain whitespace, use comma to have multiple values in a single line, invalid values found 'OS_STDOUT_CAPTURE OS_STDERR_CAPTURE OS_TEST_TIMEOUT OS_TEST_LOCK_PATH TEMPEST_CONFIG TEMPEST_CONFIG_DIR http_proxy HTTP_PROXY https_proxy HTTPS_PROXY no_proxy NO_PROXY ZUUL_CACHE_DIR REQUIREMENTS_PIP_LOCATION GENERATE_TEMPEST_PLUGIN_LIST'
  venv-tempest: FAIL code 1 (0.00 seconds)
  evaluation failed :( (0.50 seconds)
```

#### openstack上传大镜像一直卡在已排队问题

关键字《openstack创建镜像 已排队》

https://blog.csdn.net/u014299266/article/details/124193211

需要我们需要去调大image_size_total 这个参数
官方文档: https://docs.openstack.org/glance/latest/admin/quotas.html

然后我是直接去数据库修改配置
tips：数据库密码是安装openstack设置的统一密码
keystone数据库下的registered_limit表
image_size_total

[(好)不要尝试在家里部署 OpenStack](https://juejin.cn/post/7036722660885151751)
修改 /etc/glance/glance-api.conf, 效果立竿见影
```
use_keystone_limits = False
```

#### devstack最新版不支持ubuntu 18.04 server来安装了

提示支持ubuntu focal(20.04)了...

```
+./stack.sh:main:230                       SUPPORTED_DISTROS='focal|f34|opensuse-15.2|opensuse-tumbleweed|rhel8'
+./stack.sh:main:232                       [[ ! bionic =~ focal|f34|opensuse-15.2|opensuse-tumbleweed|rhel8 ]]
+./stack.sh:main:233                       echo 'WARNING: this script has not been tested on bionic'
WARNING: this script has not been tested on bionic
+./stack.sh:main:234                       [[ '' != \y\e\s ]]
+./stack.sh:main:235                       die 235 'If you wish to run this script anyway run with FORCE=yes'
+functions-common:die:198                  local exitcode=0
+functions-common:die:199                  set +o xtrace
[Call Trace]
./stack.sh:235:die
[ERROR] ./stack.sh:235 If you wish to run this script anyway run with FORCE=yes
```

强制安装
```bash
FORCE=yes ./stack.sh
```

#### (未解决)httplib2软件包冲突

暂未解决, 这种类似问题以前遇到挺多, 必须熟悉过程才能解决

```
Installing collected packages: httplib2, cursive, glance
  Attempting uninstall: httplib2
    Found existing installation: httplib2 0.9.2
ERROR: Cannot uninstall 'httplib2'. It is a distutils installed project and thus we cannot accurately determine which files belong to it which would lead to only a partial uninstall.
```

#### (未解决)ovn-central软件包缺失

debian11安装遇到的问题, 包名不一样呢, 看来devstack对debian的适配也不够好!

```
Package ovn-central is not available, but is referred to by another package.
This may mean that the package is missing, has been obsoleted, or
is only available from another source
However the following packages replace it:
  openvswitch-common

Package ovn-controller-vtep is not available, but is referred to by another package.
This may mean that the package is missing, has been obsoleted, or
is only available from another source
However the following packages replace it:
  openvswitch-common

Package ovn-host is not available, but is referred to by another package.
This may mean that the package is missing, has been obsoleted, or
is only available from another source
However the following packages replace it:
  openvswitch-common

E: Package 'ovn-central' has no installation candidate
E: Package 'ovn-controller-vtep' has no installation candidate
E: Package 'ovn-host' has no installation candidate
```
 
#### 网络不通

原因是浮动ip范围占用了128~254的ip地址, 有特殊静态路由, 其他节点机器不能使用这个范围内的ip地址

#### (未解决)web登录提示证书不可用

* 尝试1, 失败, 没找到相关修改的地方, 本来就是正确的keystone配置
Openstack在dashboard界面登录提示无效证书
修改/etc/openstack-dashboard/local_settings内容
OPENSTACK_KEYSTONE_URL = "http://%s:5000/v3" % OPENSTACK_HOST


## 参考资料

* [腾讯云上使用ubuntu18.04系统，用devstack安装openstack（成功,4核8GB）](https://blog.csdn.net/hunjiancuo5340/article/details/85005995)

* [Ubuntu 20使用devstack快速安装openstack最新版](https://blog.51cto.com/u_15103026/2646849)
* https://www.programminghunter.com/article/4154810115/

* [(好,最简单的配置)openstack的DevStack安装](https://xn--helloworld-pf2pka.top/archives/178)
