# cluster logging 日志安装使用

## 依赖

elasticsearch operator (可选)

如果使用外置elasticsearch集群，就不需要安装elasticsearch operator

## operator相关镜像

#### 从bundle镜像中提取出所有的依赖镜像

解压bundle镜像，从manifest目录的yaml文件中提取
或者get packagemanifest获取到!

registry.redhat.io/openshift-logging/cluster-logging-operator-bundle@sha256:9d529610a9ac915cf234bfd0e8c851e6e17be17ed605f6296dc947e592bef3f5
=> hub.iefcu.cn/kcp/logging-operator-index-openshift-logging-cluster-logging-operator-bundle@sha256:9d529610a9ac915cf234bfd0e8c851e6e17be17ed605f6296dc947e592bef3f5
   (通过oc adm catalog mirror同步下来)


## 源码构建镜像

#### 1. cluster-logging-operator

原始信息:
* registry.redhat.io/openshift-logging/cluster-logging-rhel8-operator@sha256:4355370442a1e722ec3fd7679b362d5f04f32016029ea2d243142a0e6ee551e0
  原始bundle镜像
* hub.iefcu.cn/kcp/logging-operator-index-openshift-logging-cluster-logging-rhel8-operator@sha256:4355370442a1e722ec3fd7679b362d5f04f32016029ea2d243142a0e6ee551e0
  mirror镜像
* https://github.com/openshift/cluster-logging-operator/commit/d0a34e663eda323f5c40c959c5cf733b4a315a77
  源码

简单修改一下构建镜像即可

修改Dockerfile
```diff
diff --git a/Dockerfile b/Dockerfile
index 4b0adb19..29a724cc 100644
--- a/Dockerfile
+++ b/Dockerfile
@@ -1,6 +1,7 @@
 ### This is a generated file from Dockerfile.in ###
 #@follow_tag(registry-proxy.engineering.redhat.com/rh-osbs/openshift-golang-builder:rhel_8_golang_1.16)
-FROM registry.ci.openshift.org/ocp/builder:rhel-8-golang-1.16-openshift-4.8 AS builder
+#FROM registry.ci.openshift.org/ocp/builder:rhel-8-golang-1.16-openshift-4.8 AS builder
+FROM hub.iefcu.cn/public/golang:1.16 AS builder
 
 ENV BUILD_VERSION=${CI_CONTAINER_VERSION}
 ENV OS_GIT_MAJOR=${CI_X_VERSION}
@@ -32,10 +33,13 @@ RUN make build
 
 
 #@follow_tag(registry-proxy.engineering.redhat.com/rh-osbs/openshift-ose-cli:v4.8)
-FROM registry.ci.openshift.org/ocp/4.8:cli AS origincli
+#FROM registry.ci.openshift.org/ocp/4.8:cli AS origincli
+# TODO: cli arm46, no x86_64
+FROM hub.iefcu.cn/xiaoyun/openshift4-arm-4.9.15:4.9.15-arm64-cli AS origincli
 
 #@follow_tag(registry.redhat.io/ubi8:latest)
-FROM registry.ci.openshift.org/ocp/4.8:base
+#FROM registry.ci.openshift.org/ocp/4.8:base
+FROM hub.iefcu.cn/library/centos:7
 RUN INSTALL_PKGS=" \
       openssl \
       rsync \
```

使用adam.sh编译构建
```bash
# TODO: 自动化集成编译，参数生成
CI_CONTAINER_VERSION=v5.3.4
CI_X_VERSION=
CI_Y_VERSION=
CI_Z_VERSION=
CI_CLUSTER_LOGGING_OPERATOR_UPSTREAM_COMMIT=d0a34e66
CI_CLUSTER_LOGGING_OPERATOR_UPSTREAM_URL=https://github.com/openshift/cluster-logging-operator
REMOTE_SOURCE=.

docker buildx build \
    -f Dockerfile \
    --build-arg http_proxy=http://proxy.iefcu.cn:20172 --build-arg https_proxy=http://proxy.iefcu.cn:20172 \
    --build-arg no_proxy=yumrepo.unikylin.com.cn,192.0.0.0/8 \
    --build-arg CI_CONTAINER_VERSION=${CI_CONTAINER_VERSION} \
    --build-arg CI_X_VERSION=${CI_X_VERSION} \
    --build-arg CI_Y_VERSION=${CI_Y_VERSION} \
    --build-arg CI_Z_VERSION=${CI_Z_VERSION} \
    --build-arg CI_ELASTICSEARCH_OPERATOR_UPSTREAM_COMMIT=${CI_ELASTICSEARCH_OPERATOR_UPSTREAM_COMMIT} \
    --build-arg CI_ELASTICSEARCH_OPERATOR_UPSTREAM_URL=${CI_ELASTICSEARCH_OPERATOR_UPSTREAM_URL} \
    --build-arg REMOTE_SOURCE=${REMOTE_SOURCE} \
    --platform=linux/arm64 \
    -t hub.iefcu.cn/kcp/cluster-logging-operator:20220406 . --push
    #-t hub.iefcu.cn/kcp/cluster-logging-operator:${CI_CONTAINER_VERSION} . --push
```

