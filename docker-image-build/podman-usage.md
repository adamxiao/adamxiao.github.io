# podman入门

https://docs.qq.com/doc/DZmRid1Jsdk9MeXFB

## 概述

底层都是使用runc容器运行时(貌似cri-o不一样)

podman的镜像存储,跟docker不一样的,但是crictl images看到的是一样的

## 安装

[Podman Installation Instructions](https://podman.io/getting-started/installation)

centos安装podman
```
yum install -y podman
```

ubuntu 20.04安装podman(高级版本ubuntu 安装podman更简单)
```bash
. /etc/os-release
echo "deb https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/testing/xUbuntu_${VERSION_ID}/ /" | sudo tee /etc/apt/sources.list.d/devel:kubic:libcontainers:testing.list
curl -L "https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/testing/xUbuntu_${VERSION_ID}/Release.key" | sudo apt-key add -
sudo apt-get update -qq
sudo apt-get -qq -y install podman
```

## 镜像存储配置

podman拉取镜像,配置registry.mirror
可以配置全局配置文件,也可以配置个人配置文件
```
# /etc/containers/registries.conf
[[registry]]
location = "quay.io/openshift-release-dev/ocp-release"
insecure = false
mirror-by-digest-only = true

[[registry.mirror]]
location = "registry.openshift4.iefcu.cn/ocp4/openshift4"
insecure = false


[[registry]]
location = "quay.io/openshift-release-dev/ocp-v4.0-art-dev"
insecure = false
mirror-by-digest-only = true

[[registry.mirror]]
location = "registry.openshift4.iefcu.cn/ocp4/openshift4"
insecure = false


[[registry]]
location = "registry.redhat.io/redhat/community-operator-index"
insecure = false
#mirror-by-digest-only = true

[[registry.mirror]]
location = "registry.openshift4.iefcu.cn/redhat/community-operator-index"
insecure = false
```
