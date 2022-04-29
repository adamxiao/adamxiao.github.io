# elasticsearch 安装使用

openshift 自带elasticsearch operator安装
由于不支持arm64,但是有源码，可以自己编译构建arm64版本安装

## 源码编译镜像

使用catalog镜像:
* hub.iefcu.cn/kcp/logging-operator-index:v4.9
这个是在x86下裁剪cluster-logging, elasticsearch的镜像(基于hub.iefcu.cnpublic/redhat-operator-index:v4.9)

#### 获取bundle镜像

从catalog镜像中获取
TODO: 有什么更好的方法去获取？

* 1.首先禁用默认的CatalogSource
* 2.然后安装自己的CatalogSource
```yaml
cat << EOF | oc apply -f -
apiVersion: operators.coreos.com/v1alpha1
kind: CatalogSource
metadata:
  name: tmp
  namespace: openshift-marketplace
spec:
  displayName: tmp
  #image: 'hub.iefcu.cn/public/redhat-operator-index:v4.9'
  image: 'hub.iefcu.cn/kcp/logging-operator-index:v4.9'
  publisher: tmp
  sourceType: grpc
EOF
```
* 3.查询bundle镜像
这个命令其实就能获取到bundle镜像里的所有依赖镜像了!
```bash
oc get packagemanifest elasticsearch-operator -o yaml
```

#### 从bundle镜像中提取出所有的依赖镜像

解压bundle镜像，从manifest目录的yaml文件中提取

* registry.redhat.io/openshift-logging/elasticsearch-rhel8-operator@sha256:973b388253d566cb7fa9c8893ae92e781b5ba5dbebea0fcbd5f4d8cdb4e1f90a
* registry.redhat.io/openshift-logging/elasticsearch-proxy-rhel8@sha256:e2bb46b85e0b99cf44220b8908f11cf7946f27ca3873f1c19b6e5ac676aa0607
* registry.redhat.io/openshift4/ose-oauth-proxy@sha256:9fff99a506db94ba61b08a8ae0ac5a049dff4f8b4453e96319115de293595dcf
* registry.redhat.io/openshift-logging/elasticsearch6-rhel8@sha256:5faaf1cde7f7dcc9ed47ce84faf7942ae7c6a24b965ed3bf47be036c4e7596e7
* registry.redhat.io/openshift-logging/kibana6-rhel8@sha256:02fc87a37bbea4156ac6fbd772ed8ab9b703508601f1122f3e3a635343a5cf58
* registry.redhat.io/openshift4/ose-kube-rbac-proxy@sha256:5c8e4c25824a724eb7ffd11fa2e08caec66d9c01256fc35bfca6cccb146e3d9f
* registry.redhat.io/openshift-logging/logging-curator5-rhel8@sha256:6011467d9943b69be1ba2a7033cabc2011e738ae5c7ee084fe00cc32b313e5dd

#### 1. elasticsearch-rhel8-operator

原始信息:
* registry.redhat.io/openshift-logging/elasticsearch-rhel8-operator@sha256:973b388253d566cb7fa9c8893ae92e781b5ba5dbebea0fcbd5f4d8cdb4e1f90a
  原始bundle镜像
* hub.iefcu.cn/kcp/logging-operator-index-openshift-logging-elasticsearch-rhel8-operator@sha256:973b388253d566cb7fa9c8893ae92e781b5ba5dbebea0fcbd5f4d8cdb4e1f90a
  mirror镜像
* https://github.com/openshift/elasticsearch-operator/commit/2559aa9964032edef6315d6d82ea0d3f1422ccdf
  源码

