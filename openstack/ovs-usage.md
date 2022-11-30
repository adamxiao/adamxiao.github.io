# ovs使用

kni模块走协议栈

关键字

- openvswitch
- dpdk

## 编译使用

[使用 DPDK 优化 VirtIO 和 OVS 网络](https://my.oschina.net/LastRitter/blog/1807032)
=> 验证一下, 版本环境旧了,用下面新版本dpdk和ovs,否则有编译问题

[centos 7.9 编译 ovs+ dpdk](https://zhuanlan.zhihu.com/p/455967651)

#### 编译dpdk

安装开发依赖包
```
yum install -y gcc numactl numactl-libs numactl-devel kernel kernel-debug kernel-debug-devel kernel-devel kernel-doc kernel-headers libpcap-devel
```

ksvd819
```
yum install -y numactl-devel libpcap-devel
```

获取源码
```
git clone https://github.com/DPDK/dpdk.git
cd dpdk &&  git checkout v19.11
```

或者使用发行版
```
wget https://fast.dpdk.org/rel/dpdk-19.11.10.tar.xz
tar -xJf dpdk-*.tar.xz
ln -sf dpdk-stable-19.11.10 dpdk
```

设置环境变量
```
export OVS_ROOT=/opt/ovs
export DPDK_DIR=$OVS_ROOT/dpdk
export DPDK_BUILD=$DPDK_DIR/build
export DPDK_INSTALL=$DPDK_DIR/install

export DPDK_TARGET=x86_64-native-linuxapp-gcc
```

配置和编译：
```
make config T=$DPDK_TARGET
make -j8 && make install DESTDIR=$DPDK_INSTALL
make -j8 -C examples RTE_SDK=$DPDK_DIR RTE_TARGET=build O=$DPDK_INSTALL/examples
```

#### 编译ovs

安装开发依赖包
```
yum -y install gcc autoconf automake libtool kernel kernel-devel
```

ksvd819适配编译
```
yum -y install gcc autoconf automake libtool
```

获取源码
```
export OVS_ROOT=/opt/ovs && cd $OVS_ROOT
git clone https://github.com/openvswitch/ovs.git && cd ovs
git checkout v2.13.6
```

或者使用发行版
```
wget https://www.openvswitch.org/releases/openvswitch-2.13.6.tar.gz
tar -xzf openvswitch-2.13.6.tar.gz
ln -sf openvswitch-2.13.6 ovs
```

设置环境变量
```
$ vi $OVS_ROOT/ovs-env-dpdk.sh
export OVS_ROOT=/opt/ovs

export DPDK_DIR=$OVS_ROOT/dpdk
export DPDK_BUILD=$DPDK_DIR/build
export DPDK_INSTALL=$DPDK_DIR/install
export DPDK_TARGET=x86_64-native-linuxapp-gcc

export OVS_DIR=$OVS_ROOT/target-dpdk
export PATH=$OVS_DIR/bin/:$OVS_DIR/share/openvswitch/scripts:$PATH
```

开始编译(支持dpdk), 还需要安装python3
```
cd $OVS_ROOT/ovs
./boot.sh
mkdir -pv $OVS_ROOT/build-dpdk $OVS_ROOT/target-dpdk && cd $OVS_ROOT/build-dpdk

../ovs/configure --with-dpdk=$DPDK_BUILD --with-linux=/lib/modules/$(uname -r)/build --prefix=$OVS_ROOT/target-dpdk CFLAGS="-g -Ofast"

make -j8 'CFLAGS=-g -Ofast -march=native' && make install
mkdir -pv $OVS_ROOT/target-dpdk/modules && cp -vf $OVS_ROOT/build-dpdk/datapath/linux/*ko $OVS_ROOT/target-dpdk/modules/
```

#### 编译FAQ

编译报错, 原因是内核-devel包跟内核不匹配, reboot换一下内核即可
```
make: *** /lib/modules/3.10.0-1160.el7.x86_64/build: No such file or directory.  Stop.
```

编译报错, 原因是centos7.9的接口名称有改动, 代码改为ndo_change_mtu_rh74即可
```
/opt/ovs/dpdk/build/build/lib/librte_eal/linuxapp/kni/kni_net.c:714:2: error: unknown field ‘ndo_change_mtu’ specified in initializer
  .ndo_change_mtu = kni_net_change_mtu,
```

## 配置使用

#### 配置大页内存

仅本次生效：
```
mkdir -pv /mnt/huges
mount -t hugetlbfs nodev /mnt/huges -o pagesize=2MB
sysctl -w vm.nr_hugepages=8192
```

重启后生效：
```
$ vi /etc/fstab
nodev /mnt/huges hugetlbfs pagesize=2MB 0 0

mkdir -pv /mnt/huges

# 这个重启就有问题? => 确实是的
echo 'vm.nr_hugepages=8192' > /etc/sysctl.d/hugepages.conf
sysctl -p /etc/sysctl.d/hugepages.conf
```

验证配置是否生效： 验证失败, 不一样, 无法重启生效
```
grep HugePages /proc/meminfo

AnonHugePages:     77824 kB
HugePages_Total:    8192
HugePages_Free:     6656
HugePages_Rsvd:        0
HugePages_Surp:        0
```

虚拟机实际配置大页内存后效果
```
[root@localhost ~]# grep HugePages /proc/meminfo
AnonHugePages:      4096 kB
HugePages_Total:    3739
HugePages_Free:     3739
HugePages_Rsvd:        0
HugePages_Surp:        0
```

#### 网卡驱动绑定

查看网卡绑定状态
```
yum install -y pciutils
/opt/ovs/dpdk/usertools/dpdk-devbind.py --status
0000:00:09.0 'I350 Ethernet Controller Virtual Function 1520' if=eth0 drv=igbvf unused=

lspci | grep Ethernet | awk '{printf($1 " "); gsub(":","\\:"); cmd="ls /sys/bus/pci/devices/0000\\:" $1 "/driver/module/drivers/";  system(cmd)}'
00:09.0 pci:igbvf
```

加载网卡 UIO 驱动模块：
```
modprobe uio
rmmod igb_uio
insmod $DPDK_INSTALL/lib/modules/`uname -r`/extra/dpdk/igb_uio.ko

[root@localhost dpdk]# insmod ./igb_uio.ko
[  370.198564] igb_uio: loading out-of-tree module taints kernel.
[  370.200101] igb_uio: module verification failed: signature and/or required key missing - tainting kernel
[  370.203327] igb_uio: Use MSIX interrupt by default

=> 报错无法分配内存?
-bash: fork: Cannot allocate memory
```

绑定 enp26s0f2 网卡 UIO 驱动：
```
$DPDK_DIR/usertools/dpdk-devbind.py -u 00:09.0
Notice: 0000:00:09.0 I350 Ethernet Controller Virtual Function  is not currently managed by any driver

$DPDK_DIR/usertools/dpdk-devbind.py --bind=igb_uio 00:09.0
[  492.680726] igb_uio 0000:00:09.0: mapping 1K dma=0x235a4f000 host=ffff942735a4f000
[  492.682597] igb_uio 0000:00:09.0: unmapping 1K dma=0x235a4f000 host=ffff942735a4f000
```

最后查看绑定状态
```
$DPDK_DIR/usertools/dpdk-devbind.py --status

0000:00:09.0 'I350 Ethernet Controller Virtual Function 1520' drv=igb_uio unused=igbvf
```

#### 启动停止OVS

手动启动
```
export OVS_DIR=$OVS_ROOT/target-dpdk
cd $OVS_DIR

mkdir -pv $OVS_DIR/var/run/openvswitch $OVS_DIR/etc/openvswitch

# 创建ovsdb-server数据库：
$OVS_DIR/bin/ovsdb-tool create $OVS_DIR/etc/openvswitch/conf.db $OVS_DIR/share/openvswitch/vswitch.ovsschema

# 启动ovsdb-server数据库服务：
$OVS_DIR/sbin/ovsdb-server --remote=punix:$OVS_DIR/var/run/openvswitch/db.sock --remote=db:Open_vSwitch,Open_vSwitch,manager_options --pidfile --detach

# 初始化数据库（只在第一次运行时需要执行）：
$OVS_DIR/bin/ovs-vsctl --no-wait init

# 查看依赖的内核模块：
cat /usr/lib/modules/`uname -r`/modules.dep | awk '$1~"^extra/openvswitch"{for(i=2;i<=NF;i++) {print $i}}' | xargs echo
cat /usr/lib/modules/`uname -r`/modules.dep | awk '$1~"openvswitch"{for(i=2;i<=NF;i++) {print $i}}' | xargs echo
kernel/net/ipv6/netfilter/nf_nat_ipv6.ko.xz kernel/net/ipv4/netfilter/nf_nat_ipv4.ko.xz kernel/net/ipv6/netfilter/nf_defrag_ipv6.ko.xz kernel/net/netfilter/nf_nat.ko.xz kernel/net/netfilter/nf_conntrack.ko.xz kernel/net/ipv4/udp_tunnel.ko.xz kernel/lib/libcrc32c.ko.xz

# 加载openvswitch.ko依赖的内核模块：
cat /usr/lib/modules/`uname -r`/modules.dep | awk '$1~"^extra/openvswitch"{for(i=2;i<=NF;i++) {mod=gensub(/\.ko\.xz/,"",1,gensub(/.*\//,"",1,$i));cmd="modprobe " mod;system(cmd)}}'
cat /usr/lib/modules/`uname -r`/modules.dep | awk '$1~"openvswitch"{for(i=2;i<=NF;i++) {mod=gensub(/\.ko\.xz/,"",1,gensub(/.*\//,"",1,$i));cmd="modprobe " mod;system(cmd)}}'
modprobe geneve; modprobe gre; modprobe ip6_udp_tunnel; modprobe ip_gre; modprobe ip_tunnel; modprobe libcrc32c; modprobe nf_conntrack; modprobe nf_defrag_ipv6; modprobe nf_nat; modprobe nf_nat_ipv4; modprobe nf_nat_ipv6; modprobe udp_tunnel; modprobe vxlan; modprobe tunnel6;

[root@localhost ~]#  modinfo $OVS_DIR/modules/openvswitch.ko |grep depends
depends:        nf_conntrack,tunnel6,nf_nat,nf_defrag_ipv6,libcrc32c,nf_nat_ipv6,nf_nat_ipv4

# 加载openvswitch.ko内核模块：
insmod $OVS_DIR/modules/openvswitch.ko
# => 上面没有加载依赖内核模块, 这里就频繁报错的: modprobe nf_nat
# openvswitch: Unknown symbol nf_conntrack_find_get (err 0)

# 启动ovs-vswitchd守护进程：
$OVS_DIR/sbin/ovs-vswitchd --pidfile --detach --log-file

# 为ovs-vswitchd增加dpdk支持：
ovs-vsctl --no-wait set Open_vSwitch . other_config:dpdk-init=true
ovs-ctl --no-ovsdb-server --db-sock="$OVS_DIR/var/run/openvswitch/db.sock" start
=> 报错, cpu不支持, 把cpu兼容模式改为直通模式之后好了

Starting ovs-vswitchd ERROR: This system does not support "SSSE3".
Please check that RTE_MACHINE is set correctly.
EAL: FATAL: unsupported cpu type.
2022-11-24T19:05:09Z|00014|dpdk|EMER|Unable to initialize DPDK: Operation not supported
ovs-vswitchd: Cannot init EAL (Operation not supported)
ovs-vswitchd: could not initiate process monitoring
[FAILED]
```

使用命令手动停止： 未验证
```
pkill -9 ovs
rm -rfv $OVS_DIR/var/run/openvswitch $OVS_DIR/etc/openvswitch/ $OVS_DIR/etc/openvswitch/conf.db
```

#### 创建 NAT 网络
在节点 A 上创建的 NAT 网络网段为 192.168.2.0/24，网关为 192.168.2.99。

新增 OVS 网桥 br-ovs：
```
ovs-vsctl add-br br-ovs -- set bridge br-ovs datapath_type=netdev
ip link set dev br-ovs up
ip addr add 192.168.2.99/24 dev br-ovs

$ ip addr show br-ovs
21: br-ovs: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN qlen 1000
    link/ether a2:e8:a6:bb:55:46 brd ff:ff:ff:ff:ff:ff
    inet 192.168.2.99/24 scope global br-ovs
       valid_lft forever preferred_lft forever
    inet6 fe80::a0e8:a6ff:febb:5546/64 scope link 
       valid_lft forever preferred_lft forever
```

增加 NAT 地址转换：
```
$ iptables -t nat -A POSTROUTING -s 192.168.2.0/24 ! -d 192.168.2.0/24 -j MASQUERADE
```
配置 DHCP 服务：
```
$ dnsmasq --strict-order --except-interface=lo --interface=br-ovs --listen-address=192.168.2.99 --bind-interfaces --dhcp-range=192.168.2.128,192.168.2.192 --conf-file="" --pid-file=/var/run/br-ovs-dhcp.pid --dhcp-leasefile=/var/run/br-ovs-dhcp.leases --dhcp-no-override
```

#### 创建桥接网络

两个节点添加的物理网卡在一个交换机的相同 VLAN 上。

在节点 A 的 br-ovs 网桥上天剑物理网口 enp26s0f2：
```
ovs-vsctl add-port br-ovs dpdk0 -- set Interface dpdk0 type=dpdk options:dpdk-devargs=00:09.0

ovs-vsctl show
08bc1d6b-f3ca-4b1f-b031-bd3b8d89d2d8
    Bridge br-ovs
        datapath_type: netdev
        Port dpdk0
            Interface dpdk0
                type: dpdk
                options: {dpdk-devargs="00:09.0"}
        Port br-ovs
            Interface br-ovs
                type: internal
```

#### 使用 server 端口

原因猜测:
- iommu
- hugepage

```
grubby --update-kernel=/boot/vmlinuz-3.10.0-1160.80.1.el7.x86_64 --args="intel_iommu=on iommu=pt iommu=pt"
grubby --update-kernel=/boot/vmlinuz-3.10.0-1160.80.1.el7.x86_64 --args="hugepagesz=1G default_hugepagesz=1G"
ksvd819适配
grubby --update-kernel=/boot/vmlinuz-4.19.90-2003.4.0.0036.ky3.kb29.ksvd2.x86_64 --args="default_hugepagesz=1G hugepagesz=1G hugepages=4"
```

启动测试虚拟机 1：
```
$ /usr/libexec/qemu-kvm -smp 2 -m 2048 -serial stdio -cdrom $OVS_ROOT/images/centos7-init.iso -hda $OVS_ROOT/images/CentOS-7-x86_64_Snapshot1.qcow2 -net none -chardev socket,id=char1,path=$OVS_DIR/var/run/openvswitch/vhost-user1 -netdev type=vhost-user,id=mynet1,chardev=char1,vhostforce -device virtio-net-pci,mac=fa:16:3e:4d:58:6f,netdev=mynet1 -object memory-backend-file,id=mem,size=2048M,mem-path=/mnt/huge,share=on -numa node,memdev=mem -mem-prealloc
```

```
$ ip addr show eth0
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP qlen 1000
    link/ether fa:16:3e:4d:58:6f brd ff:ff:ff:ff:ff:ff
    inet 192.168.2.139/24 brd 192.168.2.255 scope global dynamic eth0
       valid_lft 3540sec preferred_lft 3540sec
    inet6 fe80::f816:3eff:fe4d:586f/64 scope link 
       valid_lft forever preferred_lft forever
```

#### 使用client端口

https://blog.csdn.net/sinat_20184565/article/details/93657065
对于vhost-user端口，Open vSwitch作为服务端，QEMU为客户端。这意味着如果OVS进程挂掉，所有的虚拟机必须重新启动。反之，对于vhost-user-client端口，OVS作为客户端，QEMU为服务器。这意味着OVS可以挂掉，并在不引起问题的情况下重新启动，也可重新启动客户机自身。由此原因，vhost-user-client端口为在所有已知情况下的首选类型。唯一的限制时vhost-user-client类型端口需要QEMU版本2.7. 端口类型vhost-user目前不赞成使用，并且将在以后的版本中移除。

```
ovs-vsctl add-port br-ovs vhost-user-client1 -- set Interface vhost-user-client1 type=dpdkvhostuserclient options:vhost-server-path=$OVS_DIR/var/run/openvswitch/vhost-user-client1
=> 段错误...
```

启动虚拟机
```
/usr/libexec/qemu-kvm -smp 2 -m 2048 -serial stdio \
  -cdrom $OVS_ROOT/images/centos7-init.iso \
  -hda $OVS_ROOT/images/CentOS-7-x86_64_Snapshot1.qcow2 \
  -net none -chardev socket,id=char1,path=$OVS_DIR/var/run/openvswitch/vhost-user-client1,server \
  -netdev type=vhost-user,id=mynet1,chardev=char1,vhostforce \
  -device virtio-net-pci,mac=fa:16:3e:4d:58:6f,netdev=mynet1 \
  -object memory-backend-file,id=mem,size=2048M,mem-path=/mnt/huge,share=on \
  -numa node,memdev=mem -mem-prealloc
```

```
QEMU waiting for connection on: unix:/opt/ovs/target-dpdk/var/run/openvswitch/vhost-user-client1,server
qemu-kvm: -netdev type=vhost-user,id=mynet1,chardev=char1,vhostforce: Invalid parameter 'vhost-user'

/usr/libexec/qemu-kvm: error while loading shared libraries: librbd.so.1: cannot map zero-fill pages: Cannot allocate memory

ERROR:qom/object.c:409:object_new_with_type: assertion failed: (type != NULL)
adam.sh: line 4:  1679 Aborted                 /usr/libexec/qemu-kvm -smp 2 -m 1024 -serial stdio -net none -chardev socket,id=char1,path=$OVS_DIR/var/run/openvswitch/vhost-user-client1,server -netdev type=vhost-user,id=mynet1,chardev=char1,vhostforce -device virtio-net-pci,mac=fa:16:3e:4d:58:6f,netdev=mynet1 -object memory-backend-file,id=mem,size=1024M,mem-path=/mnt/huge,share=on
```

应该是hugepage memory没有配置导致的。

## 搜索资料

https://blog.xuegaogg.com/posts/1336/
手动配置一下 openvswitch.service, ovsdb-server.service 等?

#### 网卡支持dpdk?

82571网卡支持?
```
adam@adam-OptiPlex-3050:~$ sudo dpdk-devbind.py  --bind=vfio-pci 0000:01:00.1
adam@adam-OptiPlex-3050:~$ dpdk-devbind.py  --status

Network devices using DPDK-compatible driver
============================================
0000:01:00.0 '82571EB/82571GB Gigabit Ethernet Controller D0/D1 (copper applications) 105e' drv=vfio-pci unused=e1000e
0000:01:00.1 '82571EB/82571GB Gigabit Ethernet Controller D0/D1 (copper applications) 105e' drv=vfio-pci unused=e1000e
```


ubuntu失败
```
2022-11-28T09:19:11.921Z|00125|netdev_dpdk|WARN|Failed to enable flow control on device 0
2022-11-28T09:19:11.921Z|00126|bridge|INFO|ovs-vswitchd (Open vSwitch) 2.13.8
2022-11-28T09:19:13.972Z|00001|netdev_offload_dpdk(dp_netdev_flow_5)|WARN|dpdk0: rte_flow creation failed: 1 (Function not implemented).
2022-11-28T09:19:13.972Z|00002|netdev_offload_dpdk(dp_netdev_flow_5)|WARN|Failed flow:
  Attributes: ingress=1, egress=0, prio=0, group=0, transfer=0
rte flow eth pattern:
  Spec: src=52:54:00:71:46:36, dst=ff:ff:ff:ff:ff:ff, type=0x0806
  Mask: src=ff:ff:ff:ff:ff:ff, dst=ff:ff:ff:ff:ff:ff, type=0xffff
rte flow mark action:
  Mark: id=1
rte flow RSS action:
  RSS: queue_num=1
2022-11-28T09:19:14.066Z|00003|netdev_offload_dpdk(dp_netdev_flow_5)|WARN|dpdk0: rte_flow creation failed: 1 (Function not implemented).
2022-11-28T09:19:14.641Z|00004|netdev_offload_dpdk(dp_netdev_flow_5)|WARN|Dropped 13 log messages in last 0 seconds (most recently, 0 seconds ago) due to excessive rate
2022-11-28T09:19:14.641Z|00005|netdev_offload_dpdk(dp_netdev_flow_5)|WARN|dpdk0: rte_flow creation failed: 1 (Function not implemented).
2022-11-28T09:19:15.209Z|00006|netdev_offload_dpdk(dp_netdev_flow_5)|WARN|Dropped 27 log messages in last 1 seconds (most recently, 0 seconds ago) due to excessive rate
```

## 参考文档

[ovs官方文档 - dpdk](https://docs.openvswitch.org/en/latest/topics/dpdk/phy/)

https://metonymical.hatenablog.com/entry/2021/04/13/221445
日文的dpdk,有好多图

网络转发性能测试方法 ( l3fwd, ovs-dpdk )
https://aijishu.com/a/1060000000212215
https://blog.csdn.net/weixin_47569031/article/details/118086202
