# ovs使用

kni模块走协议栈

关键字

- openvswitch
- dpdk

## 编译使用

[使用 DPDK 优化 VirtIO 和 OVS 网络](https://my.oschina.net/LastRitter/blog/1807032)
=> TODO: 可以验证一下, 版本环境旧了,用新版本dpdk和ovs

[centos 7.9 编译 ovs+ dpdk](https://zhuanlan.zhihu.com/p/455967651)

#### 编译dpdk

安装开发依赖包
```
yum install -y gcc numactl numactl-libs numactl-devel kernel kernel-debug kernel-debug-devel kernel-devel kernel-doc kernel-headers libpcap-devel
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

#### 配置ovs服务(未验证)

- openvswitch.service
- ovsdb-server.service
- ovs-vswitchd.service

安装OVS的依赖和服务
service文件在源码的rhel/systemd目录中，建议根据实际路径更改后再拿去用

同时，要从这个目录中复制一个ovs-systemd-reload到ovs下的share/openvswitch/scripts目录中去，并且给a+x权限

service太多了懒得改了，所以我直接创建符号链接好了，把/usr/local/ovs/share/openvswitch链接到/usr/share/openvswitch，其他有必要改的再改

总共需要3个服务，第一个是主服务，剩余两个是静态服务（一个是ovsdb，一个是ovs daemon）并构成到主服务中去。只有主服务才可以被enable，静态服务要跟随主服务需要启动，不能被enable。目前所需要的最小构成就这三个，其他的暂且用不上

openvswitch.service
=> 居然没有找到 ovs-systemd-reload 这个脚本??? 文件名称不一样, 在rhel目录中
```
[Unit]
Description=Open vSwitch
Before=network.target network.service
After=network-pre.target ovsdb-server.service ovs-vswitchd.service
PartOf=network.target
Requires=ovsdb-server.service
Requires=ovs-vswitchd.service

[Service]
Type=oneshot
ExecStart=/bin/true
ExecReload=/usr/share/openvswitch/scripts/ovs-systemd-reload
ExecStop=/bin/true
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```


ovsdb-server.service
注意改PID文件的位置，否则可能会start后卡死（检测不到PID文件导致）

```
[Unit]
Description=Open vSwitch Database Unit
After=syslog.target network-pre.target
Before=network.target network.service
PartOf=openvswitch.service

[Service]
Type=forking
PIDFile=/usr/local/ovs/var/run/openvswitch/ovsdb-server.pid
Restart=on-failure
ExecStart=/usr/share/openvswitch/scripts/ovs-ctl --no-ovs-vswitchd --no-monitor --system-id=random start
ExecStop=/usr/share/openvswitch/scripts/ovs-ctl --no-ovs-vswitchd stop
ExecReload=/usr/share/openvswitch/scripts/ovs-ctl --no-ovs-vswitchd --no-monitor restart
```


ovs-vswitchd.service
同样要注意PID和套接字文件，不存在的依赖要删掉

有编译DPDK的下边的DPDK预加载部分要留着，没有编译DPDK的可以删除

```
[Unit]
Description=Open vSwitch Forwarding Unit
After=ovsdb-server.service network-pre.target systemd-udev-settle.service
Before=network.target network.service
Requires=ovsdb-server.service
ReloadPropagatedFrom=ovsdb-server.service
AssertPathIsReadWrite=/usr/local/ovs/var/run/openvswitch/db.sock
PartOf=openvswitch.service

[Service]
Type=forking
PIDFile=/usr/local/ovs/var/run/openvswitch/ovs-vswitchd.pid
Restart=on-failure
LimitSTACK=2M
#@begin_dpdk@
ExecStartPre=-/bin/sh -c '/usr/bin/chown :$${OVS_USER_ID##*:} /dev/hugepages'
ExecStartPre=-/usr/bin/chmod 0775 /dev/hugepages
#@end_dpdk@
ExecStart=/usr/share/openvswitch/scripts/ovs-ctl \
          --no-ovsdb-server --no-monitor --system-id=random \
          start
ExecStop=/usr/share/openvswitch/scripts/ovs-ctl --no-ovsdb-server stop
ExecReload=/usr/share/openvswitch/scripts/ovs-ctl --no-ovsdb-server \
          --no-monitor --system-id=random \
          restart
TimeoutSec=300
```

```
adam@adam-OptiPlex-3050:~$ systemctl status openvswitch-switch.service
● openvswitch-switch.service - Open vSwitch
     Loaded: loaded (/lib/systemd/system/openvswitch-switch.service; enabled; vendor preset: enabled)
     Active: active (exited) since Tue 2022-11-22 08:58:04 CST; 1 day 7h ago
   Main PID: 1181 (code=exited, status=0/SUCCESS)
        CPU: 2ms

Nov 22 08:58:04 adam-OptiPlex-3050 systemd[1]: Starting Open vSwitch...
Nov 22 08:58:04 adam-OptiPlex-3050 systemd[1]: Finished Open vSwitch.

openvswitch-switch.service                                                    enabled         enabled
ovs-vswitchd.service                                                          static          -

adam@adam-OptiPlex-3050:~$ ps -ef | grep openvs
root         891       1  0 Nov22 ?        00:00:10 ovsdb-server /etc/openvswitch/conf.db -vconsole:emer -vsyslog:err -vfile:info --remote=punix:/var/run/openvswitch/db.sock --private-key=db:Open_vSwitch,SSL,private_key --certificate=db:Open_vSwitch,SSL,certificate --bootstrap-ca-cert=db:Open_vSwitch,SSL,ca_cert --no-chdir --log-file=/var/log/openvswitch/ovsdb-server.log --pidfile=/var/run/openvswitch/ovsdb-server.pid --detach
root        1083       1  0 Nov22 ?        00:04:33 ovs-vswitchd unix:/var/run/openvswitch/db.sock -vconsole:emer -vsyslog:err -vfile:info --mlockall --no-chdir --log-file=/var/log/openvswitch/ovs-vswitchd.log --pidfile=/var/run/openvswitch/ovs-vswitchd.pid --detach
```

## ubuntu20.04编译使用

#### 编译dpdk

安装开发依赖包
```
# apt install -y gcc numactl numactl-libs numactl-dev kernel kernel-debug kernel-debug-devel kernel-devel kernel-doc kernel-headers libpcap-devel
sudo apt install -y gcc numactl libnuma-dev libpcap-dev
apt search linux-headers-$(uname -r)
sudo apt install -y linux-headers-5.15.0-53-generic
```

编译有报错,看来有适配问题,最好选择合适的版本

看有没有可以直接安装的版本?

```
sudo apt install -y openvswitch-switch-dpdk
```

关键字`ubuntu 22.04 install dpdk+ovs`

[OpenVswitch-DPDK](https://ubuntu.com/server/docs/openvswitch-dpdk)
```
sudo apt-get install openvswitch-switch-dpdk
sudo update-alternatives --set ovs-vswitchd /usr/lib/openvswitch-switch-dpdk/ovs-vswitchd-dpdk
ovs-vsctl set Open_vSwitch . "other_config:dpdk-init=true"
# Allocate 2G huge pages (not Numa node aware)
ovs-vsctl set Open_vSwitch . "other_config:dpdk-alloc-mem=2048"
# limit to one whitelisted device
ovs-vsctl set Open_vSwitch . "other_config:dpdk-extra=--pci-whitelist=0000:01:00.1"
sudo service openvswitch-switch restart
```

systemctl status openvswitch-switch.service

```
$ sudo ovs-vsctl clear Open_vSwitch . "other_config"
$ sudo ovs-vsctl get Open_vSwitch . "other_config"
{}
```

```
Nov 24 17:28:57 adam-OptiPlex-3050 systemd[1]: Dependency failed for Open vSwitch.
Nov 24 17:28:57 adam-OptiPlex-3050 systemd[1]: openvswitch-switch.service: Job openvswitch-switch.service/start failed with result 'dependency'.
```

```
sudo update-alternatives --set ovs-vswitchd /usr/lib/openvswitch-switch/ovs-vswitchd
```

=> 未成功...

#### ubuntu使用

关键字`ubuntu openvswitch-switch-dpdk 使用方法`

[OpenVswitch-DPDK](https://ubuntu.com/server/docs/openvswitch-dpdk)
[Configure Open vSwitch with Data Plane Development Kit on Ubuntu Server 17.04](https://www.intel.cn/content/www/cn/zh/developer/articles/technical/set-up-open-vswitch-with-dpdk-on-ubuntu-server.html)


配置内核参数, 开启iommu, hugepage?
编辑文件 /etc/default/grub
```
GRUB_CMDLINE_LINUX_DEFAULT="default_hugepagesz=1G hugepagesz=1G hugepages=16 hugepagesz=2M hugepages=2048 iommu=pt intel_iommu=on isolcpus=1-21,23-43,45-65,67-87"
```

让grub的内核参数修改生效
```
sudo update-grub
sudo reboot
```

创建桥, 添加物理网卡
```
sudo ovs-vsctl add-br ovsdpdkbr0 -- set bridge ovsdpdkbr0 datapath_type=netdev
sudo ovs-vsctl add-port ovsdpdkbr0 dpdk0 -- set Interface dpdk0 type=dpdk  "options:dpdk-devargs=0000:01:00.1"      
```

```
/usr/bin/dpdk-devbind.py
$ dpdk-devbind.py  --status

sudo modprobe vfio-pci
sudo dpdk-devbind.py --bind=vfio-pci enp1s0f1
# 绑定之后,就看不到旧网卡了
# sudo dpdk-devbind.py --bind=igb_uio 01:00.1
```

结果添加dpdk物理网卡,还是报错
```
2022-11-25T01:10:52.810Z|00093|dpdk|ERR|EAL: 0000:01:00.1 VFIO group is not viable! Not all devices in IOMMU group bound to VFIO or unbound
2022-11-25T01:10:52.810Z|00094|dpdk|ERR|EAL: Driver cannot attach the device (0000:01:00.1)
2022-11-25T01:10:52.810Z|00095|dpdk|ERR|EAL: Failed to attach device on primary process
2022-11-25T01:10:52.810Z|00096|netdev_dpdk|WARN|Error attaching device '0000:01:00.1' to DPDK
2022-11-25T01:10:52.810Z|00097|netdev|WARN|dpdk0: could not set configuration (Invalid argument)
2022-11-25T01:10:52.810Z|00098|dpdk|ERR|Invalid port_id=32
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

增加 dpdkvhostuser 端口：
```
ovs-vsctl add-port br-ovs vhost-user1 -- set Interface vhost-user1 type=dpdkvhostuser
ovs-vsctl add-port br-ovs vhost-user2 -- set Interface vhost-user2 type=dpdkvhostuser
=> 报错

ovs-vsctl: Error detected while setting up 'vhost-user1': could not open network device vhost-user1 (Unknown error -1).  See ovs-vswitchd log for details.
ovs-vsctl: The default log directory is "/opt/ovs/target-dpdk/var/log/openvswitch".
```

错误日志如下:
```
2022-11-24T19:21:24.351Z|00119|dpdk|INFO|VHOST_CONFIG: Linear buffers requested without external buffers, disabling host segmentation offloading support
2022-11-24T19:21:24.376Z|00120|dpdk|INFO|VHOST_CONFIG: vhost-user server: socket created, fd: 570
2022-11-24T19:21:24.378Z|00121|netdev_dpdk|INFO|Socket /opt/ovs/target-dpdk/var/run/openvswitch/vhost-user1 created for vhost-user port vhost-user1
2022-11-24T19:21:24.379Z|00122|dpdk|ERR|VHOST_CONFIG: failed to create fdset handling thread
2022-11-24T19:21:24.379Z|00123|netdev_dpdk|ERR|rte_vhost_driver_start failed for vhost user port: vhost-user1
2022-11-24T19:21:24.379Z|00124|netdev_dpdk|WARN|dpdkvhostuser ports are considered deprecated;  please migrate to dpdkvhostuserclient ports.
2022-11-24T19:21:24.381Z|00125|bridge|WARN|could not open network device vhost-user1 (Unknown error -1)
```

原因猜测:
- iommu
- hugepage

```
grubby --update-kernel=/boot/vmlinuz-3.10.0-1160.80.1.el7.x86_64 --args="intel_iommu=on iommu=pt iommu=pt"
grubby --update-kernel=/boot/vmlinuz-3.10.0-1160.80.1.el7.x86_64 --args="hugepagesz=1G default_hugepagesz=1G"
```

加上了iommu内核参数,以及加载openvswitch驱动的时候,改了一点点, 居然又可以了!


```
$ ovs-vsctl show
429a3e72-c5c5-4330-9670-09492255e7e9
    Bridge br-ovs
        Port "vhost-user2"
            Interface "vhost-user2"
                type: dpdkvhostuser
        Port "dpdk0"
            Interface "dpdk0"
                type: dpdk
                options: {dpdk-devargs="0000:1a:00.2"}
        Port br-ovs
            Interface br-ovs
                type: internal
        Port "vhost-user1"
            Interface "vhost-user1"
                type: dpdkvhostuser
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
