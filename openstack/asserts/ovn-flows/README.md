# ovn流表简化

* 不实现流量简化, 即不实现目的port处理? 全作为广播包处理!
* 不实现mac地址
* 不实现回环包禁止
* 去除所有的ct
* 去除不必要的reg初始化和使用
  * reg10去除, 不知道干嘛用的! => MFF_LOG_FLAGS: `One of MLF_* (32 bits)`
* 清除默认normal规则 => ovs-vsctl add-br br-int0 -- set Bridge br-int0 fail-mode=secure

## 测试用例

测试简单的vpc隔离和非隔离的情况!
* 同一个vni下的两个虚拟机，网络互通
  * 两个虚拟机在同一个宿主机上
  * 两个虚拟机在不同一个宿主机上
* 不通一个vni下的两个虚拟机，网络不互通
  * 两个虚拟机在同一个宿主机上
  * 两个虚拟机在不同一个宿主机上

先构建一个简单测试环境: => 测试通过
* A, B两个主机，建立geneve隧道
* 建立一个vni二层网络, id为1
* 分别在每个主机上建立一个虚拟机, 共两个虚拟机a,b

复杂测试环境:
* A, B, C三个主机, 两两建立geneve隧道
* 建立两个vni二层网络，id为1和2
* 每个vni二层网络下有四个虚拟机,a1,a2,b,c, 其中a1,a2虚拟机在同一个宿主机上

#### 简单测试环境建立测试

在主机A上, 211执行:
建立br-int0桥，以及隧道
```
ovs-vsctl add-br br-int0 -- set Bridge br-int0 fail-mode=secure
ovs-vsctl add-port br-int0 ovn-212 -- set interface ovn-212 type=geneve options:remote_ip=10.90.2.212 option:key=flow option:csum="true"
ovs-ofctl add-tlv-map br-int0 "{class=0x102,type=0x80,len=4}->tun_metadata0"
```

查看端口信息
```
#export PATH=/usr/lib/ksvd/bin:$PATH
ovs-ofctl show br-int0
ovs-ofctl dump-flows br-int0
ovs-ofctl dump-tlv-map br-int0
```

在主机B上, 212上执行:
建立br-int0桥，以及隧道
```
ovs-vsctl add-br br-int0 -- set Bridge br-int0 fail-mode=secure
ovs-vsctl add-port br-int0 ovn-211 -- set interface ovn-211 type=geneve options:remote_ip=10.90.2.211 option:key=flow option:csum="true"
ovs-ofctl add-tlv-map br-int0 "{class=0x102,type=0x80,len=4}->tun_metadata0"
```

在主机A上, 211上执行:
建立伪虚拟机接口vm1
```
ip netns add vm1
ovs-vsctl add-port br-int0 vm1 -- set interface vm1 type=internal
ip link set vm1 netns vm1
ip netns exec vm1 ip link set vm1 address 02:ac:10:ff:00:11
ip netns exec vm1 ip addr add 172.16.255.11/24 dev vm1
ip netns exec vm1 ip link set vm1 up
#ovs-vsctl set Interface vm1 external_ids:iface-id=ls1-vm1

ip netns exec vm1 ip addr show
```

在主机B上, 212上执行:
建立伪虚拟机接口vm2
```
ip netns add vm2
ovs-vsctl add-port br-int0 vm2 -- set interface vm2 type=internal
ip link set vm2 netns vm2
ip netns exec vm2 ip link set vm2 address 02:ac:10:ff:00:22
ip netns exec vm2 ip addr add 172.16.255.22/24 dev vm2
ip netns exec vm2 ip link set vm2 up
#ovs-vsctl set Interface vm2 external_ids:iface-id=ls1-vm2

ip netns exec vm2 ip addr show
```

在主机A, B分别加载流表
```
ovs-ofctl add-flows br-int0 simple.new
```

在vm1上尝试ping vm2
```
ip netns exec vm1 ping 172.16.255.22
```

## 初始化流表

假设已经存在几个节点隧道
* ovn-719893-0

