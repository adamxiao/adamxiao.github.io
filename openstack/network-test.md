# openstack网络调研

验证ovn dhcp:
```
ovn-nbctl ls-add dmz
ovn-nbctl lsp-add dmz dmz-vm1
ovn-nbctl lsp-set-addresses dmz-vm1 "02:ac:10:ff:01:30 172.16.255.130"
#ovn-nbctl lsp-set-port-security dmz-vm1 "02:ac:10:ff:01:30 172.16.255.130"
ovn-nbctl show

dmzDhcp="$(ovn-nbctl create DHCP_Options cidr=172.16.255.128/26 \
options="\"server_id\"=\"172.16.255.129\" \"server_mac\"=\"02:ac:10:ff:01:29\" \
\"lease_time\"=\"3600\" \"router\"=\"172.16.255.129\"")"
echo $dmzDhcp
ovn-nbctl dhcp-options-list

ovn-nbctl lsp-set-dhcpv4-options dmz-vm1 $dmzDhcp
ovn-nbctl lsp-get-dhcpv4-options dmz-vm1
```

配置虚拟机验证dhcp
```bash
ip netns add vm1
ovs-vsctl add-port br-int vm1 -- set interface vm1 type=internal
ip link set vm1 address 02:ac:10:ff:01:30
ip link set vm1 netns vm1
ovs-vsctl set Interface vm1 external_ids:iface-id=dmz-vm1
ip netns exec vm1 dhclient vm1
ip netns exec vm1 ip addr show vm1
ip netns exec vm1 ip route show
```

通过一次dhclient请求, 比较流表匹配规则差异, 得到ovn的dhcp最终实现流表规则如下:
由于用到pause, 需要使用ovs2.6版本才能支持!
https://stackoverflow.com/questions/50327210/pause-controller-action-in-open-vswitch
It looks like support for the pause controller action was added in the version 2.6.0 of Open vSwitch. Otherwise, the following syntax should work:
```
table=0, n_packets=465, n_bytes=25446, priority=100,in_port=5 actions=load:0x1->NXM_NX_REG13[],load:0x3->NXM_NX_REG11[],load:0x2->NXM_NX_REG12[],load:0x5->OXM_OF_METADATA[],load:0x1->NXM_NX_REG14[],resubmit(,8)
table=8, n_packets=465, n_bytes=25446, priority=50,reg14=0x1,metadata=0x5 actions=resubmit(,9)
table=9, n_packets=465, n_bytes=25446, priority=0,metadata=0x5 actions=resubmit(,10)
table=10, n_packets=465, n_bytes=25446, priority=0,metadata=0x5 actions=resubmit(,11)
table=11, n_packets=465, n_bytes=25446, priority=0,metadata=0x5 actions=resubmit(,12)
table=12, n_packets=450, n_bytes=24300, priority=0,metadata=0x5 actions=resubmit(,13)
table=13, n_packets=465, n_bytes=25446, priority=0,metadata=0x5 actions=resubmit(,14)
table=14, n_packets=465, n_bytes=25446, priority=0,metadata=0x5 actions=resubmit(,15)
table=15, n_packets=465, n_bytes=25446, priority=0,metadata=0x5 actions=resubmit(,16)
table=16, n_packets=465, n_bytes=25446, priority=0,metadata=0x5 actions=resubmit(,17)
table=17, n_packets=465, n_bytes=25446, priority=0,metadata=0x5 actions=resubmit(,18)
table=18, n_packets=465, n_bytes=25446, priority=0,metadata=0x5 actions=resubmit(,19)
table=19, n_packets=465, n_bytes=25446, priority=0,metadata=0x5 actions=resubmit(,20)
table=20, n_packets=465, n_bytes=25446, priority=0,metadata=0x5 actions=resubmit(,21)
table=21, n_packets=465, n_bytes=25446, priority=0,metadata=0x5 actions=resubmit(,22)
table=22, n_packets=5, n_bytes=1710, priority=100,udp,reg14=0x1,metadata=0x5,dl_src=02:ac:10:ff:01:30,nw_src=0.0.0.0,nw_dst=255.255.255.255,tp_src=68,tp_dst=67 actions=controller(userdata=00.00.00.02.00.00.00.00.00.01.de.10.00.00.00.63.ac.10.ff.82.33.04.00.00.0e.10.01.04.ff.ff.ff.c0.03.04.ac.10.ff.81.36.04.ac.10.ff.81,pause),resubmit(,23)
table=23, n_packets=6, n_bytes=1908, priority=100,udp,reg0=0x8/0x8,reg14=0x1,metadata=0x5,dl_src=02:ac:10:ff:01:30,tp_src=68,tp_dst=67 actions=move:NXM_OF_ETH_SRC[]->NXM_OF_ETH_DST[],mod_dl_src:02:ac:10:ff:01:29,mod_nw_src:172.16.255.129,mod_tp_src:67,mod_tp_dst:68,move:NXM_NX_REG14[]->NXM_NX_REG15[],load:0x1->NXM_NX_REG10[0],resubmit(,32)
table=32, n_packets=467, n_bytes=25938, priority=0 actions=resubmit(,33)
table=33, n_packets=6, n_bytes=1908, priority=100,reg15=0x1,metadata=0x5 actions=load:0x1->NXM_NX_REG13[],load:0x3->NXM_NX_REG11[],load:0x2->NXM_NX_REG12[],resubmit(,34)
table=34, n_packets=8, n_bytes=2544, priority=0 actions=load:0->NXM_NX_REG0[],load:0->NXM_NX_REG1[],load:0->NXM_NX_REG2[],load:0->NXM_NX_REG3[],load:0->NXM_NX_REG4[],load:0->NXM_NX_REG5[],load:0->NXM_NX_REG6[],load:0->NXM_NX_REG7[],load:0->NXM_NX_REG8[],load:0->NXM_NX_REG9[],resubmit(,40)
table=40, n_packets=6, n_bytes=1908, priority=0,metadata=0x5 actions=resubmit(,41)
table=41, n_packets=6, n_bytes=1908, priority=0,metadata=0x5 actions=resubmit(,42)
table=42, n_packets=6, n_bytes=1908, priority=0,metadata=0x5 actions=resubmit(,43)
table=43, n_packets=6, n_bytes=1908, priority=0,metadata=0x5 actions=resubmit(,44)
table=44, n_packets=6, n_bytes=1908, priority=34000,udp,reg15=0x1,metadata=0x5,dl_src=02:ac:10:ff:01:29,nw_src=172.16.255.129,tp_src=67,tp_dst=68 actions=resubmit(,45)
table=45, n_packets=6, n_bytes=1908, priority=0,metadata=0x5 actions=resubmit(,46)
table=46, n_packets=6, n_bytes=1908, priority=0,metadata=0x5 actions=resubmit(,47)
table=47, n_packets=6, n_bytes=1908, priority=0,metadata=0x5 actions=resubmit(,48)
table=48, n_packets=6, n_bytes=1908, priority=0,metadata=0x5 actions=resubmit(,49)
table=49, n_packets=6, n_bytes=1908, priority=50,reg15=0x1,metadata=0x5 actions=resubmit(,64)
table=64, n_packets=6, n_bytes=1908, priority=100,reg10=0x1/0x1,reg15=0x1,metadata=0x5 actions=push:NXM_OF_IN_PORT[],load:0xffff->NXM_OF_IN_PORT[],resubmit(,65),pop:NXM_OF_IN_PORT[]
table=65, n_packets=6, n_bytes=1908, priority=100,reg15=0x1,metadata=0x5 actions=output:5
```

