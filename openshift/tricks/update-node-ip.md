# 修改节点ip地址

可以有两种方法修改：
* 1.新增ip地址，保留原有ip地址
  这种方法已经验证过，可以不重启就新增ip地址等信息
* 2.弃用旧ip地址, 配置新ip地址
  待验证，可能有问题

## 配置接口新增ip地址

TODO: 问题
* 1.网关的修改?
* 2.xxx

#### 修改nmcli配置文件

网络配置文件是/etc/NetworkManager/system-connections/enp3s0.nmconnection
(注意名称可能是其他的)

新增ip地址配置，这样可以永久生效
```bash
address2=10.90.2.92/24
```

要想立即生效，则需要即时配置(注意网络连接可能是其他名称)
```bash
nmcli connection modify enp3s0 +ipv4.addresses 10.90.2.92/24
# 然后还要再up connection才行吧？
```

修改网关地址，可以把之前的网关取消掉，新的地址配置上网关，重启生效吧。
```
address1=10.90.3.35/24
address2=10.90.2.94/24,10.90.2.1
```

## 修改接口ip地址

修改步骤：
* 1.先保留新旧两个ip地址，先把dns给修改了验证，发现问题再修正问题。
  查看journel日志，发现部分逻辑依赖旧的ip地址，修改。
  /etc/systemd/system/crio.service.d/20-nodenet.conf
  /etc/systemd/system/kubelet.service.d/20-nodenet.conf
* 2.发现kube-apiserver容器运行失败，报错连接etcd失败
  使用crictl查看apiserver的地址得到的，还连接了旧的ip地址。
* 3.发现etcd-ensure-env-vars容器报错，还使用了旧的ip地址。
  Expected node IP to be 10.90.2.94 got 10.90.3.35
![](2022-03-14-17-28-33.png)
/etc/kubernetes/static-pod-resources/etcd-pod-2/etcd-pod.yaml
先修改这个文件
/etc/kubernetes/manifests/etcd-pod.yaml
* 4.修改之后重启，基本正常，etcd operator略微有一点问题。
x509: certificate is valid for 10.90.3.35, not 10.90.2.94
![](2022-03-14-18-24-08.png)
* 5.approve csr
* 6. 还是etcd有一点儿问题
sudo crictl logs etcd-health-monitor
x509: certificate is valid for ::1, 10.90.3.35, 127.0.0.1, ::1, not 10.90.2.94". Reconnecting
而且，使用curl -v -k https://10.90.2.94:2379 都失败
(原因是etcd会校验客户端的证书。)
TODO: 关键字《openshift etcd证书更新》

TODO: 目前来说，是有问题的。系统容器启动失败，报错。  

## 旧的笔记，待整理

关键字《openshift 4 change node ip address》
只搜索到了openshift虚拟化节点的ip地址修改
* 1.想到用machine config , 看了一下，可能不是针对单节点的，放弃
* 2.直接使用nmcli修改ip，发现apiserver还是shiyon
* 3.k8s修改节点ip, 据说跟新增节点逻辑一样？（这样最可靠吧？）
那单master节点怎么修改ip呢？
https://www.cnblogs.com/chenjw-note/p/11175250.html
```
k8s集群节点更换ip 或者 k8s集群添加新节点
1.需求情景：机房网络调整，突然要回收我k8s集群上一台node节点机器的ip，并调予新的ip到这台机器上，所以有了k8s集群节点更换ip一说；同时，k8s集群节点更换ip也相当于k8s集群添加新节点，他们的操作流程是一样的。
```

openshift启动顺序总结
先启动kubelet
然后apiserver等etcd控制平面
然后慢慢拉起其他容器。

CentOS7的journalctl日志查看方法
https://www.cnblogs.com/ggzhangxiaochao/p/13953887.html
例如，查看系统本次启动的日志 journalctl -b


以下是发现写了节点ip的地方，也有可能重启就可以了。
* /etc/systemd/system/crio.service.d/20-nodenet.conf
* /etc/systemd/system/kubelet.service.d/20-nodenet.conf

![](2022-03-14-14-20-19.png)

这两个文件都是运行时生成的？
![](2022-03-14-14-20-37.png)

kube-apiserver也是连接旧的ip地址

我手动写一个域名
/etc/hosts
10.90.3.141 master1.kcp4.iefcu.cn

因为kubelet老是报错：node xxx not found
Dec 15 06:59:11 master1.kcp4.iefcu.cn hyperkube[1528]: E1215 06:59:11.159415    1528 kubelet.go:2303] "Error getting node" err="node \"master1.kcp4.iefcu.cn\" not found"