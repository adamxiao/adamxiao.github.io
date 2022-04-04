# 安装

todo

### 同步release相关镜像

#### 方法一. 实时从远程镜像仓库同步到私有镜像仓库

这里需要一个跳板机，可以同时访问远程镜像仓库，和私有镜像仓库

```bash
# 需要配置pull-secret内容: 192.168.120.44:80
oc adm -a ./pull-secret.json release mirror \
  --from=quay.io/openshift-release-dev/ocp-release:4.9.25-aarch64 \
  --to=192.168.120.44/xiaoyun/openshift4-arm-4.9.25 \
  --to-release-image=192.168.120.44/xiaoyun/openshift4-arm-4.9.25:4.9.25-arm64 \
  --insecure # http镜像仓库, 需要加insecure参数
```

#### 方法二. 先同步release相关镜像到本地目录

```bash
# 创建目录
mkdir mirror
oc adm -a ${LOCAL_SECRET_JSON} release mirror \
  --from=quay.io/${PRODUCT_REPO}/${RELEASE_NAME}:${OCP_RELEASE} \
  --to-dir=mirror/
```

示例用法
```
# 创建目录
mkdir mirror
oc adm -a ./pull-secret.json release mirror \
  --from=quay.io/openshift-release-dev/ocp-release:4.9.15-aarch64 \
  --to-dir=mirror/
```

info: Mirroring completed in 22m0.96s (5.652MB/s)
Success
Update image:  openshift/release:4.9.15-arm64
To upload local images to a registry, run:
    oc image mirror --from-dir=mirror/ 'file://openshift/release:4.9.15-arm64*' REGISTRY/REPOSITORY
Configmap signature file mirror/config/signature-sha256-8fc1ec15b45fb51f.yaml created

#### 同步release镜像到目的镜像仓库

* 因为证书是非权威机构 ca 签署的，所以加--insecure
* 因为私有镜像仓库是http接口，所以加--insecure (好像还要使用podman配置insecure镜像仓库？)

```bash
# 不行，会报错, unauthorized to access repository
# 因为私有镜像仓库的认证机制有问题，加不加insecure都不行!
oc image mirror -a pull-secret.json \
  --from-dir=mirror/ 'file://openshift/release:4.9.15*' \
  hub.iefcu.cn/xiaoyun/openshift4-arm-4.9.15 \
  --insecure

# 需要配置pull-secret内容: 192.168.120.44:80
oc image mirror -a pull-secret.json \
  --from-dir=mirror/ 'file://openshift/release:4.9.15*' \
  192.168.120.44/xiaoyun/openshift4-arm-4.9.15 \
  --insecure
```

#### 简单定制一个新版本

构建Dockerfile内容如下
```dockerfile
FROM hub.iefcu.cn/xiaoyun/openshift4-arm-4.9.15:4.9.15-arm64

# 使用hub.iefcu.cn
RUN sed -i -e "s#quay.io/openshift-release-dev/ocp-v4.0-art-dev@sha256:#hub.iefcu.cn/xiaoyun/openshift4-arm-4.9.15@sha256:#g" /release-manifests/*
```

构建镜像并上传
```bash
docker build -t hub.iefcu.cn/xiaoyun/openshift4-arm-4.9.15:4.9.15-arm64-hub.iefcu.cn .
docker push hub.iefcu.cn/xiaoyun/openshift4-arm-4.9.15:4.9.15-arm64-hub.iefcu.cn
```

#### 最后可以提取openshift-install

```bash
GODEBUG=x509ignoreCN=0 oc adm release extract \
  --command=openshift-install \
  hub.iefcu.cn/xiaoyun/openshift4-arm-4.9.15:4.9.15-arm64-hub.iefcu.cn
```
