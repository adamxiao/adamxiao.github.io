# dnsmasq使用入门

## 配置dhcp服务

```
# dhcp白名单机制
dhcp-ignore=tag:!known

# 固定分配ip地址
dhcp-host=52:54:84:00:05:8a,10.90.3.20,bootstrap,set:known
# 或者不固定ip地址
dhcp-host=52:54:84:00:05:8a,set:known

#log-dhcp
# 可以配置多段ip地址分配
dhcp-range=subnet3_20,10.90.3.20,10.90.3.36,255.255.255.0,8h
dhcp-option=subnet3_20,3,10.90.3.1
dhcp-option=subnet3_20,6,10.90.3.38,192.168.168.168
dhcp-option=subnet3_20,option:domain-search,iefcu.cn
```

#### 启动dnsmasq容器服务

docker创建macvlan网络
```bash
docker network create -d macvlan \
  --subnet=10.20.1.1/20 \
  --gateway=10.20.1.1 -o parent=enp2s0 macvlan-enp2s0
```

启动dnsmasq服务
```bash
docker run \
    --name dnsmasq \
    --privileged \
    -d \
    --network kylin-macvlan-net \
    --ip 10.90.2.190 \
    -v /data/dnsmasq/dnsmasq.conf:/etc/dnsmasq.conf \
    --log-opt "max-size=100m" \
    -e "HTTP_USER=adam" \
    -e "HTTP_PASS=6251965" \
    --restart always \
    jpillora/dnsmasq
```

或者映射目录进去, 但是配置文件一定需要一个dnsmasq.conf
```
docker run ... \
    -v $HOME/Desktop/dnsmasq.d:/etc/dnsmasq.d \
    --entrypoint \
    "webproc" \
    jpillora/dnsmasq \
    "--config" "/etc/dnsmasq.d/dnsmasq.conf" "--" "dnsmasq" "--no-daemon" "--conf-file=/etc/dnsmasq.d/dnsmasq.conf"
```

## dhcp proxy

dhcp relay和dhcp proxy还是不一样的

https://blog.51cto.com/longlei/2065967
```
dhcp-range=[tag:<tag>[,tag:<tag>],][set:<tag>,]<start-addr>[,<end-addr>][,<mode>][,<netmask>[,<broadcast>]][,<lease time>]
```

- 设置 DHCP 地址池，同时启用 DHCP 功能。
- IPv4 <mode> 可指定为 static|proxy ，当 <mode> 指定为 static 时，
- 需用 dhcp-host 手动分配地址池中的 IP 地址。
- 当 <mode> 指定为 proxy 时，为指定的地址池提供 DHCP 代理。

#### 概念

https://zhidao.baidu.com/question/208855417.html

如果DHCP客户机与DHCP服务器在同一个物理网段，则客户机可以正确地获得动态分配的ip地址。如果不在同一个物理网段，则需要DCHP Relay Agent(中继代理)。用DHCP Relay代理可以去掉在每个物理的网段都要有DHCP服务器的必要,它可以传递消息到不在同一个物理子网的DHCP服务器，也可以将服务器的消息传回给不在同一个物理子网的DHCP客户机。

#### 工作原理

https://support.huawei.com/enterprise/zh/doc/EDOC1100198436/be771137

#### 配置示例

https://juejin.cn/s/dnsmasq%20dhcp%20relay%20example
```
# 监听所有接口
interface=

# 指定 DHCP 中继地址
dhcp-relay=192.168.1.1,192.168.2.1

# 指定 DHCP 服务器的 IP 地址和 DHCP 消息类型
dhcp-option=option:server-identifier,192.168.1.1,192.168.2.1
dhcp-option=option:relay,192.168.1.1,192.168.2.1
```

## FAQ

1. dns上游请求有问题，导致dnsmasq有问题, 连本地定义的dns都不处理!
  暂不清楚原因，更换上游dns服务器解决

#### ping很久10s才超时返回

发现ping不仅解析了域名，而且还通过ip反响查询域名了! `in-addr.arpa`
[ping首包慢的问题（及icmp对应关系）](https://blog.51cto.com/xzq2000/2402249)(关键字《ping 响应很慢》就搜到这篇文章了)

原因:
* 因为dnsmasq解析dns反向查询超时不返回导致

思路:
* 禁用掉dnsmasq的dns反向查询功能 => 未查到相关资料
  关键字《dnsmasq disable PTR queries》 => no
  关键字《dnsmasq disable reverse DNS queries》
  《prevent reverse DNS queries 》
* ping不使用dns反响查询功能
  [ping 反向解析](https://www.csdn.net/tags/MtjaEgxsMzY5NDgtYmxvZwO0O0OO0O0O.html)
  ping -n即可

使用dig命令可以手动执行dns反向查询
```
dig 域名  
dig ftp6.wslog.chinanetcenter.com
dig ftp6.wslog.chinanetcenter.com +short
dig ftp6.wslog.chinanetcenter.com  @8.8.8.8 
dig反向解析：
dig -x 113.107.44.229  ip反向解析
dig  229.44.107.113.in-addr.arpa ptr
```

解决方法:
加一个反向dns记录: https://www.cnblogs.com/saneri/p/14141397.html
https://wener.me/notes/service/dns/dnsmasq
```
ptr-record=110.100.168.192.in-addr.arpa,www.xxx-host.com
```

#### nat环境下tftp超时

x86主机下加载nf_nat_tftp模块即可
```
modprobe nf_nat_tftp
```

arm主机dmesg报错: 出于安全原因，默认的自动分配助手已关闭，并且未找到基于CT的防火墙规则。请改用iptables CT目标来附加助手。
通过如下办法使能tftp功能：
```
iptables -t raw -I PREROUTING -p udp --dport 69 -j CT --helper tftp
```
通过今一步分析，发现arm平台上/proc/sys/net/netfilter/nf_conntrack_helper 为0, 所以tftp不通。
发现x86平台上/proc/sys/net/netfilter/nf_conntrack_helper 为1, 所以tftp通。

配置 /etc/modprobe.d/nf_conntrack.conf
```
options nf_conntrack nf_conntrack_helper=1
```

自动加载nf_nat_tftp模块, 配置 /etc/modules-load.d/tftp.conf
```
nf_nat_tftp
```
