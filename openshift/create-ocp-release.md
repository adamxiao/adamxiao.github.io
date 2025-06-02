# 制作新的openshift release版本

关键字
* 基于kylin coreos制作release版本
* 修改release基础镜像地址

openshift安装部署所需要的所有基础镜像，都记录在一个叫release的镜像中,
例如，openshift原始镜像是:
* quay.io/openshift-release-dev/ocp-release:4.9.0-rc.6-arm64
* quay.io/openshift-release-dev/ocp-v4.0-art-dev

## 当前最新ocp版本记录

0304 修改说明:
* 基于kylin coreos 0125
* 替换0304 zhouming console镜像
* 全部镜像基础域名为hub.iefcu.cn
* release镜像版本 hub.iefcu.cn/xiaoyun/openshift4-aarch64@sha256:3668ad5942cb4bfdeea526571b267a570ae1a1201843c68c364958ab2ec4af75

```bash
docker build -f ./Dockerfile -t hub.iefcu.cn/xiaoyun/openshift4-aarch64:4.9.0-rc.6-arm64-0304-zhouming-console .
```

```dockerfile
FROM hub.iefcu.cn/xiaoyun/openshift4-aarch64:4.9.0-rc.6-arm64

# replace 4.9.0-rc.6-arm64-machine-os-content  427f68d74f88fa0855ac7398ed61f64b407e8961fe25c31d16286efbabb50adb
# 使用新的kyiln coreos content 0125
RUN sed -i -e "s#quay.io/openshift-release-dev/ocp-v4.0-art-dev@sha256:427f68d74f88fa0855ac7398ed61f64b407e8961fe25c31d16286efbabb50adb#hub.iefcu.cn/xiaoyun/openshift4-aarch64@sha256:261b0f94eccd2def621d94431854a36b167b860878da6b06995c11a8aa71d8e5#g" /release-manifests/*

# 替换原有镜像 4.9.0-rc.6-arm64-console  000b6a5917376b934aa623e585b943c47a5db32e7ceb6613e0d02de7aa003305
# 使用新的镜像 zhouming-console-20220304 19e748566d666b786b919714ec66f4b16fc1d6d1c37d0a11a4aebb6e2c2f9b23
RUN sed -i -e "s#quay.io/openshift-release-dev/ocp-v4.0-art-dev@sha256:000b6a5917376b934aa623e585b943c47a5db32e7ceb6613e0d02de7aa003305#hub.iefcu.cn/xiaoyun/openshift4-aarch64@sha256:19e748566d666b786b919714ec66f4b16fc1d6d1c37d0a11a4aebb6e2c2f9b23#g" /release-manifests/*

# 使用hub.iefcu.cn
RUN sed -i -e "s#quay.io/openshift-release-dev/ocp-v4.0-art-dev@sha256:#hub.iefcu.cn/xiaoyun/openshift4-aarch64@sha256:#g" /release-manifests/*
```

## 构建适配kylin coreos的release镜像方法

ostree系统的特殊性，以及openshift的版本升级原理,
需要构建新的os-content镜像，然后修改release镜像

os-content镜像的sha256，可以从release镜像的如下文件中找到 ./release-manifests/image-references
```
"name": "machine-os-content",
"name": "hub.iefcu.cn/xiaoyun/openshift4-x86-4.9.25@sha256:21ddd91ee17d368ba82e43b5910bce30e7def147f184948982e79976f79f4a73"
```

### 构建kylin coreos的os-content镜像

基于已有的os-content镜像，提取内容，然后替换ostree版本目录/srv/repo/

* 1. 提取原始os-content镜像到本地

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


### 基于os-content等镜像构建新的kcp release版本

修改了几个镜像:
* machine-os-content
* cluster-network-operator
* machine-config-operator

**以及将基础镜像的名称由quay.io/openshift-release-dev/ocp-v4.0-art-dev改成了hub.iefcu.cn/xiaoyun/openshift4-aarch64**

```dockerfile
FROM hub.iefcu.cn/xiaoyun/openshift4-aarch64:4.9.0-rc.6-arm64

# replace 4.9.0-rc.6-arm64-machine-os-content  427f68d74f88fa0855ac7398ed61f64b407e8961fe25c31d16286efbabb50adb
# 使用新的kyiln coreos content 0125
RUN sed -i -e "s#quay.io/openshift-release-dev/ocp-v4.0-art-dev@sha256:427f68d74f88fa0855ac7398ed61f64b407e8961fe25c31d16286efbabb50adb#hub.iefcu.cn/xiaoyun/ocp-build@sha256:261b0f94eccd2def621d94431854a36b167b860878da6b06995c11a8aa71d8e5#g" /release-manifests/*

# replace 4.9.0-rc.6-arm64-cluster-network-operator f26acbe535dbd4261ed152bfeb66e4a0cac122caa6860f6a31e7a6774d61e8e5
# 修正network-operator关于os-release的判断
RUN sed -i -e "s#quay.io/openshift-release-dev/ocp-v4.0-art-dev@sha256:f26acbe535dbd4261ed152bfeb66e4a0cac122caa6860f6a31e7a6774d61e8e5#hub.iefcu.cn/xiaoyun/ocp-build@sha256:3e1f31c63d58d6ddb976ee3769ada8ffaa958a7ef658698596e714c2a3be7dc2#g" /release-manifests/*

# replace 4.9.0-rc.6-arm64-machine-config-operator c22ff95d895155ed0e66d703409e6e803dac516b60cec03f819b02f8f99c8c22
# 修正machine-config关于os-release的判断
RUN sed -i -e "s#quay.io/openshift-release-dev/ocp-v4.0-art-dev@sha256:c22ff95d895155ed0e66d703409e6e803dac516b60cec03f819b02f8f99c8c22#hub.iefcu.cn/xiaoyun/ocp-build@sha256:b545afac322248a902e5b645d7c10c3bc841af1f898209a1c198e3cc34dbe889#g" /release-manifests/*

# 使用hub.iefcu.cn
RUN sed -i -e "s#quay.io/openshift-release-dev/ocp-v4.0-art-dev@sha256:#hub.iefcu.cn/xiaoyun/openshift4-aarch64@sha256:#g" /release-manifests/*
```

```bash
docker build -f ./Dockerfile -t hub.iefcu.cn/xiaoyun/ocp-build:4.9.0-rc.6-arm64-0125 .
```

### 提取出新的openshift-install工具使用

使用这个新的openshift-install工具，就会用到自己构建的kcp相关镜像了

```bash
GODEBUG=x509ignoreCN=0 oc adm release extract \
  --command=openshift-install \
  hub.iefcu.cn/xiaoyun/ocp-build:4.9.0-rc.6-arm64-0125
```

此时最新的openshift就会使用镜像 hub.iefcu.cn/xiaoyun/ocp-build:4.9.0-rc.6-arm64-0125
以及release镜像中指定的所有基础镜像 hub.iefcu.cn/xiaoyun/openshift4-aarch64
