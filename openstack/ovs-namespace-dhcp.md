# 基于ovs的namespace中的dhcp服务

ExecStartPre
ExecStartPost

```
./kylin-dhcp.py -c reload
```

主要逻辑:
* 读取配置文件 `/etc/kylin-dhcp/kylin-dhcp.yaml`
* 加锁处理:
* 生成dhcp配置文件: `/var/run/kylin-dhcp/xxx/`
  * dnsmasq.conf
  * hosts.dhcp 
  * hosts.dns 
  * hosts.option
  XXX: 通过重新写的方式, 更新dhcp配置文件?
* 创建网络接口
```
export ovs_bridge=bridge
export ovs_if=vpc-subnet1
/usr/lib/ksvd/bin/ovs-vsctl --db=unix:/run/openvswitch/db.sock --may-exist add-port ${ovs_bridge} ${ovs_if} -- set interface ${ovs_if} type=internal -- set Port ${ovs_if} tag=0
```

* 创建网络命名空间
```
[ssh_10.20.2.213] root@10-20-2-213: ~$ip netns list
br_em2_23_201181008915470e83728d93432dc65f (id: 1)
br_em2_23_439de85eedcd4fb18c3ddca9a0c9c88b (id: 0)
```
  => 需要安装iproute(ip命令? 一般默认已经装过的)
```
export ovs_if=vpc-subnet1
# 怎么建得有id? 2.11上建立就有id, 之前的3.37 centos7建没有?
ip netns add ${ovs_if}
ip link set ${ovs_if} netns ${ovs_if}

# 其他配置
ip netns exec ${ovs_if} ip link set ${ovs_if} address 02:ac:10:ff:00:11
ip netns exec ${ovs_if} ip addr add 192.168.101.250/24 dev ${ovs_if}
ip netns exec ${ovs_if} ip link set ${ovs_if} up
```

* 拉起dnsmasq服务
  `/usr/local/zstack/dnsmasq --conf-file=/var/lib/zstack/dnsmasq/br_em2_23_439de85eedcd4fb18c3ddca9a0c9c88b/dnsmasq.conf`
  => 需要安装dnsmasq
  XXX: 以后升级dnsmasq版本怎么办?
```
# TODO: 记录dnsmasq的pid等信息?
ip netns exec ${ovs_if} /usr/sbin/dnsmasq --conf-file=/var/lib/ksvd/dnsmasq/${ovs_if}/dnsmasq.conf
```
  TODO: 开机时请求拉起dnsmasq服务(请求网卡准备工作!)
  TODO: 更好的启动方式?

* dnsmasq服务重新读取配置文件
```
kill -hup 55381

Jul  4 14:00:53 dnsmasq[55381]: read /var/lib/ksvd/dnsmasq/vpc-subnet1/hosts.dns - 0 addresses
Jul  4 14:00:53 dnsmasq-dhcp[55381]: read /var/lib/ksvd/dnsmasq/vpc-subnet1/hosts.dhcp
Jul  4 14:00:53 dnsmasq-dhcp[55381]: read /var/lib/ksvd/dnsmasq/vpc-subnet1/hosts.option
```

dnsmasq日志显示没有可用地址?
```
Jul  4 14:15:27 dnsmasq-dhcp[55381]: DHCPDISCOVER(vpc-subnet1) 00:01:53:be:f1:fc no address available
Jul  4 14:15:33 dnsmasq-dhcp[55381]: DHCPDISCOVER(vpc-subnet1) 52:54:84:00:08:7a no address available
```

## systemctl服务

参考
systemd/system/v2ray@.service
```
[Unit]
Description=V2Ray Service
Documentation=https://www.v2fly.org/
After=network.target nss-lookup.target

[Service]
User=nobody
CapabilityBoundingSet=CAP_NET_ADMIN CAP_NET_BIND_SERVICE
AmbientCapabilities=CAP_NET_ADMIN CAP_NET_BIND_SERVICE
NoNewPrivileges=true
ExecStart=/usr/local/bin/v2ray -config /usr/local/etc/v2ray/%i.json
Restart=on-failure
RestartPreventExitStatus=23

[Install]
WantedBy=multi-user.target
```

ubuntu 22.04的dnsmasq服务
/lib/systemd/system/dnsmasq.service
也有一个xxx配置: system/dnsmasq@.service
```
[Unit]
Description=dnsmasq - A lightweight DHCP and caching DNS server
Requires=network.target
Wants=nss-lookup.target
Before=nss-lookup.target
After=network.target

[Service]
Type=forking
PIDFile=/run/dnsmasq/dnsmasq.pid

# Test the config file and refuse starting if it is not valid.
ExecStartPre=/etc/init.d/dnsmasq checkconfig

# We run dnsmasq via the /etc/init.d/dnsmasq script which acts as a
# wrapper picking up extra configuration files and then execs dnsmasq
# itself, when called with the "systemd-exec" function.
ExecStart=/etc/init.d/dnsmasq systemd-exec

# The systemd-*-resolvconf functions configure (and deconfigure)
# resolvconf to work with the dnsmasq DNS server. They're called like
# this to get correct error handling (ie don't start-resolvconf if the
# dnsmasq daemon fails to start).
ExecStartPost=/etc/init.d/dnsmasq systemd-start-resolvconf
ExecStop=/etc/init.d/dnsmasq systemd-stop-resolvconf


ExecReload=/bin/kill -HUP $MAINPID

[Install]
WantedBy=multi-user.target
```

kylin341的dnsmasq
```
# /usr/lib/systemd/system/dnsmasq.service
[Unit]
Description=DNS caching server.
After=network.target

[Service]
ExecStart=/usr/sbin/dnsmasq -k

[Install]
WantedBy=multi-user.target
```
