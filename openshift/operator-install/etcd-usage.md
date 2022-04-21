# etcd operator使用

关键字《etcd operator原理》

对于普通用户来说，如果要在 k8s 集群中部署一个高可用的 etcd 集群，那么不仅要了解其相关的配置，同时又需要特定的 etcd 专业知识才能完成维护仲裁，重新配置集群成员，创建备份，处理灾难恢复等等繁琐的事件。

而在 operator 这一类拓展服务的协助下，我们就可以使用简单易懂的 YAML 文件(同理参考 Deployment)来声明式的配置，创建和管理我们的 etcd 集群，下面我们就来一同了解下 etcd-operator 这个服务的架构以及它所包含的一些功能。

![](https://static001.infoq.cn/resource/image/2c/17/2c7d85f70680629e0ab05470463ed917.png)