dhcp方案:
* 1.dnsmasq
* 2.vr虚拟机里面配置dnsmasq
* 3.ovs实现dhcp
* 4.ovn实现dhcp

高可用方案:
多个dnsmasq副本

[Neutron 理解（5）：Neutron 是如何向 Nova 虚机分配固定IP地址的 （How Neutron Allocates Fixed IPs to Nova Instance）](https://www.pianshen.com/article/456940669/)
=> neutron节点部署运行dhcp agent

[理解 OpenStack 高可用（HA）（1）：OpenStack 高可用和灾备方案 [OpenStack HA and DR]](https://www.cnblogs.com/sammyliu/p/4741967.html)
（3）DHCP Agent 的 HA
    DHCP 协议自身就支持多个 DHCP 服务器，因此，只需要在多个网卡控制节点上，通过修改配置，为每个租户网络创建多个 DHCP Agent，就能实现 DHCP 的 HA 了。

[ovn学习-3-流表分析](https://blog.motitan.com/2017/08/29/ovn%E5%AD%A6%E4%B9%A0-3-%E6%B5%81%E8%A1%A8%E5%88%86%E6%9E%90/)
看看怎么理解ovn的dhcp实现？

[(好)使用ovn-trace分析OVN 逻辑流表（Logical Flow）](https://blog.csdn.net/zhengmx100/article/details/78140948)

最近Gurucharan Shetty添加了在OVN logical network中对于multiple L3 gateway的支持。它能够基于源IP地址在gateway之间分发流量。
我们并不需要知道这一改变的所有细节。我只想说明的是我们仅仅需要改动非常少量的代码就能实现这一特性。让我们来看一看diffstat。

DHCP
OVN支持DHCPv4和DHCPv6，所有这些都是通过logical flow实现的。在很多情况下，如果要改变它们的行为，只需要改变那些生成DHCP相关的logical flow的代码就可以了。
=> dhcp功能确实是使用流表实现的！！！

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
