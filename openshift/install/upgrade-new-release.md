# openshift升级到新版本

关键字
* update
* upgrade

## 制作release新版本

可选, 制作新版本, 参考![](./install-customizing.md) 

#### 制作新的os-content镜像

构建适配kylin coreos的release镜像方法

ostree系统的特殊性，以及openshift的版本升级原理,
需要构建新的os-content镜像，然后修改release镜像

### 构建kylin coreos的os-content镜像

基于已有的os-content镜像，提取内容，然后替换ostree版本目录/srv/repo/

* 1. 提取原始os-content镜像到本地

使用oc命令提取
```
mkdir /tmp/extracted-oscontent
oc image extract --path /:/tmp/extracted-oscontent \
  hub.iefcu.cn/xiaoyun/openshift4-aarch64:4.9.0-rc.6-arm64-machine-os-content
```

使用docker命令提取
```bash
docker create --name tmp hub.iefcu.cn/xiaoyun/openshift4-aarch64:4.9.0-rc.6-arm64-machine-os-content
docker cp tmp:/ ./4.9.0-rc.6-arm64-machine-os-content
```

* 2. 替换镜像的ostree repo目录/srv/repo/
使用kylin coreos的ostree repo压缩包, 例如kylinsec-coreos-34.20220125.dev.1-ostree.aarch64.tar
```bash
rootfs=./4.9.0-rc.6-arm64-machine-os-content
rm -rf ${rootfs}/srv/repo/
mkdir ${rootfs}/srv/repo/
tar -xf kylinsec-coreos-34.20220125.dev.1-ostree.aarch64.tar -C ${rootfs}
tar -czf ./arm-os-content-0125.tgz -C ${rootfs} .
```

* 3. 制作os-content镜像

编写Dockerfile内容如下:
```dockerfile
FROM scratch

ADD ./arm-os-content-0125.tgz /

CMD ["/bin/bash"]
```

构建镜像，并上传镜像
```bash
docker build -t hub.iefcu.cn/xiaoyun/ocp-build:4.9.0-rc.6-arm64-machine-os-content-0125 .
docker push hub.iefcu.cn/xiaoyun/ocp-build:4.9.0-rc.6-arm64-machine-os-content-0125
```

#### 制作新release

基于已有的release制作

修改了几个镜像:
* machine-os-content

**以及将基础镜像的名称由quay.io/openshift-release-dev/ocp-v4.0-art-dev改成了hub.iefcu.cn/xiaoyun/openshift4-aarch64**

```dockerfile
FROM hub.iefcu.cn/xiaoyun/openshift4-aarch64:4.9.0-rc.6-arm64

# replace 4.9.0-rc.6-arm64-machine-os-content  427f68d74f88fa0855ac7398ed61f64b407e8961fe25c31d16286efbabb50adb
# 使用新的kyiln coreos content 0125
RUN sed -i -e "s#quay.io/openshift-release-dev/ocp-v4.0-art-dev@sha256:427f68d74f88fa0855ac7398ed61f64b407e8961fe25c31d16286efbabb50adb#hub.iefcu.cn/xiaoyun/ocp-build@sha256:261b0f94eccd2def621d94431854a36b167b860878da6b06995c11a8aa71d8e5#g" /release-manifests/*

# 使用hub.iefcu.cn
RUN sed -i -e "s#quay.io/openshift-release-dev/ocp-v4.0-art-dev@sha256:#hub.iefcu.cn/xiaoyun/openshift4-aarch64@sha256:#g" /release-manifests/*
```

```bash
docker build -f ./Dockerfile -t hub.iefcu.cn/xiaoyun/ocp-build:4.9.0-rc.6-arm64-0125 .
```

## 升级新的release版本

```
oc adm upgrade --force --to-image hub.iefcu.cn/xiaoyun/kcp-release:0413-console-operator-test --allow-explicit-upgrade
```

oc get clusterversion
查看升级过程