修改Dockerfile内容如下: (就是修改编译镜像，基础镜像)
```diff
diff --git a/Dockerfile b/Dockerfile
index bc8be7ba..53db86b0 100644
--- a/Dockerfile
+++ b/Dockerfile
@@ -1,6 +1,7 @@
 ### This is a generated file from Dockerfile.in ###
 #@follow_tag(registry-proxy.engineering.redhat.com/rh-osbs/openshift-golang-builder:rhel_8_golang_1.16)
-FROM registry.ci.openshift.org/ocp/builder:rhel-8-golang-1.16-openshift-4.8 AS builder
+#FROM registry.ci.openshift.org/ocp/builder:rhel-8-golang-1.16-openshift-4.8 AS builder
+FROM hub.iefcu.cn/public/golang:1.16 AS builder


 ENV BUILD_VERSION=${CI_CONTAINER_VERSION}
@@ -26,7 +27,8 @@ ADD ${REMOTE_SOURCE}/Makefile ${REMOTE_SOURCE}/main.go ${REMOTE_SOURCE}/go.mod $
 RUN make build

 #@follow_tag(registry.redhat.io/ubi8:latest)
-FROM registry.ci.openshift.org/ocp/4.8:base
+#FROM registry.ci.openshift.org/ocp/4.8:base
+FROM hub.iefcu.cn/library/centos:7
 LABEL \
         io.k8s.display-name="OpenShift elasticsearch-operator" \
         io.k8s.description="This is the component that manages an Elasticsearch cluster on a kubernetes based platform" \
```


构建脚本adam.sh
```bash
# TODO: 自动化集成编译，参数生成
CI_CONTAINER_VERSION=v5.3.4
CI_X_VERSION=
CI_Y_VERSION=
CI_Z_VERSION=
CI_ELASTICSEARCH_OPERATOR_UPSTREAM_COMMIT=2559aa9964032edef6315d6d82ea0d3f1422ccdf
CI_ELASTICSEARCH_OPERATOR_UPSTREAM_URL=https://github.com/openshift/elasticsearch-operator
REMOTE_SOURCE=.

docker buildx build \
        -f Dockerfile.adam \
        --build-arg http_proxy=http://proxy.iefcu.cn:20172 --build-arg https_proxy=http://proxy.iefcu.cn:20172 \
        --build-arg no_proxy=yumrepo.unikylin.com.cn,192.0.0.0/8 \
        --build-arg CI_CONTAINER_VERSION=${CI_CONTAINER_VERSION} \
        --build-arg CI_X_VERSION=${CI_X_VERSION} \
        --build-arg CI_Y_VERSION=${CI_Y_VERSION} \
        --build-arg CI_Z_VERSION=${CI_Z_VERSION} \
        --build-arg CI_ELASTICSEARCH_OPERATOR_UPSTREAM_COMMIT=${CI_ELASTICSEARCH_OPERATOR_UPSTREAM_COMMIT} \
        --build-arg CI_ELASTICSEARCH_OPERATOR_UPSTREAM_URL=${CI_ELASTICSEARCH_OPERATOR_UPSTREAM_URL} \
        --build-arg REMOTE_SOURCE=${REMOTE_SOURCE} \
        --platform=linux/arm64,linux/amd64 \
        -t hub.iefcu.cn/kcp/elasticsearch-operator:20220224 . --push

        #-t hub.iefcu.cn/kcp/elasticsearch-operator:${CI_CONTAINER_VERSION} . --push
```

编译出镜像:
hub.iefcu.cn/kcp/elasticsearch-operator@sha256:b059084bee16e3a722ca5c0030a6db5136af0ab9d7b3cb0b2c2959e4512935b3


#### 2. elasticsearch-proxy-rhel8

原始信息:
* registry.redhat.io/openshift-logging/elasticsearch-proxy-rhel8@sha256:e2bb46b85e0b99cf44220b8908f11cf7946f27ca3873f1c19b6e5ac676aa0607
  原始bundle镜像
* hub.iefcu.cn/kcp/elasticsearch-proxy-rhel8@sha256:e2bb46b85e0b99cf44220b8908f11cf7946f27ca3873f1c19b6e5ac676aa0607
  mirror镜像
* https://github.com/openshift/elasticsearch-proxy/commit/b4a4ddf8c7daf631973c5ab7e8f34e4b6ed6740c
  源码


简单改一下dockerfile，和编译构建脚本即可

