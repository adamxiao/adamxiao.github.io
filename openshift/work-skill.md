# 工作技能

## 技能

58、简述Kubernetes如何保证集群的安全性？

77、简述Kubernetes Worker节点加入集群的过程？
通常需要对Worker节点进行扩容，从而将应用系统进行水平扩展。主要过程如下：

* 1、在该Node上安装Docker、kubelet和kube-proxy服务；
* 2、然后配置kubelet和kubeproxy的启动参数，将Master URL指定为当前Kubernetes集群Master的地址，最后启动这些服务；
* 3、通过kubelet默认的自动注册机制，新的Worker将会自动加入现有的Kubernetes集群中；
* 4、Kubernetes Master在接受了新Worker的注册之后，会自动将其纳入当前集群的调度范围。

=> 没配置的话会怎么样? 而且动态的怎么处理.
78、简述Kubernetes Pod如何实现对节点的资源控制？
Kubernetes集群里的节点提供的资源主要是计算资源，计算资源是可计量的能被申请、分配和使用的基础资源。当前Kubernetes集群中的计算资源主要包括CPU、GPU及Memory。CPU与Memory是被Pod使用的，因此在配置Pod时可以通过参数CPU Request及Memory Request为其中的每个容器指定所需使用的CPU与Memory量，Kubernetes会根据Request的值去查找有足够资源的Node来调度此Pod。

通常，一个程序所使用的CPU与Memory是一个动态的量，确切地说，是一个范围，跟它的负载密切相关：负载增加时，CPU和Memory的使用量也会增加。


42、简述Kubernetes deployment升级过程？
* 初始创建Deployment时，系统创建了一个ReplicaSet，并按用户的需求创建了对应数量的Pod副本。
* 当更新Deployment时，系统创建了一个新的ReplicaSet，并将其副本数量扩展到1，然后将旧ReplicaSet缩减为2。
* 之后，系统继续按照相同的更新策略对新旧两个ReplicaSet进行逐个调整。
* 最后，新的ReplicaSet运行了对应个新版本Pod副本，旧的ReplicaSet副本数量则缩减为0。
=> 这里有更新策略的区别

49、简述Kubernetes外部如何访问集群内的服务？
对于Kubernetes，集群外的客户端默认情况，无法通过Pod的IP地址或者Service的虚拟IP地址:虚拟端口号进行访问。通常可以通过以下方式进行访问Kubernetes集群内的服务：

* 映射Pod到物理机：将Pod端口号映射到宿主机，即在Pod中采用hostPort方式，以使客户端应用能够通过物理机访问容器应用。
* 映射Service到物理机：将Service端口号映射到宿主机，即在Service中采用nodePort方式，以使客户端应用能够通过物理机访问容器应用。
* 映射Sercie到LoadBalancer：通过设置LoadBalancer映射到云服务商提供的LoadBalancer地址。这种用法仅用于在公有云服务提供商的云平台上设置Service的场景。
=> traefik基于路径的ingress?

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
