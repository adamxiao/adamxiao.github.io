# 基于ovs的namespace中的dhcp服务

TODO:
* 1.错误码返回?
  例如创建接口时, 发现接口已经存在?

## 接口设计

提供接口
* 新增dhcp => ok
  生成dnsmasq服务配置, 并启动dnsmasq服务
* 新增虚拟机ip, mac绑定 => ok
  重新生成dnsmasq配置, 通知程序重新加载配置
* 销毁dhcp => ok
  停止dnsmasq服务, 销毁相关配置
* 列表所有dhcp服务
  列表当前存在的所有dnsmasq服务, 以及状态
  is-active：目前有没有正在运行中。

### 测试用例

#### 创建dhcp, 已经存在netns

已存在其他残留数据的场景
* 存在netns
  => 使用这个现有的netns! 加上日志, 不应该出现这种情况
* 存在dhcp接口
  => FIXME: 直接删除旧接口!
* 存在dhcp配置
  => 不处理
* 存在dhcp服务配置
  => 认为服务已存在, 无法创建(考虑最后请dhcp服务配置文件)

只要存在netns, 则检查服务是否存在, 不存在则认为是残留数据
存在服务认为dhcp服务存在, 不处理

#### 清理dhcp, 清理掉所有的数据

最后清理dhcp服务配置文件

## 其他

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

TODO: 是否考虑开机启动? => no? 
* 代码兼容清理旧数据
```
[ssh_10.90.2.11] root@node1: ~$systemctl cat vpc-subnet1
# /usr/lib/systemd/system/vpc-subnet1.service
[Unit]
Description=DHCP server
After=network.target

[Service]
ExecStart=/usr/sbin/ip netns exec vpc-subnet1 /usr/sbin/dnsmasq -k --conf-file=/var/lib/ksvd/dnsmasq/vpc-subnet1/dnsmasq.conf

[Install]
WantedBy=multi-user.target
```


python 子网掩码转换
参考: https://www.jianshu.com/p/8955e91a45af
```python
# 子网掩码地址转长度
def netmask_to_bit_length(netmask):
  """
  >>> netmask_to_bit_length('255.255.255.0')
  24
  >>>
  """
  # 分割字符串格式的子网掩码为四段列表
  # 计算二进制字符串中 '1' 的个数
  # 转换各段子网掩码为二进制, 计算十进制
  return sum([bin(int(i)).count('1') for i in netmask.split('.')])

# 子网掩码长度转地址
def bit_length_to_netmask(mask_int):
  """
  >>> bit_length_to_netmask(24)
  '255.255.255.0'
  >>>
  """
  bin_array = ["1"] * mask_int + ["0"] * (32 - mask_int)
  tmpmask = [''.join(bin_array[i * 8:i * 8 + 8]) for i in range(4)]
  tmpmask = [str(int(netmask, 2)) for netmask in tmpmask]
  return '.'.join(tmpmask)
```
