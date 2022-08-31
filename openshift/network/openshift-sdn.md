# openshift-sdn详解

https://zhuanlan.zhihu.com/p/466681599
[K8s] 关于Node的ExternalIP那点事儿

思路
* 安装后修改dns指向? 以方便隔离管理网和sdn? => todo
* 看cni的日志，是怎么连接vxlan的?
* bond口, 没隔离那就加大带宽
* 《openshift-sdn配置》 openshift-sdn物理网卡配置? 
* 看manifest, openshift-install生成的cvo配置!

[(好)详解openshift-sdn](https://segmentfault.com/a/1190000039689620)
我个人认为，一言蔽之，openshift-sdn就是构建了一套pod-to-pod的大二层网络。所有pod的ip都属于一个虚拟的L2中，他们彼此可以互相通过arp请求确认对方物理地址，并进行正常的网络发包。不管是arp包还是普通的ip包，都会被ovs流处理并进行必要的封装。

宿主机的IP是位于eth0上的10.173.32.63,我们看到机器上还有一些特殊的网卡：

* ovs-system 所有ovs网桥在内核中有一个统一名字，即ovs-system，我们不需要太关注
* br0 ovs服务创建的一个以太网交换机，也就是一个ovs网桥
* vethadbc25e1 使用vethpair做容器网卡虚拟化，在宿主机上会出现一个网卡
* vxlan_sys_4789 ovs网桥上的一个端口（port），用来做vxlan封装
* tun0 tun0的IP是10.178.40.1，也就是容器里的默认网关。用来转发到node、service、外部网络的流量

宿主机上有一个vxlan0，专门用来封装/解封vxlan协议的包。在ovs流表中，会将需要封装的包发给vxlan0进行封装。

当pod访问其他节点的pod时，流表会将包引向vxlan0，**IP地址封装为node的IP**，封装好之后，可以直接通过宿主机的网络发到对端节点所在的node。
=> 看这里能不能解开了。。。

可以看到对端节点ip地址192.168.100.32-35 => 能不能给节点多配置一个ip地址？
```
sudo ovs-ofctl  dump-flows br0 -O openflow13  table=90
[root@master1 core]# sudo ovs-ofctl  dump-flows br0 -O openflow13  table=90
 cookie=0xaf3f4223, duration=436762.179s, table=90, n_packets=6981944, n_bytes=2875111192, priority=100,ip,nw_dst=10.129.0.0/23 actions=move:NXM_NX_REG0[]->NXM_NX_TUN_ID[0..31],set_field:192.168.100.32->tun_dst,output:vxlan0
 cookie=0xe66d8df8, duration=436761.791s, table=90, n_packets=6609602, n_bytes=2732849491, priority=100,ip,nw_dst=10.130.0.0/23 actions=move:NXM_NX_REG0[]->NXM_NX_TUN_ID[0..31],set_field:192.168.100.33->tun_dst,output:vxlan0
 cookie=0x80a19e12, duration=436761.709s, table=90, n_packets=1491872, n_bytes=526493636, priority=100,ip,nw_dst=10.131.0.0/23 actions=move:NXM_NX_REG0[]->NXM_NX_TUN_ID[0..31],set_field:192.168.100.34->tun_dst,output:vxlan0
 cookie=0x5aba0bd0, duration=436761.605s, table=90, n_packets=121032, n_bytes=17326719, priority=100,ip,nw_dst=10.128.2.0/23 actions=move:NXM_NX_REG0[]->NXM_NX_TUN_ID[0..31],set_field:192.168.100.35->tun_dst,output:vxlan0
 cookie=0x0, duration=436768.163s, table=90, n_packets=0, n_bytes=0, priority=0 actions=drop
```

https://codeantenna.com/a/Mo1Jj0Fiaq
Openshift SDN node 配置流程
从openshift-sdn-master获得所定义的IP 地址
controller.go:47] Self IP : 192.168.0.99
registry.go:195] unmashaling {"Minion":"192.168.0.99","Sub":"10.1.1.0/24"}
controller.go:175] Output of setup script: + echo 10.1.1.1 10.1.1.0/24 10.1.0.0/16

当我们新创建一个集群或者增加一个物理节点时，SDN的Controller会对节点进行一些初始化的配置，主要包括ovs、iptables两部分