构建成功:
hub.iefcu.cn/kcp/cluster-logging-operator:20220406@sha256:c1de8a1f03f0cfd27f4562175463b4cae386303cedee9dba62b755390c89544e

#### 2. fluentd-rhel8

原始信息:
* registry.redhat.io/openshift-logging/fluentd-rhel8@sha256:b53454bc4057141e6aa3f9908bf5937fb0bcc9bde535a45bf041ab31a37f6224
  原始bundle镜像
* hub.iefcu.cn/kcp/logging-operator-index-openshift-logging-fluentd-rhel8@sha256:b53454bc4057141e6aa3f9908bf5937fb0bcc9bde535a45bf041ab31a37f6224
  mirror镜像
* https://github.com/openshift/origin-aggregated-logging/commit/c5c0a97ffe8d3db56fa5b2fdf8dfc93dde35000d
  源码

这个最好在arm64下编译，x86下使用buildx编译很慢
后来发现有jemalloc问题，还是在coreos下面使用podman编译构建镜像!

先同步ubi8 ruby25的镜像, registry.redhat.io/ubi8/ruby-25:latest

然后修改Dockerfile
```diff
diff --git a/fluentd/Dockerfile b/fluentd/Dockerfile
index 5eb49c3..46cac33 100644
--- a/fluentd/Dockerfile
+++ b/fluentd/Dockerfile
@@ -1,7 +1,8 @@
 ### This is a generated file from Dockerfile.in ###
 
 #@follow_tag(registry.redhat.io/ubi8/ruby-25:latest)
-FROM registry.ci.openshift.org/ocp/builder:ubi8.ruby.25
+#FROM registry.ci.openshift.org/ocp/builder:ubi8.ruby.25
+FROM hub.iefcu.cn/public/ubi8-ruby25
 ENV BUILD_VERSION=1.7.4
 ENV SOURCE_GIT_COMMIT=${CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_COMMIT:-}
 ENV SOURCE_GIT_URL=${CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_URL:-}
```

最后编写脚本adam.sh编译(注意是在fluentd目录下)
```bash
# TODO: 自动化集成编译，参数生成
CI_CONTAINER_VERSION=v5.3.4
CI_X_VERSION=
CI_Y_VERSION=
CI_Z_VERSION=
CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_COMMIT=c5c0a97ff
CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_URL=https://github.com/openshift/origin-aggregated-logging
REMOTE_SOURCE=.
upstream_code=.

docker build \
    -f ./Dockerfile \
    --build-arg http_proxy=http://proxy.iefcu.cn:20172 \
    --build-arg https_proxy=http://proxy.iefcu.cn:20172 \
    --build-arg no_proxy=yumrepo.unikylin.com.cn,192.0.0.0/8 \
    --build-arg CI_CONTAINER_VERSION=${CI_CONTAINER_VERSION} \
    --build-arg CI_X_VERSION=${CI_X_VERSION} \
    --build-arg CI_Y_VERSION=${CI_Y_VERSION} \
    --build-arg CI_Z_VERSION=${CI_Z_VERSION} \
    --build-arg CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_COMMIT=${CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_COMMIT} \
    --build-arg CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_URL=${CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_URL} \
    --build-arg REMOTE_SOURCE=${REMOTE_SOURCE} \
    --build-arg upstream_code=${upstream_code} \
    -t hub.iefcu.cn/kcp/fluentd-rhel8:20220407 .
```