```diff
diff --git a/Dockerfile b/Dockerfile
index 09d78bd..8f33d68 100644
--- a/Dockerfile
+++ b/Dockerfile
@@ -1,6 +1,7 @@
 ### This is a generated file from Dockerfile.in ###
 #@follow_tag(registry-proxy.engineering.redhat.com/rh-osbs/openshift-golang-builder:rhel_8_golang_1.16)
-FROM registry.ci.openshift.org/ocp/builder:rhel-8-golang-1.16-openshift-4.8 AS builder
+#FROM registry.ci.openshift.org/ocp/builder:rhel-8-golang-1.16-openshift-4.8 AS builder
+FROM hub.iefcu.cn/public/golang:1.16 AS builder

 ENV BUILD_VERSION=1.0
 ENV OS_GIT_MAJOR=1
@@ -17,7 +18,8 @@ COPY ${REMOTE_SOURCE} .
 RUN make

 #@follow_tag(registry.redhat.io/ubi8:latest)
-FROM registry.ci.openshift.org/ocp/4.8:base
+#FROM registry.ci.openshift.org/ocp/4.8:base
+FROM hub.iefcu.cn/library/centos:7
 COPY --from=builder /go/src/github.com/openshift/elasticsearch-proxy/bin/elasticsearch-proxy /usr/bin/
 ENTRYPOINT ["/usr/bin/elasticsearch-proxy"]
```

```bash
# TODO: 自动化集成编译，参数生成
CI_CONTAINER_VERSION=v5.3.4
CI_X_VERSION=
CI_Y_VERSION=
CI_Z_VERSION=
CI_ELASTICSEARCH_PROXY_UPSTREAM_COMMIT=b4a4ddf
CI_ELASTICSEARCH_PROXY_UPSTREAM_URL=https://github.com/openshift/elasticsearch-proxy
REMOTE_SOURCE=.

docker buildx build \
    -f Dockerfile \
    --build-arg http_proxy=http://proxy.iefcu.cn:20172 --build-arg https_proxy=http://proxy.iefcu.cn:20172 \
    --build-arg no_proxy=yumrepo.unikylin.com.cn,192.0.0.0/8 \
    --build-arg CI_CONTAINER_VERSION=${CI_CONTAINER_VERSION} \
    --build-arg CI_X_VERSION=${CI_X_VERSION} \
    --build-arg CI_Y_VERSION=${CI_Y_VERSION} \
    --build-arg CI_Z_VERSION=${CI_Z_VERSION} \
    --build-arg CI_ELASTICSEARCH_PROXY_UPSTREAM_COMMIT=${CI_ELASTICSEARCH_PROXY_UPSTREAM_COMMIT} \
    --build-arg CI_ELASTICSEARCH_PROXY_UPSTREAM_URL=${CI_ELASTICSEARCH_PROXY_UPSTREAM_URL} \
    --build-arg REMOTE_SOURCE=${REMOTE_SOURCE} \
    --platform=linux/arm64,linux/amd64 \
    -t hub.iefcu.cn/kcp/elasticsearch-proxy-rhel8:20220407 . --push
```

编译出镜像:
hub.iefcu.cn/kcp/elasticsearch-proxy-rhel8:20220407@sha256:9892f7b7ad86d053f40619ecc8ab0c8fffc22877365f614c5362e8093b076b31

#### 3. ose-kube-rbac-proxy

原始信息:
* registry.redhat.io/openshift4/ose-kube-rbac-proxy@sha256:5c8e4c25824a724eb7ffd11fa2e08caec66d9c01256fc35bfca6cccb146e3d9f
  原始bundle镜像
* hub.iefcu.cn/kcp/ose-kube-rbac-proxy@sha256:5c8e4c25824a724eb7ffd11fa2e08caec66d9c01256fc35bfca6cccb146e3d9f
  mirror镜像
* https://github.com/openshift/kube-rbac-proxy/commit/14c288e6d19578d96e502def75995b882f1c9b37
  源码

