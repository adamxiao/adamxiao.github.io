# vxlan概念了解使用

问题:
* 点对点隧道, 谁作为这个二层虚拟机交换机的角色?
   应该是SDN，自由组装?

需求:
* 1.网口管理: 数据通信，物理出口?
* 2.vxlan
* 3.dhcp
* 4.三层路由器(安全组,端口组)
* 5.浮动ip(dnat,snat)

TODO:
* [基于NEUTRON VXLAN网络实践01-VPC实现](https://www.jianshu.com/p/665866054b0e)
使用ovs实现的vxlan实践

## 概念

rfc7348介绍:
> Virtual eXtensible Local Area Network (VXLAN): A Framework
   for Overlaying Virtualized Layer 2 Networks over Layer 3 Networks


[深入浅出云计算VPC网络之VXLAN](https://cloud.tencent.com/developer/article/1647354)
* 1.Overlay和Underlay网络：物理网络作为Underlay网络，在其上构建出 虚拟的二层或三层网络，即Overlay网络。OverLay是基于隧道实现的，流量需要跑在UnderLay之上。
* 2.NVE:实现网络虚拟化的网络实体，报文经过NVE封装转换后，NVE间就可基于三层网络建立二层虚拟化网络。
* 3.VTEP隧道终点：封装在NVE实体中，主要用于VXLAN报文的封装和解装，一个VTEP地址对应一个VXLAN隧道,VXLAN报文中的源IP地址为本节点的VTEP地址，目的ip地址为对端VTEP地址。
* 4.VNI：网络标识，主要用于区分VXLAN段，租户和VNI映射。

验证vxlan单播隧道(Linux Network Kernel实现)
```bash
#在master虚拟机中执行
sudo ip link add vxlan1 type vxlan id 88 remote 192.168.88.8 dstport 4789 dev eth1
sudo ip link set vxlan1 up
sudo ip addr add 10.0.0.106/24 dev vxlan1

#下面的两条命令到是我了查看配置
#路由表多了vxlan1，并通过vxlan1转发
[vagrant@master ~]$ ip route | grep vxlan1
10.0.0.0/24 dev vxlan1 proto kernel scope link src 10.0.0.106
#fdb多了vxlan1,dst的vtep是192.168.88.9
[vagrant@master ~]$ bridge fdb | grep vxlan1
00:00:00:00:00:00 dev dev vxlan1 dst 192.168.88.9 via eth1 self permanent

#在slave1虚拟机中执行
sudo ip link add vxlan1 type vxlan id 88 remote 192.168.88.9 dstport 4789 dev eth1
sudo ip link set vxlan1 up
sudo ip addr add 10.0.0.107/24 dev vxlan1
```

查看接口vxlan信息
```bash
[root@localhost ~]# ip -s -d a s | grep vxlan
3: vxlan1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1450 qdisc noqueue state UNKNOWN group default qlen 1000
    vxlan id 88 remote 192.168.100.115 dev eth0 srcport 0 0 dstport 4789 ageing 300 noudpcsum noudp6zerocsumtx noudp6zerocsumrx numtxqueues 1 numrxqueues 1 gso_max_size 65536 gso_max_segs 65535
    inet 10.0.0.106/24 scope global vxlan1
```

## 应用

[华为 - VXLAN应用](https://support.huawei.com/enterprise/zh/doc/EDOC1000173014/a021a76d)

* 虚拟机迁移

## 其他资料

* ZStack的VPC特性详解及实战_凌云时刻的博客-CSDN博客
https://blog.csdn.net/bjchenxu/article/details/107036233

* SANGFOR_aCloud_网络功能虚拟化之虚拟交换机 - 深信服社区
https://bbs.sangfor.com.cn/plugin.php?id=sangfor_databases:index&mod=viewdatabase&tid=38982&highlight=

* openstack-- neutron 二/三层网络实现探究 - Michael_Tong唐唐 - 博客园
https://www.cnblogs.com/tcicy/p/10123281.html#:~:text=flat%E5%9E%8B%E7%BD%91%E7%BB%9C%E6%98%AF%E5%9C%A8local,%E5%9E%8B%E7%BD%91%E7%BB%9C%E7%9A%84%E5%9F%BA%E7%A1%80%E4%B8%8A%E5%AE%9E%E7%8E%B0%E4%B8%8D%E5%90%8C%E5%AE%BF%E4%B8%BB%E6%9C%BA%E7%9A%84instance%E4%B9%8B%E9%97%B4%E4%BA%8C%E5%B1%82%E4%BA%92%E8%81%94%E3%80%82

* L3网络（L3 Network） — zstack 0.6 文档
https://zstack-cn.readthedocs.io/zh/latest/userManual/l3Network.html

* ZStack--网络模型1：L2和L3网络 - 知乎
https://zhuanlan.zhihu.com/p/58889582

* 【ZStack学堂】第三季：ZStack VPC 网络实践_哔哩哔哩_bilibili
https://www.bilibili.com/video/av99307858

* 01VPC的概念介绍_哔哩哔哩_bilibili
https://www.bilibili.com/video/BV1Rk4y1r7q2/?spm_id_from=333.788.recommend_more_video.2

## 参考文档

* [华为 - 什么是VXLAN](https://support.huawei.com/enterprise/zh/doc/EDOC1100087027)
