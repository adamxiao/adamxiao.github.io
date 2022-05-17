# OVN实战入门

## overview

在本文中，我们将在三个host之间创建一个简单的二层overlay network。首先，我们来简单看一下，整个系统是怎么工作的。OVN基于分布式的control plane，其中各个组件分布在network的各个节点中。在OVN中包含了如下两种角色：

* OVN Central --- 现在该角色仅包含一个节点，该节点用于处理和cloud management platform等其他外部资源进行集成的API。并且在该节点中包含了OVN northbound database，用于存储追踪上层的逻辑结构，例如logical switches/port，以及OVN southbound database用于确定如何将ovn-northdb中的逻辑结构映射到物理世界中
* OVN Host -- 该角色存在于所有节点中，其中包含了virtual networking end points，例如虚拟机。OVN Host中包含一个"chassis controller"，它往上和ovn-soutdb连接，因为其中包含了权威的物理网络信息，向下作为一个openflow controller和ovs连接。
The Lab

OVN实验由三个连接到同一个子网(10.127.0.0/25)的ubuntu 17.04 server组成。每台主机以及它们的IP地址如下所示：

* ubuntu1 10.127.0.2 --- 作为OVN Central
* ubuntu2 10.127.0.3 --- 作为OVN Host
* ubuntu3 10.127.0.4 --- 作为OVN Host

## Installing Open vSwitch

和原文自行编译安装ovs不同的是，为了简单起见，我们使用了ubuntu 17.04，它的源里面已经包含了ovs 2.6.1，因此我们直接用apt-get安装即可，具体指令如下：
```bash
sudo apt-get install openvswitch-common openvswitch-switch
 
// OVN Central执行如下指令
sudo apt-get install ovn-common ovn-central ovn-host
 
// OVN Host执行如下指令
sudo apt-get install ovn-common ovn-host
```

## Creating the Integration Bridge

如果没有在输出中看到"br-int"，那么我们必须手动创建该bridge。记住，该integration bridge必须存在在所有包含虚拟机的节点中。

```bash
ovs-vsctl list-br
ovs-vsctl add-br br-int -- set Bridge br-int fail-mode=secure
ovs-vsctl list-br
```

## Connecting the Chassis Controllers to the Central Controller

在ovn2, ovn3节点上执行, 注意最后的encap-ip填写自己的
```
ovs-vsctl set open . external-ids:ovn-remote=tcp:192.168.100.121:6642
ovs-vsctl set open . external-ids:ovn-encap-type=geneve
ovs-vsctl set open . external-ids:ovn-encap-ip=192.168.100.122
```

上述命令会触发每个节点上的OVN chassis controller和ubuntu1中的OVN Central host进行连接。并且我们指定了，我们的overlay network使用geneve协议来加密数据平面流量。

我们可以使用netstat命令来确定连接是否完成。在ubuntu3的输出应当如下所示：
```
netstat -antp | grep 6642

root@ovn3:/home/adam# netstat -antp | grep 6642
tcp        0      0 192.168.100.123:33490   192.168.100.121:6642    ESTABLISHED 2240/ovn-controller
```

也能查看到br-int桥隧道建立了
```bash
root@ovn3:/home/adam# ovs-vsctl show
956bcd53-5b62-4956-8eb3-0c6e2ec55327
    Bridge br-int
        fail_mode: secure
        Port br-int
            Interface br-int
                type: internal
        Port ovn-b6254a-0
            Interface ovn-b6254a-0
                type: geneve
                options: {csum="true", key=flow, remote_ip="192.168.100.122"}
    ovs_version: "2.13.5"
```

## Defining the Logical Network

### 创建逻辑交换机

