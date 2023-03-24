# openstack安装部署使用

错误：实例热迁移到主机"AUTO_SCHEDULE"失败 Details
kolla-compute1 is not on shared storage: Shared storage live-migration requires either shared storage or boot-from-volume with no local disks. (HTTP 400) (Request-ID: req-4fbffb74-492e-485d-9f96-7fe93fd7f981) 
=> 原来使用的是本地磁盘...

```
openstack server create \
    --image centos7 \
    --flavor m1.small \
    --key-name mykey \
    --network demo-net \
    demo1
```

查看服务列表
```
openstack service list
+----------------------------------+-------------+----------------+
| ID                               | Name        | Type           |
+----------------------------------+-------------+----------------+
| 06864fe8aae14ca9ad3a021af20b6159 | nova_legacy | compute_legacy |
| 3f3b8fdfc1b04d789cbafc820ba6971d | cinderv3    | volumev3       |
| 5cb91155a74d4fe0bed0081f60376b0f | heat        | orchestration  |
| 789c635f1dc947018aaa962537547985 | glance      | image          |
| abe33e17f53d4656b71251cbf57cf24c | nova        | compute        |
| df623a12fe25412b9bd29483560eb4e5 | neutron     | network        |
| e2318f5d7a424dac9416910e6b1094f6 | placement   | placement      |
| e6c08f0c6a84421e85c8bff4c73a1b83 | heat-cfn    | cloudformation |
| ec383b1d33aa4d64ab55829a44b3c687 | keystone    | identity       |
+----------------------------------+-------------+----------------+
```

思路:
* 1.devstack安装部署

疑问:
* 1.在多节点配置时，一般保留私有地址的前十个, 什么意思?

https://docs.openstack.org/image-guide/obtain-images.html
获取系统云镜像

openstack 配置密码

https://stackoverflow.com/questions/16768272/openstack-change-admin-password-for-the-dashboard
keystone user-password-update --pass <password> <user id>

