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

#### DNAT目的地址转换

例如把访问ip1的tcp 80流量转到new_ip2上去, 如下:
```
# 转发dnat
iptables -t nat -I PREROUTING -d ${ip1}/32 -p tcp -m tcp --dport 80 -j DNAT --to-destination ${new_ip2}:80
# 本机dnat
iptables -t nat -I OUTPUT -d ${ip1}/32 -p tcp -m tcp --dport 80 -j DNAT --to-destination ${new_ip2}:80
```

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
