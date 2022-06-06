# 使用ovs流表实现dhcp

创建全新的的ovs环境, 创建br-int桥
```
apt install -y openvswitch-common openvswitch-switch

ovs-vsctl list-br
ovs-vsctl add-br br-int -- set Bridge br-int fail-mode=secure
```

添加一个接口, 对这个接口添加dhcp实现的ovs规则
```
# 手动造一个in_port=5
ovs-vsctl add-port br-int vm1 -- set interface vm1 type=internal
ovs-vsctl add-port br-int vm2 -- set interface vm2 type=internal
ovs-vsctl add-port br-int vm3 -- set interface vm3 type=internal
ovs-vsctl add-port br-int vm4 -- set interface vm4 type=internal
ovs-vsctl add-port br-int vm5 -- set interface vm5 type=internal

ip link set vm5 address 02:ac:10:ff:01:30

ovs-ofctl add-flows br-int dhcp-test.flow
```

ovs流表规则如下:
```
table=0, priority=100,in_port=5 actions=load:0x1->NXM_NX_REG13[],load:0x3->NXM_NX_REG11[],load:0x2->NXM_NX_REG12[],load:0x5->OXM_OF_METADATA[],load:0x1->NXM_NX_REG14[],resubmit(,8)
table=8, priority=50,reg14=0x1,metadata=0x5 actions=resubmit(,9)
table=9, priority=0,metadata=0x5 actions=resubmit(,10)
table=10, priority=0,metadata=0x5 actions=resubmit(,11)
table=11, priority=0,metadata=0x5 actions=resubmit(,12)
table=12, priority=0,metadata=0x5 actions=resubmit(,13)
table=13, priority=0,metadata=0x5 actions=resubmit(,14)
table=14, priority=0,metadata=0x5 actions=resubmit(,15)
table=15, priority=0,metadata=0x5 actions=resubmit(,16)
table=16, priority=0,metadata=0x5 actions=resubmit(,17)
table=17, priority=0,metadata=0x5 actions=resubmit(,18)
table=18, priority=0,metadata=0x5 actions=resubmit(,19)
table=19, priority=0,metadata=0x5 actions=resubmit(,20)
table=20, priority=0,metadata=0x5 actions=resubmit(,21)
table=21, priority=0,metadata=0x5 actions=resubmit(,22)
table=22, priority=100,udp,reg14=0x1,metadata=0x5,dl_src=02:ac:10:ff:01:30,nw_src=0.0.0.0,nw_dst=255.255.255.255,tp_src=68,tp_dst=67 actions=controller(userdata=00.00.00.02.00.00.00.00.00.01.de.10.00.00.00.63.ac.10.ff.82.33.04.00.00.0e.10.01.04.ff.ff.ff.c0.03.04.ac.10.ff.81.36.04.ac.10.ff.81,pause),resubmit(,23)
table=23, priority=100,udp,reg0=0x8/0x8,reg14=0x1,metadata=0x5,dl_src=02:ac:10:ff:01:30,tp_src=68,tp_dst=67 actions=move:NXM_OF_ETH_SRC[]->NXM_OF_ETH_DST[],mod_dl_src:02:ac:10:ff:01:29,mod_nw_src:172.16.255.129,mod_tp_src:67,mod_tp_dst:68,move:NXM_NX_REG14[]->NXM_NX_REG15[],load:0x1->NXM_NX_REG10[0],resubmit(,32)
table=32, priority=0 actions=resubmit(,33)
table=33, priority=100,reg15=0x1,metadata=0x5 actions=load:0x1->NXM_NX_REG13[],load:0x3->NXM_NX_REG11[],load:0x2->NXM_NX_REG12[],resubmit(,34)
table=34, priority=0 actions=load:0->NXM_NX_REG0[],load:0->NXM_NX_REG1[],load:0->NXM_NX_REG2[],load:0->NXM_NX_REG3[],load:0->NXM_NX_REG4[],load:0->NXM_NX_REG5[],load:0->NXM_NX_REG6[],load:0->NXM_NX_REG7[],load:0->NXM_NX_REG8[],load:0->NXM_NX_REG9[],resubmit(,40)
table=40, priority=0,metadata=0x5 actions=resubmit(,41)
table=41, priority=0,metadata=0x5 actions=resubmit(,42)
table=42, priority=0,metadata=0x5 actions=resubmit(,43)
table=43, priority=0,metadata=0x5 actions=resubmit(,44)
table=44, priority=34000,udp,reg15=0x1,metadata=0x5,dl_src=02:ac:10:ff:01:29,nw_src=172.16.255.129,tp_src=67,tp_dst=68 actions=resubmit(,45)
table=45, priority=0,metadata=0x5 actions=resubmit(,46)
table=46, priority=0,metadata=0x5 actions=resubmit(,47)
table=47, priority=0,metadata=0x5 actions=resubmit(,48)
table=48, priority=0,metadata=0x5 actions=resubmit(,49)
table=49, priority=50,reg15=0x1,metadata=0x5 actions=resubmit(,64)
table=64, priority=100,reg10=0x1/0x1,reg15=0x1,metadata=0x5 actions=push:NXM_OF_IN_PORT[],load:0xffff->NXM_OF_IN_PORT[],resubmit(,65),pop:NXM_OF_IN_PORT[]
table=65, priority=100,reg15=0x1,metadata=0x5 actions=output:5
```

