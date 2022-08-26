# ElasticSearch入门

## ES健康问题分析

思路:
* 查glusterfs日志 => 难, 让存储组搞
* 安装新版本es集群(使用新operator等) => 理论上存储有问题，es升级也用
* glusterfs使用数据存储 => 可行, 最终验证可以
* 加大ES内存 => 验证没啥效果, 2g->4g

JD的管理卷问题:
强制启动卷, 因为有一些卷居然3副本，只启动了2个副本
gluster v start xxx force
self-heal还是不行!!!

脑裂严重, 节点一下子就掉了! node-0就不工作了


0825

es集群插入数据测试，es节点掉线等异常分析；
* 家里ＥＳ集群难以复现问题
* 网络感觉有点问题, broken pipe
* ＥＳ节点掉线, 504错误
* ES节点的卷出问题, not connected
  问dzh说是脑裂，而卷的self-heal进程不正常，所以有问题!!!
  => 可能也跟某些卷部分online有关, 引发脑裂?

家里集群，早上从red变为yellow, 再变为green了(可能是首次启动正常流程, 不用管)
查看健康状态, 分片比例为83.3%
```
epoch      timestamp cluster status node.total node.data shards pri relo init unassign pending_tasks max_task_wait_time active_shards_percent
1661309030 02:43:50  test1   yellow          3         3      5   3    0    1        0             0                  -                 83.3%
* Connection #0 to host test1-es-test.apps.kcp2-arm.iefcu.cn left intact

# 启动完成后分片正常, 没有init分片了
epoch      timestamp cluster status node.total node.data shards pri relo init unassign pending_tasks max_task_wait_time active_shards_percent
1661310282 03:04:42  test1   green           3         3      6   3    0    0        0             0                  -                100.0%
```


看主节点的日志, 可以看到状态的变更, 是由于分片变化导致的
```
{"type": "server", "timestamp": "2022-08-24T02:35:16,613Z", "level": "INFO", "component": "o.e.c.s.MasterService", "cluster.name": "test1", "node.name": "test1-es-default-1", "message": "node-join[{test1-es-default-0}{iHBh1x8KS2up-LymKgpBvQ}{GEuDGW9OTwCelhCTNxhOgA}{10.131.0.9}{10.131.0.9:9300}{cdfhilmrstw} join existing leader], term: 4, version: 91, delta: added {{test1-es-default-0}{iHBh1x8KS2up-LymKgpBvQ}{GEuDGW9OTwCelhCTNxhOgA}{10.131.0.9}{10.131.0.9:9300}{cdfhilmrstw}}", "cluster.uuid": "qaXRmMjjQMWUw95VzaUx-A", "node.id": "F64ndk-1QQqcEifzIWFI9A"  }
{"type": "server", "timestamp": "2022-08-24T02:35:18,599Z", "level": "INFO", "component": "o.e.c.s.ClusterApplierService", "cluster.name": "test1", "node.name": "test1-es-default-1", "message": "added {{test1-es-default-0}{iHBh1x8KS2up-LymKgpBvQ}{GEuDGW9OTwCelhCTNxhOgA}{10.131.0.9}{10.131.0.9:9300}{cdfhilmrstw}}, term: 4, version: 91, reason: Publication{term=4, version=91}", "cluster.uuid": "qaXRmMjjQMWUw95VzaUx-A", "node.id": "F64ndk-1QQqcEifzIWFI9A"  }
{"type": "server", "timestamp": "2022-08-24T02:40:50,737Z", "level": "INFO", "component": "o.e.c.r.a.AllocationService", "cluster.name": "test1", "node.name": "test1-es-default-1", "message": "Cluster health status changed from [RED] to [YELLOW] (reason: [shards started [[alert][0]]]).", "cluster.uuid": "qaXRmMjjQMWUw95VzaUx-A", "node.id": "F64ndk-1QQqcEifzIWFI9A"  }
{"type": "server", "timestamp": "2022-08-24T02:45:43,272Z", "level": "INFO", "component": "o.e.c.r.a.AllocationService", "cluster.name": "test1", "node.name": "test1-es-default-1", "message": "Cluster health status changed from [YELLOW] to [GREEN] (reason: [shards started [[alert][0]]]).", "cluster.uuid": "qaXRmMjjQMWUw95VzaUx-A", "node.id": "F64ndk-1QQqcEifzIWFI9A"  }
```

