# 工作技能

## 技能

82、简述Kubernetes如何进行优雅的节点关机维护？
由于Kubernetes节点运行大量Pod，因此在进行关机维护之前，建议先使用kubectl drain将该节点的Pod进行驱逐，然后进行关机维护。
=> 直接关机维护会怎么样! pod会丢失一段时间，如果驱逐的话, 可以尽快恢复使用

openshift部署keepalived服务，提供vip服务？(更上层，省去手动修改xx配置文件?)
=> 为了解决上面几种服务发布方式的缺点KubeManager提供了网络出口来为服务访问提供一个高可用IP，提供了四层负载的功能来解决发布非http/https服务的需求。

4层负载均衡?
平台支持四层负载均衡和七层负载均衡。平台提供应用负载均衡基于 Nginx 的反向代理，通过设置固定端口，根据访问域名，监听规则向后端转发流量。应用负载均衡既是一种服务出口，也可以解决多个后端服务之间的流量分配。

《深信服容器云KubeManager测试方案_V1.0》
2.2.部署拓扑与IP规划
2.2.1.HCI & SCP 部署规划示例
使用深信服超融合承载 KubeManager 平台，超融合平台的网络平面分为以下五个网络平面。
管理平面：用于超融合平台管理，虚拟机热迁移、主机间心跳网络都使用该网络平面。
业务平面：虚拟机对外提供业务的网络平面，是平台南北向的通信平面。
VXLAN平面：用于承载虚拟机的东西向流量。
HCI 存储平面：是虚拟存储的通信平面，承载超融合各节点的存储数据通信流量。
PaaS存储平面：是PaaS虚拟机访问虚拟存储的网络平面，业务虚拟机通过该网络平面从虚拟存储中读取/写入数据。

问题:  
* 四层负载均衡与NodePort会不会冲突?

思路:
* 关键字《openshift四层负载均衡》
* openshift网络官方文的档
https://access.redhat.com/documentation/zh-cn/openshift_container_platform/4.9/html/networking/configuring-ipfailover#doc-wrapper

IP 故障转移（IP failover）在一组节点上管理一个虚拟 IP（VIP）地址池。集合中的每个 VIP 都由从集合中选择的节点提供服务。只要单个节点可用，就会提供 VIP。无法将 VIP 显式分发到节点上，因此可能存在没有 VIP 的节点和其他具有多个 VIP 的节点。如果只有一个节点，则所有 VIP 都在其中。
=> 就是使用keepalived实现的


## 参考资料

* [IT运维面试问题总结-LVS、Keepalived、HAProxy、Kubernetes、OpenShift等](https://jishuin.proginn.com/p/763bfbd2ea07)
