# k8s cni学习

带着问题去学习
- pod的ip地址可以固定吗? 可以给外网直接访问的固定地址吗?
  问题: pod名称可能会变化，ip地址怎么绑定, stateful的pod还可以固定一下

- IPAM服务需要保证为Pod分配唯一的IP，K8s会为每个节点分配PodCIDR，只需要保证节点上所有Pod IP不冲突即可。
  那么怎么配置合适的ip地址?

- underlay等插件验证试试效果如何?(依赖底层二层环境?)
  通常来说，CNI 插件可以分为三种：Overlay、路由及 Underlay。

- cni插件不以pod运行可以么?

## cni概念

关键字《k8s cni》《k8s cni 开发》

https://www.kubernetes.org.cn/6908.html
[从零开始入门 K8s：理解 CNI 和 CNI 插件](https://www.infoq.cn/article/6mdfwwghzadihiq9ldst)

概念:
全称是 Container Network Interface，即容器网络的 API 接口。 

常见的 CNI 插件包括 Calico、flannel、Terway、Weave Net 以及 Contiv。

通常来说，CNI 插件可以分为三种：Overlay、路由及 Underlay。

- Overlay 模式的典型特征是容器独立于主机的 IP 段，这个 IP 段进行跨主机网络通信时是通过在主机之间创建隧道的方式，将整个容器网段的包全都封装成底层的物理网络中主机之间的包。该方式的好处在于它不依赖于底层网络；
- 路由模式中主机和容器也分属不同的网段，它与 Overlay 模式的主要区别在于它的跨主机通信是通过路由打通，无需在不同主机之间做一个隧道封包。但路由打通就需要部分依赖于底层网络，比如说要求底层网络有二层可达的一个能力；
- Underlay 模式中容器和宿主机位于同一层网络，两者拥有相同的地位。容器之间网络的打通主要依靠于底层网络。因此该模式是强依赖于底层能力的。


[kubernates指南 - CNI](https://kubernetes.feisky.xyz/extension/network/cni)

[jimmysong.io - 容器网络接口（CNI）](https://jimmysong.io/kubernetes-handbook/concepts/cni.html)
=> 一点简单的概念

## cni开发

[Kubernetes网络篇——自己动手写CNI插件(上)](https://morningspace.github.io/tech/k8s-net-cni-coding-shell/)
=> 使用rkt, 是什么东西

有没有想过自己写一个CNI插件呢？也许大多数时候我们都没必要自己开发插件。不过，出于学习的目的，或者为了排查错误，也许你会读到别人写的插件。这个时候，如果事先对CNI插件编程有一定了解，那就会事半功倍。

我们用rkt作为容器运行时环境来验证我们logger插件。关于在rkt里运行CNI插件的详细情况，大家可以参考Kubernetes网络篇——将CNI用于容一文的后半部分。

[手写一个Kubernetes CNI网络插件](https://juejin.cn/post/7083372512452542478)
=> 使用kind创建模拟k8s集群, TODO: 待尝试

Kubernetes与CNI的交互逻辑如下：

不同于CRI、CSI通过rpc通信，CNI是通过二进制接口调用的，通过环境变量和标准输入传递具体网络配置，下图为Flannel CNI插件的工作流程，通过链式调用CNI插件实现对Pod的IP分配、网络配置：

CNI官方已经提供了工具包，我们只需要实现cmdAdd, cmdCheck, cmdDel接口即可实现一个CNI插件。

[使用 Go 从零开始实现 CNI](https://morven.life/posts/create-your-own-cni-with-golang/)
=> TODO: 待尝试
