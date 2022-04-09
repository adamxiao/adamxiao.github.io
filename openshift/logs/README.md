# 日志收集监控调研

#### es operator源码编译安装

首先，使用docker insepct查看到es operator和es镜像的源码，下载下来

然后修改一下dockerfile,开始编译

#### arm64下安装

安装cluster-logging operator失败

0s          Warning   UnsupportedOperatorGroup   clusterserviceversion/cluster-logging.5.3.4-13   AllNamespaces InstallModeType not supported, cannot configure to watch all namespaces

0s          Warning   TooManyOperatorGroups      clusterserviceversion/cluster-logging.5.3.4-13   csv created in namespace with multiple operatorgroups, can't pick one automatically

原来是自己的operatorgroup配置出错了，没有配置targetNamespaces，或者spec覆盖了！！！
```yaml
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: cluster-logging
  namespace: openshift-logging
spec:
  targetNamespaces:
  - openshift-logging
spec: {}
```

官方cli安装文档也是一样的，不明白怎么allnamespaces了！！！
https://docs.openshift.com/container-platform/4.9/logging/cluster-logging-deploying.html


发现olm报错

I0406 06:12:24.850288       1 event.go:282] Event(v1.ObjectReference{Kind:"Namespace", Namespace:"", Name:"openshift-logging", UID:"b7f4ce26-1a0a-4841-bf76-7ed2d2d0a7dd", APIVersion:"v1", ResourceVersion:"1054514", FieldPath:""}): type: 'Warning' reason: 'ResolutionFailed' constraints not satisfiable: no operators found from catalog adam" in namespace openshift-marketplace referenced by subscription cluster-logging, subscription cluster-logging exists

=> 原来是catalog adam名称输入错误，弄成adam"了


#### xxx

关键字《EFK原理》

EFK 架构，参考： https://ithelp.ithome.com.tw/articles/10223004
![](2022-04-01-15-55-22.png)

[一文彻底搞定 EFK 日志收集系统](https://cloud.tencent.com/developer/article/1645047)


[理解OpenShift（6）：集中式日志处理](https://www.cnblogs.com/sammyliu/p/10141242.html)

![](2022-04-01-15-58-10.png)



全新搭建的openshift x86 4.8.9环境，安装efk

遇到问题没有gp2这个存储类
```
0s          Warning   ProvisioningFailed     persistentvolumeclaim/elasticsearch-elasticsearch-cdm-6wri3xgj-1   storageclass.storage.k8s.io "gp2" not found
0s          Warning   ProvisioningFailed     persistentvolumeclaim/elasticsearch-elasticsearch-cdm-6wri3xgj-2   storageclass.storage.k8s.io "gp2" not found
0s          Warning   ProvisioningFailed     persistentvolumeclaim/elasticsearch-elasticsearch-cdm-6wri3xgj-3   storageclass.storage.k8s.io "gp2" not found
0s          Warning   FailedScheduling       pod/elasticsearch-cdm-6wri3xgj-2-654f4dfd57-fsn5l                  0/1 nodes are available: 1 pod has unbound immediate PersistentVolumeClaims.
0s          Warning   FailedScheduling       pod/elasticsearch-cdm-6wri3xgj-1-55bd577d9b-c2pgn                  0/1 nodes are available: 1 pod has unbound immediate PersistentVolumeClaims.
0s          Warning   FailedScheduling       pod/elasticsearch-cdm-6wri3xgj-3-54f47c94bb-k968r                  0/1 nodes are available: 1 pod has unbound immediate PersistentVolumeClaims.
```

还有这几个pvc要求的容量都是200G，一共需要600G
先配置改为100G*3吧
![](2022-04-01-10-26-33.png)


还有内存限制，暂时需要配置小内存运行。2000M cpu, 1G 内存，限制1G存储
![](2022-04-01-13-45-52.png)

过了一段时间，最终部署成功。
![](2022-04-01-14-53-06.png)

这里新增加了一个日志观察链接
![](2022-04-01-15-01-45.png)


问题：没有fluentd这个pod，怎么回事？

4.2.2. 查看日志记录收集器 Pod
您可以查看 Fluentd 日志记录收集器 Pod 以及它们正在运行的对应节点。Fluentd 日志记录收集器 Pod 仅在 openshift-logging 项目中运行。

最后把master节点的内存cpu加大到32u 64G可以了？但是还是没有fluentd的pods？

最后在kibana上配置出效果了，能够看日志？
主要是要配置索引!!!
![](2022-04-01-16-25-24.png)