简化的初始化流表如下:
```
# 隧道in流表规则
table=0, priority=100,in_port="ovn-719893-0" actions=move:NXM_NX_TUN_ID[0..23]->OXM_OF_METADATA[0..23],move:NXM_NX_TUN_METADATA0[16..30]->NXM_NX_REG14[0..14],move:NXM_NX_TUN_METADATA0[0..15]->NXM_NX_REG15[0..15],resubmit(,33)

# 这个新增隧道out流表规则，包含多个隧道出口
table=32, priority=100,metadata=0x11 actions=load:0x11->NXM_NX_TUN_ID[0..23],output:"ovn-719893-0",resubmit(,33)
table=32, priority=0 actions=resubmit(,33)

# FIXME: 这个规则有点复杂，看能否简化掉?
table=34, priority=0 actions=load:0->NXM_NX_REG0[],load:0->NXM_NX_REG1[],load:0->NXM_NX_REG2[],load:0->NXM_NX_REG3[],load:0->NXM_NX_REG4[],load:0->NXM_NX_REG5[],load:0->NXM_NX_REG6[],load:0->NXM_NX_REG7[],load:0->NXM_NX_REG8[],load:0->NXM_NX_REG9[],resubmit(,40)

table=64, priority=0 actions=resubmit(,65)
```

## 新加入一个隧道节点

分几种情况
* 当前节点是否存在二层网络虚拟机
  => 目前不做这个流量优化，默认就加规则!
  * 没存在, 则ovn基本加很少的流表即可
  * 存在, 则ovn还要加入虚拟机的流表转发规则

#### 简单加入隧道流表的in和out

in, 简单新增一个流表规则
```
table=0, priority=100,in_port="ovn-719893-0" actions=move:NXM_NX_TUN_ID[0..23]->OXM_OF_METADATA[0..23],resubmit(,33)
```

out就略麻烦一点，需要跟其他隧道流表规则合成一条规则
(FIXME: ovn这里如果没有对端没有虚拟机，不会下发规则! 对于指定目的mac地址，会将包发给指定隧道)
```
table=32, priority=100,reg15=0x8000,metadata=0x11 actions=load:0x11->NXM_NX_TUN_ID[0..23],set_field:0x8000->tun_metadata0,move:NXM_NX_REG14[0..14]->NXM_NX_TUN_METADATA0[16..30],output:"ovn-719893-0",output:"ovn-33aae2-0",resubmit(,33)
```

## 新加入一个二层网络

ovn不做任何处理, 相当于metadata多了一个id而已嘛
这边至少也要等虚拟机加入之后，才加入流量转发规则的！

## 新加入一个虚拟机接口

in, 简单打上vni=2
```
table=0, priority=100,in_port="vma" actions=load:0x2->OXM_OF_METADATA[],load:0x2->NXM_NX_REG14[],resubmit(,8)
```

指定源mac地址放通, 安全策略, 暂不使用
```
table=8, priority=50,reg14=0x2,metadata=0x2,dl_src=02:ac:10:ff:00:44 actions=resubmit(,9)
```

## 全流表规则

做的处理:
* 禁用controller mac相关流表规则
  table=27, ...
* 禁用ct
  table=13, table=18, table=47
* 禁用reg14,reg15
  table=0
* 禁用广播mac地址过滤
  table=8
* 禁用过滤vlan包
  table=8
* 禁用指定源mac地址包放通
  table=8
* 禁用icmp,arp包处理
  table=10, table=12
* 禁用根据目的mac地址进行流量优化
  => 均认为是广播包，进行广播
  table=27
* 禁用回环包丢弃?
  table=34

TODO: table=20的规则不明白什么意思，再验证一下, reg0, reg10用处?
TODO: table=64的规则不明白什么意思，再验证一下, reg10?
TODO: table=32, reg10的判断是什么意思? 猜测是不是某些流量不用走隧道?

