# 构建kolla容器镜像

## 安装kolla工具

使用pip直接安装
```
apt install -y python3-pip
pip install kolla 
```

## 构建cinder镜像

单独编译cinder-api镜像, 基于ubuntu
```
kolla-build -b ubuntu cinder-api
kolla-build -b ubuntu ^cinder- # 或者编译cinder所有镜像
```

只构建cinder-api的相关Dockerfile
```
kolla-build -b ubuntu --template-only --work-dir . cinder-api
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
