# 构建kolla容器镜像

## 安装kolla工具

使用pip直接安装
```
apt install -y python3-pip
pip install kolla 
```

首先创建Dockerfile目录, 然后在dockerfile目录手动构建镜像!
```
kolla-build -b ubuntu --template-only --openstack-release xena -t source --work-dir yoga3 --tag yoga3 ^cinder-
```

开始构建相关镜像
=> source需要下载cinder的release包并解压
```
pip3 install  kolla==10.4.0 #  支持ubuntu 18.04构建yoga镜像

docker build -t xxx:yoga3

kolla/ubuntu-binary-cinder-backup      yoga2
kolla/ubuntu-binary-cinder-scheduler   yoga2
kolla/ubuntu-binary-cinder-api         yoga2
kolla/ubuntu-binary-cinder-volume      yoga2
kolla/ubuntu-binary-cinder-base        yoga2
kolla/openstack-base                   yoga2
kolla/ubuntu-binary-openstack-base     yoga2
kolla/base                             yoga2
kolla/ubuntu-binary-base               yoga2
base                                   yoga2
```

## 构建cinder镜像

单独编译cinder-api镜像, 基于ubuntu
```
kolla-build -b ubuntu cinder-api
kolla-build -b ubuntu ^cinder- # 或者编译cinder所有镜像

#kolla-build -b ubuntu --base-tag 18.04 --openstack-release yoga --tag yoga2 ^cinder-
kolla-build -b ubuntu --openstack-release yoga --tag yoga2 ^cinder-
```

只构建cinder-api的相关Dockerfile
```
kolla-build -b ubuntu --template-only --work-dir . cinder-api
=> 然后手动使用docker命令构建镜像
```

配置代理 => 没有作用, 没有用到代理, 官网文档居然有问题!!!
=> 唉，还是用透明代理，或者单边网关透明代理搞吧!
```
kolla-build -b ubuntu --work-dir . \
    --build-args HTTPS_PROXY=http://proxy.iefcu.cn:20172 \
    --build-args  HTTP_PROXY=http://proxy.iefcu.cn:20172 \
    cinder-api
```

### 构建参数解析

构建镜像, 并上传到镜像仓库
```
kolla-build -b ubuntu --registry $REGISTRY --push
```

其他参数, 待尝试
```
--tag yoga
--tarballs-base TARBALLS_BASE
--openstack-release yoga
```

#### 源码构建容器镜像

创建配置文件 kolla-build.conf
```
[horizon]
type = url
location = https://tarballs.openstack.org/horizon/horizon-master.tar.gz

[keystone-base]
type = git
location = https://opendev.org/openstack/keystone
reference = stable/mitaka

[heat-base]
type = local
location = /home/kolla/src/heat

[ironic-base]
type = local
location = /tmp/ironic.tar.gz
enabled = False
```

### 基于ubuntu 18.04基础镜像构建yoga版本镜像

安装指定版本kolla
```
apt install -y python3-pip
pip3 install  kolla==10.4.0 #  支持ubuntu 18.04构建yoga镜像
```

首先创建Dockerfile目录, 然后在dockerfile目录手动构建镜像!
```
kolla-build -b ubuntu --template-only --openstack-release yoga -t source --work-dir yoga --tag yoga ^cinder-
```

开始构建相关镜像
=> source需要下载cinder的release包并解压

大致有如下一些镜像

- kolla/ubuntu-binary-cinder-backup      yoga
- kolla/ubuntu-binary-cinder-scheduler   yoga
- kolla/ubuntu-binary-cinder-api         yoga
- kolla/ubuntu-binary-cinder-volume      yoga
- kolla/ubuntu-binary-cinder-base        yoga
- kolla/ubuntu-binary-openstack-base     yoga
- kolla/openstack-base                   yoga
- kolla/ubuntu-binary-base               yoga
- kolla/base                             yoga

#### 构建base镜像

docker/base