vm4.new
```
table=0, priority=100,in_port="ovn-719893-0" actions=move:NXM_NX_TUN_ID[0..23]->OXM_OF_METADATA[0..23],resubmit(,33)
table=0, priority=100,in_port="vma" actions=load:0x2->OXM_OF_METADATA[],resubmit(,8)
table=8, priority=50,metadata=0x2 actions=resubmit(,9)
table=9, priority=0,metadata=0x2 actions=resubmit(,10)
table=10, priority=0,metadata=0x2 actions=resubmit(,11)
table=11, priority=0,metadata=0x2 actions=resubmit(,12)
table=12, priority=0,metadata=0x2 actions=resubmit(,13)
table=13, priority=0,metadata=0x2 actions=resubmit(,14)
table=14, priority=0,metadata=0x2 actions=resubmit(,15)
table=15, priority=0,metadata=0x2 actions=resubmit(,16)
table=16, priority=0,metadata=0x2 actions=resubmit(,17)
table=17, priority=0,metadata=0x2 actions=resubmit(,18)
table=18, priority=0,metadata=0x2 actions=resubmit(,19)
table=19, priority=0,metadata=0x2 actions=resubmit(,20)
table=20, priority=1,reg0=0x40/0x40,metadata=0x2 actions=push:NXM_OF_ETH_SRC[],push:NXM_OF_ETH_DST[],pop:NXM_OF_ETH_SRC[],pop:NXM_OF_ETH_DST[],load:0x1->NXM_NX_REG10[0],resubmit(,32)
table=20, priority=0,metadata=0x2 actions=resubmit(,21)
table=21, priority=0,metadata=0x2 actions=resubmit(,22)
table=22, priority=0,metadata=0x2 actions=resubmit(,23)
table=23, priority=0,metadata=0x2 actions=resubmit(,24)
table=24, priority=0,metadata=0x2 actions=resubmit(,25)
table=25, priority=0,metadata=0x2 actions=resubmit(,26)
table=26, priority=0,metadata=0x2 actions=resubmit(,27)
table=27, priority=70,metadata=0x2 actions=resubmit(,32)
table=32, priority=100,metadata=0x2 actions=load:0x2->NXM_NX_TUN_ID[0..23],output:"ovn-719893-0",resubmit(,33)
table=32, priority=0 actions=resubmit(,33)
table=33, priority=100,metadata=0x2 actions=resubmit(,34)
table=34, priority=0 actions=load:0->NXM_NX_REG0[],load:0->NXM_NX_REG1[],load:0->NXM_NX_REG2[],load:0->NXM_NX_REG3[],load:0->NXM_NX_REG4[],load:0->NXM_NX_REG5[],load:0->NXM_NX_REG6[],load:0->NXM_NX_REG7[],load:0->NXM_NX_REG8[],load:0->NXM_NX_REG9[],resubmit(,40)
table=40, priority=0,metadata=0x2 actions=resubmit(,41)
table=41, priority=0,metadata=0x2 actions=resubmit(,42)
table=42, priority=0,metadata=0x2 actions=resubmit(,43)
table=43, priority=0,metadata=0x2 actions=resubmit(,44)
table=44, priority=0,metadata=0x2 actions=resubmit(,45)
table=45, priority=0,metadata=0x2 actions=resubmit(,46)
table=46, priority=0,metadata=0x2 actions=resubmit(,47)
table=47, priority=0,metadata=0x2 actions=resubmit(,48)
table=48, priority=0,metadata=0x2 actions=resubmit(,49)
table=49, priority=100,metadata=0x2 actions=resubmit(,64)
table=64, priority=100,reg10=0x1/0x1,metadata=0x2 actions=push:NXM_OF_IN_PORT[],load:0xffff->NXM_OF_IN_PORT[],resubmit(,65),pop:NXM_OF_IN_PORT[]
table=64, priority=0 actions=resubmit(,65)
table=65, priority=100,metadata=0x2 actions=output:"vma"
```

vm3.new.new
跟vm4.new几乎一模一样, 几个端口不一样而已

验证发现这几个流表暂时没用到，不加入也行!!!
关键点就是reg10到底是干嘛用的！！！
```
table=20, n_packets=0, priority=1,reg0=0x40/0x40,metadata=0x2 actions=push:NXM_OF_ETH_SRC[],push:NXM_OF_ETH_DST[],pop:NXM_OF_ETH_SRC[],pop:NXM_OF_ETH_DST[],load:0x1->NXM_NX_REG10[0],resubmit(,32)
table=20, n_packets=0, priority=1,reg0=0x40/0x40,metadata=0x3 actions=push:NXM_OF_ETH_SRC[],push:NXM_OF_ETH_DST[],pop:NXM_OF_ETH_SRC[],pop:NXM_OF_ETH_DST[],load:0x1->NXM_NX_REG10[0],resubmit(,32)
table=32, n_packets=0, priority=0 actions=resubmit(,33)
table=64, n_packets=0, priority=100,reg10=0x1/0x1,metadata=0x2 actions=push:NXM_OF_IN_PORT[],load:0xffff->NXM_OF_IN_PORT[],resubmit(,65),pop:NXM_OF_IN_PORT[]
table=64, n_packets=0, priority=100,reg10=0x1/0x1,metadata=0x3 actions=push:NXM_OF_IN_PORT[],load:0xffff->NXM_OF_IN_PORT[],resubmit(,65),pop:NXM_OF_IN_PORT[]
```

## 旧的vlan+vxlan的流表规则

