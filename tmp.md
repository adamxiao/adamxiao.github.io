# 临时计划

同网段pc scp到eip服务器，结果却到了gw router上！！！！

## openshift 备份恢复

关键字《openshift 备份恢复》
OpenShift 4 - 备份和恢复 Etcd 数据库
https://blog.csdn.net/weixin_43902588/article/details/124822319

https://www.joyk.com/dig/detail/1587517265859351
你的 Kubernetes/Openshift 集群备份了吗

什么是 velero
看官网有一个特别简单直接的介绍， 它可以干嘛呢， 三点：

备份你的集群并在出事的时候可以恢复
迁移集群到其他集群
复制你的生产集群到开发或者测试环境

https://blog.csdn.net/weixin_43902588/article/details/122349684
OpenShift 4 - 容器应用备份和恢复
=> 使用的是velero

OpenShift 4 - 备份和恢复 Etcd 数据库
https://blog.csdn.net/weixin_43902588/article/details/124822319
https://www.codeleading.com/article/26876302164/
=> 在4.10上验证过
TODO: 简单，可以验证尝试一下

https://www.jianshu.com/p/dc7b3ec6abd6
Openshift集群全环境备份
=> 复杂
在Openshift平台，我们可以对集群的完整状态备份到外部存储。集群全环境包括：
* 集群数据文件
* etcd数据库
* Openshift对象配置
* 私有镜像仓库存储
* 持久化卷

#### project_exports.sh导出项目yaml配置

=> 也就勉强能用一点点吧, 感觉还不如从原始的方法进行部署。。。

