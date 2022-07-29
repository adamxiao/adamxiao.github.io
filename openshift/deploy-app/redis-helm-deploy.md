# redis helm部署

部署redis哨兵模式集群

参考:
redis 6.0
https://github.com/bitnami/charts, commit 89ba29c54868c1dc2b917abc5565eab8ef95134b
redis 6.2
https://github.com/bitnami/charts, commit e1efdc5f29a1ebfd581be41ec530dbd001bbfb50

修改点如下
* 制作arm64下的redis镜像（最重要最复杂）
* 以及放了离线的common依赖(charts/common子目录)
* 禁用redis密码
* 启用redis sentinel模式

```diff
diff --git a/bitnami/redis/values.yaml b/bitnami/redis/values.yaml
index 2d05d9246..2bca65f0c 100644
--- a/bitnami/redis/values.yaml
+++ b/bitnami/redis/values.yaml
@@ -76,9 +76,10 @@ diagnosticMode:
 ## @param image.debug Enable image debug mode
 ##
 image:
-  registry: docker.io
-  repository: bitnami/redis
-  tag: 6.2.7-debian-11-r3
+  registry: hub.iefcu.cn
+  repository: public/redis
+  #tag: 6.2.7-debian-11-r3
+  tag: adam-redis6.2
   ## Specify a imagePullPolicy
   ## Defaults to 'Always' if image tag is 'latest', else set to 'IfNotPresent'
   ## ref: https://kubernetes.io/docs/user-guide/images/#pre-pulling-images
@@ -109,7 +110,7 @@ architecture: replication
 auth:
   ## @param auth.enabled Enable password authentication
   ##
-  enabled: true
+  enabled: false
   ## @param auth.sentinel Enable password authentication on sentinels too
   ##
   sentinel: true
@@ -915,7 +916,7 @@ sentinel:
   ## IMPORTANT: this will disable the master and replicas services and
   ## create a single Redis&reg; service exposing both the Redis and Sentinel ports
   ##
-  enabled: false
+  enabled: true
   ## Bitnami Redis&reg; Sentinel image version
   ## ref: https://hub.docker.com/r/bitnami/redis-sentinel/tags/
   ## @param sentinel.image.registry Redis&reg; Sentinel image registry
@@ -926,9 +927,10 @@ sentinel:
   ## @param sentinel.image.debug Enable image debug mode
   ##
   image:
-    registry: docker.io
-    repository: bitnami/redis-sentinel
-    tag: 6.2.7-debian-11-r4
+    registry: hub.iefcu.cn
+    repository: public/redis-sentinel
+    #tag: 6.2.7-debian-11-r4
+    tag: adam-redis6.2
     ## Specify a imagePullPolicy
     ## Defaults to 'Always' if image tag is 'latest', else set to 'IfNotPresent'
     ## ref: https://kubernetes.io/docs/user-guide/images/#pre-pulling-images
```

#### 最终简化安装步骤

* 1.导入相关镜像
* 2.使用离线redis charts
  解压后就是一个redis charts目录, 目录名为redis
* 3.准备helm客户端程序
```bash
# arm64
wget https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/helm/3.7.1/helm-linux-arm64.tar.gz
# x86
wget https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/helm/3.7.1/helm-linux-amd64.tar.gz
```
* 4.最后一键安装
```
oc new-project redis-sentinel
oc adm policy add-scc-to-user anyuid -n redis-sentinel -z redis
./helm install redis redis
```

## 构建相关镜像

#### bitnami redis镜像

源码:
https://github.com/bitnami/bitnami-docker-redis, commit 12d7f563c4dffcf807c3c5f1b42e1e4ee05c7c4b

适配构建arm61镜像改动:
* 修改dockerfile适配改动
* 从redis官方镜像中拷贝redis等二进制构建镜像
* 编译一个wait-for-port的arm64程序
  https://github.com/bitnami/wait-for-port/archive/refs/tags/v1.0.3.tar.gz
* 放一个redis默认配置文件