[openstack设置实例的帐号密码](https://blog.csdn.net/Man_In_The_Night/article/details/111915141)
“项目”–“实例”–“创建实例”–“配置”–“选择文件”
```
#!/bin/bash
#change password
passwd root<<EOF
hao@123
hao@123
EOF
#allow ssh password login and no use dns
sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/g' /etc/ssh/sshd_config
sed -i 's/#PermitRootLogin yes/PermitRootLogin yes/g' /etc/ssh/sshd_config
sed -i 's/#UseDNS yes/UseDNS no/g' /etc/ssh/sshd_config
systemctl restart sshd
```


## devstack安装openstack集群

[openstack的DevStack安装](https://xn--helloworld-pf2pka.top/archives/178)

#### 尝试添加计算节点

## 安装devstack单节点

之前就尝试过, 现在使用ubuntu 20.04安装Yoga版本成功 - 2022-05-11

#### 安装ubuntu 20.04 server版本

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
          addresses: [8.8.8.8, 1.1.1.1]
```

ip修改配置生效
```bash
sudo netplan apply
```

#### 安装准备工作

配置代理, 参考: [代理配置](../tricks/proxy.md)

安装git，升级pip，其他
```bash
# 切到root运行
apt update
apt install -y git
apt install -y python-pip
pip install --upgrade pip
pip install -U os-testr
```

#### devstack安装准备

创建一个用户来运行DevStack, 参考devstack的脚本[create-stack-user.sh](https://github.com/openstack/devstack/blob/master/tools/create-stack-user.sh)
```bash
sudo useradd -s /bin/bash -d /opt/stack -m stack
echo "stack ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/stack
```

切到stack用户, 下载DevStack
```bash
sudo su - stack

git clone https://github.com/openstack-dev/devstack
```

#### 配置local.conf进行安装

编写local.conf配置文件(注意修改ip等信息)
```ini
[[local|localrc]]
# Define images to be automatically downloaded during the DevStack built process.
DOWNLOAD_DEFAULT_IMAGES=False
IMAGE_URLS="http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img"

# use TryStack git mirror
GIT_BASE=http://git.trystack.cn
NOVNC_REPO=http://git.trystack.cn/kanaka/noVNC.git
SPICE_REPO=http://git.trystack.cn/git/spice/sice-html5.git


# Credentials
DATABASE_PASSWORD=admin
ADMIN_PASSWORD=admin
SERVICE_PASSWORD=admin
SERVICE_TOKEN=admin
RABBIT_PASSWORD=admin
#FLAT_INTERFACE=enp0s3

HOST_IP="your vm ip"
```

切换到files目录下，执行如下命令
```bash
cd files/
wget -c https://github.com/coreos/etcd/releases/download/v3.1.10/etcd-v3.1.10-linux-amd64.tar.gz
wget -c https://github.com/coreos/etcd/releases/download/v3.1.7/etcd-v3.1.7-linux-amd64.tar.gz
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

#### xxx

参考[openstack部署方式](https://zhuanlan.zhihu.com/p/44905003)
选用[devstack](https://github.com/openstack/devstack)进行安装

[openstack基础架构以及部署资料 (好)](https://cloud.tencent.com/developer/article/1026128)

[腾讯云上使用ubuntu18.04系统，用devstack安装openstack（成功,4核8GB）](https://blog.csdn.net/hunjiancuo5340/article/details/85005995)

## 多节点集群安装

https://blog.csdn.net/m0_49212388/article/details/107606727
请参考devstack官方文档[《Multi-Node Lab》](https://docs.openstack.org/devstack/latest/guides/multinode-lab.html)

参考[devstack官方文档《Multi-Node Lab》](https://docs.openstack.org/devstack/latest/guides/multinode-lab.html)

#### 集群节点配置准备

* 修改hostname和ip
* 配置ssh互相免密登录
* xxx

注意，首先安装控制节点，再控制节点安装成功后，再安装nova计算节点，计算节点和控制节点之间要通讯正常。

#### 克隆devstack, 准备stack等用户

跟单机环境一样?略
```bash
git clone https://github.com/openstack-dev/devstack -b stable/yoga

devstack/tools/create-stack-user.sh

mv devstack /opt/stack
chown -R stack:stack /opt/stack/devstack
sudo chmod -R 777 /opt/stack
sudo echo "stack ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
```

创建stack用户
```bash
sudo useradd -s /bin/bash -d /opt/stack -m stack
echo "stack ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/stack
```

注入密钥 => 测试ok
```bash
# 手动注入ssh密钥到stack用户?
# sudo su - stack
mkdir ~/.ssh; chmod 700 ~/.ssh
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCaQ9Zpb5/nyiZEw9sR1mqpdpXgRi7WMnSeDyF2R7g7ZH3kUWZhY/Kkf/LoHWeNR82Wb1gq7s5YvEzSAy9R0VnCAGtMZ6nDFR7VgWiqj2q4nexnkrTFSNA6esrAQlpbbtCXLvKSCIUEuZa73naY87H1++DrxA51FqmRlO2ni+qDKlWcl6d/Jr+0Z+JqfWAdKmGmLDtU/L3qol4VIUolMaL1g7I8O07gbQJovXGTVypkoijLdEZ/mYnL6/3ODuPRBQZfw/A7rG39BiBJ3AxU2UYv8Mfh1Cai3CTqyX/k2wxpxDv/bPHH8fj/Qf1Ib7gZmW7KteNpC0pEl4k3r9f7j5xOwkO2D/h1q0/X1w4PdfxdSzIr1SdP1l0bHDcRGUGmrYb2ZDy9M2U14D0JBT9QWWL36CNOKHNYtrE3nu+g7f7nIUHPijc6MkUZ/h1rYsREWdOSwrTSIkmDS2ajH5CLfX+FsXuExiIor1jyhaPzk8r6M2QxgGJwUZxpEdqa5N+Od0wUDRvkjtleElRZE4ssasqTvugfzZnY+gjvyoU7e1VaMUU1WUHjCjSWxOxCUC7Z4G4pHw2u/DReJ4YMq7qsCLenDE3GvcywZXTN3XA0L+69cWFe5eOC7kG5ggAsVOtXyCFk3+DgBA6vmd415RSQeafyfoitHpPpCr3aeYsOlljyDw== root@bastion.openshift4.kylin.com" > ~/.ssh/authorized_keys
```

#### 配置集群local.conf

The cluster controller runs all OpenStack services.

TODO: 使用本地gitlab仓库, 加速代码拉取?

关键就是加了密钥和改动了local.conf吧?
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

## FAQ

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

#### httplib2软件包冲突

暂未解决, 这种类似问题以前遇到挺多, 必须熟悉过程才能解决

```
Installing collected packages: httplib2, cursive, glance
  Attempting uninstall: httplib2
    Found existing installation: httplib2 0.9.2
ERROR: Cannot uninstall 'httplib2'. It is a distutils installed project and thus we cannot accurately determine which files belong to it which would lead to only a partial uninstall.
```

#### ovn-central软件包缺失

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
```

#### 网络不通

原因是浮动ip范围占用了128~254的ip地址, 其他节点机器不能使用这个范围内的ip地址

#### web登录提示证书不可用

* 尝试1, 失败, 没找到相关修改的地方, 本来就是正确的keystone配置
Openstack在dashboard界面登录提示无效证书
修改/etc/openstack-dashboard/local_settings内容
OPENSTACK_KEYSTONE_URL = "http://%s:5000/v3" % OPENSTACK_HOST

#### 安装途中遇到的坑

收集一点别人遇到的坑

https://www.daimajiaoliu.com/daima/4ed5946659003e8

## 参考资料