使用dhclient验证dhcp效果
```bash
ip netns add vm5
ip link set vm5 address 02:ac:10:ff:01:30
ip link set vm5 netns vm5

ip netns exec vm5 dhclient vm5
ip netns exec vm5 ip addr show vm5
ip netns exec vm5 ip route show
```


[Open vSwitch---流表控制主机数据转发实验（二）](https://blog.csdn.net/weixin_40042248/article/details/112913415)
动作为controller
以packet-in消息上送给控制器

ovs-ofctl add-flow br0 in_port=1,actions=controller


https://docs.openvswitch.org/en/latest/ref/ovs-actions.7/#the-controller-action
controller
Sends the packet and its metadata to an OpenFlow controller or controllers encapsulated in an OpenFlow packet-in message. The separate controller action, described below, provides more options for output to a controller.


https://www.clear.rice.edu/comp529/www/papers/tutorial_4.pdf
SDN and OpenFlow A Tutorial

https://www.sciencedirect.com/topics/computer-science/openflow-controller
Openflow Controller
=> 存在controller这个角色，组件，可以尝试自己构建验证？
=> openflow结构图中就有controller的角色

https://wiki.onosproject.org/display/ONOS/OpenFlow+1.5+Implementation


[(好)OpenvSwitch/OpenFlow 架构解析与实践案例](https://www.cnblogs.com/jmilkfan-fanguiju/p/10589725.html)
=> 尝试安装验证controller

strace发现ovn-controller算是一个controller, 收到并处理了ovs的dhcp包
pinctrl_handle_put_dhcp_opts => 代码实现?


## ryu调研使用

[ryu实例---自学习交换机](https://blog.csdn.net/weixin_40042248/article/details/115973663)
=> 非常符合我下一步验证计划
=> 尝试一个最简单的controller?

ImportError: cannot import name 'ALREADY_HANDLED' from 'eventlet.wsgi' (/usr/local/lib/python3.8/dist-packages/eventlet/wsgi.py)

https://stackoverflow.com/questions/67409452/gunicorn-importerror-cannot-import-name-already-handled-from-eventlet-wsgi
pip install eventlet==0.33.0 


关键字《ryu安装使用入门》

http://www.muzixing.com/pages/2014/09/20/ryuru-men-jiao-cheng.html

pip install ryu

ryu-manager simple_switch.py

然后set-controller
关键字《ovs配置使用ryu》

ovs-vsctl set-controller br-int tcp:127.0.0.1:6653

https://ryu.readthedocs.io/en/latest/library_packet_ref/packet_dhcp.html
ryu DHCP packet parser/serializer

### 其他资料

OVS+RYU控制器实现源IP地址和源端口转换
https://blog.csdn.net/weixin_44713619/article/details/110520650
