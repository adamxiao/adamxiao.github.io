# haproxy容器选择节点运行

指定haproxy只到一些固定的基础设施节点上运行，并修改haproxy实例数量

etcd 的api文档

https://docs.openshift.com/container-platform/4.6/rest_api/operator_apis/etcd-operator-openshift-io-v1.html

## TODO

```bash
oc label node <node-name> node-role.kubernetes.io/infra=

oc label node master1.kcp4-arm.iefcu.cn node-role.kubernetes.io/infra=
```

## 之前的笔记


TODO:
haproxy指定容器运行。
如何在Openshift中让Router Pod独占Router节点
https://www.jianshu.com/p/9fc2f34966ce

关键字《ingress.config.openshift.io/cluster 修改》
https://access.redhat.com/documentation/zh-cn/openshift_container_platform/4.4/html/networking/nw-ingress-controller-configuration-parameters_configuring-ingress

nodePlacement 启用对 Ingress 控制器调度的明确控制。
```yaml
nodePlacement:
 nodeSelector:
   matchLabels:
     beta.kubernetes.io/os: linux
 tolerations:
 - effect: NoSchedule
   operator: Exists
```

Openshift 4 infra node setup best practices
https://chowdera.com/2021/04/20210416155434157y.html


## 参考资料

* [Openshift 4 infra node setup best practices](https://chowdera.com/2021/04/20210416155434157y.html)
* [INGRESS 控制器配置参数](https://access.redhat.com/documentation/zh-cn/openshift_container_platform/4.4/html/networking/nw-ingress-controller-configuration-parameters_configuring-ingress)
