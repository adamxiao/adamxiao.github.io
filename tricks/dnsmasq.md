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