关键字《openshift SDN网络管理网络分开》 => 没啥资料
《OpenShift企业部署 网络配置》 => 没啥资料


理解OpenShift（3）：网络之SDN
https://cloud.tencent.com/developer/article/1452506
[(好)理解OpenShift（3）：网络之 SDN](https://blog.csdn.net/weixin_30363509/article/details/97822588)
https://www.cnblogs.com/sammyliu/p/10064450.html => 一样的文章
https://koktlzz.github.io/posts/explorations-on-the-openshift-sdn-network-model/
[Openshift高阶探索实验 原创](https://blog.51cto.com/u_15127570/2714635)
[PaaS平台OpenShift企业部署的“脑图”](https://gist.github.com/baymaxium/d4bff9ffd309092f71dec8175765ac38)
你需要考虑如何访问应用程序、出口（egress）和入口（ingress）流量，以及如何配置负载平衡器。决定是否将运行 “主动-被动” 或 “主动-主动”，及如何负载均衡所有的堆栈。容器是“网络中的第一个公民”或依赖SDN抽象？如何处理DNS？是否需要相互SSL？你的集群在2 - 5年内有多大？一个节点上运行多少个容器？所有这些问题都将定义你的平台的网络设计。


1. 概况
为了OpenShift 集群中 pod 之间的网络通信，OpenShift 以插件形式提供了三种符合Kubernetes CNI 要求的 SDN实现：

ovs-subnet：ovs-subnet 实现的是一种扁平网络，未实现租户之间的网络隔离，这意味着所有租户之间的pod 都可以互访，这使得该实现无法用于绝大多数的生产环境。
ovs-multitenant：基于 OVS 和 VxLAN 等技术实现了项目（project）之间的网络隔离。
ovs-networkpolicy：介于ovs-subnet 和 ovs-multitenant 之间的一种实现。考虑到 ovs-multitenant  只是实现了项目级别的网络隔离，这种隔离粒度在一些场景中有些过大，用户没法做更精细的控制，这种需求导致了ovs-networkpolicy的出现。默认地，它和ovs-subnet 一样，所有租户之间都没有网络隔离。但是，管理员可以通过定义 NetworkPolicy 对象来精细地进行网络控制。可以粗略地将它类比为OpenStack neutron 中的neutron 网络防火墙和Nova安全组。具ä½请查阅有关文档。
http://ksoong.org/docs/content/openshift/advanced-deployment.html
=> 是否默认就是ovs-subnet?
oc describe network.config/cluster

节点角色类型：

* Master 节点：只承担 Master 角色，可不也可以承担Node 角色。主要运行 API 服务、controller manager 服务、etcd 服务、web console 服务等。
* Infra 节点：作为 Node 角色，通过设置并应用节点标签，只用于部署系统基础服务，包括Registry、Router、Prometheus 以及 EFK 等。
* Node 节点：作为 Node 角色，用于运行用户业务系统的Pod。

1.1 OpenShift 集群的网络设计
要部署一个OpenShift 生产环境，主要的网络规划和设计如下图所示：

网络类型：

* 外部网络：这是一个外部网络，用于从外部访问集群。和该网络连接的服务器或组件需要被分配公网IP地址才能被从外部访问。从内部访问外网中的服务时，比如DNS或者镜像仓库，可以通过NAT实现，而无需公网IP地址。
* 管理网络：这是一个内部网络，用于集群内部 API 访问。
* IPMI网络：这是一个内部网络，用于管理物理服务器。
* SDN网络：这是一个内部网络，用于集群内部Pod 之间的通信，承载 VxLAN Overlay 流量。
* 存储网络：这是一个内部网络，用于各节点访问基于网络的存储。
* 在PoC 或开发测试环境中，管理/SDN/存储网络可以合并为一个网络。

OpenShift多网络平面选择与配置
https://blog.csdn.net/qq_21127151/article/details/124662331

2. 静态指定
修改网络ClusterOperator，增加附加网络的定义。配置附加网络名称（macvlan-network），配置静态IP（192.168.91.250），配置网关（192.168.91.1），配置物理网卡名称（ens3），将网络定义赋予tomcat项目中 。