修改Dockerfile.ocp
```diff
diff --git a/Dockerfile.ocp b/Dockerfile.ocp
index ac777e7..6a0e49b 100644
--- a/Dockerfile.ocp
+++ b/Dockerfile.ocp
@@ -1,4 +1,5 @@
-FROM registry.ci.openshift.org/ocp/builder:rhel-8-golang-1.15-openshift-4.7 AS builder
+#FROM registry.ci.openshift.org/ocp/builder:rhel-8-golang-1.15-openshift-4.7 AS builder
+FROM hub.iefcu.cn/public/golang:1.16 AS builder
 WORKDIR /go/src/github.com/brancz/kube-rbac-proxy
 COPY . .
 ENV GO111MODULE=on
@@ -7,7 +8,7 @@ ENV GOFLAGS="-mod=vendor"
 RUN make build && \
     cp _output/kube-rbac-proxy-$(go env GOOS)-$(go env GOARCH) _output/kube-rbac-proxy

-FROM registry.ci.openshift.org/ocp/4.7:base
+FROM hub.iefcu.cn/library/centos:7
 LABEL io.k8s.display-name="kube-rbac-proxy" \
       io.k8s.description="This is a proxy, that can perform Kubernetes RBAC authorization." \
       io.openshift.tags="openshift,kubernetes" \
```

```bash
docker buildx build \
        --build-arg http_proxy=http://proxy.iefcu.cn:20172 --build-arg https_proxy=http://proxy.iefcu.cn:20172 \
        --build-arg no_proxy=yumrepo.unikylin.com.cn,192.0.0.0/8 \
        --platform=linux/arm64,linux/amd64 \
        -f Dockerfile.ocp \
        -t hub.iefcu.cn/kcp/ose-kube-rbac-proxy:20220224 . --push
```

编译出镜像:
hub.iefcu.cn/kcp/ose-kube-rbac-proxy:20220224@sha256:40dd71d8c4e066eca94967a7025be026ace8d1af7ac0945fd52fd32785fe2cd7

#### 4. ose-oauth-proxy

原始信息:
* registry.redhat.io/openshift4/ose-oauth-proxy@sha256:9fff99a506db94ba61b08a8ae0ac5a049dff4f8b4453e96319115de293595dcf
  原始bundle镜像
* hub.iefcu.cn/kcp/ose-oauth-proxy@sha256:9fff99a506db94ba61b08a8ae0ac5a049dff4f8b4453e96319115de293595dcf
  mirror镜像
* https://github.com/openshift/oauth-proxy/commit/fd4dfe78bcd8373c545284a671499681f824c645
  源码

简单

编译出镜像:
hub.iefcu.cn/kcp/ose-oauth-proxy:20220407@sha256:4a5b51edd04cb02348b9ed3a04a1add5aba96b1086a81a8ad88e4faa2e846fd6

```diff
diff --git a/Dockerfile b/Dockerfile
index ceb4424..cf85d56 100644
--- a/Dockerfile
+++ b/Dockerfile
@@ -1,8 +1,10 @@
-FROM registry.ci.openshift.org/ocp/builder:rhel-8-golang-1.15-openshift-4.7 AS builder
+#FROM registry.ci.openshift.org/ocp/builder:rhel-8-golang-1.15-openshift-4.7 AS builder
+FROM hub.iefcu.cn/public/golang:1.16 AS builder
 WORKDIR  /go/src/github.com/openshift/oauth-proxy
 COPY . .
 RUN go build .

-FROM registry.ci.openshift.org/ocp/builder:rhel-8-base-openshift-4.7
+#FROM registry.ci.openshift.org/ocp/builder:rhel-8-base-openshift-4.7
+FROM hub.iefcu.cn/library/centos:7
 COPY --from=builder /go/src/github.com/openshift/oauth-proxy/oauth-proxy /usr/bin/oauth-proxy
 ENTRYPOINT ["/usr/bin/oauth-proxy"]
```

```bash
docker buildx build \
        --build-arg http_proxy=http://proxy.iefcu.cn:20172 --build-arg https_proxy=http://proxy.iefcu.cn:20172 \
        --build-arg no_proxy=yumrepo.unikylin.com.cn,192.0.0.0/8 \
        --platform=linux/arm64,linux/amd64 \
        -f Dockerfile \
        -t hub.iefcu.cn/kcp/ose-oauth-proxy:20220407 . --push
```

#### 5. elasticsearch6-rhel8

原始信息:
* registry.redhat.io/openshift-logging/elasticsearch6-rhel8@sha256:5faaf1cde7f7dcc9ed47ce84faf7942ae7c6a24b965ed3bf47be036c4e7596e7
  原始bundle镜像
* hub.iefcu.cn/kcp/elasticsearch6-rhel8@sha256:5faaf1cde7f7dcc9ed47ce84faf7942ae7c6a24b965ed3bf47be036c4e7596e7
  mirror镜像
