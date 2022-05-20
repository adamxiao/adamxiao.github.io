# ovs vlan测试

## vr使用br-ex与br-int连接

优点：对于后续做外网防火墙的更合适

https://zhuanlan.zhihu.com/p/37408055
```bash
# 连接br-int和br-ex
# 网桥与网桥的连接需要依靠一对patch类型的端口

ovs-vsctl add-port br-int patch_to_br-ex
ovs-vsctl add-port br-ex  patch_to_br-int

ovs-vsctl set interface patch_to_br-int type=patch
ovs-vsctl set interface patch_to_br-ex  type=patch

ovs-vsctl set interface patch_to_br-int options:peer=patch_to_br-ex
ovs-vsctl set interface patch_to_br-ex  options:peer=patch_to_br-int
```

TODO: 限制端口流量（根据vlan tag啥的）

## vr公共网络使用macvlan子接口

尝试创建各种模式的网络子接口，都失败了，网络不通
https://blog.csdn.net/iceman1952/article/details/119972475

1. mode private

m1和m2直接无法通信，即使外部交换机支持hairpin模式，m1和m2也无法通信。

为什么提到外部交换机呢？因为：macvlan是二层，都连在同一个交换机上。这里的意思是说即使p所连接到的交换机支持hairpin，m1和m2也无法通信。

2. mode vepa（虚拟以太网端口聚合模式）。默认

m1和m2之间的数据传输，总是走p。p连接的交换机必须要能支持hairpin模式，或p连接到路由器（路由器都支持包转发的）。

3. mode bridge

所有终端都两两相连。通信无需p转发。

4. mode passthru [nopromisc]

该模式赋予单个终端更多能力，经常用在macvtap下。在此模式下，同一张物理网卡只允许单一一个终端。全部流量都被转发到该终端，允许virtio guest更改MAC地址，或设置promiscuous 模式，以支持对网卡进行桥接或在网卡上创建vlan接口。

默认情况下，该模式强制网卡进入promiscuous模式。传入nopromisc 标志可以禁止进入promiscuous模式。

5. mode source

该模式允许设置所允许的MAC地址列表，从底层的网卡收到frame时，对比frame中的source字段。这使得可以创建基于MAC地址的VLAN，而不是基于标准端口(port)或标记(tag)的VLAN。在部署基于 802.1x MAC的行为时，由于底层网卡的驱动不支持基于MAC的VLAN，此时mode source就很有用啦。
————————————————
版权声明：本文为CSDN博主「iceman1952」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
原文链接：https://blog.csdn.net/iceman1952/article/details/119972475


```bash
ip link add link ens3 name ens3.1 type macvlan mode bridge

# 问题, ens接口已经加入到ovs桥中，就不能这样用了
root@server1:/home/adam# ovs-vsctl show
f68dc95d-7379-40a9-8d4e-78ae77aacce6
    Bridge vswitch0
        Port vswitch0
            Interface vswitch0
                type: internal
    Bridge br-int
        Port ens3
            Interface ens3
        Port f0f6b2eacdf94_l
            tag: 123
            Interface f0f6b2eacdf94_l
        Port br-int
            Interface br-int
                type: internal
        Port c2707da016a24_l
            tag: 123
            Interface c2707da016a24_l
    ovs_version: "2.13.5"
root@server1:/home/adam# ip link add link ens3 name ens3.1 type macvlan mode bridge
RTNETLINK answers: Device or resource busy

# 移除，然后生成两个子接口，就可以加入到不同的ovs桥中去
root@server1:/home/adam# ovs-vsctl del-port ens3
root@server1:/home/adam# ip link add link ens3 name ens3.1 type macvlan mode bridge
root@server1:/home/adam# ip link add link ens3 name ens3.2 type macvlan mode bridge
root@server1:/home/adam# ovs-vsctl add-port br-int ens3.1
root@server1:/home/adam# ovs-vsctl add-br br-ex
root@server1:/home/adam# ovs-vsctl add-port br-ex ens3.2
```

## vr公共网络使用br-int桥

将 vm1 作为VLAN 100的"Access端口"添加到网桥. 这意味着由VM1进入OVS的流量将没有VLAN tag，并被假设为VLAN 100的一部分:

$ ovs-vsctl add-port br0 tap0 tag=100

在VLAN 200上添加 VM2:

$ ovs-vsctl add-port br0 tap1 tag=200
————————————————
版权声明：本文为CSDN博主「redwingz」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
原文链接：https://blog.csdn.net/sinat_20184565/article/details/94481735


```
# ovs-vsctl set Port vxlan trunks=100,200
# ovs-vsctl set Port vxlan trunks=100,200
```
端口默认类型为trunk，如果需要转发所有vlan报文，该配置可以省略


PC1、PC2、PC3、PC4设置地址在同一子网中，可以通过ping测试PC1和PC3，PC2和PC4可以互通，PC1和PC2、PC4无法互通，VLAN起到了网络隔离的作用；通过在eth0抓包可以看到vxlan封装的vlan100和200报文。
tcpdump抓包能够显示vlanid? => 我抓到的没有？wireshark能够看到vlanid
https://www.sdnlab.com/20196.html


