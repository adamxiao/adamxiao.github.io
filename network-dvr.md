# DVR(分布式路由)

TODO:
* 关键字《ovn 分布式路由》
* openstack Rock 配置分布式路由

## 概述

OpenStack 用户可能会发现，按照 Neutron 原先的设计，所有网络服务都在网络节 点上进行，这意味着大量的流量和处理，给网络节点带来了很大的压力。
这些处理的核心是路由器服务。任何需要跨子网的访问都需要路由器进行路由。

为了降低网络节点的负载，同时提高可扩展性，OpenStack 自 Juno 版本开始正式 引入了分布式路由(Distributed Virtual Router，DVR)特性(用户可以选择使用与 否)，**来让计算节点自己来处理原先的大量东西向流量和非 SNAT 南北流量(有 floating IP 的 vm 跟外面的通信)**。
=> SNAT的南北流量还是得走一个网关路由

[(好)技术分享：OpenStack DVR部署与分析 原创](https://blog.51cto.com/99cloud/2286711)

为了提高neutron网络服务的鲁棒性与性能，OpenStack从J版开始正式加入的DVR(Distributed Virtual Router)服务，它将原本集中在网络节点的部分服务分散到了计算节点上。

在该模式下，同租户的跨网段路由在计算节点之间直接完成，无需网络节点的参与。SNAT服务仍有网络节点集中化的处理。Floating服务则可以选择在计算节点分布式地处理，也可以选择在网络节点中心化的处理。

DVR在带来网络服务鲁棒性与性能提升的同时，也带来了一些缺陷。东西向的FWAAS服务变得无法实现，具体参考“链接”。简单来说就是FWAAS功能依赖于在同命名空间的vrouter下看到双向（有状态）的进出两条流。现在部署DVR功能后的东西向通信，打破了这条规则。下面将对OpenStack Queens版本的 DVR部署进行阐述分析。
-----------------------------------

### 总结优缺点

优点:
* 解决网络节点的流量瓶颈
* 降低负载
* 提高了可扩展性
缺点:
* 如果真有那么好，那为什么openstack默认没有开启dvr?
  ZStack实现了dvr了吗？ => 应该是没有，那个虚拟路由...
* 东西向的FWAAS服务变得无法实现

### 优化点

非分布式路由, 跨子网要经过网关路由器, 优化之后的情况如下:

| 方向 | 同一机器                    | 不同机器 |
| 东西 | 本地网桥处理                | 本地东西路由器 |
| 南北 | 本地南北路由器floating 转发 | 网络节点 SNAT 转发 |

####  东西向

东西向意味着租户同一个数据中心内不同子网之间的互相访问。

* 同一机器
对于同一主机上的不同子网之间访问，路由器直接在 br-int 上转发即可，不需要经 过外部网桥。

=> 实际测试一下

## 其他文档

[Distributed Virtual Routing for VLAN backed networks on OVN](https://www.openvswitch.org/support/ovscon2018/6/1440-sharma.pdf)
ovn支持vlan模式的dvr?

3.1. Deploying ML2/OVN with DVR => redhat openstack官网?
https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/13/html/networking_with_open_virtual_network/deploying-dvr-ovn

还可以 => 3.3. Deploying Internal DNS with OVN

[openstack DVR (pike)](https://www.jianshu.com/p/2a888d743f9a)


TODO:
[devstack搭建配置dvr](https://blog.csdn.net/chenwei8280/article/details/81589228)

[redhat openstack配置vdr](https://access.redhat.com/documentation/zh-cn/red_hat_openstack_platform/9/html/networking_guide/sec-dvr)

[openstack分布式路由详解](https://www.1024sou.com/article/495989.html)


为了降低网络节点的负载，同时提高可扩展性，OpenStack 自 Juno 版本开始正式引入了分布式路由（Distributed Virtual Router，DVR）服务，来让计算节点自己来处理原先的大量的东西向流量（不同 vpc 的 vm 之间的通信）和 DNAT 流量（有 floating IP 的 vm 跟外面的通信）。

注意：openstack 比较新的官方安装文档把默认的网络组件 openvswitch 改为 Linux bridge 了，原因这里不做深究。有资料显示 dvr只能部署在 ovs 上，这个点需要注意一下。
=> linux bridge不能用？

[redhat - 13.3. DVR 已知问题和注意事项](https://access.redhat.com/documentation/zh-cn/red_hat_openstack_platform/16.1/html/networking_guide/dvr-known-issues_config-dvr)

[Multiple distributed gateway ports with OVN](https://www.youtube.com/watch?v=4iH4ZGp5GSI&ab_channel=OpenvSwitch)

[(好)ovn 通过分布式网关端口连接外部网络](https://www.jianshu.com/p/dc565d6aaebd)
分布式网关端口是一个逻辑路由器端口，只不过它需要绑定到指定节点上(一个或者多个节点)。注意和网关路由器的区别，网关路由器是绑定到指定节点(只能绑定到一个节点)的逻辑路由器，而分布式网关端口只是正常逻辑路由器上的一个端口，只不过需要绑定到某些节点。

设置分布式网关端口，可参考ovn-nb的Distributed Gateway Ports部分，有两种方式，可通过设置Logical_Router_Port表的如下两个参数实现

[openstack - OVN Routing](https://docs.openstack.org/neutron/latest/admin/ovn/routing.html)
ovn路由架构

关键字《ovn enable distributed router》

[How to create an Open Virtual Network distributed gateway router](https://developers.redhat.com/blog/2018/11/08/how-to-create-an-open-virtual-network-distributed-gateway-router)

[ovn架构](https://www.cnblogs.com/laolieren/p/ovn-architecture.html)

[OVN实验四：OVN负载均衡](https://l8liliang.github.io/2021/06/01/ovn-balancer.html)

## 参考文档

* [《深入理解neutron网络实现.pdf》](https://www.lhsz.xyz/read/openstack_understand_Neutron/dvr-config.md)
  基于Juno版本的吧?
  https://github.com/yeasy/openstack_understand_Neutron