构建成功:
hub.iefcu.cn/kcp/fluentd-rhel8:20220407@sha256:db98b97ee0da6bba31db3bf8e5c44c05bad27fdfe666047dc9555cf51b57ae22

#### 3. log-file-metric-exporter-rhel8

原始信息:
* registry.redhat.io/openshift-logging/log-file-metric-exporter-rhel8@sha256:14110c2e89e0f2069e2b41700dec288bff9ae125781c85eef85a9dc7acf69dac
  原始bundle镜像
* hub.iefcu.cn/kcp/logging-operator-index-openshift-logging-log-file-metric-exporter-rhel8@sha256:14110c2e89e0f2069e2b41700dec288bff9ae125781c85eef85a9dc7acf69dac
  mirror镜像
* https://github.com/viaq/log-file-metric-exporter/commit/9aee61c79069827a3d40aea59c9e49716fa20b97
  源码

简单修改一下构建镜像即可

修改Dockerfile, TODO: 自动生成Dockerfile构建
```diff
diff --git a/Dockerfile b/Dockerfile
index a926d19..407c57e 100644
--- a/Dockerfile
+++ b/Dockerfile
@@ -1,6 +1,7 @@
 ### This is a generated file from Dockerfile.in ###
 #@follow_tag(registry-proxy.engineering.redhat.com/rh-osbs/openshift-golang-builder:rhel_8_golang_1.15)
-FROM registry.ci.openshift.org/ocp/builder:rhel-8-golang-1.15-openshift-4.7 AS builder
+#FROM registry.ci.openshift.org/ocp/builder:rhel-8-golang-1.15-openshift-4.7 AS builder
+FROM hub.iefcu.cn/public/golang:1.16 AS builder
 
 ENV BUILD_VERSION=1.0.0
 ENV OS_GIT_MAJOR=1
@@ -17,7 +18,8 @@ COPY ${REMOTE_SOURCE} .
 RUN make build
 
 #@follow_tag(registry.redhat.io/ubi8:latest)
-FROM registry.ci.openshift.org/ocp/4.7:base
+#FROM registry.ci.openshift.org/ocp/4.7:base
+FROM hub.iefcu.cn/library/centos:7
 COPY --from=builder /go/src/github.com/log-file-metric-exporter/bin/log-file-metric-exporter  /usr/local/bin/.
 COPY --from=builder /go/src/github.com/log-file-metric-exporter/hack/log-file-metric-exporter.sh  /usr/local/bin/.
```

最后编写脚本adam.sh编译构建镜像
```bash
# TODO: 自动化集成编译，参数生成
CI_LOG_FILE_METRIC_EXPORTER_UPSTREAM_COMMIT=9aee61c
CI_LOG_FILE_METRIC_EXPORTER_UPSTREAM_URL=https://github.com/viaq/log-file-metric-exporter
REMOTE_SOURCE=.

docker buildx build \
    -f Dockerfile \
    --build-arg http_proxy=http://proxy.iefcu.cn:20172 \
    --build-arg https_proxy=http://proxy.iefcu.cn:20172 \
    --build-arg no_proxy=yumrepo.unikylin.com.cn,192.0.0.0/8 \
    --build-arg CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_COMMIT=${CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_COMMIT} \
    --build-arg CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_URL=${CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_URL} \
    --build-arg REMOTE_SOURCE=${REMOTE_SOURCE} \
    --platform=linux/arm64 \
    -t hub.iefcu.cn/kcp/log-file-metric-exporter:20220407 . --push
    #-t hub.iefcu.cn/kcp/cluster-logging-operator:${CI_CONTAINER_VERSION} . --push
```

构建成功:
hub.iefcu.cn/kcp/log-file-metric-exporter:20220407@sha256:808cced797392bc7c4f36124f1dddad19cd46f26e9bd77d79400b18b7ac0f2ba

## 制作新的operator镜像

#### 修改bundle镜像

TODO: 直接自己构建bundle镜像

registry.redhat.io/openshift-logging/cluster-logging-operator-bundle@sha256:9d529610a9ac915cf234bfd0e8c851e6e17be17ed605f6296dc947e592bef3f5
=> hub.iefcu.cn/kcp/logging-operator-index-openshift-logging-cluster-logging-operator-bundle@sha256:9d529610a9ac915cf234bfd0e8c851e6e17be17ed605f6296dc947e592bef3f5
   (通过oc adm catalog mirror同步下来)