在ovn1上执行命令
```
# create the logical switch
ovn-nbctl ls-add ls1
 
# create logical port
ovn-nbctl lsp-add ls1 ls1-vm1
ovn-nbctl lsp-set-addresses ls1-vm1 02:ac:10:ff:00:11
ovn-nbctl lsp-set-port-security ls1-vm1 02:ac:10:ff:00:11
 
# create logical port
ovn-nbctl lsp-add ls1 ls1-vm2
ovn-nbctl lsp-set-addresses ls1-vm2 02:ac:10:ff:00:22
ovn-nbctl lsp-set-port-security ls1-vm2 02:ac:10:ff:00:22
 
ovn-nbctl show
```

在每一个命令集中我们都创建了一个命名唯一的logical port。通常这些logical port都会以UUID进行命名，从而确保唯一性，但是我们使用了对人类更加友好的命名方式。同时我们还定义了和每个logical port相关联的mac地址，而且我们还更近一步，利用port security对logical port进行了锁定（从而从该logical port只能使用我们提供的mac地址）。

### Addint "Fake" Virtual Machines

接下来我们将创建用于连接到logical switch的"虚拟机"。如上文所述，我们将使用OVS internal ports和network namespace来模拟虚拟机，并且使用172.16.255.0/24来作为我们的logical switch的地址空间

```bash
ip netns add vm1
ovs-vsctl add-port br-int vm1 -- set interface vm1 type=internal
ip link set vm1 netns vm1
ip netns exec vm1 ip link set vm1 address 02:ac:10:ff:00:11
ip netns exec vm1 ip addr add 172.16.255.11/24 dev vm1
ip netns exec vm1 ip link set vm1 up
ovs-vsctl set Interface vm1 external_ids:iface-id=ls1-vm1
 
ip netns exec vm1 ip addr show
```

## 其他资料

[在Packstack环境手动安装OVN](https://www.shuzhiduo.com/A/ke5jbAKV5r/)
`ovs-vsctl set open . external-ids:ovn-bridge-mappings=extnet:br-ex`

[在centos7上安装ovs ovn](https://www.jianshu.com/p/1121fcd5ab82)

[OVN学习整理](https://www.debugger.wiki/article/html/156241218917171)

[SDN控制器之OVN实验三：从OVN虚拟网络访问物理网络](https://www.cxyzjd.com/article/qq_42196196/83064982)

[OVN简介](https://www.wandouip.com/t5i351796/)
OVN的功能
* L2功能，叫Logical switches（逻辑交换机）
* L3功能，叫Logical Router（逻辑路由器）
* ACL，就像我们物理交换机可以配置ACL，OVN可以针对逻辑交换机添加ACL
* NAT，SNAT、DNAT都支持
* Load Balancer，支持面向内部的负载均衡和提供外部访问的负载均衡

## FAQ

#### 6642端口没有监听

这些包安装完成后，去ubuntu1上检查下ovsdb-server进程是否监听TCP 6641,6642端口。
6641端口用于监听OVN北向数据库，6642端口用于监听OVN南向数据库。下面是我执行netstat的输出结果:


[在centos7上安装ovs ovn](https://www.jianshu.com/p/1121fcd5ab82)
9、 让ovsdb-server监听6641,6642端口(其实，就是ovs 链接上 ovn)

在maser节点上执行 => 解决ok
```bash
ovn-nbctl set-connection ptcp:6641:192.168.100.121
ovn-sbctl set-connection ptcp:6642:192.168.100.121
```
在master节点上检查一下ovsdb-server进程是否监听TCP 6641, 6642端口。
6641端口用于监听OVN北向数据库
6642端口用于监听ovn南向数据库。


## 参考资料

* [OVN实战---《A Primer on OVN》翻译](https://www.cnblogs.com/YaoDD/p/7474536.html)
* [OVN介绍及安装流程](https://www.sdnlab.com/19157.html)
  有编译openvswitch的方法

* [OVN，你究竟对OpenShift做了啥！灵魂拷问x5 原创](https://blog.51cto.com/u_15127570/2710984)
  openshift也可以支持kube-ovn, 但默认不是 (关键字《openshift sdn ovn》)
