# iptable usage

内网端口暴露
```bash
iptables -t nat -A PREROUTING -d 1.1.1.1/32 -p tcp -m tcp --dport 9556 -j DNAT --to-destination 192.168.122.8:22
# 允许转发(可选)
iptables -I FORWARD -d 192.168.122.8/32 -j ACCEPT
```

这里是把访问 192.168.122.8 端口 22 的返回数据再通过 SNAT 的方式将数据报文的源地址改为 192.168.122.1 (即 KVM 服务器的内网地址) 发送出去。
```bash
iptables -t nat -A POSTROUTING -d 192.168.122.8/32 -p tcp -m tcp --dport 22 -j SNAT --to-source 192.168.122.1
```


dnat, snat分别修改目的地址和源地址
```
iptables -t nat -A PREROUTING -d 58.215.xxx.xxx -p tcp --dport 3306 -j DNAT --to-destination 192.168.1.3:3306
iptables -t nat -A POSTROUTING -d 192.168.1.3 -p tcp --dport 3306 -j SNAT --to 192.168.1.2
iptables -A FORWARD -o eth0 -d 192.168.1.3 -p tcp --dport 3306 -j ACCEPT
iptables -A FORWARD -i eth0 -s 192.168.1.3 -p tcp --sport 3306 -j ACCEPT
```

sudo iptables -t nat -A OUTPUT -p tcp --dport 80 -j REDIRECT --to-ports 3128
sudo iptables -t nat -A OUTPUT -p tcp --dport 80 -j DNAT --to 10.20.3.18:3128

#### 基于目的地址的路由

- 如何给节点 root@10.30.8.x 添加一个ip地址 10.30.11.xxx, 这个ip地址仅在访问 10.90.6.41/24 网段才使用，并且还是走网关10.30.0.1，先只给出方案

=> 测试ok
```
ip addr add 10.30.11.x/32 dev IFACE
ip route add 10.90.6.0/24 via 10.30.0.1 src 10.30.11.x
```

#### 基于目的端口的策略路由

gpt: 节点A访问目的ip地址B，可以配置基于端口的路由策略吗？例如访问指定端口8080，走路由a，访问其他端口，走路由b

=> deepseek回答有效，验证成功，yuanbao的有问题
```
ip rule add fwmark 100 table 100
ip route add default via 192.168.84.254 table 100
ip rule add from all to 目的地B dport 8080 table 100
```

=> 下面配置无效, **在 OUTPUT链中标记数据包（MARK）时，Linux 的路由决策已经完成**，因此这种方式可能无法生效。这是因为 Linux 网络栈的数据包处理流程中，路由查找（route lookup）发生在 mangle/OUTPUT链之前。

- 1. 应用程序发送数据包 → 
- 2. **路由决策（第一次路由查找，基于 `main` 表）** → 
- 3. `mangle/OUTPUT`（在这里标记数据包 MARK） → 
- 4. `nat/OUTPUT` → 
- 5. **策略路由（基于 `ip rule` 和 `fwmark` 的第二次路由查找）**

问题：在第 2 步时，内核已经根据 main路由表决定了出口网关和接口，后续的 MARK操作虽然能影响策略路由，但无法改变最初的出口选择（除非使用更早的干预点）。
策略路由生效时机：ip rule基于 fwmark的路由查找是第二次决策，但如果数据包已经被决定从某个接口发出，可能不会重新路由。

linux系统可以做如下配置

- 1.创建多路由表（如table 100和table 200）。
- 2.使用iptables/nftables标记数据包：
```
iptables -A OUTPUT -d [目的IP_B] -p tcp --dport 8080 -j MARK --set-mark 100
```
- 3.基于标记选择路由表：
```
ip rule add fwmark 100 table 100
ip route add default via [路由a_网关] table 100
ip route add default via [路由b_网关] table main
```

路由跟踪测试
=> 无效!... 不受上述规则影响! => 为啥不受策略路由影响? 可能是没理解清楚traceroute的原理
```
traceroute -T -p 8080 [目的IP_B]  # 测试8080端口路径
```
抓包分析
```
tcpdump -i eth0 "host [目的IP_B] and port 8080"  # 确认流量是否按预期路由
```

#### DNAT目的地址转换

例如把访问ip1的tcp 80流量转到new_ip2上去, 如下:
```
# 转发dnat
iptables -t nat -I PREROUTING -d ${ip1}/32 -p tcp -m tcp --dport 80 -j DNAT --to-destination ${new_ip2}:80
# 本机dnat
iptables -t nat -I OUTPUT -d ${ip1}/32 -p tcp -m tcp --dport 80 -j DNAT --to-destination ${new_ip2}:80
```