0824下午
虽然时green,但是节点数量只有2个，剩下一个pod卷挂载有问题!
这个卷只有两个副本在线，导致无法挂载(宿主机mount居然也返回0)
```
[2022-08-23 05:47:52.507810] E [glusterfsd.c:828:gf_remember_backup_volfile_server] 0-glusterfs: failed to set volfile server: File exists
Mounting glusterfs on /var/lib/kubelet/pods/2fc73605-b0b3-4d1c-9088-0da459ce7828/volumes/kubernetes.io~glusterfs/pvc-7c7f77e7-006b-4c19-8828-5306d8f931a4 failed.
, the following error information was pulled from the glusterfs log to help diagnose this issue:
[2022-08-23 05:47:56.638067] E [rpc-clnt.c:346:saved_frames_unwind] (--> /lib64/libglusterfs.so.0(_gf_log_callingfn+0xf8)[0xffff8bcda858] (--> /lib64/libgfrpc.so.0(+0xd664)[0xffff8bc5d664] (--> /lib64/libgfrpc.so.0(+0xd7b0)[0xffff8bc5d7b0] (--> /lib64/libgfrpc.so.0(rpc_clnt_connection_cleanup+0xa4)[0xffff8bc5e764] (--> /lib64/libgfrpc.so.0(+0xf308)[0xffff8bc5f308] ))))) 0-glusterfs: forced unwinding frame type(GlusterFS Handshake) op(GETSPEC(2)) called at 2022-08-23 05:47:52.566903 (xid=0x2)
[2022-08-23 05:47:56.638216] E [glusterfsd-mgmt.c:2159:mgmt_getspec_cbk] 0-mgmt: failed to fetch volume file (key:vol_79e8fdd0065647356c57a65bb0659d1e)
  Warning  FailedMount     15m (x14 over 27m)   kubelet  (combined from similar events): Unable to attach or mount volumes: unmounted volumes=[elasticsearch-data], unattached volumes=[elastic-internal-elasticsearch-config-local elasticsearch-logs elastic-internal-scripts elastic-internal-elasticsearch-bin-local elastic-internal-probe-user downward-api elasticsearch-data elastic-internal-http-certificates elastic-internal-transport-certificates elastic-internal-unicast-hosts elastic-internal-remote-certificate-authorities elastic-internal-elasticsearch-config elastic-internal-elasticsearch-plugins-local elastic-internal-xpack-file-realm]: timed out waiting for the condition
  Normal   AddedInterface  13m                  multus   Add eth0 [10.128.0.16/23] from openshift-sdn
  Normal   Pulled          13m                  kubelet  Container image "hub.iefcu.cn/public/elasticsearch:7.16.3" already present on machine
  Normal   Created         13m                  kubelet  Created container elastic-internal-init-filesystem
  Normal   Started         13m                  kubelet  Started container elastic-internal-init-filesystem
  Normal   Pulled          13m                  kubelet  Container image "hub.iefcu.cn/public/elasticsearch:7.16.3" already present on machine
  Normal   Created         13m                  kubelet  Created container elastic-internal-suspend
  Normal   Pulled          10m (x5 over 13m)    kubelet  Container image "hub.iefcu.cn/public/elasticsearch:7.16.3" already present on machine
  Warning  Unhealthy       5m19s (x4 over 10m)  kubelet  (combined from similar events): Readiness probe failed: {"timestamp": "2022-08-23T06:11:48+00:00", "message": "readiness probe failed", "curl_rc": "7"}
  Warning  BackOff         31s (x50 over 12m)   kubelet  Back-off restarting failed container
[core@master1 ~]$ oc get pods
NAME                 READY   STATUS             RESTARTS        AGE
test1-es-default-0   0/1     CrashLoopBackOff   9 (2m19s ago)   20h
test1-es-default-1   1/1     Running            2               20h
test1-es-default-2   1/1     Running            2               20h
[core@master1 ~]$ oc get ElasticSearch
NAME    HEALTH   NODES   VERSION   PHASE   AGE
test1   green    2       7.16.3    Ready   20h
```

关键字＜es集群状态red＞

0823早上
es状态变红，变黄，然后又变绿了!

kcp2-arm集群的ES集群有问题．．．
由于是集群突然断电导致，暂时不管这个问题吧
```
[core@master1 ~]$ oc get pods
NAME                 READY   STATUS             RESTARTS       AGE
test1-es-default-0   1/1     Running            3              6h5m
test1-es-default-1   0/1     CrashLoopBackOff   14 (85s ago)   6h5m
test1-es-default-2   0/1     PodInitializing    2              6h5m
```

节点异常, 而且不会自动恢复...
```
[core@master1 ~]$ oc get ElasticSearch
NAME    HEALTH    NODES   VERSION   PHASE             AGE
test1   unknown   1       7.16.3    ApplyingChanges   6h28m
```

