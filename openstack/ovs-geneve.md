# ovn中使用ovs流标实现geneve二层网络

创建全新的的ovs环境, 创建br-int桥
```
apt install -y openvswitch-common openvswitch-switch

ovs-vsctl list-br
ovs-vsctl add-br br-int -- set Bridge br-int fail-mode=secure
```

## Geneve概念

[网络虚拟化协议GENEVE](https://www.sdnlab.com/20693.html)

在实现上，GENEVE与VXLAN类似，仍然是Ethernet over UDP，也就是用UDP封装Ethernet。VXLAN header是固定长度的（8个字节，其中包含24bit VNI），与VXLAN不同的是，GENEVE header中增加了TLV（Type-Length-Value），由8个字节的固定长度和0~252个字节变长的TLV组成。GENEVE header中的TLV代表了可扩展的元数据。

退一步说，就算24bit的VNI是够用的，现在一些新的应用需要网络虚拟化协议里面携带其他的元数据。例如加入port ID来作为安全规则的识别符。假设port ID是16bit，那24bit的VNI只剩下8bit用来标识租户网络，这明显是不够用的。

## 验证测试

```
# 在211上执行
ovs-vsctl add-br br-int0 -- set Bridge br-int0 fail-mode=secure
ovs-vsctl add-port br-int0 ovn-212 -- set interface ovn-212 type=geneve options:remote_ip=10.90.2.212 option:key=flow option:csum="true"
ovs-ofctl add-tlv-map br-int0 "{class=0x102,type=0x80,len=4}->tun_metadata0"

# 在212上执行
ovs-vsctl add-br br-int0 -- set Bridge br-int0 fail-mode=secure
ovs-vsctl add-port br-int0 ovn-211 -- set interface ovn-211 type=geneve options:remote_ip=10.90.2.211 option:key=flow option:csum="true"
ovs-ofctl add-tlv-map br-int0 "{class=0x102,type=0x80,len=4}->tun_metadata0"
```

查看端口信息
```
#export PATH=/usr/lib/ksvd/bin:$PATH
ovs-ofctl show br-int0
ovs-ofctl dump-flows br-int0
```

新增伪虚拟机接口
在一台主机上建立vm1
```bash
ip netns add vm1
ovs-vsctl add-port br-int0 vm1 -- set interface vm1 type=internal
ip link set vm1 netns vm1
ip netns exec vm1 ip link set vm1 address 02:ac:10:ff:00:11
ip netns exec vm1 ip addr add 172.16.255.11/24 dev vm1
ip netns exec vm1 ip link set vm1 up
#ovs-vsctl set Interface vm1 external_ids:iface-id=ls1-vm1

ip netns exec vm1 ip addr show
```

再在另外一台主机建立vm2
```bash
ip netns add vm2
ovs-vsctl add-port br-int0 vm2 -- set interface vm2 type=internal
ip link set vm2 netns vm2
ip netns exec vm2 ip link set vm2 address 02:ac:10:ff:00:22
ip netns exec vm2 ip addr add 172.16.255.22/24 dev vm2
ip netns exec vm2 ip link set vm2 up
#ovs-vsctl set Interface vm2 external_ids:iface-id=ls1-vm2

ip netns exec vm2 ip addr show
```

在vm1上尝试ping vm2
```
ip netns exec vm1 ping 172.16.255.22
```

然后加载流表
```
ovs-ofctl add-flows br-int0 ovn.flows
```


## 流表分析

ovn-controller源码中也有
https://github.com/ovn-org/ovn/blob/main/controller/physical.c

#### 问题

* 不同二层怎么隔离的? => done
  好像是vni不同
  => 新建ls, 进行测试?
* 不同ls上的portid验证, 确定是否有影响?

* 二层流表全整理
  * 两个虚拟机在同一个宿主机 => 根据不同的目的port，发到不同的port!
     如果是二层三层广播包呢? 流量怎么走的 TODO:
     `arping -c 1 172.16.255.77`
     看流表，没有指定特殊的广播流表规则，再分析一下
     对于目的mac地址为广播包的，则把reg15配置为广播
     `table=27, priority=70,metadata=0x11,dl_dst=01:00:00:00:00:00/01:00:00:00:00:00 actions=load:0x8000->NXM_NX_REG15[],resubmit(,32)`
     关键就是这个table=33的流表规则, 把广播包往不同的虚拟机端口发送(以及最后还要往隧道口发送)
     `table=33, priority=100,reg15=0x8000,metadata=0x11 actions=load:0x5->NXM_NX_REG13[],load:0x5->NXM_NX_REG15[],resubmit(,34),load:0x1->NXM_NX_REG13[],load:0x1->NXM_NX_REG15[],resubmit(,34),load:0x4->NXM_NX_REG13[],load:0x3->NXM_NX_REG15[],resubmit(,34),load:0x8000->NXM_NX_REG15[]`

  * 两个虚拟机不在同一个宿主机
     对于目的mac地址为xxx的包，新增了流表规则，发给隧道端口
     `table=32, priority=100,reg15=0x3,metadata=0x11 actions=load:0x11->NXM_NX_TUN_ID[0..23],set_field:0x3->tun_metadata0,move:NXM_NX_REG14[0..14]->NXM_NX_TUN_METADATA0[16..30],output:1`
  * 对端宿主机没有此二层网络虚拟机(就是未开机嘛)
     那就不用加流表规则
  * 广播，发往多个隧道口的方法?
    reg15表示广播包?
    `table=32, priority=100,reg15=0x8000,metadata=0x11 actions=load:0x11->NXM_NX_TUN_ID[0..23],set_field:0x8000->tun_metadata0,move:NXM_NX_REG14[0..14]->NXM_NX_TUN_METADATA0[16..30],output:1,output:5,resubmit(,33)`

* 流表简化, 去除暂时没用到的流表规则

* 实际验证两个真实的虚拟机二层通信!
  => 使用那个流表是可以的!

#### reg数据分析

* FIXME: 简化流表规则, 去除reg14,reg15的使用，也是可以的吧
  同时也可以去除reg11,reg12,reg13

* metadata: 0x2 可能就是vni? 验证了多次, 确实是的
  `load:0x11->OXM_OF_METADATA[]` => 虚拟机发出来的包就打上vni=11信息
  `move:NXM_NX_TUN_ID[0..23]->OXM_OF_METADATA[0..23]` => 提取geneve隧道头中vni配置
  `load:0x11->NXM_NX_TUN_ID[0..23]` => 将vni=11, 放到隧道vni配置中
  问题: metadata只有8个字节，不够怎么办? (猜测用了其他reg存储) 还有看到是64 bit? FIXME: 测试一下就行了吧
  https://cloud.tencent.com/developer/article/1082758 说有６４个字节

* NXM_NX_TUN_ID: VXLAN and Geneve have a 24-bit virtual network identifier (VNI).
  (ovs支持的配置字段)

* NXM_NX_REG0 FIXME: 干嘛用的? ct, 暂时可以不用吧
  4bit

* NXM_OF_ETH_SRC => src mac
* NXM_OF_ETH_DST => dst mac
* NXM_NX_REG10 => FIXME: 干嘛用的? 暂时搞不清干嘛用的，暂可以不用吧?
  4bit? ovs2.6+版本才支持
  MFF_LOG_FLAGS: `One of MLF_* (32 bits)`


* OXM_OF_METADATA
  OpenFlow Metadata Field

* NXM_NX_REG15 => 存储NXM_NX_TUN_METADATA0, geneve协议选项数据, 4bit
  4bit? ovs2.6+版本才支持
  => 重点，了解geneve协议字段的含义 => 反正就是多传输了4个字节的数据
  NXM_NX_TUN_METADATA0值抓包为00,01,00,02(4bytes)
  `set_field:0x2->tun_metadata0`
  `move:NXM_NX_TUN_METADATA0[0..15]->NXM_NX_REG15[0..15]`
  => 值为00,02? 可能是源portid，和目的portid
  从ovn源码了解到是 MFF_LOG_OUTPORT, 逻辑目的端口portid

* NXM_NX_REG14 => 存储NXM_NX_TUN_METADATA0, geneve协议选项数据, 4bit
  4bit? ovs2.6+版本才支持
  NXM_NX_TUN_METADATA0值抓包为00,01,00,02(4bytes)
  => `NXM_NX_REG14[0..14]->NXM_NX_TUN_METADATA0[16..30]`
  => 值为00,01? 
  从ovn源码了解到是 MFF_LOG_INPORT, 逻辑源端口portid

* NXM_NX_REG13 => 看流表是做连接跟踪使用的
  4bit? ovs2.6+版本才支持
  MFF_LOG_CT_ZONE: Logical conntrack zone for lports

* NXM_NX_REG12 => 看流表是暂时没用到
  4bit? ovs2.6+版本才支持
  MFF_LOG_SNAT_ZONE: conntrack snat zone for gateway router

* NXM_NX_REG11 => 看流表是暂时没用到
  4bit? ovs2.6+版本才支持
  MFF_LOG_DNAT_ZONE: conntrack dnat zone for gateway router

* NXM_NX_TUN_METADATA0 => geneve协议选项数据
  其中tun_metadata0中的数据为:
使用wireshark查看，发现class为OVN, type为Critical, tun_metadata0为00,01,00,02(4bytes)
```
ovs-ofctl dump-tlv-map br-int
NXT_TLV_TABLE_REPLY (xid=0x2):
 max option space=256 max fields=64
 allocated option space=4

 mapping table:
  class  type  length  match field
 ------  ----  ------  --------------
  0x102  0x80       4  tun_metadata0
```


#### 虚拟机收发包流向分析

虚拟机发出来的icmp(或arp)包，流表走向
* table 0
  打上标志, 保存相关信息到reg
  `n_packets=21, priority=100,in_port=2 actions=load:0x1->NXM_NX_REG13[],load:0x2->NXM_NX_REG11[],load:0x3->NXM_NX_REG12[],load:0x2->OXM_OF_METADATA[],load:0x1->NXM_NX_REG14[],resubmit(,8)`
* table 8
  过滤非法mac地址? => 原来是mac地址不对，这里过滤掉了
  `n_packets=0, priority=50,reg14=0x1,metadata=0x2,dl_src=02:ac:10:ff:00:33 actions=resubmit(,9)`
* table 10
  特殊icmp协议处理?
  arp协议处理?
* table 12
  icmp6协议处理?
* table 13
  连接跟踪? 暂时没有用到
* table 18
  ipv6连接跟踪? 暂时没有用到
* table 20
  标志提取? 暂时没用到
* table 27
  reg15处理, 暂时没用到
  目前只处理了arp包
* table 33
  arp包最终通过隧道接口发送出去了!
  同时也可能是发给本宿主机上的其他虚拟机

抓包发现
```
21:26:38.514482 IP 10.90.2.211.51496 > 10.90.2.212.6081: Geneve, Flags [C], vni 0x2, options [8 bytes]: ARP, Request who-has 172.16.255.44 tell 172.16.255.33, length 28
```

另外一台主机的收包逻辑, 流表走向:
* table 0
  处理隧道geneve协议的信息: vni等
  问题：这里对端居然没有收到包?
  => 临时放开防火墙！！！ `firewall-cmd --zone=public --add-port=6081/udp`
* table 33
  `n_packets=34, priority=100,reg15=0x8000,metadata=0x2 actions=load:0x1->NXM_NX_REG13[],load:0x2->NXM_NX_REG15[],resubmit(,34),load:0x8000->NXM_NX_REG15[]`
* table 34
  重置reg相关数据...
  `n_packets=70, priority=0 actions=load:0->NXM_NX_REG0[],load:0->NXM_NX_REG1[],load:0->NXM_NX_REG2[],load:0->NXM_NX_REG3[],load:0->NXM_NX_REG4[],load:0->NXM_NX_REG5[],load:0->NXM_NX_REG6[],load:0->NXM_NX_REG7[],load:0->NXM_NX_REG8[],load:0->NXM_NX_REG9[],resubmit(,40)`
* table 40
  `n_packets=65, priority=0,metadata=0x2 actions=resubmit(,41)`
* table 41
  做啥逻辑? 暂时没有用
  `n_packets=76, priority=0,metadata=0x2 actions=resubmit(,42)`
* table 42
  ct连接跟踪, icmp和arp不用处理
  `n_packets=79, priority=0,metadata=0x2 actions=resubmit(,43)`
* table 43-46
  暂时没有用到
* table 47
  ct连接跟踪, icmp和arp不用处理
  `n_packets=88, priority=0,metadata=0x2 actions=resubmit(,48)`
* table 48
  暂时没看到啥用
* table 49
  发给目的虚拟机mac地址过滤
  `table=49, priority=50,reg15=0x2,metadata=0x4,dl_dst=02:ac:10:ff:00:22 actions=resubmit(,64)`
  广播包的处理?
  `table=49, priority=100,metadata=0x11,dl_dst=01:00:00:00:00:00/01:00:00:00:00:00 actions=resubmit(,64)`
* table 64
  `xxx`
* table 65
  最终数据包发给虚拟机接口
  `table=65, priority=100,reg15=0x2,metadata=0x4 actions=output:2`


#### 流表整理

[流表转换](https://www.jianshu.com/p/1ce3ffdc3e5e)
openflow流表按照功能划分为如下的table

```
/* OpenFlow table numbers.
 *
 * These are heavily documented in ovn-architecture(7), please update it if
 * you make any changes. */
#define OFTABLE_PHY_TO_LOG            0
#define OFTABLE_LOG_INGRESS_PIPELINE  8 /* First of LOG_PIPELINE_LEN tables. */
#define OFTABLE_REMOTE_OUTPUT        37
#define OFTABLE_LOCAL_OUTPUT         38
#define OFTABLE_CHECK_LOOPBACK       39
#define OFTABLE_LOG_EGRESS_PIPELINE  40 /* First of LOG_PIPELINE_LEN tables. */
#define OFTABLE_SAVE_INPORT          64
#define OFTABLE_LOG_TO_PHY           65
#define OFTABLE_MAC_BINDING          66
#define OFTABLE_MAC_LOOKUP           67
#define OFTABLE_CHK_LB_HAIRPIN       68
#define OFTABLE_CHK_LB_HAIRPIN_REPLY 69
#define OFTABLE_CT_SNAT_FOR_VIP      70
#define OFTABLE_GET_FDB              71
#define OFTABLE_LOOKUP_FDB           72
```

reg含义
```
/* Logical fields.
 *
 * These values are documented in ovn-architecture(7), please update the
 * documentation if you change any of them. */
#define MFF_LOG_DATAPATH MFF_METADATA /* Logical datapath (64 bits). */
#define MFF_LOG_FLAGS      MFF_REG10  /* One of MLF_* (32 bits). */
#define MFF_LOG_DNAT_ZONE  MFF_REG11  /* conntrack dnat zone for gateway router
                                       * (32 bits). */
#define MFF_LOG_SNAT_ZONE  MFF_REG12  /* conntrack snat zone for gateway router
                                       * (32 bits). */
#define MFF_LOG_CT_ZONE    MFF_REG13  /* Logical conntrack zone for lports
                                       * (32 bits). */
#define MFF_LOG_INPORT     MFF_REG14  /* Logical input port (32 bits). */
#define MFF_LOG_OUTPORT    MFF_REG15  /* Logical output port (32 bits). */

/* Logical registers.
 *
 * Make sure these don't overlap with the logical fields! */
#define MFF_LOG_REG0             MFF_REG0
#define MFF_LOG_LB_ORIG_DIP_IPV4 MFF_REG1
#define MFF_LOG_LB_ORIG_TP_DPORT MFF_REG2

#define MFF_LOG_XXREG0           MFF_XXREG0
#define MFF_LOG_LB_ORIG_DIP_IPV6 MFF_XXREG1

#define MFF_N_LOG_REGS 10
```

#### table 0

```
# 将所有隧道接口发的数据包进行flag解析
table=0, priority=100,in_port=1 actions=move:NXM_NX_TUN_ID[0..23]->OXM_OF_METADATA[0..23],move:NXM_NX_TUN_METADATA0[16..30]->NXM_NX_REG14[0..14],move:NXM_NX_TUN_METADATA0[0..15]->NXM_NX_REG15[0..15],resubmit(,33)

# 将所有虚拟机接口发的数据包处理, 配置vni=1等信息?
table=0, priority=100,in_port=2 actions=load:0x1->NXM_NX_REG13[],load:0x3->NXM_NX_REG11[],load:0x2->NXM_NX_REG12[],load:0x4->OXM_OF_METADATA[],load:0x2->NXM_NX_REG14[],resubmit(,8)
```

#### table 8

OFTABLE_LOG_INGRESS_PIPELINE
ingress流量流水线?

```
# 丢掉源地址为组播或广播的包
table=8, priority=100,metadata=0x4,dl_src=01:00:00:00:00:00/01:00:00:00:00:00 actions=drop
# 丢掉带vlan的包
table=8, priority=100,metadata=0x4,vlan_tci=0x1000/0x1000 actions=drop
# 将所有虚拟机接口mac地址处理, 发往虚拟机接口的数据处理
table=8, priority=50,reg14=0x2,metadata=0x4,dl_src=02:ac:10:ff:00:22 actions=resubmit(,9)
```

#### table 9

暂时没用到
```
table=9, priority=0,metadata=0x4 actions=resubmit(,10)
```

#### table 10

icmp和arp协议处理
```
# 虚拟机icmp协议处理
table=10, priority=90,icmp6,reg14=0x2,metadata=0x4,dl_src=02:ac:10:ff:00:22,nw_ttl=255,icmp_type=136,icmp_code=0,nd_tll=02:ac:10:ff:00:22 actions=resubmit(,11)
table=10, priority=90,icmp6,reg14=0x2,metadata=0x4,dl_src=02:ac:10:ff:00:22,nw_ttl=255,icmp_type=136,icmp_code=0,nd_tll=00:00:00:00:00:00 actions=resubmit(,11)
table=10, priority=90,icmp6,reg14=0x2,metadata=0x4,dl_src=02:ac:10:ff:00:22,nw_ttl=255,icmp_type=135,icmp_code=0,nd_sll=02:ac:10:ff:00:22 actions=resubmit(,11)
table=10, priority=90,icmp6,reg14=0x2,metadata=0x4,dl_src=02:ac:10:ff:00:22,nw_ttl=255,icmp_type=135,icmp_code=0,nd_sll=00:00:00:00:00:00 actions=resubmit(,11)
# 虚拟机arm协议处理
table=10, priority=90,arp,reg14=0x2,metadata=0x4,dl_src=02:ac:10:ff:00:22,arp_sha=02:ac:10:ff:00:22 actions=resubmit(,11)
# 虚拟机icmp6协议处理
table=10, priority=80,icmp6,reg14=0x2,metadata=0x4,nw_ttl=255,icmp_type=136,icmp_code=0 actions=drop
table=10, priority=80,icmp6,reg14=0x2,metadata=0x4,nw_ttl=255,icmp_type=135,icmp_code=0 actions=drop
# 其他
table=10, priority=80,arp,reg14=0x2,metadata=0x4 actions=drop
table=10, priority=0,metadata=0x4 actions=resubmit(,11)
```

#### table 11 控制器?

暂时没用到
```
# ？？？这个mac地址9a:ac:b9:a6:ce:24是什么? => 最终需要发给sdn控制器的...
table=11, priority=0,metadata=0x4 actions=resubmit(,12)
```

#### table 12

也是icmp相关处理?
```
# ipv6的暂时可以不处理?
table=12, priority=110,icmp6,metadata=0x4,ipv6_src=fe80::/10,icmp_type=132 actions=resubmit(,13)
table=12, priority=110,icmp6,metadata=0x4,ipv6_src=fe80::/10,icmp_type=130 actions=resubmit(,13)
table=12, priority=110,icmp6,metadata=0x4,ipv6_src=fe80::/10,icmp_type=131 actions=resubmit(,13)
table=12, priority=110,icmp6,metadata=0x4,nw_ttl=255,icmp_type=136,icmp_code=0 actions=resubmit(,13)
table=12, priority=110,icmp6,metadata=0x4,nw_ttl=255,icmp_type=135,icmp_code=0 actions=resubmit(,13)
table=12, priority=110,icmp6,metadata=0x4,nw_ttl=255,icmp_type=133,icmp_code=0 actions=resubmit(,13)
table=12, priority=110,icmp6,metadata=0x4,nw_ttl=255,icmp_type=134,icmp_code=0 actions=resubmit(,13)
table=12, priority=110,icmp6,metadata=0x4,ipv6_dst=ff02::16,icmp_type=143 actions=resubmit(,13)
table=12, priority=0,metadata=0x4 actions=resubmit(,13)
```

#### table 13

```
table=13, priority=100,ipv6,reg0=0x1/0x1,metadata=0x4 actions=ct(table=14,zone=NXM_NX_REG13[0..15])
table=13, priority=100,ip,reg0=0x1/0x1,metadata=0x4 actions=ct(table=14,zone=NXM_NX_REG13[0..15])
table=13, priority=0,metadata=0x4 actions=resubmit(,14)
```

#### table 14-17

暂没用到
```
table=14, priority=0,metadata=0x4 actions=resubmit(,15)
table=15, priority=0,metadata=0x4 actions=resubmit(,16)
table=16, priority=0,metadata=0x4 actions=resubmit(,17)
table=17, priority=0,metadata=0x4 actions=resubmit(,18)
```

#### table 18

连接跟踪?
```
table=18, priority=100,ipv6,reg0=0x4/0x4,metadata=0x4 actions=ct(table=19,zone=NXM_NX_REG13[0..15],nat)
table=18, priority=100,ip,reg0=0x4/0x4,metadata=0x4 actions=ct(table=19,zone=NXM_NX_REG13[0..15],nat)
table=18, priority=100,ip,reg0=0x2/0x2,metadata=0x4 actions=ct(commit,zone=NXM_NX_REG13[0..15],exec(load:0->NXM_NX_CT_LABEL[0])),resubmit(,19)
table=18, priority=100,ipv6,reg0=0x2/0x2,metadata=0x4 actions=ct(commit,zone=NXM_NX_REG13[0..15],exec(load:0->NXM_NX_CT_LABEL[0])),resubmit(,19)
table=18, priority=0,metadata=0x4 actions=resubmit(,19)
```

#### table 19

暂没用到
```
table=19, priority=0,metadata=0x4 actions=resubmit(,20)
```

#### table 20

dns处理?

```
table=20, priority=1,reg0=0x40/0x40,metadata=0x4 actions=push:NXM_OF_ETH_SRC[],push:NXM_OF_ETH_DST[],pop:NXM_OF_ETH_SRC[],pop:NXM_OF_ETH_DST[],move:NXM_NX_REG14[]->NXM_NX_REG15[],load:0x1->NXM_NX_REG10[0],resubmit(,32)
table=20, priority=0,metadata=0x4 actions=resubmit(,21)
```

#### table 21-26

暂没用到
```
table=21, priority=0,metadata=0x4 actions=resubmit(,22)
table=22, priority=0,metadata=0x4 actions=resubmit(,23)
table=23, priority=0,metadata=0x4 actions=resubmit(,24)
table=24, priority=0,metadata=0x4 actions=resubmit(,25)
table=25, priority=0,metadata=0x4 actions=resubmit(,26)
table=26, priority=0,metadata=0x4 actions=resubmit(,27)
```

#### table 27 controller

根据目的mac地址决定这个包发往哪个端口(逻辑目的端口)!!!
=> 即配置reg15的值
```
# 相同二层虚拟机接口相关数据处理?
table=27, priority=50,metadata=0x4,dl_dst=02:ac:10:ff:00:11 actions=load:0x1->NXM_NX_REG15[],resubmit(,32)
table=27, priority=50,metadata=0x4,dl_dst=02:ac:10:ff:00:22 actions=load:0x2->NXM_NX_REG15[],resubmit(,32)
table=27, priority=70,metadata=0x4,dl_dst=01:00:00:00:00:00/01:00:00:00:00:00 actions=load:0x8000->NXM_NX_REG15[],resubmit(,32)
```

#### table 32

```
table=32, priority=150,reg10=0x10/0x10 actions=resubmit(,33)
table=32, priority=150,reg10=0x2/0x2 actions=resubmit(,33)


# 分流目的虚拟机数据流量
table=32, priority=100,reg15=0x1,metadata=0x4 actions=load:0x4->NXM_NX_TUN_ID[0..23],set_field:0x1->tun_metadata0,move:NXM_NX_REG14[0..14]->NXM_NX_TUN_METADATA0[16..30],output:1
table=32, priority=100,reg15=0x8000,metadata=0x4 actions=load:0x4->NXM_NX_TUN_ID[0..23],set_field:0x8000->tun_metadata0,move:NXM_NX_REG14[0..14]->NXM_NX_TUN_METADATA0[16..30],output:1,resubmit(,33)
table=32, priority=0 actions=resubmit(,33)
```

#### table 33

广播包发到不同的端口上去
本机逻辑目的端口, 转换为本机物理端口?(做连接跟踪使用)
=> 最终发给哪个接口, 还是根据reg15逻辑目的端口值
```
table=33, priority=100,reg15=0x2,metadata=0x4 actions=load:0x1->NXM_NX_REG13[],load:0x3->NXM_NX_REG11[],load:0x2->NXM_NX_REG12[],resubmit(,34)
table=33, priority=100,reg15=0x8000,metadata=0x4 actions=load:0x1->NXM_NX_REG13[],load:0x2->NXM_NX_REG15[],resubmit(,34),load:0x8000->NXM_NX_REG15[]

```

#### table 34

回环包丢弃
```
table=34, priority=100,reg10=0/0x1,reg14=0x2,reg15=0x2,metadata=0x4 actions=drop
table=34, priority=0 actions=load:0->NXM_NX_REG0[],load:0->NXM_NX_REG1[],load:0->NXM_NX_REG2[],load:0->NXM_NX_REG3[],load:0->NXM_NX_REG4[],load:0->NXM_NX_REG5[],load:0->NXM_NX_REG6[],load:0->NXM_NX_REG7[],load:0->NXM_NX_REG8[],load:0->NXM_NX_REG9[],resubmit(,40)

```

#### table 40

OFTABLE_LOG_EGRESS_PIPELINE
egress出口流量流水线？

又是icmp协议?
```
table=40, priority=110,icmp6,metadata=0x4,ipv6_src=fe80::/10,icmp_type=132 actions=resubmit(,41)
table=40, priority=110,icmp6,metadata=0x4,ipv6_src=fe80::/10,icmp_type=130 actions=resubmit(,41)
table=40, priority=110,icmp6,metadata=0x4,ipv6_src=fe80::/10,icmp_type=131 actions=resubmit(,41)
table=40, priority=110,icmp6,metadata=0x4,nw_ttl=255,icmp_type=136,icmp_code=0 actions=resubmit(,41)
table=40, priority=110,icmp6,metadata=0x4,nw_ttl=255,icmp_type=135,icmp_code=0 actions=resubmit(,41)
table=40, priority=110,icmp6,metadata=0x4,nw_ttl=255,icmp_type=133,icmp_code=0 actions=resubmit(,41)
table=40, priority=110,icmp6,metadata=0x4,nw_ttl=255,icmp_type=134,icmp_code=0 actions=resubmit(,41)
table=40, priority=110,icmp6,metadata=0x4,ipv6_dst=ff02::16,icmp_type=143 actions=resubmit(,41)
table=40, priority=0,metadata=0x4 actions=resubmit(,41)
```

#### table 41

```
table=41, priority=0,metadata=0x4 actions=resubmit(,42)
```

#### table 42

```
table=42, priority=100,ipv6,reg0=0x1/0x1,metadata=0x4 actions=ct(table=43,zone=NXM_NX_REG13[0..15])
table=42, priority=100,ip,reg0=0x1/0x1,metadata=0x4 actions=ct(table=43,zone=NXM_NX_REG13[0..15])
table=42, priority=0,metadata=0x4 actions=resubmit(,43)
```

#### table 43-46

暂没用到
```
table=43, priority=0,metadata=0x4 actions=resubmit(,44)
table=44, priority=0,metadata=0x4 actions=resubmit(,45)
table=45, priority=0,metadata=0x4 actions=resubmit(,46)
table=46, priority=0,metadata=0x4 actions=resubmit(,47)
```

#### table 47

连接跟踪?
```
table=47, priority=100,ip,reg0=0x2/0x2,metadata=0x4 actions=ct(commit,zone=NXM_NX_REG13[0..15],exec(load:0->NXM_NX_CT_LABEL[0])),resubmit(,48)
table=47, priority=100,ipv6,reg0=0x2/0x2,metadata=0x4 actions=ct(commit,zone=NXM_NX_REG13[0..15],exec(load:0->NXM_NX_CT_LABEL[0])),resubmit(,48)
table=47, priority=100,ipv6,reg0=0x4/0x4,metadata=0x4 actions=ct(table=48,zone=NXM_NX_REG13[0..15],nat)
table=47, priority=100,ip,reg0=0x4/0x4,metadata=0x4 actions=ct(table=48,zone=NXM_NX_REG13[0..15],nat)
table=47, priority=0,metadata=0x4 actions=resubmit(,48)
```

#### table 48

```
table=48, priority=0,metadata=0x4 actions=resubmit(,49)
```

#### table 49

```
table=49, priority=100,metadata=0x4,dl_dst=01:00:00:00:00:00/01:00:00:00:00:00 actions=resubmit(,64)
table=49, priority=50,reg15=0x2,metadata=0x4,dl_dst=02:ac:10:ff:00:22 actions=resubmit(,64)
```

#### table 64

```
table=64, priority=100,reg10=0x1/0x1,reg15=0x2,metadata=0x4 actions=push:NXM_OF_IN_PORT[],load:0xffff->NXM_OF_IN_PORT[],resubmit(,65),pop:NXM_OF_IN_PORT[]
table=64, priority=0 actions=resubmit(,65)
```

#### table 65

发数据包给虚拟机接口
```
table=65, priority=100,reg15=0x2,metadata=0x4 actions=output:2
```

本宿主机新增了一个二层网络的端口，这里关键会多一个流表
其中reg15表示二层目的端口port
```
table=65, priority=100,reg15=0x3,metadata=0x4 actions=output:5
```

## FAQ

#### OFPT_ERROR (xid=0x8): NXFMFC_INVALID_TLV_FIELD

报错 OFPT_ERROR (xid=0x8): NXFMFC_INVALID_TLV_FIELD => 根据这个简单的关键字, 没搜到什么资料
move:NXM_NX_TUN_METADATA0[16..30]->NXM_NX_REG14[0..14],
move:NXM_NX_TUN_METADATA0[0..15]->NXM_NX_REG15[0..15],
　上述字段参考: http://www.openvswitch.org/support/dist-docs/ovs-fields.7.txt
有一些测试数据

move:NXM_NX_TUN_ID[0..15]->NXM_NX_REG15[0..15]
使用这个就报错: move:NXM_NX_TUN_METADATA0[0..15]
#if TUN_METADATA_NUM_OPTS == 64 ???
https://github.com/openvswitch/ovs/blob/master/include/openvswitch/meta-flow.h

https://pkg.go.dev/antrea.io/libOpenflow/openflow13
NXM_NX_TUN_METADATA0 = 40  /* nicira extension: tun_metadata, for Geneve header variable data */


https://manpages.debian.org/unstable/openvswitch-common/ovs-fields.7.en.html
最终使用这个命令解决
```
ovs-ofctl add-tlv-map br-int "{class=0x102,type=0,len=4}->tun_metadata0"
ovs-ofctl del-tlv-map br-int # 执行失败?
ovs-ofctl dump-tlv-map br-int
```

```
ovs-ofctl dump-tlv-map br-int
NXT_TLV_TABLE_REPLY (xid=0x2):
 max option space=256 max fields=64
 allocated option space=4

 mapping table:
  class  type  length  match field
 ------  ----  ------  --------------
  0x102  0x80       4  tun_metadata0
```

## 参考资料

https://sq.sf.163.com/blog/article/220308584666034176
https://cntofu.com/book/77/vxlan_mode/compute_node/br-tun.md
https://www.xjimmy.com/openstack-5min-149.html

* [深入理解 Neutron -- OpenStack 网络实现：VXLAN 模式](https://blog.csdn.net/qq_15437629/article/details/78702829)

* [(好)ovs流表规则字段文档](http://www.openvswitch.org/support/dist-docs/ovs-fields.7.txt)

* [(好)ovn-controller转换流表](https://www.jianshu.com/p/1ce3ffdc3e5e)
