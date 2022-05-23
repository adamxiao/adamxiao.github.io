# ovn资料

[ovn 通过分布式网关端口连接外部网络](https://www.jianshu.com/p/dc565d6aaebd)

[OVN实战三之打通真实网络提供NAT](https://www.sdnlab.com/19842.html)

## ovn ha高可用

关键字《ovn高可用》《ovn ha》

[华为云 - kube-ovn 高可用安装](https://support.huaweicloud.com/usermanual-kunpengcpfs/kunpengkubeovn_06_0013.html)

更新时间：2021-08-26 GMT+08:00

Kube-OVN的高可用包含两个组件的高可用：ovndb以及Kube-OVN-Controller。

这两个组件的高可用模式存在差异，其中ovndb通过RAFT做分布式一致性可以做到Active-Active的cluster高可用，Kube-OVN-Controller需要处理集群中的状态和事件，同一事件只能有一个工作实例，因此采用了Leader-Election的方式进行选举式的高可用。

ovndb高可用安装
增加ovndb部署节点，建议总共有奇数个部署ovndb的节点（1，3，5…）。
=> 就是部署ovn-central服务, 有nb和sb数据库, northd服务

[ovn官网 - OVN Gateway High Availability Plan](https://docs.ovn.org/en/latest/topics/high-availability.html)

## 其他

ovn-controller运行在每一个计算节点上

[RHOSP Chapter 2. Planning your OVN deployment ](https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/13/html/networking_with_open_virtual_network/planning_your_ovn_deployment)
RH OpenStack Platform关于ovn高可用的部署文档

2.4. High Availability with pacemaker and DVR

With the pacemaker HA profile enabled, ovsdb-server runs in master-slave mode, managed by pacemaker and the resource agent Open Cluster Framework (OCF) script. The OVN database servers start on all the Controllers, and pacemaker then selects one controller to serve in the master role. The instance of ovsdb-server that runs in master mode can write to the database, while all the other slave ovsdb-server services replicate the database locally from the master, and can not write to the database.

[RHOSP 14的ovn部署说明](https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/14/html/networking_with_open_virtual_network/planning_your_ovn_deployment)


[openstack - network-ovn FAQ](https://docs.openstack.org/networking-ovn/ocata/faq.html)

Q: Does OVN support DVR or distributed L3 routing?

[ovs-discuss] How to create OVN HA active-active?
https://mail.openvswitch.org/pipermail/ovs-discuss/2020-October/050753.html

## 旧的资料

[OVN HA](https://tonydeng.github.io/sdn-handbook/ovs/ovn-ha.html)
=> 借助Pacemaker来实现自动故障恢复

## 参考资料

[ovn high-availability](https://docs.ovn.org/en/latest/topics/high-availability.html)