```
5s          Warning   Unhealthy                pod/test1-es-default-1                                        Readiness probe errored: rpc error: code = NotFound desc = container is not created or running: checking if PID of 66b2d37926b15f6379a6120de642204c1ee38cf42e81d44b1b403e9ce13f8a49 is running failed: container process not found
5s          Warning   FailedMount              pod/test1-es-default-2                                        MountVolume.SetUp failed for volume "pvc-cfe95f39-a2e4-4125-9c7d-36ce34ea6209" : mount failed: mount failed: exit status 1...
```

kcp1-arm单节点ES集群测试情况
```
2022-08-22 08:56:43.558  INFO 611 --- [       Thread-5] c.estest.Application$ApplicationRunner   : 共：4432999条,已插入：4416000条,执行时间：3899s,平均：1132/s
2022-08-22 08:56:44.228  INFO 611 --- [      Thread-11] c.estest.Application$ApplicationRunner   : 共：4433999条,已插入：4417000条,执行时间：3900s,平均：1132/s
2022-08-22 08:56:44.730  INFO 611 --- [      Thread-10] c.estest.Application$ApplicationRunner   : 共：4434999条,已插入：4418000条,执行时间：3900s,平均：1132/s
2022-08-22 08:56:45.457  INFO 611 --- [       Thread-8] c.estest.Application$ApplicationRunner   : 共：4435999条,已插入：4419000条,执行时间：3901s,平均：1132/s
2022-08-22 08:56:46.681  INFO 611 --- [       Thread-2] c.estest.Application$ApplicationRunner   : 共：4436999条,已插入：4420000条,执行时间：3902s,平均：1132/s
```

查看健康状态失败!
```
$ curl -v -u "elastic:$PASSWORD" -k "http://test1-es-test.apps.kcp2-arm.iefcu.cn/_cat/health?v"
*   Trying 10.90.3.38:80...
* Connected to test1-es-test.apps.kcp2-arm.iefcu.cn (10.90.3.38) port 80 (#0)
* Server auth using Basic with user 'elastic'
> GET /_cat/health?v HTTP/1.1
> Host: test1-es-test.apps.kcp2-arm.iefcu.cn
> Authorization: Basic ZWxhc3RpYzo5M05JQjQ2cjRoWDdxZWhROWw4OWhEVDI=
> User-Agent: curl/7.74.0
> Accept: */*
>
* Mark bundle as not supporting multiuse
< HTTP/1.1 504 Gateway Time-out
< content-length: 92
< cache-control: no-cache
< content-type: text/html
<
<html><body><h1>504 Gateway Time-out</h1>
The server didn't respond in time.
</body></html>
* Connection #0 to host test1-es-test.apps.kcp2-arm.iefcu.cn left intact
```

页面访问http://test1-es-test.apps.kcp2-arm.iefcu.cn/，有返回
```
{
  "name" : "test1-es-default-0",
  "cluster_name" : "test1",
  "cluster_uuid" : "_na_",
  "version" : {
    "number" : "7.16.3",
    "build_flavor" : "default",
    "build_type" : "docker",
    "build_hash" : "4e6e4eab2297e949ec994e688dad46290d018022",
    "build_date" : "2022-01-06T23:43:02.825887787Z",
    "build_snapshot" : false,
    "lucene_version" : "8.10.1",
    "minimum_wire_compatibility_version" : "6.8.0",
    "minimum_index_compatibility_version" : "6.0.0-beta1"
  },
  "tagline" : "You Know, for Search"
}
```

## 概念

关键字《elasticsearch 入门使用》

https://www.cnblogs.com/sunsky303/p/9438737.html

