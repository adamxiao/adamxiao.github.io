# redis集群部署

思路:
* 1.使用openshift operatorhub上的redis operator部署redis集群
	暂不行，只有x86的版本
* 2.使用operatorhub.io上的redis operator部署redis集群
    暂不行，一样只有x86的operator镜像
* 3.直接通过redis operator的yaml文件部署operator
    可以，通过源码编译构建arm64的redis operator镜像
* 4.通过开发者目录的redis模板部署redis
    待研究
* 5.openshift直接部署redis集群
    待研究

使用operator方式安装stateful应用是比较合适的。

## redis集群模式

关键字《redis集群》

#### 一. 一主多从+哨兵模式

> 数据就是一份，从节点是主节点的备份，哨兵用来切主用的

架构如下:

![](../../imgs/redis-arch.png)


参考: [Redis 你了解 Redis 的三种集群模式吗？](https://segmentfault.com/a/1190000022808576)


#### 二. redis自带集群模式

## 通过源码编译生成redis-operator镜像

https://github.com/OT-CONTAINER-KIT/redis-operator
* (detached from v0.9.0)

修改Dockerfile, 使用定制
```diff
diff --git a/Dockerfile b/Dockerfile
index 1c38d14..3bd86d7 100644
--- a/Dockerfile
+++ b/Dockerfile
@@ -1,5 +1,5 @@
 # Build the manager binary
-FROM golang:1.15 as builder
+FROM hub.iefcu.cn/public/golang:1.16 as builder

 WORKDIR /workspace
 # Copy the Go Modules manifests
@@ -16,11 +16,11 @@ COPY controllers/ controllers/
 COPY k8sutils/ k8sutils/

 # Build
-RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 GO111MODULE=on go build -a -o manager main.go
+RUN CGO_ENABLED=0 GO111MODULE=on go build -a -o manager main.go

 # Use distroless as minimal base image to package the manager binary
 # Refer to https://github.com/GoogleContainerTools/distroless for more details
-FROM gcr.io/distroless/static:nonroot
+FROM hub.iefcu.cn/public/gcr.io-distroless-static:nonroot
 WORKDIR /
 COPY --from=builder /workspace/manager .
 USER 65532:65532
```

构建镜像
```
docker buildx build \
  --build-arg http_proxy=http://proxy.iefcu.cn:20172 \
  --build-arg https_proxy=http://proxy.iefcu.cn:20172 \
  --platform=linux/arm64,linux/amd64 \
  -t hub.iefcu.cn/public/redis-operator:20220209 . --push
```

还有一个redis-export
```
podman build -f ./docker/Dockerfile.arm64 -t hub.iefcu.cn/public/redis-exporter:1.0-arm64 .
origin  https://github.com/oliver006/redis_exporter.git (push)
* (detached from 18080da)
```


## 使用community operatorhub安装redis operator

参考 [operatorhub离线安装](../operatorhub-offline.html)

### 同步镜像

```bash
#podman pull registry.redhat.io/redhat/community-operator-index:v4.9

# 裁剪只保留 redis operator
opm index prune -f hub.iefcu.cn/public/community-operator-index:v4.9 \
    -p redis-operator \
    -t hub.iefcu.cn/kcp/redis-operator-index:v4.9
podman push hub.iefcu.cn/kcp/redis-operator-index:v4.9

# 同步redis相关镜像到本地文件
mkdir mirror-redis && cd mirror-redis
oc adm catalog mirror \
    hub.iefcu.cn/kcp/redis-operator-index:v4.9 \
    file:///local/index

```

## 通过redis operator的yaml文件部署operator

准备工作:
```bash
oc new-project redis-operator
oc adm policy add-scc-to-user privileged -n redis-operator -z redis-operator
```

参考: https://ot-container-kit.github.io/redis-operator/guide/installation.html

```bash
kubectl apply -f https://raw.githubusercontent.com/OT-CONTAINER-KIT/redis-operator/master/config/crd/bases/redis.redis.opstreelabs.in_redis.yaml
kubectl apply -f https://raw.githubusercontent.com/OT-CONTAINER-KIT/redis-operator/master/config/crd/bases/redis.redis.opstreelabs.in_redisclusters.yaml
kubectl apply -f https://raw.githubusercontent.com/OT-CONTAINER-KIT/redis-operator/master/config/rbac/serviceaccount.yaml
kubectl apply -f https://raw.githubusercontent.com/OT-CONTAINER-KIT/redis-operator/master/config/rbac/role.yaml
kubectl apply -f https://raw.githubusercontent.com/OT-CONTAINER-KIT/redis-operator/master/config/rbac/role_binding.yaml
kubectl apply -f https://raw.githubusercontent.com/OT-CONTAINER-KIT/redis-operator/master/config/manager/manager.yaml
```

## 创建redis实例

#### 创建redis单例

```yaml
apiVersion: redis.redis.opstreelabs.in/v1beta1
kind: Redis
metadata:
  name: redis-standalone
spec:
  kubernetesConfig:
    image: 'quay.io/opstree/redis:v6.2.5'
    imagePullPolicy: IfNotPresent
    resources:
      requests:
        cpu: 101m
        memory: 128Mi
      limits:
        cpu: 101m
        memory: 128Mi
    serviceType: ClusterIP
  storage:
    volumeClaimTemplate:
      spec:
        accessModes:
          - ReadWriteOnce
        resources:
          requests:
            storage: 1Gi
  redisExporter:
    enabled: false
    image: 'quay.io/opstree/redis-exporter:1.0'
```

#### 创建redis集群

```yaml
apiVersion: redis.redis.opstreelabs.in/v1beta1
kind: RedisCluster
metadata:
  name: redis-cluster
spec:
  clusterSize: 3
  kubernetesConfig:
    image: 'quay.io/opstree/redis:v6.2.5'
    imagePullPolicy: IfNotPresent
    resources:
      requests:
        cpu: 101m
        memory: 128Mi
      limits:
        cpu: 101m
        memory: 128Mi
  redisExporter:
    enabled: false
    image: 'quay.io/opstree/redis-exporter:1.0'
  redisLeader:
    serviceType: ClusterIP
  redisFollower:
    serviceType: ClusterIP
  storage:
    volumeClaimTemplate:
      spec:
        accessModes:
          - ReadWriteOnce
        resources:
          requests:
            storage: 1Gi
```

## FQA

#### 1.Readiness probe failed: bash: /usr/bin/healthcheck.sh: No such file or directory

redis镜像不对，没有健康检测脚本

#### 2.<jemalloc>: Unsupported system page size

在运行环境编译 redis镜像才行

## 参考文档

* [redis operator github，有文档有源码](https://github.com/ot-container-kit/redis-operator)
* [redis operator官方安装文档](https://ot-container-kit.github.io/redis-operator/guide/installation.html)