#### DNAT转发访问vmware vcenter

  192.168.98.111 访问不了 10.90.0.0/16。这台开发机 192.168.98.97 两边都能到，所以用了两层转发：测试节点把目的地址改到开发机，开发机再按端口把 TCP 原样转到 vCenter 和 ESXi。

  192.168.98.111
    iptables OUTPUT DNAT
          |
          v
  192.168.98.97  tcp_relay.py
          |
          +--> 10.90.6.41:443   vCenter
          +--> 10.90.6.40:443   ESXi
          +--> 10.90.6.40:902   NBD

  1. 开发机上的 TCP 中继

  脚本是 /tmp/tcp_relay.py。它在 192.168.98.97 上监听，收到连接后 socket.create_connection 到真实地址，双向拷贝字节，不改协议。当时开了三个进程：

```
  python3 /tmp/tcp_relay.py 192.168.98.97 18443 10.90.6.41 443
  python3 /tmp/tcp_relay.py 192.168.98.97 18440 10.90.6.40 443
  python3 /tmp/tcp_relay.py 192.168.98.97 19020 10.90.6.40 902
```

  参数顺序是：监听地址、监听端口、目标地址、目标端口。443 走 SOAP/VDDK 控制连接，902 走 NBD 磁盘数据。

  2. 测试节点上的 DNAT

  vmware-backup 和 pyVmomi 会直接连 JSON 和 vSphere 里给出的 IP，不会走 HTTP 代理。所以在 192.168.98.111 的 OUTPUT 链上，把这些目的地址改到开发机对应端口：

```
  iptables -t nat -A OUTPUT -d 10.90.6.41/32 -p tcp --dport 443 \
    -j DNAT --to-destination 192.168.98.97:18443
  iptables -t nat -A OUTPUT -d 10.90.6.40/32 -p tcp --dport 443 \
    -j DNAT --to-destination 192.168.98.97:18440
  iptables -t nat -A OUTPUT -d 10.90.6.40/32 -p tcp --dport 902 \
    -j DNAT --to-destination 192.168.98.97:19020
```

  OUTPUT 在本机进程发出包、路由之前生效，所以 111 不需要有到 10.90.0.0/16 的路由，只要能访问同网段的 192.168.98.97。

  ESXi 地址 10.90.6.40 是连上 vCenter 之后从这台虚拟机的 runtime.host 读到的，不是事先写死的。

#### 简单nat转发

```bash
iptables -t nat -I POSTROUTING -o Mdvs -j MASQUERADE
iptables -I FORWARD -o Mdvs -j ACCEPT
```

#### 一对一NAT

配置浮动ip地址, 需要注意这个浮动ip浮动的物理接口eth0

```bash
iptables -I FORWARD -j ACCEPT
ip address add 10.90.3.32/32 dev eth0
iptables -t nat -I POSTROUTING -s 192.168.100.1/32 -o eth0 -j SNAT --to-source 10.90.3.32
iptables -t nat -I PREROUTING -i eth0 -d 10.90.3.32/32 -j DNAT --to-destination 192.168.100.1
```

* SNAT 在路由之后 做源地址转换 （postrouting）
* DNA 在路由之前 做目的地地址转换 （prerouting）

TODO: 使用firewall-cmd配置验证
```bash
firewall-cmd --permanent --direct --passthrough ipv4 -t nat POSTROUTING -s 192.168.100.1/32 -o eth0 -j SNAT --to-source 10.90.3.32
firewall-cmd --permanent --direct --passthrough ipv4 -t nat PREROUTING -i eth0 -d 10.90.3.32/32 -j DNAT --to-destination -d 192.168.100.1 
```

编写了一个nat.sh脚本做这件事情，后续计划使用firewalld来做，更方便
```bash
inter_ip=192.168.100.13
extern_ip=10.90.3.20
ifname=eth0

add_nat()
{
	#iptables -I FORWARD -j ACCEPT # TODO: 只加一次
	ip address add ${extern_ip}/32 dev ${ifname} # TODO: 只加一次
	iptables -t nat -I POSTROUTING -s ${inter_ip}/32 -o ${ifname} -j SNAT --to-source ${extern_ip} # TODO: 删除残留规则, 不重复加
	iptables -t nat -I PREROUTING -i ${ifname} -d ${extern_ip}/32 -j DNAT --to-destination ${inter_ip} # TODO: 删除残留规则, 不重复加
}

# 输入参数: extern_ip, ifname
del_nat()
{
	#iptables -I FORWARD -j ACCEPT # TODO: 只加一次
	ip address del ${extern_ip}/32 dev ${ifname} # TODO: 可以重复删除
	iptables -t nat -D POSTROUTING -s ${inter_ip}/32 -o ${ifname} -j SNAT --to-source ${extern_ip} # TODO: 模糊删除未成功
	#iptables -t nat -D POSTROUTING -o ${ifname} -j SNAT --to-source ${extern_ip} # TODO: 模糊删除, 未成功
	iptables -t nat -D PREROUTING -i ${ifname} -d ${extern_ip}/32 -j DNAT --to-destination ${inter_ip} # TODO: 模糊删除
}

#add_nat
del_nat
```
