# kubevirt调研

关键字《kubevirt是什么》

KubeVirt是个Kubernetes的一个插件，使其在原本调度容器之余能够并行调度传统虚拟机。 它通过运用自定义资源定义（以下简称CRD）及其他Kubernetes相关功能来无缝扩展现有的集群，提供一系列可用于管理虚拟机的虚拟化API。

https://juejin.cn/post/7128038442277011493
KubeVirt是Red-Hat开源的，以容器方式运行的虚拟机项目。是基于Kubernetes运行的，具体的来说是基于Kubernetes的CRD（自定义资源）增加虚拟机的运行和管理相关的资源。特别是VM，VMI资源类型。也是说我们通过CRD进行增加关于虚拟机的资源类型，然后通过写YAML的形式来创建虚拟机等一系列的操作。


https://zhuanlan.zhihu.com/p/113568026
KubeVirt 架构
从kubevirt架构看如何创建虚拟机，Kubevirt架构如图所示，由4部分组件组成。从架构图看出kubevirt创建虚拟机的核心就是 创建了一个特殊的pod virt-launcher 其中的子进程包括libvirt和qemu。做过openstack nova项目的朋友应该比较 习惯于一台宿主机中运行一个libvirtd后台进程，kubevirt中采用每个pod中一个libvirt进程是去中心化的模式避免因为 libvirtd 服务异常导致所有的虚拟机无法管理。

https://segmentfault.com/a/1190000041741403
多图
在了解了 Kubevirt 是什么，它的主要架构以及比较关键的资源对象后，我们来看看如何使用 Kubevirt 进行虚拟机管理。这里主要分为**虚拟机创建、存储和网络三个部分**。

https://moelove.info/2023/09/03/KubeVirt-探秘一些核心问题解答/#kubevirt-有哪些用例
OKD用了KubeVirt?

kubevirt在360的探索之路（k8s接管虚拟化）
https://www.cnblogs.com/qinlulu/p/14671435.html
技术选型
有了以上想法以后，就开始调研，发现业界在从openstack转型k8s的过程中涌现了这么一部分比较好的项目，例如，kubevirt，virtlet，rancher/vm等，但是社区活跃度最高，设计最好的还是kubevirt。
