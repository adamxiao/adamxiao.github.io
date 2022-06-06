# 创建虚拟路由虚拟机

TODO:
* kylin-vr脚本新增参数, 适配不同的运行模式 => ok
  * 开机启动运行 --start
  * 配置更新模式 --reload
* reload不是很合理, 切换一下 => ok, 使用nmcli
  * reload发现ip冲突, 导致reload失败
  * restart network 耗时38s, 那多几个ip地址不是更长?
* kylin-vr配置文件路径设计 => ok
  /etc/kylin-vr/kylin-vr.yaml, 还要创建目录
* kylin-vr配置多个eip生效验证 => ok
* 多个程序同时调用kylin-vr脚本的冲突问题? => ok, 加锁处理？
  => 是否检测ip地址冲突, 不检查!
* kylin-vr脚本日志输出到/var/log/xxx?

```
Another app is currently holding the yum lock; waiting for it to exit...
  The other application is: yum
    Memory :  27 M RSS (1.4 GB VSZ)
    Started: Sun Jun  5 02:31:24 2022 - 05:09 ago
    State  : Sleeping, pid: 3084
```

## 测试用例

#### 新增子网

checklist:
* 网卡添加正确
* 子网ip地址配置正确
* 配置先添加, 网卡后加 => 配置先加, 运行没有问题; 网卡加上触发配置成功;
* 网卡先加, 配置后加

#### 删除子网

checklist:
* 网卡删除正确
* 没有残留ip配置
* 没有残留ip, iptables规则?

### kylin-vr脚本

执行触发逻辑:
* 开机运行 => done
* 配置更新运行 => done, 为重新全量下发配置
  * XXX: 优化为增量更新配置?
* 新增/删除网卡运行

读取配置逻辑:
* 读取配置, 生成vr相关配置 => done

#### 开机启动运行

参考cloud-init-local服务, 在网络服务前运行

/lib/systemd/system/kylin-vr.service
```
[Unit]
Description=Kylin VR Config Script(pre-networking)
#After=network.service
After=systemd-remount-fs.service
After=dbus.socket
Wants=network-pre.target
Before=NetworkManager.service network.service
Before=network-pre.target
Before=shutdown.target
Before=firewalld.target
Conflicts=shutdown.target
DefaultDependencies=no
Requires=dbus.socket
TimeoutSec=0

[Service]
ExecStart=/usr/local/bin/kylin-vr.py

Type=oneshot

[Install]
WantedBy=multi-user.target
```

配置开机运行
```bash
systemctl daemon-reload
systemctl enable kylin-vr
```

#### 配置更新运行

有大致两种情况(就是网卡添加的顺序无法保证):
* 新增了接口配置, 但是接口还没有添加上
* 接口已经增加上了 => 简单

考虑同步执行脚本, 还是单例执行?

需要做的配置:
* 可能是全部重新配置一下

关键是差异!

#### 新增/删除网卡运行

配置udev规则:
```
[ssh_10.90.3.36] root@localhost: etc$cat /etc/udev/rules.d/80-local.rules
ACTION=="add", SUBSYSTEM=="net", RUN+="/usr/local/bin/kylin-vr.py -c reload"
```

考虑通知调用脚本kylin-vr实现
* kylin-vr服务没启动, 则无需处理(使用/run/kylin-vr.sock表示?)
* 通知kylin-vr脚本进行处理(目前先直接调用吧)

参考ifup eth2实现

需要做的配置:
* 配置接口up => 简单
* set ip addr => 简单
* set gateway(dns不用)
* 其他eip, snat等配置

内核事件通知链和netlink消息
https://blog.csdn.net/homezhuyihong/article/details/120322192
=> 感知到网卡新增或删除
netdev_chain，表示网络设备状态变化；
inetaddr_chain，表示ipv4地址发生变化；
inet6addr_chain，表示ipv6地址发生变化；

ip monitor [ all | OBJECT-LIST ] [ file FILENAME ] [ label ] [
               all-nsid ] [ dev DEVICE ]
ip -timestamp monitor link
=> 能够监听到网卡事件

udevadm monitor
=> 可以监控udev事件
https://www.tecmint.com/udev-for-device-detection-management-in-linux/

#### 加锁执行

关键字《python脚本加锁防止同时执行》
* 1. 文件锁
* 2. 端口锁 => 需要占用端口...

http://blog.itpub.net/22664653/viewspace-2110638/

计划使用fcntl文件锁
http://blog.itpub.net/22664653/viewspace-2110638/

## vr配置逻辑

#### 网络配置

更新network配置文件:
/etc/sysconfig/network-scripts/ifcfg-eth0

使用nmcli c reload, 非常不错!
  => systemctl reload NetworkManager => 这个没用?
