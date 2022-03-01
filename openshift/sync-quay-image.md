# quay私有镜像仓库镜像同步

首先配置私有镜像仓库，配置内容如下，使用9443端口
![Alt text](./asserts/1646030897658.png)

然后需要把安装kcp所需要的镜像都同步过去，目前使用在线同步。

提前建立组织kcp

TODO: 使用skepoe sync，只同步arm64的镜像？

待同步的镜像列表如下：

openshift原始镜像

hub.iefcu.cn/xiaoyun/openshift4-aarch64

构建kylin coreos 0125的版本镜像

hub.iefcu.cn/xiaoyun/ocp-build:4.9.0-rc.6-arm64-0125

hub.iefcu.cn/xiaoyun/ocp-build@sha256:261b0f94eccd2def621d94431854a36b167b860878da6b06995c11a8aa71d8e5

hub.iefcu.cn/xiaoyun/ocp-build@sha256:3e1f31c63d58d6ddb976ee3769ada8ffaa958a7ef658698596e714c2a3be7dc2

hub.iefcu.cn/xiaoyun/ocp-build@sha256:b545afac322248a902e5b645d7c10c3bc841af1f898209a1c198e3cc34dbe889

heketi + glusterfs存储

hub.iefcu.cn/xiaoyun/gluster-containers:latest

hub.iefcu.cn/xiaoyun/heketi:9


同步镜像脚本如下：

目前我使用[image-syncer](https://github.com/AliyunContainerService/image-syncer)这个工具来同步镜像

```bash
cat > image-sync.json << EOF
{
    "tmp.iefcu.cn": {
        "username": "adam",
        "password": "TODO:passwd"
    }
}
EOF

cat > image-sync-list.json << EOF
{
"hub.iefcu.cn/xiaoyun/openshift4-aarch64": "tmp.iefcu.cn:9443/kcp/openshift4-aarch64"

,"hub.iefcu.cn/xiaoyun/ocp-build:4.9.0-rc.6-arm64-0125": "tmp.iefcu.cn:9443/kcp/ocp-build"
,"hub.iefcu.cn/xiaoyun/ocp-build@sha256:261b0f94eccd2def621d94431854a36b167b860878da6b06995c11a8aa71d8e5": "tmp.iefcu.cn:9443/kcp/ocp-build"
,"hub.iefcu.cn/xiaoyun/ocp-build@sha256:3e1f31c63d58d6ddb976ee3769ada8ffaa958a7ef658698596e714c2a3be7dc2": "tmp.iefcu.cn:9443/kcp/ocp-build"
,"hub.iefcu.cn/xiaoyun/ocp-build@sha256:b545afac322248a902e5b645d7c10c3bc841af1f898209a1c198e3cc34dbe889": "tmp.iefcu.cn:9443/kcp/ocp-build"

,"hub.iefcu.cn/xiaoyun/gluster-containers:latest": "tmp.iefcu.cn:9443/kcp/gluster-containers"
,"hub.iefcu.cn/xiaoyun/heketi:9": "tmp.iefcu.cn:9443/kcp/heketi"

}
EOF

image-syncer --proc=6 --auth=./image-sync.json --images=./image-sync-list.json \
  --namespace=public --registry=hub.iefcu.cn --retries=3
```

遇到一个问题：

同步这个镜像，报错 error: unsupported manifest type: application/vnd.oci.image.manifest.v1+json

hub.iefcu.cn/xiaoyun/ocp-build@sha256:b545afac322248a902e5b645d7c10c3bc841af1f898209a1c198e3cc34dbe889 

![Alt text](./asserts/2022-02-28_16-42.png)

虽然同步了镜像到quay私有镜像仓库中了，但各种安装工具中，以及yaml使用的都是原来的镜像地址，

最后需要配置ImageContentSourcePolicy来使用这个新的私有镜像仓库

修改install-config.yaml.bak

示例如下：

```yaml
imageContentSources:
- mirrors:
  - quay.iefcu.cn:9443/kcp/openshift4-aarch64
  source: quay.io/openshift-release-dev/ocp-release
- mirrors:
  - quay.iefcu.cn:9443/kcp/openshift4-aarch64
  source: quay.io/openshift-release-dev/ocp-v4.0-art-dev
- mirrors:
  - quay.iefcu.cn:9443/kcp
  source: hub.iefcu.cn/xiaoyun
- mirrors:
  - quay.iefcu.cn:9443/kcp
  source: hub.iefcu.cn/kcp
```

## 构建适配kylin coreos的release镜像方法

TODO: 构建os-content镜像


### 基于os-content等镜像构建新的kcp release版本

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
