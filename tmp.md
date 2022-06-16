# 临时计划

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