* https://github.com/openshift/origin-aggregated-logging/commit/c5c0a97ffe8d3db56fa5b2fdf8dfc93dde35000d
  源码

同步ubi8基础镜像: registry.redhat.io/ubi8:latest

修改Dockerfile
```diff
diff --git a/elasticsearch/Dockerfile b/elasticsearch/Dockerfile
index 6465d71..9661687 100644
--- a/elasticsearch/Dockerfile
+++ b/elasticsearch/Dockerfile
@@ -1,7 +1,8 @@
 ### This is a generated file from Dockerfile.in ###

 #@follow_tag(registry.redhat.io/ubi8:latest)
-FROM registry.ci.openshift.org/ocp/builder:rhel-8-base-openshift-4.7
+#FROM registry.ci.openshift.org/ocp/builder:rhel-8-base-openshift-4.7
+FROM hub.iefcu.cn/public/ubi8
 ENV BUILD_VERSION=6.8.1
 ENV SOURCE_GIT_COMMIT=${CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_COMMIT:-}
 ENV SOURCE_GIT_URL=${CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_URL:-}
```

编写编译脚本adam.sh进行构建
```bash
# TODO: 自动化集成编译，参数生成
CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_COMMIT=c5c0a97ff
CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_URL=https://github.com/openshift/origin-aggregated-logging
REMOTE_SOURCE=.
OPENSHIFT_CI=true
#JAVA_VER
#packages
#MAVEN_REPO_URL
#upstream_code=.

docker build \
        -f Dockerfile \
        --build-arg http_proxy=http://proxy.iefcu.cn:20172 --build-arg https_proxy=http://proxy.iefcu.cn:20172 \
        --build-arg no_proxy=yumrepo.unikylin.com.cn,192.0.0.0/8 \
        --build-arg CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_COMMIT=${CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_COMMIT} \
        --build-arg CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_URL=${CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_URL} \
        --build-arg REMOTE_SOURCE=${REMOTE_SOURCE} \
        --build-arg OPENSHIFT_CI=${OPENSHIFT_CI} \
        -t hub.iefcu.cn/kcp/elasticsearch6-rhel8:20220407 .
```

由于网络问题，编译一直未成功
后面尝试了好多次，居然就成功了!


编译出镜像:
hub.iefcu.cn/kcp/elasticsearch6-rhel8@sha256:f40c7d0a645f5f3060c86760d1a9f857345cbbc1f099e8c521a0cf2a08ce1232


#### 6. kibana6-rhel8

发现是node 10.24，同步docker官方node:10镜像使用

由于切换了镜像，需要修改Dockerfile的地方有点多:
* NODE_PATH需要修正为/usr/local/bin
* KIBANA_CONF_DIR环境变量配置有点问题，需要修正!
* WORKDIR提前到sed命令之前!

