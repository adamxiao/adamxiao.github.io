# firewalld 入门

用于实现持久的网络流量规则。
可以动态修改单条规则，动态管理规则集，允许更新规则而不破坏现有会话和连接
使用区域(zone)和服务(service)
默认是拒绝的，需要设置以后才能放行

firewall-cmd --list-all-zones 
/usr/lib/firewalld/zones
/etc/firewalld/zones

firewall-cmd --get-active-zone 

public
  interfaces: eth0
trusted
  sources: 10.20.1.0/20

firewall-cmd --get-default-zones 
firewall-cmd --set-default-zone=trusted

这里注意顺序问题,先匹配到就处理了
firewall-cmd --add-source=10.20.1.0/20 --zone=trusted
firewall-cmd --add-source=10.20.3.0/24 --zone=drop

TODO: zone可以有多个吗？接口对应zone是啥意思
firewall-cmd --get-zone-of-interface=eth0


（2）添加端口/服务。用户可以通过修改配置文件的方式添加端口，也可以通过命令的方式添加端口，注意，修改的内容会在/etc/firewalld/ 目录下的配置文件中还体现。例如在public区域添加tcp端口8020
--permanent：表示设置为持久； (只加到配置文件中去)
--add-port：标识添加的端口；
--add-service：标识添加的服务；

firewall-cmd --zone=public --permanent --add-port=8010/tcp
firewall-cmd --zone=public --permanent --add-service=mysql
允许10.20.1.50访问20171端口
firewall-cmd --permanent --add-rich-rule="rule family="ipv4" source address="10.20.1.50" port protocol="tcp" port="20171" accept"

重载配置文件
firewall-cmd --reload

TODO: 如何查询运行配置, 以及持久配置没有运行的？(持久配置倒是可以通过配置文件查)

（3）查看规则

firewall-cmd --list-all

public (active)
  target: default
  icmp-block-inversion: no
  interfaces: enp5s0f0 enp2s0
  sources: 
  services: KSVD dhcp samba rpc-bind libvirt libvirt-tls nfs dns dhcpv6-client ssh
  ports: 
  protocols: 
  masquerade: no
  forward-ports: 
  source-ports: 
  icmp-blocks: 
  rich rules:

（4）其它

# 查看防火墙状态
firewall-cmd --state 

# 查看默认的域
firewall-cmd --get-default-zone

# 查看所有的域
firewall-cmd --get-zones

# 查看所有域的信息
firewall-cmd --list-all-zones

# 查看指定域的信息
firewall-cmd --zone=public --list-all

# 查看可以添加的服务
firewall-cmd --get-services

关键字`firewall-cmd show service details`
https://unix.stackexchange.com/questions/486111/how-do-i-get-a-list-of-the-ports-which-belong-to-preconfigured-firewall-cmd-serv

查看服务内容
```
firewall-cmd --info-service ssh
ssh
  ports: 22/tcp
  protocols: vrrp
  source-ports:
  modules:
  destination:
```

# 设置指定域为默认域
firewall-cmd --set-default-zone=public

### 开启 NAT 转发
firewall-cmd --permanent --zone=public --add-masquerade
firewall-cmd --query-masquerade
firewall-cmd --remove-masquerade


iptables -t nat -I POSTROUTING -o Mdvs -j MASQUERADE
iptables -I FORWARD -o Mdvs -j ACCEPT

### 端口转发

将80端口的流量转发至8080
firewall-cmd --add-forward-port=port=80:proto=tcp:toport=8080

将80端口的流量转发至192.168.0.1
firewall-cmd --add-forward-port=proto=80:proto=tcp:toaddr=192.168.0.1

将80端口的流量转发至192.168.0.1的8080端口
firewall-cmd --add-forward-port=proto=80:proto=tcp:toaddr=192.168.0.1:toport=8080

firewall-cmd --permanent --zone=internal --add-interface=eth1
firewall-cmd --permanent --zone=external --add-interface=eth0
firewall-cmd --permanent --zone=external --add-masquerade 

直接放行80端口(凌驾于所有zone之上)
firewall-cmd --direct --add-rule ipv4 filter INPUT 0 -p tcp --dport 80 -j ACCEPT

firewall-cmd --permanent --direct --passthrough ipv4 -I FORWARD -i bridge0 -j ACCEPT
firewall-cmd --permanent --direct --passthrough ipv4 -I FORWARD -o bridge0 -j ACCEPT
firewall-cmd --reload

firewall-cmd --permanent --direct --passthrough ipv4 -A FORWARD -i br0 -j ACCEPT
firewall-cmd --permanent --direct --passthrough ipv4 -A INPUT -i br0 -j ACCEPT
firewall-cmd --permanent --direct --passthrough ipv4 -A FORWARD -i br0 -j ACCEPT

### ipset使用

https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/security_guide/sec-setting_and_controlling_ip_sets_using_firewalld
```
firewall-cmd --permanent --ipset=test --get-entries
```

关键字《firewall-cmd allow vrrp for specific ipset》

https://www.linuxquestions.org/questions/linux-server-73/how-to-launch-a-keepalived-server-4175693612/
```
firewall-cmd --add-rich-rule='rule source ipset="ksvdset" protocol value="vrrp" accept' --permanent
```

public.xml中是这种形式
```
  <rule>
    <source ipset="ksvdset"/>
    <protocol value="vrrp"/>
    <accept/>
  </rule>
```

### 查看丢包日志

https://www.skynats.com/blog/how-to-enable-firewalld-logging-for-a-denied-packet-on-linux/

https://serverfault.com/questions/1097034/keepalived-going-split-brain-when-firewalld-is-running
```
enabled LogDenied=all in /etc/firewalld/firewalld.conf
firewall-cmd --get-log-denied
firewall-cmd --add-rich-rule='rule protocol value="ah" accept' --permanent

dmesg | grep -i REJECT
[   75.108415] "filter_IN_public_REJECT: "IN=ethx0 OUT= MAC=52:54:84:00:0c:bd:52:54:84:00:0c:bc:08:00 SRC=192.168.101.71 DST=192.168.101.72 LEN=40 TOS=0x00 PREC=0xC0 TTL=255 ID=1 PROTO=112
```


## 参考资料

https://segmentfault.com/a/1190000019978741

https://akm111.wordpress.com/2017/04/30/linux-firewalld-port-forward-and-nat/

https://www.server-world.info/en/note?os=CentOS_7&p=firewalld&f=2

理解多区域配置中的 firewalld(不错)
firewalld 的设计者认识到大多数的 iptables 使用案例仅涉及到几个单播源 IP，仅让每个符合白名单的服务通过，而其它的会被拒绝。这种模式的好处是，firewalld 可以通过定义的源 IP 和/或网络接口将入站流量分类到不同区域zone。每个区域基于指定的准则按自己配置去通过或拒绝包。
https://zhuanlan.zhihu.com/p/31309295
