# k8s原理

controller manager

关键字《controller manager作用》


[(好)解读 kubernetes Controller Manager 工作原理](https://blog.yingchi.io/posts/2020/7/k8s-cm-informer.html)

client-go
Controller Manager 中一个很关键的部分就是 client-go，client-go 在 controller manager 中起到向 controllers 进行事件分发的作用。目前 client-go 已经被单独抽取出来成为一个项目了，除了在 kubernetes 中经常被用到，在 kubernetes 的二次开发过程中会经常用到 client-go，比如可以通过 client-go 开发自定义 controller。

client-go 包中一个非常核心的工具就是 informer，informer 可以让与 kube-apiserver 的交互更加优雅。

informer 主要功能可以概括为两点：
* 资源数据缓存功能，缓解对 kube-apiserver 的访问压力；
* 资源事件分发，触发事先注册好的 ResourceEventHandler；

[Kubernetes核心原理（二）之Controller Manager](https://blog.csdn.net/huwh_/article/details/75675761)

Controller Manager作为集群内部的管理控制中心，负责集群内的Node、Pod副本、服务端点（Endpoint）、命名空间（Namespace）、服务账号（ServiceAccount）、资源定额（ResourceQuota）的管理，当某个Node意外宕机时，Controller Manager会及时发现并执行自动化修复流程，确保集群始终处于预期的工作状态。

每个Controller通过API Server提供的接口实时监控整个集群的每个资源对象的当前状态，当发生各种故障导致系统状态发生变化时，会尝试将系统状态修复到“期望状态”。

2. Replication Controller
为了区分，资源对象Replication Controller简称RC,而本文是指Controller Manager中的Replication Controller，称为副本控制器。副本控制器的作用即保证集群中一个RC所关联的Pod副本数始终保持预设值。

只有当Pod的重启策略是Always的时候（RestartPolicy=Always），副本控制器才会管理该Pod的操作（创建、销毁、重启等）。
RC中的Pod模板就像一个模具，模具制造出来的东西一旦离开模具，它们之间就再没关系了。一旦Pod被创建，无论模板如何变化，也不会影响到已经创建的Pod。
Pod可以通过修改label来脱离RC的管控，该方法可以用于将Pod从集群中迁移，数据修复等调试。
删除一个RC不会影响它所创建的Pod，如果要删除Pod需要将RC的副本数属性设置为0。
不要越过RC创建Pod，因为RC可以实现自动化控制Pod，提高容灾能力。

2.1. Replication Controller的职责
确保集群中有且仅有N个Pod实例，N是RC中定义的Pod副本数量。
通过调整RC中的spec.replicas属性值来实现系统扩容或缩容。
通过改变RC中的Pod模板来实现系统的滚动升级。