修改Dockerfile内容
```diff
diff --git a/kibana/Dockerfile b/kibana/Dockerfile
index 7906de51b..d6dcdb1de 100644
--- a/kibana/Dockerfile
+++ b/kibana/Dockerfile
@@ -1,7 +1,8 @@
 ### This is a generated file from Dockerfile.in ###

 #@follow_tag(registry-proxy.engineering.redhat.com/rh-osbs/ubi8-nodejs-10:latest)
-FROM registry.ci.openshift.org/ocp/builder:rhel8.2.els.nodejs.10
+#FROM registry.ci.openshift.org/ocp/builder:rhel8.2.els.nodejs.10
+FROM hub.iefcu.cn/public/node:10
 ENV BUILD_VERSION=6.8.1
 ENV SOURCE_GIT_COMMIT=${CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_COMMIT:-}
 ENV SOURCE_GIT_URL=${CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_URL:-}
@@ -12,19 +13,20 @@ EXPOSE 5601

 ENV ELASTICSEARCH_URL=https://elasticsearch.openshift-logging.svc.cluster.local:9200 \
     HOME=/opt/app-root/src  \
-    KIBANA_CONF_DIR=${HOME}/config \
+    KIBANA_CONF_DIR=/opt/app-root/src/config \
     KIBANA_VERSION=6.8.1 \
     NODE_ENV=production \
     RELEASE_STREAM=prod \
     container=oci \
     NODE_ENV=production \
-    NODE_PATH=/usr/bin
+    NODE_PATH=/usr/local/bin

 ARG LOCAL_REPO

 USER 0

 ENV upstream_code=${upstream_code:-"."}
+RUN mkdir -p $HOME $KIBANA_CONF_DIR
 COPY  ${upstream_code}/vendored_tar_src/kibana-oss-6.8.1 ${HOME}/
 COPY  ${upstream_code}/vendored_tar_src/opendistro_security_kibana_plugin-0.10.0.4/ ${HOME}/plugins/opendistro_security_kibana_plugin-0.10.0.4/
 COPY  ${upstream_code}/vendored_tar_src/handlebars/ ${HOME}/node_modules/handlebars/
@@ -38,12 +40,12 @@ COPY  ${upstream_code}/kibana.yml ${KIBANA_CONF_DIR}/
 COPY  ${upstream_code}/run.sh ${HOME}/
 COPY  ${upstream_code}/utils ${HOME}/
 COPY  ${upstream_code}/module_list.sh ${HOME}/
+WORKDIR ${HOME}
 RUN sed -i -e 's/"node":.*/"node": "'$(${NODE_PATH}/node --version | sed 's/v//')'"/' package.json && \
     mkdir -p node && \
     ln -s ${NODE_PATH} node/bin
 RUN bin/kibana --optimize

-WORKDIR ${HOME}
 CMD ["./run.sh"]

 LABEL \

```

创建脚本adam.sh构建镜像
```bash
# TODO: 自动化集成编译，参数生成
CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_COMMIT=c5c0a97ff
CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_URL=https://github.com/openshift/origin-aggregated-logging
REMOTE_SOURCE=.
OPENSHIFT_CI=true
#JAVA_VER
#packages
#MAVEN_REPO_URL
#upstream_code=.

docker build \
        -f Dockerfile \
        --build-arg CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_COMMIT=${CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_COMMIT} \
        --build-arg CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_URL=${CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_URL} \
        --build-arg REMOTE_SOURCE=${REMOTE_SOURCE} \
        --build-arg OPENSHIFT_CI=${OPENSHIFT_CI} \
        -t hub.iefcu.cn/kcp/kibana6-rhel8:20220408 .
```

编译镜像:
hub.iefcu.cn/kcp/kibana6-rhel8@sha256:21f14af473cbe0d6e88d9feb1c85c9fafce15b86e2b004581ce748540f7377de

#### 7. logging-curator5-rhel8

同步ubi8-python-36镜像

修改Dockerfile, 简单使用替换构建镜像
```diff
diff --git a/curator/Dockerfile b/curator/Dockerfile
index fe3c92a05..a54fe3e2f 100644
--- a/curator/Dockerfile
+++ b/curator/Dockerfile
@@ -1,7 +1,8 @@
 ### This is a generated file from Dockerfile.in ###

 #@follow_tag(registry.redhat.io/ubi8/python-36:latest)
-FROM registry.ci.openshift.org/ocp/builder:ubi8.python.36
+#FROM registry.ci.openshift.org/ocp/builder:ubi8.python.36
+FROM hub.iefcu.cn/public/ubi8-python-36
```

编写adam.sh构建镜像
```bash
# TODO: 自动化集成编译，参数生成
CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_COMMIT=c5c0a97ff
CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_URL=https://github.com/openshift/origin-aggregated-logging
REMOTE_SOURCE=.

docker build \
        -f Dockerfile \
        --build-arg CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_COMMIT=${CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_COMMIT} \
        --build-arg CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_URL=${CI_ORIGIN_AGGREGATED_LOGGING_UPSTREAM_URL} \
        --build-arg REMOTE_SOURCE=${REMOTE_SOURCE} \
        -t hub.iefcu.cn/kcp/logging-curator5-rhel8:20220408 .
```

编译镜像:
hub.iefcu.cn/kcp/logging-curator5-rhel8@sha256:0d567aa570e2a3e5bcddb8c1641f37f9369dcd2c153c20a39408fe85bd5d32cb

## 定制catalog镜像

