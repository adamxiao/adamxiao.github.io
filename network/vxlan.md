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

## 概念

rfc7348介绍:
> Virtual eXtensible Local Area Network (VXLAN): A Framework
   for Overlaying Virtualized Layer 2 Networks over Layer 3 Networks

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
