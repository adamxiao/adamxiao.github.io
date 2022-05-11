# openstack安装部署使用

思路:
* 1.devstack安装部署

## devstack安装openstack集群

[openstack的DevStack安装](https://xn--helloworld-pf2pka.top/archives/178)

#### 安装ubuntu 18.04

[配置静态ip地址](https://www.myfreax.com/how-to-configure-static-ip-address-on-ubuntu-18-04/)

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

配置生效
```bash
sudo netplan apply
```

#### 安装准备工作

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

创建一个用户来运行DevStack
```bash
sudo useradd -s /bin/bash -d /opt/stack -m stack
```

配置用户sudo权限
```bash
echo "stack ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/stack
sudo su - stack
```

下载DevStack
```bash
# 这个下载失败
git clone https://opendev.org/openstack/devstack

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

#### xxx

参考[openstack部署方式](https://zhuanlan.zhihu.com/p/44905003)
选用[devstack](https://github.com/openstack/devstack)进行安装

[openstack基础架构以及部署资料 (好)](https://cloud.tencent.com/developer/article/1026128)

[腾讯云上使用ubuntu18.04系统，用devstack安装openstack（成功,4核8GB）](https://blog.csdn.net/hunjiancuo5340/article/details/85005995)

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

## 参考资料
