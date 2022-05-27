# openstack网络调研

openstack yoga 一个网络中的多个子网如何手动选择, 难道是自动选择的吗?

《深入理解Neutron网路实现》
Neutron管理下面的实体：

网络：隔离的 L2 域，可以是虚拟、逻辑或交换。
子网：隔离的 L3 域，IP 地址块。其中每个机器有一个 IP，同一个子网的主机彼此 L3 可见。
  => 要是没有在路由上挂载接口, L3是不是就不通了啊?
  => 不同子网之间 L3 是互相不可见的，必须通过一个三层网关（即路由器）经过 L3 上进行通信。
端口：网络上虚拟、逻辑或交换端口。 所有这些实体都是虚拟的，拥有自动生成的唯一标示id，支持CRUD功能，并在数据库中跟踪记录状态。


* ovn单独安装到纯净的系统中测试使用? => ok 验证可以
[OVN实战---《A Primer on OVN》翻译](https://www.cnblogs.com/YaoDD/p/7474536.html)
[OVN实战---《An Introduction to OVN Routing》翻译](https://www.cnblogs.com/YaoDD/p/7475728.html)

[1 Northbound DB table](https://blog.csdn.net/zhonglinzhang/article/details/119170414)
 Northbound DB 主要有如下表：
* NB_Global	Northbound configuration
* Logical_Switch	L2 logical switch
* Logical_Switch_port	L2 logical switch port

查看可用网络：openstack network list

OpenStack的VPC对应租户的概念(即tenant，后续更新为project)，可以将它简单理解为一个具有隔离性质的网络资源集合，在其内可以提供各种网络资源供虚拟机使用。

[OpenStack R版部署及VPC配置详解！](https://posts.careerengine.us/p/5dd4b21fb1bc2b756d694c16)
现在，我们在OpenStack rocky版本的allinone部署方式中，创建“VPC”网络，并且连接到实例，最后通过浮动ip实现从宿主机外部访问虚机实例。
首先创建外网，admin管理员才有权限创建外网，普通租户是没有权限的。先在管理员处创建公网，在网络类型处选择flat网络，也可以选择vxlan等其他网络。需要注意物理网络的选择。

计算节点, 其中br-int桥里面有ovn接口，应该就是vxlan实现的
```bash
stack@devstack3:~$ sudo ovs-vsctl show
206a4e4b-dc1d-47af-9e56-de5b4846a0b8
    Manager "ptcp:6640:127.0.0.1"
        is_connected: true
    Bridge br-ex
        Port patch-provnet-8e9a025a-ce05-4397-a86e-de32cc084101-to-br-int
            Interface patch-provnet-8e9a025a-ce05-4397-a86e-de32cc084101-to-br-int
                type: patch
                options: {peer=patch-br-int-to-provnet-8e9a025a-ce05-4397-a86e-de32cc084101}
        Port br-ex
            Interface br-ex
                type: internal
    Bridge br-int
        fail_mode: secure
        datapath_type: system
        Port tap53bc2f51-c0
            Interface tap53bc2f51-c0
        Port ovn-b8fe09-0
            Interface ovn-b8fe09-0
                type: geneve
                options: {csum="true", key=flow, remote_ip="10.90.3.33"}
                bfd_status: {diagnostic="No Diagnostic", flap_count="1", forwarding="true", remote_diagnostic="Neighbor Signaled Session Down", remote_state=up, state=up}
        Port patch-br-int-to-provnet-8e9a025a-ce05-4397-a86e-de32cc084101
            Interface patch-br-int-to-provnet-8e9a025a-ce05-4397-a86e-de32cc084101
                type: patch
                options: {peer=patch-provnet-8e9a025a-ce05-4397-a86e-de32cc084101-to-br-int}
        Port tapefbdbdd7-c8
            Interface tapefbdbdd7-c8
        Port br-int
            Interface br-int
                type: internal
        Port ovn-be9f27-0
            Interface ovn-be9f27-0
                type: geneve
                options: {csum="true", key=flow, remote_ip="10.90.3.31"}
                bfd_status: {diagnostic="Control Detection Time Expired", flap_count="3", forwarding="true", remote_diagnostic="No Diagnostic", remote_state=up, state=up}
    ovs_version: "2.13.5"
```

## OVN网络虚拟化概念

关键字《ovn接口》

* OVN: Open Virtual Network
OVN补充了OVS的现有功能，增加了对虚拟网络抽象的原生(native)支持，比如虚拟2层和3层还有安全组（security group）。

[DevOps ovn架构介绍](https://www.dazhuanlan.com/mescoda/topics/1563753)
ovn 是一个 sdn 控制器，是 OVS 提供的原生虚拟化网络方案，旨在解决传统 SDN 架构的性能问题

[ovn的架构简介](https://www.jianshu.com/p/d7f41c897b9a)

[(好)OVN实践](https://feisky.gitbooks.io/sdn/content/ovs/ovn-internal.html)
OVN逻辑流表会由ovn-northd分发给每台机器的ovn-controller，然后ovn-controller再把它们转换为物理流表。

使用OVN只需要把VM的tap直接连接到br-int（而不是现在需要多加一层Linux Bridge），并使用OVS conntrack根据连接状态进行匹配，提高了流表的查找速度，同时也支持有状态防火墙和NAT。

OVN 支持的 tunnel 类型有三种，分别是 Geneve，STT 和 VXLAN。HV 与 HV 之间的流量，只能用 Geneve 和 STT 两种，HV 和 VTEP 网关之间的流量除了用 Geneve 和 STT 外，还能用 VXLAN，这是为了兼容硬件 VTEP网关，因为大部分硬件 VTEP 网关只支持 VXLAN。


[ovn为外部主机提供dhcp服务](https://lk668.github.io/2020/09/21/2020-09-21-ovn-dhcp-for-external-host/)

#### OVN 架构

[OVN架构](https://www.1024sou.com/article/536650.html)
一样的文章: [OVN架构](https://www.cnblogs.com/laolieren/p/ovn-architecture.html)

* CMS
* OVN Northbound DB
* OVN Sourthbound DB
* ...

```
                                  CMS
                                   |
                                   |
                       +-----------|-----------+
                       |           |           |
                       |     OVN/CMS Plugin    |
                       |           |           |
                       |           |           |
                       |   OVN Northbound DB   |
                       |           |           |
                       |           |           |
                       |       ovn-northd      |
                       |           |           |
                       +-----------|-----------+
                                   |
                                   |
                         +-------------------+
                         | OVN Southbound DB |
                         +-------------------+
                                   |
                                   |
                +------------------+------------------+
                |                  |                  |
 HV 1           |                  |    HV n          |
+---------------|---------------+  .  +---------------|---------------+
|               |               |  .  |               |               |
|        ovn-controller         |  .  |        ovn-controller         |
|         |          |          |  .  |         |          |          |
|         |          |          |     |         |          |          |
|  ovs-vswitchd   ovsdb-server  |     |  ovs-vswitchd   ovsdb-server  |
|                               |     |                               |
+-------------------------------+     +-------------------------------+
```

[pdf不错 - OVN实践](https://feisky.gitbooks.io/sdn/content/ovs/ovn-internal.html)
OVN逻辑流表会由ovn-northd分发给每台机器的ovn-controller，然后ovn-controller再把它们转换为物理流表。

目前，OVS支持主从模式的高可用。
OVN控制平面的Active-Active高可用还在开发中，预计会借鉴etcd的方式，基于Raft算法实现。


## OVN软件包

[(很长的文章)OVN学习整理 - OVN-安装软件包](https://blog.csdn.net/weixin_30747253/article/details/99916400)

有ovn-central, ovn-host, ovn-vtep
```
OVN-安装软件包
/etc/yum.repos.d/CentOS-OpenStack-ocata.repo
# yum list installed | grep openvswitch
openvswitch.x86_64              1:2.9.0-3.el7            @centos-openstack-ocata
openvswitch-devel.x86_64        1:2.9.0-3.el7            @centos-openstack-ocata
openvswitch-ovn-central.x86_64  1:2.9.0-3.el7            @centos-openstack-ocata
openvswitch-ovn-common.x86_64   1:2.9.0-3.el7            @centos-openstack-ocata
openvswitch-ovn-docker.x86_64   1:2.6.1-10.1.git20161206.el7
openvswitch-ovn-host.x86_64     1:2.9.0-3.el7            @centos-openstack-ocata
openvswitch-ovn-vtep.x86_64     1:2.9.0-3.el7            @centos-openstack-ocata
openvswitch-test.noarch         1:2.9.0-3.el7            @centos-openstack-ocata
python2-openvswitch.noarch      1:2.9.0-3.el7            @centos-openstack-ocata
```

#### OVN存在的意义（目标）

* 可用于生产环境
* 简洁的设计
* 支持1000台以上的物理机环境（也支持相当数量的虚拟机/容器环境）
* 基于已有的OpenStack OVS 插件 来提升性能和稳定性
* 成为OpenStack+OVS集成场景下的首选方案

#### 已经实现从OVS 平滑升级到 OVN

OVN 对于运行平台没有额外的要求，只要能够运行 OVS，就可以运行 OVN，可以和 Linux，Docker，DPDK 还有 Hyper-V 兼容，所以从 OVS 升级到 OVN 是非常简单快捷的。原有的网络、路由等数据不会丢失，也不需要对这些数据导入导出来进行数据迁移

另外 OVN 可以和很多 CMS（Cloud Management System）集成到一起，尤其是 OpenStack Neutron，这些 CMS 只需要添加一个 plugin 来配置 OVN 即可。

OVN对neutron的改变（以Ocata版本中的OVN和OVS 2.9版本来看OVN带来的变化）
OVN 里面数据的读写都是通过 OVSDB 协议来做的，取代了 neutron 里面的消息队列机制，neutron 变成了一个 API server 来处理用户的 REST 请求，其他的功能都交给 OVN 来做。

#### 使得Neutron组件数量减少

OVN原生的ML2 driver替换掉 OVS ML2 driver 和 Neutron的OVS agent；

OVN原生支持L3和DHCP功能，这样就不再需要Neutron 的L3 agent、 DHCP agent 和DVR。

从 OVN 的架构可以看出，OVN 里面数据的读写都是通过 OVSDB来做的，取代了 Neutron 的消息队列机制，所以有了 OVN 之后，Neutron 里面所有的 agent 都不需要了，Neutron 变成了一个 API server 来处理用户的 REST 请求，其他的功能都交给 OVN 来做，只需要在 Neutron 里面加一个 plugin 来调用配置 OVN。

Neutron 里面的子项目 networking-ovn 就是实现 OVN 的 plugin。Plugin 使用 OVSDB 协议来把用户的配置写在 Northbound DB 里，ovn-northd 监听到 Northbound DB 配置发生改变，然后把配置翻译到 Southbound DB 里面。 ovn-controller 监控到 Southbound DB 数据的发生变化之后，进而更新本地的流表。

OVN 里面报文的处理都是通过 OVS OpenFlow 流表来实现的，而在 Neutron 里面二层报文处理是通过 OVS OpenFlow 流表来实现，三层报文处理是通过 Linux TCP/IP 协议栈来实现。

#### OVN L3 对比 Neutron L3
Neutron 的三层功能主要有路由，SNAT 和 Floating IP（也叫 DNAT），它是通 Linux kernel 的namespace 来实现的，每个路由器对应一个 namespace，利用 Linux TCP/IP 协议栈来做路由转发。

OVN 支持原生的三层功能，不需要借助 Linux TCP/IP stack，用OpenFlow 流表来实现路由查找，ARP 查找，TTL 和 MAC 地址的更改。OVN 的路由也是分布式的，路由器在每个计算节点上都有实例，有了 OVN 之后，不需要 Neutron L3 agent 了 和DVR了。

查询logical switch等命令
```bash
sudo ovn-nbctl ls-list
stack@ubuntu-devstack:~$ sudo ovn-nbctl ls-list
e0cd1fd2-5219-4225-9c36-452a850610f0 (neutron-53bc2f51-c5ce-4b7e-b028-3cd27b820d2e)
042f6a57-fdae-4d77-91f7-ced8cf68bd15 (neutron-8c30d795-c4cc-464c-a8b1-5b738965664f)
9cd07f88-899a-4b71-a3a3-6997f03da047 (neutron-8e85cc7f-3c93-4265-84f5-f872f7a98daa)

# 查询虚拟逻辑交换机信息
sudo ovn-nbctl show e0cd1fd2-5219-4225-9c36-452a850610f0
stack@ubuntu-devstack:~$ sudo ovn-nbctl show e0cd1fd2-5219-4225-9c36-452a850610f0
switch e0cd1fd2-5219-4225-9c36-452a850610f0 (neutron-53bc2f51-c5ce-4b7e-b028-3cd27b820d2e) (aka shared)
    port b7d3735b-7c80-491f-ba04-8f9aa242b585
        addresses: ["fa:16:3e:5d:ea:b6 192.168.233.46"]
    port 8fc718bf-8af3-4f67-8543-91173f2b8c26
        addresses: ["fa:16:3e:79:2f:ae 192.168.233.165"]
    port 87b0d407-237d-46e8-8ba8-143e5f6f242d
        type: localport
        addresses: ["fa:16:3e:67:20:1f 192.168.233.2"]
    port 0aec6e43-76a7-4281-8eb4-74c3e7c3a143
        addresses: ["fa:16:3e:47:6a:88 192.168.233.55"]
    port 4c7b1d99-5ee0-42fa-a6e2-997139573dab
        addresses: ["fa:16:3e:ba:67:e9 192.168.233.63"]
    port d303acea-d4fc-4a9d-accf-04e4abd2b88d
        addresses: ["fa:16:3e:dc:70:d3 192.168.233.51"]
    port efbdbdd7-c8a5-4965-bacb-31ff74d29034
        addresses: ["fa:16:3e:a8:00:56 192.168.233.122"]
    port 29a2c59e-7196-49e6-a484-9b1e49f784e1
        addresses: ["fa:16:3e:e3:20:94 192.168.233.126"]
    port 37caeb76-0fdc-40dd-8287-3af0577fb068
        addresses: ["fa:16:3e:90:3a:85 192.168.233.103"]
    port 01dfb5e2-8635-4547-84a1-ce140c3bdc5b
        addresses: ["fa:16:3e:d6:0c:30 192.168.233.180"]
    port f545c38d-6e66-4f9e-b67e-50cede504084
        addresses: ["fa:16:3e:63:fa:48 192.168.233.118"]
```

## OVN其他资料

[OVN是如何通过external logical port来为外部主机提供DHCP服务。](https://lk668.github.io/2020/09/21/2020-09-21-ovn-dhcp-for-external-host/)

[VLAN Trunking to Guest Domains with Open vSwitch](https://blog.scottlowe.org/2013/05/28/vlan-trunking-to-guest-domains-with-open-vswitch/)
ovs-vsctl set port eth5 trunks=10,20
`ovs port trunk mode`
