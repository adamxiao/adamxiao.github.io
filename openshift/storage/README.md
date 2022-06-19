# 存储概述

未分类细化的资料

* StorageClass
* pvc

## 概念

https://boilingfrog.github.io/2021/07/01/k8s中的PV和PVC理解

pod -- pvc (bind) --- pv
       pvc --- StorageClass(provisioner) --- pv

[名词解释：PV/PVC/StorageClass](https://www.kubernetes.org.cn/pvpvcstorageclass)


## hostpath provision

关键字《provisioner: kubernetes.io/host-path》

https://github.com/torchbox/k8s-hostpath-provisioner
https://github.com/kubevirt/hostpath-provisioner

https://artifacthub.io/packages/helm/rimusz/hostpath-provisioner
$ helm upgrade --install hostpath-provisioner -n hostpath-provisioner rimusz/hostpath-provisioner

https://platform9.com/blog/tutorial-dynamic-provisioning-of-persistent-storage-in-kubernetes-with-minikube/
```
provisioner: k8s.io/minikube-hostpath
```

https://docs.openshift.com/container-platform/4.7/virt/virtual_machines/virtual_disks/virt-configuring-local-storage-for-vms.html
provisioner: kubevirt.io/hostpath-provisioner

https://github.com/wenwenxiong/book/blob/master/k8s/k8s-hostpath存储使用.md
provisioner: nailgun.name/hostpath

https://blog.csdn.net/wenwenxiong/article/details/79094616
provisioner: nailgun.name/hostpath



## local volume

* [超长干货讲透你曾经分不清的 3 种 Kubernetes 存储](https://www.infoq.cn/article/fg2wp8yi8mldj5u7gign)

emptyDir、hostPath 都是 Kubernetes 很早就实现和支持了的技术，local volume 方式则是从 k8s v1.7 才刚刚发布的 alpha 版本，目前在 k8s v1.10 中发布了 local volume 的 beta 版本，部分功能在早期版本中并不支持。

有时我们需要搭建一个单节点的 k8s 测试环境，就利用到 hostPath 作为后端的存储卷，模拟真实环境提供 PV、StorageClass 和 PVC 的管理功能支持。
```
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  namespace: kube-system
  name: standard
  annotations:
    storageclass.beta.kubernetes.io/is-default-class: "true"
  labels:
    addonmanager.kubernetes.io/mode: Reconcile
provisioner: kubernetes.io/host-path
```
该场景仅能用于单节点的 k8s 测试环境中

## 其他存储介绍

[Rancher入门到精通-2.0 K8S 六种存储解决方案的性能比较测试 原创](https://blog.51cto.com/waxyz/5336846)

本文的目的就是寻找在 Kubernetes 中最常用的存储解决方案，并进行基本性能比较。本次测试使用以下 存储后端对 Azure AKS 执行所有测试：

* Azure 原生 StorageClass：Azure 高级版；
* 将 AWS cloud volume 映射到实例中：Azure hostPath，附带 Azure 托管磁盘；
* 由 Rook 管理的 Ceph；
* 由 Heketi 管理的 Gluster；
* 带有 cStor 后端的 OpenEBS；
* Portworx。

## 参考资料

