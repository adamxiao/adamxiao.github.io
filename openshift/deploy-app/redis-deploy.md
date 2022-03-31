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

![](https://segmentfault.com/img/remote/1460000022808582)


参考: [Redis 你了解 Redis 的三种集群模式吗？](https://segmentfault.com/a/1190000022808576)


#### 二. redis自带集群模式

## 通过源码编译生成redis-operator镜像

修改Dockerfile, 使用定制
```
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