Dockerfile改动点：
```
diff --git a/6.2/debian-11/Dockerfile b/6.2/debian-11/Dockerfile
index e2090f82..ea494cc2 100644
--- a/6.2/debian-11/Dockerfile
+++ b/6.2/debian-11/Dockerfile
@@ -1,17 +1,25 @@
+FROM hub.iefcu.cn/public/redis:6.2.7 as builder
+
 FROM docker.io/bitnami/minideb:bullseye
 LABEL maintainer "Bitnami <containers@bitnami.com>"
 
 ENV HOME="/" \
-    OS_ARCH="amd64" \
+    OS_ARCH="arm64" \
     OS_FLAVOUR="debian-11" \
     OS_NAME="linux"
 
 COPY prebuildfs /
 # Install required system packages and dependencies
-RUN install_packages acl ca-certificates curl gzip libc6 libssl1.1 procps tar
-RUN . /opt/bitnami/scripts/libcomponent.sh && component_unpack "wait-for-port" "1.0.3-150" --checksum 1013e2ebbe58e5dc8f3c79fc952f020fc5306ba48463803cacfbed7779173924
-RUN . /opt/bitnami/scripts/libcomponent.sh && component_unpack "redis" "6.2.7-150" --checksum adcd2145c174a1e1b922991956cc451d77f05b4beb472f02b25e2e45f886c2c4
-RUN . /opt/bitnami/scripts/libcomponent.sh && component_unpack "gosu" "1.14.0-150" --checksum da4a2f759ccc57c100d795b71ab297f48b31c4dd7578d773d963bbd49c42bd7b
+RUN install_packages acl ca-certificates curl gzip libc6 libssl1.1 procps tar gosu
+# redis-server redis-tools 
+COPY --from=builder /usr/local/bin/redis-server /usr/bin/redis-server
+COPY --from=builder /usr/local/bin/redis-cli /usr/bin/redis-cli
+RUN mkdir -p /opt/bitnami/bin /opt/bitnami/redis/etc/
+ADD ./wait-for-port /opt/bitnami/bin
+ADD ./redis-default.conf /opt/bitnami/redis/etc/
+#RUN . /opt/bitnami/scripts/libcomponent.sh && component_unpack "wait-for-port" "1.0.3-150" --checksum 1013e2ebbe58e5dc8f3c79fc952f020fc5306ba48463803cacfbed7779173924
+#RUN . /opt/bitnami/scripts/libcomponent.sh && component_unpack "redis" "6.2.7-150" --checksum adcd2145c174a1e1b922991956cc451d77f05b4beb472f02b25e2e45f886c2c4
+#RUN . /opt/bitnami/scripts/libcomponent.sh && component_unpack "gosu" "1.14.0-150" --checksum da4a2f759ccc57c100d795b71ab297f48b31c4dd7578d773d963bbd49c42bd7b
 RUN apt-get update && apt-get upgrade -y && \
     rm -r /var/lib/apt/lists /var/cache/apt/archives
 RUN chmod g+rwX /opt/bitnami
```

构建镜像
```
docker build \
  --build-arg http_proxy=http://proxy.iefcu.cn:20172 \
  --build-arg https_proxy=http://proxy.iefcu.cn:20172 \
  -t hub.iefcu.cn/public/redis-sentinel:adam-redis6.2 .
```

wait-for-port源码构建略微变动
```
diff --git a/Dockerfile b/Dockerfile
index 7f25cb1..1c66b96 100644
--- a/Dockerfile
+++ b/Dockerfile
@@ -15,9 +15,10 @@ RUN rm -rf out

 RUN make

-RUN upx --ultra-brute out/wait-for-port
+#RUN upx --ultra-brute out/wait-for-port

 FROM bitnami/minideb:stretch
+#FROM hub.iefcu.cn/public/minideb:stretch

 COPY --from=build /go/src/app/out/wait-for-port /usr/local/bin/

diff --git a/Makefile b/Makefile
index 661faa7..2ede780 100644
--- a/Makefile
+++ b/Makefile
@@ -20,7 +20,7 @@ build/%:
        @GOARCH=$(*F) go build -ldflags=$(LDFLAGS) -o $(TOOL_PATH)
        @echo "*** Binary created under $(TOOL_PATH) ***"

-build: build/amd64
+build: build/arm64

 clean:
        @rm -rf $(BUILD_DIR)
```

#### bitnami redis sentinel镜像

源码:
https://www.github.com/bitnami/bitnami-docker-redis-sentinel, commit 2e4c51ee87145e93dfd56f6eb82587e3dbe04a24

适配构建arm61镜像改动:
* 修改适配dockerfile
* 放置sentinel默认配置文件
* 从redis官方镜像拉取redis-sentinel二进制

