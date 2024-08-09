# 创建虚拟路由虚拟机

## 外部提供接口设计

提供接口
* 生效配置
  参数为kylin-vr配置文件, 实现为生效配置
* 其他子接口设计
  * 关联vpc网络(一个或多个)
  * 新增EIP配置(一个或多个)
  * 新增端口转发配置(一个或多个)

问题:
* 写空配置文件。。。
  * 句柄文件泄漏?
* 配置文件出错, reload失败?
* reload失败怎么看日志?

关键字《python string format already has {》
https://blog.finxter.com/how-to-format-a-string-that-contains-curly-braces-in-python/
* Method 1: Using Double Curly Braces
* Method 2: Using The Old String Formatting Style (%)
* Method 3: Using The JSON Library
* Method 4: Using Template Strings

## TODO:

TODO(20220608):
* kylin-vr整体rpm包安装粗略测试 => ok

TODO(20220607):
* kylin-vr异常测试
  * 配置空不报错, 处理正常
  * 没有网卡配置, 处理正常
* kylin-vr程序打包好, 方便安装配置 => 优先级低
  * 配置sysctl规则
  * 配置udev规则
* 全新创建vr虚拟机配置验证 => ok
  * 配置实现eip => ok

TODO(20220606):
* 全新创建vr虚拟机配置验证 => doing
  * 配置实现eip
* kylin-vr新增参数 reload xxx.yaml => 必要性不大, 暂不做
  * 直接作为base64参数输入?
  * 覆盖已有配置文件
  * 增量更新?
* port forward实现 => 自测麻烦
  * tcp, udp映射 => ok
  * 单端口转发 => ok
  * 端口范围转发(zstack的端口范围必须一致) => ok
  * 端口映射需要ip增加支持! => ok
  * 端口映射和ip映射冲突, 优先ip映射
* 网关接口eth0动态获取出来! => ok

done:
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
* kylin-vr脚本日志输出到/var/log/xxx? => 优先级低, 暂时不处理

## 部署虚拟路由虚拟机极简步骤

#### 1.安装centos7虚拟机镜像

例如: 使用centos7官方云镜像 CentOS-7-x86_64-GenericCloud-2009.qcow2

以及简单配置一下密码登录:
```bash
virsh set-user-password  e08979eb-99fd-390f-fee2-7e67b2b532b6  root xxxxxx
```

#### 2. 配置ip,安装kylin-vr软件

修改 /etc/sysconfig/network-scripts/ifcfg-eth0 , 修改内容如下:
```
BOOTPROTO="static"

IPADDR=10.90.3.37
PREFIX=24
GATEWAY=10.90.3.1
DNS1=10.90.3.38
```

然后重启网络:
```bash
systemctl restart network
```

安装kylin-vr软件包(注意会下载依赖包, 需要能够访问到镜像仓库)
```bash
yum install -y http://10.20.1.99:8080/kylin-vr-0.1-1.x86_64.rpm
```

#### 3. 配置kylin-vr.yaml重启测试

简单配置一下网卡ip地址, eip等
```yaml
if_list:
   - ipaddr: 10.90.3.37
     prefix: 24
     mac: 52:54:84:00:08:45
     gateway: 10.90.3.1
   - ipaddr: 192.168.100.254
     prefix: 24
     mac: 52:54:84:11:00:03
eip_list:
  - eip: 10.90.2.250
    vm-ip: 192.168.100.190
  - eip: 10.90.2.251
    vm-ip: 192.168.100.191
port_forward_list:
  - eip: 10.90.2.254
    protocal: tcp
    port: 80
    end_port: 82
    vm-port: 80
    vm-ip: 192.168.100.190
```

最后**重启**生效!

#### 4. 生成虚拟路由模板

简单, 清空还原kylin-vr.yaml配置文件, 关机即可

#### 附录: 制作kylin-vr的rpm包

生成源码包
```
mkdir /tmp/kylin-vr-0.1
# 生成源码文件
cd /tmp/
tar -cvzf kylin-vr-0.1.tar.gz kylin-vr-0.1
kylin-vr-0.1/
kylin-vr-0.1/kylin-vr.py
...

mv /tmp/kylin-vr-0.1.tar.gz ~/rpmbuild/SOURCES/
```

配置spec文件安装, 在相应附件中

## 测试用例

#### 新增子网

checklist:
* 网卡添加正确
* 子网ip地址配置正确
* 配置先添加, 网卡后加 => 配置先加, 运行没有问题; 网卡加上触发配置成功;
* 网卡先加, 配置后加 => ok 没问题

#### 删除子网

checklist:
* 网卡删除正确
* 没有残留ip配置
* 没有残留ip, iptables规则?

* 删除完所有的子网, 系统正常
* xxx

#### 端口映射

checklist:
* tcp 80 -> vm 80 => ok
* tcp 8080 -> vm 80 => ok
* tcp 端口范围映射80~82 => ok
  => 使用http协议测试tcp端口映射
* udp 80 -> vm 80 => ok
* udp 8080 -> vm 80 => ok
* udp 端口范围80~82 => ok
  => udp还得再理解一下

### kylin-vr脚本

执行触发逻辑:
* 开机运行 => done
* 配置更新运行 => done, 为重新全量下发配置
  * XXX: 优化为增量更新配置?
* 新增/删除网卡运行
* 配置文件空 => 

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

[Service]
ExecStart=/usr/local/bin/kylin-vr.py
TimeoutSec=0

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
cat > /etc/udev/rules.d/80-local.rules << EOF
ACTION=="add", SUBSYSTEM=="net", RUN+="/usr/local/bin/kylin-vr.py -c reload"
ACTION=="del", SUBSYSTEM=="net", RUN+="/usr/local/bin/kylin-vr.py -c reload"
EOF
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

```
Another app is currently holding the yum lock; waiting for it to exit...
  The other application is: yum
    Memory :  27 M RSS (1.4 GB VSZ)
    Started: Sun Jun  5 02:31:24 2022 - 05:09 ago
    State  : Sleeping, pid: 3084
```

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

#### 端口转发配置

https://blog.csdn.net/u013401853/article/details/70848433

单个端口映射
　　一般而言要在路由器里实现一条端口映射规则，需要两个iptables规则，一条是目的地址转换一条是源地址转换。 如下（192.168.40.200是wan口地址，10.0.0.150是LAN侧主机地址）：
```bash
iptables -t nat -I PREROUTING -p tcp -d 192.168.40.200 --dport 23 -j DNAT --to 10.0.0.150:23
iptables -t nat -I POSTROUTING -p tcp -s 10.0.0.150 --sport 23 -j SNAT --to 192.168.40.200:23
```

范围端口映射
　　查看man iptables可知，范围端口映射规则也挺简单，匹配源时写为--sport port[:port]，target时写为[ipaddr][-ipaddr][:port[-port]]。即上面单个的端口映射规则改为这种形式：
　　iptables -t nat -I PREROUTING -p tcp -d 192.168.40.200 --dport 23:100 -j DNAT --to 10.0.0.150:23-100

　　重点不在于规则怎么写，而是范围端口映射时是怎么映射？因为它可以少对多也可以多对少。例如配置[10-12]映射到[100-102]，我怎么知道端口11会映射到具体那个端口，101吗？ [100-200]映射到[10-20]时又会怎么样呢？

　　如果测试一下第一个问题会发现总是映射到100端口，不是想象的101端口。


https://docs.azure.cn/zh-cn/articles/azure-operations-guide/virtual-network/aog-virtual-network-using-netcat-check-the-connectivity

测试:
```bash
# 服务端监听tcp 8080端口
nc -n -l 8080 -v
# 客户端连接服务端
nc <服务器端 IP 地址> <端口号>
```

udp协议类似
```
nc -n -k -lu <端口号> -v
nc -u <服务器端 IP 地址> <端口号>
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

配置 /etc/sysctl.conf
```
net.ipv4.ip_forward = 1
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
```

#### 其他

* kylin-vr开机启动服务
* 网卡新增事件配置

## arm架构适配

关键问题: 热添加网卡后，没有更新生效 (虚拟机里面没有新增网卡)

- 1.添加网卡后上报事件, web控制台触发更新配置
  即便rescan之后, 网卡出现的时机，还是不太可控?
  以及卸载网卡, 旧系统下rescan也不起作用
  => 再次访问这个删除掉的网卡，系统crash，严重问题!
- 2.修改arm架构网卡模式，可以热添加生效(pcie root port的方式)
  可以多预留几个pci槽位
- 3.合并网卡，首次关联需要重启，后续无需添加网卡?
  => 不是很合适
- 4. vroute-vm特殊flag，后台处理，参考思路1
- 5. 使用R101等新OS系统，热添加能生效的?
  缺点: 需要重新适配配置更新程序?
  rocky linux 9.4 ? => 无法启动, 启动后，发现不能自动识别在线添加的网卡, 需要rescan!
  debian 11 ?  (都不是rpm系列了，只能做run包了?)
  centos7 arm => 不行
  R101 arm (3.5.1) => 可以, 最终使用 KylinSec-Server-3.5.1-2206-052234-aarch64.iso
  centos stream 9 => 不行, 同rocky 9

#### 基于kylin 3.5.1创建虚拟vpc路由器

- 基于iso安装最小系统
  注意选择最小安装, 配置root密码即可
  (使用os那边定制好的镜像 => 他们没做好用不了!)
- 安装kylin-vr rpm包
  可能需要手动配置ip,网关,dns
  然后使用yum源自动安装依赖包
- 安装qemu-guest-agent
```
yum install -y qemu-guest-agent
```
- 额外配置ipforward放通
```
sed -i 's/^net.ipv4.ip_forward/#&/' /etc/sysctl.conf
```
- 做个python链接
```
ln -sf /usr/bin/python3 /usr/bin/python2
ln -sf /usr/bin/python3 /usr/bin/python
```

最后关机，转换为vpc路由器模板即可!

#### 验证用例

- 创建arm vpc路由器, 关联公有网络，vpc网络, 开机生效 => ok
- arm vpc路由器，在线关联/解关联 vpc网络生效 => doing mc有bug
- 在线创建弹性ip生效 => ok
  其他端口映射，由于我没有改动，不测也没有关系

#### 旧的arm适配

- 1.下载centos7 arm64云镜像: CentOS-7-aarch64-GenericCloud-2009.qcow2
- 2.基于源码构建kylin-vr 虚拟路由器镜像rpm包:
- 3.创建arm64云服务器，安装rpm包
- 4.禁用cloud-init
- 5.转为vpc镜像模板，导出即可

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


使用firewalld配置iptables规则?
```
# /etc/firewalld/firewalld.conf
# DefaultZone=trusted

/etc/firewalld/direct.xml
<?xml version="1.0" encoding="utf-8"?>
<direct>
  <rule priority="0" table="filter" ipv="ipv4" chain="INPUT">-i docker0 -j ACCEPT</rule>
</direct>
```

禁用ipv6 《network-scripts disable ipv6》
```
# XXX: 禁用ipv6 <network-scripts disable ipv6>
# https://www.looklinux.com/how-to-disable-ipv6-in-centos-and-redhat/
# /etc/sysctl.conf
```

## FAQ

#### udev规则执行脚本有问题

原来是脚本没有解析器, 加上就好了`#!/bin/bash`

```
journalctl -f -u systemd-udevd.service
systemd-udevd[542960]: Using default interface naming scheme 'v249'.
systemd-udevd[542960]: eth0: Network interface 12 is renamed from 'eth0' to 'ethx2'
systemd-udevd[542960]: eth0: Process '/usr/bin/kylin-vr.sh' failed with exit code 1.
systemd-udevd[542992]: Using default interface naming scheme 'v249'.
```

#### vpc路由器下的vm无法访问其他子网的弹性ip

原因是做dnat，只对出口网关网卡做了, 需要修正

https://linuxhint.com/masquerade-with-iptables/
```
Specifying a Destination Address Range to Exclude from Masquerading
$iptables -t mangle -A PREROUTING -d 203.0.113.0/24 -j MARK --set-mark 1
$iptables -t nat -A POSTROUTING -o eth0 -m mark ! --mark 1 -j MASQUERADE

Specifying the Source IP Address to Masquerade
$iptables -t nat -A POSTROUTING -o eth0 --to-source 203.0.113.1 -j MASQUERADE
```

测试用例:

- snat测试用例
  注意snat的ip地址为虚拟路由器公网ip地址
  - 子网A，访问子网B的私有ip，没有snat => ok
  - 子网A，访问外部ip，有snat => ok
  - 子网A, 访问子网A(或子网B)的弹性ip, 有snat => ok
  - 外部访问子网A的弹性ip, 没有snat => ok
- dnat测试用例
  - 子网A, 访问子网A(或子网B)的弹性ip, 有dnat => 重复(上述snat已测)
  - 子网A，访问自己的弹性ip, 有dnat => ok
  - 外部访问子网A的弹性ip, 有dnat => ok


#### mac地址错误, 添加网卡失败

libvirt: Domain Config error : XML 错误：意外单播 mac 地址，找到多播 '11:11:22:22:33:00'