一些apt key的下载有点问题了, 需要处理一下
修改 docker/base/Dockerfile
主要是去除key: A20F259AEB9C94BB
```
          RUN apt-key adv --no-tty --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 391A9AA2147192839E9DB0315EDB1B62EC4926EA
               RUN apt-key adv --no-tty --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 46095ACC8548582C1A2699A9D27D666CD88E42B4
               RUN apt-key adv --no-tty --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 49B07274951063870A8B7EAE7B8AA1A344C05248
               RUN apt-key adv --no-tty --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 58118E89F3A912897C070ADBF76221572C52609D
               RUN apt-key adv --no-tty --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 4D8EB5FDA37AB55F41A135203BF88A0C6A770882
               RUN apt-key adv --no-tty --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 901F9177AB97ACBE
               #RUN apt-key adv --no-tty --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 A20F259AEB9C94BB
               RUN apt-key adv --no-tty --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 F1656F24C74CD1D8
               RUN apt-key adv --no-tty --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 F77F1EDA57EBB1CC
               RUN apt-key adv --no-tty --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 F6609E60DC62814E
```

构建镜像
```
docker build -t kolla/ubuntu-source-base:yoga .
```

#### 构建openstack-base镜像

docker/openstack-base

先准备openstack yoga版本的 requirements
```
openstack-base-archive
```

Dockerfile需要适配一下
```
apt install python3-anyjson
mkdir -p /requirements && ln -s /openstack-base-source/upper-constraints.txt /requirements/
# pip install anyjson # 去除这个anyjson
```

构建镜像
```
docker build -t kolla/ubuntu-source-openstack-base:yoga .
```

#### 构建ubuntu-source-cinder-base镜像

docker/cinder/cinder-base

需要准备cinder包 cinder-base-source

Dockerfile修改
```
RUN mkdir -p /cinder && ln -s /cinder-base-source/* /cinder/ \
```

构建镜像
```
docker build -t kolla/ubuntu-source-cinder-base:yoga .
```

#### 构建cinder-api等镜像

构建镜像
```
docker build -t hub.iefcu.cn/public/ubuntu-source-cinder-scheduler:yoga .
docker build -t hub.iefcu.cn/public/ubuntu-source-cinder-api:yoga .
docker build -t hub.iefcu.cn/xiaoyun/ubuntu-source-cinder-backup:yoga .
docker build -t hub.iefcu.cn/xiaoyun/ubuntu-source-cinder-volume:yoga .
```

保存镜像
```
docker image save \
  hub.iefcu.cn/public/ubuntu-source-cinder-scheduler:yoga \
  hub.iefcu.cn/public/ubuntu-source-cinder-api:yoga \
  hub.iefcu.cn/xiaoyun/ubuntu-source-cinder-backup:yoga \
  hub.iefcu.cn/xiaoyun/ubuntu-source-cinder-volume:yoga \
  > yoga.img
```

#### 定制cinder-api镜像

Dockerfile
```
FROM hub.iefcu.cn/public/ubuntu-source-cinder-api:yoga
ADD ./api.py /var/lib/kolla/venv/lib/python3.6/site-packages/cinder/volume/api.py
```

构建新镜像
```
docker build -t hub.iefcu.cn/public/ubuntu-source-cinder-api:yoga-new .
```

#### 制作额外驱动cinder-volume镜像

准备额外驱动
```
git clone -b python3 http://192.168.120.13/xiaoyun/mmj-cinder.git
```

Dockerfile
```
FROM hub.iefcu.cn/xiaoyun/ubuntu-source-cinder-volume:yoga
ADD ./mmj-cinder/kylinsec /var/lib/kolla/venv/lib/python3.6/site-packages/cinder/volume/drivers/kylinsec
```

构建镜像
```
docker build -t hub.iefcu.cn/xiaoyun/ubuntu-source-cinder-volume:yoga-new .
```

#### 制作rpm包

```
git clone http://192.168.120.13/xiaoyun/mmj-dev.git
cd mmj-dev
bash ./build-cinder-rpm.sh
```

## 旧的资料

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

[kolla-build镜像时，问题汇总](https://www.cnblogs.com/potato-chip/p/10100667.html)

[(好)管理2000+Docker镜像，Kolla是如何做到的](https://blog.51cto.com/u_9443135/3720391)

[OpenStack Kolla源码分析–Ansible ](https://blog.51cto.com/u_15127593/2749775)


## 参考资料

[kolla官方构建方法](https://docs.openstack.org/kolla/latest/admin/image-building.html)