dockerfile改动
```
diff --git a/6.2/debian-11/Dockerfile b/6.2/debian-11/Dockerfile
index 68d4f353..ff11c9c2 100644
--- a/6.2/debian-11/Dockerfile
+++ b/6.2/debian-11/Dockerfile
@@ -1,17 +1,25 @@
-FROM docker.io/bitnami/minideb:bullseye
+FROM hub.iefcu.cn/public/redis:6.2.7 as builder
+
+FROM hub.iefcu.cn/public/minideb:bullseye
 LABEL maintainer "Bitnami <containers@bitnami.com>"

 ENV HOME="/" \
-    OS_ARCH="amd64" \
+    OS_ARCH="arm64" \
     OS_FLAVOUR="debian-11" \
     OS_NAME="linux" \
     PATH="/opt/bitnami/redis-sentinel/bin:/opt/bitnami/common/bin:$PATH"

 COPY prebuildfs /
 # Install required system packages and dependencies
-RUN install_packages acl ca-certificates curl gzip libc6 libssl1.1 procps tar
-RUN . /opt/bitnami/scripts/libcomponent.sh && component_unpack "redis-sentinel" "6.2.7-150" --checksum 006b2ea3252061aaf999b30ec5d796f2170cd64b5a2bf97c55e3ff515836d08c
-RUN . /opt/bitnami/scripts/libcomponent.sh && component_unpack "gosu" "1.14.0-150" --checksum da4a2f759ccc57c100d795b71ab297f48b31c4dd7578d773d963bbd49c42bd7b
+RUN install_packages acl ca-certificates curl gzip libc6 libssl1.1 procps tar gosu
+# redis-sentinel redis-server redis-tools
+COPY --from=builder /usr/local/bin/redis-server /usr/bin/redis-server
+COPY --from=builder /usr/local/bin/redis-cli /usr/bin/redis-cli
+COPY --from=builder /usr/local/bin/redis-sentinel /usr/bin/redis-sentinel
+RUN mkdir -p /opt/bitnami/redis-sentinel/etc
+ADD ./sentinel.conf /opt/bitnami/redis-sentinel/etc/sentinel.conf
+#RUN . /opt/bitnami/scripts/libcomponent.sh && component_unpack "redis-sentinel" "6.2.7-150" --checksum 006b2ea3252061aaf999b30ec5d796f2170cd64b5a2bf97c55e3ff515836d08c
+#RUN . /opt/bitnami/scripts/libcomponent.sh && component_unpack "gosu" "1.14.0-150" --checksum da4a2f759ccc57c100d795b71ab297f48b31c4dd7578d773d963bbd49c42bd7b
 RUN apt-get update && apt-get upgrade -y && \
     rm -r /var/lib/apt/lists /var/cache/apt/archives
 RUN chmod g+rwX /opt/bitnami
```

构建镜像
```
docker build \
  --build-arg http_proxy=http://proxy.iefcu.cn:20172 \
  --build-arg https_proxy=http://proxy.iefcu.cn:20172 \
  -t hub.iefcu.cn/public/redis-sentinel:adam-redis6.2 .
```

#### redis sentinel proxy镜像

源码:
https://github.com/flant/redis-sentinel-proxy, commit 9d49112274678ef8c3eb75e3890601967cacb44f

后续需要优化
改动点:
```
diff --git a/Dockerfile b/Dockerfile
index 940d603..687b1c0 100644
--- a/Dockerfile
+++ b/Dockerfile
@@ -1,4 +1,4 @@
-FROM golang:1.17 AS builder
+FROM hub.iefcu.cn/public/golang:1.16 AS builder
 LABEL Andrey Kolashtov <andrey.kolashtov@flant.com>

 ADD . /redis-sentinel-proxy/
@@ -6,10 +6,11 @@ WORKDIR /redis-sentinel-proxy
 RUN go mod init redis-sentinel-proxy && \
     go build -o redis-sentinel-proxy .

-FROM alpine:3.14
+#FROM hub.iefcu.cn/public/alpine:3.14
+FROM hub.iefcu.cn/public/centos:7

 COPY --from=builder /redis-sentinel-proxy/redis-sentinel-proxy /usr/local/bin/redis-sentinel-proxy
-RUN apk --update --no-cache add redis
+#RUN apk --update --no-cache add redis

 ENTRYPOINT ["/usr/local/bin/redis-sentinel-proxy"]
-CMD ["-master", "mymaster"]
+CMD ["-listen", "0.0.0.0:6379", "-master", "mymaster", "-sentinel", "redis-headless:26379"]
```

直接构建镜像:
```
docker build \
  --build-arg http_proxy=http://proxy.iefcu.cn:20172 \
  --build-arg https_proxy=http://proxy.iefcu.cn:20172 \
  -t hub.iefcu.cn/xiaoyun/redis-sentinel-proxy:arm64 .
```

部署方法:
https://github.com/shishirkh/redis-ha, commit 8557805f770afa4b1b662637bd82077911065699
需要略微改动一下proxy.yaml, 把镜像和redis服务改一下

#### OT-CONTAINER-KIT redis operator的redis镜像

源码: https://github.com/OT-CONTAINER-KIT/redis, commit b15dd8ef9e329d6fec8716bcb85add852b4cdea0

改动:
???

#### OT-CONTAINER-KIT redis operator的redis exporter镜像

源码: https://github.com/oliver006/redis_exporter.git, commit 18080da36b0a97595d308cfb4bdf92eb1e396c44

直接构建镜像

## FAQ

当时适配redis6.0, charts里面某些配置不支持，必须使用redis6.2

## 参考资料

* [bitnami charts - redis](https://github.com/bitnami/charts)