[Elasticsearch 入门学习](https://zhuanlan.zhihu.com/p/104215274)

Elasticsearch 相对关系型数据库，更适合相关性、高性能全文检索，并且支持 restAPI 调用，而关系型数据库更适合事务性要求较强的场景，以下是两者概念上的类比：

* 关系型数据库	ElasticSearch
* Table	Index
* Row	Document
* Column	Field
* SQL	DSL

https://blog.51cto.com/u_11208931/2772642

* Cluster
  代表一个集群，集群中有多个节点，其中有一个为主节点，这个主节点是可以通过选举产生的，主从节点是对于集群内部来说的。es的一个概念就是去中心化，字面上理解就是无中心节点，这是对于集群外部来说的，因为从外部来看es集群，在逻辑上是个整体，你与任何一个节点的通信和与整个es集群通信是等价的。
* Shards
  代表索引分片，es可以把一个完整的索引分成多个分片，这样的好处是可以把一个大的索引拆分成多个，分布到不同的节点上。构成分布式搜索。分片的数量只能在索引创建前指定，并且索引创建后不能更改。
* replicas
  代表索引副本，es可以设置多个索引的副本，副本的作用一是提高系统的容错性，当某个节点某个分片损坏或丢失时可以从副本中恢复。二是提高es的查询效率，es会自动对搜索请求进行负载均衡。
* Recovery
  代表数据恢复或叫数据重新分布，es在有节点加入或退出时会根据机器的负载对索引分片进行重新分配，挂掉的节点重新启动时也会进行数据恢复。



## 基本使用

```
GET _cluster/health: 查看集群的健康状态
GET {index_name}: 查看对应索引的状态
GET {index_name}/_count：查看索引的文档总数

1. 查看集群的健康状况(很多种类状态数据)
http://localhost:9200/_cat
```

查看集群健康信息
```
curl -XGET "localhost:9200/_cat/heath?v"
# 使用密码访问
curl -v -u "elastic:$PASSWORD" -k "http://es-test-es-test.apps.kcp1-arm.iefcu.cn/_cat/health?v"

curl -v -u "elastic:$PASSWORD" -k "http://test1-es-test.apps.kcp2-arm.iefcu.cn/_cat/health?v"

epoch      timestamp cluster status node.total node.data shards pri relo init unassign pending_tasks max_task_wait_time active_shards_percent
1661240793 07:46:33  test1   green           3         3      6   3    0    0        0             0                  -                100.0%
```

返回结果的主要字段意义：

* cluster：集群名，是在ES的配置文件中配置的cluster.name的值。
* status：集群状态。集群共有green、yellow或red中的三种状态。green代表一切正常（集群功能齐全），yellow意味着所有的数据都是可用的，但是某些复制没有被分配（集群功能齐全），red则代表因为某些原因，某些数据不可用。如果是red状态，则要引起高度注意，数据很有可能已经丢失。
* node.total：集群中的节点数。
* node.data：集群中的数据节点数。
* shards：集群中总的分片数量。
* pri：主分片数量，英文全称为private。
* relo：复制分片总数。
* unassign：未指定的分片数量，是应有分片数和现有的分片数的差值（包括主分片和复制分片）。


查看集群中的节点信息。
```
curl -XGET "localhost:9200/_cat/nodes?v"
```

（3）查看集群中的索引信息。
```
curl -XGET "localhost:9200/_cat/indices?v"
curl -v -u "elastic:$PASSWORD" -k "http://es-test-es-test.apps.kcp1-arm.iefcu.cn/_cat/indices?v"
curl -v -u "elastic:$PASSWORD" -k "http://test1-es-test.apps.kcp2-arm.iefcu.cn/_cat/indices?v"

health status index uuid                   pri rep docs.count docs.deleted store.size pri.store.size
green  open   alert enfb7aHnTQu9avoJG7fUzQ   1   1    1267000            0    119.4mb         59.7mb

字段详情查看help
curl -v -u "elastic:$PASSWORD" -k "http://test1-es-test.apps.kcp2-arm.iefcu.cn/_cat/indices?help"
```

解析还可以参考官方文档 https://www.elastic.co/guide/en/elasticsearch/reference/current/cat.html
* health                            current health status
* status                            open/close status
* index                             index name
* uuid                              index uuid
* pri                               number of primary shards
* rep                               number of replica shards
* docs.count                        available docs
* docs.deleted                      deleted docs
* store.size                        store size of primaries & replicas
* pri.store.size                    store size of primaries


## 集群健康

https://www.elastic.co/guide/cn/elasticsearch/guide/current/_cluster_health.html

* green
所有的主分片和副本分片都已分配。你的集群是 100% 可用的。
* yellow
所有的主分片已经分片了，但至少还有一个副本是缺失的。不会有数据丢失，所以搜索结果依然是完整的。不过，你的高可用性在某种程度上被弱化。如果 更多的 分片消失，你就会丢数据了。把 yellow 想象成一个需要及时调查的警告。
* red
至少一个主分片（以及它的全部副本）都在缺失中。这意味着你在缺少数据：搜索只能返回部分数据，而分配到这个分片上的写入请求会返回一个异常。

问题:
* 如何查看主分片, 副分片?

[谁再问elasticsearch集群Red怎么办？把这篇笔记给他](https://segmentfault.com/a/1190000021520174)

从上图可知，集群red是由于有主分片不可用，这种情况一般是由于节点宕机

一、遇到集群Red时，我们可以从如下方法排查：

* 集群层面：/_cluster/health。
* 索引层面：/_cluster/health?pretty&level=indices。
* 分片层面：/_cluster/health?pretty&level=shards。
* 看恢复情况：/_recovery?pretty。
