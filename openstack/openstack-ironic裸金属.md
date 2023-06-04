# openstack ironic裸金属管理

目标:
- 使用IPMI管理裸设备 => ok
  例如开机关机重启，pxe启动等
- 部署实例到裸设备上
  例如部署centos系统

关键字《openstack ironic文档》

[简书 - OpenStack - Ironic](https://www.jianshu.com/p/ab799d414158)
OpenStack Ironic就是一个进行裸机部署安装的项目。

Ironic实现的功能，就是可以很方便的对指定的一台或多台裸机，执行：
- （1）硬盘RAID、分区和格式化；
- （2）安装操作系统、驱动程序；
- （3）安装应用程序。

[(好)Openstack Ironic Bare metal 实操](https://blog.csdn.net/m0_48594855/article/details/119979493)
如果把Ironic放到庞大的系统去理解，毕竟繁琐，不适合初学者；所幸的是Ironic本身是一个相对独立的模块，有模块自己的操作命令。

如果使用相关命令操作一遍，结合文档理解，清晰了然。
=> TODO: 实际操作理解

[剖析ironic](https://doodu.gitbooks.io/openstack-ironic/content/ironicpou_xi.html)

有一张图, 讲解pxe流程, 还行

利用IPMI可以实现以下功能
- 可以在服务器通电（没有启动操作系统）情况下，对它进行远程管理：开机，关机，重启
- 基于文本的控制台重定向，可以远程查看和修改BIOS设置，系统启动过程，登入系统等
- 可以远程通过串口IP映射(SoL)连接服务器，解决ssh服务无法访问，远程安装系统，查看系统启动故障等问题
- 可以通过系统的串行端口进行访问
- 故障日志记录和 SNMP 警报发送，访问系统事件日志 (System Event Log ,SEL) 和传感器状况

IPMI技术功能点总结：

- 远程电源控制 (on / off / cycle / status)
- 串口的IP映射 Serial over LAN (SoL)
- 支持健康关机（Graceful shutdown support）
- 机箱环境监控 (温度, 风扇转速, CPU电压等)
- 远程设备身份LED控制(Remote ID LED control)
- 系统事件日志（System event log）
- 平台事件跟踪（Platform Event Traps）
- 数据记录（Data logging）
- 虚拟KVM会话（Virtual KVM）
- 虚拟媒介（Virtual Media）

参考资料： https://en.wikipedia.org/wiki/Intelligent_Platform_Management_Interface

我们把fake驱动排除，其他的驱动可以分为两类：
- 一是以pex 或者 iscsi 为前缀的驱动采用PXE部署机制，这些驱动**将根硬盘作为iSCSI设备暴露给ironic conductor，由conductor将镜像复制到这里.**
- 二是以agent_ 为前缀的驱动采用Agent部署机制，conductor准备一个存储在swift上的镜像URL给IPA，由IPA下载镜像和完成部署的操作。

**openstack ironic 支持用虚拟模拟物理机进行测试!!!**

[Openstack Ironic standalone 方式部署](https://www.xiexianbin.cn/openstack/ironic/index.html)
ironic如果配置成standalone服务，其他服务如glance，neutron，nova，cinder等无需安装。

[Ironic 裸金属管理服务 原创](https://blog.51cto.com/u_15301988/3160308)
devstack部署ironic, 使用vm模拟裸金属服务器

#### 安装ironic

关键字《kolla-ansible enable ironic》《kolla-ansible 启用 ironic》

https://docs.openstack.org/kolla-ansible/latest/reference/bare-metal/ironic-guide.html

#### 添加节点

关键字《openstack ironic create node》《openstack ironic 添加节点》

https://docs.mirantis.com/mcp/q4-18/mcp-operations-guide/openstack-operations/ironic-operations/add-baremetal-nodes.html
```
ironic node-create \
    --name <node-name> \
    --driver <driver-name> \
    --driver-info deploy_ramdisk=<glance UUID of deploy image ramdisk> \
    --driver-info deploy_kernel=<glance UUID of deploy image kernel> \
    --driver-info ipmi_address=<IPMI address of the node> \
    --driver-info ipmi_username=<username for IPMI> \
    --driver-info ipmi_password=<password for the IPMI user> \
    --property memory_mb=<RAM size of the node in MiB> \
    --property cpus=<Number of CPUs on the node> \
    --property local_gb=<size of node's disk in GiB> \
    --property cpu_arch=<architecture of node's CPU>
```

https://blog.csdn.net/OldHusband/article/details/112794051
十、注册 Enrollment Baremetal Node
```
# 首先查看用到的 IPMI 的所有 Ironic Driver
openstack baremetal driver show ipmi
# 打印出 IPMI 驱动程序的属性清单
openstack baremetal driver property list ipmi
```

创建节点
(注意: ipmi协议端口默认是623)
```
openstack baremetal node create --driver ipmi --name BM01 \
--deploy-interface iscsi \
--raid-interface agent \
--driver-info ipmi_username=ADMIN \
--driver-info ipmi_password=ADMIN \
--driver-info ipmi_address=10.30.10.3 \
--driver-info ipmi_port=623 \

Could not find the following interface in the 'ironic.hardware.interfaces.deploy' entrypoint: iscsi. Valid interfaces are ['direct']. (HTTP 400)
```

### openstack 裸金属命令使用

ironic-api提供一系列接口，详见[ironic API](https://docs.openstack.org/api-ref/baremetal/?expanded=change-node-provision-state-detail,get-console-detail,start-stop-console-detail,show-driver-logical-disk-properties-detail)。

- 节点相关（node）
  - 节点增删改查（List, Searching, Creating, Updating, and Deleting)
  - 合法性检查
  - 设置和清除维修状态
  - 设置和获取boot device
  - 获取节点当前综合信息，包括power, provision, raid, console等
  - 更改电源状态
  - 更改节点提供状态（ manage, provide, inspect, clean, active, rebuild, delete (deleted), abort）
  - 设置RAID
  - 启动、停止、获取console
  - 查看、调用厂商定制方法（passthru方法）
- 端口相关(Port)
  - 对物理端口（Port）的增删改查（Listing, Searching, Creating, Updating, and Deleting ），新建的时候就要指定端口的物理地址(一般是MAC地址)与Node进行绑定。
  - 查看与Node连接的端口
- 驱动相关（driver）
  - 列举所有驱动
 - 查看驱动的详细信息、属性
 - 查看和调用厂商的驱动

#### 创建节点

(注意: ipmi协议端口默认是623)
```
openstack baremetal node create --driver ipmi --name BM01 \
--deploy-interface iscsi \
--raid-interface agent \
--driver-info ipmi_username=ADMIN \
--driver-info ipmi_password=ADMIN \
--driver-info ipmi_address=10.30.10.3 \
--driver-info ipmi_port=623 \

Could not find the following interface in the 'ironic.hardware.interfaces.deploy' entrypoint: iscsi. Valid interfaces are ['direct']. (HTTP 400)
=> 去除iscsi参数即可
```

```
openstack baremetal node list
+--------------------------------------+------+---------------+-------------+--------------------+-------------+
| UUID                                 | Name | Instance UUID | Power State | Provisioning State | Maintenance |
+--------------------------------------+------+---------------+-------------+--------------------+-------------+
| 831ac23b-7daa-462b-ab28-6dd2972c5000 | BM01 | None          | power on    | enroll             | False       |
+--------------------------------------+------+---------------+-------------+--------------------+-------------+

openstack baremetal node show 831ac23b-7daa-462b-ab28-6dd2972c5000
```

Change Node Power State (开机关机等?)
```
openstack baremetal node power off BM01
openstack baremetal node power on BM01
openstack baremetal node reboot BM01
```

#### 设置启动设备

例如设置为pxe启动
```
openstack baremetal node boot device set BM01 pxe
=> <device>  One of bios, cdrom, disk, pxe, safe, wanboot
openstack baremetal node boot device show BM01
+-------------+-------+
| Field       | Value |
+-------------+-------+
| boot_device | pxe   |
| persistent  | False |
+-------------+-------+
=> 重启后，配置就会变化为None
```

#### 配置端口mac地址

创建裸机端口：
```
openstack baremetal port create --node  node_uuid node_mac_address
openstack baremetal port create --node  e6423e53-740a-46f6-8c24-06fe8f21e53a  52:54:84:00:00:f7
```
- node_uuid：创建node时生成的uuid
- node_mac_address：裸机的网卡mac地址；如果裸机上有多个网卡，就输入和Ironic Pxe服务相连的网卡；（Pxe简单说用于下载镜像，可以参考我的相关文章）

### kolla安装ironic

global.yml配置
```
enable_ironic: "yes"
ronic_dnsmasq_interface: "eth1"
ironic_cleaning_network: "enp4s3"
ironic_dnsmasq_dhcp_ranges:
  - range: "192.168.83.100,192.168.83.180"
    routers: "192.168.83.192"
ironic_dnsmasq_boot_file: pxelinux.0
ironic_inspector_kernel_cmdline_extras: ['ipa-lldp-timeout=90.0', 'ipa-collect-lldp=1']
ironic_http_port: "8089"
```

kolla容器:
- ubuntu-source-ironic-neutron-agent:yoga ironic_neutron_agent
- ubuntu-source-dnsmasq:yoga              ironic_dnsmasq
- ubuntu-source-ironic-pxe:yoga           ironic_http
- ubuntu-source-ironic-pxe:yoga           ironic_tftp
- ubuntu-source-ironic-inspector:yoga     ironic_inspector
- ubuntu-source-ironic-api:yoga           ironic_api
- ubuntu-source-ironic-conductor:yoga     ironic_conductor
- ubuntu-source-nova-compute-ironic:yoga  nova_compute_ironic

### 验证qemu-img生成pc硬盘系统

- 首先进入ubuntu 20.04 livecd

- 然后安装qemu-img工具

- 然后挂载img nfs服务器

- 最后转换img到pc硬盘
```
qemu-img convert -f qcow2 -O raw debian10.img /dev/sda
```
=> 比较慢，跟img的虚拟大小有关!!!

待尝试其他镜像: win10, win7, win2012, ubuntu 20.04, centos7等

- debian 10 => ok
- win10 => ok
- ubuntu 20.04 => ok
  focal-server-cloudimg-amd64.img
  网上的这个镜像不是很好, 不能自动扩容磁盘分区，居然没有物理网卡
  用自己安装的虚拟机ubuntu-kolla感觉挺好
- zstack => ok
  zstack c76系统，可以不错
- KSVD => ok

## devstack 安装使用ironic

```
# Reclone each time
RECLONE=no

# Enable Ironic plugin
enable_plugin ironic https://git.openstack.org/openstack/ironic stable/stein

# Enable Swift for the direct deploy interface.
enable_service s-proxy
enable_service s-object
enable_service s-container
enable_service s-account

# Swift temp URL's are required for the direct deploy interface
SWIFT_ENABLE_TEMPURLS=True

# Create 3 virtual machines to pose as Ironic's baremetal nodes.
IRONIC_VM_COUNT=1
IRONIC_BAREMETAL_BASIC_OPS=True
DEFAULT_INSTANCE_TYPE=baremetal

# Enable additional hardware types, if needed.
#IRONIC_ENABLED_HARDWARE_TYPES=ipmi,fake-hardware
# Don't forget that many hardware types require enabling of additional
# interfaces, most often power and management:
#IRONIC_ENABLED_MANAGEMENT_INTERFACES=ipmitool,fake
#IRONIC_ENABLED_POWER_INTERFACES=ipmitool,fake
# The 'ipmi' hardware type's default deploy interface is 'iscsi'.
# This would change the default to 'direct':
#IRONIC_DEFAULT_DEPLOY_INTERFACE=direct

# Change this to alter the default driver for nodes created by devstack.
# This driver should be in the enabled list above.
IRONIC_DEPLOY_DRIVER=ipmi

# The parameters below represent the minimum possible values to create
# functional nodes.
IRONIC_VM_SPECS_RAM=1280
IRONIC_VM_SPECS_DISK=10

# Size of the ephemeral partition in GB. Use 0 for no ephemeral partition.
IRONIC_VM_EPHEMERAL_DISK=0

# To build your own IPA ramdisk from source, set this to True
IRONIC_BUILD_DEPLOY_RAMDISK=False

VIRT_DRIVER=ironic

# Log all output to files
LOGFILE=/opt/stack/devstack.log
LOGDIR=/opt/stack/logs
IRONIC_VM_LOG_DIR=/opt/stack/ironic-bm-logs
```

## FAQ

#### ironic node 一直是 wait call-back 状态

内存不足?

## 其他资料

- [理解裸机部署过程ironic](https://www.cnblogs.com/menkeyi/p/6063557.html)

https://ironic-book.readthedocs.io/zh_CN/latest/inspector/inspector.html
4.0 Inspector 介绍
在我们注册完 ironic-node 之后，我们需要把裸机的硬件信息更新到 node 表里。如果数量比较少，我们可以手动添加，但是如果是大规模部署，显然不适合手动添加。另外还有 port 的创建，裸机网口和交换机的链接关系等，都不适合自动添加。
ironic inspector 主要是帮助我们收集裸机信息的。
=> 但是IPMI不支持?

[(好)Ironic 裸金属管理服务 原创](https://blog.51cto.com/u_15301988/3160308)
- available：用户可以对一个处于可用状态的裸金属节点发起 actice API 请求执行操作系统部署，请求的同时需要将部署的详细信息（e.g. user-image、instance metadata、网络资源分配）持久化到裸金属数据库表记录中；
- deploying：部署准备阶段，此时 Ironic 会主动 cache ramdisk 到 ironic-conductor 并执行启动动作。如果此时的裸金属节点处于开启状态则执行重启动作；
- wait callback：等待裸金属节点完成启动或重启，Ironic 根据不同 Driver 类型的策略控制裸金属节点进入操作系统引导（BootLoader）。PXE 是其默认的引导方式，在这个阶段 Ironic 会等待裸金属节点的 BootLoader 进入 ramdisk，运行在 ramdisk 中的 ironic-python-agent 会回调 Ironic，告知裸金属节点已经接收 ironic-python-agent 的控制，可以进一步执行 user-image 的注入动作，并监控进度。待 user-image 注入完成后，Ironic 会进一步控制裸金属节点从 user-image 启动，并完成控制层面的数据维护；
- active：此状态表示裸金属节点的操作系统部署完成，但并不代表操作系统已经加载完成，裸金属节点的操作系统加载仍需要一定的等待时间。
=> 确实是pxe安装系统啊?

配置 Provisioning Network
首先配置一个 Physical Network 作为 Provisioning Network，用于提供 DHCP、PXE 功能，即裸金属节点部署网络。

配置新的 Physical Network
=> 需要配置安装网络? physnet1

[(好)浅谈pxe和ipxe](https://zhuanlan.zhihu.com/p/591334237)
iPXE 对 PXE 功能进行了扩展，是先前的 PXE 实现的超集，支持更多协议。最为主要的是，iPXE 支持灵活的配置脚本。

实际上即使不使用iPXE，仅使用原生的PXE也是可以实现自动部署的，但是我们增加了返回iPXE启动固件的步骤，原因是：

- iPXE支持HTTP协议，可以通过http、ISCSI SAN、Fibre Channel SAN via FCoE AoE SAN wireless network Infiniband network等方式启动
- 开源的iPXE允许我们做适配性修改
- iPXE 支持http协议的web server启动，我们可以设置统一的http请求，在web server端实现下发不同启动模板的逻辑，并可以添加认证功能
- 适配性强，除了传统X86架构，还引进了国产ARM架构，我们只需要编译一个ARM架构的iPXE启动程序，即可快速适配新架构服务器的自动部署flat_networks = public


[pxe之linux ipxe](https://www.jianshu.com/p/e60dce231e61)
Tiny PXE Server (mistyprojects.co.uk)这个东东过于强大，这里不做描述
配置简单，操作可视，一个鼠标就搞出高大上的PXE server，老夫得此佳软，夫复何求啊！ 啊！~
=> 使用tiny core linux, 一步一步制作一个pxe服务器 => 还制作成了iso...

[IRONIC的网络方案系列（一）](https://cloud.tencent.com/developer/news/161748)
- 1）：Ironic使用IPMI控制物理服务器的上下电、设置开机启动顺序（PXE启动或DISK启动）、获取电源状态、获取传感器状态、控制台重定向等。
- 2）：Ironic 使用PXE引导启动用于部署的ramdisk，且这个ramdisk内包含一个agent。它与Ironic交互，执行Ironic下发的命令。注，虽然Ironic支持iScsi和PXE等多种部署方式，本文以agent部署方式为例说明。
- 3）：cloud-init, 与虚拟机镜像一样，Ironic通过集成在镜像中的cloud-init初始化操作系统。包括创建用户、修改密码、配置网络等。

[(好)Ironic介绍](https://doodu.gitbooks.io/openstack/content/ironicji_zhu_fen_xiang.html)
我们把fake驱动排除，其他的驱动可以分为两类：

- 一是以pex 或者 iscsi 为前缀的驱动采用PXE部署机制，这些驱动将根硬盘作为iSCSI设备暴露给ironic conductor，由conductor将镜像复制到这里.
- 二是以agent_ 为前缀的驱动采用Agent部署机制，conductor准备一个存储在swift上的镜像URL给IPA，由IPA下载镜像和完成部署的操作。
从Kilo版开始，所有驱动使用agent进行部署。

## 其他

旧的调研单 #29923

## 参考资料

- [openstack官方ironic 架构](https://docs.openstack.org/ironic/latest/user/architecture.html)
