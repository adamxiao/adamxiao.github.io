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
* ucloud/redis-operator
  crd不兼容, 待调整

使用operator方式安装stateful应用是比较合适的。

## external service

https://ot-container-kit.github.io/redis-operator/guide/redis-cluster-config.html#helm-parameters
externalService.enabled

https://ot-container-kit.github.io/redis-operator/guide/configuration.html#helm-parameters

https://github.com/OT-CONTAINER-KIT/helm-charts/tree/main/charts/redis-cluster
externalService.enabled
=> 其实就是额外新建了一个service

https://ot-container-kit.github.io/redis-operator/guide/redis.html
Challenges with Kubernetes
We have to use the headless service of Redis because it’s a TCP based service and normal service is HTTP(Layer 7) based Loadbalancer. So in case of headless service, no ClusterIP will be used and we have to rely on Pod IP.

配置external service的效果!
root@53efee9aa862:/data# redis-cli -c -h 192.168.100.201
192.168.100.201:6379> set adam 1
(error) CLUSTERDOWN Hash slot not served

root@53efee9aa862:/data# redis-cli -h 192.168.100.201
192.168.100.201:6379> set adam 1
(error) CLUSTERDOWN The cluster is down
192.168.100.201:6379>

https://cloud.tencent.com/developer/article/1919678
Redis集群Hash槽分配异常 CLUSTERDOWN Hash slot not served的解决方式


使用another redis desktop manager连接:
redis client on error: Failed to refresh slots cache 
https://github.com/luin/ioredis/issues/711
=> 单机模式不能这样用, 而且k8s的redis的pod ip地址会变化的！！！

https://cnodejs.org/topic/577364910b982e0450b74586
遇到的issue

Failed to refresh slots cache
https://github.com/luin/ioredis/issues/220

如果本地没有配置集群， 不要使用new ioredis.Cluster()方法去创建redisClient,
而是用new ioredis(‘6379’, ‘127.0.0.1’)去创建client[跟node-redis一样了]
redisCluster = [{port : 6379, host: ‘redis-server-host1’},{port : 6379, host: ‘redis-server-host2’}];
if(isRedisCluster){
	redisClient = new ioredis.Cluster(redisCluster);
} else {
	redisClient = new ioredis(6379, ‘127.0.0.1’);
}

关键字《redis集群模式 k8s给外部应用使用》

