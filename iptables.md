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

#### 一对一NAT

配置浮动ip地址, 需要注意这个浮动ip浮动的物理接口eth0

```bash
iptables -I FORWARD -j ACCEPT
ip address add 10.90.3.32/32 dev eth0
iptables -t nat -I POSTROUTING -s 192.168.100.1/32 -o eth0 -j SNAT --to-source 10.90.3.32
iptables -t nat -I PREROUTING -i eth0 -d 10.90.3.32/32 -j DNAT --to-destination 192.168.100.1
```