[(好)OpenVswitch初探 - VLAN篇](https://zhuanlan.zhihu.com/p/37408055)

例如：如果一个OVS交换机的端口设置了tag标签（该端口处于access模式），数据包从该端口进入到交换机内部时，该数据包就会被打上对应的tag，于是该数据包也就只能从设置了相同tag的端口发出，而在出交换机的时候，数据包上的tag会被删除。这样就实现了交换机内部的一个隔离。


* 默认

在默认模式下（VLAN_mode没被设置），如果指定了端口的tag属性，那么这个端口就工作在access模式，并且其trunk属性的值应该保持为空。否则，这个port就工作在trunk模式下，如果trunk被指定，则使用指定的trunk值。

* trunk

trunk模式的端口允许传输所有在其trunk属性中指定的那些VLAN对应的数据包。其他VLAN的数据包就会被丢弃。从trunk模式的端口中进入的数据包其VLAN ID不会发生变化。如果进入的数据包不含有VLAN ID，则该数据包进入交换机后的VLAN为0。从trunk模式的端口出去的数据包，如果VLAN ID不为空，则依然保持该VLAN ID，如果VLAN ID为空，则出去后不再包含802.1Q头部。

* access

access模式的端口只允许不带VLAN的数据包进入，不管数据包的VLAN ID是否与其tag相同，只要含有VLAN ID，这个数据包都会被端口drop。数据包进入access端口后会被打上和端口tag相同的VLAN，而再从access端口出去时，数据包的VLAN会被删除，也就是说从access的端口出去的数据包和进来时一样是不带VLAN的。

* native-tagged

native-tagged端口类似于trunk端口，它们之间的区别是如果进入native-tagged端口的数据包不含有802.1Q头部，即没有指定VLAN，那么该数据包会被当作native VLAN，其VLAN ID由端口的tag指定。

* native-untagged

native-untagged端口类似于native-tagged端口，不同点是native VLAN中的数据包从native-untagged端口出去时，会被去掉802.1Q头部。


ovs-docker add-port br-int eth0 vm01 --ipaddress=192.168.1.1/24
ovs-docker add-port br-int eth0 vm02 --ipaddress=192.168.1.2/24

ovs-docker add-port mdvs2 eth0 vm01 --ipaddress=192.168.100.1/24


```
docker run -t -i -d --name vm01 --net=none --privileged hub.iefcu.cn/xiaoyun/tmp:centos7
docker run -t -i -d --name vm02 --net=none --privileged hub.iefcu.cn/xiaoyun/tmp:centos7
```

docker run -t -i -d --name vm-pub --net=none --privileged hub.iefcu.cn/xiaoyun/tmp:centos7

模拟虚拟路由器vm-vr
```
docker run -t -i -d --name vm-vr --net=none --privileged hub.iefcu.cn/xiaoyun/tmp:centos7

ovs-docker add-port br-int eth0 vm-vr --ipaddress=192.168.1.254/24
ovs-docker add-port br-ex eth1 vm-vr --ipaddress=192.168.100.254/24

ovs-vsctl set Port xxx tag=123 # 模拟子网接口
ovs-vsctl set Port xxx tag=0 # 模拟公共网络接口
```

```bash
# 使用ip命令配置网关
ip route add default via  192.168.1.254  dev eth0

# vr 配置ipforward? => 最重要
# vr 配置网关? => 暂时可以不搞
# vr 配置snat? => 暂时可以不搞
iptables -t nat -I POSTROUTING -o eth1 -j MASQUERADE
```

使用ovs-docker工具给容器添加网卡到ovs网桥
```
ovs-docker add-port vswitch0 eth0 vm01 --ipaddress=192.168.1.1/24
ovs-docker add-port vswitch1 eth0 vm02 --ipaddress=192.168.1.2/24
ovs-docker add-port vswitch0 eth0 vm03 --ipaddress=192.168.1.3/24
ovs-docker add-port vswitch1 eth0 vm04 --ipaddress=192.168.1.4/24
```

连接vswitch0和vswitch1
网桥与网桥的连接需要依靠一对patch类型的端口
```
$ ovs-vsctl add-port vswitch0 patch_to_vswitch1
ovs-vsctl: Error detected while setting up 'patch_to_vswitch1'.  See ovs-vswitchd log for details.

$ ovs-vsctl add-port vswitch1 patch_to_vswitch0
ovs-vsctl: Error detected while setting up 'patch_to_vswitch0'.  See ovs-vswitchd log for details.


$ ovs-vsctl set interface patch_to_vswitch1 type=patch
$ ovs-vsctl set interface patch_to_vswitch0 type=patch

$ ovs-vsctl set interface patch_to_vswitch0 options:peer=patch_to_vswitch1
$ ovs-vsctl set interface patch_to_vswitch1 options:peer=patch_to_vswitch0
```

创建完这对patch类型的端口后，两个交换机就可以相互连通了。ovs端口默认是trunk模式，且可以trunk所有的VLAN tag，所以在这对patch类型的端口上可以通过打上了任意tag的流量。