[(好 - 符合期望)云原生中间件——Redis Operator篇](http://blog.daocloud.io/5271.html)
=> 但是没有实际操作步骤
对外可达：

有一些方案在实现的时候，需要外部非容器化的服务也可以使用容器化的中间件能力，这就是对外可达的意思。

只是在选择对应的方案的时候，会有不同的选择，有的支持 K8s 的 NodePort Service，有的支持 LoabBalancer Service，有的基于开源 haproxy、nginx、envoy 或者商业化的 4 层负载，还可以使用 eBPF 实现高性能的 4 层负载，如 Cilium 中的 XDP LB 等等。

[Kubernetes使用operator安装Redis集群 原创](https://blog.51cto.com/heian99/3219763)
https://github.com/ucloud/redis-cluster-operator#deploy-redis-cluster-operator

[(好)Redis Operator学习笔记](https://blog.csdn.net/shijinghan1126/article/details/108224874)
https://www.infoq.cn/article/ppp3lrqf8bapcg3aznl3
因此我们决定为operator平台提供一个快速创建哨兵模式的redis集群的redis operator。
我们定制开发了Redis Operator在Github上开源：https://github.com/ucloud/redis-operator，提供：

使用Redis Operator我们可以很方便的起一个哨兵模式的集群，集群只有一个Master节点，多个slave节点，假如指定Redis集群的size为3，那么Redis Operator就会帮我们启动一个master节点，2个slave节点，同时启动是3个sentinel节点来管理Redis集群：

=> 目前这个比较合适!

关键字《为redis集群配置4层代理》

关键字《traefik为redis集群配置4层代理》
=> 没啥资料

https://www.cnblogs.com/wy123/p/12829673.html
伴随着Redis6.0的发布，作为最令人怦然心动的特性之一，Redis官方同时推出Redis集群的proxy了：redis-cluster-proxy，https://github.com/RedisLabs/redis-cluster-proxy
相比从前访问Redis集群时需要制定集群中所有的IP节点相比：
1，redis的redis-cluster-proxy实现了redis cluster集群节点的代理（屏蔽），类似于VIP但又比VIP简单，客户端不需要知道集群中的具体节点个数和主从身份，可以直接通过代理访问集群。
2，不仅如此，还是具有一些非常实用的改进，比如在redis集群模式下，增加了对multiple操作的支持，跨slot操作等等（有点关系数据库的分库分表中间件的感觉）。

如果没有源码开发能力，相比其他第三方proxy中间件，必须要承认官方可靠性和权威性。
那么，redis-cluster-proxy是一个完美的解决方案么，留下两个问题
1，如何解决redis-cluster-proxy单点故障？
2，proxy节点的如何面对网络流量风暴？

https://www.cnblogs.com/xiexun/p/15061298.html
在k8s上手动创建redis集群

5. tips
5.1 集群哪怕只有一个节点可访问，也要按照集群配置方式
  否则报错例如MOVED 1545 10.244.3.239:6379","data":false
  如本文的情况，redis cluster的每个节点都是一个跑在k8s里面的pod，这些pod并不能被外部直接访问，而是通过ingress等方法对外暴露一个访问接口，即只有一个统一的ip：port给外部访问。经由k8s的调度，对这个统一接口的访问会被发送到redis集群的某个节点。这时候对redis的用户来说，看起来这就像是一个单节点的redis。但是，此时无论是直接使用命令行工具redis-cli，还是某种语言的sdk，还是需要按照集群来配置redis的连接信息，才能正确连接，例如

## redis集群模式

关键字《redis集群》

#### 一. 一主多从+哨兵模式

> 数据就是一份，从节点是主节点的备份，哨兵用来切主用的

架构如下:

![](../../imgs/redis-arch.png)


参考: [Redis 你了解 Redis 的三种集群模式吗？](https://segmentfault.com/a/1190000022808576)

#### 使用operator创建redis哨兵模式集群

https://github.com/ucloud/redis-operator

#### 构建redis-operator镜像arm64

```
diff --git a/Dockerfile b/Dockerfile
index 31f75d3..9c31243 100644
--- a/Dockerfile
+++ b/Dockerfile
@@ -1,7 +1,7 @@
-FROM golang:1.13.3-alpine as go-builder
+FROM hub.iefcu.cn/public/golang:1.16 as go-builder

-RUN apk update && apk upgrade && \
-    apk add --no-cache ca-certificates git mercurial
+#RUN apt update && \
+#    apt install ca-certificates git mercurial

 ARG PROJECT_NAME=redis-operator
 ARG REPO_PATH=github.com/ucloud/$PROJECT_NAME
@@ -18,18 +18,18 @@ RUN GOPROXY=https://goproxy.cn,direct go mod download

 COPY pkg ./ cmd ./ version ./

-RUN GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -o ${GOBIN}/${PROJECT_NAME} \
+RUN GOOS=linux CGO_ENABLED=0 go build -o ${GOBIN}/${PROJECT_NAME} \
     -ldflags "-X ${REPO_PATH}/pkg/version.Version=${VERSION} -X ${REPO_PATH}/pkg/version.GitSHA=${GIT_SHA}" \
     $BUILD_PATH

 # =============================================================================
-FROM alpine:3.9 AS final
+FROM hub.iefcu.cn/public/centos:7 AS final

 ARG PROJECT_NAME=redis-operator

 COPY --from=go-builder ${GOBIN}/${PROJECT_NAME} /usr/local/bin/${PROJECT_NAME}

-RUN adduser -D ${PROJECT_NAME}
+RUN adduser ${PROJECT_NAME}
 USER ${PROJECT_NAME}

 ENTRYPOINT ["/usr/local/bin/redis-operator"]
```

podman build -t hub.iefcu.cn/xiaoyun/redis-operator:0.1.7 .

#### 部署operator

Deploy redis operator
Register the RedisCluster custom resource definition (CRD).
```
kubectl create -f deploy/crds/redis_v1beta1_rediscluster_crd.yaml
```

A namespace-scoped operator watches and manages resources in a single namespace, whereas a cluster-scoped operator watches and manages resources cluster-wide. You can chose run your operator as namespace-scoped or cluster-scoped.
```
// cluster-scoped
$ kubectl create -f deploy/service_account.yaml
$ kubectl create -f deploy/cluster/cluster_role.yaml
$ kubectl create -f deploy/cluster/cluster_role_binding.yaml
$ kubectl create -f deploy/cluster/operator.yaml

// namespace-scoped
kubectl create -f deploy/service_account.yaml
kubectl create -f deploy/namespace/role.yaml
kubectl create -f deploy/namespace/role_binding.yaml
kubectl create -f deploy/namespace/operator.yaml
```

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

还有一个redis-export (v1.5.2)
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

## redis-cli命令使用

获取从信息
```
127.0.0.1:6379> INFO replication
# Replication
role:slave
master_host:redis-node-1.redis-headless.redis.svc.cluster.local
master_port:6379
master_link_status:up
master_last_io_seconds_ago:1
master_sync_in_progress:0
slave_read_repl_offset:669785
slave_repl_offset:669785
slave_priority:100
slave_read_only:1
replica_announced:1
connected_slaves:0
master_failover_state:no-failover
master_replid:7246075702d4b3c9cd95243d962b75da98c9fc31
master_replid2:0000000000000000000000000000000000000000
master_repl_offset:669785
second_repl_offset:-1
repl_backlog_active:1
repl_backlog_size:1048576
repl_backlog_first_byte_offset:1
repl_backlog_histlen:669785
```


获取集群信息
```
# redis-cli -c -h 192.168.0.100 -p 7000 cluster info
cluster info
```

```
cluster_state:ok
cluster_slots_assigned:16384
cluster_slots_ok:16384
cluster_slots_pfail:0
cluster_slots_fail:0
cluster_known_nodes:6
cluster_size:3
cluster_current_epoch:6
cluster_my_epoch:1
cluster_stats_messages_ping_sent:101
cluster_stats_messages_pong_sent:98
cluster_stats_messages_sent:199
cluster_stats_messages_ping_received:93
cluster_stats_messages_pong_received:101
cluster_stats_messages_meet_received:5
cluster_stats_messages_received:199
```

查看集群数据槽分配
```
cluster slots
```

输出类似以下信息：

```
1) 1) (integer) 5461
   2) (integer) 10922
   3) 1) "127.0.0.1"
      2) (integer) 7001
   4) 1) "127.0.0.1"
      2) (integer) 7004
2) 1) (integer) 0
   2) (integer) 5460
   3) 1) "127.0.0.1"
      2) (integer) 7000
   4) 1) "127.0.0.1"
      2) (integer) 7003
3) 1) (integer) 10923
   2) (integer) 16383
   3) 1) "127.0.0.1"
      2) (integer) 7002
   4) 1) "127.0.0.1"
      2) (integer) 7005
```

## redis集群反向代理

https://blog.51cto.com/u_15098012/2613071
Redis代理插件
Redis代理插件有很多,这儿简单介绍几款

* predixy	高性能全特征redis代理，支持Redis Sentinel和Redis Cluster
  => 文章推荐这个
* twemproxy	快速、轻量级memcached和redis代理
* codis	redis集群代理解决方案
* redis-cerberus	Redis Cluster代理

https://cloud.tencent.com/developer/article/1442949
1.2. 代理分区方案
客户端 发送请求到一个 代理组件，代理 解析 客户端 的数据，并将请求转发至正确的节点，最后将结果回复给客户端。

 优点：简化 客户端 的分布式逻辑，客户端 透明接入，切换成本低，代理的 转发 和 存储 分离。
 缺点：多了一层 代理层，加重了 架构部署复杂度 和 性能损耗。

https://www.zhaohuabing.com/post/2020-10-14-redis-cluster-with-istio/
通过 Istio 下发 Redis Cluster 相关的 Envoy 配置
在下面的步骤中，我们将通过 Istio 向 Envoy Sidecar 下发 Redis Cluster 相关配置，以在无需改动客户端的情况下启用 Redis Cluster 的高级功能，包括数据分片、读写分离和流量镜像。
=> 只有理论

关键字《k8s部署predixy》
https://zhuanlan.zhihu.com/p/445316238
=> 通过deployment部署了2个副本, 极度复杂

https://github.com/joyieldInc/predixy/issues/128
=> predixy无法处理pod ip地址变化的情况！！！

## helm chart直接部署redis集群

https://github.com/bitnami/charts/tree/master/bitnami/redis

oc adm policy add-scc-to-user anyuid -n redis -z redis

```
[core@master1 ~]$ ./helm install redis redis
WARNING: Kubernetes configuration file is group-readable. This is insecure. Location: /var/home/core/.kube/config
NAME: redis
LAST DEPLOYED: Tue Jun 21 12:19:40 2022
NAMESPACE: metallb-system
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
CHART NAME: redis
CHART VERSION: 16.12.2
APP VERSION: 6.2.7

** Please be patient while the chart is being deployed **

Redis&reg; can be accessed on the following DNS names from within your cluster:

    redis-master.metallb-system.svc.cluster.local for read/write operations (port 6379)
    redis-replicas.metallb-system.svc.cluster.local for read-only operations (port 6379)



To get your password run:

    export REDIS_PASSWORD=$(kubectl get secret --namespace metallb-system redis -o jsonpath="{.data.redis-password}" | base64 -d)

To connect to your Redis&reg; server:

1. Run a Redis&reg; pod that you can use as a client:

   kubectl run --namespace metallb-system redis-client --restart='Never'  --env REDIS_PASSWORD=$REDIS_PASSWORD  --image docker.io/bitnami/redis:6.2.7-debian-11-r3 --command -- sleep infinity

   Use the following command to attach to the pod:

   kubectl exec --tty -i redis-client \
   --namespace metallb-system -- bash

2. Connect using the Redis&reg; CLI:
   REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -h redis-master
   REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -h redis-replicas

To connect to your database from outside the cluster execute the following commands:

    kubectl port-forward --namespace metallb-system svc/redis-master 6379:6379 &
    REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -h 127.0.0.1 -p 6379
```

REDISCLI_AUTH=eB8JaY9JJz redis-cli

TODO: 构建bitnami相关redis镜像
从redis镜像中找到源码
https://github.com/bitnami/bitnami-docker-redis
https://www.github.com/bitnami/bitnami-docker-redis-sentinel

## FAQ

#### 1.Readiness probe failed: bash: /usr/bin/healthcheck.sh: No such file or directory

redis镜像不对，没有健康检测脚本

#### 2.<jemalloc>: Unsupported system page size

在运行环境编译 redis镜像才行

#### 3. redis 哨兵集群有问题, 每个节点都变成主了!

原因确实是dns解析有问题，删除重启另外两个pod即可!

redis容器日志如下: dns解析有问题？
```
[core@master1 ~]$ oc -n redis logs --tail 20 redis-node-2 redis
 01:23:40.32 INFO  ==> about to run the command: timeout 220 redis-cli -h redis.redis.svc.cluster.local -p 26379 sentinel get-master-addr-by-name mymaster
Could not connect to Redis at redis.redis.svc.cluster.local:26379: Temporary failure in name resolution
 01:24:10.36 INFO  ==> Configuring the node as master
1:C 28 Jun 2022 01:24:10.441 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
1:C 28 Jun 2022 01:24:10.441 # Redis version=6.2.7, bits=64, commit=00000000, modified=0, pid=1, just started
1:C 28 Jun 2022 01:24:10.441 # Configuration loaded
1:M 28 Jun 2022 01:24:10.442 * monotonic clock: POSIX clock_gettime
1:M 28 Jun 2022 01:24:10.460 # A key '__redis__compare_helper' was added to Lua globals which is not on the globals allow list nor listed on the deny list.
1:M 28 Jun 2022 01:24:10.460 * Running mode=standalone, port=6379.
1:M 28 Jun 2022 01:24:10.460 # WARNING: The TCP backlog setting of 511 cannot be enforced because /proc/sys/net/core/somaxconn is set to the lower value of 128.
1:M 28 Jun 2022 01:24:10.460 # Server initialized
1:M 28 Jun 2022 01:24:10.466 * Reading RDB preamble from AOF file...
1:M 28 Jun 2022 01:24:10.466 * Loading RDB produced by version 6.2.7
1:M 28 Jun 2022 01:24:10.466 * RDB age 414839 seconds
1:M 28 Jun 2022 01:24:10.466 * RDB memory usage when created 1.91 Mb
1:M 28 Jun 2022 01:24:10.466 * RDB has an AOF tail
1:M 28 Jun 2022 01:24:10.466 # Done loading RDB, keys loaded: 1, keys expired: 0.
1:M 28 Jun 2022 01:24:10.466 * Reading the remaining AOF tail...
1:M 28 Jun 2022 01:24:10.467 * DB loaded from append only file: 0.003 seconds
1:M 28 Jun 2022 01:24:10.467 * Ready to accept connections
```

哨兵日志
```
[core@master1 ~]$ oc -n redis logs --tail 20 redis-node-2 sentinel
 01:23:58.23 INFO  ==> about to run the command: redis-cli -h redis.redis.svc.cluster.local -p 26379 sentinel get-master-addr-by-name mymaster
Could not connect to Redis at redis.redis.svc.cluster.local:26379: Temporary failure in name resolution
1:X 28 Jun 2022 01:24:28.502 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
1:X 28 Jun 2022 01:24:28.502 # Redis version=6.2.7, bits=64, commit=00000000, modified=0, pid=1, just started
1:X 28 Jun 2022 01:24:28.502 # Configuration loaded
1:X 28 Jun 2022 01:24:28.503 * monotonic clock: POSIX clock_gettime
1:X 28 Jun 2022 01:24:28.504 # A key '__redis__compare_helper' was added to Lua globals which is not on the globals allow list nor listed on the deny list.
1:X 28 Jun 2022 01:24:28.504 * Running mode=sentinel, port=26379.
1:X 28 Jun 2022 01:24:28.504 # WARNING: The TCP backlog setting of 511 cannot be enforced because /proc/sys/net/core/somaxconn is set to the lower value of 128.
1:X 28 Jun 2022 01:24:28.505 # Sentinel ID is 9fe32540b27937ed9f341b0f610a0d8df405bb63
1:X 28 Jun 2022 01:24:28.505 # +monitor master mymaster redis-node-2.redis-headless.redis.svc.cluster.local 6379 quorum 2
```

## 其他

[redis desktop manager连接redis集群_redis集群](https://www.cxyzjd.com/article/weixin_42298507/113315629)

后续备份恢复的文章
[Take a logical backup of the Redis database using Stash](https://stash.run/docs/v2021.11.24/addons/redis/helm/)

[Production Checklist for Redis on Kubernetes](https://medium.com/swlh/production-checklist-for-redis-on-kubernetes-60173d5a5325)
Bitnami supports two deployment options for Redis: a master-slave cluster with Redis Sentinel and a Redis cluster topology with sharding. 

关键字《openshift搭建redis 哨兵模式》

https://www.cnblogs.com/dukuan/p/9913420.html
=> 手动搭建redis sentinel
说明：个人认为在k8s上搭建Redis sentinel完全没有意义，经过测试，当master节点宕机后，sentinel选择新的节点当主节点，当原master恢复后，此时无法再次成为集群节点。因为在物理机上部署时，sentinel探测以及更改配置文件都是以IP的形式，集群复制也是以IP的形式，但是在容器中，虽然采用的StatefulSet的Headless Service来建立的主从，但是主从建立后，master、slave、sentinel记录还是解析后的IP，但是pod的IP每次重启都会改变，所有sentinel无法识别宕机后又重新启动的master节点，所以一直无法加入集群，虽然可以通过固定podIP或者使用NodePort的方式来固定，或者通过sentinel获取当前master的IP来修改配置文件，但是个人觉得也是没有必要的，sentinel实现的是高可用Redis主从，检测Redis Master的状态，进行主从切换等操作，但是在k8s中，无论是dc或者ss，都会保证pod以期望的值进行运行，再加上k8s自带的活性检测，当端口不可用或者服务不可用时会自动重启pod或者pod的中的服务，所以当在k8s中建立了Redis主从同步后，相当于已经成为了高可用状态，并且sentinel进行主从切换的时间不一定有k8s重建pod的时间快，所以个人认为在k8s上搭建sentinel没有意义。所以下面搭建sentinel的步骤无需在看。 

https://cloud.tencent.com/developer/article/1752570
Sentinel节点至少3个且奇数，这样才能在协议中形成多数派。配置Sentinel节点配置文件/usr/local/redis/sentinel-26377.conf，主要注意以下参数
=> TODO: 验证哨兵效果!

127.0.0.1:26377> info sentinel
可以看到master改为127.0.0.1:6378了。

故障转移的大体步骤如下：

每个Sentinel节点每隔1秒对主、从、其他Sentinel阶段发送ping探测，超过down-after-milliseconds未返回响应，则判断该节点主观下线。
Sentinel节点向其他Sentinel节点询问对于异常节点的判断，当达到 quorum个sentinel节点都认为被主观下线的节点异常时，则对该节点做客观下线。
在sentinel节点中通过Raft算法选举出一个leader来完成故障转移。
当出现故障的节点是主节点时，sentinel leader会根据优先级、复制偏移量、runid等在从节点中选出一个作为主节点，执行slaveof no one命令。
 leader向其他从节点发送指令，让他们成为新主的从节点，并将原来的主节点更新为从节点，当旧主恢复后去复制新主的数据。
复制完成后，发布主节点的切换消息。

[5分钟实现用docker搭建Redis集群模式和哨兵模式](http://fykcy.top/?m=home&c=View&a=index&aid=5007)

[【redis可高用】在Kubernetes中部署基于Sentinel模式的高可用的redis](https://www.kubernetes.org.cn/7659.html)
本文中的Redis高可用方案采用Sentinel(哨兵)模式（一个master:M1、两个slave:R2、R3，每个redis节点都有一个Sentinel:S1、S2、S3），Sentinel自身也是一个集群。在reids集群出现故障的时候，会自动进行故障转移，从而保证集群的可用性。
=> 就是使用bitnami的redis helm仓库

helm install bitnami-redis –set master.service.type=NodePort –set cluster.enabled=true –set sentinel.enabled=true –set metrics.enabled=true –set password=redis bitnami/redis –namespace=kube-public

其中：

* 使用的charts为bitnami/redis；
* 通过设置cluster.enabled为true，启用redis集群模式；
* 通过设置sentinel.enabled为true，启用哨兵模式；
* 通过设置metrics.enabled为true，允许指标被外部进行监控；
* 通过设置master.service.type类型为NodePort，外部应用通过宿主机IP+端口访问redis服务。

[开发者openshift4使用入门教程 - 12 - 部署redis - 哨兵模式](https://www.modb.pro/db/149797)
https://www.infoq.cn/article/ppp3lrqf8bapcg3aznl3
具体使用的Operator为: ucloud/redis-operator
=> crd不兼容, 应该挺好的！

https://www.modb.pro/db/43922
=> 只有理论
Redis 服务对外暴露
容器化环境不同于物理环境或者虚拟机环境，容器环境的容器IP不固定，而且容器平台使用overlay网络，网络IP对集群外不可见。在这种情景下，若应用与Redis同集群部署，可以使用为Redis Cluster建立的Service来访问，但是如果有集群外访问的需求，该种方式则不能满足。对此，需要为每个单独的Redis Pod建立NodePort型的Service，并且在Redis中增加如下配置:

## 编译bitnami redis arm64镜像

#### 编译redis sentinel镜像

参考:
https://downloads.bitnami.com/files/stacksmith/redis-sentinel-6.2.7-150-linux-amd64-debian-11.tar.gz

修改dockerfile, 直接通过apt安装redis-sentinel, gosu
```
docker build \
  --build-arg http_proxy=http://proxy.iefcu.cn:20172 \
  --build-arg https_proxy=http://proxy.iefcu.cn:20172 \
  -t hub.iefcu.cn/xiaoyun/redis-sentinel:adam .
```

#### 编译redis镜像

先编译一个wait-for-port程序出来
通过下载wait-for-port amd64程序得到源码
https://github.com/bitnami/wait-for-port/archive/refs/tags/v1.0.3.tar.gz

```
构建wait-for-port程序
```

下载redis amd64版本的配置文件!
/opt/bitnami/redis/etc/redis-default.conf

https://downloads.bitnami.com/files/stacksmith/redis-6.2.7-150-linux-amd64-debian-11.tar.gz

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

关键字《headless service 是什么》
[Headless Service使用场景](https://blog.csdn.net/qq_33326449/article/details/117401847)
有状态应用，例如数据库

例如主节点可以对数据库进行读写操作，而其它的两个工作节点只能读，在这里客户端就没必要指定pod服务的集群地址，直接指定数据库Pod ip地址即可，这里需要绑定dns，客户端访问dns，dns会自动返回pod IP地址列表

* 无头服务不需要指定集群地址
* 无头服务适用有状态应用例如数据库
* 无头服务dns查询会返回pod列表，开发人员可以自定义负载均衡策略
* 普通Service可以通过负载均衡路由到不同的容器应用

#### 参考文档

https://docs.bitnami.com/kubernetes/infrastructure/redis/get-started/understand-cluster-topologies/
https://docs.bitnami.com/google-templates/infrastructure/redis/get-started/understand-cluster-config/
https://docs.bitnami.com/kubernetes/infrastructure/redis-cluster/get-started/compare-solutions/
[Deploy a Redis Sentinel Kubernetes cluster using Bitnami Helm charts](https://docs.bitnami.com/tutorials/deploy-redis-sentinel-production-cluster/)
[[bitnami/redis] How to Access Redis Master Node in the Redis Sentinel Deployment outside the K8s Cluster](https://github.com/bitnami/charts/issues/4082)

关键字《redis sentinel headless service》
其他
直接通过statefulset来部署redis复制集群
https://www.containiq.com/post/deploy-redis-cluster-on-kubernetes

https://www.linkedin.com/pulse/creating-redis-cluster-kubernetes-shishir-khandelwal
proxy cluster

## ucloud/redis-operator部署哨兵模式

下载operator yaml配置
https://github.com/ucloud/redis-operator/archive/refs/tags/v0.1.7.tar.gz

或者直接使用最新的master
关键字《crd v1beta1 to v1》
https://redhat-connect.gitbook.io/certified-operator-guide/ocp-deployment/operator-metadata/update-crds-from-v1beta1

The CustomResourceDefinition "redisclusters.redis.kun" is invalid: spec.validation.openAPIV3Schema.type: Required value: must not be empty at the root
spec.validation.openAPIV3Schema.type

https://downloads.bitnami.com/files/stacksmith/redis-sentinel-6.0.16-150-linux-amd64-debian-11.tar.gz
https://downloads.bitnami.com/files/stacksmith/redis-6.0.16-150-linux-amd64-debian-11.tar.gz

## 参考文档

* [redis operator github，有文档有源码](https://github.com/ot-container-kit/redis-operator)
* [redis operator官方安装文档](https://ot-container-kit.github.io/redis-operator/guide/installation.html)