[OpenShift 项目的备份和恢复实验](https://www.cnblogs.com/ericnie/p/10500572.html)
本测试记录从openshift 3.6环境中导出项目，然后在将项目环境恢复到Openshift 3.11中所需要的步骤 从而指导导入导出的升级过程。


关键字《OpenShift 项目的备份和恢复》
=> project_export.sh 不能用! 经过修改, 去除--export参数，就可以导出数据了
https://github.com/openshift/openshift-ansible-contrib/blob/master/reference-architecture/day2ops/scripts/project_export.sh
=> 原理就是oc get -o=json, 导出配置, 不是很好用, 导出了多余的东西, 例如service-ca configmap

需要注意的地方包括:
* 用户不会导出，但在openshift的权限信息会保存。
* 节点的Label不会导出
* 导入导出过程需要rollout。
* 用glusterfs的时候，每个project的gluster-endpoint资源没有保存下来，估计和gluster-service没有关联相关
* 因为pv不是属于项目资源而属于整个集群资源，导入项目前，先建立pv
* 遇到pod无法启动很多时候和mount存储有关系

#### etcd数据备份和恢复

适合当前集群的备份和恢复, 具体的恢复还是不太明白!

登录master1节点, 执行etcd数据库备份操作, 将etcd数据库备份到目标目录中
```
mkdir -p /home/core/assets/backup
/usr/local/bin/cluster-backup.sh /home/core/assets/backup

# 例如备份单master节点的数据
[root@master1 core]# /usr/local/bin/cluster-backup.sh /home/core/assets/backup
found latest kube-apiserver: /etc/kubernetes/static-pod-resources/kube-apiserver-pod-16
found latest kube-controller-manager: /etc/kubernetes/static-pod-resources/kube-controller-manager-pod-6
found latest kube-scheduler: /etc/kubernetes/static-pod-resources/kube-scheduler-pod-7
found latest etcd: /etc/kubernetes/static-pod-resources/etcd-pod-2
d2af784a8998ee7be000c65cc7dc56c2099c5a73b3b6adbd2326a8face4efc25
etcdctl version: 3.4.14
API version: 3.4
{"level":"info","ts":1655434169.0621967,"caller":"snapshot/v3_snapshot.go:119","msg":"created temporary db file","path":"/home/core/assets/backup/snapshot_2022-06-17_024925.db.part"}
{"level":"info","ts":"2022-06-17T02:49:29.062Z","caller":"clientv3/maintenance.go:200","msg":"opened snapshot stream; downloading"}
{"level":"info","ts":1655434169.0624921,"caller":"snapshot/v3_snapshot.go:127","msg":"fetching snapshot","endpoint":"https://192.168.100.1:2379"}
{"level":"info","ts":"2022-06-17T02:49:31.905Z","caller":"clientv3/maintenance.go:208","msg":"completed snapshot read; closing"}
{"level":"info","ts":1655434172.1335819,"caller":"snapshot/v3_snapshot.go:142","msg":"fetched snapshot","endpoint":"https://192.168.100.1:2379","size":"104 MB","took":3.071241643}
{"level":"info","ts":1655434172.1337464,"caller":"snapshot/v3_snapshot.go:152","msg":"saved","path":"/home/core/assets/backup/snapshot_2022-06-17_024925.db"}
Snapshot saved at /home/core/assets/backup/snapshot_2022-06-17_024925.db
{"hash":668661593,"revision":5414790,"totalKey":8232,"totalSize":103858176}
snapshot db and kube resources are successfully saved to /home/core/assets/backup

[root@master1 core]# cd /home/core/assets/backup
[root@master1 backup]# ls
snapshot_2022-06-17_024925.db  static_kuberesources_2022-06-17_024925.tar.gz

# 三个节点的备份, 主要在于etcd的区别吧?
[root@master1 etcd-all-certs]# pwd
/var/home/core/assets/backup/static-pod-resources/etcd-pod-3/secrets/etcd-all-certs
[root@master1 etcd-all-certs]# ls
etcd-peer-master1.kcp2-arm.iefcu.cn.crt  etcd-peer-master3.kcp2-arm.iefcu.cn.crt     etcd-serving-master2.kcp2-arm.iefcu.cn.crt  etcd-serving-metrics-master1.kcp2-arm.iefcu.cn.crt  etcd-serving-metrics-master3.kcp2-arm.iefcu.cn.crt
etcd-peer-master1.kcp2-arm.iefcu.cn.key  etcd-peer-master3.kcp2-arm.iefcu.cn.key     etcd-serving-master2.kcp2-arm.iefcu.cn.key  etcd-serving-metrics-master1.kcp2-arm.iefcu.cn.key  etcd-serving-metrics-master3.kcp2-arm.iefcu.cn.key
etcd-peer-master2.kcp2-arm.iefcu.cn.crt  etcd-serving-master1.kcp2-arm.iefcu.cn.crt  etcd-serving-master3.kcp2-arm.iefcu.cn.crt  etcd-serving-metrics-master2.kcp2-arm.iefcu.cn.crt
etcd-peer-master2.kcp2-arm.iefcu.cn.key  etcd-serving-master1.kcp2-arm.iefcu.cn.key  etcd-serving-master3.kcp2-arm.iefcu.cn.key  etcd-serving-metrics-master2.kcp2-arm.iefcu.cn.key
```

恢复 Etcd 数据库

1. 在 Master-1 和 Master-2 节点上分别执行以下命令，先将现有 Kubernetes API 服务器 pod 文件和 etcd pod 文件从 kubelet 清单目录中移出。然后确认直到已经没有 etcd 和 kube-apiserver 的 pod 运行。
```
sudo mv /etc/kubernetes/manifests/etcd-pod.yaml /tmp
sudo mv /etc/kubernetes/manifests/kube-apiserver-pod.yaml /tmp
sudo crictl ps | grep etcd | grep -v operator
sudo crictl ps | grep kube-apiserver | grep -v operator
```

2. 在 Master-1 和 Master-2 节点上分别执行以下命令，将 etcd 数据目录移走。
```
sudo mv /var/lib/etcd/ /tmp
```

3. 在 MASTER-0 节点上执行命令恢复 Etcd 数据库。
```
sudo -E /usr/local/bin/cluster-restore.sh /home/core/backup
```

4. 在所有 Master 节点执行命令，重启 kubelet 服务。在确认服务重新运行后 Etcd 数据库即恢复完。
```
sudo systemctl restart kubelet.service
sudo systemctl status kubelet.service
```

5. 在所有 Master 节点执行命令，确认 etcd pod 正常运行。
```
sudo crictl ps | grep etcd | grep -v operator
oc get pods -n openshift-etcd | grep -v etcd-quorum-guard | grep etcd
```

最后发现服务正常，但是web console白屏无法进去(网络请求有502错误)，查看pod日志显示连接错误：
2022/06/17 06:14:52 http: proxy error: dial tcp 172.30.0.1:443: connect: connection refused
E0617 06:40:47.707707       1 auth.go:231] error contacting auth provider (retrying in 10s): Get "https://kubernetes.default.svc/.well-known/oauth-authorization-server": dial tcp 172.30.0.1:443: connect: connection refused
=> 是不是联系不上apiserver了?

