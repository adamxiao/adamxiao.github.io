# openstack ironic裸金属管理

#### 扩展调研问题

- 裸金属机器系统的网络配置?
  => 例如配置bond口, 配置网卡静态ip?
- ironic还可以对节点硬盘RAID?
- ironic还可以对节点系统安装应用程序?
- ironic展示节点的控制台console?
- ironic使用inspector获取硬件配置?

#### iornic实现的功能

- 使用IPMI管理裸设备
  例如开机关机重启，设置pxe启动, 设置硬盘等

- 部署系统到裸设备上
  例如部署centos系统

[简书 - OpenStack - Ironic](https://www.jianshu.com/p/ab799d414158)
OpenStack Ironic就是一个进行裸机部署安装的项目。

Ironic实现的功能，就是可以很方便的对指定的一台或多台裸机，执行：
- （1）硬盘RAID、分区和格式化；
- （2）安装操作系统、驱动程序；
- （3）安装应用程序。

#### 安装ironic

关键字《kolla-ansible enable ironic》《kolla-ansible 启用 ironic》

[(kolla官方文档)Ironic - Bare Metal provisioning](https://docs.openstack.org/kolla-ansible/latest/reference/bare-metal/ironic-guide.html)
https://docs.openstack.org/kolla-ansible/rocky/reference/ironic-guide.html

参考kolla官方文档，安装ironic环境非常容易

下载部署内核和镜像(配置inspector需要...)
```
curl https://tarballs.opendev.org/openstack/ironic-python-agent/dib/files/ipa-centos9-master.kernel \
  -o /etc/kolla/config/ironic/ironic-agent.kernel

curl https://tarballs.opendev.org/openstack/ironic-python-agent/dib/files/ipa-centos9-master.initramfs \
  -o /etc/kolla/config/ironic/ironic-agent.initramfs
```

在个global.yml中, 添加iron配置(基本参考官方文档)
```
enable_ironic: "yes"
ironic_dnsmasq_interface: "enp4s3"
ironic_cleaning_network: "public1"
ironic_dnsmasq_dhcp_range: "192.168.83.100,192.168.83.180,255.255.255.0"
ironic_dnsmasq_default_gateway: 192.168.83.192
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

ironic服务列表
```
$ docker ps | grep ironic
ironic_neutron_agent => 提供dhcp, 带pxe信息?
nova_compute_ironic => 创建裸金属主机实例入口点?
ironic_dnsmasq
ironic_http
ironic_tftp
ironic_inspector
ironic_api => 关键api入口
ironic_conductor => 核心ironic处理程序
```

#### 系统部署流程

我们把fake驱动排除，其他的驱动可以分为两类：
- 一是以pex 或者 iscsi 为前缀的驱动采用PXE部署机制，这些驱动**将根硬盘作为iSCSI设备暴露给ironic conductor，由conductor将镜像复制到这里.**
- 二是以agent_ 为前缀的驱动采用Agent部署机制，conductor准备一个存储在swift上的镜像URL给IPA，由IPA下载镜像和完成部署的操作。


参考官方文档: https://docs.openstack.org/ironic/yoga/user/architecture.html

以下是我验证的，官方的系统部署安装流程:
(还有其他系统安装部署方法，暂未调研)

Example: PXE Boot and Direct Deploy Process¶
This process is how Direct deploy works.
![](2023-07-11-15-57-01.png)

=> 注意： 是通过节点的网络接口获取dhcp，配置pxe的，而不是ironic的inspector dhcp...

#### 配置 Provisioning Network

=> 就是系统安装部署获取pxe dhcp ip地址的网络
(目前我就复用public1网络即可)

参考: https://blog.51cto.com/u_15301988/3244722

首先配置一个 Physical Network 作为 Provisioning Network，用于提供 DHCP、PXE 功能，即裸金属节点部署网络。

#### 裸金属服务器的生命周期

[IRONIC的网络方案系列（一）](https://cloud.tencent.com/developer/news/161748)

Ironic是OpenStack社区的子项目，专门用于提供裸机服务。它既可以独立使用也可以与nova、neutron等组件集成使用。对于被Ironic管理的物理服务器而言，主要有上架、部署、回收这三个阶段。

- 上架阶段指的是，当物理服务器完成硬件安装、网络连线等工作后。由管理员将机器的信息注册到Ironic中进行纳管。这个阶段，需要使用Ironic inspect功能以实现物理服务器硬件配置信息以及上联接入交换机信息的自动采集。

- 部署阶段指的是，当物理服务器完成上架后，处于可用状态。租（用）户根据业务需要指定镜像、网络等信息创建物理服务器实例。云平台执行资源调度、操作系统安装、网络配置等工作。有别于传统的人工部署和预先部署，租户可以在任意时刻按需选择不同的镜像、网络等信息。这个阶段，需要使用Ironic provision功能以实现配置信息的下发与自动化部署。一旦实例创建成功后，租（用）户可以使用物理服务器运行业务。

- 回收阶段指的是，当物理服务器完成使用，由租（用）户申请释放资源。这个阶段，可以使用Ironic clean功能清理物理服务器上的残留数据。

#### 裸金属节点状态机

Ironic状态机：
[(好)Ironic 裸金属管理服务 原创](https://blog.51cto.com/u_15301988/3160308)
[ironic官方文档 - 状态机](https://docs.openstack.org/ironic/latest/user/states.html)

![](../imgs/69c1621926449668895fab770923672f.webp)

状态变更过程(管理员录入裸金属节点的流程):
- 注册节点, 节点状态为enroll
- 验证节点, 节点状态变为verifing, 然后manage
- 发布节点, 节点状态变为available

节点发布后，就可以用来部署用户镜像，制作虚拟机实例了，后续的状态变更见官方文档

[(好)Ironic 裸金属管理服务 原创](https://blog.51cto.com/u_15301988/3160308)
- available：用户可以对一个处于可用状态的裸金属节点发起 actice API 请求执行操作系统部署，请求的同时需要将部署的详细信息（e.g. user-image、instance metadata、网络资源分配）持久化到裸金属数据库表记录中；
- deploying：部署准备阶段，此时 Ironic 会主动 cache ramdisk 到 ironic-conductor 并执行启动动作。如果此时的裸金属节点处于开启状态则执行重启动作；
- wait callback：等待裸金属节点完成启动或重启，Ironic 根据不同 Driver 类型的策略控制裸金属节点进入操作系统引导（BootLoader）。PXE 是其默认的引导方式，在这个阶段 Ironic 会等待裸金属节点的 BootLoader 进入 ramdisk，运行在 ramdisk 中的 ironic-python-agent 会回调 Ironic，告知裸金属节点已经接收 ironic-python-agent 的控制，可以进一步执行 user-image 的注入动作，并监控进度。待 user-image 注入完成后，Ironic 会进一步控制裸金属节点从 user-image 启动，并完成控制层面的数据维护；
- active：此状态表示裸金属节点的操作系统部署完成，但并不代表操作系统已经加载完成，裸金属节点的操作系统加载仍需要一定的等待时间。

#### 添加节点

注意: 添加节点，指定部署镜像，部署驱动等

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

#### 准备部署内核和镜像

下载部署内核和镜像, 主要有coreos, tinyipa, centos系统的 (也可以自己构建，不过我一直没构建出来...)

https://docs.openstack.org/ironic-python-agent/queens/install/index.html
[真官方文档 - Installing Ironic Python Agent](https://docs.openstack.org/ironic-python-agent/yoga/install/index.html)

下载tinyipa使用
```
wget https://tarballs.opendev.org/openstack/ironic-python-agent/tinyipa/files/tinyipa-stable-yoga.gz
wget https://tarballs.opendev.org/openstack/ironic-python-agent/tinyipa/files/tinyipa-stable-yoga.vmlinuz
```

部署时，通过这个部署内核和内存镜像，把机器pxe启动到部署系统中，然后安装用户系统镜像到硬盘上
```
openstack image create --disk-format aki --container-format aki --public \
  --file ironic-agent.kernel deploy-vmlinuz

openstack image create --disk-format ari --container-format ari --public \
  --file ironic-agent.initramfs deploy-initrd
```

可以修改现有initramfs的用户密码，进行调试

[Ironic Python Agent (IPA)](https://docs.openstack.org/kayobe/latest/configuration/reference/ironic-python-agent.html)
=> kolla构建IPA镜像? => 未尝试

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

#### 安装客户端工具

```
# ubuntu
apt install -y python3-ironicclient
# 或者pip安装
pip install python-ironicclient
```

#### 杂项命令

列举所有驱动
```
openstack baremetal driver list
```

查看用到的 IPMI 的所有 Ironic Driver
```
openstack baremetal driver show ipmi
```

打印出 IPMI 驱动程序的属性清单
```
openstack baremetal driver property list ipmi
```

#### 创建节点

ipmi协议端口默认是623, udp, 下面的节点使用vbmc虚拟机模拟bmc物理机

注册节点(注意: 需要提供部署内核和镜像)
```
export VMLINUZ_UUID=$(openstack image list | awk '/deploy-vmlinuz/ { print $2 }')
export INITRD_UUID=$(openstack image list | awk '/deploy-initrd/ { print $2 }')

openstack baremetal node create --driver ipmi --name VM01 \
  --driver-info ipmi_port=6230 --driver-info ipmi_username=admin \
  --driver-info ipmi_password=password \
  --driver-info ipmi_address=10.90.2.250 \
  --resource-class baremetal-resource-class \
  --property cpus=4 \
  --property memory_mb=4096 --property local_gb=100 \
  --property cpu_arch=x86_64 \
  --driver-info deploy_kernel=$VMLINUZ_UUID \
  --driver-info deploy_ramdisk=$INITRD_UUID
```

以及给节点创建网卡(创建裸机端口)：
```
NODE_UUID=$(openstack baremetal node list | awk '/VM01/ {print $2}')
NODE_MAC_ADDRESS=aa:bb:cc:dd:ee:ff
openstack baremetal port create $NODE_MAC_ADDRESS \
  --node $NODE_UUID \
  --physical-network physnet1
```
- NODE_UUID：创建node时生成的uuid
- NODE_MAC_ADDRESS：裸机的网卡mac地址；如果裸机上有多个网卡，就输入和Ironic Pxe服务相连的网卡；（Pxe简单说用于下载镜像，可以参考我的相关文章）

查看节点
```
openstack baremetal node list
+--------------------------------------+------+---------------+-------------+--------------------+-------------+
| UUID                                 | Name | Instance UUID | Power State | Provisioning State | Maintenance |
+--------------------------------------+------+---------------+-------------+--------------------+-------------+
| 831ac23b-7daa-462b-ab28-6dd2972c5000 | BM01 | None          | power on    | enroll             | False       |
+--------------------------------------+------+---------------+-------------+--------------------+-------------+

openstack baremetal node show 831ac23b-7daa-462b-ab28-6dd2972c5000
```

管理并检查节点状态为可用
```
openstack baremetal node manage BM01
openstack baremetal node provide BM01
```

Change Node Power State (开机关机等?)
```
openstack baremetal node power off BM01
openstack baremetal node power on BM01
openstack baremetal node reboot BM01
```

#### 创建flavor

类似于裸金属节点的机型吧 (openstack 创建实例都是需要制定flavor的!)
```
openstack flavor create my-baremetal-flavor \
  --ram 512 --disk 1 --vcpus 1 \
  --property resources:CUSTOM_BAREMETAL_RESOURCE_CLASS=1 \
  --property resources:VCPU=0 \
  --property resources:MEMORY_MB=0 \
  --property resources:DISK_GB=0
```

#### 设置节点启动设备

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

对应ipmi命令如下?
```
ipmitool -I lanplus -H xxx -U xxx -P xxx chassis bootdev pxe  
ipmitool -I lanplus -H xxx -U xxx -P xxx chassis power reset
```

### 系统部署细节调研

#### pxe启动部署镜像

ironic_http容器中会配置这个配置: /var/lib/ironic/httpboot/52:54:00:5a:b2:65.conf => f9d4b0fd-a8d0-4685-8a5f-da3f69249fb4/config
```
#!ipxe

set attempts:int32 10
set i:int32 0

goto deploy

:deploy
imgfree
kernel http://10.30.2.98:8089/f9d4b0fd-a8d0-4685-8a5f-da3f69249fb4/deploy_kernel selinux=0 troubleshoot=0 text nofb nomodeset vga=normal console=tty0 console=ttyS0,115200n8 ipa-api-url=http://10.30.2.91:6385 ipa-global-request-id=req-24f82dcf-268d-48b1-b6a7-f3b601ae1733 BOOTIF=${mac} initrd=deploy_ramdisk || goto retry

initrd http://10.30.2.98:8089/f9d4b0fd-a8d0-4685-8a5f-da3f69249fb4/deploy_ramdisk || goto retry
boot
```
=> 6385是ironic_api监听的端口

#### ipa安装部署系统流程步骤

查看ipa调试日志, 发现它在下载镜像, 安装到硬盘上, 然后校验?
```
ironic-python-agent[414]: 2023-07-14 13:26:47.204 414 INFO root [-] Picked root device /dev/vda for node f9d4b0fd-a8d0-4685-8a5f-da3f69249fb4 based on root device hints None
ironic-python-agent[414]: 2023-07-14 13:26:47.205 414 INFO ironic_python_agent.extensions.standby [-] Attempting to download image from http://10.30.2.98:8089/agent_images/f9d4b0fd-a8d0-4685-8a5f-da3f69249fb4
ironic-python-agent[414]: 2023-07-14 13:27:31.760 414 INFO ironic_python_agent.extensions.standby [-] Image streamed onto device /dev/vda in 44.554930210113525 seconds
ironic-python-agent[414]: 2023-07-14 13:27:31.760 414 DEBUG ironic_python_agent.extensions.standby [-] Verifying image at /dev/vda against sha512 checksum 2238ec208cf2c91330fb5a1da8a7e0725250dded2d7a68368f3a35e27c9530d5e4668043175dbdf5558100b1a1dbded0e388ac4f6c2b3e5c1c551304bbaa22dd verify_image /opt/ironic-python-agent/lib64/python3.6/site-packages/ironic_python_agent/extensions/standby.py:395
ironic-python-agent[414]: 2023-07-14 13:27:31.760 414 DEBUG ironic_python_agent.extensions.standby [-] Verifying image at /dev/vda against sha512 checksum 2238ec208cf2c91330fb5a1da8a7e0725250dded2d7a68368f3a35e27c9530d5e4668043175dbdf5558100b1a1dbded0e388ac4f6c2b3e5c1c551304bbaa22dd verify_image /opt/ironic-python-agent/lib64/python3.6/site-packages/ironic_python_agent/extensions/standby.py:395
```

镜像大小就是qcow2镜像的大小，改成raw格式了?
```
(ironic-http)[root@kolla images]# ls f9d4b0fd-a8d0-4685-8a5f-da3f69249fb4/
disk
(ironic-http)[root@kolla images]# pwd
/var/lib/ironic/images
(ironic-http)[root@kolla images]# ls -li f9d4b0fd-a8d0-4685-8a5f-da3f69249fb4/
total 803716
15344498 -rw-r--r-- 2 ironic ironic 2147483648 Jul 14 17:00 disk
```

关键字《ironic-python-agent安装系统流程》

[Ironic中pxe driver和agent driver的区别](https://www.cnblogs.com/zhangyufei/p/6410753.html)

历史问题：
以pxe_ipmitool 和agent_ipmitool为例，看起来似乎前者不使用ironic-python-agent，后者使用，但是实际上两者都使用ironic-python-agent进行部署，现在的命名其实是历史遗留问题。

在kilo版本之前，pxe_ipmitool 使用ramdisk进行部署，ramdisk中只有bash脚本，没有ironic-python-agent，但是后来为了减少开发和维护的复杂度，Kilo之后，pxe_ipmitool 也使用ironic-python-agent部署。

对比：
Ironic部署裸机时，裸机在内存中使用deploy镜像启动一个自带ironic-python-agent的操作系统。如果使用的pxe_ipmitool 驱动，conductor发送rest请求，使得agent将识别到的第一块磁盘，通过iscsi协议映射到conductor节点上。然后conductor从glance下载对应的镜像，convert成raw格式，写入目标磁盘。如果使用的是agent_ipmitool驱动，conductor发送rest请求，agent自行下载镜像写入裸机磁盘上。

对于qcow2 image:

如果使用agent_ipmitool，每次都要下载到内存中，convert成raw格式，再写入磁盘，对目的节点内存要求更大，如果是disk size 10G的大镜像，那么就要求内存10G以上如果使用pxe_ipmitool , 每次格式转换在conductor节点上做，缓存到conductor节点上，传输的时候通过dd写入网络，对目的机器内存无要求，但是ironic节点压力大，并且需要额外的空间存放ironic缓存的镜像。

对于raw image:

agent_ipmitool支持将raw格式的镜像直接写入磁盘，不需要先cache到内存中，所以对内存无额外要求。这种情况下，唯一的问题是大规模部署时，每个节点都要向glance去下载一次镜像，glance的压力会更大，但是如果是pxe_ipmi driver，对ironic conductor的压力也会更大，所以也不能算是一个缺点。

结论：
agent_ipmitool + raw 镜像看起来是最完美的解决方案，但是可惜的是agent_ipmitool依赖于swift或者ceph radosgw，如果是rbd方式或者filesystem方式存放镜像，agent driver不支持。问了下社区相关人员，他们没有解决这个问题的打算。或者可以通过二次开发解决来这个问题。

#### 验证qemu-img生成pc硬盘系统

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

#### vbmc模拟裸金属机器

kolla部署ironic的文档有相关资料:
https://brk3.github.io/post/kolla-ironic-libvirt/

安装使用, 例如把libvirt虚拟机virtual-baremetal配置作为一个裸金属机器:
```
yum install python-pip python-devel libvirt-devel gcc
pip install virtualbmc
vbmc add virtual-baremetal --port 6230 --username admin --password password --address 0.0.0.0
vbmc start --libvirt-uri=qemu:///session virtual-baremetal
```

使用ipmitool验证:
```
ipmitool -I lanplus -H <host node ip> -L ADMINISTRATOR -p 6230 \
  -U admin -R 12 -N 5 -P password power status
```

注意事项:
- vbmcd 这个命令启动vbmc程序
- $HOME/.vbmc/master.pid 这个可能要启动前需要手动删除

关键字《vbmc docker container》

https://hub.docker.com/r/solidcommand/virtualbmc
```
docker run -d --name virtualbmc --network host \
  -v $HOME/.ssh/id_rsa:/virtualbmc/.ssh/id_rsa:ro \
  solidcommand/virtualbmc

docker exec -i -t virtualbmc vbmc add ironic-vm1 --port 6231 --libvirt-uri 'qemu+ssh://root@node8/system' --no-daemon
docker exec -i -t virtualbmc vbmc add ironic-vm1 --port 6231 --libvirt-uri 'qemu+tcp://root@node8/system' --no-daemon
docker exec -i -t virtualbmc vbmc start 'ironic-vm1' --no-daemon
docker exec -i -t virtualbmc vbmc list

ipmitool -I lanplus -U admin -P password -H 127.0.0.1 -p 6231 power status
```

## 概念

### 部署方式

参考openstack ironic架构文档: https://docs.openstack.org/ironic/yoga/user/architecture.html

默认是direct部署?

Example: PXE Boot and Direct Deploy Process¶
This process is how Direct deploy works.
![](2023-07-11-15-57-01.png)

=> 注意： 是通过节点的网络接口获取dhcp，配置pxe的，而不是ironic的dhcp...

https://docs.openstack.org/ironic/yoga/admin/interfaces/deploy.html
还有其他部署方式:

- Ansible deploy
- Anaconda deploy
- Ramdisk deploy
- Custom agent deploy

https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html-single/performing_an_advanced_rhel_9_installation/index
RHEL9可以以如下方式安装:
- GUI-based installations
- System or cloud image-based installations
- Advanced installations
  - Perform an automated RHEL installation using Kickstart
  - Register and install RHEL from the Content Delivery Network

#### 准备部署镜像

=> agent下载镜像进行安装，而不是提供iscsi设备安装

[(好)Ironic介绍](https://doodu.gitbooks.io/openstack/content/ironicji_zhu_fen_xiang.html)
我们把fake驱动排除，其他的驱动可以分为两类：

- 一是以pex 或者 iscsi 为前缀的驱动采用PXE部署机制，这些驱动将根硬盘作为iSCSI设备暴露给ironic conductor，由conductor将镜像复制到这里.
- 二是以agent_ 为前缀的驱动采用Agent部署机制，conductor准备一个存储在swift上的镜像URL给IPA，由IPA下载镜像和完成部署的操作。
从Kilo版开始，所有驱动使用agent进行部署。

### 其他

[【重识云原生】计算第2.6节——裸金属方案](https://blog.csdn.net/junbaozi/article/details/123834314)
=> 提到了很多裸金属支持的功能

- 1.2.4 带外批量运维
  支持在线批量管理物理服务器生命周期，如开关机、重启、挂卷、删除、监控、远程登录、状态查询等。
- 1.2.5 VPC网络+自定义网络
  支持多种方式与虚拟机互联，可以建立虚拟私有网络（VPC），也可以通过自定义网络，以满足不同网络安全需求。VPC网络构建出一个安全隔离的网络环境，可以灵活自定义IP地址范围、配置路由表和网关、 创建子网等，实现弹性IP、弹性带宽、共享带宽等功能。
- 1.2.8 管理节点提供部署服务
  小规模部署服务如DHCP服务、TFTP服务、PXE服务等可以由管理节点提供，而不需要单独配置一台部署服务器，造成资源浪费；当然，达到一定规模，单独配置部署服务器十分有必要的，可以减轻管理节点压力，专机专用。

从PACKET的架构图看，PACKET的裸金属云服务主要分为以下几个模块：
- Magnum IP模块的功能是多租户的IP地址管理，IPAM是IP Address Management的缩写。
- PB&J模块的功能是电源和启动管理。
- Tinkerbell模块的作用是iPXE服务器和镜像管理。
- Soren模块的功能是流量管理和分析。
- Narwhal模块的功能是物理交换机和SDN的管理。
- SOS模块的功能是串口和远程登录的管理。

服务器启动，通过iPXE引导已经制作好的iSCSI系统镜像，这样就免去了安装操作系统的过程，并且服务器也不需要系统硬盘，节省了成本。
=> 这个怎么实现的? 某些系统支持性不是很好吧?

网络方面，裸金属服务器本质上是运行在Underlay网络的，如果要和云上已有的云主机、云存储等云产品打通，需要为其封装成overlay网络，如此才能够和云主机一样的配置ACL、VPC、负载均衡等网络功能。

对于网络打通，一方面现有头部云厂商均基于智能网卡方案，在一张PCI扩展卡上实现了基于VirtIO的网络半虚拟化能力，以此完成Overlay网络封装；另一方，对于裸金属集群，会有专有裸金属网关来负责VPC网络打通（例如腾讯云的就叫XGW）。

裸金属服务基于开源社区OpenStack的Ironic组件能力，通过华为自研增强实现裸金属服务器的发放功能。裸金属服务通过PXE技术从服务器自动下载并加载操作系统，调用IPMI带外管理接口实现裸金属服务器的上电、下电、重启等操作，通过调用Nova组件的接口实现计算资源管理，调用Neutron组件的接口实现网络的发放和配置，调用Cinder组件的接口为裸金属服务器提供基于远端存储的云硬盘。通过Cloud-init从metadata服务等数据源获取数据并对裸金属服务器进行配置，包括：主机名、用户名、密码等。
=> cloud-init配置, 我这边失败的, why?

裸金属镜像里面不植入任何管理软件，如果用户有自动化挂载云硬盘和组Bond的高级特性需求，可选择在裸金属服务里面安装华为提供的Agent完成挂载云硬盘和组Bond功能。

3. Neutron中的SDN插件会接收到Port创建和更新的消息，通过SDN设置TOR交换机上的VLAN，自动化完成网络配置工作，无需手动配置交换机。

https://github.com/huaweicloudDocs/bms/blob/master/cn.zh-cn/API%E5%8F%82%E8%80%83/%E5%88%9B%E5%BB%BA%E8%A3%B8%E9%87%91%E5%B1%9E%E6%9C%8D%E5%8A%A1%E5%99%A8.md
说明： 此时，对于安装了Cloud-init镜像的Linux裸金属服务器，若指定user_data字段，则该adminPass字段无效；对于安装了Cloudbase-init镜像的Windows裸金属服务器，若指定元数据metadata字段中的admin_pass，则该adminPass字段无效。
- 不支持文件注入功能。
- 目前仅支持创建包周期裸金属服务器。
- 不支持市场镜像创建裸金属服务器

[HCS裸金属服务介绍](https://www.huoban.com/news/post/713.html)
华为HCS裸金属服务基于开源社区OpenStack的Ironic组件能力，并通过华为自研增强实现裸金属服务器的发放功能。裸金属服务通过PXE技术从服务器自动下载并加载操作系统，调用IPMI带外管理接口实现裸金属服务器的上电、下电、重启等操作，通过调用Nova组件的接口实现计算资源管理，调用Neutron组件的接口实现网络的发放和配置，调用Cinder组件的接口为裸金属服务器提供基于远端存储的云硬盘。通过Cloud-init从metadata服务等数据源获取数据并对裸金属服务器进行配置，包括：主机名、用户名密码等。

[使用disk-image-builder（DIB）制作Ironic 裸金属镜像](http://120.132.124.40:8877/zixun/24411.html)
很奇怪前面定义的密码安装完系统之后不能登录，

https://doc.hcs.huawei.com/zh-cn/api/ecs/ApicomCreateServersV2.html
使用支持Cloud-init或Cloudbase-init功能的镜像创建云服务器时，adminPass参数无效。对于Linux弹性云服务器，如果需要注入密码，只能使用user_data进行注入，对于Windows弹性云服务器，如果需要注入密码，只能通过元数据admin_pass进行注入。


#### 网络

[ironic-简介](https://www.bladewan.com/2017/05/08/ironic/)
在Newton版前，ironic都是不支持多租户，都是在一个flat网络上，互相之间是没有隔离关系的。

=> 后面的版本怎么支持多租户的? => 优先级低

[OpenStack Ironic 裸金属服务搭建](https://howardlau.me/programming/openstack-ironic-baremetal.html)
上图是一种可行的网络拓扑，其中 API 和 DB 服务器和普通的 Web 服务器一样，可以部署在任意的地方，只要裸机控制节点和裸金属服务器可以访问就行了，托管在云上也是 OK 的。裸机控制节点则建议提供 3 个不同的子网，一个用于访问 API 服务器，一个用于提供裸金属集群的业务网，一个用于连接管理接口的管理网。

开关机的流程：
- 6.IPA 启动后，回调 Conductor，通知它下载用户镜像，然后 IPA 开始部署用户操作系统镜像
- ...

创建镜像
从虚拟机镜像转换
先像平时一样把虚拟机安装好，然后装好硬件需要的驱动，打开所有网络接口的 DHCP 功能，安装 cloud-init 包和其他需要的软件，把 vmlinuz 和 initrd 拷贝出来，导出虚拟磁盘之后用 qemu-img 转换 qcow2。

驱动用的是idrac, 是什么? => 类似ipmi? => 还用了redfish
```
export SERVER_NAME=bm-server
export DRIVER=idrac
baremetal node create --driver $SERVER_NAME --name $SERVER_NAME --resource-class $FLAVOR_NAME
```

这时候，你可以手动用 baremetal port create 命令创建网卡 MAC 和节点 UUID 对应的关系，也可以用 baremetal node inspect 命令让 Ironic 自动调取远程管理接口来填充信息。
=> 这个驱动可以inspect获取硬件信息, 而ipmi驱动不行。。。

#### 制作部署用户镜像

问题:
- 跟制作openstack镜像有什么区别?
  应该是多了一些物理设备驱动?
- 怎么支持部署用户镜像?
  就是网卡配置dhcp, 然后安装cloud-init?

[diskimage-builder官方参考手册](https://docs.openstack.org/diskimage-builder/latest/)

[Add images to the Image service](https://docs.openstack.org/ironic/yoga/install/configure-glance-images.html)
=> 上传用户镜像，设置内核，以及initramfs作用是啥? => 分区表镜像才设置这个属性!!!
For partition images to be used only with local boot (the default) the img_type property must be set:
```
 openstack image create my-image --public \
  --disk-format qcow2 --container-format bare \
  --property img_type=partition --file my-image.qcow2
```

#### 制作ironic-python-agent镜像

[官方文档 - diskimage-builder images](https://docs.openstack.org/ironic-python-agent-builder/latest/admin/dib.html)

ubuntu 20.04处理
```
export ELEMENTS_PATH=/usr/local/share/ironic-python-agent-builder/dib

cat > sources.list.debian << EOF
deb http://docker.iefcu.cn:5565/repository/bullseye-proxy/ bullseye main
deb http://docker.iefcu.cn:5565/repository/bullseye-proxy/ bullseye-updates main
EOF

export DIB_RELEASE=bullseye
export DIB_APT_SOURCES="$(pwd)/sources.list.debian"

export DIB_DEV_USER_USERNAME=ipa
export DIB_DEV_USER_PWDLESS_SUDO=yes
export DIB_DEV_USER_PASSWORD='123'
disk-image-create -o ironic-python-agent \
  debian ironic-python-agent-ramdisk devuser
```

https://docs.openstack.org/ironic-python-agent/queens/install/index.html
[真官方文档 - Installing Ironic Python Agent](https://docs.openstack.org/ironic-python-agent/yoga/install/index.html)
=> ipa镜像解释，最官方了...
下载tinyipa使用
```
wget https://tarballs.opendev.org/openstack/ironic-python-agent/tinyipa/files/tinyipa-stable-yoga.gz
wget https://tarballs.opendev.org/openstack/ironic-python-agent/tinyipa/files/tinyipa-stable-yoga.vmlinuz
```

[官方文档 - Troubleshooting Ironic-Python-Agent (IPA)](https://docs.openstack.org/ironic-python-agent/latest/admin/troubleshooting.html)
=> 刚好ipa安装部署系统，我想要调试，待看看 `sudo journalctl -u ironic-python-agent`
```
export DIB_DEV_USER_USERNAME=ipa
export DIB_DEV_USER_PWDLESS_SUDO=yes
export DIB_DEV_USER_PASSWORD='123'
export DIB_DEV_USER_AUTHORIZED_KEYS=$HOME/.ssh/id_rsa.pub
ironic-python-agent-builder -o /path/to/custom-ipa -e devuser debian
```

[ironic book - 6.0 Ironic 映像](https://ironic-book.readthedocs.io/zh_CN/latest/ironic/images.html)
=> 很多ironic的相关知识

制作ironic deploy镜像其实就是在普通镜像中添加一个ipa服务，用来裸机和ironic通信。
官方推荐制作镜像的工具有两个，分别是CoreOS tools和disk-image-builder 具体链接如下:
https://docs.openstack.org/project-install-guide/baremetal/ocata/deploy-ramdisk.html

User 映像
user 映像又分为 partition 映像和 whole disk 映像，两者的区别是 whole disk 映像包含分区表和 boot。目前 partition 映像已经很少 使用了，现在基本都使用 whole disk 映像。

镜像驱动问题
我们使用虚机制作的镜像安装在物理机上，很可能缺少驱动，而导致用户 系统起不来。这里我们以 CentOS 为例，说明如何重新制作驱动。
```
mount -o loop CentOS.iso /mnt
cd /mnt/isolinux
lsinitrd initrd.img | grep "\.ko" | awk -F / '{print $NF}' | tr "\n" " "

# 将如上命令获得的ko列表拷贝到 /etc/dracut.conf 中
add_drivers+=""

rm -rf /boot/*kdump.img
dracut --force
```

https://docs.openeuler.org/zh/docs/22.03_LTS/docs/thirdparty_migration/OpenStack-train.html
deploy ramdisk镜像制作
```
export DIB_DEV_USER_USERNAME=ipa \
export DIB_DEV_USER_PWDLESS_SUDO=yes \
export DIB_DEV_USER_PASSWORD='123'
ironic-python-agent-builder centos -o /mnt/ironic-agent-ssh -b origin/stable/rocky -e selinux-permissive -e devuser
```

[制作Openstack Ironic裸金属的部署镜像和系统镜像](https://zhuanlan.zhihu.com/p/350215847)

```
export DIB_DEV_USER_USERNAME=ipa
export DIB_DEV_USER_PASSWORD=123
export DIB_DEV_USER_PWDLESS_SUDO=YES
disk-image-create ironic-agent centos7 -o ironic-agent devuser
```
=> 安装报错: `Element 'ironic-agent' not found`

还可以用Buildroot创建OpenStack Ironic部署镜像...

#### irnoic使用的技术

=> 使用cloud-init初始化操作系统?
  => 还可以使用config driver?

[IRONIC的网络方案系列（一）](https://cloud.tencent.com/developer/news/161748)

在描述完物理服务器的组网图之后，接着简单概述下Ironic部署需要用到的技术。

- 1）：Ironic使用IPMI控制物理服务器的上下电、设置开机启动顺序（PXE启动或DISK启动）、获取电源状态、获取传感器状态、控制台重定向等。

- 2）：Ironic 使用PXE引导启动用于部署的ramdisk，且这个ramdisk内包含一个agent。它与Ironic交互，执行Ironic下发的命令。注，虽然Ironic支持iScsi和PXE等多种部署方式，本文以agent部署方式为例说明。

- 3）：cloud-init, 与虚拟机镜像一样，Ironic通过集成在镜像中的cloud-init初始化操作系统。包括创建用户、修改密码、配置网络等。

#### 裸金属终端控制台Console

=> 未验证, 后续调研一下

https://blog.51cto.com/u_15301988/3160308

Ironic 支持两种 Console 类型：

- Shellinabox
- Socat

Shellinabox 可以将终端输出转换成 Ajax 实现的 http 服务，可以直接通过浏览器访问，呈现出类似 Terminal 的界面。Socat 与 Shellinabox 类似，都是充当一个管道作用，只不过 Socat 是将终端流重定向到 TCP 连接。Shellinabox 是比较早的方式，它的限制在于只能在 Ironic Conductor 节点上运行 WEB 服务，访问范围受限，所以社区又用 Socat 实现了一套。Socat 提供 TCP 连接，可以和 Nova 的 Serial Console 对接。要使用这两者，需要在 Ironic Conductor 节点安装相应的工具。Socat 在 yum 源里就可以找到，Shellinabox 不在标准源里，要从 EPEL 源里下载，它没有外部依赖，所以直接下载这个 rpm 包安装就可以了。Ironic 的驱动中，以 Socat 结尾的驱动是支持 Socat 的，比如 agent_ipmitool_socat，其它的则是 Shellinabox 方式。使用哪种终端方式，在创建节点时要确定好。这两种方式都是双向的，可以查看终端输出，也可以键盘输入。

https://blog.csdn.net/OldHusband/article/details/112794051
```
openstack baremetal node set BM01 --console-interface ipmitool-socat
openstack baremetal node set BM01 --console-interface ipmitool-shellinabox

openstack baremetal node console enable $BAREMETAL_NODE_UUID
openstack baremetal node console show $BAREMETAL_NODE_UUID
```

#### 系统启动

[(好, 很长)Ironic介绍](https://doodu.gitbooks.io/openstack/content/ironicji_zhu_fen_xiang.html)
=> 还有代码分析...

- bootloader（引导程序，常见的有GRUB、LILO）
- kernel（内核）
- ramdisk（虚拟内存盘）
- initrd/initramfs （初始化内存磁盘镜像）

下面我们分别介绍每个概念：

- `引导加载程序`是系统加电后运行的第一段软件代码。PC机中的引导加载程序由BIOS(其本质就是一段固件程序)和位于硬盘MBR（主引导记录，通常位于第一块硬盘的第一个扇区）中的OS BootLoader（比如，LILO和GRUB等）一起组成。BIOS在完成硬件检测和资源分配后，硬盘MBR中的BootLoader读到系统的RAM中，然后控制权交给OS BootLoader。
- bootloader负责将kernel和ramdisk从硬盘读到内存中，然后跳转到内核的入口去运行。
- kernel是Linux的内核，包含最基本的程序。
- ramdisk是一种基于内存的虚拟文件系统，就好像你又有一个硬盘，你可以对它上面的文件添加修改删除等等操作。但是一掉电，就什么也没有了，无法保存。一般驱动程序放在这里面。
- initrd是boot loader initialized RAM disk, 顾名思义，是在系统初始化引导时候用的ramdisk。也就是由启动加载器所初始化的RamDisk设备，它的作用是完善内核的模块机制，让内核的初始化流程更具弹性；内核以及initrd，都由 bootloader在机子启动后被加载至内存的指定位置，主要功能为按需加载模块以及按需改变根文件系统。initramfs与initrd功能类似，是initrd的改进版本，改进了initrd大小不可变等等缺点。

#### IPMI接口

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

#### ironic-python-agent工作流程分析

https://docs.openstack.org/ironic-python-agent/latest/admin/how_it_works.html
=> 官方文档将原理?

```
使用tcpdump抓包 (6385为ironic api, 9999为ipa api)
tcpdump -v -i any -n tcp port 6385 or tcp port 9999 -s 8000 -w ~/adam.pcap
使用wireshark分析
http and ip.addr==10.90.4.179
```

GET / HTTP/1.1 => 获取api信息?
回复如下:
{"name": "OpenStack Ironic API", "description": "Ironic is an OpenStack project which enables the provision and management of baremetal machines.", "default_version": {"id": "v1", "links": [{"href": "http://10.90.2.252:6385/v1/", "rel": "self"}], "status": "CURRENT", "min_version": "1.1", "version": "1.78"}, "versions": [{"id": "v1", "links": [{"href": "http://10.90.2.252:6385/v1/", "rel": "self"}], "status": "CURRENT", "min_version": "1.1", "version": "1.78"}]}

GET /v1/lookup?addresses=52%3A54%3A84%3A00%3A02%3A94 HTTP/1.1 => 根据mac地址获取实例信息?
回复如下:
{"node": {"uuid": "e59cdb35-9764-459a-86dc-1fbca886b04e", "properties": {"cpus": 4, "memory_mb": 4096, "local_gb": 10, "cpu_arch": "x86_64", "vendor": "unknown"}, "instance_info": {"image_source": "16dae6a8-b0db-455a-ba7c-46fb71836d5b", "root_gb": "1", "swap_mb": "0", "display_name": "demo2", "vcpus": "1", "nova_host_id": "kolla2-ironic", "memory_mb": "512", "local_gb": "10", "image_type": "whole-disk", "image_disk_format": "raw", "image_checksum": null, "image_os_hash_algo": "sha512", "image_os_hash_value": "7f8188d635264e47e4daddc5aaf560b1e705d1a069a3b7dfa01cb6e6fb2911b6e7c6e1354f052ca192881e043cac0f4407cf500ccb56ffb37cab8697a36aa2f4", "image_url": "******", "image_container_format": "bare", "image_tags": [], "image_properties": {"stores": "file", "os_distro": "debian", "os_admin_user": "debian", "hw_disk_bus": "scsi", "os_hidden": false, "owner_specified.openstack.md5": "", "os_type": "linux", "os_version": "11.9.1", "virtual_size": 2147483648, "hw_scsi_model": "virtio-scsi", "owner_specified.openstack.sha256": "", "owner_specified.openstack.object": "images/debian-11-adam.img"}}, "driver_internal_info": {"content": "** Redacted - Requires baremetal:node:get:driver_internal_info permission. **"}, "links": [{"href": "http://10.90.2.252:6385/v1/nodes/e59cdb35-9764-459a-86dc-1fbca886b04e", "rel": "self"}, {"href": "http://10.90.2.252:6385/nodes/e59cdb35-9764-459a-86dc-1fbca886b04e", "rel": "bookmark"}]}, "config": {"metrics": {"backend": "noop", "prepend_host": false, "prepend_uuid": false, "prepend_host_reverse": true, "global_prefix": null}, "metrics_statsd": {"statsd_host": "localhost", "statsd_port": 8125}, "heartbeat_timeout": 300, "agent_token": "SxuToD6VNzUv4IoO-5mNN8flb6foqsDEeWMkB5XT7Jo", "agent_token_required": true}}

GET /v1/lookup?addresses=52%3A54%3A84%3A00%3A02%3A94&node_uuid=e59cdb35-9764-459a-86dc-1fbca886b04e HTTP/1.1 => 获取实例详细信息?
回复如下: 基本同上，就是隐藏了agent_token
{"node": {"uuid": "e59cdb35-9764-459a-86dc-1fbca886b04e", "properties": {"cpus": 4, "memory_mb": 4096, "local_gb": 10, "cpu_arch": "x86_64", "vendor": "unknown"}, "instance_info": {"image_source": "16dae6a8-b0db-455a-ba7c-46fb71836d5b", "root_gb": "1", "swap_mb": "0", "display_name": "demo2", "vcpus": "1", "nova_host_id": "kolla2-ironic", "memory_mb": "512", "local_gb": "10", "image_type": "whole-disk", "image_disk_format": "raw", "image_checksum": null, "image_os_hash_algo": "sha512", "image_os_hash_value": "7f8188d635264e47e4daddc5aaf560b1e705d1a069a3b7dfa01cb6e6fb2911b6e7c6e1354f052ca192881e043cac0f4407cf500ccb56ffb37cab8697a36aa2f4", "image_url": "******", "image_container_format": "bare", "image_tags": [], "image_properties": {"stores": "file", "os_distro": "debian", "os_admin_user": "debian", "hw_disk_bus": "scsi", "os_hidden": false, "owner_specified.openstack.md5": "", "os_type": "linux", "os_version": "11.9.1", "virtual_size": 2147483648, "hw_scsi_model": "virtio-scsi", "owner_specified.openstack.sha256": "", "owner_specified.openstack.object": "images/debian-11-adam.img"}}, "driver_internal_info": {"content": "** Redacted - Requires baremetal:node:get:driver_internal_info permission. **"}, "links": [{"href": "http://10.90.2.252:6385/v1/nodes/e59cdb35-9764-459a-86dc-1fbca886b04e", "rel": "self"}, {"href": "http://10.90.2.252:6385/nodes/e59cdb35-9764-459a-86dc-1fbca886b04e", "rel": "bookmark"}]}, "config": {"metrics": {"backend": "noop", "prepend_host": false, "prepend_uuid": false, "prepend_host_reverse": true, "global_prefix": null}, "metrics_statsd": {"statsd_host": "localhost", "statsd_port": 8125}, "heartbeat_timeout": 300, "agent_token": "******", "agent_token_required": true}}


POST /v1/heartbeat/e59cdb35-9764-459a-86dc-1fbca886b04e HTTP/1.1
Host: 10.90.2.252:6385
User-Agent: python-requests/2.27.1
Accept-Encoding: gzip, deflate
Accept: application/json
Connection: keep-alive
X-OpenStack-Ironic-API-Version: 1.68
Content-Type: application/json
X-OpenStack-Request-ID: req-22fdbffa-4a12-4cf4-ba40-88425c12f8b0

=> 居然使用https, 还使用了证书...
```
{"callback_url": "https://10.90.4.148:9999", "agent_token": "4Cm1DPVW2ecSbOQgUE3GE_lat9WYGhvRoji0PQQL60U",
"agent_version": "8.5.2.dev5", "agent_verify_ca": "..."}
```

HTTP/1.1 202 Accepted
date: Thu, 03 Aug 2023 06:44:42 GMT
server: Apache/2.4.41 (Ubuntu)
content-length: 0
x-openstack-ironic-api-minimum-version: 1.1
x-openstack-ironic-api-maximum-version: 1.78
x-openstack-ironic-api-version: 1.68
openstack-request-id: req-6ec70ded-98d8-47cc-ae39-b015d85f02b3

反向请求如下: (查看ipa的日志得到)
POST /v1/commands/?wait=true&agent_token=SxuToD6VNzUv4IoO-5mNN8flb6foqsDEeWMkB5XT7Jo HTTP/1.1
GET /v1/commands/ HTTP/1.1
 Asynchronous command execute_deploy_step started execution
POST /v1/commands/?wait=false&agent_token=SxuToD6VNzUv4IoO-5mNN8flb6foqsDEeWMkB5XT7Jo HTTP/1.1
 Asynchronous command prepare_image started execution

=> 估计就是执行命令, 等待或者不等待，以及查询命令执行状态?

关键字《ironic-python-agent callback_url use http》

打开ironic-conductor来分析?

https://docs.openstack.org/ironic-python-agent/victoria/install/index.html
=> 改为http的callback-url?
创建配置文件 /etc/ironic-python-agent.d/ironic_python_agent.conf
```
[DEFAULT]
listen_tls = False
advertise_protocol = http
enable_auto_tls = False # 这个参数很重要，否则会覆盖前面的参数。。。
```
ipa-advertise-protocol => 也可以通过这个内核参数决定?

=> callback-url的服务代码对应: ironic_python_agent/agent.py : serve_ipa_api
具体接口实现对应代码: ironic_python_agent/api/app.py : api_run_command

POST /v1/commands/?wait=true&agent_token=RftFPhmBhZDB_pp4NUhEXvgaRKSpYEXFLc6Y0axb8WY HTTP/1.1
```
{"name": "deploy.get_deploy_steps", "params": {"node": {"id": 13, "uuid": "735cab8e-e2ba-494f-a300-e4f1b4f24c53", "name": "VM01", "chassis_id": null, "instance_uuid": "08f0a731-6c65-49eb-97a3-8489b6677318", "driver": "ipmi", "driver_info": {"ipmi_port": 6231, "ipmi_username": "admin", "ipmi_password": "******", "ipmi_address": "10.60.5.113", "deploy_kernel": "c7bec1d1-a80e-4107-8ee6-ffb151032f9f", "deploy_ramdisk": "447ea833-36bd-4ca9-9312-bd0f72ab2690"}, "driver_internal_info": {"is_whole_disk_image": true, "deploy_steps": [{"step": "deploy", "priority": 100, "argsinfo": null, "interface": "deploy"}, {"step": "write_image", "priority": 80, "argsinfo": null, "interface": "deploy"}, {"step": "prepare_instance_boot", "priority": 60, "argsinfo": null, "interface": "deploy"}, {"step": "tear_down_agent", "priority": 40, "argsinfo": null, "interface": "deploy"}, {"step": "switch_to_tenant_network", "priority": 30, "argsinfo": null, "interface": "deploy"}, {"step": "boot_instance", "priority": 20, "argsinfo": null, "interface": "deploy"}], "deploy_boot_mode": "uefi", "deploy_step_index": 0, "last_power_state_change": "2023-08-03T09:22:14.772533", "agent_secret_token": "******", "agent_url": "http://10.90.4.135:9999", "agent_version": "8.5.2.dev5", "agent_last_heartbeat": "2023-08-03T09:23:15.426199"}, "clean_step": {}, "deploy_step": {"step": "deploy", "priority": 100, "argsinfo": null, "interface": "deploy"}, "raid_config": {}, "target_raid_config": {}, "properties": {"cpus": 4, "memory_mb": 4096, "local_gb": 10, "cpu_arch": "x86_64", "vendor": "unknown"}, "reservation": "kolla2", "conductor_affinity": 1, "conductor_group": "", "power_state": "power on", "target_power_state": null, "provision_state": "wait call-back", "provision_updated_at": "2023-08-03T09:22:26.000000", "target_provision_state": "active", "maintenance": false, "maintenance_reason": null, "fault": null, "console_enabled": false, "last_error": null, "resource_class": "baremetal-resource-class", "inspection_finished_at": null, "inspection_started_at": null, "extra": {}, "automated_clean": null, "protected": false, "protected_reason": null, "allocation_id": null, "bios_interface": "no-bios", "boot_interface": "ipxe", "console_interface": "no-console", "deploy_interface": "direct", "inspect_interface": "no-inspect", "management_interface": "ipmitool", "network_interface": "flat", "power_interface": "ipmitool", "raid_interface": "no-raid", "rescue_interface": "no-rescue", "storage_interface": "noop", "vendor_interface": "ipmitool", "traits": {"objects": []}, "owner": null, "lessee": null, "description": null, "retired": false, "retired_reason": null, "network_data": {}, "boot_mode": null, "secure_boot": null, "created_at": "2023-08-03T09:17:59.000000", "updated_at": "2023-08-03T09:23:15.431098", "instance_info": {"image_source": "16dae6a8-b0db-455a-ba7c-46fb71836d5b", "root_gb": "1", "swap_mb": "0", "display_name": "demo2", "vcpus": "1", "nova_host_id": "kolla2-ironic", "memory_mb": "512", "local_gb": "10", "image_type": "whole-disk", "image_disk_format": "raw", "image_checksum": null, "image_os_hash_algo": "sha512", "image_os_hash_value": "7f8188d635264e47e4daddc5aaf560b1e705d1a069a3b7dfa01cb6e6fb2911b6e7c6e1354f052ca192881e043cac0f4407cf500ccb56ffb37cab8697a36aa2f4", "image_url": "http://10.90.2.192:8089/agent_images/735cab8e-e2ba-494f-a300-e4f1b4f24c53", "image_container_format": "bare", "image_tags": [], "image_properties": {"virtual_size": 2147483648, "stores": "file", "owner_specified.openstack.sha256": "", "os_distro": "debian", "owner_specified.openstack.md5": "", "owner_specified.openstack.object": "images/debian-11-adam.img", "hw_disk_bus": "scsi", "os_version": "11.9.1", "os_type": "linux", "os_admin_user": "debian", "hw_scsi_model": "virtio-scsi", "os_hidden": false}}}, "ports": [{"id": 17, "uuid": "d4a1cb6a-fa6f-4fa9-a2cf-301098ad95da", "node_id": 13, "address": "52:54:84:00:02:94", "extra": {}, "local_link_connection": {}, "portgroup_id": null, "pxe_enabled": true, "internal_info": {"tenant_vif_port_id": "bc0f2f99-405e-4a9b-9065-e5a277d3ada6"}, "physical_network": "physnet1", "is_smartnic": false, "name": null, "created_at": "2023-08-03T09:18:01.000000", "updated_at": "2023-08-03T09:21:50.000000"}]}}
```

例如执行关机命令:
```
{"id": "8f2cb47f-2837-4010-933f-085ead4e0611", "command_name": "power_off", "command_status": "RUNNING", "command_error": null, "command_result": null}
```


## FAQ

#### node状态一直卡在wait call-back

这个问题困扰我最久, 需要搞清楚节点部署系统的流程才行
=> 最后发现是node无法向neutron获取到pxe dhcp ip地址导致的

猜测可能是nova给node配置image info有问题，看看相关日志，ironic部署server，需要vmlinuz和initrd的。。。以及最后的qcow2镜像?
=> 可能还没有到那一步，就出错了!

/var/log/kolla/nova/nova-compute-ironic.log
```
2023-07-11 10:48:30.350 7 ERROR oslo_messaging.rpc.server   File "/var/lib/kolla/venv/lib/python3.8/site-packages/nova/compute/manager.py", line 6384, in get_host_uptime
2023-07-11 10:48:30.350 7 ERROR oslo_messaging.rpc.server     return self.driver.get_host_uptime()
2023-07-11 10:48:30.350 7 ERROR oslo_messaging.rpc.server   File "/var/lib/kolla/venv/lib/python3.8/site-packages/nova/virt/driver.py", line 1429, in get_host_uptime
2023-07-11 10:48:30.350 7 ERROR oslo_messaging.rpc.server     raise NotImplementedError()
2023-07-11 10:48:30.350 7 ERROR oslo_messaging.rpc.server NotImplementedError

2023-07-11 10:49:13.113 7 ERROR nova.network.neutron [req-676b39ca-49c3-40a9-a730-f4b6080b8e9e 9daf4a7a49f947ae80319d05d5b58ece be87c1c91fb64486a45f446269d617ec - default default] [instance: 79b2c083-81f8-42b4-8c58-d0ae30a83321] The vnic_type of the bound port 178f21f0-b2c9-44af-b4e6-f2223c7446b9 has been changed in neutron from "normal" to "baremetal". Changing vnic_type of a bound port is not supported by Nova. To avoid breaking the connectivity of the instance please change the port vnic_type back to "normal".
```
=> TODO: 分析解决!!

openstack server list --long

查看分析port的情况?
```
openstack port list
| e9f46549-8865-4ee4-8063-b5c755709d78 |      | ac:1f:6b:12:4b:76 | ip_address='10.0.2.196', subnet_id='617d6ce1-98af-417b-af24-920989b5d99d' | ACTIVE |

=> 真的是网络配置问题，导致没有pxe启动成功? => 没能获取到dhcp ip地址呢? => kolla默认public网络默认没有开启dhcp, 开一下!
openstack port show 011a1804-36ad-4b85-b500-b75409ef143a
+-------------------------+--------------------------------------------------------------------------------------+
| Field                   | Value                                                                                |
+-------------------------+--------------------------------------------------------------------------------------+
| admin_state_up          | UP                                                                                   |
| allowed_address_pairs   |                                                                                      |
| binding_host_id         | 8fcf8fc8-28c4-4761-8c67-05f8c02b2dd1                                                 |
| binding_profile         |                                                                                      |
| binding_vif_details     | bound_drivers.0='baremetal', connectivity='legacy'                                   |
| binding_vif_type        | other                                                                                |
| binding_vnic_type       | baremetal                                                                            |
| created_at              | 2023-07-11T07:08:34Z                                                                 |
| data_plane_status       | None                                                                                 |
| description             |                                                                                      |
| device_id               | 18609a0b-fb8f-4bee-985a-f29449b6ef13                                                 |
| device_owner            | compute:nova                                                                         |
| device_profile          | None                                                                                 |
| dns_assignment          | None                                                                                 |
| dns_domain              | None                                                                                 |
| dns_name                | None                                                                                 |
| extra_dhcp_opts         | ip_version='4', opt_name='150', opt_value='10.30.2.98'                               |
|                         | ip_version='4', opt_name='tag:ipxe,67', opt_value='http://10.30.2.98:8089/boot.ipxe' |
|                         | ip_version='4', opt_name='server-ip-address', opt_value='10.30.2.98'                 |
|                         | ip_version='4', opt_name='66', opt_value='10.30.2.98'                                |
|                         | ip_version='4', opt_name='tag:!ipxe,67', opt_value='snponly.efi'                     |
| fixed_ips               | ip_address='10.0.2.198', subnet_id='617d6ce1-98af-417b-af24-920989b5d99d'            |
```

nova-conductor.log => 超时失败日志!
```
=> Failed to provision instance 79b2c083-81f8-42b4-8c58-d0ae30a83321: Timeout reached while waiting for callback for node 8fcf8fc8-28c4-4761-8c67-05f8c02b2dd1

2023-07-11 11:21:10.090 17 ERROR nova.scheduler.utils [req-717a7974-ab22-4c6f-9a5b-68266f62f141 6737de59870d4c149b842d813ff0d1f7 7096ea09f9844f87beecd990d32480e2 - default default] [instance: 79b2c083-81f8-42b4-8c58-d0ae30a83321] Error from last host: kolla-ironic (node 8fcf8fc8-28c4-4761-8c67-05f8c02b2dd1): ['Traceback (most recent call last):\n', '  File "/var/lib/kolla/venv/lib/python3.8/site-packages/nova/compute/manager.py", line 2513, in _build_and_run_instance\n    self.driver.spawn(context, instance, image_meta,\n', '  File "/var/lib/kolla/venv/lib/python3.8/site-packages/nova/virt/ironic/driver.py", line 1208, in spawn\n    LOG.error("Error deploying instance %(instance)s on "\n', '  File "/var/lib/kolla/venv/lib/python3.8/site-packages/oslo_utils/excutils.py", line 227, in __exit__\n    self.force_reraise()\n', '  File "/var/lib/kolla/venv/lib/python3.8/site-packages/oslo_utils/excutils.py", line 200, in force_reraise\n    raise self.value\n', '  File "/var/lib/kolla/venv/lib/python3.8/site-packages/nova/virt/ironic/driver.py", line 1203, in spawn\n    timer.start(interval=CONF.ironic.api_retry_interval).wait()\n', '  File "/var/lib/kolla/venv/lib/python3.8/site-packages/eventlet/event.py", line 125, in wait\n    result = hub.switch()\n', '  File "/var/lib/kolla/venv/lib/python3.8/site-packages/eventlet/hubs/hub.py", line 313, in switch\n    return self.greenlet.switch()\n', '  File "/var/lib/kolla/venv/lib/python3.8/site-packages/oslo_service/loopingcall.py", line 150, in _run_loop\n    result = func(*self.args, **self.kw)\n', '  File "/var/lib/kolla/venv/lib/python3.8/site-packages/nova/virt/ironic/driver.py", line 544, in _wait_for_active\n    raise exception.InstanceDeployFailure(msg)\n', 'nova.exception.InstanceDeployFailure: Failed to provision instance 79b2c083-81f8-42b4-8c58-d0ae30a83321: Timeout reached while waiting for callback for node 8fcf8fc8-28c4-4761-8c67-05f8c02b2dd1\n', '\nDuring handling of the above exception, another exception occurred:\n\n', 'Traceback (most recent call last):\n', '  File "/var/lib/kolla/venv/lib/python3.8/site-packages/nova/compute/manager.py", line 2336, in _do_build_and_run_instance\n    self._build_and_run_instance(context, instance, image,\n', '  File "/var/lib/kolla/venv/lib/python3.8/site-packages/nova/compute/manager.py", line 2609, in _build_and_run_instance\n    raise exception.RescheduledException(\n', 'nova.exception.RescheduledException: Build of instance 79b2c083-81f8-42b4-8c58-d0ae30a83321 was re-scheduled: Failed to provision instance 79b2c083-81f8-42b4-8c58-d0ae30a83321: Timeout reached while waiting for callback for node 8fcf8fc8-28c4-4761-8c67-05f8c02b2dd1\n']
```

会不会是这个port创建的有问题?
openstack port list

在页面上看node节点信息，发现deploy有点问题!
```
deploy 		direct 	Node 8fcf8fc8-28c4-4761-8c67-05f8c02b2dd1 failed to validate deploy image info. Some parameters were missing. Missing are: ['instance_info.image_source'] 
```

validate节点信息，也能看到上述信息
https://docs.openstack.org/ironic/wallaby/install/standalone/deploy.html
```
[ssh_10.30.2.98] root@kolla: ironic-conductor$openstack baremetal node validate 8fcf8fc8-28c4-4761-8c67-05f8c02b2dd1
+------------+--------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+
| Interface  | Result | Reason                                                                                                                                                    |
+------------+--------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+
| bios       | False  | Driver ipmi does not support bios (disabled or not implemented).                                                                                          |
| boot       | True   |                                                                                                                                                           |
| console    | False  | Driver ipmi does not support console (disabled or not implemented).                                                                                       |
| deploy     | False  | Node 8fcf8fc8-28c4-4761-8c67-05f8c02b2dd1 failed to validate deploy image info. Some parameters were missing. Missing are: ['instance_info.image_source'] |
| inspect    | False  | Driver ipmi does not support inspect (disabled or not implemented).                                                                                       |
| management | True   |                                                                                                                                                           |
| network    | True   |                                                                                                                                                           |
| power      | True   |                                                                                                                                                           |
| raid       | False  | Driver ipmi does not support raid (disabled or not implemented).                                                                                          |
| rescue     | False  | Driver ipmi does not support rescue (disabled or not implemented).                                                                                        |
| storage    | True   |                                                                                                                                                           |
+------------+--------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+
```

TODO: 配置一下?
```
baremetal node set $NODE_UUID \
    --instance-info image_source=$IMG \
    --instance-info image_checksum=$MD5HASH
```
https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/11/html/bare_metal_provisioning/sect-configure
=> 这个校验失败暂时没有问题?
Interfaces may fail validation due to missing 'ramdisk', 'kernel', and 'image_source' parameters. This result is fine, because the Compute service populates those missing parameters at the beginning of the deployment process.
=> nova部署时，会配置这些参数

驱动列表?
https://docs.openstack.org/ironic/pike/install/enrollment.html
```
[ssh_10.30.2.98] root@kolla: ironic-conductor$openstack baremetal driver list
+---------------------+----------------+
| Supported driver(s) | Active host(s) |
+---------------------+----------------+
| ipmi                | kolla          |
| redfish             | kolla          |
+---------------------+----------------+
```

驱动参数信息?
```
$ ironic driver-properties pxe_ipmitool
+----------------------+-------------------------------------------------------------------------------------------------------------+
| Property             | Description                                                                                                 |
+----------------------+-------------------------------------------------------------------------------------------------------------+
| ipmi_address         | IP address or hostname of the node. Required.                                                               |
| ipmi_password        | password. Optional.                                                                                         |
| ipmi_username        | username; default is NULL user. Optional.                                                                   |
| ...                  | ...                                                                                                         |
| deploy_kernel        | UUID (from Glance) of the deployment kernel. Required.                                                      |
| deploy_ramdisk       | UUID (from Glance) of the ramdisk that is mounted at boot time. Required.                                   |
+----------------------+-------------------------------------------------------------------------------------------------------------+
```

openstack --os-baremetal-api-version 1.31 baremetal driver show ipmi


#### pxe启动失败, exec format error

xxx, 重新下载，以及构建kernel镜像?
=> 原来是我把kernel和initram搞反了。。。

#### 裸金属节点状态无法从enroll转为manage

=> 原来是端口搞错了，物理机ipmi端口是623...

查看日志: /var/log/kolla/ironic/ironic-conductor.log
```
Command: ipmitool -I lanplus -H 10.30.10.3 -L ADMINISTRATOR -p 6230 -U ADMIN -R 1 -N 5 -f /tmp/tmpq4atxoud power status
Exit code: 1
Stdout: ''
Stderr: 'Error: Unable to establish IPMI v2 / RMCP+ session\n': oslo_concurrency.processutils.ProcessExecutionError: Unexpected error while running command.
2023-07-11 10:36:30.999 7 WARNING ironic.drivers.modules.ipmitool [req-d0822a47-9736-484e-9baa-4c77ef82f2a6 6737de59870d4c149b842d813ff0d1f7 7096ea09f9844f87beecd990d32480e2 - default default] IPMI Error encountered, retrying "ipmitool -I lanplus -H 10.30.10.3 -L ADMINISTRATOR -p 6230 -U ADMIN -R 1 -N 5 -f /tmp/tmp31k606js power status" for node fc63d131-627a-41fc-ac18-ffe902c7e308. Error: Unexpected error while running command.
```

手动执行命令, ipmitool命令失败了?
```
echo ADMIN > /tmp/tmpq4atxoud
ipmitool -I lanplus -H 10.30.10.3 -L ADMINISTRATOR -p 6230 -U ADMIN -R 1 -N 5 -f /tmp/tmpq4atxoud power status
Error: Unable to establish IPMI v2 / RMCP+ session
```

#### Could not find the following interface in the 'ironic.hardware.interfaces.deploy' entrypoint: iscsi

ipmi驱动不支持iscsi安装部署系统, 支持direct安装

```
Could not find the following interface in the 'ironic.hardware.interfaces.deploy' entrypoint: iscsi. Valid interfaces are ['direct']. (HTTP 400)
```

#### please change the port vnic_type back to "normal"

目前必现, 看是否影响到系统cloud-init运行了?

[some ports does not become ACTIVE during provisioning](https://bugs.launchpad.net/neutron/+bug/1760047)
=> 发现这个port确实状态为DOWN?

/var/log/kolla/nova/nova-compute-ironic.log
```
2023-07-11 10:49:13.113 7 ERROR nova.network.neutron [req-676b39ca-49c3-40a9-a730-f4b6080b8e9e 9daf4a7a49f947ae80319d05d5b58ece be87c1c91fb64486a45f446269d617ec - default default] [instance: 79b2c083-81f8-42b4-8c58-d0ae30a83321] The vnic_type of the bound port 178f21f0-b2c9-44af-b4e6-f2223c7446b9 has been changed in neutron from "normal" to "baremetal". Changing vnic_type of a bound port is not supported by Nova. To avoid breaking the connectivity of the instance please change the port vnic_type back to "normal".
```

#### Flavor's disk is too small for requested image

=> 修正机型配置即可

原因是机型磁盘大小为1G, 而镜像那个大小为1.049G?
(创建的flavor磁盘大小仅仅为1G)

```
Flavor's disk is too small for requested image. Flavor disk is 1073741824 bytes, image is 1127088128 bytes. (HTTP 400) (Request-ID: req-5b711f81-dfd4-49d2-9196-0995584b882c)
```

对应居然是镜像的实际大小...
```
du -sb /home/adam/ubuntu-server.img.qcow2
1127088128      /home/adam/ubuntu-server.img.qcow2
```

#### The location 10441 is outside of the device /dev/vda

=> 难道是自己构建的ubuntu镜像有问题, 换成debian10用户镜像部署成功了!

```
2023-07-14 16:16:00.480 7 ERROR nova.compute.manager [req-badd4ad2-f103-4b88-9566-8949fbe526e1 6737de59870d4c149b842d813ff0d1f7 7096ea09f9844f87beecd990d32480e2 - default default] [instance: 12c3fb33-4aa4-430f-80c7-7674028ca795] Instance failed to spawn: nova.exception.InstanceDeployFailure: Failed to provision instance 12c3fb33-4aa4-430f-80c7-7674028ca795: Deploy step deploy.write_image failed on node f9d4b0fd-a8d0-4685-8a5f-da3f69249fb4. Writing image to device /dev/vda failed with exit code 1. stdout: . stderr: Error: The location 10441 is outside of the device /dev/vda.
```

#### No suitable device was found for deployment

加了一块virtio磁盘居然可以了，之前是IDE磁盘，没有序列号, 没有/dev/sda

=> 使用tinyipa，在部署系统的时候查看，日志居然报出没有/dev/disk目录...

```
2023-07-12 21:20:02.188 7 ERROR oslo.service.loopingcall [-] Fixed interval looping call 'nova.virt.ironic.driver.IronicDriver._wait_for_active' failed: nova.exception.InstanceDeployFailure: Failed to provision instance 2105f78b-9b3a-48bf-a541-1032b12b9d3e: Deploy step deploy.write_image failed on node a7f22efc-73d6-4bb9-bc2d-acfc7a78e49a. No suitable device was found for deployment - root device hints were not provided and all found block devices are smaller than 4294967296B.
```

#### 部署debian10镜像没有配置好用户名密码

=> cloud-init被ds-identify给禁用了 (查看/run/cloud-init/下的日志得到)
新增配置文件: /etc/cloud/ds-identify.cfg
```
policy: search,found=all,maybe=none,notfound=enabled
```

后续看一下禁用cloud-init的深层原因!
https://github.com/canonical/cloud-init/blob/main/tools/ds-identify

没有dmi也会禁用cloud-init?

[ironic cloud init grow part失败和元数据失败](https://www.cnblogs.com/dream397/p/13218021.html)
```
cat /run/cloud-init/*
cloud-init is enabled but no datasource found, disabling
```

应该是cloud-init没有配置成功，计划弄一个自带用户名密码的镜像试试
=> 可以, debian10, 已经cloud-init初始化的密码也可以用!
=> 发现cloud-init-local服务没有运行, 为什么, 但是enable了? => 难道是运行条件不满足? => 原来是已经初始化过的debian镜像，放到其他地方运行有点问题！！！
=> 发现依赖目标没有满足? `systemctl status network-pre.target`
https://www.freedesktop.org/wiki/Software/systemd/NetworkTarget/
=> cloud-init-local.service 不应该`Wants=network-pre.target` ???
=> 自己造user image安装裸金属节点试试啊!!!

[如何处理cloud-init-local概率性启动失败导致裸金属服务器不能正确注入数据的问题？](https://support.huaweicloud.com/bpicg-bms/zh-cn_topic_0000001359501112.html)
=> 查看裸金属节点，感觉有点问题

创建实例的时候，传入user-data, 配置用户密码?
```
  --user-data my-script.sh \
  --password xxxx?
```
配置user-data脚本文件修改密码
```
#!/bin/sh
passwd debian<<EOF
123123
123123
EOF
```

## 其他资料

旧的调研单 #29923

https://xie.infoq.cn/article/240621481a0745456ecb89f6f
为什么说 OpenStack Ironic 是一个神秘的组件:

原因一：Ironic 使用了 BMC（Baseboard Manager Controller）即基板管理控制器，独立的系统在服务器通过额外的硬件控制器和 PXE（Pre-boot Execution Environment）网络启动，直接把事先做好的操作系统磁盘镜像克隆到物理服务器上，免去了使用 Kickstart 自动安装系统的过程，高效省时；

原因二：Ironic 是通过 Nova 来调用的，是模拟 Nova 的一个虚拟化驱动，其创建和管理物理服务器资源是和虚拟化实例创建部署流程一样。

[suse - 29 Installing Baremetal (Ironic)](https://documentation.suse.com/soc/9/html/suse-openstack-cloud-clm-all/install-ironic-overview.html)
资料挺多的...
29.3.1 Redfish Protocol Support

[Configuring the Bare Metal (Ironic) Service (optional)](https://docs.openstack.org/openstack-ansible-os_ironic/latest/configure-ironic.html)

https://docs.openstack.org/ironic/latest/user/deploy.html
=> 官方ironic用户部署系统文档?
Deploying with a config drive => 这是啥?
See Booting a Ramdisk or an ISO for details. => ISO和Ramdisk引导?

https://docs.openstack.org/ironic/latest/admin/node-deployment.html
=> 管理员部署文档? => 官方文档，怎么都值得一看的!
Writing a Deploy Step => 自己编写部署步骤?
Deploy Templates => 编写部署模板?
Creating a deploy template via API

- [理解裸机部署过程ironic](https://www.cnblogs.com/menkeyi/p/6063557.html)

https://ironic-book.readthedocs.io/zh_CN/latest/inspector/inspector.html
4.0 Inspector 介绍
在我们注册完 ironic-node 之后，我们需要把裸机的硬件信息更新到 node 表里。如果数量比较少，我们可以手动添加，但是如果是大规模部署，显然不适合手动添加。另外还有 port 的创建，裸机网口和交换机的链接关系等，都不适合自动添加。
ironic inspector 主要是帮助我们收集裸机信息的。
=> 但是IPMI不支持?

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


#### devstack 安装使用ironic

=> 一直未验证成功!!! 后续再尝试一下!

关键字《devstack ironic plugin》
[ironic官方文档](https://docs.openstack.org/ironic/latest/contributor/dev-quickstart.html#deploying-ironic-with-devstack)

[(好)Ironic 裸金属管理服务 原创](https://blog.51cto.com/u_15301988/3160308)

#### 独立使用ironic?

=> 没有neutron支持，怎么pxe启动的? 自己额外配置!

[(好)Openstack Ironic Bare metal 实操](https://blog.csdn.net/m0_48594855/article/details/119979493)
如果把Ironic放到庞大的系统去理解，毕竟繁琐，不适合初学者；所幸的是Ironic本身是一个相对独立的模块，有模块自己的操作命令。

如果使用相关命令操作一遍，结合文档理解，清晰了然。
=> TODO: 单独操作ironic接口?

了解下面一些参数干嘛用的?
- --property  boot_mode=bios
- --deploy-interface ramdisk => 干嘛用的? 我们目前是direct
- --boot-interface ipxe

目前部署的环境只支持direct部署
```
openstack baremetal driver show ipmi | grep deploy
| default_deploy_interface      | direct              |
| enabled_deploy_interfaces     | direct              |
```

[Openstack Ironic standalone 方式部署](https://www.xiexianbin.cn/openstack/ironic/index.html)
ironic如果配置成standalone服务，其他服务如glance，neutron，nova，cinder等无需安装。

#### initramfs修改用户密码

关键字《centos9 initramfs解包 打包》
[centos7 initramfs解包 打包](https://www.jianshu.com/p/218544a3531b)

如果你的centos安装了其他内核，例如elrepo的内核，initramfs就是标准linux的格式，我们执行file 查看initramfs的时候，就会发现是 gzip compressed data。这时候解包和打包，就不需要关心early_cpio的内容了。

解包
```
cd /boot
initramfs=$(ls -a initramfs-$(uname -r).img)
cp /boot/$initramfs /tmp

mkdir -p /tmp/rootfs_cpio

#解包rootfs
cd /tmp/rootfs_cpio
/usr/lib/dracut/skipcpio ../$initramfs | zcat | cpio -id
```

然后chroot修改root密码即可

打包
```
cd /tmp/rootfs_cpio
find . | cpio -o -H newc | gzip > ../rootfs_cpio.img
```

## 参考资料

- [openstack官方ironic 架构](https://docs.openstack.org/ironic/latest/user/architecture.html)

- [(好)Ironic 裸金属管理服务 原创](https://blog.51cto.com/u_15301988/3160308)
