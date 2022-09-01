# k8s原理

## controller manager

关键字《controller manager作用》


[(好)解读 kubernetes Controller Manager 工作原理](https://blog.yingchi.io/posts/2020/7/k8s-cm-informer.html)

client-go
Controller Manager 中一个很关键的部分就是 client-go，client-go 在 controller manager 中起到向 controllers 进行事件分发的作用。目前 client-go 已经被单独抽取出来成为一个项目了，除了在 kubernetes 中经常被用到，在 kubernetes 的二次开发过程中会经常用到 client-go，比如可以通过 client-go 开发自定义 controller。

client-go 包中一个非常核心的工具就是 informer，informer 可以让与 kube-apiserver 的交互更加优雅。

informer 主要功能可以概括为两点：
* 资源数据缓存功能，缓解对 kube-apiserver 的访问压力；
* 资源事件分发，触发事先注册好的 ResourceEventHandler；

[Kubernetes核心原理（二）之Controller Manager](https://blog.csdn.net/huwh_/article/details/75675761)

Controller Manager作为集群内部的管理控制中心，负责集群内的Node、Pod副本、服务端点（Endpoint）、命名空间（Namespace）、服务账号（ServiceAccount）、资源定额（ResourceQuota）的管理，当某个Node意外宕机时，Controller Manager会及时发现并执行自动化修复流程，确保集群始终处于预期的工作状态。

每个Controller通过API Server提供的接口实时监控整个集群的每个资源对象的当前状态，当发生各种故障导致系统状态发生变化时，会尝试将系统状态修复到“期望状态”。

2. Replication Controller
为了区分，资源对象Replication Controller简称RC,而本文是指Controller Manager中的Replication Controller，称为副本控制器。副本控制器的作用即保证集群中一个RC所关联的Pod副本数始终保持预设值。

只有当Pod的重启策略是Always的时候（RestartPolicy=Always），副本控制器才会管理该Pod的操作（创建、销毁、重启等）。
RC中的Pod模板就像一个模具，模具制造出来的东西一旦离开模具，它们之间就再没关系了。一旦Pod被创建，无论模板如何变化，也不会影响到已经创建的Pod。
Pod可以通过修改label来脱离RC的管控，该方法可以用于将Pod从集群中迁移，数据修复等调试。
删除一个RC不会影响它所创建的Pod，如果要删除Pod需要将RC的副本数属性设置为0。
不要越过RC创建Pod，因为RC可以实现自动化控制Pod，提高容灾能力。

2.1. Replication Controller的职责
确保集群中有且仅有N个Pod实例，N是RC中定义的Pod副本数量。
通过调整RC中的spec.replicas属性值来实现系统扩容或缩容。
通过改变RC中的Pod模板来实现系统的滚动升级。


#### 日志调试

关键字《controller-manager 日志级别》

通过配置启动参数可以看调试日志
https://cizixs.com/2017/03/27/kubernetes-introduction-controller-manager/
https://blog.csdn.net/weixin_45413603/article/details/107933040
```
# /opt/kubernetes/bin/kube-controller-manager \
    --v=4 \
```

应该可以配置环境变量
```
KUBE_LOG_LEVEL="--v=0"
```

kubelet可以通过systemctl
[Editing kubelet log level verbosity and gathering logs](https://docs.openshift.com/container-platform/4.6/rest_api/editing-kubelet-log-level-verbosity.html)

看能不能配置controller manager operator配置？
https://github.com/openshift/cluster-kube-controller-manager-operator
https://docs.okd.io/latest/rest_api/operator_apis/kubecontrollermanager-operator-openshift-io-v1.html
```
oc edit kubecontrollermanager/cluster
```
把logLevel改为:
* Normal
* Debug
* Trace
* TraceAll

关键字《openshift controller manager log level》
这个问题类似，但是没权限看
[Increasing the loglevels of OpenShift and Kube components in OpenShift 4](https://access.redhat.com/solutions/3909751)


最后查看日志
```
oc -n openshift-kube-controller-manager logs --tail 10 -f kube-controller-manager-master1.kcp2-arm.iefcu.cn
```

#### controller保证副本数量可用性验证

实际测试验证，rc在节点掉线，会保证pod数量为3吗? => 会，但是貌似时间有点长!!!十几分钟?
=> 《深信服PaaS平台KubeManager6.0技术方案建议书》
如果Pod所在的Worker宕机，则会将这个Worker上的所有Pod重新调度到其他节点上。
```
[core@master1 ~]$ oc get pods
NAME                                READY   STATUS        RESTARTS   AGE
nginx-deployment-55976fb44f-ckddx   1/1     Running       7          25d
nginx-deployment-55976fb44f-h5zpq   1/1     Running       0          4m16s
nginx-deployment-55976fb44f-rflz8   1/1     Terminating   7          25d
```


#### etcd坏了一个

```
oc[core@master1 ~]$ oc -n openshift-etcd get pods
NAME                                    READY   STATUS             RESTARTS          AGE
etcd-master1.kcp2-arm.iefcu.cn          4/4     Running            112 (3d20h ago)   72d
etcd-master2.kcp2-arm.iefcu.cn          4/4     Running            53 (3d20h ago)    72d
etcd-master3.kcp2-arm.iefcu.cn          3/4     CrashLoopBackOff   1787 (51s ago)    25s
```

```
{"level":"info","ts":"2022-08-30T03:04:44.183Z","caller":"embed/etcd.go:598","msg":"pprof is enabled","path":"/debug/pprof"}
{"level":"info","ts":"2022-08-30T03:04:44.184Z","caller":"embed/etcd.go:307","msg":"starting an etcd server","etcd-version":"3.5.0","git-sha":"GitNotFound","go-version":"go1.16.6","go-os":"linux","go-arch":"arm64","max-cpu-set":16,"max-cpu-available":16,"member-initialized":true,"name":"master3.kcp2-arm.iefcu.cn","data-dir":"/var/lib/etcd","wal-dir":"","wal-dir-dedicated":"","member-dir":"/var/lib/etcd/member","force-new-cluster":false,"heartbeat-interval":"100ms","election-timeout":"1s","initial-election-tick-advance":true,"snapshot-count":100000,"snapshot-catchup-entries":5000,"initial-advertise-peer-urls":["https://192.168.100.33:2380"],"listen-peer-urls":["https://0.0.0.0:2380"],"advertise-client-urls":["https://192.168.100.33:2379"],"listen-client-urls":["https://0.0.0.0:2379","unixs://192.168.100.33:0"],"listen-metrics-urls":["https://0.0.0.0:9978"],"cors":["*"],"host-whitelist":["*"],"initial-cluster":"","initial-cluster-state":"existing","initial-cluster-token":"","quota-size-bytes":8589934592,"pre-vote":true,"initial-corrupt-check":false,"corrupt-check-time-interval":"0s","auto-compaction-mode":"periodic","auto-compaction-retention":"0s","auto-compaction-interval":"0s","discovery-url":"","discovery-proxy":"","downgrade-check-interval":"5s"}
{"level":"warn","ts":1661828684.1843698,"caller":"fileutil/fileutil.go:57","msg":"check file permission","error":"directory \"/var/lib/etcd\" exist, but the permission is \"drwxr-xr-x\". The recommended permission is \"-rwx------\" to prevent possible unprivileged access to the data"}
panic: freepages: failed to get all reachable pages (page 4517: multiple references)

goroutine 78 [running]:
go.etcd.io/bbolt.(*DB).freepages.func2(0x400004e5a0)
        /remote-source/cachito-gomod-with-deps/deps/gomod/pkg/mod/go.etcd.io/bbolt@v1.3.6/db.go:1056 +0xc4
created by go.etcd.io/bbolt.(*DB).freepages
        /remote-source/cachito-gomod-with-deps/deps/gomod/pkg/mod/go.etcd.io/bbolt@v1.3.6/db.go:1054 +0x134
```

搜索发现还是移除不健康的节点，然后再回复把!
[Replacing an unhealthy etcd member](https://docs.openshift.com/container-platform/4.9/backup_and_restore/control_plane_backup_and_restore/replacing-unhealthy-etcd-member.html)

首先备份etcd数据库, 然后检查unhealthy节点
```
[core@master1 ~]$ oc get etcd -o=jsonpath='{range .items[0].status.conditions[?(@.type=="EtcdMembersAvailable")]}{.message}{"\n"}'
2 of 3 members are available, master3.kcp2-arm.iefcu.cn is unhealthy
```

目前发现etcd运行crash, 所以用如下方法修复
* 停止crash etcd pod
```
mkdir /var/lib/etcd-backup
mv /etc/kubernetes/manifests/etcd-pod.yaml /var/lib/etcd-backup/
# 移动数据到临时目录(最终要删除掉的)
mv /var/lib/etcd/ /tmp
```
* 移除非健康的etcd pod
```
oc -n openshift-etcd rsh etcd-master1.kcp2-arm.iefcu.cn
etcdctl member list -w table
etcdctl member remove 62bcf33650a7170a
# 移除相关secret
oc get secrets -n openshift-etcd | grep master3.kcp2-arm.iefcu.cn
```
* 强制etcd重新部署
```
oc patch etcd cluster -p='{"spec": {"forceRedeploymentReason": "single-master-recovery-'"$( date --rfc-3339=ns )"'"}}' --type=merge 
```