基于旧bundle镜像, 构建新的bundle镜像
```bash
podman create --name logging-bundle hub.iefcu.cn/kcp/logging-operator-index-openshift-logging-cluster-logging-operator-bundle@sha256:9d529610a9ac915cf234bfd0e8c851e6e17be17ed605f6296dc947e592bef3f5 bash
podman cp logging-bundle:/ ~/tmp/logging-bundle-rootfs

# 修改logging-bundle-rootfs里面的manifest目录的文件，修改镜像
# TODO: 获取sha256值? docker pull最后就会输出镜像的sha256值, 有没有更好的方法？(podman pull 不会输出sha256)
# hub.iefcu.cn/kcp/cluster-logging-operator:20220406@sha256:c1de8a1f03f0cfd27f4562175463b4cae386303cedee9dba62b755390c89544e
```

基于bundle镜像里面的Dockerfile构建新的bundle镜像（bundle镜像就是一些manifest文件等）

#### 制作catalog镜像

注意: 这里没有arm64合适的基础镜像，就指定了原来的operator作为基础镜像(x86下也可以做arm64的镜像，因为不设计架构程序运行)
```bash
opm index add \
    --bundles hub.iefcu.cn/kcp/logging-operator-bundle:20220406 \
    --tag hub.iefcu.cn/kcp/logging-operator-operatorhub:20220224 \
    --binary-image hub.iefcu.cn/public/redhat-operator-index:v4.9@sha256:fd45ebb5619656628b84266793ddf24ef6a393cd3a85bc1b5315d5500c0bf067
    #--binary-image hub.iefcu.cn/public/redhat-operator-index:v4.9
```

#### 基于catalog镜像创建

```bash
cat << EOF | oc apply -f -
apiVersion: operators.coreos.com/v1alpha1
kind: CatalogSource
metadata:
  name: cluster-logging
  namespace: openshift-marketplace
spec:
  displayName: cluster-logging
  image: 'hub.iefcu.cn/kcp/logging-operator-operatorhub:20220224'
  publisher: cluster-logging
  sourceType: grpc
EOF
```

## web控制台安装cluster logging operator

arm64下安装，有问题：

Danger alert:存在 Operator 冲突
在所选命名空间中安装此 Operator 可能会导致与提供这些下 API 的另一个 Operator 冲突：

    ClusterLogForwarder (logging.openshift.io/v1)
    ClusterLogging (logging.openshift.io/v1)

=> 可能是有一个残留的cluster logging subscription导致的!
=> 清理掉残留的订阅，确实可以安装成功了!

## cli命令安装cluster logging operator

通过CLI命令安装了logging operator，在页面居然没有显示出来，难道要刷新，要等一段时间?
通过web控制台安装了，在页面上居然也没有显示出来？？？
=> 原来是这个operator是安装到指定namespaces的，其他namespaces自然看不到!

#### 1.创建namespaces

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: openshift-logging
  annotations:
    openshift.io/node-selector: ""
  labels:
    openshift.io/cluster-logging: "true"
    openshift.io/cluster-monitoring: "true"
```

#### 2.创建operator group

```yaml
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: cluster-logging
  namespace: openshift-logging 
spec:
  targetNamespaces:
  - openshift-logging
```

#### 3.订阅安装operator

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: cluster-logging
  namespace: openshift-logging
  #labels:
  #  operators.coreos.com/cluster-logging.openshift-logging: ""
spec:
  channel: "stable" 
  installPlanApproval: "Automatic"
  source: cluster-logging
  sourceNamespace: openshift-marketplace
  name: cluster-logging
```

## FAQ

#### 1. collector日志收集pod CrashLoopBackOff

```bash
[core@master1 ~]$ oc -n openshift-logging logs collector-9hrqz collector
Setting each total_size_limit for 3 buffers to 10710049382 bytes
Setting queued_chunks_limit_size for each buffer to 1276
Setting chunk_limit_size for each buffer to 8388608
<jemalloc>: Unsupported system page size
...
<jemalloc>: Unsupported system page size
[FATAL] failed to allocate memory
```

应该是跟之前redis的jemalloc问题是一样的，需要重新编译这个镜像 => 果然可以
