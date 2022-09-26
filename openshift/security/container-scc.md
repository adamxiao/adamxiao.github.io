# 容器scc策略

## 概念

安全性上下文约束

您可以使用安全性上下文约束 (SCC) 定义 Pod 运行必须满足的一组条件，以便其能被系统接受。

可由 SCC 管理的一些方面包括：

* 运行特权容器
* 容器可请求添加的功能
* 将主机目录用作卷。
* 容器的 SELinux 上下文。
* 容器用户 ID。

## 使用

将自定义 SCC 添加到 ServiceAccount：
```
$ oc adm policy add-scc-to-user restricted-seccomp -z default
```

容器云平台提供了几个默认的scc
```
oc get scc

NAME                              PRIV    CAPS         SELINUX     RUNASUSER          FSGROUP     SUPGROUP    PRIORITY     READONLYROOTFS   VOLUMES
anyuid                            false   <no value>   MustRunAs   RunAsAny           RunAsAny    RunAsAny    10           false            ["projected","secret"]
hostaccess                        false   <no value>   MustRunAs   MustRunAsRange     MustRunAs   RunAsAny    <no value>   false            ["hostPath","projected","secret"]
hostmount-anyuid                  false   <no value>   MustRunAs   RunAsAny           RunAsAny    RunAsAny    <no value>   false            ["hostPath","nfs","projected","secret"]
hostnetwork                       false   <no value>   MustRunAs   MustRunAsRange     MustRunAs   MustRunAs   <no value>   false            ["projected","secret"]
machine-api-termination-handler   false   <no value>   MustRunAs   RunAsAny           MustRunAs   MustRunAs   <no value>   false            ["hostPath"]
node-exporter                     true    <no value>   RunAsAny    RunAsAny           RunAsAny    RunAsAny    <no value>   false            ["*"]
nonroot                           false   <no value>   MustRunAs   MustRunAsNonRoot   RunAsAny    RunAsAny    <no value>   false            ["projected","secret"]
privileged                        true    ["*"]        RunAsAny    RunAsAny           RunAsAny    RunAsAny    <no value>   false            ["*"]
restricted                        false   <no value>   MustRunAs   MustRunAsRange     MustRunAs   RunAsAny    <no value>   false            ["projected","secret"]
```

一般来说, privileged是最大权限, 基本可以用, 否则用anyuid也行
```
oc adm policy add-scc-to-user privileged -n podman-build -z default
```

## scc深入了解(旧的资料)

[Review SCC(Security Context Constraints) based on RBAC in OpenShift v4](https://daein.medium.com/review-scc-security-context-constraints-based-on-rbac-on-openshift-49007ff26317)

[(好)Linux Capabilities in OpenShift](https://cloud.redhat.com/blog/linux-capabilities-in-openshift)

![](https://cloud.redhat.com/hubfs/Openshift%20API%20Call.png)

![](https://cloud.redhat.com/hubfs/SCC_Admission_Simplified.png)

[openshift踩坑日记](https://developer.aliyun.com/article/787121)

而创建的pod资源默认归属于**Restricted**策略。管理员用户也可以创建自己的 scc 并赋予自己的 serviceaccount:

根据错误提示，找到了问题点在于 scc 。官方的介绍如下：

OpenShift 的 安全環境限制 （Security Context Constraints）類似於 RBAC 資源控制用戶訪問的方式，管理員可以使用安全環境限制（Security Context Constraints, SCC）來控制Pod 的權限。 您可以使用 SCC 定義 Pod 運行時必須特定條件才能被系統接受。

=> traefik-ee 建立了自己的一个scc，并且绑定到sa上?


[Tutorial: Use SCCs to restrict and empower OpenShift workloads](https://developer.ibm.com/learningpaths/secure-context-constraints-openshift/scc-tutorial/)
scc tutorial


查看my-scc项目的annotations，其中“sa.scc”相关参数是当SCC策略非RunAsAny时提供默认值。

```bash
oc get project traefik-mesh -o json | jq .metadata.annotations
oc get project default -o json | jq .metadata.annotations
```

scc可以和用户，组，服务帐号进行绑定!


查询scc privileged可以被谁使用, 参考[OpenShift 4 - 安全上下文](https://blog.csdn.net/weixin_43902588/article/details/103374097)
```bash
oc adm policy who-can use scc privileged
```

![](../imgs/2022-03-26-14-45-45.png)

