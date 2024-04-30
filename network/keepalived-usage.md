# keepalived使用

## 部署运行keepalived容器

#### keepalived容器制作

我已经制作好了，这里说明一下怎么做这个容器的，
参考[sealyun](https://cloud.tencent.com/developer/article/1472255)的容器制作，比较简单

```dockerfile
#FROM alpine:latest
FROM hub.iefcu.cn/public/alpine:latest

RUN apk --no-cache add keepalived

#VOLUME ["/etc/keepalived"]

CMD ["keepalived", "-n","--all", "-d", "-D",  "-f", "/etc/keepalived/keepalived.conf"]
```

构建多架构arm64和amd64的keepalived容器
```bash
docker buildx build \
    --build-arg http_proxy=http://proxy.iefcu.cn:20172 \
    --build-arg https_proxy=http://proxy.iefcu.cn:20172 \
    --build-arg no_proxy=yumrepo.unikylin.com.cn,192.0.0.0/8 \
    --platform=linux/arm64,linux/amd64 \
    -t hub.iefcu.cn/xiaoyun/keepalived . --push
```

#### 运行keepalived容器

```bash
sudo mkdir -p /etc/keepalived
# generate /etc/keepalived/keepalived.conf

# openshift 环境，为什么不需要处理selinux的问题呢？
# unconfined_u:object_r:etc_t:s0 keepalived.conf
sudo podman run -d --name keepalived \
    --net host --cap-add=NET_ADMIN \
    --cap-add=NET_BROADCAST \
    --cap-add=NET_RAW \
    -v /etc/keepalived/keepalived.conf:/etc/keepalived/keepalived.conf \
    hub.iefcu.cn/xiaoyun/keepalived

sudo podman generate systemd \
    --new --name keepalived \
    > /etc/systemd/system/kcp-keepalived.service
sudo systemctl enable kcp-keepalived
```

keepalived配置文件示例，需要修改一些参数：

* 修改interface参数，选择一个接口提供vip服务
* 修改vip地址
* 修改virtual_router_id，不同的vrrp服务，router id不能一样


主keepalived配置文件如下
```conf
vrrp_instance  VI_1 {
  state  MASTER
  interface  enp3s0
  virtual_router_id  100
  priority  100
  advert_int  1
  authentication {
      auth_type  PASS
      auth_pass  1qazXSW@
  }
  virtual_ipaddress {
      10.90.3.26
  }
}
```

备keepalived配置文件如下
```conf
vrrp_instance  VI_1 {
  state  BACKUP
  interface  enp3s0
  virtual_router_id  100
  priority  90
  advert_int  1
  authentication {
      auth_type  PASS
      auth_pass  1qazXSW@
  }
  virtual_ipaddress {
      10.90.3.26
  }
}
```

vip验证，ping 10.90.3.26，停止主keepalived容器，继续ping 10.90.3.26

#### 配置检查脚本

在Keepalived的配置文件中，我们可以指定Keepalived监控的网络接口，当系统或网络出现问题时就会进行主备切换。但是，很多时候我们需要对集群中特定的服务进行监控，但服务发生故障时就进行主备切换，此时只监控网络接口就无法满足我们的需求。Keepalived提供了vrrp_script调用自定义脚本的方式满足了我们的需求。

https://www.cnblogs.com/yu2006070-01/p/10386772.html
https://www.cnblogs.com/arjenlee/p/9258188.html

* script：调用shell命令或脚本
* interval：定义执行命令或脚本的时间间隔，单位秒
* fall：定义检测失败的最大次数，如设置为2表示当请求失败两次时就认为节点资源故障
* rise：定义请求成功的次数，如设置为1表示当进行一次请求成功后就认为节点资源恢复正常
* vrrp_instance中的track_script：调用vrrp_script使之生效

```
vrrp_script check_dns {
  script "killall -0 ksvd-dbmond"
  #script ".../check_dns.sh"
  interval 2
  weight -30
  fall 3
  rise 2
}
vrrp_instance  VI_2 {
  ...
  track_script {
    check_dns
  }
}
```

check_dns.sh
```
#!/bin/bash

count=`docker ps |grep dns|wc -l`
if [ $count -gt 0 ];then
    exit 0;
else
    exit 1;
fi
```

## keepalived原理

https://blog.csdn.net/jiajiren11/article/details/81563091
看到这里我们可以知道keepalived是怎么工作的，通过vrrp协议做主备之间的心跳，当发生切换备获得浮动IP时，发送ARP包告诉其他机器现在VIP对应的mac地址已经变成了备机的网卡的mac地址。这时如果有新的机器要和VIP通信时，找到的就是备机，从而实现的高可用。

tcpdump -i ethx0 -n vrrp

Receive advertisement timeout
=> 这个时间是多少?

[Keepalived的高可用基石 - VRRP协议](https://bugwz.com/2020/06/20/keepalived-vrrp)
备份状态(Backup)：处于该状态下的设备接收Master发送的VRRP通告报文，判断Master是否正常。
如果一定时间间隔没有收到VRRP通告报文，即Master_Down_Interval（Master_Down_Interval = 3 * Advertisement_Interval + Skew_time 超时，则判断为Master故障。

2.4.1、状态机
初始状态(Initialize)：该状态下VRRP处于不可用的状态，在此状态下设备不会对VRRP报文做任何处理，通常刚配置VRRP时或设备检测到故障时会进入该状态。收到接口startup（启动）的状态，如果设备的优先级为255（表示该设备为虚拟路由器IP地址拥有者），则直接成为Master设备。如果设备的优先级小于255，则会先切换到Backup状态。

活动状态(Master)：处于该状态下的设备为Master设备，Master设备会做如下工作：
- 定时发送VRRP通告报文，时间间隔为Advertisement_Interval；
- 以虚拟MAC地址相应对虚拟IP地址的ARP请求；
- 转发目的MAC地址为虚拟MAC地址的IP报文；
- 抢占模式下，如果收到比自己优先级大的VRRP报文，或者跟自己优先级相等，且本地接口IP地址小于源端接口IP地址时，则转变为Backup状态；
- 收到Shutdown(关闭)消息后，则立即转变为初始状态(Initialize)；

备份状态(Backup)：处于该状态下的设备接收Master发送的VRRP通告报文，判断Master是否正常。如果一定时间间隔没有收到VRRP通告报文，即Master_Down_Interval（Master_Down_Interval = 3 * Advertisement_Interval + Skew_time 超时，则判断为Master故障。
- 接收Master发送的VRRP通告报文，判断Master是否正常；
- 对虚拟IP的ARP请求不做响应；
- 丢弃目的MAC地址为虚拟路由器MAC地址的IP报文；
- 丢弃目的IP地址为虚拟路由器IP地址的IP报文；
- 如果收到优先级比自己高，或与自己相等的VRRP报文，则重置Master_Down_Interval定时器（不进一步比较IP地址）；
- 如果收到优先级比自己小的VPPR报文，且优先级为0时，（表示原Master设备声明不参与该VRRP组了），定时器时间设置为Skew_time（偏移时间，Skew_time= (256 - priority)/256）；
- 如果收到优先级比自己小的VPPR报文，且优先级不为0时，丢弃该报文，立即转变为Master状态；
- Master_Down_Interval定时器超时，立即转变为Master状态；
- 收到Shutdown（关闭）消息后，则立即转变为初始状态(Initialize)；

关键字《keepalived print stats》
```
sudo kill -s $(keepalived --signum=DATA) $(cat /var/run/keepalived.pid)
cat /tmp/keepalived.data
```

[keepalived的配置解析&安装与爬坑](https://www.cnblogs.com/shuiguizi/p/11172267.html)
=> 虽然指定了从eno2上发的包，但是如果想要给他搞一个假的ip就用他

关键字《keepalived wrong Receive advertisement timeout》

[unexpected state transition when backup node is rebooted, even though nopreempt is set](https://github.com/acassen/keepalived/issues/2209)
TLDR: firewall issue: the rebooting node was blocking incoming icmp packets until the node made an outgoing icmp request
=> 确实，关了防火墙之后，没有这个问题了!!!

VRRP has its own protocol number (at the same level as TCP or UDP) - 112.
```
-A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT
```
Once a VRRP packet has been sent, incoming VRRP adverts will be RELATED
=> 防火墙默认会放通`RELATED` 的VRRP包!

```
cat /proc/net/nf_conntrack | grep -w 112
ipv4     2 unknown  112 596 src=192.168.101.72 dst=192.168.101.71 src=192.168.101.71 dst=192.168.101.72 mark=0 zone=0 use=2
```
新的防火墙规则展示: `nft list ruleset`
```
yum install -y conntrack-tools
conntrack -F # 清除连接跟踪状态
cat /proc/sys/net/netfilter/nf_conntrack_generic_timeout # 默认老化时间可能是10分钟
600
```

https://www.cnblogs.com/wswind/p/13792585.html

关键字《firewall 放通vrrp》

https://www.cnblogs.com/wswind/p/13792585.html
=> firewalld 去除iptables依赖了, centos8的firewalld防火墙底层使用了全新的nftables替代了iptables。
```
firewall-cmd --add-protocol=vrrp --permanent
firewall-cmd --reload
```

关键字《firewall allow vrrp for specific source》
=> 就好像tcpdump 抓112端口，抓不到vrrp的包, 指定vrrp协议才行

https://superuser.com/questions/1415995/allow-vrrp-on-firewall
However, although it runs on top of IP, VRRP does not use a transport protocol and does not have "ports". Rather, it runs alongside TCP/UDP/ICMP and has the IP protocol number 112.

https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/load_balancer_administration/s1-lvs-connect-vsa
```
firewall-cmd --add-rich-rule='rule protocol value="vrrp" accept' --permanent
```

关键字《firewall-cmd allow vrrp for specific ipset》
https://serverfault.com/questions/1097034/keepalived-going-split-brain-when-firewalld-is-running
```
enabled LogDenied=all in /etc/firewalld/firewalld.conf
firewall-cmd --get-log-denied
firewall-cmd --add-rich-rule='rule protocol value="ah" accept' --permanent

dmesg | grep -i REJECT
[   75.108415] "filter_IN_public_REJECT: "IN=ethx0 OUT= MAC=52:54:84:00:0c:bd:52:54:84:00:0c:bc:08:00 SRC=192.168.101.71 DST=192.168.101.72 LEN=40 TOS=0x00 PREC=0xC0 TTL=255 ID=1 PROTO=112
```

## 问题

#### 既然backup会选主，为什么要配置一个master呢?

否则master状态的上来会抢主...

#### 非抢占问题怎么处理?

A,B同时启动后，由于A的优先级较高，因此通过选举会成为master。当A上的业务进程出现问题时，优先级会降低到60。此时B收到优先级比自己低的vrrp广播包时，将切换为master状态。那么当B上的业务出现问题时，优先级降低到50，尽管A的优先级比B的要高，但是由于设置了nopreempt，A不会再抢占成为master状态。

所以，可以在检测脚本中增加杀掉keepalived进程（或者停用keepalived服务）的方式，做到业务进程出现问题时完成主备切换。

#### 怎么查看keepalived状态切换等日志?

先加一个-l参数输出到控制台调试看吧
```
/usr/sbin/keepalived -l -n -d -D -f /etc/keepalived/keepalived.conf
```

#### 防火墙放通vrrp协议通信

https://blog.csdn.net/W_kiven/article/details/123268991

```
--add-protocol=vrrp
firewall-cmd --permanent --add-protocol=vrrp
firewall-cmd --reload

# 临时放通防火墙
firewall-cmd --add-protocol=vrrp
```

检查是否放通了。
```
firewall-cmd --list-services
ssh ...

[ssh_10.60.5.111] root@node6: xiaoyun$firewall-cmd --add-protocol=vrrp
success

firewall-cmd --list-services
ssh ...

firewall-cmd --add-protocol=vrrp
Warning: ALREADY_ENABLED: 'vrrp' already in 'public'
success

firewall-cmd --list-protocols
vrrp
```

FIXME: 每次KSVD升级会还原这个配置文件，导致临时添加的规则失效
/etc/firewalld/zones/public.xml
```
<?xml version="1.0" encoding="utf-8"?>
<zone>
  <short>Public</short>
  <service name="ssh"/>
  ...
  <protocol value="vrrp"/>
</zone>
```

FAQ 执行check失败(容器中遇到的问题。。。)
```
Wed Nov  2 02:15:34 2022: WARNING - script `pidof` resolved by path search to `/bin/pidof`. Please specify full path.
```