https://access.redhat.com/solutions/5444221
After Using the Recovery API Server, Pods are Unable to Reach 172.30.0.1:443
=> 跟这个问题一模一样, 而且问题也还没有解决！也没权限看

没有查到什么资料，看看所有的pod，是否有异常的! 都是跟172.30.0.1:443有关！！
[core@master1 ~]$ oc -n openshift-apiserver-operator get pods
NAME                                            READY   STATUS             RESTARTS          AGE
openshift-apiserver-operator-6c9d95d44d-h85qw   0/1     CrashLoopBackOff   298 (2m10s ago)   12d

=> 发现只有master1的apiserver运行正常, 丫的发现只有master1有etcd和apiserver的静态pod配置文件！！！
oc命令能够正常使用。。。 oc delete 也能用。。。 => 但是整个系统暂不知道怎么恢复

再次尝试, 遇到错误, etcd还是没起来, etcd operator错误日志如下
```
I0618 08:30:30.640858       1 base_controller.go:110] Starting #1 worker of ConfigObserver controller ...
E0618 08:30:30.727538       1 base_controller.go:272] FSyncController reconciliation failed: client query returned empty vector
I0618 08:30:31.538790       1 request.go:665] Waited for 1.498225057s due to client-side throttling, not priority and fairness, request: GET:https://172.30.0.1:443/api/v1/namespaces/kube-system/configmaps/cluster-config-v1
I0618 08:30:31.558694       1 quorumguardcontroller.go:186] etcd-quorum-guard was modified
I0618 08:30:31.558886       1 event.go:282] Event(v1.ObjectReference{Kind:"Deployment", Namespace:"openshift-etcd-operator", Name:"etcd-operator", UID:"f5d36503-a7f1-4202-a58e-78e25320c0d7", APIVersion:"apps/v1", ResourceVersion:"", FieldPath:""}): type: 'Normal' reason: 'ModifiedQuorumGuardDeployment' etcd-quorum-guard was modified
E0618 08:30:32.019055       1 base_controller.go:272] FSyncController reconciliation failed: client query returned empty vector
I0618 08:30:32.738447       1 request.go:665] Waited for 1.396265937s due to client-side throttling, not priority and fairness, request: GET:https://172.30.0.1:443/api/v1/namespaces/openshift-etcd/pods/etcd-master2.kcp2-arm.iefcu.cn
E0618 08:30:34.589319       1 base_controller.go:272] FSyncController reconciliation failed: client query returned empty vector
E0618 08:30:39.719966       1 base_controller.go:272] FSyncController reconciliation failed: client query returned empty vector
```

=> 单节点恢复了, 但是确实不容易
强制删除etcd pod, 还重启了kubelet
但是居然没有恢复出我的项目？？？但是namespaces中有 => 说明openshift-apiserver的数据还是丢失了呢