nmcli con load /etc/sysconfig/network-scripts/ifcfg-ifname
然后可能就是需要自己up一些配置!nmcli c up eth0

network服务重启很慢，而且考虑了网络ip地址冲突的问题!

参考 /etc/sysconfig/network-scripts/ifup-eth
```bash
DEVICE=eth0
GATEWAY=10.90.3.1
ip addr flush dev ${DEVICE} 2>/dev/null
ip link set dev ${DEVICE} up
ipaddr=('10.90.3.35/24' '10.90.2.253/32')
# set IP address(es)
for idx in {0..256} ; do
    if [ -z "${ipaddr[$idx]}" ]; then
        break
    fi

    if ! LC_ALL=C ip addr ls ${REALDEVICE} | LC_ALL=C grep -q "${ipaddr[$idx]}" ; then
        if ! ip addr add ${ipaddr[$idx]} dev ${DEVICE} ; then
            echo $"Error adding address ${ipaddr[$idx]} for ${DEVICE}."
        fi
    fi
done

ip route replace default via ${GATEWAY} dev ${DEVICE}
# ip route add default via $gateway dev ${DEVICE}
# ip route show default
```

### 基础环境

#### 使用centos7官方云镜像: CentOS-7-x86_64-GenericCloud-2009.qcow2

#### 安装配置辅助软件

```
yum install -y python3-pip NetworkManager
pip3 install pyyaml netifaces
```

#### 禁用selinux(让qga能够写文件)

```bash
sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/selinux/config
setenforce 0
```

#### 配置qga启用写文件, 执行命令接口

https://blog.csdn.net/weixin_43863487/article/details/104939023
如果想要将要执行的命令从黑名单中去掉，可以编辑qemu-ga 的配置文件 /etc/sysconfig/qemu-ga (这里以CentOS为例) 将配置中 BLACKLIST_RPC 中的命令去掉。

```bash
sed -i 's/^BLACKLIST_RPC/#&/' /etc/sysconfig/qemu-ga

#BLACKLIST_RPC=guest-file-open,guest-file-close,guest-file-read,guest-file-write,guest-file-seek,guest-file-flush,guest-exec,guest-exec-status
```

#### ip转发等其他配置

```
net.ipv4.ip_forward = 1
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
```

#### 其他

* kylin-vr开机启动服务
* 网卡新增事件配置

## 其他资料

```
virsh qemu-agent-command centos8 --cmd '{"execute":"guest-exec","arguments":{"path":"mkdir","arg":["-p","/root/.ssh"]}}'
{"return":{"pid":9468}}

virsh qemu-agent-command centos8 '{"execute":"guest-exec-status","arguments":{"pid":9905}}'
{"return":{"exitcode":0,"exited":true}}

virsh qemu-agent-command $domain --cmd '{"execute":"guest-exec","arguments":{"path":"touch","arg":["/root/.ssh/adam-test"],"capture-output":true}}'

# 打开文件（以读写方式打开），获得句柄 virsh qemu-agent-command centos8 --cmd '{"execute":"guest-file-open", "arguments":{"path":"/root/.ssh/authorized_keys","mode":"w+"}}'
{"return":1001}
# 写文件，假设上一步返回{"return":1000}，1000就是句柄
virsh qemu-agent-command centos8 --cmd '{"execute":"guest-file-write", "arguments":{"handle":1001,"buf-b64":"xxx"}}'

```

TODO: 句柄泄漏的问题?
写配置文件
```
virsh qemu-agent-command $domain --cmd '{"execute":"guest-file-open", "arguments":{"path":"/usr/local/bin/kylin-vr.yaml","mode":"w"}}'
{"return":1000}
# 写文件，假设上一步返回{"return":1000}，1000就是句柄
virsh qemu-agent-command $domain --cmd '{"execute":"guest-file-write", "arguments":{"handle":1000,"buf-b64":"aGVsbG86IHRydWUK"}}'
{"return":{"count":12,"eof":false}}
# 关闭文件
virsh qemu-agent-command $domain '{"execute":"guest-file-close", "arguments":{"handle":1000}}'
```


执行kylin-vr脚本
```
domain=468e4a0e-e647-38b0-6f37-ac7d2cb59585
virsh qemu-agent-command $domain --cmd '{"execute":"guest-exec","arguments":{"path":"python3","arg":["/usr/local/bin/kylin-vr.py", "/usr/local/bin/adam.yaml"]}}'
{"return":{"pid":23453}}

virsh qemu-agent-command $domain '{"execute":"guest-exec-status","arguments":{"pid":23478}}'
```


## FAQ

#### mac地址错误, 添加网卡失败

libvirt: Domain Config error : XML 错误：意外单播 mac 地址，找到多播 '11:11:22:22:33:00'
