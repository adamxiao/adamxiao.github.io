# 临时计划

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

https://www.oschina.net/comment/blog/3619846
OpenShift 项目的备份和恢复实验分享
本测试记录从openshift 3.6环境中导出项目，然后在将项目环境恢复到Openshift 3.11中所需要的步骤 从而指导导入导出的升级过程。
=> 内容为空, 只有标题

关键字《OpenShift 项目的备份和恢复》
=> project_export.sh 不能用!
https://github.com/openshift/openshift-ansible-contrib/blob/master/reference-architecture/day2ops/scripts/project_export.sh


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
