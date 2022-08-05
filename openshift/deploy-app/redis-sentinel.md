# redis哨兵模式分析调研

## 问题

sentinel集群怎么配置的?

## 整体方案

本文中的Redis高可用方案采用Sentinel(哨兵)模式（一个master:M1、两个slave:R2、R3，每个redis节点都有一个Sentinel:S1、S2、S3），Sentinel自身也是一个集群。在reids集群出现故障的时候，会自动进行故障转移，从而保证集群的可用性。

![](../../imgs/redis-arch.png)

## 使用helm部署

在线部署
```
helm repo add bitnami https://charts.bitnami.com/bitnami

helm install bitnami-redis –set master.service.type=NodePort –set cluster.enabled=true –set sentinel.enabled=true –set metrics.enabled=true –set password=redis bitnami/redis –namespace=kube-public
```

## sentinel原理

https://www.jianshu.com/p/231afa35d937

二、Sentinel的工作方式:

* 1.每个Sentinel以每秒钟一次的频率向它所知的Master，Slave以及其他 Sentinel 实例发送一个 PING 命令
* 2.如果一个实例（instance）距离最后一次有效回复 PING 命令的时间超过 down-after-milliseconds 选项所指定的值， 则这个实例会被 Sentinel 标记为主观下线。
* 3.如果一个Master被标记为主观下线，则正在监视这个Master的所有 Sentinel 要以每秒一次的频率确认Master的确进入了主观下线状态。
* 4.当有足够数量的 Sentinel（大于等于配置文件指定的值）在指定的时间范围内确认Master的确进入了主观下线状态， 则Master会被标记为客观下线
* 5.在一般情况下， 每个 Sentinel 会以每 10 秒一次的频率向它已知的所有Master，Slave发送 INFO 命令
* 6.当Master被 Sentinel 标记为客观下线时，Sentinel 向下线的 Master 的所有 Slave 发送 INFO 命令的频率会从 10 秒一次改为每秒一次
* 7.若没有足够数量的 Sentinel 同意 Master 已经下线， Master 的客观下线状态就会被移除。
* 8.若 Master 重新向 Sentinel 的 PING 命令返回有效回复， Master 的主观下线状态就会被移除。


## 其他资料

这个是kubernets的示例，有redis sentinel?
https://github.com/kubernetes/examples/tree/561467fb9d5f5c2126da5c500067de3c0fbd7d60/staging/storage/redis

在K8s上部署Redis集群的方法步骤
https://www.jb51.net/article/210827.htm
=> 通过这篇文章，了解到了redis集群的一些原理

在Deployment中，与之对应的服务是service，而在StatefulSet中与之对应的headless service，headless service，即无头服务，与service的区别就是它没有Cluster IP，**解析它的名称时将返回该Headless Service对应的全部Pod的Endpoint列表。**

除此之外，StatefulSet在Headless Service的基础上又为StatefulSet控制的每个Pod副本创建了一个DNS域名，这个域名的格式为：
```
$(podname).(headless server name)   
FQDN： $(podname).(headless server name).namespace.svc.cluster.local
```

由于Redis集群必须在所有节点启动后才能进行初始化，而如果将初始化逻辑写入Statefulset中，则是一件非常复杂而且低效的行为。这里，本人不得不称赞一下原项目作者的思路，值得学习。也就是说，我们可以在K8S上创建一个额外的容器，专门用于进行K8S集群内部某些服务的管理控制。

至此，大家可能会疑惑，那为什么没有使用稳定的标志，Redis Pod也能正常进行故障转移呢？这涉及了Redis本身的机制。**因为，Redis集群中每个节点都有自己的NodeId（保存在自动生成的nodes.conf中），并且该NodeId不会随着IP的变化和变化，这其实也是一种固定的网络标志。**也就是说，就算某个Redis Pod重启了，该Pod依然会加载保存的NodeId来维持自己的身份。

## 参考资料

* [【redis可高用】在Kubernetes中部署基于Sentinel模式的高可用的redis](https://www.kubernetes.org.cn/7659.html)
* [](https://www.jb51.net/article/210827.htm)
* [Redis哨兵模式（sentinel）学习总结及部署记录（主从复制、读写分离、主从切换）](https://www.cnblogs.com/kevingrace/p/9004460.html)
