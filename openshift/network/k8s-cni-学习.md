# k8s cni学习

带着问题去学习
- pod的ip地址可以固定吗? 可以给外网直接访问的固定地址吗?
  问题: pod名称可能会变化，ip地址怎么绑定, stateful的pod还可以固定一下

- IPAM服务需要保证为Pod分配唯一的IP，K8s会为每个节点分配PodCIDR，只需要保证节点上所有Pod IP不冲突即可。
  那么怎么配置合适的ip地址?

- underlay等插件验证试试效果如何?(依赖底层二层环境?)
  通常来说，CNI 插件可以分为三种：Overlay、路由及 Underlay。

- cni插件不以pod运行可以么?

TODO:
- flannel hostgw模式是什么? 验证使用?
  [从零开始入门 K8s | 理解 CNI 和 CNI 插件](https://www.cnblogs.com/alisystemsoftware/p/12454503.html)
  本文整理自《CNCF x Alibaba 云原生技术公开课》第 26 讲

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

## 固定IP

https://www.kubesphere.io/zh/blogs/kubernetes-cni/

固定 IP。对于现存虚拟化 / 裸机业务 / 单体应用迁移到容器环境后，都是通过 IP 而非域名进行服务间调用，此时就需要 CNI 插件有固定 IP 的功能，包括 Pod/Deployment/Statefulset。

#### 固定 IP

基本上主流 CNI 插件都有自己的 IPAM 机制，都支持固定 IP 及 IP Pool 的分配，并且各个 CNI 插件殊途同归的都使用了 Annotation 的方式指定固定 IP。对于 Pod，分配固定 IP，对于 Deployment，使用 IP Pool 的方式分配。对于有状态的 Statefulset，使用 IP Pool 分配后，会根据 Pool 的分配顺序记好 Pod 的 IP，以保证在 Pod 重启后仍能拿到同样的 IP。


[(好)Kubernetes Pod 是如何跨节点通信的？](https://koktlzz.github.io/posts/how-kubernetes-pods-communicate-across-nodes/)
=> 讲了underlay网络的模型图示!!! => 有二层同网卡/不同网卡, 以及三层(需要BGP支持)!
Underlay Network
利用 Underlay Network 实现 Pod 跨节点通信，既可以只依赖 TCP/IP 模型中的二层协议，也可以使用三层。但无论哪种实现方式，都必须对底层的物理网络有所要求。

如图所示，Pod 与节点的 IP 地址均处于同一网段。当 Pod1 向另一节点上的 Pod2 发起通信时，数据包首先通过veth-pair和cbr0送往 Node1 的网卡。由于目的地址 10.86.44.4 与 Node1 同网段，因此 Node1 将通过 ARP 广播请求 10.86.44.4 的 MAC 地址。

CNI 插件不仅为 Pod 分配 IP 地址，它还会将每个 Pod 所在的节点信息下发给 SDN 交换机。这样当 SDN 交换机接收到 ARP 请求时，将会答复 Pod2 所在节点 Node2 的 MAC 地址，数据包也就顺利地送到了 Node2 上。

阿里云 Terway 模式的 ACK 服务使用的便是这种网络模型，只不过 Pod 间通信使用的 SDN 交换机不再是节点的交换机（下图中的“Node vSwitch”），而是单独创建的“Pod vSwitch”：

[kubernetes网络之CNI与跨节点通信原理](https://cvvz.fun/post/k8s-network-cross-host/)

这些 CNI 的基础可执行文件，按照功能可以分为三类：

- Main 插件，它是用来创建具体网络设备的二进制文件，比如bridge（网桥设备）、loopback（lo 设备）、ptp（Veth Pair 设备）等等
- IPAM（IP Address Management）插件，用来给容器分配IP地址，比如dhcp和host-local。
- CNI 社区维护的第三方 CNI 插件，比如flannel，提供跨主机通信方案

## k8s underlay cni

[关于Kubernetes网络](https://fourthringroad.com/2022/06/21/kubernetes%E5%AE%9E%E7%8E%B0vpc%E7%BD%91%E7%BB%9C/)

如果pod ip不是基于overlay网络，而是基于underlay网络，那么会遇到以下的问题

- 可分配ip数目依赖于underlay网络的网络规划，有可能可用ip数目很少
- 跨网段通讯需要nat或其它映射技术的支持
- underlay网络ip的变化有可能会导致pod ip的变化


https://segmentfault.com/a/1190000041526210
=> 就是介绍Fabric的...
Fabric 是博云自研的 CNI 插件，旨在提供一个能适应多种场景，功能强大，性能卓越，稳定可靠以及简单易用的容器网络管理平台。
Fabric 支持 underlay/overlay 模式，同时支持 IPV4/IPV6 单栈和双栈，支持容器多网络/多网卡以及集群联邦，EIP，Qos，NetworkPolicy，PodSecurity，Windows 等特色功能。

1.1 主流 CNI 对比

支持underlay模式
- Flannel 否?
- Fabric  是，不依赖BGP但是需要提供独立业务网络

固定IP/MAC
- Flannel 否?

[清除k8s使用underlay网络的障碍](https://cloud.tencent.com/developer/article/1455458)
上一篇说到在k8s里使用underlay网络有一个弊端，使用了underlay网络的pod无法访问serviceIP，这一点可能通过修改修改业务应用的chart来解决，主要解决方法是：

开发cni插件的一般过程
上面实际的开发了一个崭新的cni插件，下面总结一下开发cni插件的过程：

- 首先是画好网络拓扑图，示例如下。在这个拓扑图中要将同宿主机上的pod之间、pod及宿主机、跨主机上的pod之间网络流量如何流转描述清楚，这里需要了解较多的网络知识，如网络的二三层、路由表、nat、bridge、openvswith、sdn、policy route等。


[kubernetes系列之二十：Kubernetes Calico网络插件](https://blog.csdn.net/cloudvtech/article/details/90480449)

由于calico是基于三层的解决方案，所以不要求所有节点在同一个大二层之内(当然BGP模式还是要求数据中心内部中间节点的路由器都支持BGP协议)，也不存在随着容器增加而带来的大量mac广播风暴，数据中心mac地址广播流量只和k8s节点数目有关，和容器的多少无关。


http://icyfenix.cn/immutable-infrastructure/network/cni.html
网络插件生态
- Overlay 模式
  靠隧道打通，不依赖底层网络；
- 路由模式
  靠路由打通，部分依赖底层网络；
- Underlay 模式
  靠底层网络打通，强依赖底层网络；


https://blog.yingchi.io/posts/2020/8/k8s-flannel.html
从网络模型到 CNI
在理解 CNI 机制以及 Flannel 等具体实现方案之前，首先要理解问题的背景，这里从 kubernetes 网络模型开始回顾。

从底层网络来看，kubernetes 的网络通信可以分为三层去看待：

- Pod 内部容器通信；
- 同主机 Pod 间容器通信；
- 跨主机 Pod 间容器通信；

## flannel host-gw

=> 看原理没有实现让外部其他服务访问pod的方法! => 配置一个网关应该也是可以的吧!!!

关键字《k8s flannel-host-gw》

https://hex108.gitbook.io/kubernetes-notes/wang-luo/flannel/host-gw

Host-gw原理
Host-gw并不是一个linux里类似vxlan的专有概念，它只是Flannel里的一个利用route表实现不同主机上container互连的backend，**当然前提条件是各主机在一个子网内，是layer2互通的。**

```
# node0配置
root@node0:~# /vagrant/config_docker0.sh 192.168.0.1/24 192.168.0.1/24
root@node0:~# ip route add 192.168.1.0/24 via 172.28.128.10 dev enp0s8 
root@node0:~# iptables -A FORWARD -s 192.168.0.0/16 -j ACCEPT
root@node0:~# iptables -A FORWARD -d 192.168.0.0/16 -j ACCEPT
root@node0:~# echo 1 > /proc/sys/net/ipv4/ip_forward

# node1配置
root@node1:~# /vagrant/config_docker0.sh 192.168.1.1/24 192.168.1.1/24
root@node1:~# ip route add 192.168.1.0/24 via 172.28.128.9 dev enp0s8 
root@node1:~# iptables -A FORWARD -s 192.168.0.0/16 -j ACCEPT
root@node1:~# iptables -A FORWARD -d 192.168.0.0/16 -j ACCEPT
root@node1:~# echo 1 > /proc/sys/net/ipv4/ip_forward
```

[Kubernetes Flannel：HOST-GW模式](https://blog.csdn.net/qq_34556414/article/details/125988271)
host-gw模式相比vxlan简单了许多，直接添加路由，将目的主机当做网关，直接路由原始封包

其他资料
[Flannel的两种模式解析（VXLAN、host-gw)](https://juejin.cn/post/6994825163757846565)

[Flannel HOST-GW 跨节点通信](https://blog.51cto.com/liujingyu/5353668)

使用 host-gw 通过远程机器 IP 创建到子网的 IP 路由。需要运行 flannel 的主机之间的二层互联。 Host-gw 是通过二层互联，利用了linux kernel 的 FORWARD 特性，报文不经过额外的封装和 NAT，所以提供了良好的性能、很少的依赖关系和简单的设置。
部署 host-gw 模式，只需要将 "Type": "vxlan" 更换为 "Type": "host-gw"

host-gateway 的模式的报文没有经过任何封装，而是通过宿主机路由的方式，直接指向到目的pod 所在的node 的ip地址为网关，所以这也是为什么 host-gw模式 要求要二层网络互通，**因为网关是二层的出口，如果不在同一个二层，网关的地址就不可能通过二层的方式找到，就没有办法通过路由的方式找到目的地址。**