[深入理解 Neutron -- OpenStack 网络实现 (Openstack Understand Neutron)](https://cntofu.com/book/77/vxlan_mode/compute_node/br-tun.md)

这里就learn()这个流表看不懂!
```
table=0, n_packets=31, priority=1,in_port=1 actions=resubmit(,2)
table=0, n_packets=14, priority=1,in_port=2 actions=resubmit(,4)
table=0, n_packets=6, priority=0 actions=drop
table=2, n_packets=9, priority=0,dl_dst=00:00:00:00:00:00/01:00:00:00:00:00 actions=resubmit(,20)
table=2, n_packets=22, priority=0,dl_dst=01:00:00:00:00:00/01:00:00:00:00:00 actions=resubmit(,22)
table=3, n_packets=0, priority=0 actions=drop
table=4, n_packets=12, priority=1,tun_id=0x3e9 actions=mod_vlan_vid:1,resubmit(,10)
table=4, n_packets=2, priority=0 actions=drop
table=10, n_packets=12, priority=1 actions=learn(table=20,hard_timeout=300,priority=1,NXM_OF_VLAN_TCI[0..11],NXM_OF_ETH_DST[]=NXM_OF_ETH_SRC[],load:0->NXM_OF_VLAN_TCI[],load:NXM_NX_TUN_ID[]->NXM_NX_TUN_ID[],output:NXM_OF_IN_PORT[]),output:1
table=20, n_packets=9, hard_age=33, priority=1,vlan_tci=0x0001/0x0fff,dl_dst=fa:16:3e:83:95:fa actions=load:0->NXM_OF_VLAN_TCI[],load:0x3e9->NXM_NX_TUN_ID[],output:2
table=20, n_packets=0, priority=0 actions=resubmit(,22)
table=22, n_packets=11, dl_vlan=1 actions=strip_vlan,set_tunnel:0x3e9,output:2
table=22, n_packets=10, priority=0 actions=drop
```

## 更简化过的流表规则

问题: 为什么不会循环发给自己? => TODO: 原来真的会循环发给自己...
```
# 广播包, 准备发给所有port
table=33, priority=100,reg15=0x8000,metadata=0x1 actions=load:0x1->NXM_NX_REG13[],load:0x1->NXM_NX_REG15[],resubmit(,34),load:0x4->NXM_NX_REG13[],load:0x3->NXM_NX_REG15[],resubmit(,34),load:0x8000->NXM_NX_REG15[]
# 不会回环发给自己，是这个流表规则drop了
table=34, priority=100,reg10=0/0x1,reg14=0x1,reg15=0x1,metadata=0x2 actions=drop
```

```
table=0, priority=100,in_port="ovn-719893-0" actions=move:NXM_NX_TUN_ID[0..23]->OXM_OF_METADATA[0..23],resubmit(,33)
table=0, priority=100,in_port="vma" actions=load:0x2->OXM_OF_METADATA[],resubmit(,8)
table=8, priority=50,metadata=0x2 actions=resubmit(,32)
table=32, priority=100,metadata=0x2 actions=load:0x2->NXM_NX_TUN_ID[0..23],output:"ovn-719893-0",resubmit(,33)
table=32, priority=0 actions=resubmit(,33)
table=33, priority=100,metadata=0x2 actions=resubmit(,34)
table=34, priority=0 actions=load:0->NXM_NX_REG0[],load:0->NXM_NX_REG1[],load:0->NXM_NX_REG2[],load:0->NXM_NX_REG3[],load:0->NXM_NX_REG4[],load:0->NXM_NX_REG5[],load:0->NXM_NX_REG6[],load:0->NXM_NX_REG7[],load:0->NXM_NX_REG8[],load:0->NXM_NX_REG9[],resubmit(,64)
table=64, priority=100,reg10=0x1/0x1,metadata=0x2 actions=push:NXM_OF_IN_PORT[],load:0xffff->NXM_OF_IN_PORT[],resubmit(,65),pop:NXM_OF_IN_PORT[]
table=64, priority=0 actions=resubmit(,65)
table=65, priority=100,metadata=0x2 actions=output:"vma"
```

在111和113上，如下流表验证可以(ovs2.5.3)
去除了更多的reg, 以及in_port=2
```
table=0, priority=100,in_port=2 actions=move:NXM_NX_TUN_ID[0..23]->OXM_OF_METADATA[0..23],resubmit(,33)
table=0, priority=100,in_port=1 actions=load:0x2->OXM_OF_METADATA[],resubmit(,8)
table=8, priority=50,metadata=0x2 actions=resubmit(,32)
table=32, priority=100,metadata=0x2 actions=load:0x2->NXM_NX_TUN_ID[0..23],output:2,resubmit(,33)
table=32, priority=0 actions=resubmit(,33)
table=33, priority=100,metadata=0x2 actions=resubmit(,34)
table=34, priority=0 actions=load:0->NXM_NX_REG0[],load:0->NXM_NX_REG1[],load:0->NXM_NX_REG2[],load:0->NXM_NX_REG3[],load:0->NXM_NX_REG4[],load:0->NXM_NX_REG5[],load:0->NXM_NX_REG6[],load:0->NXM_NX_REG7[],resubmit(,64)
table=64, priority=100,metadata=0x2 actions=push:NXM_OF_IN_PORT[],load:0xffff->NXM_OF_IN_PORT[],resubmit(,65),pop:NXM_OF_IN_PORT[]
table=64, priority=0 actions=resubmit(,65)
table=65, priority=100,metadata=0x2 actions=output:1
```

尝试in_port=x的包，不回环发给output:x
=> 测试成功!
```
table=0, priority=100,in_port=2 actions=move:NXM_NX_TUN_ID[0..23]->OXM_OF_METADATA[0..23],resubmit(,33)
# 保存in_port
#table=0, priority=100,in_port=1 actions=load:0x2->OXM_OF_METADATA[],load:0x1->NXM_NX_REG5[],resubmit(,8)
table=0, priority=100,in_port=1 actions=load:0x2->OXM_OF_METADATA[],resubmit(,8)
table=8, priority=50,metadata=0x2 actions=resubmit(,32)
table=32, priority=100,metadata=0x2 actions=load:0x2->NXM_NX_TUN_ID[0..23],output:2,resubmit(,33)
table=32, priority=0 actions=resubmit(,33)
#table=33, priority=100,metadata=0x2 actions=resubmit(,34)
# 新增目的port存储
table=33, priority=100,metadata=0x2 actions=load:0x1->NXM_NX_REG5[],resubmit(,34),load:0x0->NXM_NX_REG5[]
# 新增drop流表
table=34, priority=100,reg5=0x1,in_port=1,metadata=0x2 actions=drop
table=34, priority=0 actions=load:0->NXM_NX_REG0[],load:0->NXM_NX_REG1[],load:0->NXM_NX_REG2[],load:0->NXM_NX_REG3[],load:0->NXM_NX_REG4[],load:0->NXM_NX_REG5[],load:0->NXM_NX_REG6[],load:0->NXM_NX_REG7[],resubmit(,64)
table=64, priority=100,metadata=0x2 actions=push:NXM_OF_IN_PORT[],load:0xffff->NXM_OF_IN_PORT[],resubmit(,65),pop:NXM_OF_IN_PORT[]
table=64, priority=0 actions=resubmit(,65)
table=65, priority=100,metadata=0x2 actions=output:1
```

FIXME: 通过学习的方法自动获取in_port?
```
ovs-ofctl add-flow br0 \
    "table=2 actions=learn(table=10, NXM_OF_VLAN_TCI[0..11], \
                           NXM_OF_ETH_DST[]=NXM_OF_ETH_SRC[], \
                           load:NXM_OF_IN_PORT[]->NXM_NX_REG0[0..15]), \
                     resubmit(,3)"
```

## FAQ

#### 获取已有流表规则

使用这个方法导出已有流表，可以很方便移到其他节点?
```
ovs-ofctl dump-flows br-int | sed '1d' | awk '{print $3,$8,$9}'
# 下面这个更好? 就是奇怪为啥字段老是变化
ovs-ofctl dump-flows --name br-int | awk '{print $3,$6,$7}'
```

使用dump-flows命令提取ovn的流表规则:
```
ovs-ofctl dump-flows --name --rsort=priority br-int
```

获取table=10
```
ovs-ofctl dump-flows --name --rsort=priority br-int
```

显示流表规则的指定字段
```
ovs-ofctl dump-flows --rsort=priority br-int table=33 | awk '{print $4,$6,$7}'
```

## 参考资料

* [Open vSwitch Advanced Features Tutorial](https://www.openvswitch.org/support/dist-docs-2.5/tutorial/Tutorial.md.html)
* [OVS - Using OpenFlow](https://docs.openvswitch.org/en/latest/faq/openflow/)