## 其他

* docker安装，居然使用二进制安装，起不来，使用rpm安装可以
* 存在dhcp服务器，结果bootstrap有问题！关掉了!
* ip冲突问题有问题, 换私有ip装, 装好再处理

up{namespace="openshift-ingress"}
=> 可以查到数据

名称
container
endpoint
instance
job
namespace
pod
prometheus
service
值
up	router	metrics	10.90.3.33:1936	router-internal-default	openshift-ingress	router-default-66ddd5cfb-6wzt2	openshift-monitoring/k8s	router-internal-default	1


https://blog.51cto.com/u_14065119/3698192
可用性监控
除了监控主机的性能参数外，我们还需要关注实例的可用性情况，比如是否关机、exporter是否正常运行等。在exporter返回的指标，有一个up指标，可用来实现这类监控需求。

up{job="node-exporter"}



## TOOLS
https://www.youtube.com/watch?v=2OHrTQVlRMg&ab_channel=TechCraft
======

* exa - https://github.com/ogham/exa
  better ls
* bat - https://github.com/sharkdp/bat
  better cat
* ripgrep - https://github.com/BurntSushi/ripgrep
  学一下ag的区别: 正则匹配, 搜索指定类型的文件
* fzf - https://github.com/junegunn/fzf
* zoxide - https://github.com/ajeetdsouza/zoxide
  smarter cd command
* entr - https://github.com/eradman/entr
  A utility for running arbitrary commands when files change. 
* mc - https://midnight-commander.org/
  visual file manager

vpc网络虚拟化

* 分析ZStack实现方法
* 搭建最新openstack环境，分析openstack实现

#### 利用标签获取应用cpu监控指标

思路:
* 筛选出不在指定命名规则里面的项目
refer https://prometheus.io/docs/prometheus/latest/querying/basics/
```
sum(container_memory_working_set_bytes{cluster="", namespace!~"openshift.*", container!="", image!=""}) by (namespace)
```
* 根据label筛选
  没有label上报, 无法筛选
* 其他?

通过如下命令可以查询出openshift相关项目下的内存使用量?
```
sum(container_memory_working_set_bytes{cluster="", namespace=~"openshift.*", container!="", image!=""}) by (namespace)
```

然后通过页面查询 container_memory_working_set_bytes 的上报数据字段
* container
* id
* instance
* name
k8s_POD_tomcat-58c777d49f-6n5w5_adam-test_06324d9b-7782-45ea-b93b-4cf1264cc09a_0
* namespace
* node
master1
* pod
tomcat-58c777d49f-6n5w5
* ...等字段

=> 发现没有label字段, 就不可能通过label字段来过滤

可以手动查询一下?(是kubelet上报的监控数据)
curl -k -H "Authorization: Bearer sha256~TZy6BQgoMYssf2OY7Zm2pNcnzS_jbqSNNvUkJrHVENk" https://localhost:10250/metrics/cadvisor
=> 没有权限。。。

#### 自定义告警规则添加上了，但是在promethues里没看到

在内置的promethues里面没有看到
Alerts
Rules

在新prome, thanos pod中可以看到配置生效了!
* /etc/prometheus/rules/prometheus-user-workload-rulefiles-0
* /etc/thanos/rules/thanos-ruler-user-workload-rulefiles-0

refer https://access.redhat.com/documentation/zh-cn/openshift_container_platform/4.9/html-single/monitoring/index
```bash
$ oc port-forward -n openshift-user-workload-monitoring pod/prometheus-user-workload-0 9090
```

可以在 Web 浏览器中打开 http://localhost:9090/targets，并在 Prometheus UI 中直接查看项目的目标状态。检查与目标相关的错误消息。
=> 可以看这个promethues的Rules等信息

#### 监控api耗时

* 离线部署traefix-mesh
* 配置dns转发
* 应用调用使用新域名(service)