#### 修改bundle镜像

通过安装es operator得到bundle镜像，TODO: 更好的方法获取到bundle镜像地址
registry.redhat.io/openshift-logging/elasticsearch-operator-bundle@sha256:6a47a04e73b02fa27176b5508f78289a0bca9ed8328a52aea8c88e0c5720dc6c
=> hub.iefcu.cn/kcp/logging-operator-index-openshift-logging-elasticsearch-operator-bundle@sha256:6a47a04e73b02fa27176b5508f78289a0bca9ed8328a52aea8c88e0c5720dc6c

先手动提取出bundle镜像内容，然后进行修改
```bash
podman create --name es-bundle hub.iefcu.cn/kcp/logging-operator-index-openshift-logging-elasticsearch-operator-bundle@sha256:6a47a04e73b02fa27176b5508f78289a0bca9ed8328a52aea8c88e0c5720dc6c bash
podman cp es-bundle:/ ~/tmp/elasticsearch-operator-bundle-rootfs
```

TODO: 修改方法比较琐碎，等会弄一个diff文件上来, 后续弄成自动生成的？

制作成镜像:
hub.iefcu.cn/kcp/elasticsearch-operator-bundle:v4.9

#### 制作catalog镜像

TODO: elasticsearch, cluster logging合做成一个catalog镜像

注意: 这里没有arm64合适的基础镜像，就指定了原来的operator作为基础镜像(x86下也可以做arm64的镜像，因为不设计架构程序运行)
```bash
opm index add \
    --bundles hub.iefcu.cn/kcp/elasticsearch-operator-bundle:v4.9 \
    --tag hub.iefcu.cn/kcp/elasticsearch-operator-index:v4.9 \
    --binary-image hub.iefcu.cn/public/redhat-operator-index:v4.9@sha256:fd45ebb5619656628b84266793ddf24ef6a393cd3a85bc1b5315d5500c0bf067
    #--binary-image hub.iefcu.cn/public/redhat-operator-index:v4.9
```

上传catalog镜像
```bash
podman push hub.iefcu.cn/kcp/elasticsearch-operator-index:v4.9 
```

#### 创建自定义catalogSource

现在就可以基于catalogSource镜像，创建catalogSource了

```bash
cat << EOF | oc apply -f -
apiVersion: operators.coreos.com/v1alpha1
kind: CatalogSource
metadata:
  name: elasticsearch
  namespace: openshift-marketplace
spec:
  displayName: elasticsearch
  #image: 'hub.iefcu.cn/kcp/adam-operatorhub:20220224'
  image: 'hub.iefcu.cn/kcp/elasticsearch-operator-index:v4.9'
  publisher: elasticsearch
  sourceType: grpc
EOF
```

检查安装情况
```bash
oc -n openshift-marketplace get pod
oc -n openshift-marketplace get CatalogSource elasticsearch

删除catalogsource => 可以
oc -n  openshift-marketplace delete CatalogSource elasticsearch
```

### 同步operator相关镜像到私有仓库

TODO: filter-by-os ?
oc adm catalog mirror \
    registry.okd.example.com:5000/redhat/redhat-operator-index:v4.7  \
    file:///local/index \
    --index-filter-by-os="linux/amd64'" \
    -a /root/pull-secret.json \
    --insecure

```bash
# 同步grafana相关镜像到本地文件
mkdir mirror-xxx && cd mirror-xxx
oc adm catalog mirror \
    hub.iefcu.cn/kcp/redhat-operator-index:v4.9 \
    -a /tmp/pull-secret.json \
    file:///local/index

info: Mirroring completed in 1m45.84s (4.408MB/s)
wrote mirroring manifests to manifests-grafana-operator-index-1647941600

To upload local images to a registry, run:

        oc adm catalog mirror file://local/index/kcp/redhat-operator-index:v4.9 REGISTRY/REPOSITORY

# 同步镜像到私有镜像仓库
oc adm catalog mirror \
  file://local/index/kcp/redhat-operator-index:v4.9 \
  192.168.120.44/kcp/
  -a /tmp/pull-secret.json \
  --insecure
```



## cli命令安装elasticsearch operator

目前web控制台安装operator有一点问题，只能通过CLI安装

