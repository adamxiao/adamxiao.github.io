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