#### 1. 创建namespace

```bash
apiVersion: v1
kind: Namespace
metadata:
  name: openshift-operators-redhat
  annotations:
    openshift.io/node-selector: ""
  labels:
    openshift.io/cluster-monitoring: "true"
```

#### (可选)首先需要配置镜像mirror策略

可以一次配置多个mirrors
```bash
cat <<EOM | oc apply -f -
apiVersion: operator.openshift.io/v1alpha1
kind: ImageContentSourcePolicy
metadata:
  name: elasticsearch-operator
spec:
  repositoryDigestMirrors:
  - mirrors:
    - hub.iefcu.cn/kcp
    source: registry.redhat.io/openshift-logging
  - mirrors:
    - hub.iefcu.cn/kcp/ose-oauth-proxy
    source: registry.redhat.io/openshift4/ose-oauth-proxy
  - mirrors:
    - hub.iefcu.cn/kcp/ose-kube-rbac-proxy
    source: registry.redhat.io/openshift4/ose-kube-rbac-proxy
EOM

cat <<EOM | oc apply -f -
apiVersion: operator.openshift.io/v1alpha1
kind: ImageContentSourcePolicy
metadata:
  name: redhat-openshift4
spec:
  repositoryDigestMirrors:
  - mirrors:
    - hub.iefcu.cn/kcp
    source: registry.redhat.io/openshift4
EOM
```

检查mirror策略

oc get  ImageContentSourcePolicy elasticsearch-operator

#### 2. 创建OperatorGroup

注意：这个operatorGroup指明安装的operator服务于所有namespace(spec为空)
```
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: openshift-operators-redhat
  namespace: openshift-operators-redhat
spec: {}
```

#### 3. 订阅安装operator

参考: https://docs.openshift.com/container-platform/4.8/operators/admin/olm-adding-operators-to-cluster.html#olm-installing-operator-from-operatorhub-using-cli_olm-adding-operators-to-a-cluster

```bash
cat <<EOM | oc apply -f -
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: elasticsearch-operator
  #namespace: openshift-operators
  namespace: "openshift-operators-redhat"
spec:
  channel: stable
  installPlanApproval: Automatic
  name: elasticsearch-operator
  source: elasticsearch
  sourceNamespace: openshift-marketplace
EOM
```

#### 4. 创建Role和RoleBinding

参考: https://blog.csdn.net/weixin_43902588/article/details/105586460

上报promethues数据使用的吧？

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: prometheus-k8s
  namespace: openshift-operators-redhat
rules:
- apiGroups:
  - ""
  resources:
  - services
  - endpoints
  - pods
  verbs:
  - get
  - list
  - watch
```

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: prometheus-k8s
  namespace: openshift-operators-redhat
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: prometheus-k8s
subjects:
- kind: ServiceAccount
  name: prometheus-k8s
  namespace: openshift-operators-redhat
```

## 使用elasticsearch operator

### 在CLI下使用

由于web控制暂时没有适配好，暂时先在CLI下使用
配置bundle配置文件，支持arm64,可以在web控制台安装es operator了!

#### 1. 创建ES单节点

```bash
0s          Warning   FailedMount             pod/elasticsearch-cdm-jbfq5xj0-1-7846dddbdb-7cb7w                  MountVolume.SetUp failed for volume "certificates" : secret "elasticsearch" not found
0s          Warning   FailedMount             pod/elasticsearch-cdm-jbfq5xj0-1-7846dddbdb-tql6k                  Unable to attach or mount volumes: unmounted volumes=[certificates], unattached volumes=[elasticsearch-storage elasticsearch-config certificates kube-api-access-z98q8 elasticsearch-metrics]: timed out waiting for the condition
0s          Warning   FailedMount             pod/elasticsearch-cdm-jbfq5xj0-1-7846dddbdb-7cb7w                  MountVolume.SetUp failed for volume "certificates" : secret "elasticsearch" not found
```

搜索发现，这个ES operator是不能独立于cluster logging，不能单独使用的!!! 参考[redhat bug](https://bugzilla.redhat.com/show_bug.cgi?id=1686298)

#### 2. 创建ES集群

```bash
```

#### 3. 创建kibana节点
